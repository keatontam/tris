# Manages pieces individually and updates them according to their statuses
# This is essentially the "player" as the character is the current falling piece.

import random
import collections
import pygame
class Piece(pygame.sprite.Sprite):
    # get spritesheet and split-up sprites
    image = pygame.image.load('images/tetrominos.png').convert_alpha()
    rows, cols = 3,4
    width, height = image.get_size()
    cellWidth, cellHeight = width / cols, height / rows
    images = []
    for i in range(rows):
        for j in range(cols):
            subImage = image.subsurface((j * cellWidth, i * cellHeight, cellWidth, cellHeight))
            images.append(subImage)

    # set-up shapes and valid wall kicking

    IPiece=  [[0,0,0,0],
              [1,1,1,1],
              [0,0,0,0],
              [0,0,0,0]]

    JPiece = [[2,0,0],
              [2,2,2],
              [0,0,0]]

    LPiece = [[0,0,3],
              [3,3,3],
              [0,0,0]]

    OPiece = [[4,4],
              [4,4]]

    SPiece = [[0,5,5],
              [5,5,0],
              [0,0,0]]

    ZPiece = [[6,6,0],
              [0,6,6],
              [0,0,0]]

    TPiece = [[0,7,0],
              [7,7,7],
              [0,0,0]]

    roulette=[[[ 0, 0, 0, 0],
               [10,10,10,10],
               [ 0, 0, 0, 0],
               [ 0, 0, 0, 0]],

              [[10, 0, 0],
               [10,10,10],
               [ 0, 0, 0]],

              [[ 0, 0,10],
               [10,10,10],
               [ 0, 0, 0]],

              [[10,10],
               [10,10]],

              [[ 0,10,10],
               [10,10, 0],
               [ 0, 0, 0]],

              [[10,10, 0],
               [ 0,10,10],
               [ 0, 0, 0]],

              [[ 0,10, 0],
               [10,10,10],
               [ 0, 0, 0]]
              ]

    shapes = [IPiece, JPiece, LPiece, OPiece, SPiece, ZPiece, TPiece]
    wallKicks = [
        [(0, 1), (0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        [(1, 0), (0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        [(1, 2), (0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        [(2, 1), (0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        [(2, 3), (0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        [(3, 2), (0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        [(3, 0), (0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        [(0, 3), (0, 0), (1, 0), (1, 1), (0, -2), (1, -2)]
                ]
    IKicks = [
        [(0, 1), (0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        [(1, 0), (0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        [(1, 2), (0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        [(2, 1), (0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        [(2, 3), (0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        [(3, 2), (0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        [(3, 0), (0, 0), (1, 0), (-2, 0), (1, -2), (-1, 2)],
        [(0, 3), (0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)]
             ]
    # establish 7-bag random generator
    bag = [i for i in range(7)]
    random.shuffle(bag)
    # establish Delayed Autoshift (DAS) with charge potential
    DAS=200 # miliseconds
    DASCounter=0
    # Held piece statistic
    heldPiece=None

    def __init__(self,c,r):
        super(Piece,self).__init__()
        self.rotateState=0
        # decides one of the seven
        if len(Piece.bag)<=0:
            self.newBag()
        choice=Piece.bag.pop()
        self.shape=Piece.shapes[choice]
        # we need the base-shape for comparison and is never modified
        self.base=self.shape.copy()
        self.c,self.r=c-(len(self.shape)//2),r
        # tetromino.png organized for colors
        self.image=Piece.images[choice]
        # Lock Delay
        self.lockDelay=500 # miliseconds
        self.lockCounter=0
        self.moveCount=0
        self.rotated=False
        self.tspin=True

    def move(self,data,dc,dr):
        self.r+=dr
        self.c+=dc
        if not self.isLegal(data):
            self.r-=dr
            self.c-=dc
            return False
        if dr==0:
            pygame.mixer.Sound.play(data.move)
        self.rotated=False
        if self.isFloored(data):
            self.lockCancel()
        return True

    def lockCancel(self):
        self.moveCount += 1
        if self.moveCount <= 15:
            self.lockCounter = 0

    def isFloored(self,data):
        self.r+=1
        if not self.isLegal(data):
            floored=True
        else:
            floored=False
        self.r-=1
        return floored

    def rotateClockwise(self,data):
        # store pre-rotate properties for query
        oldShape = self.shape
        oldState = self.rotateState
        oldR = self.r
        oldC = self.c
        # ready post-rotate properties for query
        newShape = [[self.shape[y][x] for y in range(len(self.shape) - 1, -1, -1)]
                    for x in range(len(self.shape[0]))]
        self.shape=newShape
        self.rotateState = abs((self.rotateState + 1) % 4)
        self.r = self.r + (len(self.shape) // 2) - (len(newShape) // 2)
        self.c = self.c + (len(self.shape[0]) // 2) - (len(newShape[0]) // 2)
        if not self.isLegal(data):
            self.shape=oldShape
            self.rotateState=oldState
            self.r=oldR
            self.c=oldC
            return False
        pygame.mixer.Sound.play(data.rotate)
        self.lockCancel()
        self.rotated=True
        return True

    def wallKick(self,data,type):
        row=self.r
        col=self.c
        state=self.rotateState
        for kick in self.wallKicks if self.base!=Piece.IPiece else self.IKicks:
            # if is target rotation CW
            if type=="CW" and kick[0]==(state%4,(state+1)%4):
                for i in range (1,len(kick)):
                    self.c=col+kick[i][0]
                    self.r=row-kick[i][1]
                    if self.rotateClockwise(data):
                        return True
                    self.c=col
                    self.r=row
                    self.rotateState=state
            # is target rotate CCW
            elif type=="CCW" and kick[0]==(state%4,(state-1)%4):
                for i in range (1,len(kick)):
                    self.c=col+kick[i][0]
                    self.r=row-kick[i][1]
                    storage=self.r,self.c
                    if self.rotateCounterClockwise(data):
                        return True
                    self.c = col
                    self.r = row
                    self.rotateState = state
        return False


    def rotateCounterClockwise(self,data):
        oldShape = self.shape
        oldState = self.rotateState
        oldR = self.r
        oldC = self.c
        newShape = [[self.shape[y][x] for y in range(len(self.shape))]
                    for x in range(len(self.shape[0]) - 1, -1, -1)]
        self.shape = newShape
        self.rotateState = abs((self.rotateState - 1) % 4)
        self.r = self.r + (len(self.shape) // 2) - (len(newShape) // 2)
        self.c = self.c + (len(self.shape[0]) // 2) - (len(newShape[0]) // 2)
        if not self.isLegal(data):
            self.shape=oldShape
            self.rotateState=oldState
            self.r=oldR
            self.c=oldC
            return False
        self.lockCancel()
        self.rotated=True
        return True


    def place(self,data):
        pygame.mixer.Sound.play(data.place)
        for row in range(len(self.shape)):
            for col in range(len(self.shape[row])):
                if self.shape[row][col]!=0:
                    data.board.grid[row+self.r][col+self.c]=self.shape[row][col]
        data.piece=data.pieceQueue.popleft()
        if len(data.piece.base)%2==1:
            data.piece.c = (data.board.cols // 2) - ((len(data.piece.base) // 2)+1)
        else:
            data.piece.c = (data.board.cols // 2) - (len(data.piece.base) // 2)
        data.piece.r = 18
        data.hasHeld=False
        data.board.hasPlaced=True
        lines=data.board.clearRows(data)
        if lines==0:
            data.endCombo=True
    def drop(self,data):
        while self.isLegal(data):
            self.r+=1
        self.r-=1
        self.place(data)

    def autoshift(self,data,dt,keysDown):
        # Account for held keys and autoshift (DAS)
        if ((keysDown(pygame.K_LEFT) or
             keysDown(pygame.K_RIGHT) or
             keysDown(pygame.K_DOWN)) and
                Piece.DASCounter < Piece.DAS):
            Piece.DASCounter += dt
        elif ((not keysDown(pygame.K_LEFT)) and
              (not keysDown(pygame.K_RIGHT)) and
              (not keysDown(pygame.K_DOWN))):
            Piece.DASCounter = 0
        else:
            if keysDown(pygame.K_LEFT):
                self.move(data,-1, 0)
            if keysDown(pygame.K_RIGHT):
                self.move(data,1, 0)
            if keysDown(pygame.K_DOWN):
                self.move(data,0, 1)

    def isLegal(self,data):
        for row in range(len(self.shape)):
            for col in range(len(self.shape[0])):
                if (self.shape[row][col]!=0 and
                    (row+self.r>=data.board.rows or row+self.r<0 or
                     col+self.c>=data.board.cols or col+self.c<0 or
                     data.board.grid[row+self.r][col+self.c]!=0)):
                    return False
        return True

    @staticmethod
    def newBag():
        Piece.bag = [i for i in range(7)]
        random.shuffle(Piece.bag)

    def checkLock(self,dt,data):
        if self.isFloored(data):
            if (self.lockCounter>=self.lockDelay):
                self.place(data)
            else:
                self.lockCounter+=dt
        else:
            self.moveCount=0
            self.lockCounter=0

    def checkTspin(self,data):
        centerR=self.r+(len(self.shape)//2)
        centerC=self.c+(len(self.shape[0])//2)
        if(self.rotated and self.base==Piece.TPiece):
            upLeft=True
            upRight=True
            downLeft=True
            downRight=True
            if centerR-1>=0 and centerC-1>=0:
                upLeft=data.board.grid[centerR-1][centerC-1]!=0
            if centerR-1>=0 and centerC+1<data.board.cols:
                upRight=data.board.grid[centerR-1][centerC+1]!=0
            if centerR+1<data.board.rows and centerC-1>=0:
                downLeft=data.board.grid[centerR+1][centerC-1]!=0
            if centerR+1<data.board.rows and centerC+1<data.board.cols:
                downRight=data.board.grid[centerR+1][centerC+1]!=0
            return (upLeft or upRight) and downLeft and downRight
        return False

    def spinner(self):
        if self.roulette:
            currState=self.rotateState
            while self.rotateState!=0:
                self.rotateClockwise()
            self.shape=Piece.roulette[Piece.roulette.index(self.shape)+1]


    def update(self,dt,keysDown,data):
        if not self.isLegal(data):
            data.gameOver=True
        self.checkLock(dt,data)
        data.tspin=self.checkTspin(data)
        if len(Piece.bag)<=0:
            self.newBag()
        # if roulette block
        if 10 in self.shape:
            self.spinner()
        self.autoshift(data,dt,keysDown)

    def draw(self,screen):
        width,height=screen.get_size()
        for row in range(len(self.shape)):
            for col in range(len(self.shape[0])):
                if self.shape[row][col]!=0:
                    # we need to subtract screen height because it accounts for matrix/overlay
                    screen.blit(self.image,
                                (((self.c+col)*Piece.cellWidth),
                                 ((self.r+row+1)*Piece.cellHeight)-height))

def blitAlpha(target, source, location, opacity):
    x = location[0]
    y = location[1]
    temp = pygame.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)
    target.blit(temp, location)

class GhostPiece(Piece):
    def __init__(self,p):
        self.shape = p.shape
        self.base = self.shape.copy()
        self.c, self.r = p.c, p.r
        self.image = p.image
        self.width,self.height=self.image.get_size()
        self.moveCount=0
    def fall(self,data):
        while self.move(data, 0, 1): pass
    def update(self,dt,keysDown,data):
        self.c, self.r = data.piece.c, data.piece.r
        self.shape=data.piece.shape
        self.image=data.piece.image
        self.fall(data)
    def draw(self,screen):
        width,height=screen.get_size()
        for row in range(len(self.shape)):
            for col in range(len(self.shape[0])):
                if self.shape[row][col]!=0:
                    blitAlpha(screen,self.image,
                                (((self.c+col)*self.width),
                                 ((self.r+row+1)*self.height)-height),64)