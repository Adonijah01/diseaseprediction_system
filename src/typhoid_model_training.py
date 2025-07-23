import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# Generate synthetic data for typhoid
np.random.seed(43)
N = 500
# Features: fever, abdominal_pain, headache, diarrhea, constipation, rash, weakness, appetite, blood_test
X = np.random.randint(0, 2, size=(N, 9))
# Simple rule: typhoid likely if prolonged fever, abdominal pain, and positive blood/stool test
y = ((X[:,0] == 1) & (X[:,1] == 1) & (X[:,8] == 1)).astype(int)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=43)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=43)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print('Typhoid model accuracy:', accuracy_score(y_test, y_pred))

# Save model
with open('models/typhoid_model.sav', 'wb') as f:
    pickle.dump(model, f) 