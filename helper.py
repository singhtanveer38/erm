from pandas._libs.tslibs.period import DIFFERENT_FREQ
import psycopg2
import yaml
import numpy as np
import pandas as pd
import os
from datetime import datetime

def create_db(hostname, port, user, password, database):
    conn = psycopg2.connect(host=hostname, port=port, user=user, password=password, database="postgres")
    conn.autocommit = True
    curr = conn.cursor()

    curr.execute(f"create database {database}")
    close_connection(conn)

def close_connection(conn):
    conn.close()

def connect(hostname, port, user, password, database):
    conn = psycopg2.connect(host=hostname, port=port, user=user, password=password, database=database)
    conn.autocommit = True
    curr = conn.cursor()

    return conn, curr

def create_tables(curr):
    with open("./create_tables.sql", "r") as f:
        sql = f.readlines()
        sql = "".join(sql)
    curr.execute(sql)

def read_config():
    with open("./config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config

def preprocessing(dataDir, processedDir):
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

            df = df.replace(["AB", "Ab", "ab", "ABSENT", "ABSENT ", np.nan], 0)

            df.to_csv(processedDir+file, index=None, header=None)
            print(file+" processing done")

def into_db(conn, curr, processed_dir):
    for file in os.listdir(processed_dir):
        print(f"\nLoading {file} into DB...")
        with open(processed_dir+file, "r") as f:
            curr.copy_from(f, "marks", sep=",")
            curr.execute("insert into loaded_files(timestamp, filename) values(current_timestamp, %s)", (file,))
            conn.commit()
        print(f"{file} loaded into DB...")
