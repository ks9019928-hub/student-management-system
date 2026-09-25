import os
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")
os.makedirs(CHROMA_PATH, exist_ok=True)


class StudentVectorStore:
    """
    Manages ChromaDB vector embeddings for semantic search over student profiles.
    Distinguished from SQLite:
      - SQLite: Structured numerical queries (CGPA, Course, ID, CRUD)
      - ChromaDB: Semantic similarity over skills, bio, and career interests.
    """
    def __init__(self, persist_directory: str = CHROMA_PATH):
        self.persist_directory = persist_directory
        self._client = None
        self._collection = None

    def _get_collection(self):
        if self._collection is None:
            try:
                import chromadb
                from chromadb.config import Settings
                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(anonymized_telemetry=False)
                )
                self._collection = self._client.get_or_create_collection(
                    name="students_semantic",
                    metadata={"description": "Student skills and background embeddings"}
                )
            except Exception as e:
                print(f"[VectorStore Warning] Could not initialize ChromaDB: {e}")
                return None
        return self._collection

    @staticmethod
    def _format_student_document(student) -> str:
        """Create a rich semantic text representation of the student profile."""
        skills = getattr(student, "skills", None) or "General coursework"
        interests = getattr(student, "interests", None) or "Academics"
        bio = getattr(student, "bio", None) or "Active undergraduate student."
        course = getattr(student, "course", None) or "General"
        semester = getattr(student, "semester", None) or 1
        cgpa = getattr(student, "cgpa", None) or 0.0

        return (
            f"Student Name: {student.name}. "
            f"Department/Course: {course}, Semester: {semester}, CGPA: {cgpa}. "
            f"Technical Skills & Proficiencies: {skills}. "
            f"Interests & Career Focus: {interests}. "
            f"Biography: {bio}."
        )

    def add_or_update(self, student) -> bool:
        """Upsert a student's semantic embedding."""
        collection = self._get_collection()
        if collection is None:
            return False

        doc = self._format_student_document(student)
        metadata = {
            "student_id": int(student.id),
            "name": str(student.name),
            "course": str(getattr(student, "course", "") or ""),
            "cgpa": float(getattr(student, "cgpa", 0.0) or 0.0),
            "semester": int(getattr(student, "semester", 1) or 1),
        }

        collection.upsert(
            documents=[doc],
            metadatas=[metadata],
            ids=[str(student.id)]
        )
        return True

    def delete(self, student_id: int) -> bool:
        """Remove a student's embedding from ChromaDB upon record deletion."""
        collection = self._get_collection()
        if collection is None:
            return False
        try:
            collection.delete(ids=[str(student_id)])
            return True
        except Exception:
            return False

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Perform semantic similarity search on student profiles."""
        collection = self._get_collection()
        if collection is None:
            return []

        count = collection.count()
        if count == 0:
            return []

        actual_k = min(top_k, count)
        results = collection.query(
            query_texts=[query],
            n_results=actual_k
        )

        matches = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metadatas, distances):
                matches.append({
                    "id": meta.get("student_id"),
                    "name": meta.get("name"),
                    "course": meta.get("course"),
                    "cgpa": meta.get("cgpa"),
                    "semester": meta.get("semester"),
                    "document": doc,
                    "distance": dist,
                })
        return matches

    def count(self) -> int:
        collection = self._get_collection()
        return collection.count() if collection else 0


# Global singleton instance
vector_store = StudentVectorStore()
