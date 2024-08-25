import pandas as pd
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from model import create_model

# Load and preprocess data
df = pd.read_csv('data/synthetic_student_data.csv')

# Convert categorical data to numerical
activity_type_mapping = {'quiz': 0, 'homework': 1, 'lecture': 2}
df['activity_type'] = df['activity_type'].map(activity_type_mapping)

# Prepare sequences
sequences = []
labels = []
for student_id, group in df.groupby('student_id'):
    sequence = group[['activity_type', 'outcome', 'time_spent']].values
    sequences.append(sequence)
    labels.append(group['outcome'].iloc[-1])

# Pad sequences
sequences = pad_sequences(sequences, dtype='float32', padding='post')

# Train/test split
X_train, X_val, y_train, y_val = train_test_split(sequences, labels, test_size=0.2, random_state=42)

# Create and train the model
input_shape = (X_train.shape[1], X_train.shape[2])
model = create_model(input_shape)
model.fit(X_train, np.array(y_train), epochs=10, batch_size=64, validation_data=(X_val, np.array(y_val)))

# Save the model
model.save('saved_model.h5')
