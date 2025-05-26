from sqlalchemy import text

class CRUD():
    
    addTransaction = text(
        "INSERT INTO transactions (user_id, date, type, amount, category, notes) "
        "VALUES (:user_id, :date, :type, :amount, :category, :notes)"
    )

    updateTransaction = text(
        "UPDATE transactions SET date=:date, type=:type, amount=:amount, category=:category, notes=:notes "
        "WHERE transactions.id = :id AND transactions.user_id = :user_id"
    )

    deleteTransaction = text(
        "DELETE FROM transactions WHERE transactions.id = :id AND transactions.user_id = :user_id"
    )

    def searchTransaction(q, start, end):

        base = (
            "SELECT transactions.id, transactions.user_id, transactions.date, transactions.type, "
                "transactions.amount, transactions.category, transactions.notes "
            "FROM transactions WHERE transactions.user_id = :user_id"
        )

        if start:
            base = base + " AND transactions.date >= :start_date"
        if end:
            base = base + " AND transactions.date <= :end_date"
        if q:
            base = base + "  AND transactions.notes LIKE :filter"

        base = base + " ORDER BY transactions.date DESC"
        return text(base)
    
    daily_report = text(
        "SELECT transactions.date, transactions.type, sum(transactions.amount) AS sum "
        "FROM transactions "
        "WHERE transactions.user_id = :user_id GROUP BY transactions.date, transactions.type ORDER BY transactions.date DESC"
    )

    category_report = text(
        "SELECT transactions.category, count(transactions.category) AS count "
        "FROM transactions "
        "WHERE transactions.user_id = :user_id GROUP BY transactions.category"
    )

    login = text(
        "SELECT users.id, users.username, users.password, users.firstname, users.lastname "
        "FROM users "
        "WHERE users.username = :username AND users.password = :password"
    )

    signup = text (
        "INSERT INTO users (username, password, firstname, lastname) "
        "VALUES (:username, :password, :firstname, :lastname) RETURNING id"
    )