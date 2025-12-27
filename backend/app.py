from flask import Flask, request, jsonify
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite')

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  balance REAL DEFAULT 0)''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    balance = data.get('balance', 0)
    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (username,password,balance) VALUES (?,?,?)",
                  (username, password, balance))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "username already exists"}), 409

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        return jsonify({"status": "login success",
                        "user": {"id": user[0], "username": user[1], "balance": user[3]}})
    else:
        return jsonify({"error": "invalid credentials"}), 401

@app.route('/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, balance FROM users")
    rows = c.fetchall()
    conn.close()
    users = [{"id": r[0], "username": r[1], "balance": r[2]} for r in rows]
    return jsonify(users), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
