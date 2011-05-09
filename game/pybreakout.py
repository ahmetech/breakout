import pygame, math, time, soundmanager
import pygame.transform as transform
from pygame.locals import *
from utilities.common import Describer
from utilities.common import rm
from os.path import join
from sys import exit
from random import randrange,randint
import math
import os

RGB_BLACK     = 0,0,0
RGB_WHITE     = 255,255,255
RGB_RED        = 255,0,0

GB_WIDTH    = 280
GB_HEIGHT    = 380

PADDLE_START_TOP = GB_HEIGHT - 30
PADDLE_START_LEFT = GB_WIDTH / 2

STARTSPEED = 5
FIRST_LEVEL = 0
LAST_LEVEL = 5

class Ball(Describer):
    "Ball class, represents the ball object for the PyBreakout game"
    def __init__(self, imageFilename):
        "Ball __init__ method creates a ball in its default position with its default states"
        self.image = pygame.image.load(imageFilename)
        r = self.image.get_rect()
        self.x = r.x
        self.y = r.y
        self.w = r.w
        self.h = r.h

        #the ball has an angle from 0 to 359 degrees
        self.speed = 3
        self._angle = 45

        self.stuck = False
        self.resetState()

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    @property
    def x_dir(self):
        return self.speed * math.cos(math.radians(180+self.angle))
    @property
    def y_dir(self):
        return -self.speed * math.sin(math.radians(180+self.angle))
    
    def _getAngle(self):
        return self._angle
    def _setAngle(self, angle):
        if (angle < 0):
            angle += 2*360
        self._angle = angle % 360
    angle = property(_getAngle, _setAngle)

    def resetState(self):
        "Ball is reset to sit motionless on top of paddle, launch with Spacebar"
        self.x = PADDLE_START_LEFT+30
        self.y = PADDLE_START_TOP-self.h
    def moveDown(self, pixelsDown):
        "Move the ball image down pixelsDown worth"
        self.y += pixelsDown
    def moveUp(self, pixelsUp):
        "Move the ball image up pixelsUp worth"
        self.y -= pixelsUp
    def moveLeft(self, pixelsLeft):
        "Move the ball image left pixelsLeft worth"
        self.x -= pixelsLeft
    def moveRight(self, pixelsRight):
        "Move the ball image right pixelsRight worth"
        self.x += pixelsRight
    def autoMove(self):
        hitWall = False
        if self.stuck:
            return hitWall
        else:
            if self.rect.left <= 0:
                self.angle = 180 - self.angle
                hitWall = True
            if self.rect.right >= GB_WIDTH:
                self.angle = 180 - self.angle
                hitWall = True
            if self.rect.top <= 0:
                self.angle = 360 - self.angle
                hitWall = True

            self.x += self.x_dir
            self.y += self.y_dir
            return hitWall

class Bonus(Describer):
    "Bonus class, represents the bonus object for the PyBreakout game"
    
    def __init__(self, imageFilename):
        self.image = pygame.image.load(imageFilename)
        self.rect = self.image.get_rect()
        self.speed = 1
        self.x_dir = 0
        self.y_dir = 1    
                        
    def moveDown(self, pixelsDown):
        "Move the bonus image down pixelsDown worth"
        self.rect = self.rect.move(0,pixelsDown)
        
class Triball(Bonus):
    def __init__(self, myBrick):
        Bonus.__init__(self,rm.getImagePath("triball-bonus.png"))
        self.rect.move_ip(myBrick.position)
        
    def applyBonus(self, pybreakout):
        #print "this is where I add two additional balls"
        ball1 = Ball(rm.getImagePath("ball-mini.png"))
        ball2 = Ball(rm.getImagePath("ball-mini.png"))
        self.adjustBall(ball1,5,pybreakout)
        self.adjustBall(ball2,-5,pybreakout)
        pybreakout.balls.append(ball1)
        pybreakout.balls.append(ball2)
        #print "Adding two, len(self.balls) = " + str(len(pybreakout.balls))
    
        
    def adjustBall(self,currentBall,numPixels,pybreakout):
        currentBall.stuck = False
        currentBall.x = pybreakout.balls[0].x
        currentBall.y = pybreakout.balls[0].y + numPixels
        currentBall.angle = pybreakout.balls[0].angle

