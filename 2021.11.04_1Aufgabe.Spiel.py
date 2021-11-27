import pygame 
import os
from random import randint 

class Settings(object):
    window_height = 1000
    window_width = 800
    path_file = os.path.dirname(os.path.abspath(__file__))
    path_image = os.path.join(path_file, "images")
    title = "Pygame Squirrel"

    # Overlay Settings
    font_size = 25
    font_color = (255,255,255)

    # Game Settings
    max_spawn_counter = 100
    limit_spawn_counter = 30
    spawn_multiplier = 0.1
    
    limit_speed_counter = 10
    speed_multiplier = 0.05


    # Player Settings
    player_size = (60,70)
    player_speed = 10
    player_default_lives = 3
    player_default_points = 0

    # Killer Settings
    killer_size = (25,75)
    killer_speed = (1,3)
    killer_points_per_collect = 1

class Background(pygame.sprite.Sprite):
    def __init__(self, filename) -> None:
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert()
        self.image = pygame.transform.scale(self.image, (Settings.window_width, Settings.window_height))
      
    # Damit der Bei Null anfängt zu "zeichnen"
    def draw(self, screen):
        screen.blit(self.image,(0,0))

class Player(pygame.sprite.Sprite):
    def __init__(self, filename) -> None:
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (Settings.player_size))
        self.rect = self.image.get_rect()
        self.spawn()
    # Player spawnpoint
    def spawn(self):
        self.rect.centerx = Settings.window_width // 2
        self.rect.bottom  = Settings.window_height - self.rect.height * 2
    # Player Bewegung         
    def move_up(self):
        if self.rect.top - Settings.player_speed >= 0:
            self.rect.top -= Settings.player_speed 

    def move_down(self):
        if self.rect.bottom + Settings.player_speed <= Settings.window_height:
            self.rect.top += Settings.player_speed

    def move_left(self):
        if self.rect.left - Settings.player_speed >= 0:
            self.rect.left -= Settings.player_speed

    def move_right(self):
        if self.rect.right + Settings.player_speed <= Settings.window_width:
            self.rect.left += Settings.player_speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Killer(pygame.sprite.Sprite):
    def __init__(self, filename, speed) -> None:
        super().__init__()
        self.size = randint(Settings.killer_size[0], Settings.killer_size[1])
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect.left = randint(0, Settings.window_width - self.rect.width)
        self.rect.top = -self.rect.height
        self.speed = speed
    # Leben Berechnung der Player + Killer respawn
    def update(self):
        self.rect.top += self.speed

        if self.rect.top >= Settings.window_height:
            game.killers.remove(self)
            game.points += Settings.killer_points_per_collect 

        if pygame.sprite.spritecollide(self, game.player, False, pygame.sprite.collide_mask):
            game.lives -= 1

            if game.lives <= 0:
                game.reset()

            game.player.sprite.spawn()
            game.killers.empty()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Game(object):
    def __init__(self) -> None:
        super().__init__()
        # Init PyGame Settings
        pygame.init()
        pygame.display.set_caption(Settings.title)

        self.screen = pygame.display.set_mode((Settings.window_width, Settings.window_height))
        self.clock = pygame.time.Clock()
        
        # Sprites und Killer erscheinen
        self.background = Background("background.png")
        self.killers = pygame.sprite.Group()

        self.spawn_counter = 0
        self.max_spawn_counter = Settings.max_spawn_counter

        # Player
        self.player = pygame.sprite.GroupSingle()
        self.player.add(Player("pilot1.png"))

        # Stats
        self.lives = Settings.player_default_lives
        self.points = Settings.player_default_points

        # Overlay
        self.overlay_font = pygame.font.SysFont(None, Settings.font_size)

        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.watch_for_events()
            self.update()
            self.draw()
        pygame.quit()
    # Damit der Killer nicht Uendlich weiter spawned und ich nicht Millionen Sprites auf dem Bildschirm habe
    def spawn(self):
        self.spawn_counter += 1
        max_spawn_multiplier_counter = self.max_spawn_counter - Settings.spawn_multiplier * self.points
        if max_spawn_multiplier_counter <= Settings.limit_spawn_counter:
            max_spawn_multiplier_counter = Settings.limit_spawn_counter

        if self.spawn_counter >= max_spawn_multiplier_counter:
            self.spawn_counter = 0

            # Random Killer speed
            killer_speed = randint(Settings.killer_speed[0], Settings.killer_speed[1])
            # Multiplier Speed
            killer_speed_multiplier = killer_speed + Settings.speed_multiplier * self.points
            print(killer_speed_multiplier)
            # Max multiplier speed
            if killer_speed_multiplier >= Settings.limit_speed_counter:
                killer_speed_multiplier = Settings.limit_speed_counter

            self.killers.add(Killer("killer.png", killer_speed_multiplier))

    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.QUIT:
                self.running = False
        # Spieler Movement
        press = pygame.key.get_pressed()
        if press[pygame.K_UP] or press[pygame.K_w]:
            self.player.sprite.move_up()
        if press[pygame.K_DOWN] or press[pygame.K_s]:
            self.player.sprite.move_down()
        if press[pygame.K_RIGHT] or press[pygame.K_d]:
            self.player.sprite.move_right()
        if press[pygame.K_LEFT] or press[pygame.K_a]:
            self.player.sprite.move_left()
    # Bei Verlieren alles auf Null setzen
    def reset(self):
        self.points = Settings.player_default_points
        self.lives = Settings.player_default_lives
    # Text für die Punkte und Lebensanzeige
    def render_overlay(self):
        point_text = self.overlay_font.render(f"Punkte: {self.points}", True, Settings.font_color)
        self.screen.blit(point_text, (32,32))

        lives_text = self.overlay_font.render(f"Leben: {self.lives}", True, Settings.font_color)
        self.screen.blit(lives_text, (32, 48 + point_text.get_rect().height))

    def update(self):
        self.spawn()
        self.killers.update()
        self.player.sprite.update()

    def draw(self):
        self.background.draw(self.screen)
        self.killers.draw(self.screen)
        self.player.sprite.draw(self.screen)
        self.render_overlay()
        pygame.display.flip()


if __name__ == "__main__":
    os.environ["SDL_VIDEO_WINDOW_POS"] = "500, 50"

    game = Game()
    game.run()