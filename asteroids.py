import pygame, sys, math, random, copy
from pygame.locals import *


#- GLOBALS ---
X = 0
Y = 1
MIN = 0
MAX = 1
FPS = 30
FRICTION = 0.9
WINWIDTH = 640
WINHEIGHT = 480
SHIPHEIGHT = 11
SHIPWIDTH = 11
ACCELERATION = 0.3
BULLETWIDTH = 2 #the thickness of the bullets fired
BULLETSPEED = 2 #multiplied to the bullet's direction vector
DEG_TO_ROT = 6 #degrees that the ship is rotated when left or right is pressed
ASTEROIDSPEED = 6
ASTEROIDSIZES = ("small", "medium", "large")

#-- colors ---------------
TRANSPARENT = (255, 255, 255, 0) 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 100)
RED = (255, 0, 0)

#these change throughout the game
ALL_ASTEROIDS = [] #global list where asteroids are stored
PAUSE = False #tells the game if it's paused or not

#--------- functions -----
def adjust_top(point_list):
	#check the object's points and move the object if it's off the screen
	adjusted_points = [] #new set of points to account for the screen wrapping
	last_index = len(point_list) - 1	
	
	for i, point in enumerate(point_list): #checking the top

		if point[Y] >= 0: 
			break
		x, y = point #new point is now at the bottom of the screen
		adjusted_points.append([x, (y + WINHEIGHT)])

		if i == last_index: #each point was off the screen
			point_list = adjusted_points
	return point_list

def adjust_left(point_list):
	adjusted_points = [] #new set of points to account for the screen wrapping
	last_index = len(point_list) - 1

	for i, point in enumerate(point_list): #checking left side of screen

		if point[X] >= 0: #x coordinate is to the right of the screen
			break
		x, y = point
		adjusted_points.append([(x + WINWIDTH), y])

		if i == last_index: #each point was off the screen
			point_list = adjusted_points
	return point_list

def adjust_right(point_list):
	adjusted_points = [] #new set of points to account for the screen wrapping
	last_index = len(point_list) - 1

	for i, point in enumerate(point_list): #checking right side of screen

		if point[X] <= WINWIDTH: #x coordinate is to the left of the screen
			break #entire shape isn't off the screen 
		x, y = point
		adjusted_points.append([(x - WINWIDTH), y])

		if i == last_index: #each point was off the screen
			point_list = adjusted_points
	return point_list

def adjust_bottom(point_list):
	adjusted_points = [] #new set of points to account for the screen wrapping
	last_index = len(point_list) - 1

	for i, point in enumerate(point_list): #checking right side of screen

		if point[Y] <= WINHEIGHT: #x coordinate is to the left of the screen
			break #entire shape isn't off the screen 
		x, y = point
		adjusted_points.append([x, (y - WINHEIGHT)])

		if i == last_index: #each point was off the screen
			point_list = adjusted_points
	return point_list	

def adjust_screen_position(point_list):
	#if the point list is passed a side return the points on the opposite side
	point_list = adjust_top(point_list)
	point_list = adjust_left(point_list)
	point_list = adjust_right(point_list)
	point_list = adjust_bottom(point_list)
	return point_list

def game_quit(event):
	#check for the window being closed or escape key pressed
	return ((event.type == QUIT)
				or
			(event.type == KEYUP) and (event.key == K_ESCAPE))

def get_rand(pos_number):
	#grab a random floating point number from [-pos_number, pos_number]
	rand = random.random() #rand within [0.0, 1.0)
	rand *= (pos_number * 2) #rand within [0.0, (2)(pos_number)]
	rand -= pos_number #rand in the right range
	return rand

def paused():
	global PAUSE #set to false to unpause the game
	continueButton = Button("Continue", WHITE, BLACK, (280, (WINHEIGHT / 2)))
	quitButton = Button("Quit", WHITE, BLACK, (360, (WINHEIGHT / 2)))

	#place the buttons on the screen
	SCREEN.blit(continueButton.surface, continueButton.rect)
	SCREEN.blit(quitButton.surface, quitButton.rect)

	while PAUSE: #global @pause set to True when 'p' key is pressed
		for event in pygame.event.get():
			
			if event.type == pygame.MOUSEBUTTONUP: #mouse was clicked

				if continueButton.clicked():
					PAUSE = False; #unpause
				elif quitButton.clicked():
					pygame.quit() #quit the entire game
					sys.exit()

		pygame.display.update()
		FPSCLOCK.tick(FPS)
			
