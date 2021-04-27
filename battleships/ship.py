class Ship:

    def __init__(self, size):
        self.size = size
        self.health = size
        self.x = self.y = self.is_vertical = None

    def set_coordinates(self, y: int, x: int, is_vertical: bool):
        self.y = y
        self.x = x
        self.is_vertical = is_vertical

    def __repr__(self):
        return str(self.y) + " " + str(self.x) + " " + str(self.health) + " " + str(self.size)
