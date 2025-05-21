from sqlalchemy import create_engine, MetaData, Table, Column, \
    PrimaryKeyConstraint, ForeignKeyConstraint, \
    Integer, String, Boolean, \
    Select, Update, Delete

engine = create_engine("sqlite+pysqlite:///:memory:")
metadata = MetaData()

users = Table(
    "users", 
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True),
    Column("password", String),
)


