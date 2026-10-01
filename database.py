import os
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import FastAPI , Depends, HTTPException

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def check_database_connection():
    try:
        # Attempt to connect to the database
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
    return True

check_database_connection()

app = FastAPI(title="neon db test" , description="API to test connection with Neon PostgreSQL database",
              version="1.0.0")

@app.get("/")
def home():
    return {"message": "Welcome to the Neon PostgreSQL database test API"}

from pydantic import BaseModel ,Field , EmailStr, HttpUrl, field_validator   
class CourseCreate(BaseModel):
    title: str = Field(min_length=2, max_length=50)
    
@app.post("/courses_create")
def create_course(course: CourseCreate):
    try:
        with SessionLocal() as session:
            session.execute(
                text("INSERT INTO courses (title) VALUES (:title)"),
                {"title": course.title}             
            )
            session.commit()
        return {"message": "Course created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating course : {e}")


def get_courses():
    try:
        with SessionLocal() as session:
            result = session.execute(text("SELECT * FROM courses"))
            courses = result.mappings().all()
        return courses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching courses data: {e}")


@app.get("/courses")
def get_courses_data():
    return get_courses()

@app.get("/students")
def get_students_data():
    try:
        with SessionLocal() as session:
            result = session.execute(text("SELECT * FROM students"))
            students = result.mappings().all()
        return students
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching students data: {e}")

@app.get("/students/{student_id}")
def get_student_by_id(student_id: int):
    try:
        with SessionLocal() as session:
            result = session.execute(text("SELECT * FROM students WHERE id = :id"), {"id": student_id})
            student = result.mappings().first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching student data: {e}")

@app.delete("/students_delete/{student_id}")
def delete_student(student_id: int):
    try:
        with SessionLocal() as session:
            session.execute(
                text("DELETE FROM students WHERE id = :id"),
                {"id": student_id}
            )
            session.commit()
        return {"message": "Student deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting student: {e}")


@app.get("/students/{student_id}/courses")
def get_student_courses(student_id: int):
    try:
        with SessionLocal() as session:
            # Check if student exists
            student = session.execute(
                text("SELECT id, name FROM students WHERE id = :id"),
                {"id": student_id}
            ).fetchone()

            if not student:
                return {"error": "Student not found"}

            # Get all courses for this student
            result = session.execute(
                text("""
                    SELECT c.id, c.title
                    FROM enrollments e
                    JOIN courses c ON e.course_id = c.id
                    WHERE e.student_id = :student_id
                """),
                {"student_id": student_id}
            ).fetchall()

            courses = [{"id": row[0], "title": row[1]} for row in result]

            return {
                "student_id": student_id,
                "student_name": student[1],
                "courses": courses,
                "total_courses": len(courses)
            }
    except Exception as e:
        return {"error": str(e)}



class EnrollCreate(BaseModel):
    student_id: int = Field(..., gt=0, description="ID of the student")
    course_id: int = Field(..., gt=0, description="ID of the course")

@app.post("/enroll")
def enroll_student(enrollment: EnrollCreate):
    with SessionLocal() as session:
        # 1. check student exists
        s = session.execute(text("SELECT id FROM students WHERE id = :id"), {"id": enrollment.student_id}).fetchone()
        if not s:
            return {"error": "Student not found"}

        # 2. check course exists
        c = session.execute(text("SELECT id FROM courses WHERE id = :id"), {"id": enrollment.course_id}).fetchone()
        if not c:
            return {"error": "Course not found"}

        # 3. check duplicate
        dup = session.execute(
            text("SELECT id FROM enrollments WHERE student_id = :sid AND course_id = :cid"),
            {"sid": enrollment.student_id, "cid": enrollment.course_id}
        ).fetchone()
        if dup:
            return {"message": "Already enrolled"}

        # 4. insert
        result = session.execute(
            text("INSERT INTO enrollments (student_id, course_id) VALUES (:sid, :cid) RETURNING id"),
            {"sid": enrollment.student_id, "cid": enrollment.course_id}
        )
        new_id = result.fetchone()[0]
        session.commit()
        return {"id": new_id, "message": "Enrollment successful"}