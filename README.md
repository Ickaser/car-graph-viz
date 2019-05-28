# car-graph-visual

Built by Isaac Wheeler on internship at CNR-IIA, Montelibretti campus. Begun 23/5/2019.  

Goal: a toy problem to which AI methods can be applied, to showcase the possibility for improvement in real-time traffic 
flow. The program will take an XML file as input, which will allow real map data to be used as a graph structure.  

At present: the program generates a graph with semirandom coordinates and structure, and dots representing cars move 
along the edges of the graph, randomly picking a new direction of travel each time they reach a node.


To simulate traffic slowdown, there are two main ideas at the moment:
1. Add a system of capacities and weights to the graph which lowers the effective speed limit along an edge as the number 
of cars on that edge increases. This method is loosely implemented, but needs significant tuning.
2. Disallow car overlay and slow down cars so that they do not collide visually; separate them on opposite sides of the 
edge. This is currently not implemented.

1. graphGen.py:
Implements a Graph class. 
The Graph is currently initialized with a semirandom structure. Eventually, it will take an XML input file, from which it
will construct the graph structure.  
The system of weights and capacities is largely implemented in this class, with some interfacing with the Position class.
The structure is as follows:
* graph.nodes: A list of dictionaries. Effectively, access a point by accessing the list at the point's index; access that point's attributes with string keys, notably:
    * "coords" for XY coordinates 
    * "connect" for a list of connected points.
* graph.edges: A dictionary of dictionaries. 
    * Access an edge with a tuple of the two points connected (in either order), 
    * Access an edge's attributes with string key:
        * "length" 
        * "speed" for speed limit
        * "capacity" for capacity factor (used to model high-density traffic)
        * "weighted speed" for speed limit adjusted for traffic (distinct for each direction of travel)
        * "population" for the number of cars currently on the edge (distinct for each direction of travel). This property is not accessed internally.

        
  
2. cars.py:
Implements a Position class and a Car class, which combined handle movement of cars.