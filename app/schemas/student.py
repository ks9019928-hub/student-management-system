from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict


class StudentCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    course: Optional[str] = None
    semester: Optional[int] = None
    cgpa: Optional[float] = None
    phone: Optional[str] = None
    skills: Optional[str] = None


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    course: Optional[str] = None
    semester: Optional[int] = None
    cgpa: Optional[float] = None
    phone: Optional[str] = None
    skills: Optional[str] = None


class StudentResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    course: Optional[str] = None
    semester: Optional[int] = None
    cgpa: Optional[float] = None
    phone: Optional[str] = None
    skills: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StudentStatsResponse(BaseModel):
    total_students: int
    average_cgpa: float
    highest_cgpa: float
    department_distribution: Dict[str, int]
