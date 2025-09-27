#!/usr/bin/env python3
"""
FA Recommendation System - Application Runner

This file serves as the main entry point for the FA Recommendation System.
It initializes the Flask application and handles the ML model training.

Usage:
    python run.py
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

try:
    from app import app
    from models.ml_model import FARecommendationModel
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all required packages are installed:")
    print("pip install -r backend/requirements.txt")
    sys.exit(1)

def setup_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'backend/data',
        'backend/models/__pycache__',
        'backend/utils/__pycache__',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Directory structure verified")

def create_sample_dataset():
    """Create a sample dataset if none exists"""
    dataset_path = Path('backend/data/dataset.csv')
    
    if not dataset_path.exists():
        print("Creating sample dataset...")
        
        # Sample data based on the research paper
        sample_data = {
            'What is your current year of study ?': [
                '2nd Year', '1st Year', '2nd Year', '3rd Year', '2nd Year',
                '2nd Year', '1st Year', '2nd Year', '2nd Year', '2nd Year'
            ],
            'How many hours per week do you usually spend on self-study (outside lectures)?': [
                '6–10 hours', '0–5 hours', '0–5 hours', '0–5 hours', '0–5 hours',
                '6–10 hours', '0–5 hours', '11–15 hours', '6–10 hours', '11–15 hours'
            ],
            'How confident do you feel about understanding new topics? (Self-confidence level)': [
                '4 (High) 🙂', '1 (Very Low) 😟', '3 (Moderate) 😐', '4 (High) 🙂', '3 (Moderate) 😐',
                '4 (High) 🙂', '3 (Moderate) 😐', '3 (Moderate) 😐', '3 (Moderate) 😐', '3 (Moderate) 😐'
            ],
            'What is your preferred learning mode?': [
                'Watching (Videos, Animations)', 'Reading / Writing (Books, Notes)', 
                'Doing Experiments / Practical Work', 'Watching (Videos, Animations)', 
                'Watching (Videos, Animations)', 'Reading / Writing (Books, Notes)',
                'Doing Experiments / Practical Work', 'Watching (Videos, Animations)',
                'Doing Experiments / Practical Work', 'Watching (Videos, Animations)'
            ],
            ' How difficult do you usually find your course topics?': [
                'Medium', 'Easy', 'Medium', 'Medium', 'Medium',
                'Medium', 'Medium', 'Medium', 'Hard', 'Medium'
            ],
            'Which resources are easily available to you? (Select all that apply)': [
                'Internet;Computer', 'None', 'Internet;Computer;Lab', 'Internet',
                'Internet;Computer;Lab', 'Internet;Computer;Lab;Library', 
                'Internet;Computer;Library', 'Internet', 'Internet;Computer;Library', 'Library'
            ],
            'How much time do you usually have for completing assessments?': [
                'Medium (30–60 mins)', 'Short (less than 30 mins)', 'Long (more than 1 hour)',
                'Medium (30–60 mins)', 'Medium (30–60 mins)', 'Medium (30–60 mins)',
                'Medium (30–60 mins)', 'Medium (30–60 mins)', 'Long (more than 1 hour)',
                'Short (less than 30 mins)'
            ],
            'What type of topic do you usually study?': [
                'Mixed', 'Theory', 'Mixed', 'Mixed', 'Mixed',
                'Mixed', 'Theory', 'Mixed', 'Theory', 'Theory'
            ],
            'Which formative assessment tools have you used before? (Select all that apply)': [
                'Quiz;Presentation / PPT;Written Paper;Open Book Test',
                'Quiz;Written Paper', 'Quiz;Lab Work;Case Study;Presentation / PPT;Written Paper;Role Play;Viva / Oral Test',
                'Quiz;Project;Presentation / PPT;Viva / Oral Test;Open Book Test',
                'Quiz;Project;Lab Work;Case Study;Group Work;Presentation / PPT',
                'Quiz;Project;Lab Work;Case Study;Group Work;Presentation / PPT;Written Paper;Role Play;Poster Presentation;Viva / Oral Test;Reflection Journal;Open Book Test',
                'Project;Lab Work;Presentation / PPT;Open Book Test',
                'Quiz;Project;Lab Work;Presentation / PPT;Viva / Oral Test',
                'Presentation / PPT;Poster Presentation',
                'Quiz;Project;Case Study;Presentation / PPT;Role Play;Poster Presentation;Viva / Oral Test'
            ],
            ' Which Bloomâ€™s Taxonomy level do you want to focus on improving?': [
                'Apply;Analyze;Create', 'Remember;Apply', 'Analyze', 'Apply;Evaluate',
                'Remember;Understand;Apply;Analyze;Evaluate;Create', 
                'Remember;Understand;Apply;Analyze;Evaluate;Create',
                'Remember;Understand', 'Remember;Understand;Apply;Analyze;Evaluate',
                'Remember;Understand;Apply;Analyze', 'Evaluate'
            ]
        }
        
        df = pd.DataFrame(sample_data)
        df.to_csv(dataset_path, index=False)
        print(f"✓ Sample dataset created at {dataset_path}")
    else:
        print("✓ Dataset found")

def train_ml_model():
    """Train or load the ML model"""
    print("Initializing ML model...")
    
    model = FARecommendationModel()
    model_path = Path('backend/data/fa_model.pkl')
    dataset_path = Path('backend/data/dataset.csv')
    
    if not model_path.exists() and dataset_path.exists():
        print("Training ML model...")
        try:
            accuracy = model.train_model(str(dataset_path))
            print(f"✓ Model trained successfully with {accuracy:.2%} accuracy")
        except Exception as e:
            print(f"✗ Error training model: {e}")
            return False
    elif model_path.exists():
        try:
            model.load_model(str(model_path))
            print("✓ Pre-trained model loaded successfully")
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            return False
    else:
        print("✗ No dataset found for training")
        return False
    
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'flask', 'pandas', 'numpy', 'scikit-learn', 
        'joblib', 'matplotlib', 'seaborn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("✗ Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✓ All dependencies satisfied")
    return True

def display_welcome_message():
    """Display welcome message and system information"""
    print("=" * 60)
    print("🤖 FA RECOMMENDATION SYSTEM")
    print("   AI-Driven Formative Assessment Tool Recommendation")
    print("=" * 60)
    print("📚 PCCOE - Department of CSE (AI&ML)")
    print("🏆 Young Researchers' Conference 2025")
    print("=" * 60)
    print()

def display_access_info():
    """Display access URLs and credentials"""
    print("🌐 ACCESS INFORMATION")
    print("-" * 30)
    print("Application URL: http://localhost:5000")
    print()
    print("👨‍🏫 TEACHER LOGIN:")
    print("   Username: teacher1")
    print("   Password: teacher123")
    print()
    print("👨‍🎓 STUDENT LOGIN:")
    print("   Username: student1")
    print("   Password: student123")
    print()
    print("📊 FEATURES:")
    print("   • AI-powered assessment recommendations")
    print("   • Interactive teacher dashboard")
    print("   • Student preference analysis")
    print("   • Automated rubric generation")
    print("   • Real-time analytics")
    print("=" * 60)

def main():
    """Main application entry point"""
    display_welcome_message()
    
    print("🚀 INITIALIZING SYSTEM...")
    print("-" * 30)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Create sample dataset if needed
    create_sample_dataset()
    
    # Train/load ML model
    if not train_ml_model():
        print("⚠️  Warning: ML model not available. Some features may not work.")
    
    print()
    display_access_info()
    
    # Start the Flask application
    try:
        print("🔄 Starting Flask server...")
        print("Press Ctrl+C to stop the server")
        print("-" * 60)
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Avoid double initialization
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"✗ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()