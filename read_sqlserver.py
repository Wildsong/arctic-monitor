import pandas as pd
import pyodbc

class ReadSqlServer(object):

    def __init__(self: object, connstr: str) -> None:
        self.conn = pyodbc.connect(connstr)
        pass
        
    def read(self: object) -> str:
        query=f"""SELECT TOP (20) 
            [compress_start]
            ,[start_state_count]
            ,[compress_end]
            ,[end_state_count]
            ,[compress_status]
        FROM [sde].[SDE_compress_log]
        ORDER BY [compress_id] DESC"""

        return pd.read_sql(query, self.conn)

    def close(self: object) -> None:
        del self.conn
        return
    
if __name__ == "__main__":
    from config import Config

    # Install driver
    # https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=debian18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline#microsoft-odbc-driver-13-for-sql-server
    driver = "ODBC Driver 18 for SQL Server"

    conn = f"Driver={driver};Server={Config.DBSERVER};Database={Config.DATABASE};uid={Config.DBUSER};pwd={Config.DBPASSWORD};Encrypt=No;"
    r = ReadSqlServer(conn)
    df = r.read()
    print(df.to_html())
