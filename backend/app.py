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
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  balance REAL DEFAULT 0)''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    name = data.get('name')
    email = data.get('email')
    balance = data.get('balance', 0)
    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (name,email,balance) VALUES (?,?,?)",
                  (name, email, balance))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "email already exists"}), 409

@app.route('/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, email, balance FROM users")
    rows = c.fetchall()
    conn.close()
    users = [{"id": r[0], "name": r[1], "email": r[2], "balance": r[3]} for r in rows]
    return jsonify(users), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
