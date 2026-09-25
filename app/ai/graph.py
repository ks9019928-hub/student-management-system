from typing import TypedDict, List, Dict, Any, Optional
import re
from langgraph.graph import StateGraph, END

from app.ai.gemini import get_llm
from app.ai.tools import (
    find_student_by_name,
    query_students_by_filter,
    get_aggregate_stats,
    search_student_skills_semantic
)


class ChatbotState(TypedDict):
    """
    LangGraph Workflow State.
    Maintains user input, routing decision, retrieved context, and final synthesis.
    """
    user_message: str
    route: str                    # 'sqlite', 'chromadb', 'hybrid', or 'general'
    tools_called: List[str]
    context_data: Dict[str, Any]
    final_response: str


def router_node(state: ChatbotState) -> ChatbotState:
    """
    Step 1 in LangGraph: Analyze the user question and determine storage routing.
    - Day 5 & 6 Concept:
      SQLite -> Structured fields (name, course, semester, cgpa, age, counts)
      ChromaDB -> Semantic concepts (skills, interests, machine learning, web dev, projects)
    """
    message = state["user_message"].lower()

    semantic_keywords = [
        "interested", "interest", "skill", "skills", "machine learning", "ml",
        "ai", "data science", "web", "frontend", "backend", "devops",
        "python", "react", "cybersecurity", "profile", "background", "recommend", "talent"
    ]
    structured_keywords = [
        "cgpa", "gpa", "marks", "score", "semester", "sem", "cse", "ece", "it", "mech",
        "how many", "count", "average", "highest", "lowest", "list all", "student id", "phone", "email"
    ]

    has_semantic = any(kw in message for kw in semantic_keywords)
    has_structured = any(kw in message for kw in structured_keywords)

    if has_semantic and has_structured:
        route = "hybrid"
    elif has_semantic:
        route = "chromadb"
    elif has_structured:
        route = "sqlite"
    else:
        # Check if looking for a specific student's name
        words = [w for w in message.split() if len(w) > 3 and w not in ["what", "who", "where", "which", "show", "tell", "give"]]
        route = "sqlite" if words else "general"

    state["route"] = route
    return state


def execute_tools_node(state: ChatbotState) -> ChatbotState:
    """
    Step 2 in LangGraph: Execute SQLite and/or ChromaDB tools based on routing.
    """
    route = state["route"]
    message = state["user_message"]
    msg_lower = message.lower()
    tools_called = []
    context = {}

    if route in ["sqlite", "hybrid"]:
        # Case A: Check for specific student name
        name_match = re.search(r"(?:who is|about|cgpa of|marks of|is)\s+([A-Za-z]+)", message, re.IGNORECASE)
        student_name = name_match.group(1) if name_match else None
        
        # Also test common name patterns in message
        if not student_name:
            for word in message.split():
                clean_word = re.sub(r"[^A-Za-z]", "", word)
                if clean_word.lower() not in ["what", "who", "show", "list", "students", "student", "highest", "lowest", "cgpa", "course", "semester"]:
                    test_res = find_student_by_name(clean_word)
                    if test_res.get("status") == "success":
                        student_name = clean_word
                        break

        if student_name:
            res = find_student_by_name(student_name)
            tools_called.append(f"find_student_by_name('{student_name}')")
            context["student_lookup"] = res
        
        # Case B: Aggregate stats
        if any(term in msg_lower for term in ["how many", "total", "average", "departments", "count"]):
            stats = get_aggregate_stats()
            tools_called.append("get_aggregate_stats()")
            context["aggregate_stats"] = stats

        # Case C: Filtering by CGPA / course / semester
        course = None
        for c in ["cse", "ece", "it", "mech", "civil", "ai"]:
            if c in msg_lower.split() or f" {c} " in f" {msg_lower} ":
                course = c.upper()
                break

        min_cgpa = None
        cgpa_match = re.search(r"(?:above|greater than|>|>=)\s*([0-9\.]+)", msg_lower)
        if cgpa_match:
            try:
                min_cgpa = float(cgpa_match.group(1))
            except ValueError:
                pass

        top_n = None
        if "highest" in msg_lower or "top" in msg_lower:
            top_n = 3

        sem = None
        sem_match = re.search(r"semester\s*([0-9]+)", msg_lower)
        if sem_match:
            try:
                sem = int(sem_match.group(1))
            except ValueError:
                pass

        if course or min_cgpa is not None or top_n or sem or not student_name:
            filtered = query_students_by_filter(
                course=course,
                min_cgpa=min_cgpa,
                semester=sem,
                top_n=top_n
            )
            tools_called.append("query_students_by_filter()")
            context["student_filter"] = filtered

    if route in ["chromadb", "hybrid"]:
        # Query ChromaDB semantic vector store
        res = search_student_skills_semantic(query=message, top_k=4)
        tools_called.append("search_student_skills_semantic()")
        context["vector_matches"] = res

    state["tools_called"] = tools_called
    state["context_data"] = context
    return state


