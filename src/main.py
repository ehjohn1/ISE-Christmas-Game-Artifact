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
WHITE = (255, 255, 255)
GLOW_BLUE = (173, 216, 230)
DARK_NAVY = (20, 20, 40)
GRAY = (100, 100, 100)
GOLD = (255, 215, 0)

# Fonts
font_main = pygame.font.SysFont("Arial", 80, bold=True)
font_sub = pygame.font.SysFont("Arial", 30)

# Game States
STATE_MENU = "MENU"
STATE_STORY = "STORY"
STATE_LEVEL_SELECT = "LEVEL_SELECT"
STATE_GAME = "GAME"
STATE_EASTER_EGG = "EASTER_EGG"

# Progression Variables
current_state = STATE_MENU
unlocked_levels = 1  # Start with only Level 1 unlocked
active_level = 1
player_pos = [WIDTH // 2, HEIGHT // 2]
particles = []

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x - img.get_width()//2, y))

def main_menu():
    screen.fill(DARK_NAVY)
    draw_text("NORTH POLE PROTOCOL", font_main, GLOW_BLUE, WIDTH//2, 150)
    mouse = pygame.mouse.get_pos()
    button_rect = pygame.Rect(WIDTH//2 - 125, 400, 250, 60)
    color = (0, 200, 0) if button_rect.collidepoint(mouse) else (0, 150, 0)
    pygame.draw.rect(screen, color, button_rect, border_radius=10)
    draw_text("ENTER MISSION", font_sub, WHITE, WIDTH//2, 415)
    return button_rect

def story_screen():
    screen.fill((0, 0, 0))
    story_text = [
        "The North Pole's automation has been hacked.",
        "A rogue Elf has turned the toys into a robotic army.",
        "Your mission: Stop the Glitch Elf and save Christmas.",
        "",
        "[ Press SPACE to View Missions ]"
    ]
    for i, line in enumerate(story_text):
        draw_text(line, font_sub, WHITE, WIDTH//2, 200 + (i * 50))

def level_select_screen():
    screen.fill(DARK_NAVY)
    draw_text("MISSION SELECTOR", font_main, GLOW_BLUE, WIDTH//2, 80)
    mouse = pygame.mouse.get_pos()
    level_rects = []
    
    for i in range(1, 7):
        # Grid Layout: 3 columns, 2 rows
        col = (i-1) % 3
        row = (i-1) // 3
        x = 300 + (col * 350)
        y = 300 + (row * 180)
        
        rect = pygame.Rect(x-100, y, 200, 100)
        is_unlocked = i <= unlocked_levels
        
        if is_unlocked:
            color = (0, 180, 0) if rect.collidepoint(mouse) else (0, 120, 0)
        else:
            color = (60, 60, 60) # Dark Gray for locked
            
        pygame.draw.rect(screen, color, rect, border_radius=15)
        label = f"LEVEL {i}" if is_unlocked else "LOCKED"
        draw_text(label, font_sub, WHITE, x, y + 35)
        level_rects.append((rect, i))
    
    draw_text("[ PRESS 'C' TO DEBUG: UNLOCK NEXT LEVEL ]", font_sub, GOLD, WIDTH//2, 650)
    return level_rects

def easter_egg_screen():
    screen.fill((10, 50, 10)) # Christmas Green
    draw_text("GLITCH ELF DEFEATED!", font_main, GOLD, WIDTH//2, 200)
    draw_text("Christmas is safe... for now.", font_sub, WHITE, WIDTH//2, 350)
    draw_text("PART 2: THE REVENGE - COMING CHRISTMAS 2026", font_sub, GLOW_BLUE, WIDTH//2, 450)
    draw_text("[ Press ESC for Menu ]", font_sub, WHITE, WIDTH//2, 550)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Menu Transitions
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == STATE_MENU:
                if main_menu().collidepoint(event.pos):
                    current_state = STATE_STORY
            
            elif current_state == STATE_LEVEL_SELECT:
                for rect, lvl_num in level_select_screen():
                    if rect.collidepoint(event.pos) and lvl_num <= unlocked_levels:
                        active_level = lvl_num
                        current_state = STATE_GAME

        if event.type == pygame.KEYDOWN:
            if current_state == STATE_STORY and event.key == pygame.K_SPACE:
                current_state = STATE_LEVEL_SELECT
            
            if current_state == STATE_LEVEL_SELECT and event.key == pygame.K_c:
                if unlocked_levels < 6: unlocked_levels += 1 # Debug Unlock
            
            if event.key == pygame.K_ESCAPE:
                current_state = STATE_MENU

    # State Rendering
    if current_state == STATE_MENU:
        main_menu()
    elif current_state == STATE_STORY:
        story_screen()
    elif current_state == STATE_LEVEL_SELECT:
        level_select_screen()
    elif current_state == STATE_EASTER_EGG:
        easter_egg_screen()
    elif current_state == STATE_GAME:
        screen.fill(DARK_NAVY)
        draw_text(f"PLAYING: MISSION {active_level}", font_sub, WHITE, WIDTH//2, 30)
        
        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: player_pos[1] -= 5
        if keys[pygame.K_s]: player_pos[1] += 5
        if keys[pygame.K_a]: player_pos[0] -= 5
        if keys[pygame.K_d]: player_pos[0] += 5

        # Effects & Player
        particles.append([[player_pos[0] + 25, player_pos[1] + 25], [random.randint(-2, 2), random.randint(-2, 2)], 5])
        for p in particles:
            p[0][0] += p[1][0]; p[0][1] += p[1][1]; p[2] -= 0.1
            pygame.draw.circle(screen, GLOW_BLUE, [int(p[0][0]), int(p[0][1])], int(p[2]))
        particles = [p for p in particles if p[2] > 0]
        pygame.draw.rect(screen, (0, 255, 0), (player_pos[0], player_pos[1], 50, 50))

        # Completion Mockup: If player reaches right edge, unlock next
        if player_pos[0] > WIDTH - 60:
            if active_level == 6:
                current_state = STATE_EASTER_EGG
            else:
                if active_level == unlocked_levels:
                    unlocked_levels += 1
                current_state = STATE_LEVEL_SELECT
                player_pos = [WIDTH // 2, HEIGHT // 2] # Reset pos

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
