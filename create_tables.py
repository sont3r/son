import psycopg2
import os
from config import Config

# Get database URL from config
db_url = os.environ.get('DATABASE_URL') or Config.SQLALCHEMY_DATABASE_URI

# Parse the database URL to get connection parameters
if db_url.startswith('postgresql://'):
    # Format: postgresql://username:password@host:port/database
    parts = db_url.replace('postgresql://', '').split('@')
    credentials = parts[0].split(':')
    connection = parts[1].split('/')
    
    if ':' in connection[0]:  # If port is specified
        host, port = connection[0].split(':')
    else:
        host = connection[0]
        port = 5432
    
    user = credentials[0]
    password = credentials[1]
    database = connection[1]
else:
    print(f"Unsupported database URL format: {db_url}")
    exit(1)

# Read SQL from db.sql file
with open('db.sql', 'r') as file:
    sql_script = file.read()

# Connect to the database and execute the SQL
try:
    conn = psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
    
    # Create a cursor
    cursor = conn.cursor()
    
    # Execute the SQL script
    cursor.execute(sql_script)
    
    # Commit the changes
    conn.commit()
    
    print("Database tables created successfully using SQL script")
    
except Exception as e:
    print(f"Error creating tables: {e}")
    
finally:
    # Close the cursor and connection
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()