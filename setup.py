import psycopg2
import yaml

def connect(hostname, port, user, password, database):
    conn = psycopg2.connect(hostname=hostname, port=port, user=user, password=password, database=database)
    cur = conn.cursor()

    return conn, cur

def close_connection(conn):
    conn.close()

def create_tables(conn, cur):
    cur.execute(query1)


with open("./config.yaml", "r") as f:
    cred = yaml.load(f, Loader=yaml.FullLoader)

print(cred)
