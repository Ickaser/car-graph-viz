# Built by Isaac Wheeler, interning at CNR-IIA, beginning on 23/5/2019

# Depends heavily on the rasterized graph data structure created by graphGen.py

import numpy as np

# Position class: for readability
# Implements attributes and methods related to a car's position
class Position:
    """
    At initialization, calls first node index nodeFrom, second nodeTo: be clear about the direction. \n
    Distance is always measured from lower-index node, regardless of direction of travel; at initialization, pass distance from departure node.
    Makes reference to whatever graph is passed at initialization.
    direction = True means nodeTo has higher index than nodeFrom; False means the opposite
    """
    # Should be based either on a single node or on two nodes and progress along edge
    # Should have an equals operator, so that car's positions can be compared
    # Note: equivalence operator will allow for approximate equals, so that it can be used to check if cars are overlapping
    

    def __init__(self, graph, nodeFrom, nodeTo, dist = 0, eqTol = 10):
        """
        Takes graph, two integers indicating node indices and a distance along edge
        Graph is stored (by reference).
        If both indices are the same, places car at node and sets atNode = True.
        If indices are different, places car along edge and sets atNode = False.
        Third argument is distance along the edge from the departure node. Defaults to 0 (placed at node)
        eqTol defaults to 10; sets tolerance for equals operator, related to size of cars (in pixels)
        """
        s = self
        s.graph = graph
        s.eqTol = eqTol
        

        # store nodes, check direction of travel and set appropriate booleans
        s.nodeFrom = nodeFrom
        s.nodeTo = nodeTo
        if s.nodeTo > s.nodeFrom:
            s.direction = True
            s.atNode = False
        elif s.nodeFrom > s.nodeTo:
            s.direction = False
            s.atNode = False
        # for case where is at node already, compute some coordinates and return early
        else:
            s.atNode = True
            s.coords = s.graph.nodes[s.nodeTo]["coords"]
            s.xPos, s.yPos = s.coords
            return

        # store then check length of the edge
        # take given distance, and match it to system coordinates (from lower-index to higher-index node)
        # compute distance to destination, store it (toNext)
        if s.direction:
            s.length = graph.edges[(s.nodeFrom, s.nodeTo)]["length"]
            s.dist = dist
            s.toNext = s.length - dist
        else:
            s.length = graph.edges[(s.nodeTo, s.nodeFrom)]["length"]
            s.dist = s.length - dist
            s.toNext = dist

        
        
        if dist > s.length+1:
            raise ValueError("The distance along an edge must be less than the edge's length.")
            
        
        # calculate coordinates of position if along an edge
        if not s.atNode:
            #interpolate between node coordinates to find position along edge
            s.fromCoords = s.graph.nodes[s.nodeFrom]["coords"]
            s.toCoords = s.graph.nodes[s.nodeTo]["coords"]
            prog = s.dist / float(s.length)
            s.xPos = int(prog * s.fromCoords[0] + (1-prog) * s.toCoords[0])
            s.yPos = int(prog * s.fromCoords[1] + (1-prog) * s.toCoords[1])
            s.coords = (s.xPos, s.yPos)

        # vars to update always: atNode, dist, xPos, yPos, coords
        # vars to update at node change: fromCoords, toCoords, length, direction

        if s.graph.weighted:
            graph.edges[(s.nodeFrom, s.nodeTo)]["population"][s.direction] += 1


    # equivalence operator (==)
    def __eq__(self, other):
        
        # Two positions are considered equal if they have the same direction, travel nodes, and are within eqTol of each other
        if self.direction == other.direction:
            if self.nodeFrom == other.nodeFrom and self.nodeTo == other.nodeTo:
                if abs(self.dist - other.dist) <= eqTol:
                    return True
        # The following block would give equality of position if traveling in opposite directions at same place
        # else:
        #     if self.nodeFrom == other.nodeTo and self.nodeTo == other.nodeFrom:
        #         if abs(self.dist - other.dist) <= eqTol:
        #             return True
        return False

    # nonequivalence operator (!=) (required by Python 2)
    def __ne__(self, other):
        return not self == other

    def update(self, displace):
        """
        Moves position along edge. If car is already at destination node, fails.
        Takes displacement from previous position as argument. Preferably an integer
        Adds displacement to distance along edge in the appropriate direction
        Updates values: dist, xPos, yPos, coords, atNode
        """

        #check if car is on an edge, throw error otherwise
        if self.atNode:
            raise ValueError("A car at a node cannot move, it needs a new destination node")

        # Move car along edge in correct direction
        self.dist = self.dist + displace if self.direction else self.dist - displace
        # Recompute distance to next node, according to direction
        self.toNext = self.length - self.dist if self.direction else self.dist

        # Interpolate to recalculate other coordinates
        prog = (self.toNext if self.direction else self.dist) / float(self.length)
        self.xPos = int(prog * self.fromCoords[0] + (1-prog) * self.toCoords[0])
        self.yPos = int(prog * self.fromCoords[1] + (1-prog) * self.toCoords[1])
        self.coords = (self.xPos, self.yPos)

        # if the new position is at or past its destination node, then set atNode=True and location at new node
        if (self.dist <= 0 and not self.direction) or (self.dist >= self.length and self.direction):
            self.atNode = True
            self.coords = self.toCoords
            self.xPos, yPos = self.coords
    
    # generates a new Position object, using a given new node
    def changeNodes(self, newNode):
        """
        Give the car a new destination node. Fails if the car is not at its destination node.
        Calls the init method to recalculate all values.
        """
        if not self.atNode:
            raise ValueError("A car not at its destination node cannot change destination nodes")

        # if using weighted graph behavior, update numbers of cars along street
        if self.graph.weighted and self.nodeFrom != self.nodeTo:
            self.graph.edges[(self.nodeFrom, self.nodeTo)]["population"][self.direction] -= 1
        self.nodeFrom = self.nodeTo
        
        self.__init__(self.graph, self.nodeTo, newNode, eqTol=self.eqTol)

                

        



