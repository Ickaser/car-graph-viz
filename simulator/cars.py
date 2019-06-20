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
            # check to see if is already within reach of node
            if self.toNext <= displace:
                # check if node is not fully populated
                if self.graph.nodes[self.nodeTo]["capacity"] > len(self.graph.nodes[self.nodeTo]["population"]): # or self in self.graph.nodes[self.nodeTo]["population"]:
                    
                    # move to node: add self to population list
                    self.graph.nodes[self.nodeTo]["population"].append(self)
                    self.atNode = True
                    #compute coords
                    self.toNext = 0
                    self.dist += displace if self.direction else -displace
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

        if self.toNext > self.carSize:
            print("A car skipped an edge, somehow.")
        if not (self.nodeTo, newNode) in self.graph.edges:
            raise ValueError("A car tried to move to a nonexistent edge.")
        

        # # if using weighted graph behavior, update numbers of cars along street
        # if self.graph.weighted and self.nodeFrom != self.nodeTo:
        #     self.graph.edges[(self.nodeFrom, self.nodeTo)]["population"][self.direction].remove(self)

            # if successfully moves away, remove self from population of node
        self.graph.nodes[self.nodeTo]["population"].remove(self)

        # self.nodeFrom = self.nodeTo
        
        self.__init__(self.graph, self.nodeTo, newNode, carSize=self.eqTol)

                

        



