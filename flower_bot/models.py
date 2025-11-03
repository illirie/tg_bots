from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from consts import  host, database, user, password, port

Model = declarative_base()
engine = create_engine(
    f"postgresql://{user}:{password}@{host}:{port}/{database}"
)
Session = sessionmaker(bind=engine)
session = Session()

class Flower(Model):
    __tablename__ = 'flowers'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    cost = Column(Integer)
    quantity = Column(Integer)
    supplier = Column(String(255))


class User(Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    role = Column(String(255), default='user', nullable=False)

class Order(Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    flower_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)