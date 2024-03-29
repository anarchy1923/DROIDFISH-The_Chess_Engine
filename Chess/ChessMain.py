"""
This is our main driver file. It will be responsible for handling user input and displaying the current GameState(class) object.
"""

import pygame as p
from Chess import ChessEngine, SmartMoveFinder
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512 # alternative to be 400
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  #dimesions of the board being 8 x 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15  #for animations later on
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called exactly once in the main.
'''
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #Note: we can access an image by using 'IMAGES['wp']'

'''
THE MAIN driver for our code. This will handle user input and updating the graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  #flag variable for when a move is made
    animate = False #flag variable for when when we should animate a move
    loadImages()    #only do this once, before the while loop
    running = True
    sqSelected = ()  #makes this a tuple no square is selected initially(tuple: (row,col)
    playerClicks = []  #keep track of the player clicks (two tuples: [(6,4),(4,4)]
    gameOver = False
    playerOne = True #if a human is playing white, this is true. If an AI is playing it is false  #we can pit two ai against each other by turning it false
    playerTwo = False  #same as above but for black
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:  #event functionality
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  #(x,y) location of the mouse
                    col = location[0]//SQ_SIZE      #source of the bug
                    row = location[1]//SQ_SIZE
                    if sqSelected  == (row, col) or col >= 8: #the user clicked the same square twice or user click the mouse log
                        sqSelected = ()  #deselcted
                        playerClicks  = []  #clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  #append for both 1sr and 2nf clicks
                    if len(playerClicks) == 2:  #after second click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () #reset user clicks
                                playerClicks = []
                        if not moveMade:
                                playerClicks = [sqSelected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False     #here animate is a flag variable
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:  #reset the board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True


        #AI move finder logic
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("thinking...")
                returnQueue = Queue()   #used to pass the data between threads
                moveFinderProcess = Process(target=SmartMoveFinder.findBestMove, args= (gs, validMoves, returnQueue))
                moveFinderProcess.start() #call findBestMove(gs, validMoves, returnQueue)

            if not moveFinderProcess.is_alive():
                print("done thinking")
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = SmartMoveFinder.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False


        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)    #we are animating the last move in the movelog, on the screen with the board using pygame clock
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)
        if gs.checkMate or gs.staleMate:
            gameOver = True
            text = 'Stalemate' if gs.staleMate else 'Black wins by Checkmate' if gs.whiteToMove else 'White wins by Checkmate'
            drawEndGameText(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()

'''
Responsible for all graphics within a current GameState
'''
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)  #draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  #draw pieces on top of those squares
    drawMoveLog(screen, gs, moveLogFont)

'''
Draw squares on the board. The top left square is always light
'''
def drawBoard(screen):
    global colors
    colors = [p.Color("white"),p.Color("darkgreen")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):  #for 8 rows and 8 coloumns
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


            #the dark squares are off parity and white squares are even parity

'''
Highlights the square selected and moves for piece selected
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):   #sqSelected is a piece hat can be moved
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  #transparency value, -> 0 transparent, 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from the square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


'''
Draw the pieces on the board using the current gamestate.board
'''
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  #not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
'''
Draw the move Log
'''
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)  # a rectangel object
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):    #make sure black made a move
            moveString += str(moveLog[i+1]) + "  "
        moveTexts.append(moveString)
    #1. e2e4 e4e5 2.

    movesPerRow = 3
    padding = 5
    textY = padding
    lineSpacing = 2 #in pixels
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]        #does three moves altogether
        textObject = font.render(text, True, p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


'''
Animating a move
'''
def animateMove(move, screen, board, clock):
    coords = []  #list of coordinates that the animation will move through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 #frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the pieceMoved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)   #is a pygame object, sqsize is the length
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        if move.pieceMoved != '--':
            screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()

