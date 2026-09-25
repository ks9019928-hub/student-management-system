from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import SessionLocal
from app.database.models import Student
from app.vectorstore.chroma import vector_store


def find_student_by_name(name: str) -> Dict[str, Any]:
    """
    SQLite Tool: Look up a student by full or partial name.
    Useful for questions like: 'What is Abhishek's CGPA?'
    """
    db: Session = SessionLocal()
    try:
        student = (
            db.query(Student)
            .filter(Student.name.ilike(f"%{name}%"))
            .first()
        )
        if not student:
            return {"status": "not_found", "message": f"No student found with name matching '{name}'."}

        return {
            "status": "success",
            "student": {
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "age": student.age,
                "gender": student.gender,
                "course": student.course,
                "semester": student.semester,
                "cgpa": student.cgpa,
                "phone": student.phone,
                "skills": student.skills,
                "bio": student.bio,
            }
        }
    finally:
        db.close()


def query_students_by_filter(
    course: Optional[str] = None,
    min_cgpa: Optional[float] = None,
    max_cgpa: Optional[float] = None,
    semester: Optional[int] = None,
    top_n: Optional[int] = None,
) -> Dict[str, Any]:
    """
    SQLite Tool: Query students matching structured academic criteria.
    Useful for questions like:
      - 'Who are all the CSE students?'
      - 'Show students with CGPA above 8.0.'
      - 'Who has the highest CGPA?'
    """
    db: Session = SessionLocal()
    try:
        q = db.query(Student)
        if course:
            q = q.filter(Student.course.ilike(f"%{course}%"))
        if min_cgpa is not None:
            q = q.filter(Student.cgpa >= min_cgpa)
        if max_cgpa is not None:
            q = q.filter(Student.cgpa <= max_cgpa)
        if semester is not None:
            q = q.filter(Student.semester == semester)

        if top_n:
            q = q.order_by(Student.cgpa.desc()).limit(top_n)
        else:
            q = q.order_by(Student.name.asc())

        students = q.all()
        return {
            "status": "success",
            "count": len(students),
            "students": [
                {
                    "id": s.id,
                    "name": s.name,
                    "course": s.course,
                    "semester": s.semester,
                    "cgpa": s.cgpa,
                    "gender": s.gender,
                    "skills": s.skills,
                }
                for s in students
            ]
        }
    finally:
        db.close()


def get_aggregate_stats() -> Dict[str, Any]:
    """
    SQLite Tool: Get overall database metrics (counts, averages, departments).
    Useful for questions like:
      - 'How many students are enrolled?'
      - 'What is the average CGPA across branches?'
    """
    db: Session = SessionLocal()
    try:
        total = db.query(Student).count()
        avg_cgpa = db.query(func.avg(Student.cgpa)).scalar() or 0.0
        dept_counts = (
            db.query(Student.course, func.count(Student.id))
            .group_by(Student.course)
            .all()
        )
        return {
            "status": "success",
            "total_students": total,
            "average_cgpa": round(float(avg_cgpa), 2),
            "departments": {dept or "Unknown": count for dept, count in dept_counts}
        }
    finally:
        db.close()


def search_student_skills_semantic(query: str, top_k: int = 4) -> Dict[str, Any]:
    """
    ChromaDB Vector Tool: Perform semantic similarity search over skills, projects, and bios.
    Useful for questions like:
      - 'Find students interested in machine learning'
      - 'Who has skills in backend web development?'
    """
    try:
        results = vector_store.search(query=query, top_k=top_k)
        return {
            "status": "success",
            "matches_found": len(results),
            "matches": results
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
