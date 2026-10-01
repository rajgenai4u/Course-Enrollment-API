# Course Enrollment API

A RESTful API built with **FastAPI** and **SQLAlchemy** for managing students, courses, and enrollments.

---

## Features

- **Course Management:** Create courses (`POST /courses`) and list all courses (`GET /courses`).
- **Student Operations:** Fetch student details by ID (`GET /students/{student_id}`) and view student course enrollments (`GET /students/{student_id}/courses`).
- **Enrollments:** Enroll students in courses (`POST /enroll`) with built-in duplicate prevention (`409 Conflict`).
- **Unenrollment:** Remove enrollment records (`DELETE /enroll/{enrollment_id}`).
- **Error Handling:** Standardized HTTP status codes (`200`, `201`, `400`, `404`, `409`, `500`).

---

## Environment Setup & Installation

### 1. Prerequisites
- Python 3.9+
- A PostgreSQL database instance

### 2. Clone the Repository
```bash
git clone [https://github.com/rajgenai4u/Course-Enrollment-API.git](https://github.com/rajgenai4u/Course-Enrollment-API.git)
cd Course-Enrollment-API

### 3. Set Up Virtual Environment & Install Dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

### 4. Configure Environment Variables (.env)
Create a .env file in the root directory and add your DATABASE_URL:

DATABASE_URL=postgresql://neondb_owner:npg_gx4lX1PGTyKm@ep-silent-salad-b5acl3m1-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require

### 5. Database Setup & Schema
Before running the application, ensure the database tables are created using the following SQL script:

CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS enrollments (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id INT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    CONSTRAINT unique_student_course UNIQUE (student_id, course_id)
);

### 6. Starting the Application
Start the FastAPI application using Uvicorn:

uvicorn database:app --reload

Once running, access the interactive API documentation:

Base URL: http://127.0.0.1:8000
Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

API Endpoints Overview:

Method    Endpoint.                       Description.                            Expected Status

GET       /API                             health check                             200 OK
POST      /courses                         Create a new course                      201 Created
GET       /courses                         Retrieve all courses                     200 OK
GET       /students/{student_id}           Fetch student profile                    200 / 404
GET       /students/{student_id}/courses   List enrolled courses for a student      200 OK / 404
POST      /enroll                          Enroll a student in a course         201 Created/404/409
DELETE    /enroll/{enrollment_id}.         Remove an enrollment record.              200 OK / 
