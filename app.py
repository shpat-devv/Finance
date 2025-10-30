import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from api.database import Database

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database (for anyone at harvard checking this, im using my own database handler because im using my local computer to write this and i didn't want to install cs50's library)
db = Database("finance.db")
db.connect()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        #add error handling 
        if request.form.get("symbol") and request.form.get("shares") and int(request.form.get("shares")) > 0:
            cost = lookup(request.form.get("symbol"))["price"] * int(request.form.get("shares"))
            user = db.find_user(session["user_id"], "id")

            if cost > int(user["cash"]):
                return apology("you dont have enough money")
            
            db.update_user(session["user_id"], "cash", int(user["cash"]) - cost)

            stock_data = lookup(request.form.get("symbol"))
            db.insert_stock(stock_data["name"], stock_data["price"], stock_data["symbol"], request.form.get("shares"), session["user_id"])
        
            return redirect("/")
        else:
            print(request.form.get("symbol"), request.form.get("shares"))
            return apology("form not filled correctly")
    return render_template("buy.html")


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Show name of stock, how many stocks the user purchased, the current price of the stock, the total value and the users money balance"""
    if request.method == "POST":
        user_stocks = db.get_stocks(session["user_id"])
        user = db.find_user(session["user_id"], "id")
        
        stock_info = []

        for row in user_stocks:
            current_price = lookup(row["symbol"])
            overall_value = current_price["price"] * row["shares"]

            stock_info.append([row["name"], row["shares"], current_price, overall_value])

        return render_template("history.html", reload = False, stocks = stock_info, balance = user["cash"])
    else:
        return render_template("history.html", reload = True)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        user = db.find_user(request.form.get("username"), "username") #actual username and table name

        if not user or not check_password_hash(
            user["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user["id"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        if request.form.get("symbol"):  
            quote_data = lookup(request.form.get("symbol"))
            if quote_data:
                return render_template("quote.html", quotes = quote_data)
            else:
                return apology("couldn't get quotes")
        else:
            return apology("symbol not passed in")
    else:
        return render_template("quote.html")

#add password confirmation, login automatically
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)
        
        if db.find_user(request.form.get("username"), "username"):
            return apology("username already exists", 403)

        #users by default start with 10k in cash
        db.insert_user(request.form.get("username"), generate_password_hash(request.form.get("password")))

        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")