def start_new_game(ship, levels):
	#display "game over": NOT IMPLEMENTED

	#reset ship lives
	ship.lives = 3
	#start levels from the beginning
	levels.restart()
	levels.set_next_level()
	#start the game or exit the game

def within_screen(points):
	num_points_in = 0

	for point in points: 

		if ((0 <= point[X]) and (point[X] <= WINWIDTH)
			and 
			(0 <= point[Y]) and (point[Y] <= WINHEIGHT)):
			num_points_in += 1

	return (num_points_in == len(points))

#----- CLASSES ----------------------------------------------------------------

class Asteroid:
	def __init__(self, sz, start=None):
		self.size = sz #go to a lower size if bullet hits
		self.get_points(sz, start) #creates a list of points
		#x, y between [-1.0, 1.0)
		self.direction = [get_rand(1), get_rand(1)]
		#speed of rock, could increase as level goes up

	def split_up(self):
		#asteroid breaks into smaller pieces and those get stored
		if self.size != "small": #large and medium break into smaller asteroids
			new_index = ASTEROIDSIZES.index(self.size) - 1
			smaller_size = ASTEROIDSIZES[new_index]

			if self.size == "large": #could have dictionary of number to add
				num_to_add = 2 #large asteroid becomes 2 medium
			else: #it's a medium asteroid, make 3 small ones 
				num_to_add = 3
			#have the smaller asteroids start where the bigger one was
			for i in range(num_to_add): #have each refer to new starting point
				start = copy.copy(self.point_list[0])
				ALL_ASTEROIDS.append(Asteroid(smaller_size, start))
		#the current asteriod is always deleted when hit 
		if self in ALL_ASTEROIDS: #ADDED
			ALL_ASTEROIDS.remove(self)

	def detect_collision(self, ship):
		#check if a bullet or the ship has collided with current asteroid

		for point in ship.point_list:
			#check to see if any point from the object is in the asteroid
			if self.within_rect(point): #ship and asteroid collided
				#break the ship, remove a ship image from the lives display
				self.split_up() #asteroid breaks into smaller ones
				ship.lives -= 1 #player has on less life

		for i, bullet in enumerate(ship.bullets):
			for point in bullet.point_list:

				if self.within_rect(point): #bullet hit the asteroid
					if bullet in ship.bullets: 
						del ship.bullets[i] #bullet disappears as it hits the asteroid
					self.split_up() #break into more asteroids
					break #one point hit the asteroid, don't check the others
		
	def draw(self):
		pygame.draw.polygon(SCREEN, WHITE, self.point_list, 1)

	def get_points(self, size, start=None):
		#get and add random starting point. add the rest of the points
		self.point_list = []

		if start == None: #no starting point passed in, start somewhere random
			x = random.randint(0, WINWIDTH)
			y = random.randint(0, WINHEIGHT)
			start = [x, y]
		self.point_list.append(start)

		if size == "large":
			self.make_large()
		
		elif size == "medium":
			self.make_medium()

		elif size == "small":
			self.make_small()

		self.set_rectangle_values() #set collision box around asteroid

	def make_large(self):
		f_x, f_y = self.point_list[0] #first x,y coordinates
		offsets = ((6, 2), (10, 6), (12, 12), (8, 13), (10, 15), (14, 18), 
					(6, 22), (0, 25), ((-8), 18), ((-14), 22), ((-20), 18),
					((-30), 10), ((-22), 0), ((-10), 5))

		for offset in offsets:
			self.point_list.append([f_x + offset[X], f_y + offset[Y]])

	def make_medium(self):
		f_x, f_y = self.point_list[0]
		offsets = ((4, 10), (2, 14), ((-3), 11), (-6, 16), (-10, 14),
					(-12, 5), (-8, 1))

		for offset in offsets:
			self.point_list.append([(f_x + offset[X]), (f_y + offset[Y])])

	def make_small(self):
		f_x, f_y = self.point_list[0]
		offsets = ((3, 4), (5, 0), (6, 8), (1, 9), ((-4), 4))

		for offset in offsets:
			self.point_list.append([f_x + offset[X], f_y + offset[Y]])

	def move(self):
		#move the asteroid in its stored direction
		for i in range(len(self.point_list)):
			self.point_list[i][X] += (self.direction[X] * ASTEROIDSPEED)
			self.point_list[i][Y] += (self.direction[Y] * ASTEROIDSPEED)

		self.point_list = adjust_screen_position(self.point_list)
		self.set_rectangle_values() #inner rectangle needs to move too

	def set_rectangle_values(self):
		#not dynamic mins / max, but the shapes of the rocks are fine..
		if self.size == "medium":
			indices = (6, 2, 0, 4)
		elif self.size == "large":
			indices = (12, 6, 0, 8)
		elif self.size == "small":
			indices = (0, 1, 2, 3)

		#set min, max x,y values for collision detecting rectangle
		left = self.point_list[indices[0]] #left most point (x min)
		right = self.point_list[indices[1]] #right most point (x max)
		top = self.point_list[indices[2]]  #you get the point
		bottom = self.point_list[indices[3]]

		self.x_rect_vals = (left[X], right[X]) #add tuple of min/max values
		self.y_rect_vals = (top[Y], bottom[Y]) #represents inner rectangle
		#top is 'min' because y gets bigger as it goes down the screen

	def within_rect(self, point):
		#check to see if a point is inside the asteroid
		return \
		((self.x_rect_vals[MIN] <= point[X]) and
		(point[X] <= self.x_rect_vals[MAX])
		and #it's within the inner rectangle
		(self.y_rect_vals[MIN] <= point[Y]) and
		(point[Y] <= self.y_rect_vals[MAX]))


