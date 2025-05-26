from sqlalchemy import create_engine, MetaData, Table, Column, \
    PrimaryKeyConstraint, ForeignKeyConstraint, ForeignKey, \
    Integer, String, Boolean, \
    Select, Update, Delete
from sqlalchemy.dialects.sqlite import DATE

engine = create_engine("sqlite+pysqlite:///database.db")

metadata = MetaData()

users = Table(
    "users", 
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True),
    Column("password", String),
    Column("firstname", String),
    Column("lastname", String),
)

transactions = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("date", DATE),
    Column("type", String),
    Column("amount", Integer),
    Column("category", String),
    Column("notes", String)
)



if __name__=="__main__":
    metadata.create_all(engine)
    # metadata.drop_all(engine, [transactions])