class Slowball(Bonus):
    def __init__(self, myBrick):
        Bonus.__init__(self,rm.getImagePath("slowball-bonus.png"))
        self.rect.move_ip(myBrick.position)
        
    def applyBonus(self, pybreakout):
        pybreakout.speed = 0

        
class Paddle(Describer):
    "A Paddle object"
    
    def __init__(self, imageFilename, ball, maxsize=(GB_WIDTH, GB_HEIGHT)):
        self.image = pygame.image.load(imageFilename)
        r = self.image.get_rect()
        self.x = r.x
        self.y = r.y
        self.w = r.w
        self.h = r.h
        self.maxsize = maxsize
        self.ball = ball
        self.angle = 0
        self.resetState()

    @property
    def rect(self):
        rw = transform.rotate(self.image, self.angle).get_rect().w
        rh = transform.rotate(self.image, self.angle).get_rect().h
        return pygame.Rect(int(self.x), int(self.y), rw, rh)
        
    def resetState(self):
        "Paddle object is reset to the bottom center of the screen"
        self.x = PADDLE_START_LEFT
        self.y = PADDLE_START_TOP

    def moveLeft(self, pixelsLeft):
        self.x -= pixelsLeft
        self.x = max(self.x, 0)
        if self.ball.stuck:
            self.ball.moveLeft(pixelsLeft)

    def moveRight(self, pixelsRight):
        self.x += pixelsRight
        self.x = min(self.x+self.w, self.maxsize[0]) - self.w
        if self.ball.stuck:
            self.ball.moveRight(pixelsRight)

    def moveUp(self, pixelsUp):
        self.y -= pixelsUp
        self.y = max(self.y, 0)
        if self.ball.stuck:
            self.ball.moveUp(pixelsUp)

    def moveDown(self, pixelsDown):
        self.y += pixelsDown
        self.y = min(self.y+self.h, self.maxsize[1]) - self.h
        if self.ball.stuck:
            self.ball.moveDown(pixelsDown)

    @property
    def position(self):
        rw = transform.rotate(self.image, self.angle).get_rect().w
        rh = transform.rotate(self.image, self.angle).get_rect().h
        x = self.x + self.w/2 - rw/2
        y = self.y + self.h/2 - rh/2
        return x,y

    def rotate(self, angle):
        self.angle += angle
        self.angle = self.angle % 180

    def setAngle(self, angle):
        self.angle = angle % 180


class Brick(Describer):
    """every brick has the following
    an image: filename
    point value: int
    isDestructible: True/False
    isDestroyed: True/False
    a rectangular position: (x,y)"""
    
    def __init__(self, imageFilename, position, value=10, destructible=True, destroyed=False):
        self.image = pygame.image.load(imageFilename)
        self.rect = self.image.get_rect()
        self.position = position
        self.rect.move_ip(position)
        self.pointValue = value
        self.isDestructible = destructible
        self.isDestroyed = destroyed
        self.hasBonus = False
        self.hitCount = 0

    
    def addBonus(self, bonusType):
        self.hasBonus = True
        self.bonus = bonusType

