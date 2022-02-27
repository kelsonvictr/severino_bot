from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://postgres:123@localhost:5432/ccontrol")
Session = sessionmaker(bind=engine)
Base = declarative_base()


def sqlalchemy_starter():
    return Session, Base, engine
