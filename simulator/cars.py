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
        # set boolean direction
        s.direction = (s.nodeTo > s.nodeFrom)
        s.atNode = False
        # for case where is at node already, compute some coordinates and return early
        if s.nodeFrom == s.nodeTo:
            s.atNode = True
            s.coords = s.graph.nodes[s.nodeTo]["coords"]
            s.xPos, s.yPos = s.coords
            if self.lanes:
                self.graph.nodes[self.nodeTo]["population"].append(self)
            return

        # store then check length of the edge
        # take given distance, and match it to system coordinates (from lower-index to higher-index node)
        # compute distance to destination, store it (toNext)
        s.length = graph.edges[(s.nodeFrom, s.nodeTo)]["length"]
        if s.direction:
            s.dist = dist
            s.toNext = s.length - dist
        else:
            s.dist = s.length - dist
            s.toNext = s.dist

        
        
        if dist > s.length+1:
            raise ValueError("The distance along an edge must be less than the edge's length.")
            
        
        # calculate coordinates of position if along an edge
        if not s.atNode:
            # get and store coordinates of nodeFrom, nodeTo
            s.fromCoords = s.graph.nodes[s.nodeFrom]["coords"]
            s.toCoords = s.graph.nodes[s.nodeTo]["coords"]
            s.calcCoords()


        # vars to update always: atNode, dist, xPos, yPos, coords
        # vars to update at node change: fromCoords, toCoords, length, direction

    # used to interpolate between positions of the two nodes and get coordinates; useful only for visualization
    def calcCoords(self):
        """
        Takes no arguments other than self, but depends internally on having coordinates
        for nodeFrom and nodeTo
        """
        prog = (self.toNext if self.direction else self.dist) / float(self.length)
        self.xPos = int(prog * self.fromCoords[0] + (1-prog) * self.toCoords[0])
        self.yPos = int(prog * self.fromCoords[1] + (1-prog) * self.toCoords[1])

        # if using lanes implemenation, adjust coords to move to side of line
        if self.lanes:
            xDiff = float(self.toCoords[0] - self.fromCoords[0])
            yDiff = float(self.toCoords[1] - self.fromCoords[1])
            # x += margin * sin(theta)
            self.xPos += int((self.carSize * 1.5) * (-yDiff/self.length))
            # y += margin * cos(theta)
            self.yPos += int((self.carSize * 1.5 ) * (xDiff/self.length))

        self.coords = (self.xPos, self.yPos)
