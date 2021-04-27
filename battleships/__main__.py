from game import Game
from player import Player
from field import Field
import curses
import os
import pickle
import sys

SAVES_PATH = 'saves'
SAVE_NAME = "last_save.pkl"


def main(screen: curses.window, mheight: int, mwidth: int):
    # removing cursor
    curses.curs_set(0)
    # setting color for menu
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # things to be printed
    prev_game = load_game()

    str_start_game = "Start New Game"
    str_load_game = "Load Game"
    str_exit = "Exit"
    menu_items = [str_load_game, str_start_game, str_exit] if prev_game else [str_start_game, str_exit]

    cur_index = 0  # selected menu item
    display_menu(screen, menu_items, cur_index)

    while True:
        # listen to input
        key = screen.getch()

        # handling navigation
        if key == curses.KEY_UP and cur_index > 0:
            cur_index -= 1
        elif key == curses.KEY_DOWN and cur_index < len(menu_items) - 1:
            cur_index += 1
        # handling Enter button
        elif key == curses.KEY_ENTER or key in [10, 13]:
            cur_item = menu_items[cur_index]

            if cur_item == str_start_game:
                # adjust length of the symbols
                Field.recal_sybms(len(str(mwidth)))
                # start new game
                start_game(screen, mheight, mwidth)
            elif cur_item == str_load_game:
                # adjust length of the symbols
                Field.recal_sybms(len(str(prev_game.map_width)))
                # continue last saved game
                play_game(screen, game=prev_game)
            elif cur_item == str_exit:
                return

        screen.clear()
        display_menu(screen, menu_items, cur_index)


def start_game(screen: curses.window, mheight: int, mwidth: int) -> None:
    """
    function for starting a new game
    mheight: map height
    mwidth: map width
    """
    # reading player's name
    screen.clear()
    print_to_center(screen, ['Enter your name: '])
    screen.refresh()
    curses.curs_set(1)
    curses.echo()
    name = screen.getstr().decode("utf-8")
    curses.curs_set(0)
    curses.noecho()

    screen.clear()
    print_to_center(screen, ['Preparing the game...'])
    screen.refresh()

    # initializing a new game
    game = Game(mheight, mwidth)
    # making necessary preparations
    game.prepare_game(player_name=name)
    # playing the game
    play_game(screen=screen, game=game)


def print_to_center(screen: curses.window, messages) -> None:
    """
    function for printing messages to the center of the screen
    :param screen:
    :param messages: list-like iterable element
    """

    sheight, swidth = screen.getmaxyx()

    for index, message in enumerate(messages):
        screen.addstr(sheight // 2 + index, swidth // 2 - len(message) // 2, message)


def display_game(screen: curses.window, cur_player: Player, game: Game):
    """
    function for printing game on the console
    """
    # obtain coordinates for displaying fields
    sheight, swidth = screen.getmaxyx()
    my_coords, enemy_coords = game.display_field(sheight=sheight, swidth=swidth)

    # print fields and stats on the console
    screen.clear()
    display_field(screen, my_coords, cur_player, True, game=game)
    display_field(screen, enemy_coords, cur_player, False, game=game)
    stats = game.num_alive_ships()
    display_stats(screen=screen, statistics=stats[0], my=True, game=game)
    display_stats(screen=screen, statistics=stats[1], my=False, game=game)


def process_shooting(screen: curses.window, cur_player: Player, game: Game, is_human: bool):
    """
    function for processing current player's shot
    """
    # shoot
    succ, hit = game.player_shoot()
    # if player chose an inappropriate cell, do nothing
    if not succ:
        game.turn -= 1
    else:
        screen.clear()

        message = "You missed" if is_human else "AI missed"
        if hit:
            message = "You hit enemy ship" if is_human else "AI hit enemy ship"
            game.check_victory()
            game.turn -= 1

        # printing the result of the shot to the screen
        if is_human:
            print_to_center(screen, [message])
        else:
            y_shot = cur_player.enemy_field.y_cur
            x_shot = cur_player.enemy_field.x_cur
            print_to_center(screen, [f"AI has shot to {y_shot} {x_shot}", message])

        screen.refresh()
        screen.getch()

    screen.refresh()


def process_human_move(screen: curses.window, cur_player: Player, game: Game):
    """
    function for listening to player's input and taking appropriate actions
    """
    buttons_move_cursor = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT,
                           ord('w'), ord('s'), ord('a'), ord('d')]

    buttons_shoot = [curses.KEY_ENTER, 10, 12, 13, 14]

    while True:
        # get fields
        my_field = cur_player.my_field
        enemy_field = cur_player.enemy_field

        display_game(screen, cur_player, game)

        # listen to the input
        key = screen.getch()
        # move corresponding cursors
        if key in buttons_move_cursor:
            move_cursor(key, my_field=my_field, enemy_field=enemy_field, game=game)
        # shoot at the current location of the cursor
        elif key in buttons_shoot:
            process_shooting(screen, cur_player, game, is_human=True)
            break
        # save the game
        elif key == ord('o'):
            screen.clear()
            save_game(game)
            print_to_center(screen, ['The game was saved'])
            screen.getch()
            game.turn -= 1
            break


