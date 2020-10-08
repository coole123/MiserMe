from flask import Flask, render_template, redirect, request, session
from flask_session import Session 
from helpers import login_required

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
@login_required
def index():
    """ Show the available monthly funds, fixed expenses, and total left """
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Login the User """
    
    # Forget any user_id
    session.clear()

    # If the request is GET, return the login.html
    if request.method == "GET":
        return render_template("login.html")
    else:
        return render_template("index.html")