import requests
import json

# Use a session to persist cookies between requests
session = requests.Session()

# 1. Login
login = session.post(
    "http://127.0.0.1:5000/api/login",   # Use /api/login
    json={"username": "student1", "password": "student123"}
)

print("Login Response:")
print(json.dumps(login.json(), indent=2))

if login.status_code != 200:
    print("Login failed. Exiting...")
    exit()

# 2. Predict FA tool
student_data = {
    "student_id": 1,
    "student_data": {
        "year": 2,
        "study_hours": 2,
        "confidence": 4,
        "learning_mode": 3,
        "difficulty": 2,
        "time_available": 2,
        "topic_type": 3
    }
}

predict = session.post(
    "http://127.0.0.1:5000/api/predict",
    json=student_data
)

print("\nPrediction Response:")
print(json.dumps(predict.json(), indent=2))
