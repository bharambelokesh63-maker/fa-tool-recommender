import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from models.ml_model import FARecommendationModel

fa_model = FARecommendationModel()
accuracy = fa_model.train_model("data/dataset.csv")

df = pd.read_csv("data/dataset.csv")
processed = fa_model.preprocess_data(df)
processed['Preferred_Tool'] = processed.apply(fa_model.determine_preferred_tool, axis=1)

X = processed.drop(columns=['Preferred_Tool'])
y_true = processed['Preferred_Tool']
y_pred = fa_model.model.predict(X)

print("Model Accuracy:", accuracy)
print("\nClassification Report:\n", classification_report(y_true, y_pred))

cm = confusion_matrix(y_true, y_pred, labels=fa_model.model.classes_)
plt.figure(figsize=(10,7))
sns.heatmap(cm, annot=True, fmt='d', xticklabels=fa_model.model.classes_, yticklabels=fa_model.model.classes_, cmap="Blues")
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("True")
plt.show()

importances = fa_model.model.feature_importances_
plt.figure(figsize=(10,6))
plt.bar(fa_model.feature_names, importances)
plt.xticks(rotation=45, ha='right')
plt.title("Feature Importances")
plt.ylabel("Importance")
plt.tight_layout()
plt.show()
