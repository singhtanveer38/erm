from pandas._libs.tslibs.period import DIFFERENT_FREQ
import psycopg2
import yaml
import numpy as np
import pandas as pd
import os
from datetime import datetime
import io

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

            df["class"] = int(std)
            df["section"] = sec
            df["exam"] = exam
            df["exam_total"] = int(exam_total)

            df = df.melt(id_vars=["roll no", "name", "class", "section", "exam", "exam_total"], var_name="subject", value_name="marks")

            df = df.fillna(0)

            attendence = []
            marks_new = []
            for i in df["marks"]:
                if i in ["AB", "Ab", "ab", "ABSENT", "ABSENT "]:
                    attendence.append("absent")
                    marks_new.append(0)
                else:
                    attendence.append("present")
                    marks_new.append(float(i))

            df["attendence"] = attendence
            df["marks"] = marks_new
            print(type(df["marks"][0]))
            df["percentage"] = round((df["marks"]/df["exam_total"]) * 100, 2)

            category = []
            for attendence, percentage in zip(df["attendence"], df["percentage"]):
                if attendence == "absent":
                    category.append("absent")
                else:
                    if percentage < 33:
                        category.append("0_to_33")
                    elif 33 <= percentage < 45:
                        category.append("33_to_45")
                    elif 45 <= percentage < 60:
                        category.append("45_to_60")
                    elif 60 <= percentage < 75:
                        category.append("60_to_75")
                    elif 75 <= percentage < 90:
                        category.append("75_to_90")
                    else:
                        category.append("90_to_100")

            df["category"] = category

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

def overall_result(conn, curr):
    curr.execute("select * from marks")
    data = curr.fetchall()
    columns = ["roll_no", "name", "class", "section", "exam_name", "exam_marks", "subject", "marks_obtained", "attendence", "percentage", "category"]
    df = pd.DataFrame(data, columns=columns)
    df["marks_obtained"] = df["marks_obtained"].astype("int")
    df = df.groupby(by=["roll_no", "name", "class", "section", "exam_name", "exam_marks"], as_index=False).agg({"marks_obtained": "sum"})
    df["percentage"] = round((df["marks_obtained"]/(df["exam_marks"]*6))*100, 2)

    category = []
    for percentage in df["percentage"]:
        if percentage < 33:
            category.append("0_to_33")
        elif 33 <= percentage < 45:
            category.append("33_to_45")
        elif 45 <= percentage < 60:
            category.append("45_to_60")
        elif 60 <= percentage < 75:
            category.append("60_to_75")
        elif 75 <= percentage < 90:
            category.append("75_to_90")
        else:
            category.append("90_to_100")

    df["category"] = category

    output = io.StringIO()
    df.to_csv(output, sep='\t', header=True, index=False)
    output.seek(0)
    copy_query = "COPY overall_result FROM STDOUT csv DELIMITER '\t' NULL ''  ESCAPE '\\' HEADER "
    curr.copy_expert(copy_query, output)
    conn.commit()