# equivalence operator: created a bug with the population list's remove method.
# NOT CURRENTLY USED, used a different implementation in the end
    # equivalence operator (==)
    # def __eq__(self, other):
        
    #     # Two positions are considered equal if they have the same direction, travel nodes, and are within eqTol of each other
    #     if self.direction == other.direction:
    #         if self.nodeFrom == other.nodeFrom and self.nodeTo == other.nodeTo:
    #             if abs(self.dist - other.dist) <= self.eqTol:
    #                 return True
    #     # The following block would give equality of position if traveling in opposite directions at same place
    #     # else:
    #     #     if self.nodeFrom == other.nodeTo and self.nodeTo == other.nodeFrom:
    #     #         if abs(self.dist - other.dist) <= eqTol:
    #     #             return True
    #     return False

    # # nonequivalence operator (!=) (required by Python 2)
    # def __ne__(self, other):
    #     return not self == other

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
        
        # using lanes behavior, check position before moving
        if self.lanes:
            # check to see if is already at node
            if self.toNext <= displace:
                # check if node is not fully populated
                if self.graph.nodes[self.nodeTo]["capacity"] > len(self.graph.nodes[self.nodeTo]["population"]): # or self in self.graph.nodes[self.nodeTo]["population"]:
                    
                    # move to node: add self to population list
                    self.graph.nodes[self.nodeTo]["population"].append(self)
                    self.atNode = True
                    #compute coords
                    self.coords = self.toCoords
                    self.xPos, self.yPos = self.coords
                    # end the method here
                    return
                # do nothing if node is already occupied
                else:
                    return

        # Move car along edge in correct direction
        self.dist += displace if self.direction else -displace
        # Recompute distance to next node, according to direction
        self.toNext = self.length - self.dist if self.direction else self.dist

        # Recalculate other coordinates
        self.calcCoords()

        # if the new position is at or past its destination node, then set atNode=True and location at new node
        if not self.lanes and self.toNext <= 0:
            self.atNode = True
            self.graph.nodes[self.nodeTo]["population"].append(self)
            self.coords = self.toCoords
            self.xPos, self.yPos = self.coords
    
    # re-initalizes the Position object, using a given new node
    def changeNodes(self, newNode):
        """
        Give the car a new destination node. Fails if the car is not at its destination node.
        If the graph has weighted=True, moves weighting from old edge to new edge.
        If the graph has lanes=True, checks that there is space to move to the new edge before doing so
        Calls the init method to recalculate all values.
        """
        if not self.atNode:
            raise ValueError("A car not at its destination node cannot change destination nodes")

        if not (self.nodeTo, newNode) in self.graph.edges:
            raise ValueError("A car tried to move to a nonexistent edge.")
        
        # if using lanes, check if the next position along the desired edge is available
        if self.lanes:
            nextCar = (self.graph.edges[(self.nodeFrom, self.nodeTo)]["population"][-1])
            if type(nextCar) == Car:
                if nextCar.toNext >= nextCar.length - self.carSize:
                    # if there is a car within carSize of the node along the desired edge, do nothing
                    return

        # # if using weighted graph behavior, update numbers of cars along street
        # if self.graph.weighted and self.nodeFrom != self.nodeTo:
        #     self.graph.edges[(self.nodeFrom, self.nodeTo)]["population"][self.direction].remove(self)

            # if using lanes behavior, update number of cars at a given node
            self.graph.nodes[self.nodeTo]["population"].remove(self)

        # self.nodeFrom = self.nodeTo
        
        self.__init__(self.graph, self.nodeTo, newNode, carSize=self.eqTol)

                

        



# Car class: designed to be independent of visualization system
# Depends on the above Position class
class Car:
    """
    Simulates a car moving along the graph.
    graph argument: a fully built graph. Will be stored by reference in the car's data
    randomBehavior: Defaults to True. If false, should have goal. Not yet implemented.
    accel: sets an overall acceleration, which serves as base for car velocity
    nodeWait: sets the number of time steps it takes a car to get through a node
    pos: defaults to 0, not used. If is an instance of Position class and randomBehavior is False, should be a starting position.
    carSize: sets the size of car in pixel, used in lanes implementation and accessible for visualization
    Gets weighted or lanes property from graph.
    """
    def __init__(self, graph, randomBehavior = True, carSize = 5, accel = 5, nodeWait = 1, pos = 0):

        self.graph = graph
        self.randomBehavior = randomBehavior
        self.pos = pos
        self.accel = accel
        self.nodeWait = nodeWait
        self.currentWait = 0
        self.lanes = self.graph.lanes
        self.weighted = self.graph.weighted
        self.carSize = carSize

        # TUNING
        # Inital car position

        # Option 1: random point along a random edge
        # startNode = np.random.randint(0, graph.size)
        # startNodes = (startNode, np.random.choice(self.graph.nodes[startNode]["connect"]))
        # startDist = np.random.randint(0, self.graph.edges[startNodes]["length"])

        # Option 2: random dead-end node, at node
        startNode = np.random.choice(self.graph.endNodes)
        startNodes = (startNode, self.graph.nodes[startNode]["connect"][0])
        startDist = 0

        # /TUNING

        self.pos = Position(self.graph, startNodes[0], startNodes[1], startDist)

        # if following a planned path, set plan
        if not randomBehavior:
            # Still uses random goals, but follows a direct course to the goal
            # TUNING
            # self.nodeGoal = np.random.randint(0, graph.size)
            self.nodeGoal = np.random.choice(graph.endNodes)
            # /TUNING
            self.plan = self.routePlan(self.pos.nodeTo, self.nodeGoal)
            # Plan includes current nodeTo, so remove that from list
            self.plan.pop(0)

        # for purposes of edge population tracking, needs to already be at an edge and fully initialized at edge. Copied from below
        self.speedLimit = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["speed"]
        self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["population"][self.pos.direction].append(self)

        self.velocity = 0
    
    def updatePosition(self):
        """
        All-inclusive method to move the car by one time step.
        Takes no arguments; returns True if car has reached goal node, otherwise returns False.
        """

        # if at node, move to the next edge (or end movement and remove the car)
        if self.pos.atNode:

            if self.currentWait < self.nodeWait:
                self.currentWait += 1
                return

            # remove self from old population list, if using weights or lanes
            if self.weighted or self.lanes:
                self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["population"][self.pos.direction].remove(self)

            # Select the next node, either randomly or from a goal list
            if self.randomBehavior:
                self.pos.changeNodes(np.random.choice(self.graph.nodes[self.pos.nodeTo]["connect"]))
            else:
                if self.pos.nodeTo == self.nodeGoal or len(self.plan) == 0:
