import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import RPi.GPIO as GPIO
import time
import random

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

font = ImageFont.load_default()

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)



# setup game vars
#buttonLeft = 21
buttonLeft = 16
#buttonRight = 20
buttonRight = 26

# setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# setup buttons
GPIO.setup(buttonLeft,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buttonRight, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# setup GPIO buttons handling
#GPIO.add_event_detect(buttonLeft, GPIO.FALLING, bouncetime=500)
#GPIO.add_event_detect(buttonRight, GPIO.FALLING, bouncetime=500)

#GPIO.add_event_callback(buttonLeft, callback_left)
#GPIO.add_event_callback(buttonRight, callback_right)

class Bullet:
    size = 6
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def getBody(self):
        body = [self.x, self.y, self.x + self.size, self.y + self.size]
        return body


class Entity:
    size = 5
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def checkBounds(self):
        if (self.x < areaX[0]):
            self.x = areaX[0]
        if (self.x > areaX[1]-self.size):
            self.x = areaX[1]-self.size
            
    def getBody(self):
        body = [self.x, self.y, self.x + self.size, self.y + self.size]
        return body



player = Entity(64, 46)
enemy = Entity(40, 0)
bullet = Bullet(64, player.y)

leftClick = False
rightClick = False

alive = True
score = 0

def checkRightButton():
    global buttonRight
    global rightClick
    
    if not GPIO.input(buttonRight):
        rightClick = True
    else:
        rightClick = False
        
def checkLeftButton():
    global buttonLeft
    global leftClick
    
    if not GPIO.input(buttonLeft):
        leftClick = True
    else:
        leftClick = False

def intersect(e1, e2):
    if (e1.getBody()[0] < e2.getBody()[2] and e1.getBody()[2] > e2.getBody()[0]):
        if (e1.getBody()[1] < e2.getBody()[3] and e1.getBody()[3] > e2.getBody()[1]):
            return True
    else:
        return False

enemies = []
bullets = []

enemies.append(enemy)
bullets.append(bullet)

areaX = [0, 127]
areaY = [0, 53]

bulletClock = 0
enemyClock = 0

def movePlayer(leftClick, rightClick, player):
    if leftClick:
        player.x = player.x - 1
        
    if rightClick:
        player.x = player.x + 1

while(alive):
    
    #================= UPDATE LOGIC ========================
    
    # Spawn
    if (enemyClock > 10 and len(enemies) < 10):
        enemies.append(Entity(random.randint(areaX[0], areaX[1] - e.size), -5))
        enemyClock = 0
    
    # Move
    for e in enemies:
        e.y = e.y + 1
    
    for b in bullets:
        b.y = b.y - 3
        
    checkLeftButton()
    checkRightButton()
    
    # Move player
    movePlayer(leftClick, rightClick, player)
        
    player.checkBounds()
    
    
    # Teleport enemy
    for e in enemies:
        if (e.y > areaY[1] - e.size):
            e.y = -5
            e.x = random.randint(areaX[0], areaX[1] - e.size)
       
    
    # Delete bullets
    for b in bullets:
        if (b.y < 0 - b.size):
            bullets.remove(b)
            bullets.append(Bullet(player.x, 48))
            
    # Collision
    for e in enemies:
        if ( intersect(e, player) ):
            alive = False
	
    for b in bullets:
        for e in enemies:
            if ( intersect(e, b) ):
                enemies.remove(e)
                enemies.append(Entity(random.randint(areaX[0], areaX[1] - e.size), -5))
                if (b in bullets):
                    bullets.remove(b)
                    bullets.append(Bullet(player.x, 48))
                score = score + 1
    
    
    bulletClock = bulletClock + 1
    enemyClock = enemyClock + 1
    #================= RENDER LCD ==========================
    
    # UI
    draw.line((areaX[0], areaY[1], areaX[1], areaY[1]), fill=255)
    
    for b in bullets:
        if b:
            draw.ellipse(b.getBody(), outline=255, fill=1)
    
    for e in enemies:
        if e:
            draw.rectangle(e.getBody(), outline=255, fill=0)
    
    draw.rectangle(player.getBody(), outline=255, fill=1)
    
    
    draw.text((20, 54), str(len(enemies)) +' '+ str(score), font=font, fill=255)
    
	# Display image
    disp.image(image)
    disp.display()
    # Clear image
    draw.rectangle((0,0,width,height), outline=0, fill=0)
	
    
draw.rectangle((0,0,width,height), outline=0, fill=0)

draw.text((30, 10), 'Your score:', font=font, fill=255)
draw.text((30, 20), str(score), font=font, fill=255)


f = open("highscoreOLED.txt", "r")
highscore = int(f.read())
f.close()

if (score > highscore):
    highscore = score
    f = open("highscoreOLED.txt", "w")
    f.write(str(score))

draw.text((30, 30), 'Highest score:', font=font, fill=255)
draw.text((30, 40), str(highscore), font=font, fill=255)

disp.image(image)
disp.display()