def process_ai_move(screen: curses.window, cur_player: Player, game: Game):
    """
    function for simulating ai move
    """
    # get coordinates for shooting
    y_shot, x_shot = cur_player.get_rand_shoot()
    cur_player.enemy_field.y_cur = y_shot
    cur_player.enemy_field.x_cur = x_shot

    # shoot
    process_shooting(screen, cur_player, game, is_human=False)


def declare_winner(screen: curses.window, game: Game):
    """
    function for printing the winner to the screen
    """
    screen.clear()
    message = f'Congrats! Player {game.winner} has won!'
    print_to_center(screen, [message])
    screen.refresh()
    screen.getch()


def play_game(screen: curses.window, game: Game) -> None:
    """
    function for simulating the game
    """

    while not game.is_finished:
        # obtaining the current player
        cur_player = game.players[game.turn % 2]
        # if human
        if cur_player.is_human:
            process_human_move(screen, cur_player, game)
            screen.refresh()

        # if current player is AI
        else:
            process_ai_move(screen, cur_player, game)
            screen.refresh()

        game.turn += 1

    declare_winner(screen, game)


def save_game(game):
    """
    function for saving the game

    save is located in ./save folder
    """

    if not os.path.exists(SAVES_PATH):
        os.makedirs(SAVES_PATH)

    with open(os.path.join(SAVES_PATH, SAVE_NAME), 'wb') as save:
        pickle.dump(game, save, pickle.HIGHEST_PROTOCOL)


def load_game():
    """
    returns a saved game if any
    """

    # check if the file exists
    if not os.path.exists(os.path.join(SAVES_PATH, SAVE_NAME)):
        return None

    # load save
    with open(os.path.join(SAVES_PATH, SAVE_NAME), 'rb') as load:
        game = pickle.load(load)
        return game


def move_cursor(key, my_field, enemy_field, game):
    """
    function for moving cursors on both fields
    """
    if key == curses.KEY_UP and enemy_field.y_cur - 1 >= 0:
        enemy_field.y_cur -= 1
    elif key == curses.KEY_DOWN and enemy_field.y_cur + 1 < game.map_height:
        enemy_field.y_cur += 1
    elif key == curses.KEY_LEFT and enemy_field.x_cur - 1 >= 0:
        enemy_field.x_cur -= 1
    elif key == curses.KEY_RIGHT and enemy_field.x_cur + 1 < game.map_width:
        enemy_field.x_cur += 1
    elif key == ord('w') and my_field.y_cur - 1 >= 0:
        my_field.y_cur -= 1
    elif key == ord('s') and my_field.y_cur + 1 < game.map_height:
        my_field.y_cur += 1
    elif key == ord('a') and my_field.x_cur - 1 >= 0:
        my_field.x_cur -= 1
    elif key == ord('d') and my_field.x_cur + 1 < game.map_width:
        my_field.x_cur += 1


