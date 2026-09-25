import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Verify service health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_crud_student_lifecycle():
    """Verify complete CRUD lifecycle: Create, Read, Update, Delete."""
    test_email = "abhi@gmail.com"

    # 1. CREATE
    payload = {
        "name": "Abhishek",
        "email": test_email,
        "age": 20,
        "course": "CSE",
        "semester": 5,
        "cgpa": 8.5,
        "phone": "9876543210"
    }
    create_res = client.post("/students/", json=payload)
    assert create_res.status_code in [200, 201]
    created = create_res.json()
    assert created["id"] is not None
    assert created["name"] == "Abhishek"
    student_id = created["id"]

    # 2. READ (One)
    read_res = client.get(f"/students/{student_id}")
    assert read_res.status_code == 200
    assert read_res.json()["email"] == test_email

    # 3. READ (All with filter)
    filter_res = client.get("/students/?course=CSE&min_cgpa=8.0")
    assert filter_res.status_code == 200
    cse_students = filter_res.json()
    assert any(s["id"] == student_id for s in cse_students)

    # 4. UPDATE
    update_res = client.put(f"/students/{student_id}", json={"cgpa": 9.2, "semester": 6})
    assert update_res.status_code == 200
    assert update_res.json()["cgpa"] == 9.2
    assert update_res.json()["semester"] == 6

    # 5. CREATE SECOND STUDENT
    payload2 = {
        "name": "Rahul Sharma",
        "email": "rahul@gmail.com",
        "age": 21,
        "course": "CSE",
        "semester": 5,
        "cgpa": 8.1,
        "phone": "9876543211"
    }
    create_res2 = client.post("/students/", json=payload2)
    assert create_res2.status_code in [200, 201]
    assert create_res2.json()["name"] == "Rahul Sharma"

    # 6. DELETE FIRST STUDENT
    delete_res = client.delete(f"/students/{student_id}")
    assert delete_res.status_code == 200

    # 7. VERIFY 404 AFTER DELETION
    not_found_res = client.get(f"/students/{student_id}")
    assert not_found_res.status_code == 404


def test_upsert_on_same_email():
    """Verify that re-submitting with the same email updates student instead of breaking."""
    email = "test.upsert@example.com"
    res1 = client.post("/students/", json={"name": "First Input", "email": email, "cgpa": 7.5})
    assert res1.status_code in [200, 201]
    id1 = res1.json()["id"]

    res2 = client.post("/students/", json={"name": "Updated Input", "email": email, "cgpa": 8.9})
    assert res2.status_code in [200, 201]
    assert res2.json()["id"] == id1
    assert res2.json()["name"] == "Updated Input"
    assert res2.json()["cgpa"] == 8.9


def test_student_stats():
    """Verify statistical aggregation endpoint."""
    response = client.get("/students/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_students" in data
    assert "average_cgpa" in data
    assert data["total_students"] >= 0


def test_ai_chatbot_structured_query():
    """Verify LangGraph chatbot endpoint with structured query."""
    response = client.post("/chat/", json={"message": "Who are all the CSE students?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "source" in data


def test_ai_chatbot_semantic_query():
    """Verify LangGraph chatbot endpoint with semantic query."""
    response = client.post("/chat/", json={"message": "Find students skilled in machine learning"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["source"] in ["chromadb", "hybrid"]
