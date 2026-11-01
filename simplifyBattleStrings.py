from data_generation import *


keywords = {
    "yellow" : "small",
    "orange" : "medium",
    "blue"   : "big",
    "red"    : "huge",
    "computer" : "hit chance",
    "shield"   : "evasion",
    "interceptor" : "ship",
    "cruiser"     : "ship",
    "dreadnought" : "ship",
    "starbase"    : "ship"
}

def vectorToSimplifiedBattles (x):
    battleString = vectorToBattle([int(v) for v in x]).toString()

    for keyword in keywords:
        replacement = keywords[keyword]
        battleString = battleString.replace (keyword, replacement)

    return battleString
        
if __name__ == "__main__":

    battle = [1,5,0,0,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,14,0,0,0,0,0,0,0,2,0,0,0,0,0,0,1,7,4,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    print (vectorToBattle([int(v) for v in battle]).toString())
    print(vectorToSimplifiedBattles(battle))