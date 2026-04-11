from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ================= DATABASE INIT =================
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

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

# ================= API ENDPOINT =================
@app.route('/log', methods=['POST'])
def log():
    data = request.json

    name = data.get("name", "Unknown")
    status = data.get("status", "UNKNOWN")
    method = data.get("method", "")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO logs (name, status, method, time)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        status,
        method,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "saved"})

# ================= MODERN DASHBOARD =================
@app.route('/logs')
def logs():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT name, status, method, time FROM logs ORDER BY id DESC")
    data = c.fetchall()

    conn.close()

    html = """
    <html>
    <head>
        <title>Biometric Dashboard</title>

        <style>
            body {
                margin: 0;
                font-family: Arial;
                background: #0f172a;
                color: white;
            }

            h1 {
                text-align: center;
                padding: 20px;
                color: #38bdf8;
            }

            .container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
                gap: 15px;
                padding: 20px;
            }

            .card {
                background: #1e293b;
                padding: 15px;
                border-radius: 12px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                transition: 0.3s;
            }

            .card:hover {
                transform: scale(1.03);
            }

            .name {
                font-size: 18px;
                font-weight: bold;
                color: #facc15;
            }

            .status {
                margin-top: 8px;
                display: inline-block;
                padding: 5px 10px;
                border-radius: 6px;
                font-weight: bold;
            }

            .APPROVED {
                background: #16a34a;
                color: white;
            }

            .DENIED {
                background: #dc2626;
                color: white;
            }

            .meta {
                margin-top: 10px;
                font-size: 12px;
                color: #cbd5e1;
                line-height: 1.5;
            }
        </style>
    </head>

    <body>
        <h1>Biometric Attendance Dashboard</h1>
        <div class="container">
    """

    for row in data:
        html += f"""
        <div class="card">
            <div class="name">{row[0]}</div>

            <div class="status {row[1]}">
                {row[1]}
            </div>

            <div class="meta">
                Method: {row[2]}<br>
                Time: {row[3]}
            </div>
        </div>
        """

    html += """
        </div>
    </body>
    </html>
    """

    return html


# ================= RUN SERVER =================
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)