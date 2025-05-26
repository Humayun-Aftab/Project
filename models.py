from sqlalchemy import create_engine, text
from sqlalchemy.dialects.sqlite import DATE

engine = create_engine("sqlite+pysqlite:///database.db")


users = text('''
    CREATE TABLE users (
        id INTEGER NOT NULL,
        username VARCHAR,
        password VARCHAR,
        firstname VARCHAR,
        lastname VARCHAR,
        PRIMARY KEY (id),
        UNIQUE (username)
    )
''')

transactions = text('''
    CREATE TABLE transactions (
        id INTEGER NOT NULL,
        user_id INTEGER,
        date DATE,
        type VARCHAR,
        amount INTEGER,
        category VARCHAR,
        notes VARCHAR,
        PRIMARY KEY (id),
        FOREIGN KEY(user_id) REFERENCES users (id)
    )   
''')


# "python models.py" creates a database with above tables (it not exists already)
if __name__=="__main__":
    with engine.begin() as conn:
        conn.execute(users)
        conn.execute(transactions)