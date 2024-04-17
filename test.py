from classes import *


quantity_table = Table(constants.quantity_values)
quantity_table.set_calculating(1, 0)
quantity_table.calculate_paths()

print(quantity_table.calculating)
