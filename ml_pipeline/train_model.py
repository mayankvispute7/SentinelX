import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
import xgboost as xgb
import joblib
import warnings

warnings.filterwarnings('ignore')

print("🚀 Starting SentinelX Model Training Pipeline...")

# 1. Load Dataset
print("Loading data...")
df = pd.read_csv('creditcard.csv')

# 2. Explore Class Imbalance
fraud_cases = df[df['Class'] == 1]
valid_cases = df[df['Class'] == 0]
print(f"Total Transactions: {len(df)}")
print(f"Fraudulent Transactions: {len(fraud_cases)} ({round(len(fraud_cases)/len(df) * 100, 3)}%)")

"""
WHY FRAUD DATASETS ARE IMBALANCED:
In the real world, 99.8% of transactions are legitimate. If a model simply guessed 
"Not Fraud" every single time, it would be 99.8% accurate, but entirely useless. 
We must force the model to pay attention to the minority class.
"""

# 3. Split into Features (X) and Target (y)
X = df.drop('Class', axis=1)
y = df['Class']

# Split into Train and Test sets (80% training, 20% testing)
# stratify=y ensures the 80/20 split maintains the same ratio of fraud to non-fraud
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 4. Handle Imbalance dynamically
# scale_pos_weight is the ratio of negative class to positive class
scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])
print(f"Calculated scale_pos_weight: {scale_pos_weight:.2f}")

# 5. Train XGBoost Classifier
print("Training XGBoost Model (This may take a minute or two)...")
model = xgb.XGBClassifier(
    objective='binary:logistic',
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    max_depth=4, # Kept relatively shallow to prevent overfitting
    n_estimators=100
)

model.fit(X_train, y_train)

# 6. Evaluate the Model
print("Evaluating Model...")
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)

print("\n--- MODEL METRICS ---")
print(f"Precision: {precision:.4f} (When it flags fraud, how often is it right?)")
print(f"Recall:    {recall:.4f} (Out of all actual fraud, how much did it catch?)")
print(f"F1 Score:  {f1:.4f}")
print(f"ROC-AUC:   {roc_auc:.4f}")

"""
WHY RECALL MATTERS MORE THAN ACCURACY:
In fraud detection, a False Negative (missing a fraudulent transaction) costs the 
company actual money (chargebacks, lost funds). A False Positive (flagging a normal 
transaction as fraud) costs user friction (they have to click an SMS link to verify).
We optimize for Recall to catch as much fraud as possible, accepting a slight 
increase in False Positives.
"""

# 7. Save the Model
print("\nSaving model to disk...")
joblib.dump(model, 'model.pkl')
print("✅ Model successfully saved as 'model.pkl'. Phase 1 Complete.")