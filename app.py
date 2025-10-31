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

# Configure database
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
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol or not shares:
            return apology("form not filled correctly")

        try:
            shares = int(shares)
            if shares <= 0:
                return apology("shares must be positive")
        except ValueError:
            return apology("shares must be an integer")

        stock_data = lookup(symbol)
        if not stock_data:
            return apology("invalid symbol")

        cost = stock_data["price"] * shares
        user = db.find_user(session["user_id"], "id")

        if cost > user["cash"]:
            return apology("you don't have enough money")

        # update user cash 
        new_cash = user["cash"] - cost
        db.update_table(session["user_id"], "users", "cash", new_cash)
        db.insert_stock(stock_data["name"], stock_data["price"], stock_data["symbol"], shares, session["user_id"])

        # add transaction
        stock_id = db.get_last("stocks", "id")
        db.insert_transaction(stock_id["id"])
        return redirect("/")
    return render_template("buy.html")


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    if request.method == "POST":
        user_stocks = db.get_stocks(session["user_id"], "*")
        user = db.find_user(session["user_id"], "id")

        stock_info = []

        for row in user_stocks:
            current_price = lookup(row["symbol"])
            overall_value = current_price["price"] * row["shares"]

            stock_info.append([
                row["name"],
                row["shares"],
                usd(current_price["price"]),
                usd(overall_value)
            ])

        return render_template("history.html", reload=False, stocks=stock_info, balance=usd(user["cash"]))
    else:
        return render_template("history.html", reload=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username", 403)
        if not password:
            return apology("must provide password", 403)

        user = db.find_user(username, "username")

        if not user or not check_password_hash(user["hash"], password):
            return apology("invalid username and/or password", 403)

        session["user_id"] = user["id"]
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("symbol not provided")

        quote_data = lookup(symbol)
        if not quote_data:
            return apology("couldn't get quotes")

        # Pass formatted data to front-end
        quote_data["price"] = usd(quote_data["price"])
        return render_template("quote.html", quotes=quote_data)

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username", 403)
        if not password or not confirmation:
            return apology("must provide password", 403)
        if password != confirmation:
            return apology("passwords don't match", 403)
        if db.find_user(username, "username"):
            return apology("username already exists", 403)

        db.insert_user(username, generate_password_hash(password), 10000.0)
        return redirect("/login")

    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == 'POST':
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide symbol", 403)
        if not shares:
            return apology("must provide shares", 403)

        try:
            shares = int(shares)
            if shares <= 0:
                return apology("quantity must be higher than 0")
        except ValueError:
            return apology("please select a number for shares", 403)

        user_stocks = db.get_stocks(session["user_id"], "symbol, shares")
        user = db.find_user(session["user_id"], "id")

        for stock in user_stocks:
            if symbol == stock["symbol"] and shares <= stock["shares"]:
                sale_value = lookup(symbol)["price"] * shares
                new_cash = user["cash"] + sale_value
                remaining_shares = stock["shares"] - shares

                # Update user's cash
                db.update_table(session["user_id"], "users", "cash", new_cash)

                # Update stock record
                db.cursor.execute(
                    "UPDATE stocks SET shares = ? WHERE user_id = ? AND symbol = ?",
                    (remaining_shares, session["user_id"], symbol)
                )
                db.connection.commit()

                return redirect("/")

        return apology("you don't own that many shares", 403)

    else:
        user_stocks = db.get_stocks(session["user_id"], "symbol")
        user_symbols = [stock["symbol"] for stock in user_stocks]
        return render_template('sell.html', reload=True, symbols=user_symbols)
