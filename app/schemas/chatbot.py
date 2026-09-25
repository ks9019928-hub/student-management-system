from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, json_schema_extra={"example": "What is Abhishek's CGPA?"})


class ChatResponse(BaseModel):
    response: str
    source: str = Field(..., description="DataSource: 'sqlite', 'chromadb', 'hybrid', or 'general'")
    tools_used: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
