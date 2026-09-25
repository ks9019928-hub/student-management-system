from typing import Dict, Any
from app.ai.graph import student_ai_graph
from app.schemas.chatbot import ChatResponse


class ChatbotService:
    """
    Chatbot Service layer (Day 9: Encapsulation).
    Invokes the LangGraph workflow and formats the output.
    """

    @staticmethod
    def process_message(message: str) -> ChatResponse:
        initial_state = {
            "user_message": message,
            "route": "general",
            "tools_called": [],
            "context_data": {},
            "final_response": ""
        }

        # Execute the LangGraph workflow
        result = student_ai_graph.invoke(initial_state)

        return ChatResponse(
            response=result.get("final_response", ""),
            source=result.get("route", "general"),
            tools_used=result.get("tools_called", []),
            metadata={
                "tools_count": len(result.get("tools_called", [])),
                "has_context": bool(result.get("context_data"))
            }
        )
