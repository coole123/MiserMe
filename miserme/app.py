from flask import Flask, render_template, redirect, request, session, Response
from flask_session import Session 
import sqlite3
from helpers import login_required, usd
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
    c.execute("SELECT funds_id, txn_name, date, predicted_cost, true_cost, funds_added, notes FROM finances WHERE user_id = :user_id", {"user_id": session["user_id"]})
    rows = c.fetchall()

    funds_snapshot = []

    for row in rows:
        funds_snapshot.append({
            "funds_id": row[0],
            "name": row[1],
            "date": row[2],
            "predict": usd(row[3]),
            "true": usd(row[4]),
            "added": usd(row[5]),
            "notes": row[6]
        })
    
    c.execute("SELECT funds, budget FROM registrants WHERE id = :user_id", {"user_id": session["user_id"]})
    rows = c.fetchall()
    current_funds = usd(rows[0][0])
    budget = usd(rows[0][1])
    
    return render_template("index.html", funds_snapshot=funds_snapshot, current_funds=current_funds, budget=budget)

@app.route("/start_budget", methods=["GET", "POST"])
@login_required
def start_budget():
    """ Have the user begin the budget by inputting starting budget, starting funds """
    if request.method == "GET":
        return render_template("start_budget.html")
    else:
        user_budget = request.form.get("user_budget")

        c.execute("UPDATE registrants SET budget = :user_budget WHERE id = :user_id", {"user_budget": user_budget, "user_id": session["user_id"]})
        c.execute("UPDATE registrants SET funds = :user_budget WHERE id = :user_id", {"user_budget": user_budget, "user_id": session["user_id"]})
        c.execute("DELETE FROM finances WHERE user_id = :user_id", {"user_id": session["user_id"]})
        conn.commit()
        c.execute("DELETE FROM history WHERE user_id = :user_id", {"user_id": session["user_id"]})
        conn.commit()

        history_query = "Started the budget with %s." % user_budget

        c.execute("INSERT INTO history (user_id, notes) VALUES (?, ?)", (session["user_id"], history_query))
        conn.commit()
        return redirect("/")

