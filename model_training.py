import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

from data_generation import *
from dataset_generation import TRAINING_AND_VALIDATION_DATASET, FINAL_TEST_DATASET

# meta parameters
EPOCHS = 50
VALIDATION_PROPORTION = 0.2

# Load the training and test datasets
train_data = pd.read_csv(TRAINING_AND_VALIDATION_DATASET)
test_data  = pd.read_csv(FINAL_TEST_DATASET)

outputs = 33
# Preprocessing
X_train = train_data.iloc[:,1:-outputs:].values  # All rows, all columns except the first and 33 last ones
y_train = train_data.iloc[:,  -outputs:].values  # All rows, last 33 columns are labels

X_test  =  test_data.iloc[:,1:-outputs:].values   # All rows, all columns except the last one
y_test  =  test_data.iloc[:,  -outputs:].values   # All rows, last column as labels

# Build the neural network model
model = Sequential()

# Input layer
model.add(Dense(128, input_dim=116, activation='relu'))

# Hidden layer
model.add(Dense(256, activation='relu'))
model.add(Dense(128, activation='relu'))
model.add(Dense(64, activation='relu'))

# Output layer with as many neurons as outputs
model.add(Dense(33, activation='relu'))

# Compile the model using MSE loss (L2 norm)
model.compile(optimizer=Adam(), loss='mean_squared_error', metrics=['mae'])  # Mean Absolute Error (optional)

# Train the model
model.fit(X_train, y_train, epochs=EPOCHS, batch_size=32, validation_split=VALIDATION_PROPORTION)  # Validation split is for evaluation during training

# Evaluate the model on the test dataset
loss, accuracy = model.evaluate(X_test, y_test)

# evaluate win chance specifically
predictions = model.predict(X_test)
win_chance_pred = predictions[:, 0]
win_chance_true = y_test[:, 0]

win_chance_mae = np.mean(np.abs(win_chance_pred - win_chance_true))
win_chance_rmse = np.sqrt(np.mean((win_chance_pred - win_chance_true) ** 2))

print(f"Win chance MAE: {win_chance_mae*100:.1f}%")
print(f"Win chance RMSE: {win_chance_rmse*100:.1f}%")

print(f"Average prediction error: {round(100 * win_chance_mae)}%")


print ("Test 1: 1 base cruiser vs 1 base starbase")
battle_data = Battle ([Ship(1, "CRU", 2, 1, 1, 0, [1,0,0,0,0], [0,0,0,0,0])], BattleModifier(False, False), [Ship(1, "SBA", 4, 2, 1, 0, [1,0,0,0,0], [0,0,0,0,0])], BattleModifier(False, False))
battle_data.solveBattle()

input_vector = [battle_data.toVector()] # model expects a 2D input
prediction = model.predict(input_vector)
print ("exact value:", battle_data.getResult()["attacker_win_chance"])
print("model prediction:", prediction[0])  # For a single output, we return the scalar value (not the array)


print ("Test 2: 3 base cruisers vs 1 base starbase")
battle_data = Battle ([Ship(3, "CRU", 2, 1, 1, 0, [1,0,0,0,0], [0,0,0,0,0])], BattleModifier(False, False), [Ship(1, "SBA", 4, 2, 1, 0, [1,0,0,0,0], [0,0,0,0,0])], BattleModifier(False, False))
battle_data.solveBattle()
input_vector = [battle_data.toVector()] # model expects a 2D input

prediction = model.predict(input_vector)
print ("exact value:", battle_data.getResult()["attacker_win_chance"])
print("model prediction:", prediction[0])  # For a single output, we return the scalar value (not the array)
