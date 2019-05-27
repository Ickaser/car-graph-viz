import graphGen
import cars

 
size = (800, 800)

graph = graphGen.Graph(8)
graph.makeCoords8nodes(size)
graph.calcEdgeLengths()

pos = cars.Position(graph, 3, 2, 80)
print(pos.__dict__)