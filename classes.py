import time
import pygame
import constants
from tkinter import Tk, messagebox


class Table:
    editing = (-1, -1)
    calculating = []
    starting = None
    content = None
    num_rows = 0
    num_columns = 0
    horizontal = True
    eval = []
    costs = []
    cost = -1

    def __init__(self, values, screen=None):
        self.screen = screen
        self.content = [
            [Cell(j, x, y) for x, j in enumerate(i)] for y, i in enumerate(values)
        ]
        self.num_rows = len(self.content)
        self.num_columns = len(self.content[0])
        print(f"rows: {self.num_rows}, columns: {self.num_columns}")

    def pprint(self):
        for i in self.content:
            [print(j, end=" ") for j in i]
            print()

    def add_costs(self, costs):
        self.costs = costs

    def calculate_paths(self, sleep=0.1):
        while True:
            self.screen.fill(constants.GRAY)
            self.draw_table(self.screen, 0, False)
            pygame.display.flip()
            prev_calculating = self.calculating.copy()
            self._calculate_step()
            if self.calculating == prev_calculating:
                break  # hasn't found new ways
            time.sleep(sleep)
            # while True:
            #     if pygame.event.wait().type == pygame.KEYDOWN:
            #         break
        self.calculating = [i for i in self.calculating if len(i) % 2 == 1]

    def calculate_costs(self):
        total = 0
        for j, column in enumerate(self.content):
            for i, cell in enumerate(column):
                if cell.value > 0:
                    total += cell.value * self.costs.content[j][i].value
        self.cost = total
        return total

    def auto_find(self):
        lowest = 9999999
        lowest_cell = (-1, -1)
        for j in range(self.num_rows):
            for i in range(self.num_columns):
                self.set_calculating(j, i)
                print(i, j)
                self.calculate_paths(sleep=0.1)
                try:
                    low = min([self.evaluate_path(x) for x in self.calculating])
                except:
                    continue
                print(low)
                if low < lowest:
                    lowest = low
                    lowest_cell = (j, i)
        print(lowest)
        if lowest < 0:
            self.set_calculating(lowest_cell[0], lowest_cell[1])
            self.calculate_paths(sleep=0.3)
            self.update_table()
            self.auto_find()
        self.deselect()

    def evaluate_path(self, path):
        mult = True
        sum = 0
        for item in path[:-1]:
            sum += self.costs.content[item.y][item.x].value * (1 if mult else -1)
            mult = not mult
        print(sum)
        return sum

    def update_table(self):
        print(f"sc {self.calculating}")
        if not self.calculating:
            return
        min_costs = 100000
        selected_path = None
        for path in self.calculating:
            if self.evaluate_path(path) < min_costs:
                selected_path = path
        mult = True
        # get smallest value to substract
        minimum = min(
            [i.value for i in [x for x in selected_path[1::2]] if i.value > 0]
        )
        print("minimum is", minimum)
        for item in selected_path[:-1]:
            item.value = max(item.value, 0)
            item.value += minimum * (1 if mult else -1)
            if item.value == 0:
                item.value = -1
            mult = not mult
        # degen
        all = [item for sub_list in self.content for item in sub_list]
        values = len([i for i in all if i.value >= 0])
        degeneration = self.num_columns + self.num_rows - 1 - values
        print("degen:", degeneration)
        for i in range(degeneration):
            for x in path:
                if x.value == -1:
                    x.value = 0
                    break
        self.calculating = []
        print(self.calculate_costs())

    # self.editing = [ # list of paths
    #     [c1, c2, c3],
    #     [c1, c3, c4],
    #     [c1, c4, c2],
    # ]
    def _prevent_duplicate(self, item):
        seen = set()
        for i in item:
            if i in seen:
                return False
            elif i != self.start:
                seen.add(i)
        return True

    def _calculate_step(self):
        print(self.calculating)
        # for each path:
        new_calculating = []
        for path in self.calculating:
            if path[0].value != -1:
                return
            # calculate possibilities
            if path[-1] == self.start and len(path) > 1:  # if loop completed
                new_calculating += [path]
                continue

            possibilities = self._calculate_posibilities(path[-1])

            # append each possibility to the path
            new_paths = [path + [item] for item in possibilities]
            new_paths = [
                item
                for item in new_paths
                if item[-1] != item[-2] and self._prevent_duplicate(item)
            ]  # prevent adding same element at the end
            # save new paths to new_array
            new_calculating += new_paths
        # update calculating
        self.calculating = new_calculating
        self.horizontal = not self.horizontal

    def _calculate_posibilities(self, cell):
        if self.horizontal:
            all_on_axis = self.content[cell.y]
        else:
            all_on_axis = [self.content[y][cell.x] for y in range(len(self.content))]

        # filter -> same row/column | has a positive value | can be start except first iteration
        print(
            "new possibilities ",
            [item.str() for item in all_on_axis if item == cell or item.value > 0],
        )
        return [item for item in all_on_axis if item == self.start or item.value > 0]

    def draw_table(self, screen, y_offset, editing):
        if not editing:
            self.editing = (-1, -1)
        values = self.content

        font = pygame.font.Font(None, constants.FONT_SIZE)

        # Calculate the width of the table
        table_width = constants.CELL_WIDTH * (self.num_columns + 2)

        # Calculate the starting x-coordinate for centering
        start_x = (constants.SCREEN_WIDTH - table_width) // 2

        label_text = f"Cost: {self.cost}"
        text_surface = font.render(label_text, True, constants.BLACK)
        text_rect = text_surface.get_rect(
            center=(
                start_x + constants.CELL_WIDTH // 2,
                y_offset + constants.CELL_HEIGHT * 1.5,
            )
        )
        screen.blit(text_surface, text_rect)

        # Draw row labels
        for i in range(self.num_rows):
            label_text = f"a{i+1}"
            text_surface = font.render(label_text, True, constants.BLACK)
            text_rect = text_surface.get_rect(
                center=(
                    start_x + constants.CELL_WIDTH // 2,
                    (i + 2) * constants.CELL_HEIGHT
                    + y_offset
                    + constants.CELL_HEIGHT // 2,
                )
            )
            screen.blit(text_surface, text_rect)

        # Draw column labels
        for j in range(self.num_columns):
            label_text = f"b{j+1}"
            text_surface = font.render(label_text, True, constants.BLACK)
            text_rect = text_surface.get_rect(
                center=(
                    start_x
                    + (j + 1) * constants.CELL_WIDTH
                    + constants.CELL_WIDTH // 2,
                    constants.CELL_HEIGHT + y_offset + constants.CELL_HEIGHT // 2,
                )
            )
            screen.blit(text_surface, text_rect)

        # Draw remaining cells
        for i in range(self.num_rows):
            for j in range(self.num_columns):
                cell_rect = pygame.Rect(
                    start_x + (j + 1) * constants.CELL_WIDTH,
                    (i + 2) * constants.CELL_HEIGHT + y_offset,
                    constants.CELL_WIDTH,
                    constants.CELL_HEIGHT,
                )
                # if editing green, if calculating red
                values[i][j].rect = cell_rect
                pygame.draw.rect(screen, constants.BLACK, cell_rect, 1)
                text_value = str(values[i][j].value) if values[i][j].value >= 0 else "-"
                text = font.render(text_value, True, constants.BLACK)
                text_rect = text.get_rect(center=cell_rect.center)
                screen.blit(text, text_rect)

        # Draw row sums
        for i, cells in enumerate(self.content):
            label_text = f"{sum(max(x.value, 0) for x in cells)}"
            text_surface = font.render(label_text, True, constants.BLACK)
            text_rect = text_surface.get_rect(
                center=(
                    start_x
                    + (self.num_columns + 1) * constants.CELL_WIDTH
                    + constants.CELL_WIDTH // 2,
                    (i + 2) * constants.CELL_HEIGHT
                    + y_offset
                    + constants.CELL_HEIGHT // 2,
                )
            )
            screen.blit(text_surface, text_rect)

        # Draw column sums
        for j in range(self.num_columns):
            all_on_axis = [self.content[y][j] for y in range(len(self.content))]
            label_text = f"{sum(max(x.value, 0) for x in all_on_axis)}"
            text_surface = font.render(label_text, True, constants.BLACK)
            text_rect = text_surface.get_rect(
                center=(
                    start_x
                    + (j + 1) * constants.CELL_WIDTH
                    + constants.CELL_WIDTH // 2,
                    constants.CELL_HEIGHT
                    + y_offset
                    + (self.num_columns+1) * constants.CELL_HEIGHT
                    + constants.CELL_HEIGHT // 2,
                )
            )
            screen.blit(text_surface, text_rect)

        # Draw total
        total = sum([max(x.value, 0) for row in self.content for x in row])
        label_text = f"{total}"
        text_surface = font.render(label_text, True, constants.BLACK)
        text_rect = text_surface.get_rect(
            center=(
                start_x
                + (self.num_columns + 1) * constants.CELL_WIDTH
                + constants.CELL_WIDTH // 2,
                (self.num_rows + 2) * constants.CELL_HEIGHT
                + y_offset
                + constants.CELL_HEIGHT // 2,
            )
        )
        screen.blit(text_surface, text_rect)

        if self.calculating:
            for path in self.calculating:
                for index, item in enumerate(path):
                    cell_rect = pygame.Rect(
                        start_x
                        + (item.x + 1) * constants.CELL_WIDTH
                        + constants.CELL_GAP,
                        (item.y + 2) * constants.CELL_HEIGHT
                        + y_offset
                        + constants.CELL_GAP,
                        constants.CELL_WIDTH - constants.CELL_GAP * 2,
                        constants.CELL_HEIGHT - constants.CELL_GAP * 2,
                    )
                    pygame.draw.rect(
                        screen,
                        constants.RED if index == len(path) - 1 else constants.GREEN,
                        cell_rect,
                        3,
                    )
                    screen.blit(text, text_rect)

        if self.editing != (-1, -1):
            cell_rect = pygame.Rect(
                start_x
                + (self.editing[1] + 1) * constants.CELL_WIDTH
                + constants.CELL_GAP,
                (self.editing[0] + 2) * constants.CELL_HEIGHT
                + y_offset
                + constants.CELL_GAP,
                constants.CELL_WIDTH - constants.CELL_GAP * 2,
                constants.CELL_HEIGHT - constants.CELL_GAP * 2,
            )
            pygame.draw.rect(screen, constants.WHITE, cell_rect, 3)
            screen.blit(text, text_rect)

            return True

        return False

    def set_calculating(self, y, x):
        self.calculating = [[self.content[y][x]]]
        self.start = self.content[y][x]

    def handle_click(self, pos, left=True):
        for i, row in enumerate(self.content):
            for j, item in enumerate(row):
                if item.rect.collidepoint(pos):
                    print(f"clicked {i}, {j}, {item.value}")
                    if left:
                        self.editing = (i, j)
                    else:
                        self.set_calculating(i, j)
                        self.calculate_paths(sleep=0.2)
                        for path in self.calculating:
                            Tk().wm_withdraw()
                            messagebox.showinfo(
                                "Finished",
                                f"Cheapest costs for this path: {self.evaluate_path(path)}",
                            )
                    return True

    def handle_input(self, event):
        if self.editing == (-1, -1):
            return
        editing = self.content[self.editing[0]][self.editing[1]]
        editing.value = editing.value if editing.value != -1 else 0
        if event.key == pygame.K_BACKSPACE:
            try:
                editing.value = int(str(editing.value)[0:-1])
            except:
                editing.value = -1
        else:
            try:
                editing.value = int(str(editing.value) + event.unicode)
            except:
                return

    def deselect(self):
        self.editing = (-1, -1)
        self.calculating = []


class Cell:
    rect = None
    factor = 0

    def __init__(self, value, x, y):
        if value < -1:
            raise Exception("Nichtnegativitäts prinzip")
        self.value = int(value)
        self.x = x
        self.y = y

    def __str__(self):
        return f"Cell({self.value})"

    def str(self):
        return f"Cell({self.value})"
