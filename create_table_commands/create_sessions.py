import pyodbc
from dotenv import load_dotenv
import os

def create_sessions_table():
    try:
        # Load environment variables
        load_dotenv()
        
        # Get connection details
        server = os.getenv("SQL_SERVER")
        database = os.getenv("SQL_DATABASE")
        username = os.getenv("SQL_USERNAME")
        password = os.getenv("SQL_PASSWORD")

        # Create connection string
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        
        # Connect to database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Create Sessions table
        create_table_query = """
        CREATE TABLE Sessions (
            session_id UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
            user_id UNIQUEIDENTIFIER NOT NULL,
            created_at DATETIME2 DEFAULT GETDATE(),
            expires_at DATETIME2 NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ Sessions table created successfully!")
        
        # Close connection
        cursor.close()
        conn.close()
            
    except Exception as e:
        print("❌ Failed to create table!")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    create_sessions_table()