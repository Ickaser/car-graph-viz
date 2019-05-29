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
* `graph.nodes`: A list of dictionaries. Effectively, access a point by accessing the list at the point's index; access that point's attributes with string keys, notably:
    * `"coords"` for XY coordinates 
    * `"connect"` for a list of connected points.
* `graph.edges`: A dictionary of dictionaries. 
    * Access an edge with a tuple of the two points connected (in either order), 
    * Access an edge's attributes with string key:
        * `"length"` 
        * `"speed"` for speed limit
        * `"capacity"` for capacity factor (used to model high-density traffic)
        * `"weighted speed"` for speed limit adjusted for traffic (distinct for each direction of travel)
        * `"population"` for the number of cars currently on the edge (distinct for each direction of travel). This
        property is not accessed internally.
* `graph.updateWeights()`: a function to call when using the weighted slowdown system. Using the `"population"` and 
`"capacity"` values for each edge, adjusts the `"weighted speed"` value. The `Position.update(displace)` function depends on that weighted speed if the weighted functionality is set to True.

        
  
2. cars.py:
Implements a Position class and a Car class, which combined handle movement of cars.  

The Position class depends heavily on the Graph class, as described above. To simplify the interface with pygame, all values are rounded off and stored as ints.
* Properties of an instance of Position (called pos for convenience):
    * `pos.xPos`, `pos.yPos`: x and y coordinates of position
    * `pos.coords`: A tuple of the x and y coordinates. 
    * `pos.nodeFrom`, `pos.nodeTo`: The indices of the nodes on the graph which define the edge on which a `Position` is found. The distinction between `nodeFrom` and `nodeTo` matters; it determines the direction of movement at a given position.
    * `pos.fromCoords`, `pos.toCoords`: Tuples indicating the XY coordinates of `nodeFrom` and `nodeTo`, respectively.
    * `pos.direction`: A Boolean, used to identify the direction of travel along the current edge. `True` if `nodeFrom < nodeTo` (traveling from lower to higher node), False otherwise.
    * `pos.dist`: The Euclidean distance **from the lower-index node** of the current edge, along the currently occupied edge. This property is **independent of the direction** of travel.
    * `pos.length`: The length of the edge, as taken from the graph information.
    * `pos.toNext`: The Euclidean distance along the current edge to `nodeTo`. This property is **dependent on the direction** of travel.
    * `pos.atNode`: a Boolean indicating whether the position is equal to the position of `nodeTo`. If `nodeFrom` has a lower index than `nodeTo`, this means `pos.dist` == `pos.length`; if `nodeFrom` has the higher index, `pos.dist` == 0. In both cases, `pos.toNext` == 0.
    * `pos.eqTol`: Set at initialization of instance, defaults to 10. Sets a margin within which two positions are considered to be equal by the `==` operator
* Functions and methods of a Position instance:
    * `Position(graph, nodeFrom, nodeTo, dist = 0, eqTol = 10)` : takes the graph, stores it internally (by reference, of course); takes `nodeFrom` and `nodeTo`, which sets the edge on which the car begins; dist is the distance *from `nodeFrom`*, which allows a position to be initialized on the edge instead of at the node.
    * `pos.update(displace)`: Adds `displace` to the distance along the edge according to `pos.direction`, then recalculates `pos.coords` (and `xPos` and `yPos` as well).
    