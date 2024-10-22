from helper import create_db, read_config, connect, create_tables, close_connection

config = read_config()
# try:
#     conn, curr = connect(config["hostname"], config["port"], config["username"], config["password"], config["db_name"])
#     create_tables(curr)
#     close_connection(conn)
# except:
#     print("Database please update config file accordingly")
create_db(config["hostname"], config["port"], config["username"], config["password"], config["db_name"])
conn, curr = connect(config["hostname"], config["port"], config["username"], config["password"], config["db_name"])
create_tables(curr)
close_connection(conn)
