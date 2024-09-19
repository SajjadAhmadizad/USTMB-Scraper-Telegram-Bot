import sqlalchemy
import os
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, ForeignKey, exists, and_, or_, UniqueConstraint
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, validates

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()


class Teacher(Base):
    __tablename__ = "Teacher"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(60), nullable=True)


class Student(Base):
    __tablename__ = "Student"
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    is_active = Column(Boolean, default=False)
    student_code = Column(BigInteger, unique=True, nullable=False)
    national_code = Column(BigInteger, unique=True, nullable=False)

    sessions = relationship("StudentSession", back_populates="student", uselist=False)

    @validates('student_code', 'national_code')
    def validate_codes(self, key, value):
        if not isinstance(value, int):
            raise ValueError(f"{"کد ملی" if key == "national_code" else "شماره دانشجویی"} باید یک عدد صحیح باشد")
        if key == 'national_code' and len(str(value)) != 10:
            raise ValueError("کد ملی باید دقیقاً 10 رقم باشد")
        elif key == "student_code" and len(str(value)) != 12:
            raise ValueError("شماره دانشجویی باید دقیقاً 12 رقم باشد")
        return value


class StudentSession(Base):
    __tablename__ = 'Student_Sessions'

    id = Column(Integer, primary_key=True)
    student_id = Column(BigInteger, ForeignKey('Student.id'), nullable=False)
    NET_SessionId = Column("ASP.NET_SessionId", String(255), unique=True, nullable=False)
    ASPXAUTH = Column(".ASPXAUTH", String(255), unique=True, nullable=False)
    Menu = Column("Menu", String(20), nullable=True)
    expires_at = Column(DateTime, nullable=False)

    student = relationship("Student", back_populates="sessions")

    __table_args__ = (
        UniqueConstraint('student_id', name='uq_student_session'),
    )

# base.metadata.create_all(engine)

if __name__ == "__main__":
    pass
    # Base.metadata.create_all(engine)

# for t in teachers:
#     print(t.id, t.name)

# Insert

# session.add(Teacher)
