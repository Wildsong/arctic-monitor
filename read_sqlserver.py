import pandas as pd
import pyodbc

# Install driver
# https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=debian18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline#microsoft-odbc-driver-13-for-sql-server

#driver = "{SQL Server Native Client 11.0}" # Windows 
driver = "ODBC Driver 18 for SQL Server"

class ReadSqlServer(object):

    def __init__(self, database) -> None:
        servername = "cc-sqlservers"
        self.conn = pyodbc.connect(
                f"Driver={driver};"
                f"Server={servername};"
                f"Database={database};"
                "uid=bwilson;pwd=to live is to suffer;"
                "TrustedServerCertificate=yes;"
        )
        
    def read(self):
        query=f"""SELECT TOP (10) 
            [compress_start]
            ,[start_state_count]
            ,[compress_end]
            ,[end_state_count]
            ,[compress_status]
        FROM [{database}].[sde].[SDE_compress_log]
        ORDER BY [compress_id] DESC"""

        return pd.read_sql(query, self.conn)

    def close(self):
        del self.conn
        return
    
if __name__ == "__main__":

    database = 'Clatsop'
    r = ReadSqlServer(database)
    df = r.read()
    print(df.to_html())
