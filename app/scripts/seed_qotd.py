from app.db.database import SessionLocal
from app.models.question import Question


questions = [
    Question(
        type="mcq",
        difficulty="easy",
        content={
            "question": "What is the time complexity of accessing an array element by index?",
            "options": [
                "O(1)",
                "O(log n)",
                "O(n)",
                "O(n log n)",
            ],
        },
        correct_answer={
            "value": "O(1)"
        },
        explanation=(
            "Array elements can be accessed directly using their index, "
            "so the operation takes constant time."
        ),
        points=10,
        tags=["array", "complexity"],
        is_used=False,
    ),

    Question(
        type="mcq",
        difficulty="medium",
        content={
            "question": "Which data structure follows LIFO?",
            "options": [
                "Queue",
                "Stack",
                "Linked List",
                "Graph",
            ],
        },
        correct_answer={
            "value": "Stack"
        },
        explanation=(
            "A stack follows Last-In-First-Out (LIFO)."
        ),
        points=20,
        tags=["stack"],
        is_used=False,
    ),

    Question(
        type="mcq",
        difficulty="hard",
        content={
            "question": "What is the average time complexity of lookup in a hash table?",
            "options": [
                "O(1)",
                "O(log n)",
                "O(n)",
                "O(n log n)",
            ],
        },
        correct_answer={
            "value": "O(1)"
        },
        explanation=(
            "Hash tables provide O(1) average-case lookup time "
            "when the hash function distributes keys well."
        ),
        points=30,
        tags=["hash-table", "complexity"],
        is_used=False,
    ),
]


def seed():
    db = SessionLocal()

    try:
        db.add_all(questions)
        db.commit()
        print("QotD questions inserted successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()