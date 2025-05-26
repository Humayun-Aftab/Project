from flask import Flask, request, render_template, \
    session, redirect, abort, make_response, jsonify
from utility import logged_in, get_logger, notify
from models import engine, users, transactions
from sqlalchemy import select, insert, exc
from datetime import datetime, date
import json
from sql import CRUD
from collections import defaultdict


app = Flask(__name__)
app.secret_key = ":)"
logger = get_logger()


# teeno routes wely
@app.route('/')
@logged_in
def index():
    return render_template('index.html')


@app.route('/transaction')
@logged_in
def transaction():
    return render_template("transaction.html")


@app.route("/deployment")
@logged_in
def deployment():
    return render_template("deployment.html")


@app.get("/api/transaction")
@logged_in
def get_transaction():
    args = request.args

    start, end, q = [args.get("start-date"), args.get("end-date"), args.get("search")]

    with engine.begin() as conn:
        result = conn.execute(CRUD.searchTransaction(q, start, end), {
            "user_id": session.get("user").get("id"), "filter":  f"%{q}%",
            "end_date": end, "start_date": start
        })
        mappings = {"transactions": [dict(x) for x in result.mappings().all()]}
        return json.dumps(mappings, default=str)
    

@app.post("/api/transaction")
@logged_in
def post_transaction():
     with engine.begin() as conn:
        try:
            date = datetime.strptime(request.form.get('date'), "%Y-%m-%d").date()
            conn.execute(CRUD.addTransaction, {
                **request.form, "date": date, "user_id": session['user']['id']
            })
            return notify({"status": "success", "text": "Added successfully!"}, 200)
        except (exc.StatementError, ValueError):
            return notify({"status": "failed", "text": "Did you leave some field empty?"}, 400)



@app.patch("/api/transaction")
@logged_in
def update_transaction():
    try: 
        with engine.begin() as conn:
            conn.execute(CRUD.updateTransaction, {
                **request.form, "date": date.fromisoformat(request.form.get("date")),
                "id": request.form.get("id"), "user_id": session['user']['id']
            })
            return notify({"status": "success", "text": "Updated successfully!"}, 200)
    except (exc.StatementError, ValueError):
        return notify({"status": "failed", "text": "Please check the input fields."})


@app.delete("/api/transaction")
@logged_in
def delete_transaction():
    transaction_id = request.args.get("id")
    user_id = session.get("user").get("id")

    with engine.begin() as conn:
        conn.execute(CRUD.deleteTransaction, {
            "id": transaction_id, "user_id": user_id
        })
        return notify() # default -> successful op



@app.route('/api/report')
@logged_in
def report():
    with engine.begin() as conn:

        # monthly/daily report calculations
        result = conn.execute(CRUD.daily_report, {"user_id": session.get("user").get("id")})

        daily_report_dict = defaultdict(dict)
        for row in result:
            mapping = dict(row._mapping)
            type = mapping['type']
            mapping[type] = mapping.pop('sum')
            del mapping['type']
            daily_report_dict[row.date].update(mapping)
        daily_report = list(daily_report_dict.values())

        monthly_report_dict = defaultdict(lambda : dict(income=0, expense=0, investment=0))
        for day in daily_report:
            date_obj = date.fromisoformat(day['date'])
            month = date_obj.month
            monthly_report_dict[month]['income'] += day.get("income", 0)
            monthly_report_dict[month]['expense'] += day.get('expense', 0)
            monthly_report_dict[month]['investment'] += day.get('investment', 0)
            monthly_report_dict[month].setdefault(
                "month", date_obj.strftime("%B")
            )
        monthly_report_list = list(monthly_report_dict.values())
        monthly_report = list(map(
            lambda x : {**x, "growth": x["investment"] + x["income"] - x["expense"]},
            monthly_report_list
        ))
        
        # transaction categories calculation
        result = conn.execute(CRUD.category_report, {"user_id": session.get("user").get("id")})
        categories = []
        for row in result:
            categories.append({
                "label": row.category,
                "value": row.count,
            })

        # investment calculation
        investment = sum(e["investment"] for e in monthly_report)

        # jsonifies python structs
        resp = json.dumps({
            "daily_report": daily_report,
            "monthly_report": monthly_report,
            "categories": categories,
            "total_investment": investment
        }, default=str, indent=2)
        return resp


@app.route('/login', methods=["GET", "POST"])
def login():
    # manages get request
    if request.method == "GET" and session.get("user") == None:
        return render_template("login.html")
    if request.method == "GET":
        session["user"] = None
        return redirect("/")
    
    # manages post request
    data = request.form.get("username").lower(), request.form.get("password")
    with engine.begin() as conn:
        current_user = conn.execute(CRUD.login, {"username": data[0], "password": data[1]}).first()
        
        if not current_user:
            return "You haven't registered"
        
        # add profile info to session
        session["user"] = {"id": current_user.id, "username": current_user.username}
        return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def register():
    # manages get requests
    if request.method == "GET" and session.get("user"):
        return redirect("/")
    if request.method == "GET":
        return render_template("signup.html")
        
    
    # manages post request  
    f = request.form  
    data = f.get("username").lower(), f.get("password"), f.get("firstname"), f.get("lastname")

    # no extensive checks
    if not data[0] or not data[1] or not data[2] or not data[3]:
        return "Please don't leave a field empty"
    
    with engine.begin() as conn:
        result = conn.execute(CRUD.signup, request.form).fetchone()
        session["user"] = {"id": result.id ,"username": str(data[0])}
        return redirect("/")
    

@app.route("/signout")
def signout():
    session.clear()
    return redirect("/login")