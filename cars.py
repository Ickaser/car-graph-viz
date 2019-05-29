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
    

    def __init__(self, graph, nodeFrom, nodeTo, dist = 0, carSize = 5):
        """
        Takes graph, two integers indicating node indices and a distance along edge
        Graph is stored (by reference).
        If both indices are the same, places car at node and sets atNode = True.
        If indices are different, places car along edge and sets atNode = False.
        Third argument is distance along the edge from the departure node. Defaults to 0 (placed at node)
        carSize: sets tolerance for equals operator and for car following
        """
        s = self
        s.graph = graph
        s.eqTol = carSize
        s.carSize = carSize
        s.lanes = graph.lanes
        

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
            prog = (self.toNext if self.direction else self.dist) / float(self.length)
            s.xPos = int(prog * s.fromCoords[0] + (1-prog) * s.toCoords[0])
            s.yPos = int(prog * s.fromCoords[1] + (1-prog) * s.toCoords[1])
            s.coords = (s.xPos, s.yPos)

        # vars to update always: atNode, dist, xPos, yPos, coords
        # vars to update at node change: fromCoords, toCoords, length, direction


# equivalence operator: created a bug with the population list's remove method. Uncomment only
# if you are ready to implement a different list removal method
    # equivalence operator (==)
    def __eq__(self, other):
        
        # Two positions are considered equal if they have the same direction, travel nodes, and are within eqTol of each other
        if self.direction == other.direction:
            if self.nodeFrom == other.nodeFrom and self.nodeTo == other.nodeTo:
                if abs(self.dist - other.dist) <= self.eqTol:
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
        If the graph has weighted=True, moves weighting from old edge to new edge.
        Calls the init method to recalculate all values.
        """
        if not self.atNode:
            raise ValueError("A car not at its destination node cannot change destination nodes")

        # # if using weighted graph behavior, update numbers of cars along street
        # if self.graph.weighted and self.nodeFrom != self.nodeTo:
        #     self.graph.edges[(self.nodeFrom, self.nodeTo)]["population"][self.direction].remove(self)
        self.nodeFrom = self.nodeTo
        
        self.__init__(self.graph, self.nodeTo, newNode, carSize=self.eqTol)

                

        



# Car class: designed to be independent of visualization system
# Depends on the above Position class
class Car:
    """
    Simulates a car moving along the graph.
    graph argument: a fully built graph. Will be stored by reference in the car's data
    randomBehavior: Defaults to True. If false, should have goal. Not yet implemented.
    accel: sets an overall acceleration, which serves as base for car velocity
    pos: defaults to 0, not used. If is an instance of Position class and randomBehavior is False, should be a starting position.
    Gets lanes property from graph's lanes property.
    """
    def __init__(self, graph, randomBehavior = True, carSize = 5, accel = 5, pos = 0):

        self.graph = graph
        self.randomBehavior = randomBehavior
        self.pos = pos
        self.accel = accel
        self.lanes = self.graph.lanes
        self.weighted = self.graph.weighted
        self.carSize = carSize

        if not randomBehavior:
            # TODO
            pass
        else:
            startNode = np.random.randint(0, graph.size)
            self.pos = Position(self.graph, startNode, startNode)

            # for purposes of population, needs to already be at an edge and fully initialized at edge. Copied from below
            self.pos.changeNodes(np.random.choice(self.graph.nodes[self.pos.nodeTo]["connect"]))
            self.speedLimit = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["speed"]
            self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["population"][self.pos.direction].append(self)

            self.velocity = 0
        
        
    
    def updatePosition(self):
        if not self.randomBehavior:
            # TODO
            pass
        
        # if at node, randomly select another node from the nodes connected to the current node and set as destination
        # also get speed limit info from graph, store that; end the method here
        if self.pos.atNode:
            # remove self from old population list, if using weights or lanes
            if self.weighted or self.lanes:
                self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["population"][self.pos.direction].remove(self)

            self.pos.changeNodes(np.random.choice(self.graph.nodes[self.pos.nodeTo]["connect"]))

            # add self to new population list, if using weights or lanes
            if self.weighted or self.lanes:
                self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["population"][self.pos.direction].append(self)

            self.speedLimit = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["speed"]
            return
        
        # along edge: update velocity, then move that far along edge
        # TODO: checking cars' positions amongst themselves
        

        # To update velocity, there are two methods: with and without lanes implementation
        # Acceleration handling: with collision avoidance
        if self.lanes:        
            # Get list of other cars on edge
            otherCars = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["population"][self.pos.direction]

            # Find the nearest car ahead, if there is one
            # Idea: the list implementation means that this arithemetic could be avoided (just find the index on the list, get the lower index) TODO
            carAhead = False
            for car in otherCars:
                # if no cars found ahead yet, but car is ahead:
                if carAhead == False and car.pos.toNext < self.pos.toNext:
                    # call it the next car, and note that there is one
                    nextCar = car
                    carAhead = True
                # if the car being examined is closer than the current nextCar, replace the current with the new
                elif self.pos.toNext > car.pos.toNext and car.pos.toNext > nextCar.pos.toNext:
                    nextCar = car
            
            # if a car is found ahead on the road, compute an appropriate velocity adjustment
            if carAhead:
                veloDiff = nextCar.velocity - self.velocity
                distDiff = self.pos.toNext - nextCar.pos.toNext - self.carSize     

                decelDist = self.accel * sum(range(int(nextCar.velocity/self.accel), int(self.velocity/self.accel+1))) # removed +1 on second int
                
                if veloDiff > self.accel:
                    self.velocity += self.accel
                elif veloDiff < self.accel and veloDiff > 0:
                    self.velocity += veloDiff
                elif veloDiff < 0 and distDiff <= decelDist:
                    self.velocity -= self.accel if self.velocity >= self.accel else self.velocity
                    
                elif veloDiff < 0 and distDiff > decelDist:
                    self.velocity += self.accel

                
                

        # Acceleration handling: calculate to next node (either no lanes, or no cars ahead)
        if not self.lanes or not carAhead:

            # distance required to decelerate completely
            decelDist = self.accel * sum(range(int(self.velocity/self.accel+1)))
    
            # if using weighted graph behavior, fetch weighted speed limit at each update
            if self.graph.weighted:
                self.speedLimit = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["weighted speed"][self.pos.direction]
    
            # if car has room to decelerate later, accelerate up to speed limit
            if self.pos.toNext > self.velocity + self.accel +  decelDist:
                if self.velocity <= self.speedLimit - self.accel:
                    self.velocity += self.accel
                elif self.velocity < self.speedLimit:
                    self.velocity = self.speedLimit
    
            # if car is approaching node, begin decelerating
            elif self.pos.toNext <= decelDist:
                self.velocity -= self.accel
            # if car is close, but going very slow, set velocity to 5
            if self.pos.toNext <= 10 and self.velocity < 5:
                self.velocity = 5
    
        # travel along edge
        self.pos.update(self.velocity)
        

    

