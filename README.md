# 💹 C$50 Finance — Stock Trading Simulator

A full-stack Flask web application that simulates a stock trading platform.  
Users can register, log in securely, look up stock prices, buy and sell shares, and view their complete transaction history — all with persistent data stored in SQLite.

---

## 🚀 Features

- **Secure Authentication**
  - Passwords are hashed using `werkzeug.security`
  - Session-based login system (server-side sessions via `flask_session`)
  - Protected routes using a custom `@login_required` decorator

- **Portfolio Management**
  - View owned stocks, current prices, and total portfolio value
  - Price lookups via a CS50 API (`lookup()` helper)
  - Dynamic recalculation of total cash + stock worth

- **Form Validation & Error Handling**
  - Custom `apology()` function for user-friendly error messages
  - Ensures all forms and inputs are validated before processing

- **Clean Template Integration**
  - Uses Jinja2 filters (like a custom `usd` filter) for currency formatting
  - Responsive, server-rendered HTML pages (`index.html`, `buy.html`, `sell.html`, etc.)

---

## ⚙️ Setup & Run Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/shpat-devv/finance-app.git
   cd finance-app
```
2. **Create a virtual environment and activate it**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Start project**
   ```bash
   flask --app app run
   ```

## Error Handling

If any error occurs during database operations try running the following command in your terminal to reset the database schema:

```bash
sqlite3 finance.db < tables.sql
```

## 📸 Show off

[![Watch this](https://img.youtube.com/vi/KmNe_vO_jeQ/0.jpg)](https://www.youtube.com/watch?v=KmNe_vO_jeQ)

## 📄 License
This project was made for fun, Do whatever you want with it <3