def display_stats(screen: curses.window, statistics, my: bool, game: Game):
    """
    function for printing a table displaying how many ships are alive/dead
    """
    # if the size of the longest ship is greater than 50
    # then tables with stats won't fit on the screen
    # thus, just don't print it
    if game.longest_ship_sz > 50:
        return

    sheight, swidth = screen.getmaxyx()

    title = "Your Ships" if my else "Enemy Ships"
    str_size = "Size"
    str_alive = "Alive"
    str_dead = "Dead"
    col_names = f"| {str_size} | {str_alive} | {str_dead} |"
    offset_x = 0

    # Each table is 8 blocks away from fields
    if my:
        offset_x = swidth // 2 - Field.WINDOW_WIDTH * len(Field.EMPTY) // 2 \
                   - len(str(game.map_width)) - len(col_names) - 8
    else:
        offset_x = swidth // 2 - Field.WINDOW_WIDTH * len(Field.EMPTY) // 2 \
                   + (len(Field.EMPTY) + 1) * Field.WINDOW_WIDTH + 8

    # Each table close to the middle of the fields but at least 1 block away from the top of the console
    offset_y = max(1, (Field.WINDOW_HEIGHT * 2 + 10) // 2 - (len(statistics) + 3) // 2)
    longest_ship_sz = game.longest_ship_sz

    # printing table's heading
    screen.addstr(offset_y, offset_x + (len(col_names) // 2 - len(title) // 2), title)
    screen.addstr(offset_y + 1, offset_x, "-" * (len(col_names)))
    screen.addstr(offset_y + 2, offset_x, col_names)

    # printing stats
    row = 3
    for i in range(len(statistics)):
        alive = str(statistics[i])
        dead = str(longest_ship_sz - (i + 1) + 1 - statistics[i])
        # cross out if there are no alive ships
        if alive == '0':
            screen.addstr(offset_y + row, offset_x, "|" + "/" * (len(col_names) - 2) + "|")
        else:
            screen.addstr(offset_y + row, offset_x, "| " + str(i + 1) + " " * (len(str_size) + 1 - len(str(i + 1))) +
                          '| ' + alive + " " * (len(str_alive) + 1 - len(alive)) +
                          '| ' + dead + " " * (len(str_dead) + 1 - len(dead)) + "|"
                          )
        row += 1

    screen.addstr(offset_y + row, offset_x, "-" * (len(col_names)))


def display_field(screen: curses.window, coords, player: Player, my: bool, game: Game) -> None:
    """
    function for printing fields on the console
    """
    # obtaining field
    field = player.my_field if my else player.enemy_field
    # obtaining sliding window borders
    start_left = field.border_left
    start_top = field.border_top
    iter_row = start_top
    iter_col = start_left
    for y, x, symb in coords:
        # replacing current active element with the cursor
        if iter_row == field.y_cur and iter_col == field.x_cur:
            screen.addstr(y, x, Field.CURSOR)
        else:
            screen.addstr(y, x, symb)
        # printing numbers on the top of the sliding window
        if iter_row == start_top:
            num_zeros = len(str(game.map_width)) - len(str(iter_col))
            power_of_ten = 10 ** len(str(game.map_width))
            screen.addstr(y - 1, x,
                          "0" * num_zeros + str(iter_col) + " " if iter_col < power_of_ten else str(iter_col) + ' ')
        # printing numbers on the left of the sliding window
        if iter_col == start_left:
            screen.addstr(y, x - len(str(iter_row)), str(iter_row))

        iter_col += 1
        if iter_col == start_left + Field.WINDOW_WIDTH:
            iter_col = start_left
            iter_row += 1

    screen.refresh()


def display_menu(screen: curses.window, menu_items, cur_index: int):
    """
    prints the menu to the console
    """

    # obtaining size of the screen
    sheight, swidth = screen.getmaxyx()

    welcome = "Welcome to Battleships"

    screen.addstr(1, swidth // 2 - len(welcome) // 2, '#' * len(welcome))
    screen.addstr(2, swidth // 2 - len(welcome) // 2, welcome)
    screen.addstr(3, swidth // 2 - len(welcome) // 2, '#' * len(welcome))

    # printing the menu in center of the screen
    for index, item in enumerate(menu_items):
        x = swidth // 2 - len(item) // 2
        y = sheight // 2 - len(menu_items) // 2 + index
        if index == cur_index:
            screen.attron(curses.color_pair(1))
            screen.addstr(y, x, item)
            screen.attroff(curses.color_pair(1))
        else:
            screen.addstr(y, x, item)

    screen.refresh()


class UserException(Exception):
    def __init__(self, msg):
        self.msg = msg


def read_args():
    """
    function for reading arguments

    returns
    """

    try:
        if len(sys.argv) != 3:
            raise UserException("Incorrect arguments")

        n = int(sys.argv[1])
        k = int(sys.argv[2])

        if n < 5 or k < 5:
            raise UserException("Incorrect arguments")

        return True, n, k
    except UserException as e:
        print(e.msg)
        print("Please, run 'python3 battleships N K'")
        print("where N >= 5 is height of the field and K >= 5 is its width")
        return False, 0, 0


if __name__ == '__main__':
    succ, map_height, map_width = read_args()
    if succ:
        try:
            curses.wrapper(main, map_height, map_width)
        except curses.error:
            print("Console size is too small")
            print("Please, make it full screen")
