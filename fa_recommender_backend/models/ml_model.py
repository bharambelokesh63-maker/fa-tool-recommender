import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class FARecommendationModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_names = []
        self.fa_tools = [
            'Quiz', 'Project', 'Lab Work', 'Case Study', 'Group Work',
            'Presentation / PPT', 'Written Paper', 'Role Play',
            'Poster Presentation', 'Viva / Oral Test', 'Reflection Journal',
            'Open Book Test'
        ]

    def preprocess_data(self, df):
        """Preprocess dataset: map categorical to numeric, drop unused cols"""

        data = df.copy()

        # Year → numeric
        year_mapping = {
            '1st Year': 1,
            '2nd Year': 2,
            '3rd Year': 3,
            '4th Year': 4
        }
        if 'Year' in data.columns:
            data['Year'] = data['Year'].map(year_mapping)

        # Learning style → numeric
        learning_style_mapping = {
            'Visual': 1,
            'Auditory': 2,
            'Reading/Writing': 3,
            'Kinesthetic': 4
        }
        if 'LearningStyle' in data.columns:
            data['LearningStyle'] = data['LearningStyle'].map(learning_style_mapping)

        # ConfidenceLevel → numeric
        if 'ConfidenceLevel' in data.columns:
            data['ConfidenceLevel'] = pd.to_numeric(data['ConfidenceLevel'], errors='coerce')

        # Bloom’s taxonomy → numeric
        bloom_mapping = {
            'Remember': 1,
            'Understand': 2,
            'Apply': 3,
            'Analyze': 4,
            'Evaluate': 5,
            'Create': 6
        }
        if 'BloomLevel' in data.columns:
            data['BloomLevel'] = data['BloomLevel'].map(bloom_mapping)

        # Drop non-feature columns
        drop_cols = ['StudentID', 'PreferredTool', 'LeastEffectiveTool']
        for col in drop_cols:
            if col in data.columns:
                data.drop(col, axis=1, inplace=True)

        return data

    def train_model(self, csv_file_path):
        """Train model using dataset"""
        df = pd.read_csv(csv_file_path)

        # Preprocess dataset
        X = self.preprocess_data(df)

        # Target labels
        y = df['PreferredTool']

        # Handle NaN
        X = X.fillna(0)

        self.feature_names = list(X.columns)

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train RF model
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model Accuracy: {accuracy:.2f}")
        print("\nClassification Report:\n", classification_report(y_test, y_pred))

        # Save model
        self.save_model()

        return accuracy

    def predict_fa_tool(self, student_data):
        """Predict FA tool for a student"""
        df = pd.DataFrame([student_data])

        processed = self.preprocess_data(df)

        # Ensure features match training
        for feature in self.feature_names:
            if feature not in processed.columns:
                processed[feature] = 0
        processed = processed[self.feature_names].fillna(0)

        prediction = self.model.predict(processed)[0]
        prediction_proba = self.model.predict_proba(processed)[0]

        return {
            'predicted_tool': prediction,
            'confidence': float(max(prediction_proba)),
            'all_probabilities': dict(zip(self.model.classes_, prediction_proba))
        }

    def save_model(self, filename='data/fa_model.pkl'):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'feature_names': self.feature_names,
            'fa_tools': self.fa_tools
        }, filename)
        print(f"✅ Model saved to {filename}")

    def load_model(self, filename='data/fa_model.pkl'):
        if os.path.exists(filename):
            data = joblib.load(filename)
            self.model = data['model']
            self.feature_names = data['feature_names']
            self.fa_tools = data['fa_tools']
            print(f"✅ Model loaded from {filename}")
            return True
        return False

# Quick test
if __name__ == "__main__":
    model = FARecommendationModel()
    acc = model.train_model("data/dataset.csv")
    print("Trained with accuracy:", acc)

    student_example = {
        'Year': 2,
        'LearningStyle': 1,
        'ConfidenceLevel': 4,
        'BloomLevel': 3
    }
    print(model.predict_fa_tool(student_example))
