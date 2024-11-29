from flask import Flask, render_template, request, jsonify
from cryptography.fernet import Fernet
import sqlite3
import os

app = Flask(__name__)

# Encryption key generation or loading
KEY_FILE = "encryption.key"
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
else:
    with open(KEY_FILE, "rb") as key_file:
        key = key_file.read()
cipher = Fernet(key)

# Database initialization
DB_FILE = "password_manager.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_password():
    data = request.json
    service = data.get("service")
    username = data.get("username")
    password = data.get("password")
    
    if not service or not username or not password:
        return jsonify({"error": "All fields are required!"}), 400

    encrypted_password = cipher.encrypt(password.encode()).decode()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)",
                   (service, username, encrypted_password))
    conn.commit()
    conn.close()

    return jsonify({"message": "Password generated and stored successfully!"})

@app.route("/retrieve", methods=["POST"])
def retrieve_password():
    data = request.json
    service = data.get("service")
    username = data.get("username")
    
    if not service or not username:
        return jsonify({"error": "Service and Username are required!"}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM passwords WHERE service = ? AND username = ?", (service, username))
    result = cursor.fetchone()
    conn.close()

    if result:
        decrypted_password = cipher.decrypt(result[0].encode()).decode()
        return jsonify({"password": decrypted_password})

    return jsonify({"error": "No matching entry found."}), 404

@app.route("/delete", methods=["POST"])
def delete_password():
    data = request.json
    service = data.get("service")
    username = data.get("username")

    if not service or not username:
        return jsonify({"error": "Service and Username are required!"}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM passwords WHERE service = ? AND username = ?", (service, username))
    conn.commit()
    conn.close()

    return jsonify({"message": "Password deleted successfully!"})

if __name__ == "__main__":
    app.run(debug=True)
