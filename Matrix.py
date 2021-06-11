# Manages the matrix and scoring systems

import pygame
import copy
import random
import os
import decimal
import decimal

def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

def blitAlpha(target, source, location, opacity):
    x = location[0]
    y = location[1]
    temp = pygame.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)
    target.blit(temp, location)

class Matrix(pygame.sprite.Sprite):
    # we need both the board and block sprites
    board=pygame.image.load('images/matrix.png').convert_alpha()
    overlay=pygame.image.load('images/matrixOverlay.png').convert_alpha()
    cells=pygame.image.load('images/defaultBack.png').convert_alpha()
    rows,cols=4,3
    width,height=cells.get_size()
    cellWidth,cellHeight=width/cols,height/rows
    backdrop=[]
    for i in range(rows):
        for j in range(cols):
            subImage=cells.subsurface((j*cellWidth,i*cellHeight,cellWidth,cellHeight))
            backdrop.append(subImage)
    cells = pygame.image.load('images/tetrominos.png').convert_alpha()
    rows, cols = 3, 4
    width, height = cells.get_size()
    cellWidth, cellHeight = width / cols, height / rows
    minos = []
    for i in range(rows):
        for j in range(cols):
            subImage = cells.subsurface((j * cellWidth, i * cellHeight, cellWidth, cellHeight))
            minos.append(subImage)
    def __init__(self,x,y,mode):
        # game attributes
        self.mode=mode
        self.countdownTimer=0
        self.countdown=3000

        # sprite attributes
        super(Matrix,self).__init__()
        self.rainbow = [(255,0,0),(255,128,0),(255,255,0),(128,255,0),
                        (0,255,0),(0,255,128),(0,255,255),(0,128,255),
                        (0,0,255),(128,0,255),(255,0,255),(255,0,128)]
        self.backdrop=Matrix.backdrop
        self.backAnim=0
        self.animDelay=100
        self.animTrack=0
        self.comboAnim=0
        self.comboDelay=25
        self.comboTrack=0
        self.image = Matrix.board.copy()
        self.oImage=self.image.copy()
        self.overlay = Matrix.overlay.copy()
        self.oOverlay = self.overlay.copy()
        self.blocks=Matrix.minos
        self.width,self.height=self.image.get_size()
        self.overW,self.overH=self.overlay.get_size()
        self.overX=x-self.overW//2
        self.overY=y-self.overH//2
        self.x=x-self.width//2
        self.y=y-self.height//2
        self.cellSize=min(Matrix.cellWidth,Matrix.cellHeight)

        # score attributes
        self.highScore=self.getHighScore()
        self.scoreboard=pygame.Rect(self.x,self.y-40,self.width,40)
        self.linesCleared=0
        self.lines=0
        self.score=0
        self.combo=0
        self.hasPlaced=False
        self.canB2B=False

        # 15 level Standard Marathon
        if self.mode=="standard":
            self.level=1
            self.linesRemaining=10
        # 2 minute Ultra
        elif self.mode=="ultra":
            self.remainingTime=120000
        # 40 line Sprint
        elif self.mode=="sprint":
            self.timeElapsed=0
            self.linesRemaining=40

        # matrix attributes
        self.cols = 10
        self.rows = 40
        self.grid = [[0] * self.cols for r in range(self.rows)]
        self.emptyGrid=copy.deepcopy(self.grid)

        # matrix status
        self.sealTimer = None  # None = inactive
        self.sealOpacity=0

    def getHighScore(self):
        with open("records.txt", 'r') as f:
            for line in f:
                if line.startswith(self.mode):
                    return int(line.split(":")[1])

    def setHighScore(self):
        if self.mode=="standard":
            setScore=self.score
        elif self.mode=="sprint":
            setScore=self.timeElapsed
        elif self.mode=="ultra":
            setScore=self.score
        os.rename('records.txt','input.txt')
        with open('input.txt', 'r') as inputFile, open('records.txt', 'w') as outputFile:
            for line in inputFile:
                if line.startswith(self.mode):
                    outputFile.write('%s:%d\n'%(self.mode,setScore))
                else:
                    outputFile.write(line)
        os.remove('input.txt')

    def clear(self,data,lines):
        cleared=0
        if self.sealOpacity==0:
            pygame.mixer.Sound.play(data.bomb)
            
            for i in range(0,len(self.grid)):
                if cleared<lines and self.grid[i]!=[0]*self.cols:
                    self.grid.remove(self.grid[i])
                    i-=1
                    cleared+=1
                    self.grid.insert(0,[0]*self.cols)
            return True
        else:
            return False

    def clearRows(self,data):
        rowsCleared = 0
        if self.sealOpacity==0:
            for i in range(len(self.grid)-1,-1,-1):
                if 0 not in self.grid[i]:
                    self.grid.remove(self.grid[i])
                    i+=1
                    rowsCleared += 1
            for r in range(rowsCleared):
                self.grid.insert(0, [0] * 10)
            data.piece.r+=rowsCleared
            self.lines+=rowsCleared
            self.updateScore(data,rowsCleared)
        return rowsCleared

    def garbage(self,data,lines):
        pygame.mixer.Sound.play(data.garbage)
        
        for i in range(lines):
            garbage = [8] * self.cols
            garbage[random.randint(0,len(garbage)-1)]=0
            self.grid.pop(0)
            self.grid.append(garbage)
        while not data.piece.isLegal(data):
            data.piece.r-=1

    import random
    def whirlwind(self,data):
        pygame.mixer.Sound.play(data.whirlwind)
        
        for row in self.grid:
            random.shuffle(row)

    def updateScore(self,data,lines):
        self.linesCleared+=lines
        if data.endCombo:
            self.combo=0
            data.endCombo=not data.endCombo
        if self.grid != self.emptyGrid:
            self.hasPlaced = True
        if lines>=1:
            # perfect clear
            perfectClear = [800,1000,1800,2000]
            if self.grid == self.emptyGrid and self.hasPlaced:
                pygame.mixer.Sound.play(data.perfectClear)
                
                self.score+=perfectClear[lines-1] if lines<4 else perfectClear[3]
                self.hasPlaced = False
            diffClear=False
            # T-spins!
            if data.tspin:
                pygame.mixer.Sound.play(data.tspinSound)
                
                data.tspin=False
                # T-spin Single
                tSingle=(800 + (50 * self.combo))
                tDouble=(1200 + (50 * self.combo))
                tTriple=(1600 + (50 * self.combo))
                if lines==1 and not self.canB2B:
                    self.score += tSingle
                    self.lines
                # B2B T-spin Single
                elif lines==1 and self.canB2B:
                    self.score += 1.5*tSingle
                # T-spin Double
                elif lines==2 and not self.canB2B:
                    self.score += tDouble
                # B2B T-spin Double
                elif lines==2 and self.canB2B:
                    self.score += 1.5*tDouble
                # T-Spin Triple
                elif lines==3 and not self.canB2B:
                    self.score += tTriple
                # B2B T-spin Triple
                elif lines==3 and self.canB2B:
                    self.score += 1.5*tTriple
                diffClear =True
                self.canB2B = True
                if self.mode=="standard":
                    self.lines+=5*self.level
            # Standard Line Clears
            else:
                pygame.mixer.Sound.play(data.rowClear)
                
                if lines%2==1:
                    clear=(100+(lines-1)*(100*(lines-1)))+(50*self.combo)
                else:
                    clear=100+lines*(100*(lines))+(50*self.combo)
                # テトリス
                if lines>=4 and not self.canB2B:
                    self.score+=clear
                    diffClear=True
                    self.canB2B=True
                # back-to-back tetris
                elif lines>=4 and self.canB2B:
                    self.score+=1.5*clear
                    diffClear=True
                # non-special line clears
                else:
                    self.score += clear
                if self.mode=="standard":
                    if lines==1:
                        self.lines+=1
                    elif lines==2:
                        self.lines+=3
                    elif lines==3:
                        self.lines+=5
                    else:
                        self.lines+=8
            # Update final statistics
            if not (self.mode=="boss" or self.mode=="sprint"):
                if self.score>self.highScore:
                    self.highScore=self.score
            self.combo += 1
            if not diffClear:
                self.canB2B=False

    def setSeal(self,data,time):
        pygame.mixer.Sound.play(data.seal)
        
        self.sealTimer=time
        return True

    def removeSeal(self,data):
        if self.sealTimer!=None:
            pygame.mixer.Sound.play(data.sealClear)
            
            self.sealTimer=0
            self.sealOpacity=0
            return True
        return False

    def unseal(self,dt,data):
        if self.sealTimer!=None:
            self.sealTimer-=dt
            if self.sealOpacity<256 and self.sealTimer/dt>256:
                self.sealOpacity += 8
            if self.sealTimer/dt<256 and not data.tspin:
                self.sealOpacity-=1
            if data.tspin:
                if self.sealTimer>0:
                    pygame.mixer.Sound.play(data.sealRec)
                    
                self.sealTimer=0
                self.sealOpacity-=48
            if self.sealTimer<0:
                self.sealTimer=0
        if self.sealOpacity<=0:
            self.sealOpacity=0
            self.sealTimer=None

    def updateMode(self,dt,data):
        if self.mode=="standard":
            self.linesRemaining -= self.lines
            self.lines = 0
            if self.linesRemaining <= 0:
                self.level += 1
                data.gravity -= 25
                self.linesRemaining = min(self.level * 10, max(100, (self.level * 10) - 50))
        elif self.mode=="ultra" and not (data.paused or data.gameOver):
            self.remainingTime-=dt
            if self.remainingTime<=0:
                data.gameOver=True
                self.remainingTime=0
        elif self.mode=="sprint" and not (data.paused or data.gameOver):
            self.timeElapsed+=dt
            self.linesRemaining-= self.lines
            self.lines=0
            if self.linesRemaining<=0:
                if self.highScore==-1 or self.timeElapsed<self.highScore:
                    self.setHighScore()
                data.gameOver=True

    def animate(self,dt):
        self.animTrack += dt
        self.comboTrack += dt
        if self.animTrack > self.animDelay:
            self.animTrack = 0
            self.backAnim = (self.backAnim + 1) % len(self.backdrop)
        if self.comboTrack > self.comboDelay:
            self.comboTrack = 0
            self.comboAnim = (self.comboAnim + 1) % len(self.rainbow)
        self.image=self.oImage.copy()
        self.overlay=self.oOverlay.copy()

    def update(self,dt,data):
        if not data.paused or data.gameOver:
            self.countdownTimer += dt
        if (not (data.paused or data.gameOver) and
            self.countdownTimer>self.countdown):
            self.updateMode(dt, data)
            self.unseal(dt,data)
            self.clearRows(data)
        self.animate(dt)
        if (data.gameOver and
            self.highScore==self.score and
            (data.mode=="standard" or
             data.mode=="ultra")):
            self.setHighScore()

    def drawScoreboard(self,screen):
        white=(255,255,255)
        black=(0,0,0)
        pygame.draw.rect(screen,black,self.scoreboard)
        font=pygame.font.Font("fonts/Pixeled.ttf",8)
        color=self.rainbow[self.comboAnim]
        if self.highScore<0:
            highScore="NaN"
        elif self.mode!="sprint":
            highScore="%d"%self.highScore
        else:
            minutes="%d"%(self.highScore//60000)
            seconds=(self.highScore%60000)//1000
            if seconds<10:
                seconds="0%d"%seconds
            else:
                seconds="%d"%seconds
            highScore="%s:%s"%(minutes,seconds)
        scoreDisp=font.render("High Score:%s"%highScore,True,color)
        screen.blit(scoreDisp,(self.x+5,self.y-18))
        if self.mode=="standard":
            text=font.render("Level:%d"%self.level,True,white)
            text2=font.render("Lines Remaining:%d"%self.linesRemaining,True,white)
        elif self.mode=="sprint":
            minutes="%d"%(self.timeElapsed//60000)
            seconds=(self.timeElapsed%60000)//1000
            if seconds<10:
                seconds="0%d"%seconds
            else:
                seconds="%d"%seconds
            text=font.render("Time Elapsed:%s:%s"%(minutes,seconds),True,white)
            text2=font.render("Lines Cleared:%d/40"%self.linesCleared,True,white)
        elif self.mode=="ultra":
            minutes="%d"%(self.remainingTime//60000)
            seconds=(self.remainingTime%60000)//1000
            if seconds<10:
                seconds="0%d"%seconds
            else:
                seconds="%d"%seconds
            text=font.render("Time Remaining:%s:%s"%(minutes,seconds),True,white)
            if self.score!=self.highScore:
                color=white
            text2=font.render("Score:%d"%self.score,True,color)
        screen.blit(text,(self.x+5,self.y-45))
        screen.blit(text2,(self.x+5,self.y-32))

    def drawBuffs(self,screen):
        font=pygame.font.Font("fonts/Pixeled.ttf",11)
        if self.sealTimer!=None:
            magenta=(128,0,128)
            text=font.render("Sealed for %0.2f seconds"%(self.sealTimer/1000),True,magenta)
            w,h=text.get_size()
            screen.blit(text,(self.overX+self.overW-w-5,self.overY+self.overH-h-10))

    def drawCombo(self,screen):
        if self.combo>1:
            color=self.rainbow[self.comboAnim]
            font=pygame.font.Font("fonts/Pixeled.ttf",18)
            font.set_bold(True)
            text=font.render("Combo %d"%self.combo,True,color)
            w,h=text.get_size()
            blitAlpha(screen,text,
                      (self.x+(self.width-w)//2,self.y+(self.height-h)//2),128)

    def drawTimer(self,screen):
        yellow = (255, 255, 0)
        red = (255, 0, 0)
        font = pygame.font.Font('fonts/Pixeled.ttf', 72)
        time = roundHalfUp((self.countdown - self.countdownTimer) / 1000)
        if time != 0:
            text = font.render("%d" % time, True, yellow)
        else:
            if self.mode == "boss":
                text = font.render("FIGHT!", True, red)
            else:
                text = font.render("GO!", True, yellow)
        tW, tH = text.get_size()
        width, height = screen.get_size()
        screen.blit(text,((width-tW)//2,
                          (height-tH)//2))

    def draw(self,screen):
        if self.mode!="boss":
            screen.blit(self.backdrop[self.backAnim],(0,0))
        screen.blit(self.overlay,(self.overX,self.overY))
        screen.blit(self.image,(self.x,self.y))
        self.drawCombo(screen)
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c]!=0 and r>18:
                    # because grid[r][c]=0 means its empty and colors start at 0
                    color=self.grid[r][c]-1
                    screen.blit(self.blocks[color],
                                (self.x+(c*self.cellSize),self.y+((r+1)*self.cellSize)-self.height))
                    if self.sealTimer!=None:
                        blitAlpha(screen,self.blocks[8],
                                    (self.x+(c*self.cellSize),self.y+((r+1)*self.cellSize)-self.height),self.sealOpacity)
        self.drawBuffs(screen)
        if self.mode!="boss":
            self.drawScoreboard(screen)
        if self.countdownTimer<self.countdown:
            self.drawTimer(screen)