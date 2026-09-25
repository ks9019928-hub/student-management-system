from app.database.database import SessionLocal, engine, Base
from app.database.models import Student
from app.vectorstore.chroma import vector_store

SEED_STUDENTS = [
    {
        "name": "Abhishek Kumar",
        "email": "abhishek@example.com",
        "age": 20,
        "gender": "Male",
        "course": "CSE",
        "semester": 5,
        "cgpa": 8.5,
        "phone": "9876543210",
        "skills": "Python, FastAPI, Machine Learning, LangChain",
        "interests": "Generative AI, Agentic Workflows, Backend Systems",
        "bio": "Pre-final year CSE student building intelligent full-stack applications with LLMs."
    },
    {
        "name": "Rahul Sharma",
        "email": "rahul@example.com",
        "age": 21,
        "gender": "Male",
        "course": "CSE",
        "semester": 5,
        "cgpa": 8.1,
        "phone": "9876543211",
        "skills": "Java, Spring Boot, MySQL, Docker",
        "interests": "Cloud Native Microservices, Distributed Databases",
        "bio": "Enthusiastic backend engineer focused on high-throughput microservice architectures."
    },
    {
        "name": "Priya Singh",
        "email": "priya@example.com",
        "age": 20,
        "gender": "Female",
        "course": "ECE",
        "semester": 5,
        "cgpa": 9.0,
        "phone": "9876543212",
        "skills": "Embedded C, IoT, Signal Processing, Computer Vision",
        "interests": "Autonomous Robotics, Edge AI, Drone Tech",
        "bio": "Top academic ranker in ECE researching real-time edge computer vision on microcontrollers."
    },
    {
        "name": "Aman Kumar",
        "email": "aman@example.com",
        "age": 21,
        "gender": "Male",
        "course": "CSE",
        "semester": 6,
        "cgpa": 7.8,
        "phone": "9876543213",
        "skills": "JavaScript, React, Node.js, Tailwind CSS",
        "interests": "Full Stack Web Development, UI/UX Interaction",
        "bio": "Creative front-end developer passionate about smooth responsive user interfaces."
    },
    {
        "name": "Sneha Patel",
        "email": "sneha@example.com",
        "age": 22,
        "gender": "Female",
        "course": "AI & Data Science",
        "semester": 7,
        "cgpa": 9.3,
        "phone": "9876543214",
        "skills": "PyTorch, Transformers, Deep Learning, NLP",
        "interests": "Large Language Models, Multimodal AI, Healthcare Diagnostics",
        "bio": "Senior student published in biomedical NLP and transformer fine-tuning."
    },
    {
        "name": "Rohan Verma",
        "email": "rohan@example.com",
        "age": 19,
        "gender": "Male",
        "course": "ECE",
        "semester": 3,
        "cgpa": 8.4,
        "phone": "9876543215",
        "skills": "VLSI, Verilog, Circuit Design, Python",
        "interests": "Semiconductor Design, FPGA Acceleration",
        "bio": "Second-year electronics student exploring hardware accelerators for machine learning."
    },
    {
        "name": "Ananya Roy",
        "email": "ananya@example.com",
        "age": 20,
        "gender": "Female",
        "course": "CSE",
        "semester": 4,
        "cgpa": 8.9,
        "phone": "9876543216",
        "skills": "Python, Data Analysis, SQL, Tableau, Pandas",
        "interests": "Data Analytics, Business Intelligence, FinTech",
        "bio": "Aspiring data analyst with strong quantitative modeling and visualization capabilities."
    },
    {
        "name": "Vikram Malhotra",
        "email": "vikram@example.com",
        "age": 22,
        "gender": "Male",
        "course": "Mechanical",
        "semester": 7,
        "cgpa": 7.9,
        "phone": "9876543217",
        "skills": "SolidWorks, ANSYS, MATLAB, Python Automation",
        "interests": "Automotive Engineering, Aerodynamics, EV Design",
        "bio": "Lead chassis designer for the university formula student race car team."
    }
]


def seed_database(force: bool = False):
    """Seed the SQLite database and sync ChromaDB vectors."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = db.query(Student).count()
        if count > 0 and not force:
            print(f"[Seed] Database already contains {count} students. Skipping auto-seed.")
            return

        print(f"[Seed] Populating database with {len(SEED_STUDENTS)} diverse student records...")
        for data in SEED_STUDENTS:
            existing = db.query(Student).filter(Student.email == data["email"]).first()
            if not existing:
                student = Student(**data)
                db.add(student)
                db.commit()
                db.refresh(student)
                # Auto-sync to ChromaDB
                try:
                    vector_store.add_or_update(student)
                except Exception as e:
                    print(f"[Seed Warning] Vector store sync error: {e}")

        print("[Seed] Seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database(force=True)
