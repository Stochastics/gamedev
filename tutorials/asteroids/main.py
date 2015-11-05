# Space Rocks! (asteroids)
# KidsCanCode 2015
import pygame as pg
import sys
from random import choice, randint, uniform
from os import path

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# basic constants to set up your game
WIDTH = 800
HEIGHT = 600
FPS = 60
TITLE = "Space Rocks!"
BGCOLOR = BLACK

class Player(pg.sprite.Sprite):
    def __init__(self, game, img, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.game = game
        self.image = img
        self.image.set_colorkey(BLACK)
        self.image_clean = img.copy()
        self.rect = self.image.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        self.rot = 0
        self.rot_cache = {}
        self.pos = pg.math.Vector2(WIDTH / 2, HEIGHT / 2)
        self.vel = pg.math.Vector2(0, 0)
        self.acc = pg.math.Vector2(0, 0)
        self.thrust = pg.math.Vector2(0, 0)
        self.thrust_power = 0.2
        self.friction = 0.02
        self.shoot_delay = 350
        self.last_shot = pg.time.get_ticks()

    def get_keys(self):
        keystate = pg.key.get_pressed()
        if keystate[pg.K_LEFT]:
            self.rot_speed = 2
        if keystate[pg.K_RIGHT]:
            self.rot_speed = -2
        if keystate[pg.K_UP]:
            self.thrust = pg.math.Vector2(0, -self.thrust_power).rotate(-self.rot)
        if keystate[pg.K_SPACE]:
            self.shoot()

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            Bullet(self, [self.game.all_sprites, self.game.bullets])

    def rotate(self):
        self.rot = (self.rot + self.rot_speed) % 360
        if self.rot in self.rot_cache:
            image = self.rot_cache[self.rot]
        else:
            image = pg.transform.rotate(self.image_clean, self.rot)
            self.rot_cache[self.rot] = image
        old_center = self.rect.center
        self.image = image
        self.rect = self.image.get_rect(center=old_center)

    def update(self):
        self.rot_speed = 0
        self.thrust = pg.math.Vector2(0, 0)
        self.acc = pg.math.Vector2(0, 0)
        self.get_keys()
        self.rotate()
        self.acc += self.thrust
        self.acc += self.vel * -self.friction
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        if self.pos.y > HEIGHT:
            self.pos.y = 0
        if self.pos.y < 0:
            self.pos.y = HEIGHT
        self.rect.center = self.pos

class Rock(pg.sprite.Sprite):
    # rock sizes 0-3 (3 biggest)
    def __init__(self, game, size, center, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.size = size
        self.game = game
        self.image = choice(self.game.rock_images[size])
        self.image.set_colorkey(BLACK)
        self.image_clean = self.image.copy()
        self.rect = self.image.get_rect()
        self.rot_cache = {}
        self.rot = 0
        self.rot_speed = choice([-1, -0.5, 0.5, 1])
        if self.size == 3:
            edge = choice(['h', 'v'])
            if edge == 'h':
                self.rect.x = -self.rect.width
                self.rect.y = randint(0, HEIGHT)
            elif edge == 'v':
                self.rect.y = -self.rect.height
                self.rect.x = randint(0, WIDTH)
        else:
            self.rect.center = center
        self.vel = pg.math.Vector2(uniform(-2, 2), uniform(-2, 2))

    def rotate(self):
        self.rot = (self.rot + self.rot_speed) % 360
        if self.rot in self.rot_cache:
            image = self.rot_cache[self.rot]
        else:
            image = pg.transform.rotate(self.image_clean, self.rot)
            self.rot_cache[self.rot] = image
        old_center = self.rect.center
        self.image = image
        self.rect = self.image.get_rect(center=old_center)

    def update(self):
        self.rotate()
        self.rect.center += self.vel
        if self.rect.left < -self.rect.width:
            self.rect.left = WIDTH
        if self.rect.right > WIDTH + self.rect.width:
            self.rect.right = 0
        if self.rect.top < -self.rect.height:
            self.rect.top = HEIGHT
        if self.rect.bottom > HEIGHT + self.rect.height:
            self.rect.bottom = 0

class Bullet(pg.sprite.Sprite):
    def __init__(self, ship, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.ship = ship
        self.image = pg.transform.rotate(self.ship.game.bullet_img, self.ship.rot)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.pos = self.ship.pos - pg.math.Vector2(0, 20).rotate(-self.ship.rot)
        self.vel = self.ship.vel + -pg.math.Vector2(0, 8).rotate(-self.ship.rot)
        # self.vel = -pg.math.Vector2(0, 12).rotate(-self.ship.rot)
        self.spawn_time = pg.time.get_ticks()
        self.lifetime = 2000

    def update(self):
        now = pg.time.get_ticks()
        if now - self.spawn_time > self.lifetime:
            self.kill()
        self.pos += self.vel
        self.rect.center = self.pos
        # wrap around?

class Game:
    def __init__(self):
        pg.init()
        # pygame.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()

    def new(self):
        # initialize all your variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.rocks = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.player = Player(self, self.player_img, [self.all_sprites])
        for i in range(3):
            Rock(self, 3, None, [self.all_sprites, self.rocks])
        self.score = 0

    def load_data(self):
        self.player_img = pg.image.load(path.join(img_dir, 'playerShip1_red.png')).convert()
        self.player_img = pg.transform.rotozoom(self.player_img, 0, 0.6)
        self.rock_images = []
        for size in ['tiny', 'small', 'med', 'big']:
            images = []
            for i in (1, 2):
                fname = 'meteorGrey_{}{}.png'.format(size, i)
                img = pg.image.load(path.join(img_dir, fname)).convert()
                images.append(img)
            self.rock_images.append(images)
        self.bullet_img = pg.image.load(path.join(img_dir, 'laserBlue01.png')).convert()
        self.bullet_img = pg.transform.rotozoom(self.bullet_img, 0, 0.4)

    def run(self):
        # The Game loop - set self.running to False to end the game
        self.running = True
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # the update part of the game loop
        self.all_sprites.update()
        # collide bullets with rocks, each hit spawns two smaller rocks
        hits = pg.sprite.groupcollide(self.rocks, self.bullets, True, True)
        for hit in hits:
            self.score += 4 - hit.size
            if hit.size > 0:
                Rock(self, hit.size - 1, hit.rect.center, [self.all_sprites, self.rocks])
                Rock(self, hit.size - 1, hit.rect.center, [self.all_sprites, self.rocks])
        # collide rocks with player
        hits = pg.sprite.spritecollide(self.player, self.rocks, True)
        if hits:
            # decrease shield / lives
            pass

    def draw(self):
        # draw everything to the screen
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            # this one checks for the window being closed
            if event.type == pg.QUIT:
                self.quit()
            # add any other events here (keys, mouse, etc.)

    def show_start_screen(self):
        # show the start screen
        pass

    def show_go_screen(self):
        # show the game over screen
        pass

# create the game object
g = Game()
while True:
    g.show_start_screen()
    g.new()
    g.run()
    g.show_go_screen()