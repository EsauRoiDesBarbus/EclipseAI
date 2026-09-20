import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

import keras_tuner as kt
from tensorflow import keras
from tensorflow.keras import layers

from data_generation import *

# meta parameters
MAX_EPOCHS = 100
TUNER_EPOCHS = 10
TUNER_TRIALS = 20
VALIDATION_PROPORTION = 0.2
INPUTS = 116
OUTPUTS = 33

def build_model_hardcoded ():
    model = keras.Sequential()

    model.add(keras.Input(shape=(INPUTS,)))
    
    # Tune number of layers
    LAYERS = 4
    for i in range(LAYERS):
        model.add(layers.Dense(
            units=128*2**i,
            activation='relu'))
    for i in range(LAYERS):
        model.add(layers.Dense(
            units=64*2**(LAYERS-i),
            activation='relu'))
    
    model.add(layers.Dense(OUTPUTS,activation='relu'))  # adjust for your output
    
    hp_lr = 1e-4
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=hp_lr),
        loss='mse',
        metrics=['mae'])
    return model


def build_model(hyper_parameters):
    MAX_NEURONS_PER_LAYER = 1024
    MIN_NEURONS_PER_LAYER = 32
    NEURON_STEP = 32
    MIN_HIDDEN_LAYERS = 1
    MAX_HIDDEN_LAYERS = 10

    model = keras.Sequential()

    model.add(keras.Input(shape=(INPUTS,)))

    units=hyper_parameters.Int(f'units', min_value=MIN_NEURONS_PER_LAYER, max_value=MAX_NEURONS_PER_LAYER, step=NEURON_STEP)
    
    # Tune number of layers
    for i in range(hyper_parameters.Int('num_layers', MIN_HIDDEN_LAYERS, MAX_HIDDEN_LAYERS)):
        model.add(layers.Dense(
            units=units,
            activation='relu'))
    
    model.add(layers.Dense(OUTPUTS,activation='relu'))  # adjust for your output
    
    # Tune learning rate
    hp_lr = hyper_parameters.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=hp_lr),
        loss='mse',
        metrics=['mae'])
    return model

def fit_model_to_dataset_and_save(training_and_validation_data, output_path):
    X_train = training_and_validation_data.iloc[:,1:-OUTPUTS:].values  # All rows, all columns except the first and 33 last ones
    y_train = training_and_validation_data.iloc[:,  -OUTPUTS:].values  # All rows, last 33 columns are labels

    # tuner = kt.BayesianOptimization(
    #     build_model,
    #     objective='val_loss',
    #     max_trials=TUNER_TRIALS,
    #     overwrite=True)

    # tuner.search(X_train, y_train,epochs=TUNER_EPOCHS,validation_split=VALIDATION_PROPORTION)
    
    # model = tuner.get_best_models(num_models=1)[0]

    model = build_model_hardcoded ()

    # Train the model
    early_stop = EarlyStopping(
        monitor='val_loss',       # what to watch
        patience=10,               # stop if no improvement for this many epochs
        restore_best_weights=True  # roll back to the best epoch's weights, not the last one
    )
    model.fit(X_train, y_train, epochs=MAX_EPOCHS, batch_size=32, validation_split=VALIDATION_PROPORTION, callbacks=[early_stop])  # Validation split is for evaluation during training
    model.save(output_path)

def evaluate_model (test_data, model_path):
    X_test  =  test_data.iloc[:,1:-OUTPUTS:].values   # All rows, all columns except the last one
    y_test  =  test_data.iloc[:,  -OUTPUTS:].values   # All rows, last column as labels

    model = load_model(model_path)

    loss, accuracy = model.evaluate(X_test, y_test)

    # evaluate win chance specifically
    predictions = model.predict(X_test)
    win_chance_pred = predictions[:, 0]
    win_chance_true = y_test[:, 0]

    win_chance_mae = np.mean(np.abs(win_chance_pred - win_chance_true))
    win_chance_rmse = np.sqrt(np.mean((win_chance_pred - win_chance_true) ** 2))

    print(f"Win chance MAE: {win_chance_mae*100:.1f}%")
    print(f"Win chance RMSE: {win_chance_rmse*100:.1f}%")

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
