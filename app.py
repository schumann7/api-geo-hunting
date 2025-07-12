import os
from time import time
from psycopg2 import pool
from dotenv import load_dotenv
from flask import Flask, jsonify

app = Flask(__name__)

# Load .env file
load_dotenv()

# Get the connection string from the environment variable
connection_string = os.getenv('DATABASE_URL')

# Create a connection pool
connection_pool = pool.SimpleConnectionPool(
    1,  # Minimum number of connections in the pool
    10,  # Maximum number of connections in the pool
    connection_string
)

# Check if the pool was created successfully
if connection_pool:
    print("Connection pool created successfully")

# Close all connections in the pool
# connection_pool.closeall()

def get_db_connection():
    conn = connection_pool.getconn()
    return conn

@app.route("/")
def index():
    conn = get_db_connection()

    # Create a cursor object
    cur = conn.cursor()

    # Execute SQL commands to retrieve the current time and version from PostgreSQL
    cur.execute('SELECT NOW();')
    time = cur.fetchone()[0]

    cur.execute('SELECT version();')
    version = cur.fetchone()[0]

    # Close the cursor and return the connection to the pool
    cur.close()
    connection_pool.putconn(conn)
    return {"message": "A API está rodando",
            "Current time": time,  
            "PostgreSQL version": version}


@app.route("/dados")
def dados():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM salas;")
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    result = [dict(zip(colnames, row)) for row in rows]
    cur.close()
    connection_pool.putconn(conn)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)