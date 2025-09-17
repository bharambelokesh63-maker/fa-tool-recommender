from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import json
import os
from models.ml_model import FARecommendationModel
from utils.rubric_generator import RubricGenerator

app = Flask(__name__)
app.secret_key = 'fa_recommendation_secret_key'
CORS(app)

# Initialize ML model and rubric generator
fa_model = FARecommendationModel()
rubric_gen = RubricGenerator()

# Database setup
def init_db():
    conn = sqlite3.connect('fa_system.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            subject_name TEXT NOT NULL,
            assessment_name TEXT NOT NULL,
            bloom_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER,
            student_id INTEGER,
            year_of_study INTEGER,
            study_hours INTEGER,
            confidence_level INTEGER,
            learning_mode INTEGER,
            difficulty_level INTEGER,
            time_available INTEGER,
            topic_type INTEGER,
            resources TEXT,
            previous_tools TEXT,
            bloom_focus TEXT,
            predicted_tool TEXT,
            confidence_score REAL,
            explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES assessments (id),
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rubrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER,
            total_marks INTEGER,
            rubric_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES assessments (id)
        )
    ''')

    # Default users
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)',
                   ('teacher1', 'teacher123', 'teacher'))
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)',
                   ('student1', 'student123', 'student'))
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)',
                   ('student2', 'student123', 'student'))

    conn.commit()
    conn.close()

# Init DB + Model
init_db()
if not fa_model.load_model():
    if os.path.exists('data/dataset.csv'):
        fa_model.train_model('data/dataset.csv')
    else:
        print("⚠️ No dataset found in data/ directory")

# ---------- ROUTES ---------- #

@app.route('/')
def index():
    return jsonify({"status": "Backend is running", "message": "FA Tool Recommendation System API"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect('fa_system.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM users WHERE username = ? AND password = ?',
                   (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['role'] = user[2]
        return jsonify({"message": "Login successful", "role": user[2], "username": user[1]})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

# Teacher endpoints
@app.route('/teacher/assessments', methods=['GET'])
def teacher_assessments():
    if session.get('role') != 'teacher':
        return jsonify({"error": "Unauthorized"}), 401

    conn = sqlite3.connect('fa_system.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM assessments WHERE teacher_id = ?', (session['user_id'],))
    assessments = cursor.fetchall()
    conn.close()

    return jsonify({"assessments": assessments})

@app.route('/teacher/create_assessment', methods=['POST'])
def create_assessment():
    if session.get('role') != 'teacher':
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    subject_name = data.get("subject_name")
    assessment_name = data.get("assessment_name")
    bloom_level = data.get("bloom_level")

    conn = sqlite3.connect('fa_system.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO assessments (teacher_id, subject_name, assessment_name, bloom_level)
        VALUES (?, ?, ?, ?)
    ''', (session['user_id'], subject_name, assessment_name, bloom_level))
    conn.commit()
    conn.close()

    return jsonify({"message": "Assessment created successfully"})

@app.route('/teacher/generate_rubric/<int:assessment_id>', methods=['POST'])
def generate_rubric(assessment_id):
    if session.get('role') != 'teacher':
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    total_marks = data.get("total_marks", 20)

    conn = sqlite3.connect('fa_system.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM assessments WHERE id = ?', (assessment_id,))
    assessment = cursor.fetchone()

    if not assessment:
        return jsonify({"error": "Assessment not found"}), 404

    rubric_data = rubric_gen.generate_rubric(
        assessment_name=assessment[3],
        fa_tool="Quiz",
        total_marks=total_marks,
        bloom_level=assessment[4]
    )

    cursor.execute('''
        INSERT OR REPLACE INTO rubrics (assessment_id, total_marks, rubric_data)
        VALUES (?, ?, ?)
    ''', (assessment_id, total_marks, json.dumps(rubric_data)))

    conn.commit()
    conn.close()

    return jsonify({"message": "Rubric generated", "rubric": rubric_data})

# Student endpoints
@app.route('/student/submit_assessment', methods=['POST'])
def submit_assessment():
    if session.get('role') != 'student':
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    assessment_id = data.get("assessment_id")

    student_data = {
        'Year': data.get("year"),
        'LearningStyle': data.get("learning_style"),
        'ConfidenceLevel': data.get("confidence"),
        'BloomLevel': data.get("bloom_level")
    }

    prediction_result = fa_model.predict_fa_tool(student_data)

    conn = sqlite3.connect('fa_system.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO student_responses (
            assessment_id, student_id, year_of_study, study_hours, confidence_level,
            learning_mode, difficulty_level, time_available, topic_type, resources,
            previous_tools, bloom_focus, predicted_tool, confidence_score, explanation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        assessment_id, session['user_id'], data.get("year"), None, data.get("confidence"),
        data.get("learning_style"), None, None, None,
        ','.join(data.get("resources", [])), ','.join(data.get("previous_tools", [])),
        ','.join(data.get("bloom_focus", [])), prediction_result['predicted_tool'],
        prediction_result['confidence'], prediction_result.get("explanation", "Recommended based on ML model")
    ))
    conn.commit()
    conn.close()

    return jsonify({"message": "Response submitted", "prediction": prediction_result})

if __name__ == "__main__":
    app.run(debug=True)
