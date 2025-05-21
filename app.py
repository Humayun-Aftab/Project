from flask import Flask, request, render_template, session, redirect
from utility import logged_in, apology
from models import engine, users
from sqlalchemy import select


app = Flask(__name__)
app.secret_key = "key"

@app.route('/')
@logged_in
def index():
    return render_template('index.html')


@app.route('/<clientEndpoint>')
@logged_in
def serve(clientEndpoint):
    return render_template(f'{clientEndpoint}.html')


@app.route('/login')
def login():
    # manages get request
    if request.method == "GET" and session.get("user") == None:
        return render_template("login.html")
    if request.method == "GET":
        session["user"] = None
        return redirect("/")
    
    # manages post request
    data = request.form.get("username").lower(), request.form.get("pass")
    with engine.connect() as conn:
        current_user = conn.execute(
            select(users).where(users.c.username == data[0], users.c.password == data[1])
        ).first()
        
        if not current_user:
            return "You haven't registered"
        
        session["user"] = {"id": current_user.id, "username": current_user.username}
        return redirect("/")


@app.route('/transactions/get')
def get_transactions():
    return {
        "transactions": [
            {
            "transaction_id": 240,
            "transaction_amount": 200.00,
            "transaction_type": "income",
            "transaction_date": "2025-01-10",
            "notes": "Course fee",
            "transaction_category": "Credit Card"
            },
            {
            "transaction_id": 241,
            "transaction_amount": 50.75,
            "transaction_type": "expense",
            "transaction_date": "2025-01-01",
            "notes": "Weekly grocery shopping",
            "transaction_category": "Credit Card"
            },
            {
            "transaction_id": 243,
            "transaction_amount": 100.00,
            "transaction_type": "expense",
            "transaction_date": "2025-01-03",
            "notes": "Electricity bill payment",
            "transaction_category": "PayPal"
            },
            {
            "transaction_id": 245,
            "transaction_amount": 20.00,
            "transaction_type": "expense",
            "transaction_date": "2025-01-02",
            "notes": "Movie tickets",
            "transaction_category": "Debit Card"
            },
            {
            "transaction_id": 248,
            "transaction_amount": 25.00,
            "transaction_type": "expense",
            "transaction_date": "2025-01-02",
            "notes": "Bus fare",
            "transaction_category": "Cash"
            },
            {
            "transaction_id": 250,
            "transaction_amount": 15.00,
            "transaction_type": "expense",
            "transaction_date": "2025-01-04",
            "notes": "Movie ticket",
            "transaction_category": "Credit Card"
            },
            {
            "transaction_id": 240,
            "transaction_amount": 200.00,
            "transaction_type": "income",
            "transaction_date": "2025-01-10",
            "notes": "Course fee",
            "transaction_category": "Credit Card"
            },
            {
            "transaction_id": 241,
            "transaction_amount": 50.75,
            "transaction_type": "expense",
            "transaction_date": "2025-01-01",
            "notes": "Weekly grocery shopping",
            "transaction_category": "Credit Card"
            },
            {
            "transaction_id": 243,
            "transaction_amount": 100.00,
            "transaction_type": "expense",
            "transaction_date": "2025-01-03",
            "notes": "Electricity bill payment",
            "transaction_category": "PayPal"
            },
            {
            "transaction_id": 245,
            "transaction_amount": 20.00,
            "transaction_type": "expense",
            "transaction_date": "2025-01-02",
            "notes": "Movie tickets",
            "transaction_category": "Debit Card"
            },
            {
            "transaction_id": 248,
            "transaction_amount": 25.00,
            "transaction_type": "expense",
            "transaction_date": "2025-01-02",
            "notes": "Bus fare",
            "transaction_category": "Cash"
            },
            {
            "transaction_id": 250,
            "transaction_amount": 15.00,
            "transaction_type": "expense",
            "transaction_date": "2025-01-04",
            "notes": "Movie ticket",
            "transaction_category": "Credit Card"
            }
        ]
    }