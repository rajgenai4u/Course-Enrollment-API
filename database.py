import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def check_database_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
    return True


check_database_connection()

app = FastAPI(
    title="Course Enrollment API",
    description="API to manage students, courses, and course enrollments",
    version="1.0.0",
)


# --- Request Schemas ---
class EnrollCreate(BaseModel):
    student_id: int
    course_id: int


class CourseCreate(BaseModel):
    title: str


# --- API Endpoints ---

@app.get("/")
def home():
    return {"message": "Welcome to the Course Enrollment API"}


# 1. Correct Endpoint Path: POST /courses
@app.post("/courses", status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate):
    try:
        with SessionLocal() as session:
            session.execute(
                text("INSERT INTO courses (title) VALUES (:title)"),
                {"title": course.title},
            )
            session.commit()
        return {"message": "Course created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating course: {e}")


@app.get("/courses")
def get_courses():
    try:
        with SessionLocal() as session:
            result = session.execute(text("SELECT id, title FROM courses")).fetchall()
            return [{"id": row[0], "title": row[1]} for row in result]
    except Exception as e:
        # Fix: Report actual DB error as 500 instead of masking as 404
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error fetching courses: {e}",
        )


@app.get("/students/{student_id}")
def get_student_by_id(student_id: int):
    try:
        with SessionLocal() as session:
            student = session.execute(
                text("SELECT id, name FROM students WHERE id = :id"),
                {"id": student_id},
            ).fetchone()

            if not student:
                # Fix: Raise 404 when student is not found
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Student not found",
                )

            return {"id": student[0], "name": student[1]}
    except HTTPException:
        # Fix: Re-raise HTTPException directly so 404 is not converted into 500
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching student: {e}",
        )


# Fix Blocker: Annotate with EnrollCreate (matches model name)
@app.post("/enroll", status_code=status.HTTP_201_CREATED)
def enroll_student(enrollment: EnrollCreate):
    try:
        with SessionLocal() as session:
            # Check student existence
            student = session.execute(
                text("SELECT id FROM students WHERE id = :id"),
                {"id": enrollment.student_id},
            ).fetchone()
            if not student:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Student not found",
                )

            # Check course existence
            course = session.execute(
                text("SELECT id FROM courses WHERE id = :id"),
                {"id": enrollment.course_id},
            ).fetchone()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found",
                )

            # Fix Major: Prevent duplicate enrollments (Return 409 Conflict)
            existing_enrollment = session.execute(
                text(
                    "SELECT id FROM enrollments WHERE student_id = :s_id AND course_id = :c_id"
                ),
                {"s_id": enrollment.student_id, "c_id": enrollment.course_id},
            ).fetchone()

            if existing_enrollment:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Student is already enrolled in this course",
                )

            # Insert enrollment
            session.execute(
                text(
                    "INSERT INTO enrollments (student_id, course_id) VALUES (:s_id, :c_id)"
                ),
                {"s_id": enrollment.student_id, "c_id": enrollment.course_id},
            )
            session.commit()
            return {"message": "Student enrolled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enrolling student: {e}",
        )


# Fix Major: Route corrected from /enrollments/{id} to /enroll/{enrollment_id}
@app.delete("/enroll/{enrollment_id}")
def delete_enrollment(enrollment_id: int):
    try:
        with SessionLocal() as session:
            result = session.execute(
                text("SELECT id FROM enrollments WHERE id = :id"),
                {"id": enrollment_id},
            ).fetchone()

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Enrollment not found",
                )

            session.execute(
                text("DELETE FROM enrollments WHERE id = :id"),
                {"id": enrollment_id},
            )
            session.commit()

        return {"message": "Enrollment deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting enrollment: {e}",
        )
