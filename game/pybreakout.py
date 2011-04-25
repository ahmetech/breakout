import pygame, math, time, soundmanager
from pygame.locals import *
from utilities.common import Describer
from utilities.common import rm
from os.path import join
from sys import exit
from random import randrange,randint


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
        self.rect = self.image.get_rect()
        
        #the ball has an angle from 0 to 359 degrees
        self.angle = 135
        self.speed = 1
        self.x_dir = 1
        self.y_dir = -1
        self.stuck = True
        self.resetState()
    
    def resetState(self):
        "Ball is reset to sit motionless on top of paddle, launch with Spacebar"
        self.rect = self.rect.move(PADDLE_START_LEFT+30, PADDLE_START_TOP-self.rect.height)
                        
    def moveDown(self, pixelsDown):
        "Move the ball image down pixelsDown worth"
        self.rect = self.rect.move(0,pixelsDown)
        
    def moveUp(self, pixelsUp):
        "Move the ball image up pixelsUp worth"
        self.rect = self.rect.move(0,-pixelsUp)
        
    def moveLeft(self, pixelsLeft):
        "Move the ball image left pixelsLeft worth"
        self.rect = self.rect.move(-pixelsLeft, 0)
        
    def moveRight(self, pixelsRight):
        "Move the ball image right pixelsRight worth"
        self.rect = self.rect.move(pixelsRight, 0)
        
    def autoMove(self):
        hitWall = False
        if self.stuck:
            return hitWall
        else:
            x_part = math.cos(math.radians(self.angle))/self.speed
            y_part = math.sin(math.radians(self.angle))/self.speed
            #print "x_part = %s , y_part = %s"%(x_part,y_part)
            
            if self.rect.left == 0:
                self.x_dir = 1
                hitWall = True
            if self.rect.right == GB_WIDTH:
                self.x_dir = -1
                hitWall = True
            if self.rect.top == 0:
                self.y_dir = 1
                hitWall = True
            
            #print "x_dir = %s, y_dir = %s, x = %s, y = %s"%(self.x_dir,self.y_dir,self.rect.x,self.rect.y)
            self.rect = self.rect.move(self.x_dir, self.y_dir)
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
        currentBall.rect.top = 0
        currentBall.rect.left = 0
        #print "pybreakout.balls[1].rect = " + str(pybreakout.balls[1].rect)
        currentBall.rect.move_ip(pybreakout.balls[0].rect.x,pybreakout.balls[0].rect.y+numPixels)
        #print "pybreakout.balls[1].rect after moving to balls[0] = " + str(pybreakout.balls[1].rect)
        currentBall.stuck = False
        currentBall.x_dir = pybreakout.balls[0].x_dir
        currentBall.y_dir = pybreakout.balls[0].y_dir

class Slowball(Bonus):
    def __init__(self, myBrick):
        Bonus.__init__(self,rm.getImagePath("slowball-bonus.png"))
        self.rect.move_ip(myBrick.position)
        
    def applyBonus(self, pybreakout):
        pybreakout.speed = 0

        
