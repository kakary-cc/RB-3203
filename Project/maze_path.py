import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Exploration Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Player attributes
player_pos = [WIDTH // 2, 750]
player_angle = math.pi / 2
player_speed = 2
path = [player_pos[:]]

# Arrow attributes
arrow_points = [(0, -15), (10, 15), (0, 10), (-10, 15)]

# Game loop
running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos[0] += player_speed * math.cos(player_angle)
        player_pos[1] -= player_speed * math.sin(player_angle)
    if keys[pygame.K_s]:
        player_pos[0] -= player_speed * math.cos(player_angle)
        player_pos[1] += player_speed * math.sin(player_angle)
    if keys[pygame.K_a]:
        player_angle += 0.05
    if keys[pygame.K_d]:
        player_angle -= 0.05

    # Draw player
    rotated_arrow = [(p[0] * math.sin(player_angle) - p[1] * math.cos(player_angle),
                      p[0] * math.cos(player_angle) + p[1] * math.sin(player_angle))
                     for p in arrow_points]
    transformed_arrow = [(int(p[0] + player_pos[0]), int(p[1] + player_pos[1])) for p in rotated_arrow]
    pygame.draw.polygon(screen, BLACK, transformed_arrow)

    # Draw path
    path.append(player_pos[:])
    for i in range(len(path)-1):
        pygame.draw.line(screen, RED, path[i], path[i+1], 2)

    pygame.display.flip()

pygame.quit()
sys.exit()
