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
RED = (200, 0, 0)
DARK_NAVY = (20, 20, 40)

# Fonts
font_main = pygame.font.SysFont("Arial", 80, bold=True)
font_sub = pygame.font.SysFont("Arial", 30)

# Game States
STATE_MENU = "MENU"
STATE_STORY = "STORY"
STATE_GAME = "GAME"
current_state = STATE_MENU

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x - img.get_width()//2, y))

def main_menu():
    screen.fill(DARK_NAVY)
    draw_text("NORTH POLE PROTOCOL", font_main, GLOW_BLUE, WIDTH//2, 150)
    
    # Simple Button Logic
    mouse = pygame.mouse.get_pos()
    button_rect = pygame.Rect(WIDTH//2 - 100, 400, 200, 60)
    
    color = (0, 200, 0) if button_rect.collidepoint(mouse) else (0, 150, 0)
    pygame.draw.rect(screen, color, button_rect, border_radius=10)
    draw_text("START GAME", font_sub, WHITE, WIDTH//2, 415)
    
    return button_rect

def story_screen():
    screen.fill((0, 0, 0)) # Cinematic Black
    story_text = [
        "The North Pole's automation has been hacked.",
        "A rogue Elf has turned the toys into a robotic army.",
        "You are the Guardian Elf.",
        "Your mission: Stop the Glitch Elf and save Christmas.",
        "",
        "[ Press SPACE to Begin Protocol ]"
    ]
    for i, line in enumerate(story_text):
        draw_text(line, font_sub, WHITE, WIDTH//2, 150 + (i * 50))

# Player Vars
player_pos = [WIDTH // 2, HEIGHT // 2]
particles = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and current_state == STATE_MENU:
            if main_menu().collidepoint(event.pos):
                current_state = STATE_STORY
                
        if event.type == pygame.KEYDOWN and current_state == STATE_STORY:
            if event.key == pygame.K_SPACE:
                current_state = STATE_GAME

    if current_state == STATE_MENU:
        main_menu()
        
    elif current_state == STATE_STORY:
        story_screen()
        
    elif current_state == STATE_GAME:
        screen.fill(DARK_NAVY)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: player_pos[1] -= 5
        if keys[pygame.K_s]: player_pos[1] += 5
        if keys[pygame.K_a]: player_pos[0] -= 5
        if keys[pygame.K_d]: player_pos[0] += 5

        # Particle Effect
        particles.append([[player_pos[0] + 25, player_pos[1] + 25], [random.randint(-2, 2), random.randint(-2, 2)], 5])
        for p in particles:
            p[0][0] += p[1][0]; p[0][1] += p[1][1]; p[2] -= 0.1
            pygame.draw.circle(screen, GLOW_BLUE, [int(p[0][0]), int(p[0][1])], int(p[2]))
        particles = [p for p in particles if p[2] > 0]

        pygame.draw.rect(screen, (0, 255, 0), (player_pos[0], player_pos[1], 50, 50))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
