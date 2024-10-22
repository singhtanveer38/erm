import yaml
import numpy as np
import pandas as pd
import os

def preprocessing():
    with open("./config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

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

def into_db(conn, curr):
