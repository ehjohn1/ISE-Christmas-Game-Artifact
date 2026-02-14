import pygame
import random

# Initialize Pygame
pygame.init()

# PC Gamer Screen Setup (Standard Laptop Resolution)
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_available_data_results = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ISE: North Pole Protocol - Trial Level")

# Colors
WHITE = (255, 255, 255)
GLOW_BLUE = (173, 216, 230)

# Player Setup
player_pos = [WIDTH // 2, HEIGHT // 2]
particles = []

def draw_particles():
    for p in particles:
        p[0][0] += p[1][0]
        p[0][1] += p[1][1]
        p[2] -= 0.1
        pygame.draw.circle(screen, GLOW_BLUE, [int(p[0][0]), int(p[0][1])], int(p[2]))
    return [p for p in particles if p[2] > 0]

running = True
while running:
    screen.fill((20, 20, 40)) # Dark night sky color
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # PC Controls (WASD)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player_pos[1] -= 5
    if keys[pygame.K_s]: player_pos[1] += 5
    if keys[pygame.K_a]: player_pos[0] -= 5
    if keys[pygame.K_d]: player_pos[0] += 5

    # Special Effect: Particle Trail (Sugar Rush teaser)
    particles.append([[player_pos[0] + 25, player_pos[1] + 25], [random.randint(-2, 2), random.randint(-2, 2)], 5])
    particles = draw_particles()

    # Draw Placeholder Elf
    pygame.draw.rect(screen, (0, 255, 0), (player_pos[0], player_pos[1], 50, 50))
    
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
