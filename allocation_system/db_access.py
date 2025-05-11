import pyodbc
import pandas as pd
from allocation_system.config_env import EnvConfig

def get_connection():
    env_config = EnvConfig()
    
    driver  = "SQL Anywhere 17"
    DSN = env_config.get("DSN")
    DBUID = env_config.get("DBUID")
    DBPWD = env_config.get("DBPWD")
    DATABASENAME = env_config.get("DATABASENAME")
    ENGINENAME = env_config.get("ENGINENAME")
    AUTOSTOP = env_config.get("AUTOSTOP")
    
    conn_str = (
        f"Driver={driver};"
        f"UID={DBUID};"
        f"PWD={DBPWD};"
        f"ENG={ENGINENAME};"
        f"DBN={DATABASENAME};"
        f"LINKS=TCPIP;"
        f"AUTOSTOP={AUTOSTOP};"
    )
    
    return pyodbc.connect(conn_str)
    
def fetch_dataframe(sqlstr, LOGGER):
    LOGGER.debug(f"実行SQL: {sqlstr}")
    with get_connection() as conn:
        df = pd.read_sql(sqlstr, conn)
    return df