def synthesizer_node(state: ChatbotState) -> ChatbotState:
    """
    Step 3 in LangGraph: Gemini LLM synthesizes Prompt + Context into final response.
    - Day 6 Concept:
      Prompt: User's question
      Context: Data retrieved by SQLite/ChromaDB tools
    """
    user_msg = state["user_message"]
    context = state["context_data"]
    route = state["route"]
    tools = state["tools_called"]

    llm = get_llm()

    if llm:
        try:
            from langchain_core.messages import SystemMessage, HumanMessage
            system_prompt = (
                "You are the intelligent NexusEdu Student Management AI Assistant.\n"
                "Answer the user's question clearly, concisely, and accurately based ONLY on the provided context.\n"
                "If the context provides student data, format names, CGPAs, courses, and skills neatly.\n"
                "Do not make up facts not present in the context."
            )
            context_str = f"Route Used: {route}\nRetrieved Context: {context}\nTools Invoked: {tools}"
            human_prompt = f"Context:\n{context_str}\n\nUser Question: {user_msg}"

            ai_message = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ])
            state["final_response"] = ai_message.content
            return state
        except Exception as e:
            print(f"[Synthesizer LLM Warning] Fallback triggered: {e}")

    # Deterministic fallback formatting (ensures app works smoothly even before entering API key)
    lines = []
    if "student_lookup" in context and context["student_lookup"].get("status") == "success":
        s = context["student_lookup"]["student"]
        lines.append(f"Student Found: {s['name']}")
        lines.append(f"• Course: {s.get('course')}, Semester: {s.get('semester')}")
        lines.append(f"• CGPA: {s.get('cgpa')}")
        lines.append(f"• Email: {s.get('email')}, Phone: {s.get('phone')}")
        if s.get("skills"):
            lines.append(f"• Skills: {s.get('skills')}")

    elif "student_filter" in context and context["student_filter"].get("status") == "success":
        st_list = context["student_filter"]["students"]
        lines.append(f"Found {len(st_list)} student(s) matching your request:")
        for idx, s in enumerate(st_list, 1):
            lines.append(f"{idx}. {s['name']} — {s.get('course') or 'N/A'} (Semester {s.get('semester') or 'N/A'}), CGPA: {s.get('cgpa')}")

    elif "vector_matches" in context and context["vector_matches"].get("status") == "success":
        matches = context["vector_matches"]["matches"]
        lines.append(f"ChromaDB Semantic Search found {len(matches)} relevant profile(s):")
        for idx, m in enumerate(matches, 1):
            lines.append(f"{idx}. {m['name']} ({m.get('course')}, CGPA: {m.get('cgpa')})")
            lines.append(f"   {m.get('document')}")

    elif "aggregate_stats" in context and context["aggregate_stats"].get("status") == "success":
        stats = context["aggregate_stats"]
        lines.append(f"Overall Student Statistics:")
        lines.append(f"• Total Enrolled: {stats['total_students']}")
        lines.append(f"• Average CGPA: {stats['average_cgpa']}")
        lines.append(f"• Departments: {stats['departments']}")
    else:
        lines.append("I am your Student Management AI Assistant. You can ask me about student CGPA, department lists, or search by skills (e.g., 'What is Abhishek's CGPA?' or 'Find students skilled in machine learning').")

    state["final_response"] = "\n".join(lines)
    return state


def build_langgraph_app():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(ChatbotState)

    workflow.add_node("router", router_node)
    workflow.add_node("execute_tools", execute_tools_node)
    workflow.add_node("synthesizer", synthesizer_node)

    workflow.set_entry_point("router")
    workflow.add_edge("router", "execute_tools")
    workflow.add_edge("execute_tools", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow.compile()


# Global compiled LangGraph workflow instance
student_ai_graph = build_langgraph_app()