# lines to execute if car has reached goal node
                    self.graph.nodes[self.pos.nodeTo]["population"].remove(self.pos)
                    del self
                    return True
                else:
                    self.pos.changeNodes(self.plan.pop(0))

            # add self to new population list, if using weights or lanes
            if self.weighted or self.lanes:
                self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["population"][self.pos.direction].append(self)

            self.speedLimit = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["speed"]
            return
        
        # along edge: update velocity, then move that far along edge
        # TODO: checking cars' positions amongst themselves
        

        # To update velocity, there are two methods: with and without lanes implementation
        # Acceleration handling: lanes implementation, which avoids collision
        if self.lanes:        
            # Get list of other cars on edge
            otherCars = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["population"][self.pos.direction]

            # Find the nearest car ahead, if there is one
            # Idea: the list implementation means that this arithemetic could be avoided (just find the index on the list, get the lower index) TODO

            # # Arithmetic Implementation
            # carAhead = False
            # for car in otherCars:
            #     # if no cars found ahead yet, but car is ahead:
            #     if carAhead == False and car.pos.toNext <= self.pos.toNext and not car is self:
            #         # call it the next car, and note that there is one
            #         nextCar = car
            #         carAhead = True
            #     # if the car being examined is closer than the current nextCar, replace the current with the new
            #     elif self.pos.toNext > car.pos.toNext and car.pos.toNext > nextCar.pos.toNext and not car is self:
            #         nextCar = car

            # List Implementation
            ind = otherCars.index(self) 
            if ind == 0:
                carAhead = False
            else:
                carAhead = True
                nextCar = otherCars[ind - 1]
                
            
            # if a car is found ahead on the road, compute an appropriate velocity adjustment
            if carAhead:
                veloDiff = nextCar.velocity - self.velocity
                distDiff = self.pos.toNext - nextCar.pos.toNext     

                decelDist = 2 * self.carSize + self.accel * sum(range(int(nextCar.velocity/self.accel), int(self.velocity/self.accel)+1)) 

                # acceleration behavior depends on veloDiff, distDiff, and decelDist. 

                # car ahead is actually at same position: fudge the distance a little so they spread apart
                if distDiff == 0:
                    self.velocity += -1 if self.velocity > 0 else 1
                # car ahead is going faster, is not on top: accelerate
                elif veloDiff > 0 and distDiff > self.carSize:
                    self.velocity += self.accel if veloDiff >= self.accel else veloDiff
                # car ahead is slower and close: decelerate
                elif veloDiff < 0 and distDiff <= decelDist:
                    self.velocity -= self.accel if self.velocity >= self.accel else self.velocity
                # car ahead is slower or same speed but far away: ignore car ahead (triggers next block below)
                elif veloDiff < 0 and distDiff > decelDist:
                    carAhead = False
                # car ahead is same speed and close: maintain
                elif veloDiff == 0 and distDiff <= decelDist:
                    pass
                # car ahead is same speed and far: ignore car ahead
                elif veloDiff == 0 and distDiff > decelDist: 
                    carAhead = False

                # car ahead is going same speed: do nothing
                

                
                

        # Acceleration handling: calculate to next node (either no lanes, or no cars ahead)
        if not self.lanes or not carAhead:

            # distance required to decelerate completely
            decelDist = self.accel * sum(range(int(self.velocity/self.accel)+1))
    
            # if using weighted graph behavior, fetch weighted speed limit at each update
            if self.graph.weighted:
                self.speedLimit = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["weighted speed"][self.pos.direction]
    
            # if car has room to decelerate later, accelerate up to speed limit
            if self.pos.toNext > self.velocity + self.accel +  decelDist:
                if self.velocity < self.speedLimit:
                    speedUnder = self.speedLimit-self.velocity
                    self.velocity += self.accel if speedUnder >= self.accel else speedUnder
    
            # if car is approaching node, begin decelerating
            elif self.pos.toNext <= decelDist:
                self.velocity -= self.accel
            # if car is close, but going very slow, set velocity to self.accel baseline
            if self.pos.toNext <= self.carSize and self.velocity < self.accel:
                self.velocity = self.accel

        # require self.velocity to be nonnegative and less than speed limit
        if self.velocity < 0:
            self.velocity = 0
        elif self.velocity >self.speedLimit:
            self.velocity = self.speedLimit
            # for debug purposes
            print("A car tried to go faster than the speed limit.")
            print("Deets: veloDiff =", veloDiff, "distDiff =", distDiff, "decelDist =", decelDist)
        # travel along edge
        self.pos.update(self.velocity)
        

    def routePlan(self, startNode, endNode):
        
        """
        A* search for best path from startNode to endNode.
        Based on: https://github.com/laurentluce/python-algorithms/blob/master/algorithms/a_star_path_finding.py

        Returns list of nodes, which form a route from startNode to endNode.
        If there is no possible route, returns an empty list and prints a message saying so.
        """
        def h(node):
            """Estimates with distance, minimum speed limit
            Update this later probably?
            """
            # TODO make this more relevant?
            xDiff = self.graph.nodes[endNode]["coords"][0] - self.graph.nodes[node]["coords"][0]
            yDiff = self.graph.nodes[endNode]["coords"][1] - self.graph.nodes[node]["coords"][1]
