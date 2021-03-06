# built by Isaac Wheeler, intern at CNR-IIA, beginning on 24/5/2019

import pygame
import pygame.freetype
import simulator.graphGen as graphGen
import simulator.cars as cars
import numpy as np

# window size to be used by pygame. (X, Y)
# gets used in a number of functions, as it turns out
size = (650, 455)


# configurable values used when generating cars
carSettings = dict(
    carSize = 13,
    carAccel = 3,
    nodeWait = 5,
    randomBehavior = False,
    mistakes = True
)
lanes = True
weights = False
carsNum = 5
stepsNum = 1
fps = 20

# should be in same directory as this file
xmlFilename = "storage_a.xml"

#pseudorandom: set a constant seed so that it runs the same each time
np.random.seed(1234)

def main():

    global stepsNum
    global carsNum
    global size
    global font

    start_pygame()
    font = pygame.freetype.SysFont("Times New Roman", 14)

    graph = graphGen.Graph(nodeNum = 8, xml = xmlFilename, weighted=weights, lanes = lanes)
    graph_init(graph, size)

    # draw the map  
    map = pygame.Surface(size)
    draw_map(graph, map)

    # create a window with the above specified size
    screen = pygame.display.set_mode(size)

    # copy the map as drawn to the window, update the display
    # Start a list called dirtyRects: used below with pygame.display.update to avoid redrawing the whole screen every time
    screen.blit(map, (0, 0))
    pygame.display.flip()

    # create the cars
    carList = [cars.Car(graph, carSettings) for i in range(carsNum)]

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

                # print final results
                np.savetxt("results.txt", graph.history, fmt="%s", header = "Next run begins here.")

            elif event.type == pygame.KEYDOWN:
                sliders(event, screen)
        
        # update system state
        update_system(stepsNum, carList, graph)           

        # draw system to screen
        update_screen(screen, map, carList)

        # tick the system clock
        clock.tick(fps) #framerate of 20 fps



# -------------------------------------------------------------------------
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
    pygame.display.set_caption("Traffic Simulation")

    # stat pygame's typesetting system
    pygame.freetype.init()

def graph_init(graph, size):
    """
    Encapsulates the functions which initialize the graph.
    Takes window size as an argument.
    """

    # create the graph
    if not graph.xml:
        graph.makeCoords8nodes(size)
        graph.calcEdgeLengths()
        graph.genEdgeSpeeds()

    # alternative: read from the xml
    else:
        graph.xmlGetStreetProperties()

    
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
        while len(carList) < carsNum:
            carList.append(cars.Car(graph, carSettings))

def update_screen(screenObj, mapObj, carList):

    
    # draw the map again, to overwrite old car positions
    screenObj.blit(mapObj, (0, 0))

    # Draw cars to the screen
    # Keeps a list of areas of the screen which have been updated
    for i, car in enumerate(carList):
        #keep exactly one of the following uncommented

        #various colors, oldest cars are red and newest are green
        # colorOffset = int(255.0/len(carList))
        # pygame.draw.circle(screenObj, pygame.Color(255 - colorOffset * i, colorOffset*i, 0, 255), car.pos.coords, car.carSize / 2)

        #various colors, random based on car id
        pygame.draw.circle(screenObj, pygame.Color((int(id(car))/4 +128) % 255, int(id(car))/5 % 255, 100, 255), car.pos.coords, car.carSize / 2)

        #red one way, blue the other
        # pygame.draw.circle(screenObj, pygame.Color("red" if car.pos.direction else "blue"), car.pos.coords, car.carSize / 2)

        #red at stopped, more green at speed
        # pygame.draw.circle(screenObj, pygame.Color(*(255 - 5*car.velocity, 5*car.velocity, 0, 255)), car.pos.coords, car.carSize / 2)

    # Write slider state to screen
    font.render_to(screenObj, (10,size[1]-20), "Total cars: {0}    Steps per frame: {1}".format(len(carList), stepsNum) , fgcolor = pygame.color.Color("black"))

    # Update the display
    pygame.display.update()

def sliders(event, screenObj):
    global carsNum
    global stepsNum
    # slider functionality: left slows down, right speeds up
    if event.key == pygame.K_LEFT:
        stepsNum -= 1 if stepsNum > 0 else 0
    elif event.key == pygame.K_RIGHT:
        stepsNum += 1

    # slider functionality: up adds cars, down subtracts (once cars reach their goal)
    elif event.key == pygame.K_UP:
        carsNum += 1
    elif event.key == pygame.K_DOWN:
        carsNum -= 1 if carsNum > 0 else 0

# -------------------------------------------------

if __name__=="__main__":
    main()
