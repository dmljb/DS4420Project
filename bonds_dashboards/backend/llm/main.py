# scores = []
# for i in range(len(data)):
#     scores.append({data[i]['date'] : minute_analysis(data[i]['full_text'])})
# with open("scores.json", "w") as f:
#     json.dump(scores, f, indent=2)


# macro_df = pd.DataFrame()
# for i in range(len(data)):
#     macro_df[i] = fetch_macro_indicators(data[i]['date'])

# macro_df = macro_df.T 

# macro_df.to_json('macro_indicators.json', orient='records', indent=2)


# from llm_calls import minute_analysis
# from nlp import extract_fed_sentiment
from data_gathering import fetch_macro_indicators, parse_first_day
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import StratifiedKFold

import json
# Load your data
file_path = 'fomc_training_data.json'
with open(file_path, 'r') as f:
    data = json.load(f)

n_meetings = len(data) - 1 

with open('scores.json', 'r') as f:
    minutes_data = json.load(f)

for item in minutes_data:
    for old_key in list(item.keys()):
        new_key = parse_first_day(old_key)
        if new_key != old_key:
            item[new_key] = item.pop(old_key)

minutes_list = []
for item in minutes_data[:-1]:  # Take first N-1 meetings
    date_label = list(item.keys())[0]
    features = item[date_label]
    features['date_label'] = date_label 
    minutes_list.append(features)

minutes_df = pd.DataFrame(minutes_list)
minutes_df['date'] = pd.to_datetime(minutes_df['date_label']).dt.date
minutes_df = minutes_df.drop(columns=['date_label'])

# Get macro data for meetings 1 to N-1 (current conditions when decisions made)
macro_df = pd.read_json('macro_indicators.json', orient='records')
macro_df = macro_df.iloc[1:n_meetings+1].reset_index(drop=True)  # Take rows 1 to N-1

# Labels: decisions from meetings 1 to N-1 
label_map = {"cut": 0, "hold": 1, "hike": 2}
y = np.array([label_map[data[i]["decision"]] for i in range(1, n_meetings+1)], dtype=np.int32)

# Combine features
combined_df = minutes_df.join(macro_df, lsuffix='_minutes', rsuffix='_macro')
combined_df = combined_df.drop(['date'], axis=1, errors='ignore')

# Now everything should have the same length
print(f"Minutes shape: {minutes_df.shape}")
print(f"Macro shape: {macro_df.shape}")  
print(f"Combined shape: {combined_df.shape}")
print(f"Labels length: {len(y)}")

# Convert to features
Phi = np.asarray(combined_df, dtype=np.float32)

# Verify shapes match
print(f"Phi shape: {Phi.shape}, y shape: {y.shape}")
assert Phi.shape[0] == len(y), f"Mismatch: {Phi.shape[0]} vs {len(y)}"

print("Checking for NaN values:")
print(f"Phi has NaN: {np.isnan(Phi).any()}")
print(f"Phi has inf: {np.isinf(Phi).any()}")
print(f"Phi min/max: {Phi.min():.4f} / {Phi.max():.4f}")

# 2. Check class distribution
print("Label distribution:")
unique, counts = np.unique(y, return_counts=True)
for label, count in zip(unique, counts):
    print(f"  {label}: {count}")


scaler = MinMaxScaler()
Phi = scaler.fit_transform(Phi).astype(np.float32)

# Replace your current train_test_split section with this:
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

def create_model(input_shape):
    model = Sequential([
        Dense(32, activation='relu', input_shape=(input_shape,)),
        Dense(16, activation='relu'),
        Dense(3)  # logits for [cut, hold, hike]
    ])
    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )
    return model

# Replace the StratifiedKFold section with temporal split:

# Define temporal split - use last 20% as test set (most recent meetings)
test_size = int(0.2 * len(Phi))  # Last ~11 meetings
train_size = len(Phi) - test_size

# Split: train on older meetings, test on most recent
Phi_train = Phi[:train_size]
Phi_test = Phi[train_size:]
y_train = y[:train_size]
y_test = y[train_size:]

print(f"Training on meetings 0-{train_size-1} ({train_size} samples)")
print(f"Testing on meetings {train_size}-{len(Phi)-1} ({test_size} samples)")
print(f"Train label distribution: {np.bincount(y_train)}")
print(f"Test label distribution: {np.bincount(y_test)}")

# Train model
model = create_model(Phi_train.shape[1])

history = model.fit(
    Phi_train, y_train,
    epochs=50,
    batch_size=min(16, len(Phi_train)),
    verbose=1
)

# Predict on most recent meetings
logits = model.predict(Phi_test, verbose=0)
probs = tf.nn.softmax(logits, axis=-1).numpy()
y_pred = np.argmax(probs, axis=1)

# Evaluate
print(f"\nTest Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Cut', 'Hold', 'Hike']))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Show predictions with stance
weights = np.array([-1.0, 0.0, 1.0])
stance = (probs * weights).sum(axis=1)

results_df = pd.DataFrame({
    "y_true": y_test,
    "p_cut": probs[:, 0],
    "p_hold": probs[:, 1],
    "p_hike": probs[:, 2],
    "stance": stance
})
print("\nRecent meeting predictions:")
print(results_df)