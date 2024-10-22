from helper import read_config, connect, preprocessing, into_db

config = read_config()
conn, curr = connect(config["hostname"], config["port"], config["username"], config["password"], config["db_name"])

preprocessing(config["data_dir"], config["processed_dir"])
into_db(conn, curr, config["processed_dir"])
