import os
from psycopg2 import pool
from dotenv import load_dotenv
from flask import Flask, jsonify, request
import random
import string

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

def get_db_connection():
    conn = connection_pool.getconn()
    return conn

# Generate a unique ID for the room
def generate_id():
    caracteres = string.ascii_uppercase + string.digits
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check in database to ensure that the generated ID is not already in use
    # Loop until a unique ID is found
    while True:
        codigo = ''.join(random.choices(caracteres, k=4))
        cur.execute("SELECT id FROM salas WHERE id = %s", (codigo,))
        if not cur.fetchone():
            break

    cur.close()
    conn.close()
    return codigo

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
    return jsonify({"message": "A API está rodando corretamente!",
            "Current time": time,
            "PostgreSQL version": version})


@app.route("/find_rooms", methods=["GET"])
def find_rooms():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM salas;")
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    result = [dict(zip(colnames, row)) for row in rows]
    cur.close()
    connection_pool.putconn(conn)
    return jsonify(result)

@app.route("/create_room", methods=["POST"])
def create_room():
    data = request.get_json()
    
    required_fields = ["nomedasala", "privada", "latitude", "longitude"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo obrigatório faltando: {field}"}), 400

    # Password validation for private rooms
    if data["privada"] and ("senha" not in data or data["senha"] is None):
        return jsonify({"error": "Senha obrigatória para salas privadas"}), 400

    try:
        # Generate a unique ID for the room
        generated_id = generate_id()

        conn = get_db_connection()
        cur = conn.cursor()

        # Insert the new room into the database
        cur.execute("""
            INSERT INTO salas (id, nomedasala, privada, senha, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (generated_id, data['nomedasala'], data['privada'], data.get('senha'), data['latitude'], data['longitude']))
        conn.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        connection_pool.putconn(conn)

    data['id'] = generated_id
    return jsonify({"message": "Sala criada com sucesso!", "data": data}), 201


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)