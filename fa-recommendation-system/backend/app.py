from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os
from models.ml_model import FARecommendationModel
from utils.rubric_generator import RubricGenerator
import pandas as pd

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = 'fa_recommendation_secret_key'
CORS(app)

# Initialize ML model
fa_model = FARecommendationModel()
rubric_gen = RubricGenerator()

# Database initialization
def init_db():
    conn = sqlite3.connect('fa_system.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # FA Assessments table
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
    
    # Student responses table
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
    
    # Rubrics table
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
    
    # Insert default users
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', 
                   ('teacher1', 'teacher123', 'teacher'))
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', 
                   ('student1', 'student123', 'student'))
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', 
                   ('student2', 'student123', 'student'))
    
    conn.commit()
    conn.close()

# Initialize database and load model on startup
init_db()

# Try to load existing model, train if not found
if not fa_model.load_model():
    if os.path.exists('data/dataset.csv'):
        fa_model.train_model('data/dataset.csv')
    else:
        print("Warning: No dataset found. Please add dataset.csv to data/ directory")

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
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
        
        if user[2] == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Teacher Routes
@app.route('/teacher/dashboard')
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('fa_system.db')
    cursor = conn.cursor()
    
    # Get teacher's assessments
    cursor.execute('''
        SELECT a.*, COUNT(sr.id) as response_count 
        FROM assessments a 
        LEFT JOIN student_responses sr ON a.id = sr.assessment_id 
        WHERE a.teacher_id = ? 
        GROUP BY a.id 
        ORDER BY a.created_at DESC
    ''', (session['user_id'],))
    assessments = cursor.fetchall()
    
    # Get analytics data
    cursor.execute('''
        SELECT predicted_tool, COUNT(*) as count 
        FROM student_responses sr 
        JOIN assessments a ON sr.assessment_id = a.id 
        WHERE a.teacher_id = ? 
        GROUP BY predicted_tool
    ''', (session['user_id'],))
    tool_analytics = cursor.fetchall()
    
    conn.close()
    
    return render_template('teacher/dashboard.html', 
                         assessments=assessments, 
                         tool_analytics=tool_analytics)

@app.route('/teacher/create_assessment', methods=['GET', 'POST'])
def create_assessment():
    if session.get('role') != 'teacher':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        subject_name = request.form['subject_name']
        assessment_name = request.form['assessment_name']
        bloom_level = request.form['bloom_level']
        
        conn = sqlite3.connect('fa_system.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO assessments (teacher_id, subject_name, assessment_name, bloom_level) 
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], subject_name, assessment_name, bloom_level))
        conn.commit()
        conn.close()
        
        flash('Assessment created successfully!')
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('teacher/create_assessment.html')

@app.route('/teacher/assessment/<int:assessment_id>')
def view_assessment_details():
    if session.get('role') != 'teacher':
        return redirect(url_for('index'))
    
    assessment_id = request.view_args['assessment_id']
    
    conn = sqlite3.connect('fa_system.db')
    cursor = conn.cursor()
    
    # Get assessment details
    cursor.execute('SELECT * FROM assessments WHERE id = ? AND teacher_id = ?', 
                   (assessment_id, session['user_id']))
    assessment = cursor.fetchone()
    
    # Get student responses
    cursor.execute('''
        SELECT sr.*, u.username 
        FROM student_responses sr 
        JOIN users u ON sr.student_id = u.id 
        WHERE sr.assessment_id = ?
    ''', (assessment_id,))
    responses = cursor.fetchall()
    
    conn.close()
    
    return render_template('teacher/assessment_details.html', 
                         assessment=assessment, 
                         responses=responses)

@app.route('/teacher/generate_rubric/<int:assessment_id>', methods=['GET', 'POST'])
def generate_rubric():
    if session.get('role') != 'teacher':
        return redirect(url_for('index'))
    
    assessment_id = request.view_args['assessment_id']
    
    if request.method == 'POST':
        total_marks = int(request.form['total_marks'])
        
        conn = sqlite3.connect('fa_system.db')
        cursor = conn.cursor()
        
        # Get assessment details
        cursor.execute('SELECT * FROM assessments WHERE id = ?', (assessment_id,))
        assessment = cursor.fetchone()
        
        # Get most recommended tool for this assessment
        cursor.execute('''
            SELECT predicted_tool, COUNT(*) as count 
            FROM student_responses 
            WHERE assessment_id = ? 
            GROUP BY predicted_tool 
            ORDER BY count DESC 
            LIMIT 1
        ''', (assessment_id,))
        top_tool = cursor.fetchone()
        
        # Generate rubric
        rubric_data = rubric_gen.generate_rubric(
            assessment_name=assessment[3],
            fa_tool=top_tool[0] if top_tool else 'Quiz',
            total_marks=total_marks,
            bloom_level=assessment[4]
        )
        
        # Save rubric
        cursor.execute('''
            INSERT OR REPLACE INTO rubrics (assessment_id, total_marks, rubric_data) 
            VALUES (?, ?, ?)
        ''', (assessment_id, total_marks, json.dumps(rubric_data)))
        
        conn.commit()
        conn.close()
        
        flash('Rubric generated successfully!')
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('teacher/rubric_generator.html', assessment_id=assessment_id)

