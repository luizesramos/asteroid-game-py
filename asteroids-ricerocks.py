# Rice Asteroids game implementation
# author: Luiz Ramos
# Note This program runs on http://www.codeskulptor.org/
# To run it, copy and paste the code into the text 
# box on the right and hit the "play" button

import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
MAX_ROCKS = 12
score = 0
lives = 3
time = 0.5
steer = 0
chrsz = 28
fntsz = 15
color = "Yellow"
pad = 3
started = False

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated
    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info, sound):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.sound = sound
        self.sound.rewind()
        
    def silence(self):
        self.sound.pause()
        self.sound.rewind()
        
    def draw(s,canvas):
        if s.thrust:
          center = (s.image_center[0]+s.image_size[0],s.image_center[1])
        else:
          center = s.image_center
            
        canvas.draw_image(s.image, center, s.image_size, s.pos, s.image_size, s.angle)
        #canvas.draw_circle(s.pos, s.radius, 1, "White")
        #canvas.draw_circle(s.get_cannon_pos(), 10, 1, "Red", "Red")        

    def get_forward(s):
        return angle_to_vector(s.angle)
        
    def get_cannon_pos(s):
        offset = s.radius + 3
        fwd = angle_to_vector(s.angle)
        return [s.pos[0]+offset*fwd[0],s.pos[1]+offset*fwd[1]]
        
    def set_angv(self, av):
        self.angle_vel = av
        #print self.angle_vel, self.angle
        
    def set_thrust(self, status):
        self.thrust = status
        if self.thrust:
           self.sound.play()
        else:
           self.sound.pause()
           self.sound.rewind() 

    def get_radius(self):
        return self.radius
            
    def get_pos(self):
        return self.pos
            
    def get_vel(self):
        return self.vel
        
    def set_vel(self, dimension, fwd, acc):
        self.vel[dimension] = self.vel[dimension] + fwd[dimension]*acc
        self.vel[dimension] *= 0.98
        
    def update(self):
        self.angle += self.angle_vel
        fwd = angle_to_vector(self.angle)

        if self.thrust:
            acc = 0.2 # acceleration
        else:
            acc = 0

        self.set_vel(0,fwd,acc)
        self.set_vel(1,fwd,acc)
       
        self.pos[0] = (self.pos[0]+self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1]+self.vel[1]) % HEIGHT
        
    def shoot(self):
        fwd = self.get_forward()
        vel = self.get_vel()
        m = Sprite(self.get_cannon_pos(),
                   (vel[0]+fwd[0]*6,vel[1]+fwd[1]*6),\
                    0, 0, missile_image, missile_info, missile_sound)
        m.play_sound()
        return m

# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            self.sound = sound
            sound.rewind()
        else:
            self.sound = None
               
    def set_angv(self, av):
        self.angle_vel = av
        
    def set_pos(self, pos):
        self.pos = [pos[0],pos[1]]

    def set_vel(self, vel):
        self.vel = [vel[0],vel[1]]

    def play_sound(self):
        self.sound.play()
        
    def draw(s, canvas):
        if s.animated:
          center = (s.image_center[0]+s.age*s.image_size[0],s.image_center[1])  
          canvas.draw_image(s.image, center, s.image_size,\
                            s.pos, s.image_size, s.angle)
        else:
          canvas.draw_image(s.image, s.image_center, s.image_size,\
                            s.pos, s.image_size, s.angle)
    
    def update(self):
        self.angle += self.angle_vel
        self.pos[0] = (self.pos[0]+self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1]+self.vel[1]) % HEIGHT
        self.age += 1
        return self.age >= self.lifespan

    def get_radius(self):
        return self.radius
            
    def get_pos(self):
        return self.pos
        
    def collide(self, other):
        return dist(self.pos,other.get_pos()) <= (self.radius+other.get_radius())
    