class PyBreakout(Describer):
    "This is the main game class for PyBreakout"
    
    def __init__(self, cventry):
        self.running = False
        self.dump = False
        
        self.size = GB_WIDTH, GB_HEIGHT
        self.height = self.size[1]
        self.width = self.size[0]
        
        self.soundManager = soundmanager.SoundManager()
        
        self.startGame()
        self.initializeScreen()
        self.cventry = cventry
        cventry.setCallbacks(self.onMove, self.onSetAngle)

    def setDump(self, dump_or_not):
        self.dump = dump_or_not
        self.cventry.dump = dump_or_not
        
    def initializeScreen(self):
        #Create Gameboard with RGB_BLACK background
        self.screen = pygame.display.set_mode(self.size)
        self.updateScreen()
        
    def loadBricks(self):
        self.bonuses = []
        allBricks = []
        levelFile = open(rm.getGameLevelPath('level'+str(self.level)+".dat"))
        levelData = levelFile.readlines()
        self.drawLocation = [0,120]
        for levelLine in levelData:
            lineBricks = levelLine.strip().split(',')
            for brickChar in lineBricks:
                allBricks.append(self.createBrick(brickChar))
            self.drawLocation = 0,self.drawLocation[1]+10
        return allBricks
        
    def drawBricks(self):
        '''given all the Brick objects:
            1) Check to see if they are Destroyed
            2) if not Destroyed, draw currentBrick.image at currentBrick.position'''
        for currentBrick in self.bricks:
            if not currentBrick.isDestroyed:
                self.screen.blit(currentBrick.image, currentBrick.position)
            
    def createBrick(self, brickChar):
        "Given a brickChar, create the appropriate instance object of the Brick class and return it"
        
        if brickChar == 'R':
            newBrick = Brick(rm.getImagePath("brick-red.png"), self.drawLocation)
            luckyNum = randint(0,4)
            #luckyNum = 3
            if luckyNum == 3:
                newBrick.addBonus(Triball(newBrick))
        elif brickChar == 'P':
            newBrick = Brick(rm.getImagePath("brick-purple.png"), self.drawLocation)
            luckyNum = randint(0,4)
            if luckyNum == 3:
                newBrick.addBonus(Triball(newBrick))
        elif brickChar == 'G':
            newBrick = Brick(rm.getImagePath("brick-green.png"), self.drawLocation)
            luckyNum = randint(0,7)
            if luckyNum == 3:
                newBrick.addBonus(Slowball(newBrick))
        elif brickChar == 'O':
            newBrick = Brick(rm.getImagePath("brick-orange.png"), self.drawLocation)
            luckyNum = randint(0,5)
            if luckyNum == 5:
                newBrick.addBonus(Triball(newBrick))
        elif brickChar == 'B':
            newBrick = Brick(rm.getImagePath("brick-blue.png"), self.drawLocation)
            luckyNum = randint(0,5)
            if luckyNum == 0:
                newBrick.addBonus(Triball(newBrick))
        elif brickChar == 'Q':
            newBrick = Brick(rm.getImagePath("brick-grey.png"), self.drawLocation, 0, False)
        elif brickChar == '.':
            newBrick = Brick(rm.getImagePath("brick-grey.png"), self.drawLocation, 0, True, True)
        if newBrick.isDestructible and not(newBrick.isDestroyed):
            self.numDestructibleBricks +=1
        self.drawLocation = self.drawLocation[0]+40,self.drawLocation[1]
        return newBrick
        
    def updateScreen(self):
        "Draw everything on the screen"
        
        self.screen.fill(RGB_BLACK)
        
        #Draw Paddle and Ball
        self.screen.blit(transform.rotate(self.paddle.image,
                                self.paddle.angle), self.paddle.position)
        
        for ball in self.balls:
            self.screen.blit(ball.image, (ball.x, ball.y))

        #Draw Points Label and Points String
        self.screen.blit(self.pointsLabel, (10,10))
        self.screen.blit(self.pointsString, (80,10))
        
        #Draw Level Label and Level String
        self.screen.blit(self.levelLabel, (200, 10))
        self.screen.blit(self.levelString, (250, 10))
        
        #Draw non-destroyed Bricks for current level
        self.drawBricks()
        
        #Draw any bonuses that are on screen at the moment
        for boni in self.bonuses:
            self.screen.blit(boni.image, boni.rect)

        #Draw Mini-paddles signifying lifes left
        self.drawMiniPaddles()
        
        pygame.display.flip()

    
    def drawMiniPaddles(self):
        if(self.numLives == 0):
            return
        drawPos = 0
        miniPaddleImage = pygame.image.load(rm.getImagePath("paddle-mini.png"))
        miniPaddleRect = miniPaddleImage.get_rect()
        for numLife in range(self.numLives):
            self.screen.blit(miniPaddleImage,(0+drawPos,GB_HEIGHT-miniPaddleRect.height))
            drawPos = drawPos + 22
        
    def reset(self):
        "Reset Ball, Paddle, and Speed to default positions and states. Called after a ball falls into the abyss."
        
        self.balls = []
        self.balls.append(Ball(rm.getImagePath("ball-mini.png")))
        self.paddle = Paddle(rm.getImagePath("paddle.png"),self.balls[0], self.size)
        
        self.pointsColor = RGB_WHITE
        self.running = True
        self.speed = self.level
        
    def startGame(self):
        "Start a new game, reset everything to default positions and states"
        self.level = 0
        self.reset()
        self.points = 0
        
        #self.level = "TEST1"
        self.numDestructibleBricks = 0
        
        #Load bricks
        self.bricks = self.loadBricks()
        
        self.numLives = 2
        self.oneUpBonuses = [False,False]


        
        self.font = pygame.font.Font(rm.getFont("Verdana.TTF"),12)
        self.pointsLabel = self.font.render("Points: ", True, RGB_WHITE)
        self.pointsString = self.font.render(str(self.points), True, self.pointsColor)
        self.levelLabel = self.font.render("Level: ", True, RGB_WHITE)
        self.levelString = self.font.render(str(self.level), True, RGB_WHITE)
        self.gameOver = False

    def onMove(self, dx, dy):
        #print "(x,y): ",dx, dy
        if dx > 0:
           self.paddle.moveRight(dx)
        else:
           self.paddle.moveLeft(abs(dx))
        if dy > 0:
           self.paddle.moveDown(dy)
        else:
           self.paddle.moveUp(abs(dy))

    def onSetAngle(self, angle):
        #print "angle: ", angle
        self.paddle.setAngle(angle)

    def dumpScreen(self):
        if not self.dump:
            return
        i = 0
        while os.path.exists('game%.4d.png' % (i,)):
           i += 1
        pygame.image.save(self.screen, 'game%.4d.png' % (i,))
        
    def play(self):
        "The main game loop occurs here, checks for keyboard input, updates game state, etc..."
        self.running = True
        lastLevelUpTime = time.time()
        i = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: exit()
                
            keys = pygame.key.get_pressed()
            if keys[K_q]:
               exit(0)
            elif keys[K_RETURN]:
                if (len(self.balls) <= 0) or (len(self.balls) == 1 and not self.balls[0].stuck):
                    if self.numLives >=1:
                        self.numLives -=1
                        self.reset()
                        print "self.numLives = %s"%self.numLives
                    else:
                        self.running = False
                        self.endgame()
            elif keys[K_y]:
                if self.gameOver:
                    self.startGame()
        
            if self.running:
                if (i % 4 == 0):
                    self.cventry.run()
                self.checkBonusCollision()
                
                for ball in self.balls[:]:
                    self.checkBallCollision(ball)
                    hitWall = ball.autoMove()
                    if hitWall:
                        self.soundManager.play('cartoon-spring-sound',[0.2,0.2])
                    if(ball.rect.top >= GB_HEIGHT):
                        self.balls.remove(ball)
                
                for boni in self.bonuses:
                    boni.moveDown(1)
                    if boni.rect.y > GB_HEIGHT:
                        #if it reaches the bottom of the screen remove it from the bonuses list
                        self.bonuses.remove(boni)
                
                self.pointsString = self.font.render(str(self.points), True, self.pointsColor)
                self.updateScreen()
                if (i % 4 == 0):
                   self.dumpScreen()
                i += 1
                
                #All balls have left the gameboard, need to pause and wait for Right Click
                # or if numLives == 0, then end game.
                if len(self.balls) == 0:
                    self.running = False
                    self.pointsColor = RGB_RED
                    if self.numLives == 0:
                        self.endgame()
                
                if self.checkLevelUp():
                    self.speed = self.level
                    if self.level == LAST_LEVEL:
                        self.level = -1
                    self.level += 1
                    self.levelString = self.font.render(str(self.level), True, RGB_WHITE)
                    self.bricks = self.loadBricks()
                    
                    self.balls = []
                    self.balls.append(Ball(rm.getImagePath("ball-mini.png")))
                    self.paddle = Paddle(rm.getImagePath("paddle.png"),self.balls[0])
                    
            
                #Wait a couple of milliseconds
                currentTime = time.time()
                if(currentTime - lastLevelUpTime > 15):
                    lastLevelUpTime = currentTime
                    if (STARTSPEED - self.speed > 0):
                        #print "15 s elapsed increasing speed by 1"
                        self.speed +=1
                    #else:
                        #print "reached max speed"
                
            #pygame.time.wait(STARTSPEED - self.speed)
        
    def checkBallCollision(self, currentBall):
        if(currentBall.rect.colliderect(self.paddle.rect)):
            #Check if it is a vertical collision or horizontal collision
            firstFifth = self.paddle.rect.left + 8
            secondFifth = self.paddle.rect.left + 16
            thirdFifth = self.paddle.rect.left + 24
            fourthFifth = self.paddle.rect.left + 32

            theta = currentBall.angle
            phi = self.paddle.angle
            
            currentBall.angle = 2 * phi - theta
            #paddle and ball collided, play appropriate sound
            
            self.soundManager.play('cartoon-blurp-sound',[0.3,0.3])
        #check for collision with any non-destroyed bricks
        for brick in self.bricks:
            if(brick.isDestroyed):
                pass
            elif(currentBall.rect.colliderect(brick.rect)):
                if not brick.isDestructible:
                    #indestructible brick and ball collided, play appropriate sound
                    brick.hitCount += 1
                    self.soundManager.play('cartoon-blurp-sound',[0.3,0.3])
                testpointright = currentBall.rect.left+currentBall.rect.width+1,currentBall.rect.top
                testpointleft = currentBall.rect.left-1,currentBall.rect.top
                testpointtop = currentBall.rect.left,currentBall.rect.top-1
                testpointbottom = currentBall.rect.left,currentBall.rect.top+currentBall.rect.height+1
                
                if(brick.rect.collidepoint(testpointright)):
                    #test if the right side of the ball collided with the brick
                    #currentBall.x_dir = -1 * abs(currentBall.x_dir)
                    currentBall.angle = 180 - currentBall.angle
                elif(brick.rect.collidepoint(testpointleft)):
                    #test if the left side of the ball collided with the brick
                    #currentBall.x_dir = 1 * abs(currentBall.x_dir)
                    currentBall.angle = 180 - currentBall.angle
                
                if(brick.rect.collidepoint(testpointtop)):
                    #test if top of ball collided with brick
                    currentBall.angle = 360 - currentBall.angle
                    #currentBall.y_dir = 1 * abs(currentBall.y_dir)
                elif(brick.rect.collidepoint(testpointbottom)):
                    #test if the bottom of the ball collided with the brick
                    currentBall.angle = 360 - currentBall.angle
                    #currentBall.y_dir = -1 * abs(currentBall.y_dir)
                
                self.points += brick.pointValue
                
                if(brick.isDestructible or brick.hitCount == 4):
                    brick.isDestroyed = True
                    if(brick.isDestructible):
                        self.numDestructibleBricks -=1
                    self.soundManager.play('punchhard',[0.3,0.3])
                    if brick.hasBonus:
                        self.bonuses.append(brick.bonus)
                    #only give out bonuses when a destructible brick is hit
                    if (self.points == 500 and not self.oneUpBonuses[0]):
                        self.numLives +=1
                        self.soundManager.play('triangle',[0.3,0.3])
                        self.oneUpBonuses[0] = True
                    elif (self.points == 1500 and not self.oneUpBonuses[1]):
                        self.numLives +=1
                        self.soundManager.play('triangle',[0.3,0.3])
                        self.oneUpBonuses[1] = True
                    #print "numDestructibleBricks = %s"%self.numDestructibleBricks
                break
    
    def checkBonusCollision(self):
        for boni in self.bonuses:
            if boni.rect.colliderect(self.paddle.rect):
                self.bonuses.remove(boni)
                boni.applyBonus(self)
        
    def checkLevelUp(self):
        if self.numDestructibleBricks == 0:
            return True
        return False
    
    def endgame(self):
        print "endgame called!"
        if self.gameOver:
            return
        self.gameOverLabel = self.font.render("GAME OVER", True, RGB_WHITE)
        self.playAgainLabel = self.font.render("Play Again?", True, RGB_WHITE)
        self.instructionsLabel = self.font.render("YES (y) / NO (ESC)", True, RGB_WHITE)
        self.screen.blit(self.gameOverLabel,(100, 40))
        self.pointsColor = RGB_RED
        self.screen.blit(self.playAgainLabel,(100, 75))
        self.screen.blit(self.instructionsLabel,(80, 95))
        self.gameOver = True
        pygame.display.flip()
            
if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("PyBreakout")
    
    game = PyBreakout()
    game.initializeScreen()
    game.play()
                

