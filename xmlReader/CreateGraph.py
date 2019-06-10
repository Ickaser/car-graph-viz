#!/usr/bin/env python
"""
   Description: Classes for map generation as an undirected graph
   Author: Paolo Fazzini
   Email: paolo.fazzini@iia.cnr.it
   Company: CNR-IIA
   Copyright: 2019
   Version: 0.1
"""

import numpy as np
import itertools
class Node:
    newid = next(itertools.count())
    def __init__(self, x = 0, y = 0, node_name = ''):
        self.id = Node.newid()
        if node_name == "":
            self.name = str(self.id)
        else:
            self.name = node_name
        self.streets = []
        self.highlighted = False
        self.x = x
        self.y = y
 
    def __repr__(self):
        return str(self.streets)


class Parking:
    def __init__(self, parking_id):
        self.id = parking_id
        self.street_perc = [] 
        self.right_side = True


class Street:
    newid = next(itertools.count())
    def __init__(self, street_name = "No Name", nodes = None):
        if nodes != None:
            self.id = Street.newid()
            self.nodes = nodes.copy()
            self.node_distance = self._compute_crow_distance()
        else:
            self.id = 0
            self.nodes = []
            self.node_distance = 0

        self.name = street_name
        self.xs = []       
        self.ys = []   
        self.speed_limit = 50
        self.parkings =  []  
        self.length = 0#self._compute_length()
        self.allowed_directions = 0 #three state flag: 0 -> bidirectional; 1 -> from node 1 to node 2; 2 -> from node 2 to node 1

    def _pairwise(self, iterable):
        "s -> (s0, s1), (s2, s3), (s4, s5), ..."
        a = iter(iterable)
        return zip(a, a)    

    def _compute_crow_distance(self):
        return np.sqrt((self.nodes[0].x - self.nodes[1].x)**2 + (self.nodes[0].y - self.nodes[1].y)**2)

    #def _compute_length(self):
        #todo: approx to polyline?    
        #        self.length = 0
        #        for x1, x2 in self._pairwise(self.xs):
        #            self.length = self.length + np.sqrt((self.nodes[0].x - self.nodes[1].x)**2 + (self.nodes[0].y - self.nodes[1].y)**2)


    def __repr__(self):
        return str(self.name)



