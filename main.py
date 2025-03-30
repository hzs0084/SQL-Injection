from flask import Flask, request
import sqlite3
import datetime
import json
import os

app = Flask(__name__)

# Setup SQLite and secret flag
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    c.execute("INSERT INTO users (username, password) VALUES ('admin', 'SuperSecret123')")
    c.execute("INSERT INTO users (username, password) VALUES ('ctf_user', 'flag{bl1nd_sql_master}')")
    conn.commit()
    conn.close()

@app.route('/')
@app.route('/')
def index():
    return '''
        <h2>Login</h2>
        <form action="/login" method="get">
            Username: <input name="username"><br>
            <input type="submit" value="Login">
        </form>

        <h3>💡 Hints (click to reveal)</h3>
        <div onclick="toggleHint(1)" style="cursor:pointer; border:1px solid #aaa; padding:10px; margin:10px; border-radius:8px;">
            Hint 1: <span id="hint1" style="display:none;">Just because you don't see anything doesn’t mean you're blind.</span>
        </div>
        <div onclick="toggleHint(2)" style="cursor:pointer; border:1px solid #aaa; padding:10px; margin:10px; border-radius:8px;">
            Hint 2: <span id="hint2" style="display:none;">Ask the right question, and the database will whisper its secrets.</span>
        </div>
        <div onclick="toggleHint(3)" style="cursor:pointer; border:1px solid #aaa; padding:10px; margin:10px; border-radius:8px;">
            Hint 3: <span id="hint3" style="display:none;">I'm not a sadist but you have to manually carve the flag out using <code>substr</code>.</span>
        </div>
        <div onclick="toggleHint(4)" style="cursor:pointer; border:1px solid #aaa; padding:10px; margin:10px; border-radius:8px;">
            Hint 4: <span id="hint4" style="display:none;">The name of the table is users and the flag is behing ctf_user</span>
        </div>

        <script>
            function toggleHint(num) {
                var hint = document.getElementById('hint' + num);
                hint.style.display = (hint.style.display === 'none') ? 'inline' : 'none';
            }
        </script>
    '''


# Logs each attempt to logs.json
def log_attempt(username_input, query, ip):
    log_entry = {
        "timestamp": str(datetime.datetime.now()),
        "ip": ip,
        "input": username_input,
        "query": query
    }

    # Create logs.json if it doesn't exist
    if not os.path.exists("logs.json"):
        with open("logs.json", "w") as f:
            json.dump([], f)

    # Read existing logs
    with open("logs.json", "r") as f:
        logs = json.load(f)

    # Append the new log
    logs.append(log_entry)

    # Write back to file
    with open("logs.json", "w") as f:
        json.dump(logs, f, indent=2)

@app.route('/login')
def login():
    username = request.args.get('username', '')
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Vulnerable query
    query = f"SELECT * FROM users WHERE username = '{username}'"

    # Log the injection attempt
    log_attempt(username, query, request.remote_addr)

    try:
        c.execute(query)
        result = c.fetchone()
    except sqlite3.OperationalError as e:
        conn.close()
        return f"SQL Error: {e}"

    conn.close()

    if result:
        return "Welcome!"
    else:
        return "User not found."

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
