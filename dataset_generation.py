from data_generation import *
import os
import csv
from time import time

if __name__ == "__main__":
    train_dataset = "datasets/training_dataset.csv"
    tests_dataset = "datasets/testing_dataset.csv"
    verif_dataset = "datasets/verification_dataset.csv"
    error_dataset = "datasets/error_dataset.csv"
    datasets = [train_dataset, tests_dataset, verif_dataset, error_dataset]

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
    start_time = time ()
    for i in range (1000):
        # generate battle 
        battle_data = randomBattle(max_ships=2)


        # check signatures for doublon
        signature = battle_data.signature()
        if signature in signatures:
            doublons+=1
            continue # this battle is already in one of the datasets, create another one
        else:
            signatures.append(signature)
            print (i, time ()-start_time)
            # TODO: add timeout
            battle_data.solveBattle()

            # add to one of the datasets
            if battle_data.errorCheck():
                dataset = error_dataset
            else:
                key = signature%10 # 50% training, 30% testing, 20% verification
                if   key <5:
                    dataset = train_dataset
                elif key <8:
                    dataset = tests_dataset
                else:
                    dataset = verif_dataset

            battle_data.appendToCSV(dataset)
    print ("Doublons: ", doublons)
