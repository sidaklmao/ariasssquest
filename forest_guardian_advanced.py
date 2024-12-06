import pygame
import random
import math
import time
import sys
import os


def resource_path(relative_path):
    """ Get the absolute path to a resource (works with PyInstaller) """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gaia's Quest")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Fonts
font = pygame.font.Font(resource_path("zapf_international_bold.ttf"), 24)
story_font = pygame.font.Font(resource_path("zapf_international_bold.ttf"), 28)

# Game clock
clock = pygame.time.Clock()
FPS = 60

# Story Text
story_text = [
    "Planet Earth has been pushed to its limits.",
    "Years of pollution, unchecked industrial growth, and disregard",
    "for nature have awakened monstrous entities that embody",
    "the damage caused by human negligence.",
    "",
    "These forces of destruction—Trash Titan, Oilbeast, and Smogzilla—",
    "now threaten to make the planet uninhabitable.",
    "",
    "You play as Aria, a courageous Climate Hero who is chosen",
    "by Earth itself to restore balance and save the planet.",
    "Guided by Earth’s spirit, Aria must travel across polluted",
    "environments, defeat the forces of destruction,",
    "and heal the scars of human negligence."
]

# Load assets
player_img = pygame.image.load(resource_path("aria.png"))
player_img = pygame.transform.scale(player_img, (50, 50))

boss_sprites = [
    pygame.image.load(resource_path("trashtitan.png")),
    pygame.image.load(resource_path("oilbeast.png")),
    pygame.image.load(resource_path("smogzilla.png"))
]
boss_sprites = [pygame.transform.scale(sprite, (100, 100)) for sprite in boss_sprites]

backgrounds = [
    pygame.image.load(resource_path("level1bg.png")),
    pygame.image.load(resource_path("lvl2bg.png")),
    pygame.image.load(resource_path("lvl3bg.png"))
]
backgrounds = [pygame.transform.scale(bg, (WIDTH, HEIGHT)) for bg in backgrounds]

boss_attack_sprites = [
    pygame.image.load(resource_path("trashcan.png")),
    pygame.image.load(resource_path("oilb.png")),
    pygame.image.load(resource_path("emission.png"))
]
boss_attack_sprites = [pygame.transform.scale(attack, (15, 15)) for attack in boss_attack_sprites]

# Player setup
player_x, player_y = WIDTH // 2, HEIGHT - 100
player_speed = 5
player_health = 250
player_max_health = 250

# Shield setup
shield_active = False
shield_timer = 0
shield_duration = 180  # Frames (3 seconds at 60 FPS)
shield_cooldown = 300  # Frames (5 seconds at 60 FPS)
shield_ready = True
shield_img = pygame.Surface((60, 60), pygame.SRCALPHA)  # Transparent shield
pygame.draw.circle(shield_img, (0, 255, 255, 128), (30, 30), 30)  # Cyan semi-transparent shield

# Bullets
bullet_img = pygame.Surface((10, 10))
bullet_img.fill(WHITE)
bullets = []
bullet_speed = -10
can_shoot = False
shoot_timer = 0
shoot_interval = random.randint(300, 660)
shoot_duration = random.randint(300, 420)

# Boss setup
bosses = [
    {"health": 3000, "speed": 3, "fire_rate": 0.01},
    {"health": 6000, "speed": 4, "fire_rate": 0.02},
    {"health": 10000, "speed": 5, "fire_rate": 0.03}
]
current_boss_level = 0
boss_health = bosses[current_boss_level]["health"]
boss_x, boss_y = WIDTH // 2 - 50, 50
boss_bullets = []

# Game state
running = True
game_started = False
game_over = False
victory = False


def draw_text(text, x, y, color=WHITE):
    """Renders text on the screen."""
    label = font.render(text, True, color)
    screen.blit(label, (x, y))


def draw_story():
    """Displays the static story screen."""
    screen.fill(BLACK)  # Black background for the story
    for i, line in enumerate(story_text):
        text_surface = story_font.render(line, True, WHITE)
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, 50 + i * 40))
    pygame.display.flip()


def reset_level():
    """Resets the level for the current boss."""
    global player_x, player_y, player_health, bullets, boss_bullets, game_over, victory, can_shoot, shoot_timer, shoot_interval, shoot_duration
    global boss_x, boss_y, boss_health, shield_active, shield_timer, shield_ready
    player_x, player_y = WIDTH // 2, HEIGHT - 100
    player_health = player_max_health
    bullets = []
    boss_bullets = []
    game_over = False
    victory = False
    can_shoot = False
    shoot_timer = 0
    boss_x, boss_y = WIDTH // 2 - 50, 50
    boss_health = bosses[current_boss_level]["health"]
    shoot_interval = random.randint(300, 660)
    shoot_duration = random.randint(300, 420)
    shield_active = False
    shield_ready = True


def next_level():
    """Moves to the next boss level or ends the game if all bosses are defeated."""
    global current_boss_level, boss_health, player_health
    current_boss_level += 1
    if current_boss_level < len(bosses):
        boss_health = bosses[current_boss_level]["health"]
        player_health = player_max_health
        reset_level()
    else:
        global victory
        victory = True


# Show the story screen for 5 seconds
draw_story()
time.sleep(5)
game_started = True

