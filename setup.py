import psycopg2
import yaml
import numpy as np
import pandas as pd
import os

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

def read_config():
    with open("./config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config

def preprocessing():
    config = read_config()

    dataDir = config["data_dir"]
    processedDir = config["processed_dir"]

    if not os.path.exists(processedDir):
        os.makedirs(processedDir)

    for file in os.listdir(dataDir):
        print(file)
        if file.split(".")[-1] == "csv":
            print("Processing "+file)
            df = pd.read_csv(dataDir+file)
            std, sec, exam, exam_total = file.split("_")[1:]
            exam_total = exam_total.split(".")[0]

            df["class"] = std
            df["section"] = sec
            df["exam"] = exam
            df["exam_total"] = exam_total

            df = df.melt(id_vars=["roll no", "name", "class", "section", "exam", "exam_total"], var_name="subject", value_name="marks")

            df = df.replace(["AB", "Ab", "ab", "ABSENT", "ABSENT "], np.nan)

            df.to_csv(processedDir+file, index=None)
            print(file+" processing done")

def into_db(curr, processed_dir):
    for file in os.listdir(processed_dir):



# with open("./config.yaml", "r") as f:
#     cred = yaml.load(f, Loader=yaml.FullLoader)

# try:
#     conn, cur = connect(cred["hostname"], cred["port"], cred["username"], cred["password"], cred["db_name"])
#     create_tables(cur)
#     close_connection(conn)
# except:
#     print("Database or table already exist")
