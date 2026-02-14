import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen Setup
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ISE: North Pole Protocol")

# Colors
WHITE, GLOW_BLUE = (255, 255, 255), (173, 216, 230)
DARK_NAVY, GOLD = (20, 20, 40), (255, 215, 0)

# Fonts
font_main = pygame.font.SysFont("Arial", 80, bold=True)
font_sub = pygame.font.SysFont("Arial", 30)

# Game States
STATE_MENU, STATE_STORY = "MENU", "STORY"
STATE_TUTORIAL, STATE_LEVEL_SELECT = "TUTORIAL", "LEVEL_SELECT"
STATE_GAME, STATE_EASTER_EGG = "GAME", "EASTER_EGG"

# Global Game Variables
current_state = STATE_MENU
unlocked_levels = 0  # 0 means only Tutorial is available
active_level = 0
tutorial_step = 0 # 0: Move, 1: Shoot
player_pos = [WIDTH // 2, HEIGHT // 2]
particles, snowballs, enemies = [], [], []

class Snowball:
    def __init__(self, x, y, target_x, target_y):
        self.pos = [x, y]
        speed = 12
        dx, dy = target_x - x, target_y - y
        dist = (dx**2 + dy**2)**0.5
        self.vel = [dx/dist * speed, dy/dist * speed] if dist != 0 else [speed, 0]

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

class Enemy:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.rect = pygame.Rect(x, y, 40, 40)

    def update(self):
        self.rect.topleft = self.pos

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x - img.get_width()//2, y))

# --- State Functions ---
def main_menu():
    screen.fill(DARK_NAVY)
    draw_text("NORTH POLE PROTOCOL", font_main, GLOW_BLUE, WIDTH//2, 150)
    rect = pygame.Rect(WIDTH//2 - 125, 400, 250, 60)
    color = (0, 200, 0) if rect.collidepoint(pygame.mouse.get_pos()) else (0, 150, 0)
    pygame.draw.rect(screen, color, rect, border_radius=10)
    draw_text("ENTER MISSION", font_sub, WHITE, WIDTH//2, 415)
    return rect

def tutorial_logic():
    global tutorial_step, unlocked_levels, current_state
    screen.fill((30, 50, 80))
    
    if tutorial_step == 0:
        draw_text("STEP 1: USE 'WASD' TO MOVE", font_sub, WHITE, WIDTH//2, 100)
        if player_pos[0] < 100 or player_pos[0] > WIDTH-100: tutorial_step = 1
    elif tutorial_step == 1:
        draw_text("STEP 2: LEFT CLICK TO SHOOT THE TARGET", font_sub, WHITE, WIDTH//2, 100)
        if not enemies: enemies.append(Enemy(WIDTH-200, HEIGHT//2))
        if not enemies: # Target hit
            draw_text("BOOTCAMP COMPLETE! PRESS 'E' TO EXIT", font_sub, GOLD, WIDTH//2, 200)

def level_select_screen():
    screen.fill(DARK_NAVY)
    draw_text("MISSION SELECTOR", font_main, GLOW_BLUE, WIDTH//2, 80)
    mouse = pygame.mouse.get_pos()
    rects = []
    for i in range(1, 7):
        x, y = 300 + ((i-1)%3)*350, 300 + ((i-1)//3)*180
        rect = pygame.Rect(x-100, y, 200, 100)
        is_unlocked = i <= unlocked_levels
        color = (0, 120, 0) if is_unlocked else (60, 60, 60)
        pygame.draw.rect(screen, color, rect, border_radius=15)
        draw_text(f"LEVEL {i}" if is_unlocked else "LOCKED", font_sub, WHITE, x, y+35)
        rects.append((rect, i))
    return rects

# --- Main Game Loop ---
running = True
while running:
    screen.fill(DARK_NAVY)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == STATE_MENU and main_menu().collidepoint(event.pos):
                current_state = STATE_STORY
            elif current_state == STATE_LEVEL_SELECT:
                for r, l in level_select_screen():
                    if r.collidepoint(event.pos) and l <= unlocked_levels:
                        active_level, current_state = l, STATE_GAME
            elif current_state in [STATE_TUTORIAL, STATE_GAME] and event.button == 1:
                snowballs.append(Snowball(player_pos[0]+25, player_pos[1]+25, *event.pos))

        if event.type == pygame.KEYDOWN:
            if current_state == STATE_STORY and event.key == pygame.K_SPACE:
                current_state = STATE_TUTORIAL
            if current_state == STATE_TUTORIAL and event.key == pygame.K_e and tutorial_step == 1 and not enemies:
                unlocked_levels, current_state = 1, STATE_LEVEL_SELECT

    # Rendering States
    if current_state == STATE_MENU: main_menu()
    elif current_state == STATE_STORY:
        screen.fill((0,0,0))
        draw_text("MISSION: ELF BOOTCAMP", font_main, GLOW_BLUE, WIDTH//2, 200)
        draw_text("[ Press SPACE to Start Training ]", font_sub, WHITE, WIDTH//2, 400)
    elif current_state == STATE_TUTORIAL:
        tutorial_logic()
        # Draw Player/Snowballs in tutorial
        pygame.draw.rect(screen, (0, 255, 0), (player_pos[0], player_pos[1], 50, 50))
        for s in snowballs[:]:
            s.update()
            pygame.draw.circle(screen, WHITE, (int(s.pos[0]), int(s.pos[1])), 8)
        for e in enemies[:]:
            pygame.draw.rect(screen, RED, e.rect)
            for s in snowballs[:]:
                if e.rect.collidepoint(s.pos):
                    enemies.remove(e); snowballs.remove(s)
    elif current_state == STATE_LEVEL_SELECT: level_select_screen()
    elif current_state == STATE_GAME:
        draw_text(f"MISSION {active_level} ACTIVE", font_sub, WHITE, WIDTH//2, 50)
        pygame.draw.rect(screen, (0, 255, 0), (player_pos[0], player_pos[1], 50, 50))

    # Basic WASD Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player_pos[1] -= 5
    if keys[pygame.K_s]: player_pos[1] += 5
    if keys[pygame.K_a]: player_pos[0] -= 5
    if keys[pygame.K_d]: player_pos[0] += 5

    pygame.display.flip()
    pygame.time.Clock().tick(60)
pygame.quit()
