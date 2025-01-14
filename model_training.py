import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

from data_generation import *

# Load the training and test datasets
train_data = pd.read_csv('datasets/training_dataset.csv')
test_data  = pd.read_csv('datasets/testing_dataset.csv')

# Preprocessing
# Assuming the last column is the label (y) and the rest are features (X)
X_train = train_data.iloc[:, 1:-2].values  # All rows, all columns except the first and two last ones
y_train = train_data.iloc[:,   -1].values  # All rows, last column as labels

X_test  =  test_data.iloc[:, 1:-2].values   # All rows, all columns except the last one
y_test  =  test_data.iloc[:,   -1].values    # All rows, last column as labels

# Build the neural network model
model = Sequential()

# Input layer
model.add(Dense(128, input_dim=116, activation='relu'))

# Hidden layer
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(16, activation='relu'))

# Output layer with 1 neuron for regression
model.add(Dense(1, activation='linear'))  # Linear activation for regression

# Compile the model using MSE loss (L2 norm)
model.compile(optimizer=Adam(), loss='mean_squared_error', metrics=['mae'])  # Mean Absolute Error (optional)

# Train the model
model.fit(X_train, y_train, epochs=10, batch_size=16, validation_split=0.2)  # Validation split is for evaluation during training

# Evaluate the model on the test dataset
loss, accuracy = model.evaluate(X_test, y_test)

print(f"Test Loss: {loss}")


print ("Test 1: 1 base cruiser vs 1 base starbase")
battle_data = BattleData ([ShipData(1, "CRU", 2, 1, 1, 0, [1,0,0,0,0], [0,0,0,0,0])], BonusData(0,0), [ShipData(1, "SBA", 4, 2, 1, 0, [1,0,0,0,0], [0,0,0,0,0])], BonusData(0,0))
battle_data.solveBattle()
print ("exact value:", battle_data._attacker_win_chance)
input_vector = [battle_data.toVector()] # model expects a 2D input

prediction = model.predict(input_vector)
print("model prediction:", prediction[0][0])  # For a single output, we return the scalar value (not the array)


print ("Test 2: 3 base cruisers vs 1 base starbase")
battle_data = BattleData ([ShipData(3, "CRU", 2, 1, 1, 0, [1,0,0,0,0], [0,0,0,0,0])], BonusData(0,0), [ShipData(1, "SBA", 4, 2, 1, 0, [1,0,0,0,0], [0,0,0,0,0])], BonusData(0,0))
battle_data.solveBattle()
print ("exact value:", battle_data._attacker_win_chance)
input_vector = [battle_data.toVector()] # model expects a 2D input

prediction = model.predict(input_vector)
print("model prediction:", prediction[0][0])  # For a single output, we return the scalar value (not the array)
