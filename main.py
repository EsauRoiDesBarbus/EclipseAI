from model_training import *
from dataset_generation import DATASET_2, DATASET_3, DATASET_4



MODEL_PATH = "battle_prediction_neural_network.keras"



training_and_validation_data = pd.DataFrame(
    np.vstack([pd.read_csv(DATASET_2).values,pd.read_csv(DATASET_3).values])
)
test_data  = pd.read_csv(DATASET_4)

fit_model_to_dataset_and_save(training_and_validation_data, MODEL_PATH)


evaluate_model (test_data, MODEL_PATH)



