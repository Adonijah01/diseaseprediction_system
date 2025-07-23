import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# Generate synthetic data for malaria
np.random.seed(42)
N = 500
# Features: fever, chills, headache, nausea, muscle_pain, fatigue, travel, blood_test
X = np.random.randint(0, 2, size=(N, 8))
# Simple rule: malaria likely if fever, chills, and positive blood test
y = ((X[:,0] == 1) & (X[:,1] == 1) & (X[:,7] == 1)).astype(int)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print('Malaria model accuracy:', accuracy_score(y_test, y_pred))

# Save model
with open('models/malaria_model.sav', 'wb') as f:
    pickle.dump(model, f) 