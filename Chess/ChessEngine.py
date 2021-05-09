"""
This class is responsible for storing all the information about the current state of the chess game. Will also be responsible for determining the
valid moves at the current state. It will also keep a move log.
"""
class GameState():
    def __init__(self):    #building the structure
        #board is an eight by eight 2d list and each element of the list has 2 characters
        #the first character represents the color of the piece 'b' or ' w'
        #the second character represents the type of the piece 'K','q', etc.
        #"--" represents empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'p': self .getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}  #createsa dictionary

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()    #coordinates for the square where enassant capture is possible
        self.enpassantPossibleLog = [self.enpassantPossible]
        #castling rights
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]



        '''
        Takes a move as a parameter and executes it (this will not work for castling, pawn promotion, and en-passant
        '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  #swap players
        #update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #enpassantMove
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'  #capturing the pawn

        #update the enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:  #only for two square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  #kingsideCastle move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  #moves the rook
                self.board[move.endRow][move.endCol + 1] = '--'  #erase the old rook
            else: #queensideCastleMove
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]     #move the rook
                self.board[move.endRow][move.endCol - 2] = '--'
        self.enpassantPossibleLog.append(self.enpassantPossible)
        #update castling Rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

        '''
        Undo the last move 
        '''
    def undoMove(self):
        if len(self.moveLog) != 0:#making sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved #put piece on the starting square
            self.board[move.endRow][move.endCol] = move.pieceCaptured   #put back captured piece
            self.whiteToMove = not self.whiteToMove #switch turns back
            #update the king's location if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            #undo the enpassantMove
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'  #leave the landing square blamk
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            #undo castling Rights
            self.castleRightsLog.pop()  #gets rid of the one we just saved
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)  #set the current castle rights to the previous one in the list that is the last one
            #undo the castleMove
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  #kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  #queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'  #sets the preious location to blank

            #adding
            self.checkMate = False
            self.staleMate = False


    '''
    Update the castle rights given the move 
    '''

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left Rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':  # for the black side
            if move.startRow == 0:
                if move.startCol == 0:  # left Rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.bks = False


    '''
    All moves with considering checks
    '''
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastlingRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                          self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)  #copies the current castling rights
        #1. generate all possible moves
        moves = self.getAllPossibleMoves()
        '''
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        '''
        #2. for each move, make the move
        for i in range(len(moves) - 1, -1, -1):  #go through backwards when you are removing from a list as iterating
            self.makeMove(moves[i])
            #3. generate all opponents moves
            #4. for each of your opponent's moves, see if they attack  your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  #5. if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:  #either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
            '''
        else:
            self.checkMate = False
            self.staleMate = False
            '''
        self.enpassaantPossible = tempEnpassantPossible    #save the value for when the whole
        self.currentCastlingRight = tempCastlingRights    #rests them back to temp
        return moves

    '''
    Determine if the current player is in chnick diaz is a true legend and 
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])  #square under attack of the white king location
        else:                                                                                    #if the black king is considered, let's see if the black king is nder attack
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
     Determine if the enemy can attack the square r, c
    '''
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  #switch to opponent's turns as we want to see their turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  #switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  #square is under attack
                #self.whiteToMove = not self.whiteToMove
                #self.whiteToMove = not self.whiteToMove  #switch the turn back
                return True
        return False

    '''
    All moves without considering checks.
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):   #number of rows
            for c in range(len(self.board[r])):  #number of cols in the given row
                turn = self.board[r][c][0]
                if(turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):  #to find the bugs print any random statement
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)  #calls the appropriate move function based on piece types
        return moves
    '''
        Get all the pawn moves for the pawn located at row, col and add these moves to thee list
    '''
    def getPawnMoves(self, r, c, moves):
        '''
        piecePinned = False
        pinDirection = ()
        '''
        '''
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
                '''
        if self.whiteToMove:    #white pawn moves asderwald
            if self.board[r-1][c] == "--": #1 square move
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  #2 square pawn advance
                    moves.append(Move((r, c), (r-2, c), self.board))
                    '''
                moves.append(Move((r,c), (r+moveAmount, c), self.board, pawnPromotion=pawnPromotion))
                if r == startRow and self.board[r+2*moveAmount][c] == "--":  #2 square moves   
                    moves.append(Move((r, c), (r+2*moveAmount, c), self.board))'''
            if c-1 >= 0:  #captures to the left and makes sure that the pieces o not breach the boundaries of the board
                if self.board[r-1][c-1][0] == 'b':  #enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
                '''
                if (r + moveAmount, c - 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, enPassant = True))
                '''
            if c+1 <= 7:  #captures to the right
                if self.board[r - 1][c + 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))

        else:   #black pawn moves
            if self.board[r+1][c] == "--": #1 square move
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
                    '''
                moves.append(Move((r,c), (r+moveAmount, c), self.board, pawnPromotion=pawnPromotion))
                if r == startRow and self.board[r+2*moveAmount][c] == "--":  #2 square moves
                    moves.append(Move((r, c), (r+2*moveAmount, c), self.board))
                    '''
            if c - 1 >= 0:  # captures to the left and makes sure that the pieces o not breach the boundaries of the board
                if self.board[r + 1][c - 1][0] == 'w':  # enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
                    '''
                    if (r + moveAmount, c - 1) == self.enPassantPossible:
                        moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, enPassant = True))
                    '''
            if c + 1 <= 7:  # captures to the right
                if self.board[r + 1][c + 1][0] == 'w':  #enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))
            #add pawn promotions later
        '''
        Get all the rook moves for the rook located at row, col and add these moves to the list
        '''
    def getRookMoves(self, r, c, moves):
        '''
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':  #cant' remove queen from pin on rook moves, only removes it on bishop moves
                    self.pins.remove(self.pins[i])
                break
                '''
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))   #up, left, down right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #on board
                    #if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):  #the piece should be able to move towards the pin and away from the pin
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": #empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: #enemy Piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: #friendly piece invalid
                        break
                else:  #off board
                    break
        '''
            Get all the knight moves for the rook located at row, col and add these moves to the list
        '''

    def getKnightMoves(self, r, c, moves):
        '''
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
                '''
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                '''if not piecePinned:'''
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  #not an ally piece (empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    '''
    Get all the bishop moves for the rook located at row, col and add these moves to the list
    '''

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  #4 diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):  #bishop can move max of 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  #is it on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty Piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: #enemy piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  #friendly piece invalid
                        break
                else:  # off board
                    break
        '''
            Get all the queen moves for the rook located at row, col and add these moves to the list
        '''

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    '''
        Get all the king moves for the rook located at row, col and add these moves to the list
    '''

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            '''
            for i in range(8):
                endRow = r + kingMoves[i][0]
                endCol = c + kingMoves[i][1]
                '''
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # not an ally piece (empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    '''
    Generate all the valid Castling Moves for the king at (r, c) and add them to the list of moves
    '''
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return  #we can't castle we are in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)


    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':   #makes sure that that the sqyare is empty
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove = True))


    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][ c - 3] == '--':   #we do not have to worry about the third one
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove = True))

    '''
    Returns if player is in check, a list of pins, and a list of checks
    '''

    def checkForPinsAndChecks(self):
        pins = []  # squares where the allied pinned piece is and direction pinned from
        checks = []  # squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd allied piece, so no pin or check is possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities here in this complex conditional
                        # 1. orthogoinally away from king and piece is a rook
                        # 2. diagonally away from king and piece is a bishop
                        # 3. 1 square away diagonally from the king and piece is a pawn
                        # 4. any direction and piece is a queen
                        # 5, any direction 1 square away and piece is king ( this is necessary to prevent a king move to a square controlled by another king
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():  # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:
                    break  # off board
        #check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0]  == enemyColor and endPiece[1] == 'N':  #enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  #left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:    #right rook
                    self.currentCastlingRight.wks = False
            elif move.pieceMoved == 'bR':
                if move.startRow == 0:
                    if move.startCol == 0:  #left rook
                        self.currentCastlingRight.bqs = False
                    elif move.startCol == 7:    #right rook
                        self.blackCastleQueenside = False

            #if a rook is captured
            if move.pieceCaptured == 'wR':
                if move.endRow == 7:
                    if move.endCol == 0:
                        self.currentCastlingRight.wqs = False
                    elif move.endCol == 7:
                        self.currentCastlingRight.wks = False
            elif move.pieceCaptured == 'bR':
                if move.endRow == 0:
                    if move.endCol == 0:
                        self.currentCastlingRight.bqs = False
                    elif move.endCol == 7:
                        self.currentCastlingRight.bks = False


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks   #initialising them
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    # maps keys to values
    # keys:values
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}  # used for reversing in a dictionary
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):    #in this class we are adding optional paramters
        self.startRow = startSq[0]     #decoupling tuples
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        #pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        #En Passante
        self.isEnpassantMove = isEnpassantMove  #enPassant captures opposite colored pawn
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        #castle move
        self.isCastleMove = isCastleMove    #only generates the valid castling moves
        self.isCapture = self.pieceCaptured != '--'   #piece captured is not an empty space
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

        '''
        Overriding the equals method
        '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # real chess notations can be added later
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    #overriding the string function
    def __str__(self):
        #castle move
        if self.isCastleMove:
            return "O-O" if self.endCol == 6  else "O-O-O" #kingside castle

        endSquare = self.getRankFile(self.endRow, self.endCol)
        #pawn moves
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare

        #two of the same type of piece moving to a square, nbd2 if both knights can move to d2
        #also adding + fr check move, and #for checkmate move


        #piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += 'x'
        return moveString + endSquare

