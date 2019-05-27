# Built by Isaac Wheeler, interning at CNR-IIA, beginning on 23/5/2019

# Depends heavily on the rasterized graph data structure created by graphGen.py

import numpy as np

# Position class: for readability
# Implements attributes and methods related to a car's position
class Position:
    """
    At initialization, calls first node index nodeFrom, second nodeTo: be clear about the direction. \n
    Distance is always measured from lower-index node, regardless of direction of travel.
    Makes reference to whatever graph is passed at initialization.
    True direction means nodeTo has higher index than nodeFrom; False means the opposite
    """
    # Should be based either on a single node or on two nodes and progress along edge
    # Should have an equals operator, so that car's positions can be compared
    # Note: equivalence operator will allow for approximate equals, so that it can be used to check if cars are overlapping
    

    def __init__(self, graph, node1, node2, dist = 0, eqTol = 10):
        """
        Takes graph, two integers and a float, indicating node indices and distance along edge
        Graph is stored (by reference).
        If both indices are the same, places car at node and sets atNode = True.
        If indices are different, places car along edge and sets atNode = False.
        Third argument is distance along the edge, from the lower-numbered node to higher-numbered node, which defaults to 0 (placed at lower node)
        eqTol defaults to 10; sets tolerance for equals operator, related to size of cars (in pixels)
        """
        s = self
        s.graph = graph
        s.dist = dist

        # store nodes, check direction of travel and set appropriate booleans
        s.nodeFrom = node1
        s.nodeTo = node2
        if s.nodeTo > s.nodeFrom:
            s.direction = True
            s.atNode = False
        elif s.nodeFrom > s.nodeTo:
            s.direction = False
            s.atNode = False
        else:
            s.atNode = True

        # store then check length of the edge
        if s.direction:
            s.length = graph.edges[(s.nodeFrom, s.nodeTo)]["length"]
        else:
            s.length = graph.edges[(s.nodeTo, s.nodeFrom)]["length"]
        
        if dist > s.length:
            raise ValueError("The distance along an edge must be less than the edge's length.")
            # handle the error??? TODO
            pass
        
        # calculate coordinates of position
        s.fromCoords = s.graph.nodes[s.nodeFrom]["coords"]
        s.toCoords = s.graph.nodes[s.nodeTo]["coords"]
        prog = s.dist / float(s.length)
        s.xPos = int(prog * s.fromCoords[0] + (1-prog) * s.toCoords[0])
        s.yPos = int(prog * s.fromCoords[1] + (1-prog) * s.toCoords[1])
        s.coords = (s.xPos, s.yPos)

        # vars to update always: atNode, dist, xPos, yPos, coords
        # vars to update at node change: fromCoords, toCoords, length, direction


    # equivalence operator (==)
    def __eq__(self, other):
        # TODO
        if self.direction == other.direction:
            if self.nodeFrom == other.nodeFrom and self.nodeTo == other.nodeTo:
                if abs(self.dist - other.dist) <= eqTol:
                    return True
        else:
            if self.nodeFrom == other.nodeTo and self.nodeTo == other.nodeFrom:
                if abs(self.dist - other.dist) <= eqTol:
                    return True
        return False

    # nonequivalence operator (!=) (required by Python 2)
    def __ne__(self, other):
        return not self == other

    def update(self, displace):
        """
        Moves car along edge. If car is already at destination node, fails.
        Takes displacement from previous position as argument. Preferably an integer
        Adds displacement to distance along edge in the appropriate direction
        Updates values: dist, xPos, yPos, coords, atNode
        """
        if self.atNode:
            raise ValueError("A car at a node cannot move, it needs a new destination node")

        self.dist += displace if direction else -= displace
        prog = self.dist / float(self.length)
        self.xPos = int(prog * self.fromCoords[0] + (1-prog) * self.toCoords[0])
        self.yPos = int(prog * self.fromCoords[1] + (1-prog) * self.toCoords[1])
        self.coords = (self.xPos, self.yPos)

        if self.dist <= 0 or self.dist >= self.length:
            self.atNode = True
    
    # generates a new Position object, using a given new node
    def changeNodes(self, newNode):
        """
        If the car is at a node
        """
        if not self.atNode:
            raise ValueError("A car not at its destination node cannot change destination nodes")
        # TODO


# Car class: designed to be independent of visualization system
# Depends on the above Position class
class Car:
    
    def __init__(self, graph, startGiven = False, pos = 0):
        """
        graph argument: a fully built graph. Will be stored by reference in the car's data
        startGiven: defaults to False. If false, randomly generates starting position
        position: defaults to 0, not used. If startGiven True, should be an instance of Position class.
        """

        self.graph = graph
        if startGiven:
            # TODO
            pass
        else:
            startNode = np.random.randint(0, graph.size)

        

    