# Magic number warning
            return np.sqrt(xDiff*xDiff + yDiff*yDiff) / 30

        def update(next, current):
            node_g[next] = node_g[current] + self.graph.heuristicWeight(current, next)
            node_h[next] = h(next)
            node_parent[next] = current
            node_f[next] = node_g[next] + node_h[next]

        if startNode == endNode:
            return [startNode]
        
        size = self.graph.size
        node_g = [0 for i in range(size)]
        node_f = [0 for i in range(size)]
        node_h = [0 for i in range(size)]
        node_parent = ["" for i in range(size)]

        closed = []
        open = [startNode]

        while len(open):
            #pop index of next node from list
            current = open.pop(0)
            closed.append(current)
            # if at goal, return final path
            if current == endNode:
                node = endNode
                path = [node]
                while node_parent[node] != startNode:
                    node = node_parent[node]
                    path.append(node)
                path.append(startNode)
                path.reverse()
                return path
            # iterate through connected nodes
            adjNodes = self.graph.nodes[current]["connect"]
            for next in adjNodes:
                if next not in closed:
                    if next in open:
                        if node_g[next] > node_g[current] + self.graph.heuristicWeight(current, next):
                            update(next, current)
                #Probable bug right here: does it work if the node is unexplored?
                    else:
                        update(next, current)
                        open.append(next)
        
        # If the route planning fails, warn the user and return an empty list.
        print("Route planning system found no possible route for a car.")
        print("Attempted route from node", startNode, "to node", endNode)
        return []
        

            

    

