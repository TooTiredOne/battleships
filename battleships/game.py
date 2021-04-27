from player import Player
from ship import Ship
from field import Field


class Game:
    # list of players
    def __init__(self, height: int, width: int):
        self.players = []
        self.turn = 0
        self.is_finished = False
        self.winner = None
        self.longest_ship_sz = 0  # the size of the longest ship
        self.map_height = height
        self.map_width = width

    def _init_players(self, player_name: str) -> None:
        """
        method for initialization of players
        """
        human = Player(name=player_name, is_human=True)
        computer = Player(name="AI", is_human=False)

        self.players.append(human)
        self.players.append(computer)

    def _init_ships(self) -> None:
        """
        method for creating right # of ships with right sizes

        we need to find such n that there will be

        1 ship of size n
        2 ships of size n-1
        ...
        n-1 ships of size 2
        n ships of size 1

        Area taken by those ships may be calculated by the following formula
        S = (1 / 6) * n * (n + 1) * (n + 2)

        S should be around 20% of map's area
        """

        # overall area
        field_area = self.map_height * self.map_width
        n = 1  # see method's description
        ships_area = 1
        while ships_area / field_area < 0.2:
            n += 1
            ships_area = (1 / 6) * n * (n + 1) * (n + 2)

        self.longest_ship_sz = n
        fp_ships = []  # 1st player's ships
        sp_ships = []  # 2nd player's ships
        count = 1
        while n > 0:
            # creating "count" number of ships of size "n" for both players
            for i in range(count):
                fp_ships.append(Ship(n))
                sp_ships.append(Ship(n))
            count += 1
            n -= 1

        # setting players' ships
        self.players[0].set_ships(ships=fp_ships)
        self.players[1].set_ships(ships=sp_ships)

    def _init_fields(self) -> None:
        """
        method for placing ships on both players' fields
        """
        # set player.my_field
        self.players[0].set_and_fill_field(field=Field(height=self.map_height, width=self.map_width))
        self.players[1].set_and_fill_field(field=Field(height=self.map_height, width=self.map_width))

        # set player.enemy_field
        self.players[0].enemy_field = Field(height=self.map_height, width=self.map_width)
        self.players[1].enemy_field = Field(height=self.map_height, width=self.map_width)

    def prepare_game(self, player_name: str) -> None:
        """
        method for preparing everything needed to play the game
        """
        self._init_players(player_name=player_name)
        self._init_ships()
        self._init_fields()

    def _ship_mark_destroyed(self, player, ship, my_field: bool):
        """
        methods marks surrounding of the destroyed ship as "was shot"
        """

        field = player.my_field if my_field else player.enemy_field

        if ship.is_vertical:
            if ship.y - 1 >= 0:
                field.cells[ship.y - 1][ship.x].get_shot(has_ship=False)
            for i in range(-1, ship.size + 1):
                if 0 <= ship.y + i < field.height:
                    if ship.x - 1 >= 0:
                        field.cells[ship.y + i][ship.x - 1].get_shot(has_ship=False)
                    if ship.x + 1 < field.width:
                        field.cells[ship.y + i][ship.x + 1].get_shot(has_ship=False)
            if ship.y + ship.size < field.height:
                field.cells[ship.y + ship.size][ship.x].get_shot(has_ship=False)
        else:
            if ship.x - 1 >= 0:
                field.cells[ship.y][ship.x - 1].get_shot(has_ship=False)
            for i in range(-1, ship.size + 1):
                if 0 <= ship.x + i < field.width:
                    if ship.y - 1 >= 0:
                        field.cells[ship.y - 1][ship.x + i].get_shot(has_ship=False)
                    if ship.y + 1 < field.height:
                        field.cells[ship.y + 1][ship.x + i].get_shot(has_ship=False)
            if ship.x + ship.size < field.width:
                field.cells[ship.y][ship.x + ship.size].get_shot(has_ship=False)

    def check_victory(self):
        """
        method for checking if the current player has won
        """
        # obtaining players
        cur_player = self.players[self.turn % 2]  # shoots
        other_player = self.players[(self.turn + 1) % 2]  # gets shot

        has_won = True
        for ship in other_player.ships:
            if ship.health > 0:
                has_won = False
                break

        if has_won:
            self.is_finished = True
            self.winner = cur_player

    def _player_get_shot(self, player, y_shot, x_shot):
        """
        method for player who is getting shot
        """
        # shot cell
        cell = player.my_field.cells[y_shot][x_shot]
        ship = cell.ship

        # if ship was hit
        if ship:
            ship.health -= 1
            # if it was destroyed
            if ship.health <= 0:
                cell.get_shot(has_ship=True)
                self._ship_mark_destroyed(player=player, ship=ship, my_field=True)
            # if it was damaged
            else:
                cell.get_shot(has_ship=True)
        else:
            cell.get_shot(has_ship=False)

    def player_shoot(self) -> (bool, bool):
        """
        player whose turn is now shooting at the other player

        the method returns 2 boolean values:
         1. if player shot at shootable cell
         2. if player hit enemy shit
        """
        # obtaining players
        cur_player = self.players[self.turn % 2]  # shoots
        other_player = self.players[(self.turn + 1) % 2]  # gets shot
        # obtaining coordinates of the cell that's being shot
        x_shot = cur_player.enemy_field.x_cur
        y_shot = cur_player.enemy_field.y_cur

        # if the cell isn't shootable, then return False
        if not cur_player.enemy_field.cells[y_shot][x_shot].shootable():
            return False, False

        # other player marks where he/she was shot
        self._player_get_shot(player=other_player, y_shot=y_shot, x_shot=x_shot)

        # if hit enemy ship
        if other_player.my_field.cells[y_shot][x_shot].ship:
            # mark as hit
            cur_player.enemy_field.cells[y_shot][x_shot].get_shot(has_ship=True)
            # if ship was destroyed
            if other_player.my_field.cells[y_shot][x_shot].ship.health <= 0:
                # mark as destroyed
                self._ship_mark_destroyed(player=cur_player, my_field=False,
                                          ship=other_player.my_field.cells[y_shot][x_shot].ship)
            return True, True
        else:
            cur_player.enemy_field.cells[y_shot][x_shot].get_shot(has_ship=False)
            return True, False

    def num_alive_ships(self):
        """
        methods for calculating alive ships of both players
        """
        statistics = []
        for player in self.players:
            ships_alive = [0 for _ in range(self.longest_ship_sz)]
            for ship in player.ships:
                if ship.health > 0:
                    ships_alive[ship.size - 1] += 1

            statistics.append(ships_alive)

        return statistics[0], statistics[1]

    def display_field(self, sheight, swidth):
        # displaying human's fields
        return self.players[0].display_field(sheight=sheight, swidth=swidth)