class Bullet:
	def __init__(self, start, dir): 
		#pass in the starting point and the direction vector
		#direction vector is twice the needed length
		self.direction = ((dir[X] / 2), (dir[Y] / 2))
		#use a copy of the ship's front coordinates
		f_x, f_y = start #first x and y 
		self.point_list = [[f_x, f_y], ]
		self.point_list.append([f_x + self.direction[X], 
								f_y + self.direction[Y]])

	def move(self):

		for i in range(len(self.point_list)):
			self.point_list[i][X] += (self.direction[X] * BULLETSPEED)
			self.point_list[i][Y] += (self.direction[Y] * BULLETSPEED)

	def draw(self):
		f_point = self.point_list[0] #first and second point
		s_point = self.point_list[1]
		pygame.draw.line(SCREEN, WHITE, f_point, s_point, BULLETWIDTH)


class Button:
	def __init__(self, text, textColor, backColor, start):
		self.text = pygame.font.Font('freesansbold.ttf', 32) #text object
		#surface to render the text
		self.surface = self.text.render(text, True, textColor, backColor)
		#rectangle to check position
		self.rect = self.surface.get_rect(center=start) 

	def clicked(self):
		mousePos = pygame.mouse.get_pos() #where the cursor is currently
		#check if the mouse is within the button
		return self.rect.collidepoint(mousePos) 


class Levels:
	def __init__(self, filename):
		self.file = open(filename, "r") #open the levels file for reading

	def restart(self):
		#read from the beginning of the file again
		self.file.seek(0) 

	def set_next_level(self):
		#read a line from the file and add asteroids to the global list
		line = self.file.readline()

		if line == "":
			pass #user has completed all of the levels
		sizes = line.split() #letters are seperated by whitespace

		for size in sizes: #go through sizes list and add the asteroids
		#for each letter make the appropriate asteroid
			if size == "L":
				size = "large"
			elif size == "M":
				size = "medium"
			elif size == "S":
				size = "small"
			#add it to the global asteroids list
			ALL_ASTEROIDS.append(Asteroid(size))


