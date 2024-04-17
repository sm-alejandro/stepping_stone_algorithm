import pygame
import sys
import constants
from classes import *

# Initialize Pygame
pygame.init()
FONT = pygame.font.Font(None, constants.FONT_SIZE)


# Set up the screen
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Stepping stone algorithm")


quantity_table = Table(constants.quantity_values, screen)
cost_table = Table(constants.cost_values)
costs = quantity_table.calculate_costs(cost_table)
print(f"COSTS FOR THIS PATH: {costs}")
editing = False
# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:  # Left Click
                editing = quantity_table.handle_click(mouse_pos, cost_table)
                editing = cost_table.handle_click(mouse_pos, cost_table)
            elif pygame.mouse.get_pressed()[2]:  # Right Click
                quantity_table.handle_click(mouse_pos, cost_table, False)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quantity_table.deselect()
                cost_table.deselect()
            elif event.key == pygame.K_u:
                quantity_table.update_table(cost_table)
            else:
                quantity_table.handle_input(event)
                cost_table.handle_input(event)

    screen.fill(constants.GRAY)
    editing = quantity_table.draw_table(screen=screen, y_offset=0, editing=not editing)
    editing = cost_table.draw_table(screen=screen, y_offset=300, editing=not editing)

    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
