from eclipseCpp_interface import *
from random import randint, choices, sample
from time import time
import csv


#################
# WRITE IN FILE #
#################
def addBattleToCSV (battle, file, with_result=True):
    # the format is (int) signature, (int array) toVector, (float array) _result_vector
    row = [battle.signature()] + battle.toVector() 
    if (with_result):
        row+= [i for i in battle._result_vector]

    with open(file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

###############################
# RANDOM GENERATION FUNCTIONS #
###############################
def smallStatBonus ():
    # function that returns a small increment, to account for stat bonuses on discovery tiles and such
    return choices(range(0,4), weights = [0.9, 0.08, 0.01, 0.01])[0]

def decreasingLikelyhood (max_number):
    # function that returns a random number between 1 and max_number, with exponentially decreasing likelyhood
    # n+1 is 2 times less likely than n
    rand_number = randint (1, 2**max_number-1)
    number = 1
    while (rand_number<2**(max_number-number)):
        number+=1
    return number


def randomShip (type):
    #todo make it random
    if (type=="INT"):
        max_number = 8
        free_tiles = 4
        initiative = 3
        #return ShipData(1, "INT", 3, 0, 0, 0, [1,0,0,0,0], [0,0,0,0,0]) # base INT
    if (type=="CRU"):
        max_number = 4
        free_tiles = 6
        initiative = 2
        #return ShipData(1, "CRU", 2, 1, 1, 0, [1,0,0,0,0], [0,0,0,0,0]) # base CRU
    if (type=="DRE"):
        max_number = 2
        free_tiles = 8
        initiative = 1
        #return ShipData(1, "DRE", 1, 2, 1, 0, [2,0,0,0,0], [0,0,0,0,0]) # base DRE
    if (type=="SBA"):
        max_number = 4
        free_tiles = 5
        initiative = 4
        #return ShipData(1, "SBA", 4, 2, 1, 0, [1,0,0,0,0], [0,0,0,0,0]) # base SBA
    
    # generate a number of ships, with weight such that 
    number = decreasingLikelyhood(max_number)

    # generate initiative
    if (type!="SBA"):
        #add engine
        engine_initiative = choices (range (0, 5), weights =[0.1, 0.4, 0.25, 0.2, 0.05])[0] # the engine that give 0 and 4 initiative are more rare
        nb_engines = choices (range (1, 4), weights = [0.9, 0.05, 0.05])[0]
        free_tiles-=nb_engines
        initiative+=engine_initiative*nb_engines
    # other bonuses to initiative
    initiative+=smallStatBonus()

    # remove tiles for power
    nb_power = choices (range(0,4), weights = [0.05, 0.8, 0.1, 0.05])[0]
    free_tiles-=nb_power

    # there should always be at least 1 weapon
    free_tiles = max (1, free_tiles)

    # generate weapon
    nb_weapons = decreasingLikelyhood(free_tiles) 
    canons   = [0,0,0,0,0]
    missiles = [0,0,0,0,0]

    canons_or_missiles = choices (range(0, 2), weights = [0.8, 0.2])[0]
    if (canons_or_missiles==0): # canons
        color = choices (range(5), weights = [0.3, 0.3, 0.1, 0.2, 0.1])[0]
        canons[color] += nb_weapons
    else: # missiles
        color = choices (range(4), weights = [0.1, 0.7, 0.1, 0.1])[0] # there are no pink missiles
        if (color<=1):
            missiles[color] += 2*nb_weapons #yellow and orange missiles come in pairs
        else:
            nb_weapons = 1 # blue and red missiles are discovery tiles so there can only be 1
            missiles[color] += nb_weapons
        
    free_tiles-=nb_weapons


    # split remaining tiles between hull, computer and shield
    # start with a small base value for each of the 3 stats
    hull = smallStatBonus ()
    computer = smallStatBonus ()
    shield = smallStatBonus ()
    # choose one tech for each stat
    hull_tech     = choices (range(1,4), weights =[0.3, 0.6, 0.1])[0]
    computer_tech = choices (range(1,4), weights =[0.3, 0.4, 0.3])[0]
    shield_tech   = randint (1, 2)
    # for each remaining free tile, add 1 of the 3 stats
    while (free_tiles>0):
        choice = randint (0, 2)
        if (choice==0):
            hull+=hull_tech
        if (choice==1):
            computer+=computer_tech
        if (choice==2):
            shield+=shield_tech
        free_tiles-=1

    return Ship(number, type, initiative, hull, computer, shield, canons, missiles)



def randomBattle (max_ships=2):
    nb_attacker_ships = randint(1, min(3, max_ships-1))
    nb_defender_ships = randint(1, min(4, max_ships-nb_attacker_ships))

    attacker_ships = []
    for type in sample(["INT", "CRU", "DRE"]       , k=nb_attacker_ships):
        attacker_ships.append(randomShip(type))

    defender_ships = []
    for type in sample(["INT", "CRU", "DRE", "SBA"], k=nb_defender_ships):
        defender_ships.append(randomShip(type))

    #TODO randomize bonuses
    return Battle(attacker_ships, BattleModifier (False, False), defender_ships, BattleModifier (False, False))

if __name__ == "__main__":
    # small battery of tests
    #battle = randomBattle(max_ships=5)
    #print (battle.toString())
    #print (vectorToBattle(battle.toVector()).toString())
    #print (battle.solveBattle())
    #print (battle._attacker_win_chance)
    #print (battle._calculation_time)


    start_time = time ()
    for i in range (1000):
        print (i, time ()-start_time)
        battle = randomBattle(max_ships=4)
        battle.solveBattle()
        addBattleToCSV(battle, "datasets/test.csv")

    #for i in range (10):
    #    ship = randomShip("INT")
    #    print (ship.toVector())
    #    print (ship.toString())
    #    print (vectorToShip(ship.toVector(), "INT").toString())

    vec = [1,3,0,3,0,0,2,0,0,0,0,0,0,0,0,0,1,8,0,5,1,0,0,0,0,0,0,0,2,0,0,0,1,1,5,3,3,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,2,1,2,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    print (len(vec))
    print (vectorToBattle(vec).toString())