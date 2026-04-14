from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB = "database.db"

# ================= INIT DB =================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            name TEXT PRIMARY KEY,
            role TEXT,
            finger_id INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            status TEXT,
            method TEXT,
            time TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= USERS =================
@app.route("/users", methods=["GET"])
def get_users():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT name, role, finger_id FROM users")
    data = c.fetchall()
    conn.close()

    return jsonify([
        {"name": r[0], "role": r[1], "id": r[2]}
        for r in data
    ])


@app.route("/users", methods=["POST"])
def add_user():
    data = request.json

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        INSERT OR REPLACE INTO users VALUES (?, ?, ?)
    """, (
        data.get("name"),
        data.get("role"),
        data.get("id", 0)
    ))

    conn.commit()
    conn.close()

    return jsonify({"msg": "user added"})


@app.route("/users/<name>", methods=["DELETE"])
def delete_user(name):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("DELETE FROM users WHERE name=?", (name,))
    conn.commit()
    conn.close()

    return jsonify({"msg": "deleted"})


# ================= LOGS =================
@app.route("/log", methods=["POST"])
def log():
    data = request.json

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        INSERT INTO logs (name, status, method, time)
        VALUES (?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("status"),
        data.get("method", "FACE+FP"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return jsonify({"msg": "saved"})


# ================= DASHBOARD =================
@app.route("/")
def dashboard():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT name, role FROM users")
    users = c.fetchall()

    c.execute("SELECT name, status, method, time FROM logs ORDER BY id DESC")
    logs = c.fetchall()

    conn.close()

    html = """
    <html>
    <head>
    <title>Novlex Employees</title>

    <style>
        body {
            margin: 0;
            font-family: Arial;
            overflow-x: hidden;

            background: linear-gradient(-45deg,
                #ff4d6d,
                #ff8fa3,
                #c77dff,
                #4cc9f0
            );
            background-size: 400% 400%;
            animation: bg 10s ease infinite;
        }

        @keyframes bg {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        h1 {
            text-align: center;
            color: white;
            padding: 18px;
            letter-spacing: 2px;
        }

        .search {
            text-align: center;
            margin-bottom: 10px;
        }

        input {
            padding: 10px;
            width: 55%;
            border-radius: 12px;
            border: none;
            outline: none;
        }

        .container {
            display: flex;
            flex-wrap: wrap;
            gap: 18px;
            justify-content: center;
            padding: 20px;
        }

        .card {
            width: 340px;
            background: rgba(255,255,255,0.92);
            border-radius: 18px;
            padding: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.25);
            backdrop-filter: blur(8px);
        }

        .name {
            font-size: 20px;
            font-weight: bold;
            color: #0f172a;
        }

        .role {
            font-size: 13px;
            color: #64748b;
            margin-bottom: 10px;
        }

        .log {
            background: #f8fafc;
            margin-top: 6px;
            padding: 8px;
            border-radius: 10px;
            font-size: 12px;
            border-left: 4px solid #94a3b8;
        }

        .APPROVED { border-left: 4px solid #22c55e; }
        .DENIED { border-left: 4px solid #ef4444; }

        button {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            border: none;
            border-radius: 10px;
            background: #ef4444;
            color: white;
            cursor: pointer;
        }
    </style>

    <script>
        function searchEmployee(){
            let input = document.getElementById("search").value.toLowerCase();
            let cards = document.getElementsByClassName("card");

            for(let c of cards){
                let name = c.getAttribute("data-name");
                c.style.display = name.includes(input) ? "block" : "none";
            }
        }

        async function deleteUser(name){
            await fetch("/users/" + name, {method:"DELETE"});
            location.reload();
        }
    </script>

    </head>

    <body>

    <h1>Novlex Employees</h1>

    <div class="search">
        <input id="search" onkeyup="searchEmployee()" placeholder="Search employee...">
    </div>

    <div class="container">
    """

    # ================= EMPLOYEE CARDS =================
    for u in users:
        name = u[0]
        role = u[1]

        html += f"""
        <div class="card" data-name="{name.lower()}">

            <div class="name">{name}</div>
            <div class="role">{role}</div>

            <b>Attendance</b>
        """

        user_logs = [l for l in logs if l[0] == name]

        if not user_logs:
            html += "<div class='log'>No attendance yet</div>"

        for l in user_logs:
            html += f"""
            <div class="log {l[1]}">
                {l[1]} | {l[2]}<br>
                {l[3]}
            </div>
            """

        html += f"""
            <button onclick="deleteUser('{name}')">Delete</button>
        </div>
        """

    html += """
    </div>
    </body>
    </html>
    """

    return html


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)