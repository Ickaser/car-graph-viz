# car-graph-visual

Built by Isaac Wheeler on internship at CNR-IIA, Montelibretti campus. Begun 23/5/2019.  


1. graphGen.py:
Implements a Graph class. 
The Graph is currently initialized with a semirandom structure. Eventually, it will take an XML input file, from which it
will construct the graph structure.
The structure is as follows:
* graph.nodes: A list of dictionaries. Effectively, access a point by accessing the list at the point's index; access that point's attributes with string keys, notably:
    * "coords" for XY coordinates 
    * "connect" for a list of connected points.
* graph.edges: A dictionary of dictionaries. 
    * Access an edge with a tuple of the two points connected (in either order), 
    * Access an edge's attributes with string key:
        * "length" 
        * "speed" for speed limit
        * "weighted speed" for speed limit adjusted for traffic
        
  
1. cars.py:
Implements a Position class and a Car class, which combined handle m