@app.route("/add_funds", methods=["GET", "POST"])
@login_required
def add_funds():
    """ Allow the user to add more funds to their wallet. Useful in cases where user get unexpected income. """
    if request.method == "GET":
        return render_template("add_funds.html")
    else:
        added_funds = request.form.get("add_funds")
        special_note = request.form.get("special_note")

        c.execute("UPDATE registrants SET funds = funds + :added_funds WHERE id = :user_id", {"added_funds": added_funds, "user_id": session["user_id"]})

        c.execute("SELECT funds FROM registrants WHERE id = :user_id", {"user_id": session["user_id"]})
        rows = c.fetchall()
        new_funds = usd(rows[0][0])

        history_query = "Added %s to available funds. New total = %s. Note: %s" % (added_funds, new_funds, special_note)

        c.execute("INSERT INTO history (user_id, notes) VALUES (?, ?)", (session["user_id"], history_query))
        conn.commit()

        c.execute("""INSERT INTO finances (
            user_id, txn_name, 
            date, predicted_cost, 
            true_cost, funds_added, notes) 
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session["user_id"], "---", "---", "---", "---", added_funds, special_note))
        conn.commit()

        return redirect("/")

@app.route("/expense", methods=["GET", "POST"])
@login_required
def expense():
    """ Allow the user to log in an expense by filling out a short form that speaks to the finances database """
    if request.method == "GET":
        return render_template("expense.html")
    else:
        txn_name = request.form.get("txn_name")
        if txn_name == "":
                txn_name = "---"
        txn_date = request.form.get("txn_date")
        if txn_date == "":
            txn_date = "---"
        txn_p_cost = request.form.get("txn_p_cost")
        if txn_p_cost == "":
            txn_p_cost = "---"
        txn_t_cost = request.form.get("txn_t_cost")
        if txn_t_cost == "":
            txn_t_cost = "---"
        txn_notes = request.form.get("txn_notes")
        if txn_notes == "":
            txn_notes == "---"

        c.execute("INSERT INTO finances (user_id, txn_name, date, predicted_cost, true_cost, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (session["user_id"], txn_name, txn_date, txn_p_cost, txn_t_cost, txn_notes))
        conn.commit()

        history_query = "New Entry --> Name: %s | Date: %s | Predicted Cost: %s | True Cost: %s | Notes: %s" % (txn_name, txn_date, txn_p_cost, txn_t_cost, txn_notes)

        c.execute("INSERT INTO history (user_id, notes) VALUES (?, ?)", (session["user_id"], history_query))
        conn.commit()

        # Insert the new funds after subtracting an expense based on predicted or true cost
        c.execute("SELECT funds FROM registrants WHERE id = :user_id;", {"user_id": session["user_id"]})

        rows = c.fetchall()
        current_funds = float(rows[0][0])
        update_available_funds = 0

        if txn_p_cost != "---":
            update_available_funds = current_funds - float(txn_p_cost)
        elif txn_t_cost != "---":
            update_available_funds = current_funds - float(txn_t_cost)

        c.execute("UPDATE registrants SET funds = :update_available_funds WHERE id = :user_id", {"update_available_funds": update_available_funds, "user_id": session["user_id"]})
        conn.commit()
            
        return redirect("/")

@app.route("/history")
@login_required
def history():
    """ Allows the user to view past transactions made. Including adding funds and expenses. """
    
    c.execute(""" 
    SELECT notes, timestamp FROM history WHERE user_id = :user_id;
    """, {"user_id": session["user_id"]})

    rows = c.fetchall()
    entries = []

    for row in rows:
        entries.append({
            "notes": row[0],
            "timestamp": row[1]
        })

    return render_template("history.html", entries = entries)

@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    """ Take the current entry row and replace it with a new one """
    if request.method == "GET":
        
        rows = c.execute("""
        SELECT funds_id from finances
        WHERE user_id = :user_id
        AND funds_added = '---';
        """, {"user_id": session["user_id"]})

        return render_template("edit.html", entries = [ row[0] for row in rows ])
    else:
        old_entry = request.form.get("entry_id")

        # Add in the old costs to ensure accuracy when decrementing new costs
        c.execute("""
        SELECT predicted_cost, true_cost
        FROM finances
        WHERE funds_id = :funds_id
        AND
        user_id = :user_id;
        """, {"funds_id": old_entry, "user_id": session["user_id"]})

        rows = c.fetchall()
        old_costs = 0

        if isinstance(rows[0][0], float):
            old_costs += rows[0][0]
        if isinstance(rows[0][1], float):
            old_costs += rows[0][1]

        c.execute("UPDATE registrants SET funds = funds + :old_costs WHERE id = :user_id", {"old_costs": old_costs, "user_id": session["user_id"]})
        conn.commit()
        
        # Prevent the user from not selecting a entry to edit
        txn_name = request.form.get("txn_name")
        if txn_name == "":
                txn_name = "---"
        txn_date = request.form.get("txn_date")
        if txn_date == "":
            txn_date = "---"
        txn_p_cost = request.form.get("txn_p_cost")
        if txn_p_cost == "":
            txn_p_cost = "---"
        txn_t_cost = request.form.get("txn_t_cost")
        if txn_t_cost == "":
            txn_t_cost = "---"
        txn_notes = request.form.get("txn_notes")
        if txn_notes == "":
            txn_notes == "---"

        c.execute("""
        UPDATE finances
        SET txn_name = :txn_name,
            date = :date,
            predicted_cost = :predicted_cost,
            true_cost = :true_cost,
            notes = :notes
        WHERE
            funds_id = :funds_id
        AND
            user_id = :user_id;
        """, {"txn_name": txn_name, "date": txn_date, "predicted_cost": txn_p_cost, "true_cost": txn_t_cost, "notes": txn_notes, "funds_id": old_entry, "user_id": session["user_id"]})
        conn.commit()

        # Add the change to history
        history_query = "Changed Entry ID: %s. New entry data is (%s, %s, %s, %s, %s)." % (old_entry, txn_name, txn_date, txn_p_cost, txn_t_cost, txn_notes)

        c.execute("INSERT INTO history (user_id, notes) VALUES (?, ?)", (session["user_id"], history_query))
        conn.commit()

        # Update available funds if any changes were made to cost
        c.execute("SELECT funds FROM registrants WHERE id = :user_id;", {"user_id": session["user_id"]})

        rows = c.fetchall()
        current_funds = float(rows[0][0])
        update_available_funds = 0

        if txn_p_cost != "---":
            update_available_funds = current_funds - float(txn_p_cost)
        elif txn_t_cost != "---":
            update_available_funds = current_funds - float(txn_t_cost)

        c.execute("UPDATE registrants SET funds = :update_available_funds WHERE id = :user_id", {"update_available_funds": update_available_funds, "user_id": session["user_id"]})
        conn.commit()

        return redirect("/")

@app.route("/edit_added", methods=["GET", "POST"])
@login_required
def edit_added():
    if request.method == "GET":

        # Select all entries that have a funds_added data
        rows = c.execute("""
        SELECT funds_id FROM finances
        WHERE user_id = :user_id
        AND funds_added != '---';
        """, {"user_id": session["user_id"]})

        return render_template("edit_added.html", entries=[ row[0] for row in rows ])
    else:
        # Firstly, subtract the original amount from available funds
        old_funds_entry = request.form.get("entry_id")
        
        c.execute("""
        SELECT funds_added FROM finances
        WHERE funds_id = :funds_id
        AND user_id = :user_id
        """, {"funds_id": old_funds_entry, "user_id": session["user_id"]})

        rows = c.fetchall()
        old_funds_total = float(rows[0][0])

        c.execute("UPDATE registrants SET funds = funds - :old_funds_total WHERE id = :user_id", {"old_funds_total": old_funds_total, "user_id": session["user_id"]})
        conn.commit()

        # Replace the old amount with the new amount 
        new_funds_added = request.form.get("edited_funds")

        c.execute("""
        UPDATE finances
        SET funds_added = :new_funds_added
        WHERE funds_id = :funds_id
        AND user_id = :user_id
        """, {"new_funds_added": new_funds_added, "funds_id": old_funds_entry, "user_id": session["user_id"]})
        conn.commit()

        # Update the available funds with the new amount
        c.execute("""
        UPDATE registrants
        SET funds = funds + :new_funds_added
        WHERE id = :user_id
        """, {"new_funds_added": new_funds_added, "user_id": session["user_id"]})
        conn.commit()

        # Insert a new entry into history
        history_query = "Changed Entry ID: %s. Funds added changed to $%s." % (old_funds_entry, new_funds_added)

        c.execute("INSERT INTO history (user_id, notes) VALUES (?, ?)", (session["user_id"], history_query))
        conn.commit()

        return redirect("/")

@app.route("/download")
@login_required
def download():
    """ Allow the user to download a copy of the current expenses listed on the homepage """

    # c.execute(".headers on")
    # c.execute(".mode csv")
    # c.execute(".output miserme.csv")
    # c.execute("SELECT * FROM finances WHERE user_id = :user_id", {"user_id": session["user_id"]})
    # c.execute(".quit")

    c.execute("SELECT * FROM finances WHERE user_id = :user_id", {"user_id": session["user_id"]})
    download_file = c.fetchall()

    return Response(download_file, mimetype="text/csv")


@app.route("/logout")
def logout():
    """ Log the current user out of the app """

    # clear all sessions of the user
    session.clear()

    # Redirect user to homepage / login page
    return redirect("/")