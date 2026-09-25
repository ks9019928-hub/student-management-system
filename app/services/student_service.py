from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.models import Student
from app.schemas.student import StudentCreate, StudentUpdate
from app.crud import student as student_crud
from app.vectorstore.chroma import vector_store


class StudentService:
    """
    Encapsulates business operations on Students (Day 9: Encapsulation).
    Ensures that whenever SQLite records are created, updated, or deleted,
    the ChromaDB vector store remains synchronized automatically.
    """

    @staticmethod
    def create(db: Session, student_in: StudentCreate) -> Student:
        student = student_crud.create_student(db, student_in)
        # Real-time synchronization with ChromaDB vector store
        try:
            vector_store.add_or_update(student)
        except Exception as e:
            print(f"[Service Warning] ChromaDB sync failed on create: {e}")
        return student

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        course: Optional[str] = None,
        min_cgpa: Optional[float] = None,
        search: Optional[str] = None
    ) -> List[Student]:
        return student_crud.get_students(
            db=db,
            skip=skip,
            limit=limit,
            course=course,
            min_cgpa=min_cgpa,
            search=search
        )

    @staticmethod
    def get_by_id(db: Session, student_id: int) -> Optional[Student]:
        return student_crud.get_student(db, student_id)

    @staticmethod
    def update(
        db: Session,
        student_id: int,
        student_in: StudentUpdate
    ) -> Optional[Student]:
        student = student_crud.update_student(db, student_id, student_in)
        if student:
            try:
                vector_store.add_or_update(student)
            except Exception as e:
                print(f"[Service Warning] ChromaDB sync failed on update: {e}")
        return student

    @staticmethod
    def delete(db: Session, student_id: int) -> Optional[Student]:
        student = student_crud.delete_student(db, student_id)
        if student:
            try:
                vector_store.delete(student_id)
            except Exception as e:
                print(f"[Service Warning] ChromaDB delete failed: {e}")
        return student

    @staticmethod
    def get_stats(db: Session) -> dict:
        return student_crud.get_student_stats(db)

    @staticmethod
    def sync_all_to_vectorstore(db: Session) -> int:
        """Re-indexes all students from SQLite into ChromaDB."""
        students = student_crud.get_students(db, limit=1000)
        synced = 0
        for s in students:
            if vector_store.add_or_update(s):
                synced += 1
        return synced
