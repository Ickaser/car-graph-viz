# Built by Isaac Wheeler, interning at CNR-IIA, beginning on 23/5/2019


import numpy as np

class Graph:

    def __init__(self, nodes, xml = False):
        # create a list, with an empty dict for each node
        if xml:
            #do something else to import information from xml
            pass
        self.size = nodes
        self.nodes = [{"coords":(), "connect":[]} for i in range(self.size)]
        # for the edges, create a dict of dicts
        self.edges = {}


    def connect(self, point1, point2):
        """
        Takes two integers, which are indexes for points on the graph
        Creates a dict for the edge and gives it a length of 0.
        """
        # tell each point that there is an edge
        self.nodes[point1]["connect"].append(point2)
        self.nodes[point2]["connect"].append(point1)

        #create main edge data structure
        #sort two point indices, check if there is already an edge between them, use tuple of indices as key for dict
        if point1 < point2:
            nodeNums = (point1, point2)
        elif point2 < point1:
            nodeNums = (point2, point1)
        else:
            print("Cannot connect a node to itself.")
            pass

        if nodeNums in self.edges:
            print("Edge already exists.")
            pass
        else: 
            self.edges[nodeNums] = {"length":0}

        
        # edge structure: dict of dicts, first is keyed by connected nodes and second is keyed by attributes of edge

    def makeCoords8nodes(self, pixels):
        """
        Takes a tuple of size 2, indicating size of screen to use in the end.
        Randomly assigns coordinates to 8 points
        """

        xdim, ydim = pixels

        # at the moment, just assigns positions randomly
        if self.size / 8.0 != 1:
            pass
            # do something different
        else:
            # randomly generate coordinates for the points
            xList = list(np.random.randint(0, xdim/2, 4)) + list(np.random.randint(xdim/2, xdim, 4))
            yList = list(np.random.randint(0, ydim/2, 2)) + list(np.random.randint(ydim/2, ydim, 4)) + list(np.random.randint(0, ydim/2, 2)) 
            
            # assign coordinates
            for n in range(self.size):
                self.nodes[n]["coords"] = (xList[n], yList[n])
            
            # create edges, with some order to hopefully avoid overlaps

            def coinFlip():
                r = np.random.randint(0,2)
                if r == 0:
                    return False
                if r == 1:
                    return True

            for i in range(4):
                # indexes for the two points in a certain quadrant
                p1 = i * 2
                p2 = p1 + 1

                # connect the two points
                self.connect(p1, p2)

                #connect one of the points in each quadrant with a point in another quadrant
                if i == 0:
                    if coinFlip():
                        self.connect(p1, 6) if coinFlip() else self.connect(p1, 7)
                    else:
                        self.connect(p2, 6) if coinFlip() else self.connect(p2, 7)
                else:
                    if coinFlip():
                        self.connect(p1, p1 - 2) if coinFlip() else self.connect(p1, p1 - 1)
                    else:
                        self.connect(p2, p1 - 2) if coinFlip() else self.connect(p2, p1 - 1)
                        
    def calcEdgeLengths(self):
        """
        Assumes all nodes have coordinates already.
        For all existing edges, computes edge length from node coordinates
        """
        for i in self.edges.keys():
            p1, p2 = i
            x1, y1 = self.nodes[p1]["coords"]
            x2, y2 = self.nodes[p2]["coords"]
            self.edges[i]["length"] = int(np.sqrt( (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2) ))

    def genEdgeSpeeds(self):
        """
        Randomly assigns speed limits for all edges. Ints between 30 and 70.        
        """
        for i in self.edges.keys():
            self.edges[i]["speed"] = np.random.randint(30, 71)

        




            

            



