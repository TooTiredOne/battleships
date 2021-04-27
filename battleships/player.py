from field import Field
import random


class Player:
    def __init__(self, name: str, is_human: bool):
        self.name = name
        self.is_human = is_human
        self.my_field = None  # to observe friendly ships
        self.enemy_field = None  # to shoot enemy ships
        self.ships = None

    def __repr__(self):
        return str(self.name)

    def _get_rand_row(self):
        """
        returns index of a random row from enemy's field
        """
        return random.randint(0, self.enemy_field.height - 1)

    def get_rand_shoot(self):
        """
        returns correct random indexes of cells to shoot at
        """
        cols = []
        row = -1

        # while there will be at least 1 shootable cell in the row
        while len(cols) == 0:
            # get random row
            row = self._get_rand_row()
            for index, cell in enumerate(self.enemy_field.cells[row]):
                if cell.shootable():
                    cols.append(index)

        return row, random.choice(cols)

    def _rand_ship_coordinates(self):
        """
        returns random coordinates for a ship
        """

        y, x = random.randint(0, self.my_field.height - 1), random.randint(0, self.my_field.width - 1)
        is_vertical = random.choice((True, False))

        return y, x, is_vertical

    def _can_place_ship(self, y, x):
        """
        checks if one can place a part of the ship on this cell
        """

        if self.my_field.cells[y][x].ship:
            return False

        if y - 1 >= 0:
            if self.my_field.cells[y - 1][x].ship:
                return False

            if x + 1 < self.my_field.width and self.my_field.cells[y - 1][x + 1].ship:
                return False

            if x - 1 >= 0 and self.my_field.cells[y - 1][x - 1].ship:
                return False

        if y + 1 < self.my_field.height:
            if self.my_field.cells[y + 1][x].ship:
                return False

            if x + 1 < self.my_field.width and self.my_field.cells[y + 1][x + 1].ship:
                return False

            if x - 1 >= 0 and self.my_field.cells[y + 1][x - 1].ship:
                return False

        if x + 1 < self.my_field.width and self.my_field.cells[y][x + 1].ship:
            return False

        if x - 1 >= 0 and self.my_field.cells[y][x - 1].ship:
            return False

        return True

    def display_field(self, sheight, swidth):
        """
        method for acquiring location of fields on the screen
        """
        return self.my_field.display_field(sheight=sheight, swidth=swidth, on_top=True), \
               self.enemy_field.display_field(sheight=sheight, swidth=swidth, on_top=False)

    def set_and_fill_field(self, field: Field):
        """
        method for setting player's field and randomly filling it with ships
        """
        self.my_field = field

        is_filled = False  # has all ships been successfully set
        while not is_filled:
            is_filled = True

            for ship in self.ships:
                reset_after = 50
                """
                we try to fit a single ship 50 times
                if we fail then we clear the field and start placing ships from the very beginning
                """
                while reset_after > 0:
                    y, x, is_vertical = self._rand_ship_coordinates()  # coordinates of ship's head and its orientation
                    is_placed = True  # checks if the ship was placed on the field

                    # if ship's orientation is vertical
                    if is_vertical:
                        # break if there's not enough space
                        if y + ship.size - 1 >= field.height:
                            reset_after -= 1
                            continue

                        # check if all cells are available
                        for i in range(ship.size):
                            # break if not
                            if not self._can_place_ship(y + i, x):
                                is_placed = False
                                break
                        # fill the field if the ship was placed
                        if is_placed:
                            # set ship's head coordinates
                            ship.y = y
                            ship.x = x
                            ship.is_vertical = is_vertical
                            for i in range(ship.size):
                                self.my_field.cells[y + i][x].set_ship(ship)
                            break
                        else:
                            reset_after -= 1
                            continue

                    # if ship is placed horizontally
                    else:
                        # the process is similar to vertical placement
                        if x + ship.size - 1 >= field.width:
                            reset_after -= 1
                            continue

                        for i in range(ship.size):
                            if not self._can_place_ship(y, x + i):
                                is_placed = False
                                break
                        if is_placed:
                            ship.y = y
                            ship.x = x
                            ship.is_vertical = is_vertical
                            for i in range(ship.size):
                                self.my_field.cells[y][x + i].set_ship(ship)
                            break
                        else:
                            reset_after -= 1
                            continue

                if reset_after <= 0:
                    is_filled = False
                    break

            # clear the field
            if not is_filled:
                self.my_field.clear_cells()

    def set_ships(self, ships):
        """
        ship's setter
        """
        self.ships = ships
