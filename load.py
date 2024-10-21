import yaml
import pandas as pd
import os

with open("./config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

dataDir = config["data_dir"]

for file in dataDir:
    pass
