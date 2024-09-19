import sqlalchemy
import os
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, insert
from sqlalchemy import Column, BigInteger, String, Date, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import and_, or_

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
base = declarative_base()

session = sessionmaker(bind=engine)()


class Teacher(base):
    __tablename__ = "Teacher"
    id = Column("id", BigInteger, unique=True, primary_key=True, autoincrement=True)
    name = Column("name", String(60), nullable=True)


class Student(base):
    __tablename__ = "Student"
    id = Column("id", BigInteger, unique=True, primary_key=True, autoincrement=True)
    student_code = Column("student_code", BigInteger, unique=True)
    national_code = Column("national_code", BigInteger, unique=True)


# base.metadata.create_all(engine)

# Select
# teachers = session.query(Teacher).filter(and_(Teacher.id == 1, Teacher.name=="رحیم پور")).all()

# for t in teachers:
#     print(t.id, t.name)

# Insert

# session.add(Teacher)