class Paddle(Describer):
    "A Paddle object"
    
    def __init__(self, imageFilename, ball):
        self.image = pygame.image.load(imageFilename)
        self.rect = self.image.get_rect()
        self.ball = ball
        self.resetState()
        
    def resetState(self):
        "Paddle object is reset to the bottom center of the screen"
        self.rect = self.rect.move(PADDLE_START_LEFT,PADDLE_START_TOP)
        
    def moveLeft(self, pixelsLeft):
        self.rect = self.rect.move(-pixelsLeft, 0)
        if self.ball.stuck:
            self.ball.rect = self.ball.rect.move(-pixelsLeft,0)
        
    def moveRight(self, pixelsRight):
        self.rect = self.rect.move(pixelsRight, 0)
        if self.ball.stuck:
            self.ball.rect = self.ball.rect.move(pixelsRight,0)

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
    
    def __init__(self):
        self.running = False        
        
        self.size = GB_WIDTH, GB_HEIGHT
        self.height = self.size[1]
        self.width = self.size[0]
        
        self.soundManager = soundmanager.SoundManager()
        
        self.startGame()
        self.initializeScreen()
        
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
        self.screen.blit(self.paddle.image, self.paddle.rect)
        
        for ball in self.balls:
            self.screen.blit(ball.image, ball.rect)

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
        self.paddle = Paddle(rm.getImagePath("paddle.png"),self.balls[0])
        
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
        
    def play(self):
        "The main game loop occurs here, checks for keyboard input, updates game state, etc..."
        self.running = True
        lastLevelUpTime = time.time()
        #Excellent suggestions from Peter Nosgoth to have tighter control over Mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: exit()
                
            keys = pygame.key.get_pressed()
            mouse_x = pygame.mouse.get_pos()[0]
            button1,button2,button3 = pygame.mouse.get_pressed()
            
            #print "mouse_x = %s"%mouse_x
            mousePosEqual = True
            while mousePosEqual:
                mousePosEqual = mouse_x != self.paddle.rect.left
                if mouse_x < self.paddle.rect.left:
                    self.paddle.moveLeft(1)
                elif mouse_x > self.paddle.rect.left:
                    if self.paddle.rect.right < self.width:
                        self.paddle.moveRight(1)
                    else:
                        mousePosEqual = False

            if keys[K_SPACE] or button1:
                if self.balls[0].stuck:
                    self.balls[0].stuck = False
            elif keys[K_RETURN] or button2 or button3:
                if (len(self.balls) <= 0) or (len(self.balls) == 1 and not self.balls[0].stuck):
                    if self.numLives >=1:
                        self.numLives -=1
                        self.reset()
                        #print "self.numLives = %s"%self.numLives
                    else:
                        self.running = False
                        self.endgame()
            elif keys[K_y]:
                if self.gameOver:
                    #print "K_y pressed launch brand new game"
                    self.startGame()
            elif keys[K_ESCAPE]:
                #print "K_ESCAPE pressed launch brand new game"
                exit()
        
            if self.running:
                self.checkBonusCollision()
                
                for ball in self.balls:
                    self.checkBallCollision(ball)
                    hitWall = ball.autoMove()
                    if hitWall:
                        self.soundManager.play('cartoon-spring-sound',[0.2,0.2])
                        #print self.ball
                    if(ball.rect.top >= GB_HEIGHT):
                        self.balls.remove(ball)
                
                for boni in self.bonuses:
                    boni.moveDown(1)
                    if boni.rect.y > GB_HEIGHT:
                        #if it reaches the bottom of the screen remove it from the bonuses list
                        self.bonuses.remove(boni)
                
                self.pointsString = self.font.render(str(self.points), True, self.pointsColor)
                self.updateScreen()
                
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
                
            pygame.time.wait(STARTSPEED - self.speed)
        
    def checkBallCollision(self, currentBall):
        if(currentBall.rect.colliderect(self.paddle.rect)):
            #Check if it is a vertical collision or horizontal collision
            firstFifth = self.paddle.rect.left + 8
            secondFifth = self.paddle.rect.left + 16
            thirdFifth = self.paddle.rect.left + 24
            fourthFifth = self.paddle.rect.left + 32

            if currentBall.rect.left < firstFifth:
                #Any incoming ball should be redirected up and left
                #print "Hit firstFifth of paddle"
                currentBall.x_dir = -1
                currentBall.y_dir = -1
            elif currentBall.rect.left >= firstFifth and currentBall.rect.left < secondFifth:
                #Any incoming ball that hits this area should be redirect in opposite y and opposite x
                #print "Hit secondFifth of paddle"
                currentBall.x_dir = -1
                currentBall.y_dir = -1 * currentBall.y_dir
            elif currentBall.rect.left >= secondFifth and currentBall.rect.left < thirdFifth:
                #Any incoming ball that hits this area should be redirect in opposite y and opposite x
                #print "Hit thirdFifth of paddle"
                currentBall.x_dir = 0
                currentBall.y_dir = -1 * currentBall.y_dir
            elif currentBall.rect.left >= thirdFifth and currentBall.rect.left < fourthFifth:
                #Any incoming ball that hits this area should be redirect in opposite y and opposite x
                #print "Hit fourthFifth of paddle"
                currentBall.x_dir = 1
                currentBall.y_dir = -1 * currentBall.y_dir
            else:
                #print "Hit fifthFifth of paddle"
                currentBall.x_dir = 1
                currentBall.y_dir = -1
                
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
                    currentBall.x_dir = -1
                elif(brick.rect.collidepoint(testpointleft)):
                    #test if the left side of the ball collided with the brick
                    currentBall.x_dir = 1
                
                if(brick.rect.collidepoint(testpointtop)):
                    #test if top of ball collided with brick
                    currentBall.y_dir = 1
                elif(brick.rect.collidepoint(testpointbottom)):
                    #test if the bottom of the ball collided with the brick
                    currentBall.y_dir = -1
                
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
        #print "endgame called!"
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
                

