import pygame
import pygame.freetype
import graphGen

def main():

    # inizializzare pygame
    pygame.init()
    # caricare e impostare il logo
    logo = pygame.image.load("32x32CNRIIA.jpg")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("minimal program")

    #grandezza dello schermo utilizzato da pygame
    size = (800, 800)

    #creare o importare la mappa

    graph = graphGen.Graph(8)
    graph.makeCoords8nodes(size)
    graph.calcEdgeLengths()

    #disegnare la mappa
    map = pygame.Surface(size)
    WHITE = pygame.Color("white")
    BLACK = pygame.Color("black")
    map.fill(WHITE)


    #disegnare la mapppa: questa parte e specificata al mio graph randomico
    for n in graph.nodes:
        pygame.draw.circle(map, BLACK, n["coords"], 7)

    pygame.freetype.init()
    font = pygame.freetype.SysFont("Times New Roman", 12)

    for e in graph.edges.keys(): 
        lineArea = pygame.draw.line(map, BLACK, graph.nodes[e[0]]["coords"], graph.nodes[e[1]]["coords"], 3)

        
        # disegnare con testo la lunghezza di ciascun edge
        font.render_to(map, (lineArea.centerx + 5, lineArea.centery), str(int(graph.edges[e]["length"])))
        

    
    

    #creare superficie sullo schermo con grandezza sopra specificata
    screen = pygame.display.set_mode(size)

    screen.blit(map, (0, 0))
    pygame.display.flip()

    # variabile per controllare il loop main
    running = True

    # map = MapGenerate(Graph)

    # loop main
    while running:

        # gestione degli eventi: acquisisce tutti gli eventi
        for event in pygame.event.get():
            
            # se evento e QUIT:
            if event.type == pygame.QUIT:
                # exit loop
                running = False
        
        
        # Cars.Update()
        # Screen.Update()
        # 

if __name__=="__main__":
    main()
