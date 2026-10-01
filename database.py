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
    
@app.post("/courses", status_code=201)
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
        raise HTTPException(status_code=500, detail=f"Error creating course: {e}")


def get_courses():
    try:
        with SessionLocal() as session:
            result = session.execute(text("SELECT * FROM courses"))
            courses = result.mappings().all()
        return courses
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error fetching courses data: {e}")


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

@app.delete("/enrollments/{enrollment_id}")
def delete_enrollment(enrollment_id: int):
    try:
        with SessionLocal() as session:
            # Check if the enrollment exists
            result = session.execute(
                text("SELECT id FROM enrollments WHERE id = :id"),
                {"id": enrollment_id}
            )
            enrollment = result.mappings().first()
            if not enrollment:
                raise HTTPException(status_code=404, detail="Enrollment not found")

            # Delete the enrollment record
            session.execute(
                text("DELETE FROM enrollments WHERE id = :id"),
                {"id": enrollment_id}
            )
            session.commit()
            
        return {"message": "Enrollment deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting enrollment: {e}")

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
                raise HTTPException(status_code=404, detail="Student not found")

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
                "courses": courses
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching student courses: {e}")


class EnrollCreate(BaseModel):
    student_id: int = Field(..., gt=0, description="ID of the student")
    course_id: int = Field(..., gt=0, description="ID of the course")

@app.post("/enroll")
def enroll_student(enrollment: EnrollmentCreate):
    try:
        with SessionLocal() as session:
            # Check if student exists
            student = session.execute(
                text("SELECT id FROM students WHERE id = :id"),
                {"id": enrollment.student_id}
            ).fetchone()
            if not student:
                raise HTTPException(status_code=404, detail="Student not found")

            # Check if course exists
            course = session.execute(
                text("SELECT id FROM courses WHERE id = :id"),
                {"id": enrollment.course_id}
            ).fetchone()
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            # Enroll student
            session.execute(
                text("INSERT INTO enrollments (student_id, course_id) VALUES (:student_id, :course_id)"),
                {"student_id": enrollment.student_id, "course_id": enrollment.course_id}
            )
            session.commit()
            return {"message": "Student enrolled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enrolling student: {e}")
