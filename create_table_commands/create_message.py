import pyodbc
from dotenv import load_dotenv
import os

def create_messages_table():
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

        # Create Messages table
        create_table_query = """
        CREATE TABLE Messages (
            message_id UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
            session_id UNIQUEIDENTIFIER NOT NULL,
            user_message NVARCHAR(MAX) NOT NULL,
            assistant_message NVARCHAR(MAX),
            created_at DATETIME2 DEFAULT GETDATE(),
            FOREIGN KEY (session_id) REFERENCES Sessions(session_id)
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ Messages table created successfully!")
        
        # Close connection
        cursor.close()
        conn.close()
            
    except Exception as e:
        print("❌ Failed to create table!")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    create_messages_table()