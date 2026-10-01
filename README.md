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
- A PostgreSQL database (e.g., Neon PostgreSQL or local instance)

### 2. Clone the Repository
```bash
git clone [https://github.com/rajgenai4u/Course-Enrollment-API.git](https://github.com/rajgenai4u/Course-Enrollment-API.git)
cd Course-Enrollment-API