# Student Routes
@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('fa_system.db')
    cursor = conn.cursor()
    
    # Get available assessments
    cursor.execute('SELECT * FROM assessments WHERE is_active = 1 ORDER BY created_at DESC')
    assessments = cursor.fetchall()
    
    # Get student's previous responses
    cursor.execute('''
        SELECT sr.*, a.subject_name, a.assessment_name 
        FROM student_responses sr 
        JOIN assessments a ON sr.assessment_id = a.id 
        WHERE sr.student_id = ? 
        ORDER BY sr.created_at DESC
    ''', (session['user_id'],))
    my_responses = cursor.fetchall()
    
    conn.close()
    
    return render_template('student/dashboard.html', 
                         assessments=assessments, 
                         my_responses=my_responses)

@app.route('/student/assessment/<int:assessment_id>')
def student_assessment_form():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    
    assessment_id = request.view_args['assessment_id']
    
    conn = sqlite3.connect('fa_system.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM assessments WHERE id = ?', (assessment_id,))
    assessment = cursor.fetchone()
    conn.close()
    
    return render_template('student/assessment_form.html', assessment=assessment)

@app.route('/student/submit_assessment', methods=['POST'])
def submit_assessment():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    
    # Get form data
    assessment_id = request.form['assessment_id']
    year_of_study = int(request.form['year_of_study'])
    study_hours = int(request.form['study_hours'])
    confidence_level = int(request.form['confidence_level'])
    learning_mode = int(request.form['learning_mode'])
    difficulty_level = int(request.form['difficulty_level'])
    time_available = int(request.form['time_available'])
    topic_type = int(request.form['topic_type'])
    resources = request.form.getlist('resources')
    previous_tools = request.form.getlist('previous_tools')
    bloom_focus = request.form.getlist('bloom_focus')
    
    # Prepare data for ML prediction
    student_data = {
        'year': year_of_study,
        'study_hours': study_hours,
        'confidence': confidence_level,
        'learning_mode': learning_mode,
        'difficulty': difficulty_level,
        'time_available': time_available,
        'topic_type': topic_type
    }
    
    # Get ML prediction
    prediction_result = fa_model.predict_fa_tool(student_data)
    
    # Save to database
    conn = sqlite3.connect('fa_system.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO student_responses (
            assessment_id, student_id, year_of_study, study_hours, confidence_level,
            learning_mode, difficulty_level, time_available, topic_type, resources,
            previous_tools, bloom_focus, predicted_tool, confidence_score, explanation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        assessment_id, session['user_id'], year_of_study, study_hours, confidence_level,
        learning_mode, difficulty_level, time_available, topic_type, 
        ','.join(resources), ','.join(previous_tools), ','.join(bloom_focus),
        prediction_result['predicted_tool'], prediction_result['confidence'], 
        prediction_result['explanation']
    ))
    conn.commit()
    conn.close()
    
    return render_template('student/recommendation.html', 
                         prediction=prediction_result,
                         student_data=student_data)

# API Routes for AJAX calls
@app.route('/api/assessment_analytics/<int:assessment_id>')
def get_assessment_analytics():
    if session.get('role') != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401
    
    assessment_id = request.view_args['assessment_id']
    
    conn = sqlite3.connect('fa_system.db')
    cursor = conn.cursor()
    
    # Get tool distribution
    cursor.execute('''
        SELECT predicted_tool, COUNT(*) as count
        FROM student_responses 
        WHERE assessment_id = ? 
        GROUP BY predicted_tool
    ''', (assessment_id,))
    tool_distribution = [{'tool': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Get confidence distribution
    cursor.execute('''
        SELECT confidence_level, COUNT(*) as count
        FROM student_responses 
        WHERE assessment_id = ? 
        GROUP BY confidence_level
    ''', (assessment_id,))
    confidence_distribution = [{'level': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Get learning mode distribution
    cursor.execute('''
        SELECT learning_mode, COUNT(*) as count
        FROM student_responses 
        WHERE assessment_id = ? 
        GROUP BY learning_mode
    ''', (assessment_id,))
    learning_mode_distribution = [{'mode': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'tool_distribution': tool_distribution,
        'confidence_distribution': confidence_distribution,
        'learning_mode_distribution': learning_mode_distribution
    })

if __name__ == '__main__':
    app.run(debug=True)