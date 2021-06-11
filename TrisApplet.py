# TrisApplet is our main that runs the game, It deals with all the menu-ing
# and mode setting for the entire game.

import pygame
import collections
import os
# Initialize Pygame
x = 0
y = 30
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
width=1368
height=842
fps=60
pygame.init()
screen=pygame.display.set_mode((width,height))
caption="Tris V.1.0"
pygame.display.set_caption(caption)
clock = pygame.time.Clock()

# loading screen so I can load ALL THE ASSETS!
font = pygame.font.Font("fonts/Pixeled.ttf", 32)
loading=font.render("Loading...",True,(255,255,255))
logo=pygame.image.load("images/logoLarge.png")
lW,lH=logo.get_size()
screen.blit(logo,((width-lW)//2,(height-lH)//2))
screen.blit(loading,(20,0))
pygame.display.flip()

from Matrix import Matrix
from Piece import Piece
from Piece import GhostPiece
import Enemy

def mousePressed(x, y):
    pass

def mouseReleased(x, y):
    pass

def mouseMotion(x, y):
    pass

def mouseDrag(x, y):
    pass

def isKeyPressed(key):
    return keys.get(key,False)

def keyPressed(keyCode,modifier):
    pass

def selectMode(menu,choice):
    pygame.mixer.Sound.play(data.select)
    # main menu
    if menu==0:
        # clicked 'start'
        if choice==0:
            data.menuMode=1
        # clicked 'options'
        elif choice==1:
            data.menuMode=2
        # clicked 'help'
        elif choice==2:
            data.mode="help"
            data.initHelp()
        # clicked 'credits'
        elif choice==3:
            data.mode="credits"
            data.initCredits()
        data.selection=0
    # tetris menu
    elif menu==1:
        # 15 level standard
        if choice==0:
            data.mode="standard"
            data.initTris(data.mode)
        # 40 line sprint
        elif choice==1:
            data.mode="sprint"
            data.initTris(data.mode)
        # 2-min ultra
        elif choice==2:
            data.mode='ultra'
            data.initTris(data.mode)
        # battle menu
        elif choice==3:
            data.menuMode=6
            data.selection=0
        # go back to main
        elif choice==4:
            data.menuMode=0
            data.selection=0
    # options menu WIP
    elif menu==2:
        # confirm changes
        if choice==-1:
            confirmSettings()
            data.menuMode=0
            data.selection=0
        # set defaults
        elif choice==0:
            data.tempSfx=.5
            data.tempBgm=.5
        # cancel changes
        elif choice==1:
            data.tempBgm=data.bgm
            data.tempSfx=data.sfx
            data.menuMode=0
            data.selection=0
    # pause screen menu
    elif menu==3:
        # resume
        if choice==0:
            data.paused=False
            pygame.mixer.music.unpause()
        # restart
        elif choice==1:
            if data.mode!="boss":
                data.initTris(data.mode)
            else:
                data.initBoss(data.bossName)
        # quit to menu
        if choice==2:
            data.initMenu()
    # game over menu
    elif menu==4:
        # restart
        if choice==0:
            if data.mode!="boss":
                data.initTris(data.mode)
            else:
                data.initBoss(data.bossName)
        elif choice==1:
            # boss select
            if data.mode=="boss":
                data.initMenu()
                data.menuMode=6
                data.selection=0
            else:
                data.initMenu()
        # quit to main menu
        elif choice==2:
            data.initMenu()
    # Boss win menu
    elif menu==5:
        if choice==0:
            data.initBoss(data.bossName)
        elif choice==1:
            data.initMenu()
            data.menuMode=6
        elif choice==2:
            data.initMenu()
    # Challenge select screen
    elif menu==6:
        # battle morpho
        if choice==0:
            data.initBoss("morphoKnight")
        # battle boss 2
        elif choice==1:
            data.menuMode=1 #temporary
            data.selection=0
        # go back
        else:
            data.menuMode=1
            data.selection=0
    # Active select screen
    elif menu==7:
        pass


def keyPressedMenu(keyCode,modifier):
    if keyCode==pygame.K_UP:
        if data.selection>0:
            pygame.mixer.Sound.play(data.select)
            data.selection-=1
    if keyCode==pygame.K_DOWN:
        if ((data.menuMode==0 and data.selection<3) or
            (data.menuMode==1 and data.selection<4) or
            (data.menuMode==2 and data.selection<2) or
            (data.menuMode==6 and data.selection<1)):
                pygame.mixer.Sound.play(data.select)
                data.selection+=1
    if keyCode==pygame.K_LEFT:
        # hovering over confirm/default/cancel
        if data.menuMode==2 and data.selection==2:
            if data.subSelect>-1:
                pygame.mixer.Sound.play(data.select)
                data.subSelect-=1
    if keyCode==pygame.K_RIGHT and data.selection==2:
        # hovering over confirm/default/cancel
        if data.menuMode==2:
            if data.subSelect<1:
                pygame.mixer.Sound.play(data.select)
                data.subSelect+=1
    if keyCode==pygame.K_RETURN:
        if data.menuMode==2:
            selectMode(data.menuMode,data.subSelect)
        else:
            selectMode(data.menuMode,data.selection)
    if keyCode==pygame.K_ESCAPE or keyCode==pygame.K_BACKSPACE:
        if data.menuMode!=0:
            pygame.mixer.Sound.play(data.deselect)
            data.menuMode=0
            data.selection=0

def keyPressedHelp(keyCode,modifier):
    if keyCode==pygame.K_LEFT:
        if data.currPage>0:
            pygame.mixer.Sound.play(data.select)
            data.currPage-=1
    if keyCode==pygame.K_RIGHT:
        if data.currPage<6:
            pygame.mixer.Sound.play(data.select)
            data.currPage+=1
    if keyCode==pygame.K_ESCAPE:
        data.initMenu()

def keyPressedTris(keyCode, modifier):
    if (not (data.gameOver or data.paused) and
        data.board.countdownTimer>data.board.countdown):
        if keyCode==pygame.K_LEFT:
            data.piece.move(data,-1,0)
        if keyCode==pygame.K_RIGHT:
            data.piece.move(data,1,0)
        if keyCode==pygame.K_DOWN:
            data.piece.move(data,0,1)
        if keyCode==pygame.K_z:
            if not data.piece.rotateCounterClockwise(data):
                data.piece.wallKick(data,"CCW")
        if keyCode==pygame.K_x:
            if not data.piece.rotateClockwise(data):
                data.piece.wallKick(data,"CW")
        if keyCode==pygame.K_SPACE:
            data.piece.drop(data)
        if keyCode==pygame.K_LCTRL:
            hold()
        if (keyCode==pygame.K_c and data.skillC!=None and
            data.skillC["type"]=="Active"):
            if  data.skillC["opacity"]==256 and data.skillC["effect"]():
                pygame.mixer.Sound.play(data.useActive)
                
                data.skillC["timer"]=0
                data.skillC["opacity"]=128
            else:
                pygame.mixer.Sound.play(data.activeFailed)
                
        if (keyCode==pygame.K_v and data.skillV!=None and
            data.skillV["type"]=="Active"):
            if  data.skillV["opacity"]==256 and data.skillV["effect"]():
                pygame.mixer.Sound.play(data.useActive)
                
                data.skillV["timer"] = 0
                data.skillV["opacity"] = 128
            else:
                pygame.mixer.Sound.play(data.activeFailed)
                
    if data.paused or data.gameOver:
        if keyCode==pygame.K_DOWN:
            if data.selection<2 and data.paused:
                pygame.mixer.Sound.play(data.select)
                data.selection+=1
            elif data.selection<2 and data.gameOver and data.mode=="boss":
                pygame.mixer.Sound.play(data.select)
                data.selection += 1
            elif data.selection<1 and data.gameOver:
                pygame.mixer.Sound.play(data.select)
                data.selection+=1
        if keyCode==pygame.K_UP:
            if data.selection>0:
                pygame.mixer.Sound.play(data.select)
                
                data.selection-=1
        if keyCode==pygame.K_RETURN:
            if data.paused:
                selectMode(3,data.selection)
            if data.gameOver:
                selectMode(4,data.selection)

    if keyCode==pygame.K_ESCAPE and not data.gameOver:
        if data.paused:
            pygame.mixer.Sound.play(data.deselect)
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.Sound.play(data.select)
            pygame.mixer.music.pause()
        data.paused=not data.paused
        data.board.countdownTimer = 0
        data.selection=0

def keyPressedBoss(keyCode,modifier):
    if data.boss.opacity!=0:
        keyPressedTris(keyCode,modifier)
    else:
        if keyCode==pygame.K_UP and data.selection>0:
            pygame.mixer.Sound.play(data.select)
            data.selection-=1
        if keyCode==pygame.K_DOWN and data.selection<2:
            pygame.mixer.Sound.play(data.select)
            data.selection+=1
        if keyCode==pygame.K_RETURN:
            pygame.mixer.Sound.play(data.select)
            data.menuMode=5
            selectMode(data.menuMode,data.selection)

def keyPressed(keycode,modifier):
    if data.mode=="menu":
        keyPressedMenu(keycode,modifier)
    elif data.mode=="help":
        keyPressedHelp(keycode,modifier)
    elif data.mode=="credits":
        if keycode==pygame.K_ESCAPE:
            data.mode="menu"
    elif(data.mode=="standard" or
         data.mode=="sprint" or
         data.mode=="ultra"):
        keyPressedTris(keycode,modifier)
    elif data.mode=="boss":
        keyPressedBoss(keycode,modifier)

def keyReleased(keyCode, modifier):
    pass

def timerFiredMenu(dt):
    data.currFrame=(data.currFrame+1)%len(data.menuAnim)
    if data.menuMode==2:
        pygame.mixer.music.set_volume(data.tempBgm)
        for sound in data.sounds:
            sound.set_volume(data.tempSfx)
        if data.selection!=2:
            data.subSelect=0
        if isKeyPressed(pygame.K_LEFT):
            if data.selection==0 and data.tempBgm>0:
                data.tempBgm-=0.01
            elif data.selection==1 and data.tempSfx>0:
                data.tempSfx-=0.01
        if isKeyPressed(pygame.K_RIGHT):
            if data.selection==0 and data.tempBgm<1:
                data.tempBgm+=0.01
            elif data.selection==1 and data.tempSfx<1:
                data.tempSfx+=0.01
    else:
        pygame.mixer.music.set_volume(data.bgm)
        for sound in data.sounds:
            sound.set_volume(data.sfx)


def timerFiredTris(dt):
    data.board.update(dt, data)
    data.ghostPiece.update(dt, isKeyPressed, data)
    updateQueue()
    if (not (data.gameOver or data.paused) and
        data.board.countdownTimer>data.board.countdown):
        data.piece.update(dt, isKeyPressed, data)
        data.gravTimer+=dt
        if data.gravTimer>=data.gravity:
            data.piece.move(data,0,1)
            data.gravTimer-=data.gravity
        updateActives(dt)
    if data.gameOver:
        pygame.mixer.music.stop()

def updateActives(dt):
    if (data.skillC != None and
            data.skillC["type"] == "Active" and
            data.skillC["timer"] < data.skillC["cooldown"]):
        data.skillC["timer"] += dt
        if data.skillC["timer"] >= data.skillC["cooldown"]:
            data.skillC["timer"] = data.skillC["cooldown"]
            pygame.mixer.Sound.play(data.activeUp)
            
            data.skillC["opacity"] = 256
    if (data.skillV != None and
            data.skillV["type"] == "Active" and
            data.skillV["timer"] < data.skillV["cooldown"]):
        data.skillV["timer"] += dt
        if data.skillV["timer"] >= data.skillV["cooldown"]:
            data.skillV["timer"] = data.skillV["cooldown"]
            pygame.mixer.Sound.play(data.activeUp2)
            
            data.skillV["opacity"] = 256

def updateQueue():
    # the calculations in this seem arbitrary because the locations are
    # relative to the board overlay rather than the board
    while len(data.pieceQueue) < 6:
        if len(data.pieceQueue) == 0:
            data.pieceQueue.append(Piece(0,0))
        else:
            data.pieceQueue.append(Piece(0,0))
            if data.pieceQueue[len(data.pieceQueue)-1].base==Piece.OPiece:
                r=28.5+(len(data.pieceQueue)*2.5)
            else:
                r=30+(len(data.pieceQueue)*2.5)-(len(data.pieceQueue[-1].base)/2)
            data.pieceQueue[len(data.pieceQueue)-1].r=r
        c=(data.board.cols+11)-(len(data.pieceQueue[len(data.pieceQueue)-1].base[0])/2)
        data.pieceQueue[len(data.pieceQueue)-1].c=c
        # correct for popped pieces
        if(data.pieceQueue[0].base==Piece.OPiece and
           data.pieceQueue[0].r!=30):
            data.pieceQueue[0].r=30
            for i in range(1,len(data.pieceQueue)-1):
                data.pieceQueue[i].r-=2.5
        elif(data.pieceQueue[0].base!=Piece.OPiece and
             data.pieceQueue[0].r != 31.5-(len(data.pieceQueue[0].base)/2)):
            data.pieceQueue[0].r=31.5-(len(data.pieceQueue[0].base)/2)
            for i in range(1,len(data.pieceQueue)-1):
                data.pieceQueue[i].r-=2.5

def timerFiredBoss(dt):
    if not data.boss.killed:
        timerFiredTris(dt)
    data.boss.update(dt,data)

def timerFired(dt):
    if data.mode=="menu":
        timerFiredMenu(dt)
    if data.mode=="credits":
        if not isKeyPressed(pygame.K_UP):
            data.timer-=1
        if isKeyPressed(pygame.K_DOWN):
            data.timer-=10
        if isKeyPressed(pygame.K_UP) and data.timer<0:
            data.timer+=10
        if data.timer<-8250:
            data.mode="menu"
    elif (data.mode=="standard" or
        data.mode=="sprint" or
        data.mode=="ultra"):
        timerFiredTris(dt)
    elif data.mode=="boss":
        timerFiredBoss(dt)

def blitAlpha(target, source, location, opacity):
    x = location[0]
    y = location[1]
    temp = pygame.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)
    target.blit(temp, location)

def drawGameOver(screen):
    white = (255, 255, 255)
    gray = (128, 128, 128)
    darkGray = (64, 64, 64)
    red=(255,0,0)
    window = pygame.Rect(width//4,height//4,width//2,height//2)
    pygame.draw.rect(screen, darkGray, window)
    if data.mode!="boss":
        colors = [gray, gray]
        colors[data.selection]=white
        font = pygame.font.Font("fonts/Pixeled.ttf", 32)
        message = font.render("Game Over!", True, red)
        mW, mH = message.get_size()
        hiColor = data.board.rainbow[data.board.comboAnim]
        font = pygame.font.Font("fonts/Pixeled.ttf", 24)
        if data.mode=="standard" or data.mode=="ultra":
            score=font.render("Final Score: %d"%data.board.score,True,white)
            highScore=font.render("High Score: %d"%data.board.highScore,True,hiColor)
            if data.board.score==data.board.highScore and data.board.score!=0:
                score=font.render("NEW HIGH SCORE",True,hiColor)
        elif data.mode=="sprint":
            # time score
            if data.board.linesRemaining<=0:
                minutes = "%d" % (data.board.timeElapsed // 60000)
                seconds = (data.board.timeElapsed % 60000) // 1000
                if seconds < 10:
                    seconds = "0%d" % seconds
                else:
                    seconds = "%d" % seconds
                scoreR = "%s:%s" % (minutes, seconds)
            else:
                scoreR="NaN"
            # time high score
            if data.board.highScore==-1:
                scoreH="NaN"
            else:
                minutesH = "%d" % (data.board.highScore // 60000)
                secondsH = (data.board.highScore % 60000) // 1000
                if secondsH < 10:
                    secondsH = "0%d" % secondsH
                else:
                    secondsH = "%d" % secondsH
                scoreH = "%s:%s" % (minutesH, secondsH)
            score=font.render("Final Score: %s"%scoreR,True,white)
            highScore=font.render("High Score: %s"%scoreH,True,hiColor)
            if data.board.highScore<data.board.timeElapsed and data.board.linesRemaining<=0:
                score = font.render("NEW HIGH SCORE", True, hiColor)
                highScore=font.render("High Score: %s"%scoreR,True,hiColor)
    else:
        colors=[gray,gray,gray]
        colors[data.selection]=white
        font = pygame.font.Font("fonts/Pixeled.ttf", 24)
    restart = font.render("Play Again", True, colors[0])
    rW, rH = restart.get_size()
    if data.mode=="boss":
        message=font.render("You have fallen...",True,red)
        mW, mH = message.get_size()
        restart = font.render("Try Again", True, colors[0])
        rW, rH = restart.get_size()
        select=font.render("Select Challenge",True,colors[1])
        sW,sH=select.get_size()
        end = font.render("Quit", True, colors[2])
        eW, eH = end.get_size()
        screen.blit(message,((width-mW)//2,(height-mH)*6//20))
        screen.blit(select,((width-sW)//2,((height-sH)*11//20)))
        screen.blit(restart,((width-rW)//2,(height-rH)*9//20))
    else:
        sW, sH = score.get_size()
        hW, hH = highScore.get_size()
        end = font.render("Quit", True, colors[1])
        eW, eH = end.get_size()
        screen.blit(score,((width-sW)//2,((height-sH)*8//20)))
        screen.blit(highScore,((width-hW)//2,((height-hH)*9//20)))
        screen.blit(message, ((width - mW) // 2, ((height - mH) * 6 // 20)))
        screen.blit(restart, ((width - rW) // 2, ((height - rH) * 11 // 20)))

    screen.blit(end, ((width - eW) // 2, ((height - eH) * 13 // 20)))

def redrawAllMenu(screen):
    white=(255,255,255)
    gray=(64,64,64)
    red=(255,0,0)
    darkRed=(128,0,0)
    screen.blit(data.menuAnim[data.currFrame],(0,0))
    font = pygame.font.Font("fonts/Pixeled.ttf", 15)
    font.set_bold(True)
    if data.menuMode!=6:
        imW,imH=data.logo.get_size()
        screen.blit(data.logo,((width-imW)//2,(height-imH)*1//4))
    if data.menuMode==0:
        colors=[gray,gray,gray,gray,gray]
        colors[data.selection]=white
        start = font.render("Start", True, colors[0])
        sW,sH=start.get_size()
        options = font.render("Options", True, colors[1])
        oW,oH=options.get_size()
        help = font.render("Help", True, colors[2])
        hW,hH=help.get_size()
        credits = font.render("Credits", True, colors[3])
        cW,cH=credits.get_size()
        screen.blit(start,((width-sW)//2,(height-sH)*13//20))
        screen.blit(options,((width-oW)//2,(height-oH)*14//20))
        screen.blit(help,((width-hW)//2,(height-hH)*15//20))
        screen.blit(credits,((width-cW)//2,(height-cH)*16//20))
    elif data.menuMode==1:
        colors=[gray,gray,gray,darkRed,gray]
        colors[data.selection]=white if colors[data.selection]==gray else red
        standard=font.render("Standard",True,colors[0])
        sW, sH = standard.get_size()
        sprint=font.render("Sprint", True, colors[1])
        pW,pH=sprint.get_size()
        ultra=font.render("Ultra", True, colors[2])
        uW,uH=ultra.get_size()
        boss=font.render("Battle",True,colors[3])
        bW,bH=boss.get_size()
        back=font.render("Back",True,colors[4])
        rW,rH=back.get_size()
        screen.blit(standard,((width-sW)//2,(height-sH)*13//20))
        screen.blit(sprint,((width-pW)//2,(height-pH)*14//20))
        screen.blit(ultra,((width-uW)//2,(height-uH)*15//20))
        screen.blit(boss,((width-bW)//2,(height-bH)*16//20))
        screen.blit(back,((width-rW)//2,(height-rH)*17//20))
    elif data.menuMode==2:
        colors=[gray,gray,[gray,gray,gray]]
        if data.selection!=2:
            colors[data.selection]=white
        else:
            colors[2][data.subSelect+1]=white
        bgm=font.render("BGM: %d"%(data.tempBgm*100),True,colors[0])
        bW,bH=bgm.get_size()
        sfx=font.render("SFX: %d"%(data.tempSfx*100),True,colors[1])
        sW,sH=sfx.get_size()
        confirm=font.render("Confirm",True,colors[2][0])
        cW,cH=confirm.get_size()
        default=font.render("Default",True,colors[2][1])
        dW,dH=default.get_size()
        cancel=font.render("Cancel",True,colors[2][2])
        eW,eH=cancel.get_size()
        screen.blit(bgm,((width-bW)//2,(height-bH)*12//20))
        screen.blit(sfx,((width-sW)//2,(height-sH)*14//20))
        screen.blit(confirm,((width-cW-dW)*13//30,(height-cH)*16//20))
        screen.blit(default,((width-dW)//2,(height-dH)*16//20))
        screen.blit(cancel,((width-eW+dW)*11//20,(height-eH)*16//20))
    elif data.menuMode==6:
        darkYellow=(128,128,0)
        yellow=(255,255,0)
        colors=[gray,gray]
        colors[data.selection]=white
        # boss list
        if "morphoKnight" in data.bossTracker:
            colors[0] = darkYellow
            if data.selection == 0:
                colors[0]=yellow
        morpho=font.render("Morpho Knight",True,colors[0])
        mW,mH=morpho.get_size()

        # go back and assist menu
        back=font.render("Back",True,colors[1])
        bW,bH=back.get_size()
        screen.blit(morpho,((width-mW)//2,(height-mH)*4//6))
        screen.blit(back,((width-bW)//2,(height-bH)*5//6))


def redrawAllHelp(screen):
    if data.currPage==0:
        img=data.help
    elif data.currPage==1:
        img = data.help1
    elif data.currPage==2:
        img = data.help2
    elif data.currPage==3:
        img = data.help3
    elif data.currPage==4:
        img = data.help4
    elif data.currPage==5:
        img = data.help5
    elif data.currPage==6:
        img = data.help6
    w,h=img.get_size()
    screen.blit(img,((width-w)//2,(height-h)//2))

def drawSkills(screen):
    black=(0,0,0)
    white=(255,255,255)
    if data.skillC != None:
        if data.skillC["timer"]!=data.skillC["cooldown"]:
            w,h=data.skillC["dim"]
            x,y=data.skillC["loc"]
            pygame.draw.rect(screen,black,(x-10,y+h,5,-h))
            pygame.draw.rect(screen,white,(x-10,y+h,5,
                                           -h*data.skillC["timer"]/data.skillC["cooldown"]))
        blitAlpha(screen,data.skillC["image"],
                  data.skillC["loc"],
                  data.skillC["opacity"])
    if data.skillV != None:
        if data.skillV["timer"]!=data.skillV["cooldown"]:
            w, h = data.skillV["dim"]
            x, y = data.skillV["loc"]
            pygame.draw.rect(screen,black,(x-10,y+h,5,-h))
            pygame.draw.rect(screen,white,(x-10,y+h,5,
                                           -h*data.skillV["timer"]/data.skillV["cooldown"]))
        blitAlpha(screen,data.skillV["image"],
                  data.skillV["loc"],
                  data.skillV["opacity"])

def drawPauseScreen(screen):
    white=(255,255,255)
    gray=(128,128,128)
    darkGray=(64,64,64)
    window=pygame.Rect(width//4,height//4,width//2,height//2)
    pygame.draw.rect(screen,darkGray,window)
    colors=[gray,gray,gray]
    colors[data.selection]=white
    font = pygame.font.Font("fonts/Pixeled.ttf", 32)
    message=font.render("Game is Paused!",True,white)
    mW,mH=message.get_size()
    font = pygame.font.Font("fonts/Pixeled.ttf", 24)
    resume=font.render("Resume",True,colors[0])
    rW,rH=resume.get_size()
    restart=font.render("Restart",True,colors[1])
    tW,tH=restart.get_size()
    end=font.render("Quit",True,colors[2])
    eW,eH=end.get_size()
    screen.blit(message,((width-mW)//2,((height-mH)*6//20)))
    screen.blit(resume,((width-rW)//2,((height-rH)*9//20)))
    screen.blit(restart,((width-tW)//2,((height-tH)*11//20)))
    screen.blit(end,((width-eW)//2,((height-eH)*13//20)))

def redrawAllTris(screen):
    data.piece.draw(data.board.image)
    data.ghostPiece.draw(data.board.image)
    if data.heldPiece!=None:
        data.heldPiece.draw(data.board.overlay)
    for piece in data.pieceQueue:
        piece.draw(data.board.overlay)
    drawSkills(data.board.overlay)
    data.board.draw(screen)
    if data.paused:
        drawPauseScreen(screen)
    if data.gameOver:
        drawGameOver(screen)

def drawVictory(screen):
    white = (255, 255, 255)
    gray = (128, 128, 128)
    darkGray = (64, 64, 64)
    yellow = (255, 255, 0)
    window = pygame.Rect(width // 4, height // 4, width // 2, height // 2)
    pygame.draw.rect(screen, darkGray, window)
    font = pygame.font.Font("fonts/Pixeled.ttf", 32)
    message = font.render("You defeated", True, yellow)
    mW,mH=message.get_size()
    font = pygame.font.Font("fonts/Pixeled.ttf", 24)
    name=font.render(data.boss.name,True,yellow)
    nW,nH=name.get_size()
    colors=[gray,gray,gray]
    colors[data.selection]=white
    restart = font.render("Play Again", True, colors[0])
    rW, rH = restart.get_size()
    select=font.render("Choose Challenge",True,colors[1])
    sW,sH=select.get_size()
    end = font.render("Quit", True, colors[2])
    eW, eH = end.get_size()
    screen.blit(message,((width-mW)//2,((height-mH)*6//20)))
    screen.blit(name,((width-nW)//2,((height-nH)*8//20)))
    screen.blit(restart,((width-rW)//2,((height-rH)*10//20)))
    screen.blit(select,((width-sW)//2,((height-sH)*12//20)))
    screen.blit(end,((width-eW)//2,((height-eH)*14//20)))

def redrawAllBoss(screen):
    data.boss.draw(screen)
    redrawAllTris(screen)
    if data.boss.opacity==0:
        drawVictory(screen)

def redrawAll(screen):
    screen.fill((0,0,0))
    if data.mode=="menu":
        redrawAllMenu(screen)
    elif data.mode=="help":
        redrawAllHelp(screen)
    elif data.mode=="credits":
        if data.timer>-7750:
            screen.blit(data.credits, (0, data.timer))
        else:
            screen.blit(data.credits,(0,-7750))
    elif   (data.mode=="standard" or
            data.mode=="ultra" or
            data.mode=="sprint"):
        redrawAllTris(screen)
    elif data.mode=="boss":
        redrawAllBoss(screen)
    pygame.display.flip()

def hold():
    if not data.hasHeld:
        pygame.mixer.Sound.play(data.holdSound)
        
        if data.heldPiece==None:
            data.heldPiece=data.piece
            data.piece=data.pieceQueue.popleft()
        else:
            data.heldPiece,data.piece=data.piece,data.heldPiece
        data.heldPiece.c=4-(len(data.heldPiece.shape)/2)
        data.heldPiece.r=31.5-(len(data.heldPiece.shape[0])/2)
        data.heldPiece.shape = data.heldPiece.base
        data.heldPiece.rotateState = 0
        if len(data.piece.base)%2==1:
            data.piece.c = (data.board.cols // 2) - ((len(data.piece.base) // 2)+1)
        else:
            data.piece.c = (data.board.cols // 2) - (len(data.piece.base) // 2)
        data.piece.r = 18
        data.hasHeld=True

def confirmSettings():
    data.bgm=data.tempBgm
    data.sfx=data.tempSfx
    os.rename('records.txt', 'input.txt')
    with open('input.txt', 'r') as inputFile, open('records.txt', 'w') as outputFile:
        for line in inputFile:
            if line.startswith("bgm"):
                outputFile.write("bgm:%f\n"%data.bgm)
            elif line.startswith("sfx"):
                outputFile.write("sfx:%f\n"%data.sfx)
            else:
                outputFile.write(line)
    os.remove('input.txt')

class Data(object):
    def initResources(self):
        # menu resources
        data.logo=pygame.image.load('images/logo.png').convert_alpha()
        sheet = pygame.image.load('images/menuBack.png').convert_alpha()
        rows, cols = 4, 8
        width, height = sheet.get_size()
        cellWidth, cellHeight = width / cols, height / rows
        data.menuAnim = []
        data.bossTracker=set()
        for i in range(rows):
            for j in range(cols):
                subImage = sheet.subsurface((j * cellWidth, i * cellHeight, cellWidth, cellHeight))
                data.menuAnim.append(subImage)
        # records
        try:
            with open("records.txt", 'r') as f:
                for line in f:
                    if line.startswith("bgm"):
                        data.bgm = float(line.split(":")[1])
                    elif line.startswith("sfx"):
                        data.sfx = float(line.split(":")[1])
                    elif line.startswith("m#&p=9nez"):
                        data.bossTracker.add("morphoKnight")
        except IOError:
            f = open("records.txt", 'w')
            f.write("standard:0\n"
                    "sprint:-1\n"
                    "ultra:0\n"
                    "bgm:0.5\n"
                    "sfx:0.5\n")
            data.bgm = 1
            data.sfx = 1
        # actions
        data.sounds=set()
        data.select=pygame.mixer.Sound('music/select.ogg')
        data.sounds.add(data.select)
        data.deselect=pygame.mixer.Sound('music/deselect.ogg')
        data.sounds.add(data.deselect)
        data.move=pygame.mixer.Sound('music/move.ogg')
        data.sounds.add(data.move)
        data.holdSound=pygame.mixer.Sound('music/hold.ogg')
        data.sounds.add(data.holdSound)
        data.rowClear=pygame.mixer.Sound('music/rowClear.ogg')
        data.sounds.add(data.rowClear)
        data.place=pygame.mixer.Sound('music/place.ogg')
        data.sounds.add(data.place)
        data.rotate=pygame.mixer.Sound('music/rotate.ogg')
        data.sounds.add(data.rotate)
        data.tspinSound=pygame.mixer.Sound('music/tspin.ogg')
        data.sounds.add(data.tspinSound)
        data.perfectClear=pygame.mixer.Sound('music/perfectClear.ogg')
        data.sounds.add(data.perfectClear)
        data.bomb=pygame.mixer.Sound('music/bomb.ogg')
        data.sounds.add(data.bomb)
        # hazards
        data.garbage=pygame.mixer.Sound('music/garbage.ogg')
        data.sounds.add(data.garbage)
        data.whirlwind=pygame.mixer.Sound('music/whirlwind.ogg')
        data.sounds.add(data.whirlwind)
        data.seal=pygame.mixer.Sound('music/seal.ogg')
        data.sounds.add(data.seal)
        data.sealRec=pygame.mixer.Sound('music/rowSealRec.ogg')
        data.sounds.add(data.sealRec)
        data.sealClear=pygame.mixer.Sound('music/sealHeal.ogg')
        data.sounds.add(data.sealClear)
        # skills
        data.activeUp=pygame.mixer.Sound('music/activeUp.ogg')
        data.sounds.add(data.activeUp)
        data.activeUp2=pygame.mixer.Sound('music/activeUp2.ogg')
        data.sounds.add(data.activeUp2)
        data.useActive=pygame.mixer.Sound('music/useActive.ogg')
        data.sounds.add(data.useActive)
        data.activeFailed=pygame.mixer.Sound('music/failActive.ogg')
        data.sounds.add(data.activeFailed)
        data.clearFourImage=pygame.image.load('images/clearFour.png').convert_alpha()
        data.sealClearImage=pygame.image.load('images/recover.png').convert_alpha()
        # boss defaults
        data.death = pygame.mixer.Sound('music/death.ogg')
        data.sounds.add(data.death)
        data.recieveDmg = pygame.mixer.Sound('music/recieveDmg.ogg')
        data.sounds.add(data.recieveDmg)
        data.timerChange = pygame.mixer.Sound('music/timerChange.ogg')
        data.sounds.add(data.timerChange)
        # data.skill = pygame.mixer.Sound('music/skill.ogg')
        # data.skill.set_volume(data.sfx)
        for sound in data.sounds:
            sound.set_volume(data.sfx)
    def initMenu(self):
        data.currFrame=0
        data.menuTheme = pygame.mixer.music.load('music/menu.ogg')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(data.bgm)
        data.mode = "menu"
        # 0 main, 1 tris mode select, 2 option menu
        data.menuMode=0
        # 0 start (standard, sprint, ultra, boss), 1 options, 2 help, 3 credits menu
        data.selection=0
        # 0 standard 1 sprint 2 ultra 3 boss
        data.subSelect=0
        data.tempBgm=data.bgm
        data.tempSfx=data.sfx
    def initHelp(self):
        data.currPage=0
        data.helpMusic=pygame.mixer.music.load('music/help.ogg')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(data.bgm)
        data.help=pygame.image.load('images/help.png')
        data.help1=pygame.image.load('images/basics.png').convert_alpha()
        data.help2=pygame.image.load('images/modes.png').convert_alpha()
        data.help3=pygame.image.load('images/techniques.png').convert_alpha()
        data.help4=pygame.image.load('images/actives.png').convert_alpha()
        data.help5=pygame.image.load('images/states.png').convert_alpha()
        data.help6=pygame.image.load('images/sendOff.png').convert_alpha()
    def initCredits(self):
        data.credits=pygame.image.load('images/credits.png').convert_alpha()
        data.timer=0

    def initTris(self,mode):
        data.mode=mode
        pygame.mixer.music.load('music/korobeiniki.ogg')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(data.bgm)
        Piece.newBag()
        data.board = Matrix(width // 2, height // 2, data.mode)
        data.piece = Piece((data.board.cols) // 2, 18)
        data.ghostPiece = GhostPiece(data.piece)
        data.pieceQueue = collections.deque()
        data.heldPiece = None
        data.hasHeld = False
        data.gravity = 500
        data.gravTimer = 0
        data.tspin = False
        data.endCombo = False
        # non-gameplay stats
        data.gameOver = False
        data.paused=False
        data.selection=0

        clearFour = {
            'name': "Big Bang",
            'image': data.clearFourImage,
            'dim': data.clearFourImage.get_size(),
            'description': "Clears the top four lines with blocks",
            'type': "Active",
            'effect': lambda:data.board.clear(data,4),
            'cooldown': 15000,
            'timer': 0,
            'opacity':128
                    }

        sealClear = {
            'name': "Healing Water",
            'image': data.sealClearImage,
            'dim': data.sealClearImage.get_size(),
            'description': "Removes sealed status",
            'type': "Active",
            'effect': lambda:data.board.removeSeal(data),
            'cooldown': 20000,
            'timer':0,
            'opacity':128
                    }

        #In Development
        shiftLeft = {
            'name': "Earth Gauntlets",
            'image': None,
            'dim': None,
            'description': "Shifts rows to the left side",
            'type': "Active",
            'effect':None,
            'cooldown': 20000,
            'timer':0,
            'opacity':128
                    }
        slotMachine =   {
            'name': 'Roulette Machine',
            'image': None,
            'dim': None,
            'description': 'Increases chance of roulette tetrominos',
            'type':"Passive",
            'effect':None
                        }
        sealer =    {
            'name': 'Starchains of Andromeda',
            'image': None,
            'dim':None,
            'description':'Seals the board for 5 seconds',
            'type':'Active',
            'effect':lambda:data.board.setSeal(data,5000),
            'cooldown':10000,
            'timer':0,
            'opacity':128
                    }
        extraLife=  {
            'name': 'Soul Heart',
            'image':None,
            'dim':None,
            'description':'Grants an extra chance at life',
            'type':'Passive',
            'effect':None
                    }
        gravity=    {
            'name': 'Heaven Render',
            'image':None,
            'dim':None,
            'description':'Deals damage to enemies',
            'type':'Active',
            'cooldown':50000,
            'timer':0,
            'opacity':128
                    }

        data.skillC=clearFour
        data.skillV=sealClear
        if data.skillC!=None:
            data.skillC["loc"]=(24,160)
        if data.skillV!=None:
            data.skillV["loc"]=(24,256)
    def initBoss(self,boss):
        data.mode="boss"
        self.initTris(data.mode)
        data.board = Matrix(width // 2, height*2 // 3, data.mode)
        data.won=False
        data.bossName=boss
        if boss=="morphoKnight":
            data.boss=Enemy.BetaKnight()
        pygame.mixer.music.load(data.boss.music)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(data.bgm)

data=Data()
# Run Game
data.initResources()
data.initMenu()
running = True
keys = dict()
try:
    while running:
        time = clock.tick(fps)
        timerFired(time)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mousePressed(*(event.pos))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouseReleased(*(event.pos))
            elif (event.type == pygame.MOUSEMOTION and
                  event.buttons == (0, 0, 0)):
                mouseMotion(*(event.pos))
            elif (event.type == pygame.MOUSEMOTION and
                  event.buttons[0] == 1):
                mouseDrag(*(event.pos))
            elif event.type == pygame.KEYDOWN:
                keys[event.key] = True
                keyPressed(event.key, event.mod)
            elif event.type == pygame.KEYUP:
                keys[event.key] = False
                keyReleased(event.key, event.mod)
            elif event.type == pygame.QUIT:
                running = False
        redrawAll(screen)
    pygame.quit()
except pygame.error:
    print("%s crashed because <<%s>>"%(caption,pygame.get_error()))
    pygame.quit()