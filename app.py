from flask import Flask, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "clave_super_segura_123"

# ----------------- DB -----------------
def init_db():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS inscritos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        telefono TEXT,
        email TEXT,
        objetivo TEXT
    )
    """)

    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username, password) VALUES (?,?)",
                    ("admin", "1234"))

    conn.commit()
    conn.close()

init_db()

# ----------------- HOME (MÓVIL) -----------------
@app.route("/")
def home():
    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>
    body {
        margin:0;
        font-family:Arial;
        background:#0b1220;
        color:white;
    }

    .header {
        padding:25px;
        text-align:center;
        background:linear-gradient(135deg,#0ea5e9,#6366f1);
    }

    .container {
        max-width:600px;
        margin:auto;
        padding:15px;
    }

    .card {
        background:#111827;
        padding:15px;
        margin:10px 0;
        border-radius:15px;
        box-shadow:0 10px 20px rgba(0,0,0,0.3);
    }

    input, select {
        width:100%;
        padding:12px;
        margin:6px 0;
        border-radius:10px;
        border:none;
        background:#0b1220;
        color:white;
        font-size:16px;
    }

    button {
        width:100%;
        padding:14px;
        border:none;
        border-radius:12px;
        background:linear-gradient(135deg,#0ea5e9,#6366f1);
        color:white;
        font-weight:bold;
        font-size:16px;
    }

    a { color:#38bdf8; text-decoration:none; }

    .bar {
        position:fixed;
        bottom:0;
        left:0;
        right:0;
        background:#111827;
        display:flex;
        justify-content:space-around;
        padding:10px;
        border-top:1px solid #1f2937;
    }
    </style>

    <div class="header">
        <h1>🐺 Black Jackals</h1>
        <p>Running Team</p>
        <a href="/login">Admin</a>
    </div>

    <div class="container">

    <div class="card">
        <h2>Planes</h2>
        <p>5K • 10K • Trail • Ultra</p>
        <p>Total inscritos: """ + str(total()) + """</p>
    </div>

    <div class="card">
        <h2>Anotate</h2>

        <form action="/enviar" method="POST">

        <input name="nombre" placeholder="Nombre">
        <input name="telefono" placeholder="Telefono">
        <input name="email" placeholder="Email">

        <select name="objetivo">
            <option>5K</option>
            <option>10K</option>
            <option>Trail</option>
            <option>Ultra</option>
        </select>

        <button>Unirme</button>

        </form>
    </div>

    </div>

    <div class="bar">
        <a href="/">🏠</a>
        <a href="/admin">👤</a>
        <a href="/login">⚙️</a>
    </div>
    """

# ----------------- TOTAL -----------------
def total():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM inscritos")
    t = cur.fetchone()[0]
    conn.close()
    return t

# ----------------- ENVIAR -----------------
@app.route("/enviar", methods=["POST"])
def enviar():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO inscritos (nombre, telefono, email, objetivo)
    VALUES (?,?,?,?)
    """, (
        request.form["nombre"],
        request.form["telefono"],
        request.form["email"],
        request.form["objetivo"]
    ))

    conn.commit()
    conn.close()

    return redirect("/")

# ----------------- LOGIN -----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["user"] == "admin" and request.form["password"] == "1234":
            session["admin"] = True
            return redirect("/admin")
        return "❌ error login"

    return """
    <h1>Login Admin</h1>
    <form method="POST">
        <input name="user" placeholder="usuario"><br><br>
        <input name="password" type="password" placeholder="password"><br><br>
        <button>Entrar</button>
    </form>
    """

# ----------------- ADMIN -----------------
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM inscritos")
    data = cur.fetchall()
    conn.close()

    lista = ""
    for d in data:
        lista += f"""
        <div style='background:#111827;padding:10px;margin:10px;border-radius:10px;'>
        <b>{d[1]}</b> - {d[4]} <br>
        📞 {d[2]} | ✉ {d[3]} <br>
        <a href="/delete/{d[0]}">Eliminar</a>
        </div>
        """

    return f"""
    <h1>Panel Admin 🧠</h1>
    <a href="/logout">Salir</a>
    <hr>
    {lista}
    """

# ----------------- DELETE -----------------
@app.route("/delete/<int:id>")
def delete(id):
    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM inscritos WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")

# ----------------- LOGOUT -----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ----------------- RUN -----------------
if __name__ == "__main__":
    app.run(debug=True)
