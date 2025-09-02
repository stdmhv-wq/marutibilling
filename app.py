from flask import Flask, render_template, request, redirect, url_for, session
from db import get_db, close_db   # 👈 db.py માંથી functions import
import os

# ----------------- Flask Setup -----------------
app = Flask(__name__)
app.secret_key = "marutibilling_demo"

# ----------------- Upload Folder ----------------
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------- DB Close Setup ----------------
@app.teardown_appcontext
def teardown_db(exception):
    close_db()

# ----------------- ROUTES -----------------

# Login Page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s AND is_verified=1",
                    (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("companies"))
        else:
            return render_template("login.html", error="❌ Invalid credentials or not verified!")

    return render_template("login.html")


# Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""INSERT INTO users (fullname, email, mobile, username, password, is_verified) 
                       VALUES (%s, %s, %s, %s, %s, 1)""",
                    (fullname, email, mobile, username, password))
        conn.commit()
        cur.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# Companies List
@app.route("/companies")
def companies():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM companies WHERE user_id=%s", (session["user_id"],))
    companies = cur.fetchall()
    cur.close()

    return render_template("companies.html", companies=companies)


# Add Company
@app.route("/companies/add", methods=["GET", "POST"])
def add_company():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        gst = request.form["gst"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        address = request.form["address"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""INSERT INTO companies (user_id, name, gst_number, email, mobile, address) 
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (session["user_id"], name, gst, email, mobile, address))
        conn.commit()
        cur.close()

        return redirect(url_for("companies"))

    return render_template("add_company.html")


# Edit Company
@app.route("/companies/edit/<int:id>", methods=["GET", "POST"])
def edit_company(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["name"]
        gst = request.form["gst"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        address = request.form["address"]

        cur.execute("""UPDATE companies SET name=%s, gst_number=%s, email=%s, mobile=%s, address=%s 
                       WHERE id=%s AND user_id=%s""",
                    (name, gst, email, mobile, address, id, session["user_id"]))
        conn.commit()
        cur.close()
        return redirect(url_for("companies"))

    cur.execute("SELECT * FROM companies WHERE id=%s AND user_id=%s", (id, session["user_id"]))
    company = cur.fetchone()
    cur.close()

    return render_template("edit_company.html", company=company)


# Delete Company
@app.route("/companies/delete/<int:id>")
def delete_company(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM companies WHERE id=%s AND user_id=%s", (id, session["user_id"]))
    conn.commit()
    cur.close()

    return redirect(url_for("companies"))


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ----------------- RUN APP -----------------
if __name__ == "__main__":
    app.run(debug=True)
