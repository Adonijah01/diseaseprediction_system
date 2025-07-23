import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# Generate synthetic data for AIDS (HIV)
np.random.seed(44)
N = 500
# Features: weight_loss, fever, night_sweats, fatigue, lymph_nodes, risky_behavior, hiv_test
X = np.random.randint(0, 2, size=(N, 7))
# Simple rule: AIDS likely if weight loss, fever, and positive HIV test
y = ((X[:,0] == 1) & (X[:,1] == 1) & (X[:,6] == 1)).astype(int)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=44)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=44)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print('AIDS model accuracy:', accuracy_score(y_test, y_pred))

# Save model
with open('models/aids_model.sav', 'wb') as f:
    pickle.dump(model, f) 