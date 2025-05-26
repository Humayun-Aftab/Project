from flask import Flask, request, render_template, \
    session, redirect, abort, make_response, jsonify
from utility import logged_in, get_logger, notify
from models import engine, users, transactions
from sqlalchemy import select, insert, update, delete, func, desc, exc
from datetime import datetime, date
import json
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

    stmt = (
        select(transactions)
        .filter_by(user_id=session.get("user").get("id"))
        .order_by(desc("date"))
    )
    start, end, q = [args.get("start-date"), args.get("end-date"), args.get("search")]

    if start:
        stmt = stmt.where(transactions.c.date >= request.args['start-date'])
    if end:
        stmt = stmt.where(transactions.c.date <= request.args['end-date'])
    if q:
        stmt = stmt.where(transactions.c.notes.like(f"%{q}%"))

    with engine.begin() as conn:
        result = conn.execute(stmt)
        mappings = {"transactions": [dict(x) for x in result.mappings().all()]}
        return json.dumps(mappings, default=str)
    

@app.post("/api/transaction")
@logged_in
def post_transaction():
     with engine.begin() as conn:
        try:
            date = datetime.strptime(request.form.get('date'), "%Y-%m-%d").date()
            conn.execute(insert(transactions), {
                **request.form, "date": date, "user_id": session['user']['id']
            })
            return notify({"status": "success", "text": "Added successfully!"}, 200)
        except (exc.StatementError, ValueError):
            return notify({"status": "failed", "text": "Did you leave some field empty?"}, 400)



@app.patch("/api/transaction")
@logged_in
def update_transaction():
    stmt = (
        update(transactions).filter_by(
            id=request.form.get("id"), user_id=session['user']['id']
        ).values(request.form).values({"date": date.fromisoformat(request.form.get("date"))})
    )
    try: 
        with engine.begin() as conn:
            conn.execute(stmt)
            return notify({"status": "success", "text": "Updated successfully!"}, 200)
    except (exc.StatementError, ValueError):
        return notify({"status": "failed", "text": "Please check the input fields."})


@app.delete("/api/transaction")
@logged_in
def delete_transaction():
    transaction_id = request.args.get("id")
    user_id = session.get("user").get("id")

    with engine.begin() as conn:
        conn.execute(delete(transactions).filter_by(id=transaction_id, user_id=user_id))
        return notify() # default -> successful op



@app.route('/api/report')
@logged_in
def report():
    with engine.begin() as conn:

        # monthly/daily report calculations
        stmt = (
            select(transactions.c["date", "type"], func.sum(transactions.c.amount).label("sum"))
            .filter_by(user_id = session.get("user").get("id"))
            .group_by("date", "type").order_by(desc("date"))
        )
        result = conn.execute(stmt)

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
            month = day['date'].month
            monthly_report_dict[month]['income'] += day.get("income", 0)
            monthly_report_dict[month]['expense'] += day.get('expense', 0)
            monthly_report_dict[month]['investment'] += day.get('investment', 0)
            monthly_report_dict[month].setdefault(
                "month", day['date'].strftime("%B")
            )
        monthly_report_list = list(monthly_report_dict.values())
        monthly_report = list(map(
            lambda x : {**x, "growth": x["investment"] + x["income"] - x["expense"]},
            monthly_report_list
        ))
        
        # transaction categories calculation
        stmt = (
            select(transactions.c.category, func.count(transactions.c.category).label("count"))
            .group_by("category").filter_by(user_id=session.get("user").get("id"))
        )
        result = conn.execute(stmt)
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
        current_user = conn.execute(
            select(users).where(users.c.username == data[0], users.c.password == data[1])
        ).first()
        
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
    
    stmt = insert(users).values(**request.form).returning(users.c.id)
    with engine.begin() as conn:
        result = conn.execute(stmt).fetchone()
        logger.info(f"REGISTER ENDPOINT RESP: {result}")
        session["user"] = {"id": result.id ,"username": str(data[0])}
        return redirect("/")
    

@app.route("/signout")
def signout():
    session.clear()
    return redirect("/login")