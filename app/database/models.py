from sqlalchemy import Column, Integer, String, Float, Text
from app.database.database import Base


class Student(Base):
    """
    SQLAlchemy Database Model for Students.
    Incorporates core attributes as well as Day 5's worked example ('gender')
    and profile skills/bio for rich ChromaDB semantic vector search.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)  # Day 5 Page 6 worked example!
    course = Column(String, nullable=True, index=True)
    semester = Column(Integer, nullable=True)
    cgpa = Column(Float, nullable=True, index=True)
    phone = Column(String, nullable=True)
    
    # Standout profile fields for ChromaDB semantic retrieval & talent matching
    skills = Column(String, nullable=True)      # e.g. "Python, PyTorch, LangChain, FastAPI"
    interests = Column(String, nullable=True)   # e.g. "Artificial Intelligence, Autonomous Systems"
    bio = Column(Text, nullable=True)           # e.g. "Passionate sophomore researching LLM agents."

    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}', course='{self.course}', cgpa={self.cgpa})>"
