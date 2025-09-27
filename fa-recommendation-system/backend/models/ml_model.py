import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class FARecommendationModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoders = {}
        self.feature_names = []
        self.fa_tools = [
            'Quiz', 'Project', 'Lab Work', 'Case Study', 'Group Work',
            'Presentation / PPT', 'Written Paper', 'Role Play',
            'Poster Presentation', 'Viva / Oral Test', 'Reflection Journal',
            'Open Book Test'
        ]
        
    def preprocess_data(self, df):
        """Preprocess the dataset for training"""
        # Create a copy to avoid modifying original data
        data = df.copy()
        
        # Map categorical variables to numerical
        categorical_mappings = {
            'What is your current year of study ?': {
                '1st Year': 1, '2nd Year': 2, '3rd Year': 3, '4th Year': 4
            },
            'How many hours per week do you usually spend on self-study (outside lectures)?': {
                '0–5 hours': 1, '6–10 hours': 2, '11–15 hours': 3, '16–20 hours': 4, 'More than 20 hours': 5
            },
            'How confident do you feel about understanding new topics? (Self-confidence level)': {
                '1 (Very Low) 😟': 1, '2 (Low) 😕': 2, '3 (Moderate) 😐': 3, '4 (High) 🙂': 4, '5 (Very High) 😃': 5
            },
            'What is your preferred learning mode?': {
                'Reading / Writing (Books, Notes)': 1, 'Listening (Lectures, Podcasts)': 2,
                'Watching (Videos, Animations)': 3, 'Doing Experiments / Practical Work': 4
            },
            ' How difficult do you usually find your course topics?': {
                'Easy': 1, 'Medium': 2, 'Hard': 3, 'Very Hard': 4
            },
            'How much time do you usually have for completing assessments?': {
                'Short (less than 30 mins)': 1, 'Medium (30–60 mins)': 2, 'Long (more than 1 hour)': 3
            },
            'What type of topic do you usually study?': {
                'Theory': 1, 'Practical': 2, 'Mixed': 3
            }
        }
        
        # Apply categorical mappings
        for column, mapping in categorical_mappings.items():
            if column in data.columns:
                data[column] = data[column].map(mapping)
        
        # Handle multi-select columns (resources, previous tools, bloom's levels)
        multi_select_columns = [
            'Which resources are easily available to you? (Select all that apply)',
            'Which formative assessment tools have you used before? (Select all that apply)',
            ' Which Bloomâ€™s Taxonomy level do you want to focus on improving?'
        ]
        
        for col in multi_select_columns:
            if col in data.columns:
                # Split by semicolon and create binary features
                unique_values = set()
                for value in data[col].dropna():
                    if isinstance(value, str):
                        unique_values.update([v.strip() for v in value.split(';')])
                
                for unique_val in unique_values:
                    data[f'{col}_{unique_val}'] = data[col].apply(
                        lambda x: 1 if isinstance(x, str) and unique_val in x else 0
                    )
                data.drop(col, axis=1, inplace=True)
        
        return data
    
    def determine_preferred_tool(self, row):
        """Logic to determine preferred FA tool based on student characteristics"""
        # Extract key features
        year = row.get('What is your current year of study ?', 2)
        confidence = row.get('How confident do you feel about understanding new topics? (Self-confidence level)', 3)
        learning_mode = row.get('What is your preferred learning mode?', 3)
        difficulty = row.get(' How difficult do you usually find your course topics?', 2)
        time_available = row.get('How much time do you usually have for completing assessments?', 2)
        topic_type = row.get('What type of topic do you usually study?', 3)
        
        # Logic for tool recommendation
        if learning_mode == 4:  # Practical work preferred
            if topic_type in [2, 3]:  # Practical or Mixed
                return 'Lab Work'
            else:
                return 'Project'
        elif learning_mode == 3:  # Visual learning
            if time_available == 1:  # Short time
                return 'Quiz'
            else:
                return 'Presentation / PPT'
        elif learning_mode == 1:  # Reading/Writing
            if confidence >= 4:
                return 'Written Paper'
            else:
                return 'Quiz'
        elif learning_mode == 2:  # Listening
            if confidence >= 4:
                return 'Viva / Oral Test'
            else:
                return 'Group Work'
        
        # Default based on confidence and time
        if confidence >= 4 and time_available >= 2:
            return 'Project'
        elif confidence <= 2:
            return 'Quiz'
        else:
            return 'Case Study'
    
    def train_model(self, csv_file_path):
        """Train the model using the dataset"""
        # Load the dataset
        df = pd.read_csv(csv_file_path)
        
        # Preprocess the data
        processed_data = self.preprocess_data(df)
        
        # Generate preferred tool labels
        processed_data['Preferred_Tool'] = processed_data.apply(self.determine_preferred_tool, axis=1)
        
        # Prepare features (X) and target (y)
        feature_columns = [col for col in processed_data.columns if col != 'Preferred_Tool']
        X = processed_data[feature_columns]
        y = processed_data['Preferred_Tool']
        
        # Handle any remaining NaN values
        X = X.fillna(0)
        
        self.feature_names = feature_columns
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model Accuracy: {accuracy:.2f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Save the model
        self.save_model()
        
        return accuracy
    
    def predict_fa_tool(self, student_data):
        """Predict FA tool for a student"""
        # Convert student data to DataFrame
        df = pd.DataFrame([student_data])
        
        # Preprocess the data
        processed_data = self.preprocess_data(df)
        
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in processed_data.columns:
                processed_data[feature] = 0
        
        # Reorder columns to match training data
        processed_data = processed_data[self.feature_names].fillna(0)
        
        # Make prediction
        prediction = self.model.predict(processed_data)[0]
        prediction_proba = self.model.predict_proba(processed_data)[0]
        
        # Get feature importance for explanation
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        # Generate explanation
        explanation = self.generate_explanation(student_data, prediction, feature_importance)
        
        return {
            'predicted_tool': prediction,
            'confidence': max(prediction_proba),
            'explanation': explanation,
            'all_probabilities': dict(zip(self.model.classes_, prediction_proba))
        }
    
    def generate_explanation(self, student_data, prediction, feature_importance):
        """Generate explanation for the recommendation"""
        explanations = []
        
        # Confidence level explanation
        confidence = student_data.get('confidence', 3)
        if confidence >= 4:
            explanations.append("Your high confidence level suggests you can handle more challenging assessments.")
        elif confidence <= 2:
            explanations.append("Your confidence level indicates you might benefit from less intimidating assessment formats.")
        
        # Learning mode explanation
        learning_mode_map = {1: "reading/writing", 2: "listening", 3: "visual", 4: "hands-on"}
        learning_mode = student_data.get('learning_mode', 3)
        if learning_mode in learning_mode_map:
            explanations.append(f"Your {learning_mode_map[learning_mode]} learning preference aligns well with {prediction}.")
        
        # Time availability explanation
        time_available = student_data.get('time_available', 2)
        if time_available == 1 and prediction in ['Quiz', 'Viva / Oral Test']:
            explanations.append("Given your limited time, this assessment format is efficient and focused.")
        elif time_available == 3 and prediction in ['Project', 'Case Study']:
            explanations.append("Your available time allows for more comprehensive assessment formats.")
        
        # Study hours explanation
        study_hours = student_data.get('study_hours', 2)
        if study_hours >= 3:
            explanations.append("Your dedicated study time indicates readiness for detailed assessment formats.")
        
        return " ".join(explanations) if explanations else "This tool is recommended based on your overall learning profile."
    
    def save_model(self, filename='data/fa_model.pkl'):
        """Save the trained model"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'fa_tools': self.fa_tools
        }
        joblib.dump(model_data, filename)
        print(f"Model saved to {filename}")
    
    def load_model(self, filename='data/fa_model.pkl'):
        """Load a trained model"""
        if os.path.exists(filename):
            model_data = joblib.load(filename)
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            self.fa_tools = model_data['fa_tools']
            print(f"Model loaded from {filename}")
            return True
        return False

# Usage example
if __name__ == "__main__":
    # Initialize and train the model
    fa_model = FARecommendationModel()
    
    # Train with your dataset
    accuracy = fa_model.train_model('data/dataset.csv')
    
    # Example prediction
    student_example = {
        'year': 2,
        'study_hours': 2,
        'confidence': 4,
        'learning_mode': 3,
        'difficulty': 2,
        'time_available': 2,
        'topic_type': 3
    }
    
    result = fa_model.predict_fa_tool(student_example)
    print(f"\nPrediction: {result['predicted_tool']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Explanation: {result['explanation']}")