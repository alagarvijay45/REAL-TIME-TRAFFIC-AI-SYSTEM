import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset
df = pd.read_csv("US_Accidents.csv")

# Reduce size for faster training
df = df.sample(100000)

# Feature engineering
df['Hour'] = pd.to_datetime(df['Start_Time']).dt.hour

# Select features
X = df[['Start_Lat', 'Start_Lng', 'Temperature(F)', 'Hour']]
y = (df['Severity'] > 2).astype(int)

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

print("Accuracy:", model.score(X_test, y_test))

# Save
pickle.dump(model, open("model.pkl", "wb"))
