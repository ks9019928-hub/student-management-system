from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentStatsResponse
)
from app.services.student_service import StudentService

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Adds a student record to SQLite and synchronizes their profile to the ChromaDB vector store."
)
def create(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    from app.crud.student import get_student_by_email
    existing = get_student_by_email(db, student.email)
    if existing:
        # If student already exists with this email, update it so user is never blocked
        update_data = StudentUpdate(**student.model_dump())
        return StudentService.update(db, existing.id, update_data)

    return StudentService.create(db, student)


@router.get(
    "/",
    response_model=List[StudentResponse],
    summary="Retrieve all students",
    description="Fetch list of all students currently stored in the SQLite database."
)
def read_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    course: Optional[str] = Query(None, description="Filter by course/department"),
    min_cgpa: Optional[float] = Query(None, ge=0.0, le=10.0, description="Minimum CGPA filter"),
    search: Optional[str] = Query(None, description="Search by name, email, or skill keywords"),
    db: Session = Depends(get_db)
):
    return StudentService.get_all(
        db=db,
        skip=skip,
        limit=limit,
        course=course,
        min_cgpa=min_cgpa,
        search=search
    )


@router.get(
    "/stats",
    response_model=StudentStatsResponse,
    summary="Get campus analytics and stats",
    description="Compute total students, average CGPA, and branch distribution."
)
def get_stats(db: Session = Depends(get_db)):
    return StudentService.get_stats(db)


@router.post(
    "/seed",
    summary="Populate sample students (Optional)",
    description="Loads sample students into SQLite and ChromaDB for instant demonstration."
)
def seed_sample_students():
    from app.database.seed import seed_database
    seed_database(force=True)
    return {"message": "Sample students successfully populated."}


@router.delete(
    "/all/clear",
    summary="Clear all students",
    description="Empties the SQLite database and ChromaDB vector store for fresh testing."
)
def clear_all_students(db: Session = Depends(get_db)):
    from app.database.models import Student
    from app.vectorstore.chroma import vector_store
    db.query(Student).delete()
    db.commit()
    try:
        col = vector_store._get_collection()
        if col:
            existing_ids = col.get()["ids"]
            if existing_ids:
                col.delete(ids=existing_ids)
    except Exception:
        pass
    return {"message": "Database and vector store cleared. Ready for fresh inputs."}


@router.post(
    "/sync-vectors",
    summary="Re-sync SQLite database with ChromaDB vector store",
    description="Ensures all existing SQLite student records have embeddings in ChromaDB."
)
def sync_vectors(db: Session = Depends(get_db)):
    count = StudentService.sync_all_to_vectorstore(db)
    return {"message": f"Successfully synced {count} student profile(s) to ChromaDB vector store."}


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Retrieve student by ID"
)
def read_one(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = StudentService.get_by_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    return student


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update student details"
)
def update(
    student_id: int,
    student: StudentUpdate,
    db: Session = Depends(get_db)
):
    result = StudentService.update(db, student_id, student)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    return result


@router.delete(
    "/{student_id}",
    summary="Delete student record"
)
def delete(
    student_id: int,
    db: Session = Depends(get_db)
):
    result = StudentService.delete(db, student_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    return {
        "message": "Student deleted successfully",
        "deleted_id": student_id
    }
