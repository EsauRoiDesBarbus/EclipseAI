from model_training import *
from dataset_generation import DATASET_2, DATASET_3



MODEL_PATH = "battle_prediction_neural_network.keras"
fit_model_to_dataset_and_save(DATASET_3, MODEL_PATH)


evaluate_model (DATASET_2, MODEL_PATH)



