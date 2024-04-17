import pygame
import sys
import constants
from classes import *

# Initialize Pygame
pygame.init()
FONT = pygame.font.Font(None, constants.FONT_SIZE)


class Button:
    def __init__(self, rect, color, text, text_color, action):
        self.rect = rect
        self.color = color
        self.text = text
        self.text_color = text_color
        self.action = action

    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_click(self, pos):
        return self.rect.collidepoint(pos)


# Function to edit a cell
def edit_cell(screen, values, i, j, y_offset):
    font = pygame.font.Font(None, FONT_SIZE)
    input_text = ""
    editing = True

    while editing:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if calculate_button.check_click(mouse_pos):
                    print("Calculate button clicked!")
                    pygame.draw.rect(
                        screen,
                        RED,
                        (
                            start_x + (j + 1) * CELL_WIDTH,
                            (i + 3) * CELL_HEIGHT + y_offset,
                            CELL_WIDTH,
                            CELL_HEIGHT,
                        ),
                        3,
                    )
                else:
                    editing = False
                    mouse_pos = pygame.mouse.get_pos()
                    if mouse_pos[1] < (SCREEN_HEIGHT // 2) + CELL_HEIGHT * 2:
                        cell_x = (mouse_pos[0] - start_x - CELL_WIDTH) // CELL_WIDTH
                        cell_y = (mouse_pos[1] - CELL_HEIGHT * 2) // CELL_HEIGHT
                    if 0 <= cell_y < len(table_values_quantity) and 0 <= cell_x < len(
                        table_values_quantity[0]
                    ):
                        edit_cell(screen, table_values_quantity, cell_y, cell_x, 0)
                    elif (
                        (SCREEN_HEIGHT // 2) + CELL_HEIGHT * 2
                        <= mouse_pos[1]
                        < SCREEN_HEIGHT
                    ):
                        cell_x = (mouse_pos[0] - start_x - CELL_WIDTH) // CELL_WIDTH
                        cell_y = (
                            mouse_pos[1] - SCREEN_HEIGHT // 2 - CELL_HEIGHT * 2
                        ) // CELL_HEIGHT
                        if 0 <= cell_y < len(table_values_costs) and 0 <= cell_x < len(
                            table_values_costs[0]
                        ):
                            edit_cell(
                                screen,
                                table_values_costs,
                                cell_y,
                                cell_x,
                                SCREEN_HEIGHT // 2,
                            )

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        values[i][j] = int(input_text)
                    except ValueError:
                        pass
                    editing = False
                if event.key == pygame.K_ESCAPE:
                    editing = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_TAB:
                    if j < len(values[0]) - 1:
                        try:
                            values[i][j] = int(
                                input_text
                            )  # Save the change before moving to the next cell
                        except:
                            pass
                        editing = False
                        edit_cell(screen, values, i, j + 1, y_offset)
                    elif i < len(values) - 1:
                        try:
                            values[i][j] = int(
                                input_text
                            )  # Save the change before moving to the next cell
                        except:
                            pass
                        editing = False
                        edit_cell(screen, values, i + 1, 0, y_offset)
                    else:
                        try:
                            values[i][j] = int(
                                input_text
                            )  # Save the change before exiting editing mode
                        except:
                            pass
                        editing = False
                else:
                    input_text += event.unicode

        screen.fill(WHITE)

        # Draw the "Calculate" button
        if values[i][j] < 0:
            calculate_button.draw(screen, pygame.font.Font(None, FONT_SIZE))

        draw_table(screen, values, "", y_offset)

        if i >= 0 and j >= 0:
            # Highlight the current cell being edited
            pygame.draw.rect(
                screen,
                RED,
                (
                    start_x + (j + 1) * CELL_WIDTH,
                    (i + 2) * CELL_HEIGHT + y_offset,
                    CELL_WIDTH,
                    CELL_HEIGHT,
                ),
                3,
            )

            # Render the input text
            input_surface = font.render(input_text, True, BLACK)
            screen.blit(
                input_surface,
                (
                    start_x + (j + 1) * CELL_WIDTH + 10,
                    (i + 2) * CELL_HEIGHT + 10 + y_offset,
                ),
            )

        pygame.display.flip()


# Set up the screen
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Stepping stone algorithm")

# Create the "Calculate" button
calculate_button_rect = pygame.Rect(10, 10, 100, 40)
calculate_button = Button(
    calculate_button_rect,
    constants.WHITE,
    "Calculate",
    constants.BLACK,
    lambda: print("Calculating..."),
)

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
            if pygame.mouse.get_pressed()[0]:  # left
                editing = quantity_table.handle_click(mouse_pos, cost_table)
                editing = cost_table.handle_click(mouse_pos, cost_table)
            elif pygame.mouse.get_pressed()[2]:  # Right click
                quantity_table.handle_click(mouse_pos, cost_table, False)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quantity_table.deselect()
                cost_table.deselect()
            elif event.key == pygame.K_u:
                quantity_table.update_table(cost_table)

    screen.fill(constants.GRAY)
    editing = quantity_table.draw_table(screen=screen, y_offset=0, editing=not editing)
    editing = cost_table.draw_table(screen=screen, y_offset=300, editing=not editing)

    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
