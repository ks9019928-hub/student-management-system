from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import Student
from app.schemas.student import StudentCreate, StudentUpdate


def create_student(db: Session, student: StudentCreate) -> Student:
    """Create a new student record in SQLite (Day 5: CRUD - Create)."""
    db_student = Student(
        name=student.name,
        email=student.email,
        age=getattr(student, "age", None),
        gender=getattr(student, "gender", None),
        course=getattr(student, "course", None),
        semester=getattr(student, "semester", None),
        cgpa=getattr(student, "cgpa", None),
        phone=getattr(student, "phone", None),
        skills=getattr(student, "skills", None),
        interests=getattr(student, "interests", None),
        bio=getattr(student, "bio", None),
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    course: Optional[str] = None,
    min_cgpa: Optional[float] = None,
    search: Optional[str] = None,
) -> List[Student]:
    """Retrieve multiple students with optional filtering (Day 5: CRUD - Read)."""
    query = db.query(Student)
    if course:
        query = query.filter(Student.course.ilike(f"%{course}%"))
    if min_cgpa is not None:
        query = query.filter(Student.cgpa >= min_cgpa)
    if search:
        query = query.filter(
            (Student.name.ilike(f"%{search}%")) |
            (Student.email.ilike(f"%{search}%")) |
            (Student.skills.ilike(f"%{search}%"))
        )
    return query.offset(skip).limit(limit).all()


def get_student(db: Session, student_id: int) -> Optional[Student]:
    """Read a single student by primary key ID."""
    return db.query(Student).filter(Student.id == student_id).first()


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    """Read a single student by unique email address."""
    return db.query(Student).filter(Student.email.ilike(email)).first()


def update_student(
    db: Session,
    student_id: int,
    student: StudentUpdate
) -> Optional[Student]:
    """Update existing student attributes (Day 5: CRUD - Update)."""
    db_student = get_student(db, student_id)
    if not db_student:
        return None

    update_data = student.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_student, key):
            setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int) -> Optional[Student]:
    """Delete a student record by ID (Day 5: CRUD - Delete)."""
    db_student = get_student(db, student_id)
    if not db_student:
        return None

    db.delete(db_student)
    db.commit()
    return db_student


def get_student_stats(db: Session) -> dict:
    """Compute aggregate analytics for the student dashboard."""
    total = db.query(Student).count()
    if total == 0:
        return {
            "total_students": 0,
            "average_cgpa": 0.0,
            "highest_cgpa": 0.0,
            "department_distribution": {}
        }

    avg_cgpa = db.query(func.avg(Student.cgpa)).scalar() or 0.0
    max_cgpa = db.query(func.max(Student.cgpa)).scalar() or 0.0

    dept_counts = (
        db.query(Student.course, func.count(Student.id))
        .group_by(Student.course)
        .all()
    )
    dist = {course or "Unassigned": count for course, count in dept_counts}

    return {
        "total_students": total,
        "average_cgpa": round(float(avg_cgpa), 2),
        "highest_cgpa": round(float(max_cgpa), 2),
        "department_distribution": dist
    }