# Car class: designed to be independent of visualization system
# Depends on the above Position class
class Car:
    """
    Simulates a car moving along the graph.
    graph argument: a fully built graph. Will be stored by reference in the car's data
    randomBehavior: Defaults to True. If false, should have goal. Not yet implemented.
    startGiven: defaults to False. If false, randomly generates starting position
    accel: sets an overall acceleration, which serves as base for car velocity
    position: defaults to 0, not used. If startGiven True, should be an instance of Position class.
    """
    def __init__(self, graph, startGiven = False, randomBehavior = True, accel = 5, pos = 0):

        self.graph = graph
        self.randomBehavior = randomBehavior
        self.pos = pos
        self.accel = accel

        if not randomBehavior:
            # TODO
            pass
        else:
            startNode = np.random.randint(0, graph.size)
            self.pos = Position(self.graph, startNode, startNode)
            self.velocity = 0
    
    def updatePosition(self):
        if not self.randomBehavior:
            # TODO
            pass
        
        # if at node, randomly select another node from the nodes connected to the current node and set as destination
        # also get speed limit info from graph, store that; end the method here
        if self.pos.atNode:
            self.pos.changeNodes(np.random.choice(self.graph.nodes[self.pos.nodeTo]["connect"]))
            self.speedLimit = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["speed"]
            return
        
        # along edge: update velocity, then move that far along edge
        # TODO: checking cars' positions amongst themselves
        
        # distance required to decelerate completely
        decelerate = self.accel * sum(range(int(self.velocity/self.accel+1)))

        # if using weighted graph behavior, fetch weighted speed limit at each update
        if self.graph.weighted:
            self.speedLimit = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["weighted speed"][self.pos.direction]

        # if car has room to decelerate later, accelerate up to speed limit
        if self.pos.toNext > self.velocity + self.accel +  decelerate:
            if self.velocity <= self.speedLimit - self.accel:
                self.velocity += self.accel
            elif self.velocity < self.speedLimit:
                self.velocity = self.speedLimit

        # if car is approaching node, begin decelerating
        elif self.pos.toNext <= decelerate:
            self.velocity -= self.accel
        # if car is close, but going very slow, set velocity to 5
        if self.pos.toNext <= 10 and self.velocity < 5:
            self.velocity = 5
    
        # travel along edge
        self.pos.update(self.velocity)
        

    

