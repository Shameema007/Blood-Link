from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "bloodlink_secret"

DB_NAME = "database.db"
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        phone TEXT NOT NULL,
        city TEXT NOT NULL,
        last_donation TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        hospital TEXT NOT NULL,
        city TEXT NOT NULL,
        phone TEXT NOT NULL,
        urgency TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register_donor():
    if request.method == "POST":
        name = request.form["name"]
        blood_group = request.form["blood_group"]
        phone = request.form["phone"]
        city = request.form["city"]
        last_donation = request.form["last_donation"]

        if not name or not blood_group or not phone or not city:
            flash("Please fill all required fields", "error")
            return redirect(url_for("register_donor"))

        conn = get_db()
        conn.execute(
            "INSERT INTO donors (name, blood_group, phone, city, last_donation) VALUES (?, ?, ?, ?, ?)",
            (name, blood_group, phone, city, last_donation)
        )
        conn.commit()
        conn.close()

        flash("Donor registered successfully!", "success")
        return redirect(url_for("home"))

    return render_template("donor_register.html")

@app.route("/request", methods=["GET", "POST"])
def request_blood():
    if request.method == "POST":
        name = request.form["name"]
        blood_group = request.form["blood_group"]
        hospital = request.form["hospital"]
        city = request.form["city"]
        phone = request.form["phone"]
        urgency = request.form["urgency"]

        conn = get_db()
        conn.execute(
            "INSERT INTO requests (name, blood_group, hospital, city, phone, urgency) VALUES (?, ?, ?, ?, ?, ?)",
            (name, blood_group, hospital, city, phone, urgency)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("match_donors", blood_group=blood_group, city=city, urgency=urgency))

    return render_template("request_blood.html")

@app.route("/donors")
def match_donors():
    blood_group = request.args.get("blood_group")
    city = request.args.get("city")
    urgency = request.args.get("urgency")

    conn = get_db()
    if city:
        donors = conn.execute(
            "SELECT * FROM donors WHERE blood_group=? AND city LIKE ?",
            (blood_group, f"%{city}%")
        ).fetchall()
    else:
        donors = conn.execute(
            "SELECT * FROM donors WHERE blood_group=?",
            (blood_group,)
        ).fetchall()

    conn.close()
  
    return render_template("donors_list.html", donors=donors, blood_group=blood_group, city=city, urgency=urgency)
if __name__ == "__main__":
    app.run(debug=True)