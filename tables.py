import os
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, ForeignKey, exists, and_, or_, UniqueConstraint
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, validates

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
Base = declarative_base()

Session = sessionmaker(bind=engine, expire_on_commit=False)
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
    student_code = Column(BigInteger, nullable=False)
    national_code = Column(BigInteger, nullable=False)

    sessions = relationship("StudentSession", back_populates="student", uselist=False)

    @validates('student_code', 'national_code')
    def validate_codes(self, key, value):
        if not isinstance(value, int):
            raise ValueError(f'{"کد ملی" if key == "national_code" else "شماره دانشجویی"} باید یک عدد صحیح باشد')
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
    ASPXAUTH = Column(".ASPXAUTH", String(450), unique=True, nullable=False)
    Menu = Column("Menu", String(20), nullable=True)
    expires_at = Column(DateTime, nullable=False)

    student = relationship("Student", back_populates="sessions")

    __table_args__ = (
        UniqueConstraint('student_id', name='uq_student_session'),
    )


if __name__ == "__main__":
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(bind=engine)

    # INSERT DATA

    # new_student = Student(telegram_id=1234, student_code=123456789012, national_code=1234567890)
    # session.add(new_student)
    # session.flush()
    #
    # print(new_student.id)
    #
    # new_session = StudentSession(
    #     student_id=new_student.id,
    #     NET_SessionId="XXXXXX",
    #     ASPXAUTH="YYYYY",
    #     expires_at=datetime.datetime.now() + datetime.timedelta(10)
    # )
    # SELECT DATA

    # query = session.query(
    #     StudentSession, Student
    # ).join(
    #     Student, StudentSession.student_id == Student.id
    # )
    # results = query.all()
    #
    # print(results)

    # new_session = StudentSession(student_id=1, NET_SessionId="session123", ASPXAUTH="auth_token",
    #                              Menu="main", expires_at=datetime.datetime.now())
    # session.add(new_session)
    # session.commit()

    # result = session.query(
    #     Student, StudentSession
    # ).join(
    #     StudentSession, Student.id == StudentSession.student_id, isouter=True
    # ).filter(
    #     Student.telegram_id == 1212
    # ).first()
    #

    # if result:
    #     student, student_session = result
    #     print(f"Student ID: {student.id}, Telegram ID: {student.telegram_id}")
    #     # print(f"Session ID: {student_session.id}, Session Expires At: {student_session.expires_at}")
    #     if student_session:
    #         print(f"Session ID: {student_session.NET_SessionId}, Session Expires At: {student_session.expires_at}")
    #     else:
    #         pass
    # else:
    #     print("No student found with this Telegram ID.")