def place_text(canvas, string, value, pos, width):
    w = width * chrsz
    h = 2 * fntsz
    #canvas.draw_polygon([(pos[0],pos[1]),\
    #                     (pos[0]+w,pos[1]),\
    #                     (pos[0]+w,pos[1]+h),\
    #                     (pos[0],pos[1]+h)], 2, "Green")

    #canvas.draw_circle((pos[0],pos[1]), 4, 4, "Green")
    #canvas.draw_circle((pos[0]+w,pos[1]), 4, 4, "Green")    
    #canvas.draw_circle((pos[0]+w,pos[1]+h), 4, 4, "Green")    
    #canvas.draw_circle((pos[0],pos[1]+h), 4, 4, "Green")        
    
    l = (len(string)*fntsz, len(value)*fntsz)
    ps = (pos[0]+(w-l[0])//2, pos[1]+chrsz)
    pv = (pos[0]+(w-l[1])//2, pos[1]+chrsz*2)
    #canvas.draw_circle((pos[0]+w//2-l[0]//2, pos[1]+fntsz), 4, 1, "White")
    #canvas.draw_circle((pos[0]+w//2, pos[1]+fntsz), 4, 1, "White")
    #canvas.draw_text(string, (pos[0]+w//2-l[0]//2, pos[1]+chrsz), chrsz, color, "monospace")
    #canvas.draw_text(value,  (pos[0]+w//2, pos[1]+2*chrsz), chrsz, color, "monospace")
    canvas.draw_text(string, ps, chrsz, color, "monospace")
    canvas.draw_text(value,  pv, chrsz, color, "monospace")  

def process_sprite_group(canvas, group):
  delset = set([])
  for x in group:
    x.draw(canvas)
    if x.update():
        delset.add(x)
        
  if len(delset) > 0:
    group.difference_update(delset)

def group_group_collide(group_a, group_b):
  delset_a = set([])
  delset_b = set([])
  
  for a in group_a:
    for b in group_b:
      if a.collide(b):
        delset_a.add(a)
        delset_b.add(b)
        explosion_group.add(Sprite(a.get_pos(), [0,0], 0, 0, explosion_image, explosion_info))

  if len(delset_a) > 0:  
    group_a.difference_update(delset_a)

  if len(delset_b) > 0:  
    group_b.difference_update(delset_b)
    
  return len(delset_b)
    
def group_collide(group,x):
  delset = set([])
  for y in group:
    if y.collide(x):
        delset.add(y)
        explosion_group.add(Sprite(y.get_pos(), [0,0], 0, 0, explosion_image, explosion_info))

  if len(delset) > 0:  
    group.difference_update(delset)
    #print delset
  return len(delset)

def start():
   global started, my_ship, score, lives
   score = 0
   lives = 3
   started = True
   timer.start()
   my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info,ship_thrust_sound)
   soundtrack.rewind()
   soundtrack.play()

def die():
  global started
  started = False
  timer.stop()
  my_ship.silence()
  soundtrack.pause()

def explode():
   explosion_sound.rewind()
   explosion_sound.play()
    
def draw(canvas):
    global time, rock_group, lives, score, started
    
    # animiate background
    time += 1
    center = debris_info.get_center()
    size = debris_info.get_size()
    wtime = (time / 8) % center[0]
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, [center[0] - wtime, center[1]], [size[0] - 2 * wtime, size[1]], 
                                [WIDTH / 2 + 1.25 * wtime, HEIGHT / 2], [WIDTH - 2.5 * wtime, HEIGHT])
    canvas.draw_image(debris_image, [size[0] - wtime, center[1]], [2 * wtime, size[1]], 
                                [1.25 * wtime, HEIGHT / 2], [2.5 * wtime, HEIGHT])

    if started:
      # draw ship and sprites / update ship and sprites
      my_ship.draw(canvas)
      process_sprite_group(canvas,rock_group)
      process_sprite_group(canvas,missile_group)
      process_sprite_group(canvas,explosion_group)   
      my_ship.update()
    
    # check collisions
    points = group_group_collide(rock_group,missile_group)
    if points > 0:
      explode()
      score += points
    
    if group_collide(rock_group,my_ship) > 0:
      explode()
      lives -= 1
      if lives == 0:
         die()

    # score and lives
    place_text(canvas,"LIVES",str(lives),[pad,pad],pad)
    place_text(canvas,"SCORE",str(score),[WIDTH-(pad*(chrsz+pad)),pad],pad)
    
    if not started:
      clear_set(rock_group)
      clear_set(missile_group)
      clear_set(explosion_group)
      canvas.draw_image(splash_image, splash_info.get_center(), splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH/2, HEIGHT/2])
      return

def clear_set(x):
  if len(x) > 0:
    x.difference_update(x)
    
def keydown(key): # key is a number
  global my_ship, steer
  if not started:
    return
    
  if key == simplegui.KEY_MAP["left"]:
    steer = -1
    my_ship.set_angv(-0.05)
  elif key == simplegui.KEY_MAP["right"]:
    steer = 1
    my_ship.set_angv(0.05)
  elif key == simplegui.KEY_MAP["up"]:
    my_ship.set_thrust(True)
  elif key == simplegui.KEY_MAP["space"]:
    missile_group.add(my_ship.shoot())

def keyup(key):
    global steer
    if not started:
      return
  
    if key == simplegui.KEY_MAP["up"]:
      my_ship.set_thrust(False)
    elif key == simplegui.KEY_MAP["left"] and steer == -1:
      my_ship.angle_vel = 0
    elif key == simplegui.KEY_MAP["right"] and steer == 1:
      my_ship.angle_vel = 0

def click(pos):
    global started
    center = (WIDTH/2,HEIGHT/2)
    size = splash_info.get_size()
    l = center[0]-size[0]/2 # top
    r = center[0]+size[0]/2 # bottom
    t = center[1]-size[1]/2 # left
    b = center[1]+size[1]/2 # right
    #print l,r, t,b ,pos
    if pos[0] >= l and pos[0] <= r:
      if pos[1] >= t and pos[1] <=  b:
        start()
        
def rvel():
  '''generates a random 1-dimensional velocity'''
  vel = (random.randrange(score+70)/10.0+1.0)/10.0
  if(random.randrange(2) > 0):
    return vel
  else:
    return -vel

def rpos(n, dimension, radius):
  '''generates a position far from te ship's position'''
  r = random.randrange(n)
  #if r < dimension + 2*radius:
  #   r = (dimension + 4*radius) % n
    
  return r

# timer handler that spawns a rock
def rock_spawner():
    if len(rock_group) > (MAX_ROCKS-1):
      return
    
    angv = (-9+(random.randrange(20)))/100
    posx = rpos(WIDTH, my_ship.get_pos()[0], my_ship.get_radius())
    posy = rpos(HEIGHT, my_ship.get_pos()[1], my_ship.get_radius())

    if dist((posx,posy),my_ship.get_pos()) < 2.5*my_ship.get_radius():
        return

    rock_group.add(Sprite((posx,posy), [rvel(),rvel()], 0, angv, asteroid_image, asteroid_info))

# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = None
rock_group = set([])
missile_group = set([])
explosion_group = set([])

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
frame.start()
