# car-graph-visual

Built by Isaac Wheeler on internship at CNR-IIA, Montelibretti campus. Begun 23/5/2019.  

TODO:
Improve readability of cars.py (car behavior functions)  
Improve car following (cars still get too close, when moving slow at nodes)  
Data generation
Cars can get completely blocked: good, that is physical. What then?

Document cars.py
Example script
Document tuning/adjustable areas


Goal: a toy problem to which AI methods can be applied, to showcase the possibility for improvement in real-time traffic 
flow. The program will take an XML file as input, which will allow real map data to be used as a graph structure.  

At present: the program generates a graph with semirandom coordinates and structure, and dots representing cars move 
along the edges of the graph, randomly picking a new direction of travel each time they reach a node.  
No data files are generated as the program is run--it runs the simulation in a way that allows visualization, and nothing more.


To simulate traffic slowdown, there are two main ideas at the moment:
1. `weights`: Add a system of capacities and weights to the graph which lowers the effective speed limit along an edge as the number 
of cars on that edge increases. This method is loosely implemented, but needs significant refinement and tuning
before it will resemble normal traffic flow.  
2. `lanes`: Disallow car overlay and slow down cars so that they do not collide visually; separate them on opposite sides of the 
edge.  
To use either implementation, initialize the Graph class with either `lanes = True` or `weights = True`; Positions and Cars 
initialized with the graph will inherit their behavior from that attribute. Using both is untested and discouraged. 

Three main classes are used to run the simulation; they are separated to make the code easier to work with, but depend heavily on 
each other.

1. graphGen.py:
Implements a `Graph` class. 
The `Graph` is currently initialized with a semirandom structure. Eventually, it will take an XML input file, from which it
will construct the graph structure.  
The system of weights and capacities is largely implemented in this class, with some interfacing with the Position class.
The structure is as follows:
* `graph.nodes`: A list of dictionaries. Effectively, access a point by accessing the list at the point's index; access that point's attributes with string keys, notably:
    * `"coords"` for XY coordinates 
    * `"connect"` for a list of connected points.
    * `"capacity"` for an int, indicating max number of cars in the node. Used only with lanes implementation.
    * `"population"` for a list of Positions of the cars which are on the node. Used only with lanes implementation
* `graph.edges`: A dictionary of dictionaries. 
    * Access an edge with a tuple of the two points connected (in either order), 
    * Access an edge's attributes with string key:
        * `"length"` 
        * `"speed"` for speed limit
        * `"capacity"` for capacity factor (used to model high-density traffic)
        * `"weighted speed"` for speed limit adjusted for traffic (distinct for each direction of travel)
        * `"population"` is a list containing two lists (one for each direction of travel). This
        property is not modified within the Graph class; interacts with Position and Car classes.
* `graph.updateWeights()`: a function to call when using the weighted slowdown system. Using the `"population"` and 
`"capacity"` values for each edge, adjusts the `"weighted speed"` value. The `Position.update(displace)` function depends on that weighted speed if the weighted functionality is set to True.

        
  
2. cars.py:
Implements a `Position` class and a `Car` class, which combined handle movement of cars.  

The `Position` class depends heavily on the `Graph` class, as described above. To simplify the interface with pygame, all values are rounded off and stored as ints.
* Functions and methods of a Position instance:
    * `Position(graph, nodeFrom, nodeTo, dist = 0, eqTol = 10)` : takes the graph, stores it internally (by reference, of course); takes `nodeFrom` and `nodeTo`, which sets the edge on which the car begins; dist is the distance *from `nodeFrom`*, which allows a position to be initialized on the edge instead of at the node. If the graph has `weighted=True`, then adds the new instance to the `"population"` list attribute of the edge.
    * `pos.update(displace)`: Adds `displace` to the distance along the edge according to `pos.direction`, then recalculates `pos.coords` (and `xPos` and `yPos` as well). If using the `lanes` implementation, does not move if the
    * `pos.changeNodes(newNode)`: Used to move `pos` to a new edge. Makes a call to the `__init__` function described above, in order to recalculate all values. If using `weights` or `lanes`, removes pos from the edge's `"population"` attribute before calling the `__init__` so that the population is accurate. 
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
    
The Car class depends heavily on both the Graph and Position classes above.

* Arguments to set when initializing the class:
    * graph: should be an instance of the above Graph class. Car behavior is determined by `graph.lanes` and `graph.weights`.
    * randomBehavior: defaults to `True` at the moment. No implementation yet for `False`. If `False`, should have a goal and seek the destination.
    * carSize: defaults to `5`. Should be a size in pixels; gets used internally within `lanes` behavior to keep cars from overlapping. May be used in car visualization.
    * accel: defaults to `5`. The acceleration and deceleration of the cars; `5` means at each position update, the car's velocity (in pixels per frame) changes by at most 5.
    * pos: defaults to `0`. Currently unused; once implemented, will give a starting position to the car.
* Functions and methods:
    * `updatePosition()`: Implements the entire movement system of the car. Call it once per update cycle: if the car is at a node, moves to the next edge (by calling `Position.ChangeNodes(nextNode)`), or if car is on edge, updates the `velocity` attribute (according to base, `weights`, or `lanes` implementation, which are checked internally), then moves along edge according to `velocity` attribute by calling `Position.update(velocity)`.  
    This method is fairly large and contains all of the logic for each individual car's movement behavior.




Essential functions to call to run a simulation:  


TODO:  
* Improve heuristic weight function (Graph class).
* Implement stochastic failure to follow route plan (Car class, updatePostion function)
* Implement online search for route plan: within Car class?
* Implement ACS (ant colony system) intelligence within route planning.