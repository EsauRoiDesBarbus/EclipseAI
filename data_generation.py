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

def randomShip (type):
    #todo make it random
    if (type=="INT"):
        return ShipData(1, "INT", 3, 0, 0, 0, [1,0,0,0,0], [0,0,0,0,0])
    if (type=="CRU"):
        return ShipData(1, "CRU", 2, 1, 1, 0, [1,0,0,0,0], [0,0,0,0,0])
    if (type=="DRE"):
        return ShipData(1, "DRE", 1, 2, 1, 0, [2,0,0,0,0], [0,0,0,0,0])
    if (type=="SBA"):
        return ShipData(1, "SBA", 4, 2, 1, 0, [1,0,0,0,0], [0,0,0,0,0])

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