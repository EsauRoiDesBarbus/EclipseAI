from data_generation import *
import os
import csv
from time import time

DATASET_2 = "datasets/2_ship_types.csv"
DATASET_3 = "datasets/3_ship_types.csv"
DATASET_4 = "datasets/4_ship_types.csv"
DATASET_5 = "datasets/5_ship_types.csv"
TIMEOUT_DATASET = "datasets/timeouts.csv"
ERROR_DATASET = "datasets/errors.csv"

if __name__ == "__main__":

    NUMBER_OF_RANDOM_BATTLES = 1000000

    NUMBER_SHIP_TYPES = 3

    datasets = [DATASET_2, DATASET_3, DATASET_4, DATASET_5, TIMEOUT_DATASET, ERROR_DATASET]

    timeout_s = 30

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
    duplicates = 0
    timeouts = 0

    start_time = time ()
    for random_battle in range (NUMBER_OF_RANDOM_BATTLES):

        print (random_battle, time ()-start_time)
        # generate battle 
        battle_data = randomBattle(number_ship_types=NUMBER_SHIP_TYPES)
        print (battle_data.toString())
        print ("Duplicates proportion : " + str(100.*duplicates/(1+random_battle)) + "%")

        # check signatures for doublon
        signature = battle_data.signature()
        if signature in signatures:
            duplicates+=1
            continue # this battle is already in one of the datasets, create another one
        else:
            signatures.append(signature)

            # solve battle 
            status = battle_data.solveBattle(timeout_s)

            if (status=="TIMEOUT"):
                # solveBattle timed out
                timeouts+=1
                dataset = TIMEOUT_DATASET
                with_result = False
            elif (status=="OK"):
                with_result = True
                # solveBattle finished within time
                # add to one of the datasets

                ship_types = battle_data.numberOfShipTypes()

                dataset =DATASET_2 if ship_types==2 \
                    else DATASET_3 if ship_types==3 \
                    else DATASET_4 if ship_types==4 \
                    else DATASET_5
            else:
                dataset = ERROR_DATASET
                with_result = False

            addBattleToCSV(battle_data, dataset, with_result)

    print ("timeouts: ", timeouts)
