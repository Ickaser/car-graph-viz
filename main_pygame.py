# built by Isaac Wheeler, intern at CNR-IIA, beginning on 24/5/2019

import pygame
import pygame.freetype
import graphGen
import cars

def main():

    # initialize pygame
    pygame.init()
    # set up the top bar of the window
    logo = pygame.image.load("32x32CNRIIA.jpg")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("macchine che muovono")

    # window size to be used by pygame
    size = (800, 800)

    # create/import the graph
    # TODO: encapsulate this better

    graph = graphGen.Graph(8)
    graph.makeCoords8nodes(size)
    graph.calcEdgeLengths()
    graph.genEdgeSpeeds()

    #create a car: random style
    # TODO create multiple cars, organized goals
    carsNum = 100
    stepsNum = 1
    carList = [cars.Car(graph) for i in range(carsNum)]
    

    # draw the map (TODO: encapsulate this better)
    map = pygame.Surface(size)
    WHITE = pygame.Color("white")
    BLACK = pygame.Color("black")
    RED = pygame.Color("red")
    map.fill(WHITE)
    font = pygame.freetype.SysFont("Times New Roman", 12)

    # drawing the map: this portion is specified to graphGen's graph structure
    for i, n in enumerate(graph.nodes):
        pygame.draw.circle(map, BLACK, n["coords"], 7)
        font.render_to(map, (n["coords"][0] + 10, n["coords"][1]), str(i), pygame.Color("black"))

    pygame.freetype.init()
    

    for e in graph.edges.keys(): 
        lineArea = pygame.draw.line(map, BLACK, graph.nodes[e[0]]["coords"], graph.nodes[e[1]]["coords"], 3)

        
        # label all of the edge lengths
        font.render_to(map, (lineArea.centerx + 5, lineArea.centery), str(int(graph.edges[e]["length"])))
        

    
    

    # create a window with the above specified size
    screen = pygame.display.set_mode(size)

    # copy the map as drawn to the window, update the display
    dirtyRects = [screen.blit(map, (0, 0))]
    pygame.display.flip()

    

    # variable for controlling the main() loop
    running = True

    # pygame Clock object for controlling the framerate and update speed
    clock = pygame.time.Clock()

    # loop main
    while running:

        # event handling: get all events since previous loop
        for event in pygame.event.get():
            
            # if event is QUIT:
            if event.type == pygame.QUIT:
                # exit loop
                running = False
        
        # update system state
        for step in range(stepsNum):
            for car in carList:
                car.updatePosition()


        # draw system to screen
        # TODO: wrap this

        # draw the map again, to overwrite old car positions
        screen.blit(map, (0, 0))

        # Draw car to the screen
        # Keeps a list of areas of the screen which have been updated
        for car in carList:
            dirtyRects.append(pygame.draw.circle(screen, RED, car.pos.coords, 5))

        
        # update the parts of the screen which have changed
        pygame.display.update(dirtyRects[-carsNum*2:] )

        # tick the system clock
        clock.tick(20) #framerate of 20 fps


        
        # 


if __name__=="__main__":
    main()
