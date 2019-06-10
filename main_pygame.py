# built by Isaac Wheeler, intern at CNR-IIA, beginning on 24/5/2019

import pygame
import pygame.freetype
import graphGen
import cars
from numpy.random import randint

# Currently: running with lanes, randomly generated graph with 8 nodes
# Color of car dots is half blue and half red

# window size to be used by pygame. (X, Y)
# gets used in a number of functions, as it turns out
size = (800, 800)

# configurable values used when generating cars
carsNum = 1
carSize = 20
stepsNum = 1
carAccel = 3
lanes = True
weights = False
randomBehavior = False

def main():


    start_pygame()

    graph = graphGen.Graph(8, weighted=weights, lanes = lanes)
    graph_init(graph, size)

    #create cars: random style
    # TODO: nonrandom cars & goals
    carList = [cars.Car(graph, randomBehavior = randomBehavior, accel = carAccel, carSize = carSize) for i in range(carsNum)]
    oldCarsNum = carsNum

    # draw the map  
    map = pygame.Surface(size)
    draw_map(graph, map)

    # create a window with the above specified size
    screen = pygame.display.set_mode(size)

    # copy the map as drawn to the window, update the display
    # Start a list called dirtyRects: used below with pygame.display.update to avoid redrawing the whole screen every time
    dirtyRects = [screen.blit(map, (0, 0))]
    pygame.display.flip()

    # variable for controlling the main() loop
    running = True

    # pygame Clock object for controlling the framerate and update speed
    clock = pygame.time.Clock()

    # main loop
    while running:

        # event handling: get all events since previous loop
        for event in pygame.event.get():
            
            # if event is QUIT:
            if event.type == pygame.QUIT:
                # exit loop
                running = False
        
        # update system state
        update_system(stepsNum, carList, graph)           


        # draw system to screen
        update_screen(screen, map, carList, dirtyRects)

        # tick the system clock
        clock.tick(20) #framerate of 20 fps

# -----------------------------------------------------
# Encapsulation functions (just to make the main more readable)

def start_pygame():
    """
    Encapsulates the functions which initialize a pygame window.
    """

    # initialize pygame
    pygame.init()
    # set up the top bar of the window
    logo = pygame.image.load("32x32CNRIIA.jpg")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("macchine che muovono")

    # stat pygame's typesetting system
    pygame.freetype.init()

def graph_init(graph, size):
    """
    Encapsulates the functions which initialize the graph.
    Takes window size as an argument.
    """

    # create/import the graph
    # TODO: encapsulate this better

    graph.makeCoords8nodes(size)
    graph.calcEdgeLengths()
    graph.genEdgeSpeeds()
    
def draw_map(graph, map):
    """
    Encapsulates the functions which draw the map to a pygame Surface object.
    Takes the graph and a pygame Surface object as arguments.
    """

    WHITE = pygame.Color("white")
    BLACK = pygame.Color("black")
    RED = pygame.Color("red")
    map.fill(WHITE)
    font = pygame.freetype.SysFont("Times New Roman", 12)

    # drawing the map: this portion is specified to graphGen's graph structure
    for i, n in enumerate(graph.nodes):
        pygame.draw.circle(map, pygame.Color("black"), n["coords"], 7)
        font.render_to(map, (n["coords"][0] + 10, n["coords"][1]), str(i), pygame.Color("black"))

    

    for e in graph.edges.keys(): 
        lineArea = pygame.draw.line(map, pygame.Color("black"), graph.nodes[e[0]]["coords"], graph.nodes[e[1]]["coords"], 3)

        
        # label all of the edge lengths
        font.render_to(map, (lineArea.centerx + 5, lineArea.centery), str(int(graph.edges[e]["length"])))


def update_system(stepsNum, carList, graph):
    for step in range(stepsNum):
        if graph.weighted:
            graph.updateWeights()
        for car in carList:
            #Update position for each car; if returns True, has reached goal
            if car.updatePosition():
                # remove car from list if at goal
                carList.remove(car)
                del car
                # make a new car
                carList.append(cars.Car(graph, randomBehavior = randomBehavior, accel = carAccel, carSize = carSize))

def update_screen(screenObj, mapObj, carList, dirtyRects):

    # draw the map again, to overwrite old car positions
    screenObj.blit(mapObj, (0, 0))

    # Draw cars to the screen
    # Keeps a list of areas of the screen which have been updated
    for i, car in enumerate(carList):
        #keep exactly one of the following uncommented

        #various colors, each car stays the same
        colorOffset = int(255.0/len(carList))
        dirtyRects.append(pygame.draw.circle(screenObj, pygame.Color(255 - colorOffset * i, colorOffset*i, 0, 255), car.pos.coords, car.carSize/2))
        #red one way, blue the other
        # dirtyRects.append(pygame.draw.circle(screenObj, pygame.Color("red" if car.pos.direction else "blue"), car.pos.coords, car.carSize/2))
        #red at stopped, more green at speed
        # dirtyRects.append(pygame.draw.circle(screenObj, pygame.Color(*(255, 3*car.velocity, 0, 255)), car.pos.coords, 5))

    
    # update the parts of the screen which have changed
    
    dirtyRects[:] = dirtyRects[-carsNum*2:]
    pygame.display.update(dirtyRects)

# -------------------------------------------------

if __name__=="__main__":
    main()
