from eclipseCpp import battleBuilder, Weapons
from random import randint, choices


class ShipData:
    def __init__ (self, number, type, initiative, hull, computer, shield, canons, missiles):
        self._number = number
        self._type = type
        self._initiative = initiative
        self._hull = hull
        self._computer = computer
        self._shield = shield
        self._canons = canons
        self._missiles = missiles
        self._regen = 0

    def toVector (self):
        # writes the ship as a vector for the neural network
        # type is not written here as it is implicit as the position in the battle vector
        vec = [self._number, self._initiative, self._hull, self._computer, self._shield, self._regen]
        vec+= [self._canons[0]  ,self._canons[1]  ,self._canons[2]  ,self._canons[3]  ,self._canons[4]]
        vec+= [self._missiles[0],self._missiles[1],self._missiles[2],self._missiles[3],self._missiles[4]]
        return vec

def emptyShip ():
    return ShipData(0, "INT", 0, 0, 0, 0, [0,0,0,0,0], [0,0,0,0,0])

class BonusData:
    def __init__ (self, is_npc, antimatter_splitter):
        # saves battle modifiers as 0 (False) and 1 (True)
        if (is_npc == True)or(is_npc == 1):
            self._is_npc = 1
        else:
            self._is_npc = 0
        if (antimatter_splitter == True)or(antimatter_splitter == 1):
            self._antimatter_splitter = 1
        else:
            self._antimatter_splitter = 0

    def toVector (self):
        # writes the bonus as a vector for the neural network
        return [self._is_npc, self._antimatter_splitter]


class BattleData:
    def __init__ (self, attacker_ships, attacker_bonus, defender_ships, defender_bonus):
        # mirrors the constructor of ShipBattleStates in eclipseCpp
        self._attacker_ships = attacker_ships
        self._defender_ships = defender_ships

        self._attacker_bonus = attacker_bonus
        self._defender_bonus = defender_bonus

    def toVector (self):
        # writes the battle as a vector for the neural network
        vec = []
        for type in ["INT", "CRU", "DRE"]:
            no_ship=True
            for ship in self._attacker_ships:
                if (ship._type == type)and(no_ship):
                    vec+= ship.toVector()
                    no_ship=False
            if (no_ship):
                vec+=emptyShip().toVector()
            
        vec+= self._attacker_bonus.toVector()


        for type in ["INT", "CRU", "DRE", "SBA"]:
            no_ship=True
            for ship in self._defender_ships:
                if (ship._type == type)and(no_ship):
                    vec+= ship.toVector()
                    no_ship=False
            if (no_ship):
                vec+=emptyShip().toVector()

        vec+= self._defender_bonus.toVector()

        return vec
    
    def signature (self):
        # use injective hash function on toVector to detect and remove duplicates
        return hash(tuple(self.toVector()))
    def solveBattle (self):
        # use the eclipseCpp library to solve the battle
        return 0
    def toCSV (self):
        # the format is signature, toVector, Battleresult
        return 0


def smallStatBonus ():
    # function that returns a small increment, to account for stat bonuses on discovery tiles and such
    return choices(range(0,4), weights = [0.7, 0.15, 0.1, 0.05])[0]

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

    return ShipData(number, type, initiative, hull, computer, shield, canons, missiles)



def randomBattle (max_ships=2):
    nb_attacker_ships = randint(1, min(3, max_ships-1))
    nb_defender_ships = randint(1, min(4, max_ships-nb_attacker_ships))

    attacker_ships = []
    for type in choices(["INT", "CRU", "DRE"]       , k=nb_attacker_ships):
        attacker_ships.append(randomShip(type))

    defender_ships = []
    for type in choices(["INT", "CRU", "DRE", "SBA"], k=nb_defender_ships):
        defender_ships.append(randomShip(type))

    #TODO randomize bonuses
    return BattleData(attacker_ships, BonusData (False, False), defender_ships, BonusData (False, False))


battle = randomBattle(max_ships=5)

print (battle.toVector())
print (battle.signature())


for i in range (10):
    print (randomShip("DRE").toVector())