class Ship:
	def __init__(self):
		self.center = (0, 0) #have a center variable from the beginning
		self.point_list = self.get_points([WINWIDTH / 2, WINHEIGHT / 2])
		self.lives = 3
		self.velocity = 0
		self.bullets = [] #each bullet fired is stored here
		self.deg_to_rotate = 5 #rotate the ship this much with arrow keys
		self.acceleration = 0 #increases as up key is held

	def blow_up(self):
		pass
		#destroy the ship, each side moves in a separate direction

		#rotate each line
			#make rotation based on line (it's center, just it's points)
			#adjust rotate function

		#dont allow player to rotate ship

		#grab each line

		#display the lines

		#move the lines for a short time

		#place the ship back together

	def fire(self):
		#make bullet for drawing and check if it collides with asteroids
		#bullet starts at the tip of the ship and goes in the ship's direction
		bullet = Bullet(self.point_list[0], self.get_direction())
		self.bullets.append(bullet)

	def get_direction(self):
		front = self.point_list[0]
		back = self.point_list[2]
		#vector from the back of the ship to the front
		return [front[X] - back[X], front[Y] - back[Y]]

	def get_points(self, tip): # @tip: where the ship's tip is located
		points = [tip,]
		points.append([tip[X] + 5, tip[Y] + 10])
		points.append([tip[X], tip[Y] + 6])
		points.append([tip[X] - 5, tip[Y] + 10])
		return points

	def draw(self):
		#draw the ship and any bullets fired
		pygame.draw.polygon(SCREEN, WHITE, self.point_list, 1)

		for i, bullet in enumerate(self.bullets):
			bullet.draw()
			bullet.move() #bullets continously move until off the screen

			if not within_screen(bullet.point_list):
				del self.bullets[i] #dont need to keep track of this bullet

	def accelerate(self):
		self.velocity += ACCELERATION

	def move(self):
		direction = self.get_direction()
		
		for i in range(len(self.point_list)):
			self.point_list[i][X] += (direction[X] * self.velocity)
			self.point_list[i][Y] += (direction[Y] * self.velocity)

		self.point_list = adjust_screen_position(self.point_list)
		
		self.set_center() #move the center as well
		self.velocity *= FRICTION #always slow down after moving

	def rotate(self, direction):
		theta = self.deg_to_rotate #rotate clockwise as default

		if direction == "counterclock":
			theta = -self.deg_to_rotate 

		self.set_rotated_points(theta, self.center, self.point_list)

	def set_rotated_points(self, theta, center, points):
		rad = math.radians(theta) #get the radians equivalent
		c = math.cos(rad)
		s = math.sin(rad)

		upterm = center[X] * (1 - c) + center[Y] * s
		downterm = center[Y] * (1 - c) - center[X] * s

		for i in range(len(points)):
			x, y = points[i] #the old x,y values for calculations

			points[i][X] = (x * c) + (y * -s) + upterm
			points[i][Y] = (x * s) + (y * c) + downterm

	def set_center(self):
		front = self.point_list[0]
		back = self.point_list[2]
		#the center is halfway between the front and back on both axis
		x = (front[X] + back[X]) / 2
		y = (front[Y] + back[Y]) / 2

		self.center = [x, y]

#---------------- program starts here -------------------------
def main(): 
	global FPSCLOCK, SCREEN, PAUSE
	pygame.init()

	FPSCLOCK = pygame.time.Clock() #to control the frames per second
	SCREEN = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
	pygame.display.set_caption("Asteroids | Cloned by Chris Mendoza")

	levels = Levels("levels.txt") #read levels from file
	ship = Ship() #create the ship
	levels.set_next_level()
	#image of the ship to display the number of lives 
	#livesSurf = pygame.image.load('ship_img.png')

	while True:
		SCREEN.fill(BLACK)

		for event in pygame.event.get():

			if game_quit(event):
				pygame.quit()
				sys.exit()

			elif event.type == KEYUP: #a keyboard key was pressed / released

				if event.key == K_SPACE: #space bar fires a bullet
					ship.fire()

				elif event.key == K_p: #'p' key pauses the game
					PAUSE = True 
					paused()

		#check continously pressed keys for ship movement 
		keys = pygame.key.get_pressed()

		if keys[K_LEFT]:
			ship.rotate("counterclock")
		elif keys[K_RIGHT]:
			ship.rotate("clockwise")

		if keys[K_UP]:
			ship.accelerate()

		ship.move()
		ship.draw()
		#work with a copy but delete from the original
		all_asteroids_cpy = ALL_ASTEROIDS

		for asteroid in all_asteroids_cpy:
			asteroid.draw()
			asteroid.detect_collision(ship) #asteroids deleted here
			asteroid.move()

		if len(ALL_ASTEROIDS) == 0: #all asteroids were destroyed
			levels.set_next_level() #go to the next level

		pygame.display.update()
		FPSCLOCK.tick(FPS)


if __name__ == '__main__':
	main()