# Main Game Loop
while running:
    if game_started:
        screen.blit(backgrounds[current_boss_level], (0, 0))  # Draw background

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - 50:
            player_x += player_speed
        if keys[pygame.K_UP] and player_y > boss_y + 150:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < boss_y + 400:
            player_y += player_speed
        if keys[pygame.K_d] and shield_ready:  # Activate shield
            shield_active = True
            shield_timer = 0
            shield_ready = False

        # Shield logic
        if shield_active:
            shield_timer += 1
            if shield_timer > shield_duration:
                shield_active = False
                shield_timer = 0
        else:
            if not shield_ready:
                shield_timer += 1
                if shield_timer > shield_cooldown:
                    shield_ready = True
                    shield_timer = 0

        # Handle shooting
        shoot_timer += 1
        if not can_shoot and shoot_timer >= shoot_interval:
            can_shoot = True
            shoot_timer = 0
            shoot_duration = random.randint(300, 420)

        if can_shoot and shoot_timer >= shoot_duration:
            can_shoot = False
            shoot_timer = 0
            shoot_interval = random.randint(300, 660)

        if keys[pygame.K_SPACE] and can_shoot and len(bullets) < 5:
            bullets.append([player_x + 20, player_y])

        # Update bullets
        for bullet in bullets[:]:
            bullet[1] += bullet_speed
            if bullet[1] < 0:
                bullets.remove(bullet)
            elif boss_x < bullet[0] < boss_x + 100 and boss_y < bullet[1] < boss_y + 100:
                boss_health -= 10
                bullets.remove(bullet)

        # Boss attacks
        boss_speed = bosses[current_boss_level]["speed"]
        fire_rate = bosses[current_boss_level]["fire_rate"]

        if not game_over and random.random() < fire_rate:
            dx = player_x + 25 - (boss_x + 50)
            dy = player_y + 25 - (boss_y + 50)
            distance = math.hypot(dx, dy)
            if distance != 0:
                vx = boss_speed * (dx / distance)
                vy = boss_speed * (dy / distance)
                boss_bullets.append([boss_x + 50, boss_y + 50, vx, vy])

        for boss_bullet in boss_bullets[:]:
            boss_bullet[0] += boss_bullet[2]
            boss_bullet[1] += boss_bullet[3]
            if boss_bullet[1] > HEIGHT or boss_bullet[0] < 0 or boss_bullet[0] > WIDTH:
                boss_bullets.remove(boss_bullet)
            elif player_x < boss_bullet[0] < player_x + 50 and player_y < boss_bullet[1] < player_y + 50:
                if shield_active:
                    boss_bullets.remove(boss_bullet)  # Absorbed by shield
                else:
                    player_health -= 10
                    boss_bullets.remove(boss_bullet)

        # Check game state
        if player_health <= 0:
            game_over = True
        if boss_health <= 0:
            next_level()

        # Draw entities
        screen.blit(player_img, (player_x, player_y))
        if shield_active:
            screen.blit(shield_img, (player_x - 5, player_y - 5))  # Draw shield
        screen.blit(boss_sprites[current_boss_level], (boss_x, boss_y))

        for bullet in bullets:
            screen.blit(bullet_img, (bullet[0], bullet[1]))

        for boss_bullet in boss_bullets:
            screen.blit(boss_attack_sprites[current_boss_level], (boss_bullet[0], boss_bullet[1]))

        # Draw health bars
        pygame.draw.rect(screen, RED, (50, HEIGHT - 50, 200, 20))
        pygame.draw.rect(screen, GREEN, (50, HEIGHT - 50, 200 * (player_health / player_max_health), 20))
        pygame.draw.rect(screen, RED, (WIDTH - 250, 50, 200, 20))
        pygame.draw.rect(screen, GREEN, (WIDTH - 250, 50, 200 * (boss_health / bosses[current_boss_level]["health"]), 20))

        # Text
        draw_text("Player Health", 50, HEIGHT - 80)
        draw_text("Boss Health", WIDTH - 250, 20)
        draw_text(f"Level: {current_boss_level + 1}", WIDTH // 2 - 50, 20)

        if can_shoot:
            draw_text("Shoot Now!", WIDTH // 2 - 50, HEIGHT - 80, BLACK)  # Changed to black

        if not shield_ready:
            draw_text(f"Shield Cooldown: {shield_cooldown // 60 - shield_timer // 60}s", WIDTH // 2 - 100, HEIGHT - 120, RED)
        elif not shield_active:
            draw_text("Shield Ready! (Press D)", WIDTH // 2 - 100, HEIGHT - 120, BLACK)  # Changed to black


        if game_over:
            draw_text("GAME OVER", WIDTH // 2 - 100, HEIGHT // 2, RED)
            draw_text("Press R to Restart", WIDTH // 2 - 120, HEIGHT // 2 + 40)
            if keys[pygame.K_r]:
                current_boss_level = 0
                reset_level()

        if victory:
            draw_text("VICTORY!", WIDTH // 2 - 100, HEIGHT // 2, GREEN)
            draw_text("Press R to Restart", WIDTH // 2 - 120, HEIGHT // 2 + 40)
            if keys[pygame.K_r]:
                current_boss_level = 0
                reset_level()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
