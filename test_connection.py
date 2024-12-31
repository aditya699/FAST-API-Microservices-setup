import pyodbc
from dotenv import load_dotenv
import os

def test_sql_connection():
    try:
        # Load environment variables
        load_dotenv()
        
        # Get connection details
        server = os.getenv("SQL_SERVER")
        database = os.getenv("SQL_DATABASE")
        username = os.getenv("SQL_USERNAME")
        password = os.getenv("SQL_PASSWORD")

        # Create direct connection string (similar to SSMS)
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        
        # Test connection
        conn = pyodbc.connect(conn_str)
        print("✅ Successfully connected to database!")
        print("Connection test complete!")
        conn.close()
            
    except Exception as e:
        print("❌ Connection failed!")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_sql_connection()