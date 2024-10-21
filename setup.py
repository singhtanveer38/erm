import psycopg2
import yaml

def connect(hostname, port, user, password, database):

    conn = psycopg2.connect(host=hostname, port=port, user=user, password=password, database="postgres")
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"create database {database}")
    close_connection(conn)

    conn = psycopg2.connect(host=hostname, port=port, user=user, password=password, database=database)
    conn.autocommit = True
    cur = conn.cursor()

    return conn, cur

def close_connection(conn):
    conn.close()

def create_tables(cur):
    with open("./create_tables.sql", "r") as f:
        sql = f.readlines()
        sql = "".join(sql)
    cur.execute(sql)

with open("./config.yaml", "r") as f:
    cred = yaml.load(f, Loader=yaml.FullLoader)

try:
    conn, cur = connect(cred["hostname"], cred["port"], cred["username"], cred["password"], cred["db_name"])
    create_tables(cur)
    close_connection(conn)
except:
    print("Database or table already exist")
