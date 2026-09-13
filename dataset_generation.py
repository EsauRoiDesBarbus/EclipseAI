from data_generation import *
import os
import csv
from time import time

TRAINING_AND_VALIDATION_DATASET = "datasets/training_and_validation_dataset.csv"
FINAL_TEST_DATASET = "datasets/final_test_dataset.csv"
TIMEOUT_DATASET = "datasets/timeout_dataset.csv"
ERROR_DATASET = "datasets/error_dataset.csv"

if __name__ == "__main__":

    NUMBER_OF_RANDOM_BATTLES = 100000

    MAX_SHIP_TYPES = 2

    TRAINING_AND_VALIDATION_PERCENTAGE = 90 # the rest are set apart for final validation

    datasets = [TRAINING_AND_VALIDATION_DATASET, FINAL_TEST_DATASET, TIMEOUT_DATASET, ERROR_DATASET]

    timeout = 30 # seconds

    # Check if the file exists
    for dataset in datasets:
        if not os.path.exists(dataset):
            with open(dataset, mode='w', newline='') as file:
                writer = csv.writer(file)

    #pull all signatures from datasets
    signatures = []
    for dataset in datasets:
        with open(dataset, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                signatures.append(row[0])

    
    # generate data
    doublons = 0
    timeouts = 0

    start_time = time ()
    for i in range (NUMBER_OF_RANDOM_BATTLES):

        print (i, time ()-start_time)
        # generate battle 
        battle_data = randomBattle(max_ships=MAX_SHIP_TYPES)
        print (battle_data.toString())

        # check signatures for doublon
        signature = battle_data.signature()
        if signature in signatures:
            doublons+=1
            continue # this battle is already in one of the datasets, create another one
        else:
            signatures.append(signature)

            # solve battle 
            status = battle_data.solveBattle(timeout)

            if (status=="TIMEOUT"):
                # solveBattle timed out
                timeouts+=1
                dataset = TIMEOUT_DATASET
                with_result = False
            elif (status=="OK"):
                with_result = True
                # solveBattle finished within time
                # add to one of the datasets
                random_number_between_0_and_99 = signature%100
                if   random_number_between_0_and_99 <TRAINING_AND_VALIDATION_PERCENTAGE:
                    dataset = TRAINING_AND_VALIDATION_DATASET
                else:
                    dataset = FINAL_TEST_DATASET
            else:
                dataset = ERROR_DATASET
                with_result = False

            addBattleToCSV(battle_data, dataset, with_result)


    print ("Doublons: ", doublons)
    print ("timeouts: ", timeouts)
