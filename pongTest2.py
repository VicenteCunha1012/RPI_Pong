from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
import framebuf
import time
from math import sqrt

#hardware
WIDTH     = 128
HEIGHT    = 64
potentMax = 2**16 -1
potentiometerPin = 26
sclPin = 17
sdaPin = 16
#game preference
lineHeight    = 10
ballRadius    = 4
initialXSpeed = -1 #pixels per frame
initialYSpeed = 1



stopGame = False
winner   = 0
step = int(potentMax / HEIGHT - lineHeight)



class Potentiometer:
    def __init__(self, pin):
        self.object = ADC(pin)
        self.value  = self.object.read_u16()
        
    def update(self):
        self.value = self.object.read_u16()
        
        
class Player1:
    def __init__(self, pos, potentRep):
        self.pos       = potentRep.value
        self.potentRep = potentRep
        
    def move(self):
        self.potentRep.update()
        self.pos = int(self.potentRep.value / step)
        if self.pos > HEIGHT - lineHeight - 3:
            self.pos = HEIGHT - lineHeight -3
        elif self.pos < 3:
            self.pos = 3
        display.line(0, self.pos, 0, self.pos + lineHeight, 1) # draw player 1
    
class Player2:
    def __init__(self, pos):
        self.pos = pos
        
    def checkHeight(self, accuracy, ball):
        
        if accuracy == 100:
            self.pos = ball.posY - int(lineHeight / 2)
        else:
            pass
        display.line(WIDTH -1 , self.pos, WIDTH - 1, self.pos + lineHeight, 1) #draw player 2
            
            
class Ball:
    def __init__(self, posX, posY, speedX, speedY, ballRadius):
        self.posX = posX
        self.posY = posY
        self.speedX = speedX
        self.speedY = speedY
        self.ballRadius = ballRadius
        self.isVisible = True
    
    def update(self,player1, player2):
        self.searchCollision(player1, player2)
        self.posX += self.speedX
        self.posY += self.speedY
        if self.isVisible:
            paint_circle(self.posX, self.posY, self.ballRadius, 1)
    
    def searchCollision(self, player1, player2):
        if self.posX - self.ballRadius < 1:
            if player1.pos <= self.posY <= player1.pos + lineHeight:
                self.speedX = -self.speedX
            else:
                self.isVisible = False
                stopGame = True
                winner = 2
        elif self.posX + self.ballRadius > WIDTH - 1:
            if player2.pos <= self.posY <= player2.pos + lineHeight:
                self.speedX = -self.speedX
            else:
                self.isVisible = False
                stopGame = True
                winner = 1
        elif self.posY - self.ballRadius < 0 or self.posY + self.ballRadius > HEIGHT -2:
            self.speedY = -self.speedY
            
def paint_circle(centerX, centerY, radius, color=1):
    for i in range(centerX - radius, centerX + radius):
        for j in range(centerY - radius, centerY + radius):
            if sqrt( ( (centerX -i) **2) + ( (centerY -j) ** 2)) < radius:
                display.pixel(i, j, color)

        
i2c = I2C(0, scl=Pin(sclPin),sda=Pin(sdaPin), freq=400000)
display = SSD1306_I2C(WIDTH, HEIGHT, i2c)

potent1 = Potentiometer(potentiometerPin)
player1 = Player1(5,potent1)
player2 = Player2(int(HEIGHT / 2))
ball = Ball(int(WIDTH / 2), int(HEIGHT / 2),  initialXSpeed, initialYSpeed, ballRadius)

display.fill(0)


while not stopGame:
    display.fill(0)
    potent1.update()
    player1.move()
    player2.checkHeight(100, ball)
    ball.update(player1, player2)
    
    if not stopGame:
        display.line(0,  0, 128,  0, 1) #top border line
        display.line(0, 63, 128, 63, 1) #bottom border line
    else:
        if winner == 2:
            display.text(0, int(HEIGHT / 2), "Winner: Player 2")
            display.show()
            break
        elif winner == 1:
            display.text(0, int(HEIGHT / 2), "Winner: Player1 ")
            display.show()
            break
        
    display.show()
        