# Car class: designed to be independent of visualization system
# Depends on the above Position class
class Car:
    """
    Simulates a car moving along the graph.  
    graph argument: a fully built graph. Will be stored by reference in the car's data. Car gets weighted/lanes properties from graph.
    carBehavior argument: a dict containing the following variables.  \n\n
    randomBehavior: Defaults to True. If false, gets a random goal and creates a plan at init.  
    accel: sets an overall acceleration, which serves as base for car velocity.  
    nodeWait: sets the number of time steps it takes a car to get through a node  
    pos: defaults to 0, not used. If is an instance of Position class and randomBehavior is False, should be a starting position.  
    carSize: sets the size of car in pixel, used in lanes implementation and accessible for visualization  
    """
    def __init__(self, graph, carBehavior = {}): # randomBehavior = True, carSize = 5, accel = 5, nodeWait = 1, pos = 0):

        self.graph = graph
        self.lanes = self.graph.lanes
        self.weighted = self.graph.weighted

        self.randomBehavior = carBehavior.get("randomBehavior", True)
        self.pos = carBehavior.get("pos", 0)
        self.accel = carBehavior.get("accel", 5)
        self.nodeWait = carBehavior.get("nodeWait", 1)
        self.carSize = carBehavior.get("carSize", 5) 

        self.currentWait = 0

        self.lifetime = 0
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
        if not self.randomBehavior:
            # Still uses random goals, but follows a direct course to the goal
            # TUNING
            # self.nodeGoal = np.random.randint(0, graph.size)
            self.nodeGoal = np.random.choice(graph.endNodes)
            # /TUNING
            self.plan = self.routePlan(self.pos.nodeTo, self.nodeGoal)
            # Plan includes current nodeTo, so remove that from list
            self.plan.pop(0)
            
        self.history = []
        self.history += startNodes

        # for purposes of edge population tracking, needs to already be at an edge and fully initialized at edge. Copied from below
        self.speedLimit = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["speed"]
        self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["population"][self.pos.direction].append(self)

        self.velocity = 0
    
    def updatePosition(self):
        """
        All-inclusive method to move the car by one time step. \n
        Takes no arguments; returns True if car has reached goal node, otherwise returns False. \n
        If the car is at a node, calls self.nodeBehavior; if the car is at node, accelerates and moves
        """
        # for data generation purposes, increment lifetime
        self.lifetime += 1

        # if at node, move to the next edge (or end movement and remove the car)
        if self.pos.atNode:
            return self.nodeBehavior()

        # Acceleration handling: lanes implementation, which avoids collision
        if self.lanes:        
            nextCar = self.getNextCarEdge()
            if nextCar:
                carAhead = True
            else:
                carAhead = False
            # if a car is found ahead on the road, compute an appropriate velocity adjustment
            if carAhead:
                self.velocity += self.accelWithFollowing(nextCar)

        # Acceleration handling: calculate to next node (either without lanes, or no cars ahead)
        if not self.lanes or not carAhead:
            self.velocity += self.accelWithoutFollowing()

        # require self.velocity to be nonnegative and less than speed limit
        if self.velocity < 0:
            self.velocity = 0
        elif self.velocity > self.speedLimit:
            self.velocity = self.speedLimit
            # for debug purposes
            print("A car tried to go faster than the speed limit.")
        # travel along edge
        self.pos.update(self.velocity)

    def accelWithFollowing(self, nextCar):
        """
        Takes self and a Car object as argument; the Car object should be on the same edge and ahead of self.
        Returns the appropriate acceleration (change in velocity, either + or -).
        """
        # Compute the values on which the behavior is based
        veloDiff = nextCar.velocity - self.velocity
        distDiff = self.pos.toNext - nextCar.pos.toNext     
        decelDist = 2 * self.carSize + self.accel * sum(range(int(nextCar.velocity/self.accel)-1, int(self.velocity/self.accel)+1)) 

        # car ahead is actually at same position: fudge the distance a little so they spread apart
        if distDiff == 0:
            return -1 if self.velocity > 0 else 1
        # car ahead is going faster, is not overlapping: accelerate
        elif veloDiff > 0 and distDiff > self.carSize:
            return self.accel if veloDiff >= self.accel else veloDiff
        # car ahead is slower and close: decelerate
        elif veloDiff < 0 and distDiff <= decelDist + self.velocity:
            return -self.accel if self.velocity >= self.accel else -self.velocity
        # car ahead is slower or same speed but far away: ignore car ahead (call other function)
        elif veloDiff < 0 and distDiff > decelDist:
            return self.accelWithoutFollowing()
        # car ahead is same speed and close: maintain speed
        elif veloDiff == 0 and distDiff <= decelDist:
            return 0
        # car ahead is same speed and far: ignore car ahead (call other function)
        elif veloDiff == 0 and distDiff > decelDist: 
            return self.accelWithoutFollowing()

        # if none of the above cases are true, maintain speed
        return 0
                
    def accelWithoutFollowing(self):
        """
        Takes only self as argument.
        Returns the acceleration, such that the car slows down before it reaches the next destination.
        """

        # distance required to decelerate completely
        decelDist = self.accel * sum(range(int(self.velocity/self.accel)+1)) 

        # if using weighted graph behavior, fetch weighted speed limit at each update
        if self.graph.weighted:
            self.speedLimit = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["weighted speed"][self.pos.direction]

        # if car has room to decelerate later before reaching node, accelerate up to speed limit
        if self.pos.toNext > self.velocity + self.accel +  decelDist:
            if self.velocity < self.speedLimit:
                speedUnder = self.speedLimit-self.velocity
                return self.accel if speedUnder >= self.accel else speedUnder

        # if car is close to node, but going very slow, increase velocity slightly to ensure the car arrives
        if self.pos.toNext <= self.carSize and self.velocity < self.accel:
            return self.accel - self.velocity

        # if car is approaching node, begin decelerating
        elif self.pos.toNext <= decelDist:
            return -self.accel

        # if none of the other cases are true, maintain velocity
        return 0

    def getNextCarEdge(self):
        """
        Takes no arguments. If finds a car ahead of self on the same edge, returns that car; otherwise, returns False.
        """
        # Get list of all cars on same edge
        edgeCars = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["population"][self.pos.direction]

        # Find the nearest car ahead, if there is one

        # # Arithmetic implementation: seems to work worse than the list implementation below
        # carAhead = False
        # for car in edgeCars:
        #     # if no cars found ahead yet, but car is ahead:
        #     if carAhead == False and car.pos.toNext <= self.pos.toNext and not car is self:
        #         # call it the next car, and note that there is one
        #         nextCar = car
        #         carAhead = True
        #     # if the car being examined is closer than the current nextCar, replace the current with the new
        #     elif self.pos.toNext > car.pos.toNext and car.pos.toNext > nextCar.pos.toNext and not car is self:
        #         nextCar = car

        # List Implementation
        ind = edgeCars.index(self) 
        if ind == 0:
            return False
        else:
            nextCar = edgeCars[ind - 1]
            return nextCar


    def nodeBehavior(self):
        """
        Takes no arguments. Implements car behavior when it has reached a node. \n
        Returns True if the car has reached its goal node.
        """

        # check if car has already waited long enough at node; if not, increment wait time
        if self.currentWait < self.nodeWait:
            self.currentWait += 1
            return

        # decide what the next node should be
        if self.randomBehavior:
            newNode = np.random.choice(self.graph.nodes[self.pos.nodeTo]["connect"])
        else:
            if self.pos.nodeTo == self.nodeGoal or len(self.plan) == 0:
                self.graph.nodes[self.pos.nodeTo]["population"].remove(self.pos)
                self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["population"][self.pos.direction].remove(self)

                # execute any other code dealing with car reaching goal
                # TODO
                travelDist = sum( [ self.graph.edges[(self.history[i], self.history[i+1])]["length"] for i in range(len(self.history)-1) ] ) 
                outputStr = "Lifetime (time steps): {0} \t Distance traveled: {1} \t Average speed: {2:.2f} \t Overall route: {3}".format(self.lifetime, travelDist, travelDist/float(self.lifetime), self.history)
                self.graph.history.append(outputStr)

                # delete the car, return true
                del self
                return True
            else:
                newNode = self.plan[0]

        # if using lanes, check if the next position along the desired edge is available
        if self.lanes:
            population = self.graph.edges[(self.pos.nodeTo, newNode)]["population"][0 if self.pos.nodeTo > newNode else 1]
            if len(population) > 0:
                nextCar = population[-1]
                if nextCar.pos.toNext >= nextCar.pos.length - self.carSize:
                    # if there is a car within carSize of the node along the desired edge, do nothing and end function
                    return 

        # remove self from old population list, if using weights or lanes
        if self.weighted or self.lanes:
            self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["population"][self.pos.direction].remove(self)


        # move to next edge
        self.pos.changeNodes(newNode)
                    
        # If successfully moves, execute the rest of this function

        # add newNode to car's route history
        self.history.append(newNode)

        # remove newNode from plan
        if not self.randomBehavior:
            self.plan.pop(0)

        # add self to new population list, if using weights or lanes
        if self.weighted or self.lanes:
            self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["population"][self.pos.direction].append(self)

        self.currentWait = 0
        self.speedLimit = self.graph.edges[(self.pos.nodeFrom, self.pos.nodeTo)]["speed"]
        return


    def routePlan(self, startNode, endNode):
        # Based on: https://github.com/laurentluce/python-algorithms/blob/master/algorithms/a_star_path_finding.py
        """
        A* search for best path from startNode to endNode.
        Returns list of nodes, which form a route from startNode to endNode.
        If there is no possible route, returns an empty list and prints a message saying so.
        """
        def h(node):
            """
            Estimates with distance, minimum speed limit
            Update this later probably?
            """
            # TODO make this more relevant?
            xDiff = self.graph.nodes[endNode]["coords"][0] - self.graph.nodes[node]["coords"][0]
            yDiff = self.graph.nodes[endNode]["coords"][1] - self.graph.nodes[node]["coords"][1]
            return np.sqrt(xDiff*xDiff + yDiff*yDiff)

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
        

            

    

