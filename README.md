# Course Enrollment API

A lightweight RESTful API built with **FastAPI** and **SQLAlchemy** to manage students, courses, and course enrollments.

---

## Features

- **Course Management:** Create new courses (`POST /courses`) and retrieve all listed courses (`GET /courses`).
- **Student Enrollments:** Enroll students into courses (`POST /enroll`) and view courses enrolled by a student (`GET /students/{student_id}/courses`).
- **Enrollment Management:** Delete or unenroll student course records (`DELETE /enrollments/{enrollment_id}`).
- **Robust Error Handling:** Proper HTTP status codes (e.g., `404 Not Found` for missing students/courses, `201 Created` for successful resource creation).

---

## Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database ORM/Execution:** [SQLAlchemy](https://www.sqlalchemy.org/)
- **Data Validation:** [Pydantic](https://docs.pydantic.dev/)
- **Environment Management:** `python-dotenv`

---

## Getting Started

### Prerequisites

- Python 3.9+
- Database instance (e.g., PostgreSQL, MySQL, or SQLite)

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/rajgenai4u/Course-Enrollment-API.git](https://github.com/rajgenai4u/Course-Enrollment-API.git)
   cd Course-Enrollment-API
