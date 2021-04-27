
class Cell:
    def __init__(self, exists: bool):
        self.symbol = Field.EMPTY if exists else Field.DOESNT_EXIST
        self.ship = None

    def set_ship(self, ship):
        """
        setting a ship
        """
        self.ship = ship
        self.symbol = Field.SHIP

    def shootable(self) -> bool:
        return self.symbol == Field.EMPTY

    def get_shot(self, has_ship: bool):
        """
        method changes the symbol of the cell
        """
        self.symbol = Field.SHOT_HIT if has_ship else Field.SHOT_MISS


class Field:
    EMPTY = '   '
    DOESNT_EXIST = '/' * len(EMPTY)
    SHIP = '▩' * len(EMPTY)
    CURSOR = '□' * len(EMPTY)
    SHOT_MISS = '⊙'
    SHOT_HIT = '⚔'
    WINDOW_HEIGHT = 10
    WINDOW_WIDTH = 10

    @staticmethod
    def recal_sybms(n: int):
        """
        method for adjusting length of the symbols to match cursors length
        """
        Field.EMPTY = ' ' * n
        Field.DOESNT_EXIST = '/' * n
        Field.SHIP = '▩' * n
        Field.CURSOR = '□' * n
        Field.SHOT_MISS = ' ' * (n // 2) + '⊙'
        Field.SHOT_HIT = ' ' * (n // 2) + '⚔'

    def __init__(self, height, width):
        self.height = height  # map height
        self.width = width  # map width
        self.cells = []
        self._init_cells()
        self.border_left = 0  # the left-most column of the sliding window
        self.border_top = 0  # the top-most column of the sliding window
        self.x_cur = self.y_cur = 0  # current active cell

    def _init_cells(self) -> None:
        """
        setting cells

        field's sliding window size is at least WINDOW_HEIGHT x WINDOW_WIDTH
        """
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(Cell(exists=True))
            for j in range(self.width, Field.WINDOW_WIDTH):
                row.append(Cell(exists=False))

            self.cells.append(row)

        for i in range(self.height, Field.WINDOW_HEIGHT):
            self.cells.append([Cell(exists=False) for _ in range(max(self.width, 10))])

    def clear_cells(self) -> None:
        """
        clearing cells
        """
        self.cells = []
        self._init_cells()

    def _adjust_borders(self):
        """
        method for acquiring numbers on the edges of the sliding window
        """
        if self.x_cur < self.border_left:
            self.border_left = self.x_cur
        elif abs(self.x_cur - self.border_left) + 1 > Field.WINDOW_WIDTH:
            self.border_left = self.x_cur - Field.WINDOW_WIDTH + 1

        if self.y_cur < self.border_top:
            self.border_top = self.y_cur
        if abs(self.y_cur - self.border_top) + 1 > Field.WINDOW_HEIGHT:
            self.border_top = self.y_cur - Field.WINDOW_HEIGHT + 1

    def display_field(self, sheight, swidth, on_top: bool):
        """
        method for displaying sliding window on the screen

        it returns coordinates of the cells to be printed on the console
        """
        self._adjust_borders()

        result = []

        row_count = col_count = 0
        if on_top:
            for i in range(self.border_top, self.border_top + Field.WINDOW_HEIGHT):
                for j in range(self.border_left, self.border_left + Field.WINDOW_WIDTH):
                    x = swidth // 2 - Field.WINDOW_WIDTH * len(Field.EMPTY) // 2 + (len(Field.EMPTY) + 1) * col_count
                    y = 3 + row_count
                    result.append((y, x, f"{self.cells[i][j].symbol}"))
                    col_count += 1

                col_count = 0
                row_count += 1
        else:
            for i in range(self.border_top, self.border_top + Field.WINDOW_HEIGHT):
                for j in range(self.border_left, self.border_left + Field.WINDOW_WIDTH):
                    x = swidth // 2 - Field.WINDOW_WIDTH * len(Field.EMPTY) // 2 + (len(Field.EMPTY) + 1) * col_count
                    y = 17 + row_count
                    result.append((y, x, f"{self.cells[i][j].symbol}"))
                    col_count += 1

                col_count = 0
                row_count += 1

        return result
