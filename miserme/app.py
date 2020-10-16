from flask import Flask, render_template, redirect, request, session
from flask_session import Session 
import sqlite3
from helpers import login_required
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

conn = sqlite3.connect('registrants.db', check_same_thread=False)
c = conn.cursor()

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Login the User """
    
    session.clear()

    # If the request is GET, return the login.html
    if request.method == "GET":
        return render_template("login.html")
    # Otherwise, search the inputted username and password inside the registrants.db
    else:
        # if username or password is empty, return error page
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("errorpage.html")
        # elif look through database for the username and password
        c.execute("SELECT * FROM registrants WHERE username = :username", {"username": request.form.get("username")})
        results = c.fetchall()

        # check that the user exists in the database and the password matches
        if len(results) != 1 or not check_password_hash(results[0][2], request.form.get("password")):
            return render_template("errorpage.html")
        
        # recognize the user based on id
        session["user_id"] = results[0][0]
        return redirect("/")
        

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register a New User """
    if request.method == "GET":
        return render_template("register.html")
    else:
        if request.form.get("username") == "" or request.form.get("password") == "":
            return render_template("errorpage.html")
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("errorpage.html")
        else:
            username = request.form.get("username")
            hashing = generate_password_hash(request.form.get("password"))
            default = 0
            try:
                c.execute("INSERT INTO registrants (username, password, funds) VALUES (?, ?, ?)", (username, hashing, default))
                conn.commit()
            except:
                return render_template("error_user_exists.html")
            
            return render_template("/register_success.html")

@app.route("/")
@login_required
def index():
    """ Show the available monthly funds, fixed expenses, and total left """
    return render_template("index.html")