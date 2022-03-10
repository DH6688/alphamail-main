from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, linear_regression, detect_words

import numpy as np

# Configure application
app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///amail.db")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

         # Ensure fields were submitted
        if email == "" or password == "" or confirmation == "":
            return apology("Must fill in all fields", 400)
        
        # Ensure that email address is appropriate
        elif email.find("@amail.com") == -1:
            return apology("____@amail.com")

        # Makes sure that the length of password is fine
        elif len(password) < 6:
            return apology("Password too short")
        elif any(map(str.isdigit, password)) == False:
            return apology("Password must have numbers")
        elif any(c.isupper() for c in password) == False:
            return apology("Password must have uppercase")

        rows = db.execute("SELECT * FROM users WHERE username = ?", email)

        # Ensure username doesn't exist 
        if len(rows) != 0:
            return apology("username is not available", 400)
        else:
            if password != confirmation:
                return apology("Passwords Don't Match", 400)
            
            hash = generate_password_hash(password)

            # Inserts the email and password
            db.execute("INSERT INTO users (username,hash) VALUES (?,?)", email, hash)
                
        return render_template("login.html")

    else:
        return render_template("register.html")

@app.route("/compose", methods=["GET","POST"])

def compose():

    if request.method == "POST":
        
        address = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        sender = db.execute("SELECT username from users WHERE id = ?", session["user_id"])[0]["username"]
        time = db.execute("SELECT CURRENT_TIMESTAMP")[0]["CURRENT_TIMESTAMP"]

       
        # Checks if email exists
        row = db.execute("SELECT * FROM users WHERE username = ?", address)
        if len(row) != 1:
            return apology("Email does not exist")

        # Calculates linear_regression
        reg = linear_regression()

        # Calculates importance of the message
        importance = reg.predict(np.array([detect_words(message)]))[0]
        db.execute("INSERT INTO inbox (sender, subject, message, email, time, importance) VALUES (?,?,?,?,?,?)", sender, subject, message, address, time, importance)

        # Updates sent database
        db.execute("INSERT INTO sent (sender, subject, message, destination, time) VALUES (?,?,?,?,?)", sender, subject, message, address, time)
       
        # Formats sent
        sent = db.execute("SELECT * FROM sent WHERE sender = ?", sender)
        return render_template("sent.html", sent=sent)
    
    
    else:
        return render_template("compose.html")

@app.route("/inbox", methods=["GET","POST"])
@app.route("/", methods=["GET","POST"])
@login_required
def inbox():
    
    if request.method == "POST":
        # Reads contents of form
        sender = request.form.get("sender")
        subject = request.form.get("subject")
        message = request.form.get("message")

        # Renders email template
        return render_template("email.html", sender=sender, subject=subject, message=message)


    else:
        # Retrieves inbox of the current user
        email = db.execute("SELECT username FROM users WHERE id = ?",  session["user_id"])[0]["username"]
        inbox = db.execute("SELECT * FROM inbox WHERE email = ? ORDER BY importance DESC", email)

        # Renders inbox
        return render_template("inbox.html", inbox=inbox)

@app.route("/sent", methods=["GET","POST"])
@login_required
def sent():
    
    sender = db.execute("SELECT username FROM users WHERE id = ?",  session["user_id"])[0]["username"] 

    if request.method == "POST":

         # Reads contents of form
        subject = request.form.get("subject")
        message = request.form.get("message")
        
        # Renders email tempalte
        return render_template("email.html", sender=sender, subject=subject, message=message)


    else:
        # Retrieves sent emails of the current user
        sent = db.execute("SELECT * FROM sent WHERE sender = ?", sender)
        # Renders sent page
        return render_template("sent.html", sent=sent)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)