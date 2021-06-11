# Enemy.py contains all Boss enemy statistics. This could be done with a dictionary, but
# AI is much easier to determine by just hardcoding in an enemy's potential behaviors

import random
import pygame
import os
import math

def blitAlpha(target, source, location, opacity):
    x = location[0]
    y = location[1]
    temp = pygame.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)
    target.blit(temp, location)

class Enemy(pygame.sprite.Sprite):
    def __init__(self,hp,spriteSheet,backdrop):
        # display stats
        self.name="NaN"
        self.backdrop=backdrop
        self.backLength=len(self.backdrop)
        self.backFrame=0
        self.backTrack=0
        self.backDelay=1
        self.animation=spriteSheet
        self.animLength=len(self.animation)
        self.currentFrame=0
        self.frameTrack=0
        self.frameDelay=1
        self.width,self.height=self.animation[0].get_size()
        self.x=(1368//2)-(self.width//2)
        self.y=(842//4)-(self.height//2)
        self.opacity=256

        self.hpBar=pygame.Rect(self.x,self.y+self.height,self.width,30)
        self.hpBarFull=self.hpBar.copy()

        self.timeBar=pygame.Rect(self.x,self.y-10,self.width,10)
        self.timeFull=self.timeBar.copy()

        self.messages=[]
        # enemy stats
        self.hp=hp
        self.maxHP=self.hp
        self.resistance=1
        self.defense=False
        self.cooldown=0
        self.timer=0
        self.usedExe=False
        self.killed=False
        # battle stats
        self.damage=[]
        self.accDamage=[]
    def attack(self,data):
        data.board.garbage(data,1)
    def defend(self,data):
        if data.board.score>0 or data.board.lines>0:
            pygame.mixer.Sound.play(data.recieveDmg)
            
            if self.defense==True:
                self.damage.append(data.board.lines)
            else:
                self.damage.append(data.board.score)
            self.accDamage.append(0)
            data.board.score = 0
            data.board.lines = 0
    def animate(self,dt):
        self.frameTrack += dt
        self.backTrack += dt
        if self.frameTrack > self.frameDelay:
            self.frameTrack = 0
            self.currentFrame = (self.currentFrame + 1) % (self.animLength)
        if self.backTrack > self.backDelay:
            self.backTrack = 0
            self.backFrame = (self.backFrame + 1) % (self.backLength)

    def dealDamage(self,dt,data):
        i=0
        while i<len(self.damage):
            if self.damage[i] > 0:
                # we decrement hp at intervals of dmg/50 because all scores divisible by 50
                self.accDamage[i] += self.damage[i]/50
                self.hp -= self.damage[i]/50
                if self.accDamage[i] == self.damage[i]:
                    self.damage.pop(i)
                    self.accDamage.pop(i)
                    i=i-1
                self.hpBar = pygame.Rect(self.x, self.y + self.height,
                                         int(self.width * (self.hp / self.maxHP)), 30)
            i+=1

    def writeRecord(self,data):
        completed=False
        os.rename('records.txt', 'input.txt')
        with open('input.txt', 'r') as inputFile, open('records.txt', 'w') as outputFile:
            for line in inputFile:
                if line.startswith(self.secretName):
                    completed=True
                outputFile.write(line)
            if not completed:
                outputFile.write(self.secretName)
        os.remove('input.txt')

    def update(self,dt,data):
        if data.board.countdownTimer>data.board.countdown:
            self.animate(dt)
            if self.hp<1:
                if not self.killed:
                    pygame.mixer.Sound.play(data.death)
                    
                    pygame.mixer.music.fadeout(int(data.death.get_length()*1000))
                if self.opacity>0:
                    self.opacity-=(256/(data.death.get_length()*1000))*dt
                else:
                    self.opacity=0
                    self.writeRecord(data)
                self.killed=True
            elif not (data.gameOver or data.paused):
                self.timer += dt
                self.timeBar = pygame.Rect(self.x, self.y - 10,
                                           int(self.width * (1 - (self.timer / self.cooldown))), 10)
                if self.timer >= self.cooldown:
                    self.timer -= self.cooldown
                    self.attack(data)
                self.defend(data)
                self.dealDamage(dt,data)

    def draw(self,screen):
        black=(0,0,0)
        green=(0,255,0)
        red=(255,0,0)
        screen.blit(self.backdrop[self.backFrame],(0,0))
        if not self.killed:
            pygame.draw.rect(screen,black,self.timeFull)
            pygame.draw.rect(screen,red,self.timeBar)
            pygame.draw.rect(screen, black, self.hpBarFull)
            pygame.draw.rect(screen, green, self.hpBar)
            font = pygame.font.Font("fonts/Pixeled.ttf", 12)
            font.set_bold(True)
            text=font.render("%d/%d"%(self.hp,self.maxHP),True,red)
            screen.blit(text,(self.x+5,self.y+self.height))
        blitAlpha(screen, self.animation[self.currentFrame], (self.x, self.y), self.opacity)

class BetaKnight(Enemy):
    # enemy sprite
    sheet = pygame.image.load('images/bosses/betaknight.png').convert_alpha()
    rows, cols = 2,5
    width, height = sheet.get_size()
    cellWidth, cellHeight = width / cols, height / rows
    animation = []
    for i in range(rows):
        for j in range(cols):
            subImage = sheet.subsurface((j * cellWidth, i * cellHeight, cellWidth, cellHeight))
            animation.append(subImage)
    # backdrop
    sheet = pygame.image.load('images/bosses/betaknightbackdrop.png').convert_alpha()
    rows, cols = 2,4
    width, height = sheet.get_size()
    cellWidth, cellHeight = width / cols, height / rows
    backdrop = []
    for i in range(rows):
        for j in range(cols):
            subImage = sheet.subsurface((j * cellWidth, i * cellHeight, cellWidth, cellHeight))
            backdrop.append(subImage)
    def __init__(self):
        super().__init__(10000,BetaKnight.animation,BetaKnight.backdrop)
        self.name="Morpho Knight"
        self.secretName="m#&p=9nez"
        self.music='music/galacta2.ogg'
        self.defense=False
        self.cooldown=7000
        self.frameDelay=100
        self.backDelay=100
        self.resistance=100
    def attack(self,data):
        gen=random.randint(1,100)
        if self.hp<1000 and not self.usedExe:
            data.board.setSeal(data,50000)
            self.usedExe=True
        if self.hp<5000:
            if self.cooldown==7000:
                pygame.mixer.Sound.play(data.timerChange)
                self.cooldown=3500
            else:
                data.board.garbage(data,1)
        elif data.board.sealTimer==None:
            data.board.setSeal(data, 10000)
        else:
            data.board.whirlwind(data)
            if gen<20:
                data.board.garbage(data,4)
            else:
                data.board.garbage(data,1)