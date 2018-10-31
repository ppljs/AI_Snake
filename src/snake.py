import numpy as np
from enum import Enum
from random import randint
import threading
import os
from subprocess import call
from pynput.keyboard import Key, Listener
import utils


BOARD_WIDTH = 15
BOARD_HEIGHT = 15


class Content(Enum):
    void = 0
    wall = 1
    apple = 2
    snake = 3
    snake_head = 4


class Direction(Enum):
    up = 0
    down = 1
    left = 2
    right = 3


class Scores(Enum):
    MOV_CLOSER = 1
    MOV_FARTHER = -2
    ATE_APPLE = 10


class Game:
    def __init__(self, max_moves=None):
        self.board = Board()
        # self.printer = Printer(self.board.block_board)
        self.keyboard_handler = KeyboardHandler()
        self.score = 0
        self.max_moves = max_moves

    def calc_score(self, snake_pos_before, snake_size_before):
        if self.board.snake_head.size > snake_size_before:
            self.score += Scores.ATE_APPLE.value
            self.score += Scores.MOV_CLOSER.value
            self.max_moves += 20
        elif utils.distance(self.board.apple_pos, snake_pos_before) > \
                utils.distance(self.board.apple_pos, self.board.snake_head.get_pos()):
            self.score += Scores.MOV_CLOSER.value
        else:
            self.score += Scores.MOV_FARTHER.value

    def run(self, automated_dir=None, use_keyboard=True):
        if self.max_moves is not None:
            if self.max_moves > 0:
                self.max_moves -= 1
            else:
                return False

        if use_keyboard:
            new_dir = self.keyboard_handler.get_dir()
        else:
            new_dir = self.board.snake_head.snakedir_to_worldref(automated_dir)

        snake_pos_before = self.board.snake_head.get_pos()
        snake_size_before = self.board.snake_head.size

        to_return = self.board.update(new_dir)

        self.calc_score(snake_pos_before, snake_size_before)

        # self.printer.update_print()
        return to_return


class KeyboardHandler:
    def __init__(self):
        self.keyboard_listener = Listener(on_press=self.on_press)
        self.key_to_direction = {Key.up: Direction.up,
                                 Key.down: Direction.down,
                                 Key.left: Direction.left,
                                 Key.right: Direction.right}

        self.dir_list = []
        self.lock = threading.Lock()

        self.keyboard_listener.start()

    def on_press(self, key):
        if key in self.key_to_direction:
            with self.lock:
                self.dir_list.append(self.key_to_direction[key])

    def get_dir(self):
        with self.lock:
            try:
                tmp_dir = self.dir_list.pop(0)
            except Exception as e:
                tmp_dir = None
            return tmp_dir


class Printer:
    def __init__(self, block_board):
        self.block_board = block_board
        self.content_to_char = {Content.void: '-',
                                Content.apple: '&',
                                Content.snake: 'o',
                                Content.snake_head: 'o',
                                Content.wall: 'X'}
        self.matrix_draw = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)

    def update_print(self):
        self.clear_screen()
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                self.matrix_draw[i][j] = self.block_board[i][j].content.value

        #print(self.matrix_draw)

    def clear_screen(self):
        call('clear' if os.name == 'posix' else 'cls')


class Block:
    def __init__(self, content):
        self.content = content
        self.cycles_to_clear = 0
        self.change = False

    def __str__(self):
        return str(self.content)

    def set_snake_head(self, snake_size):
        self.content = Content.snake_head
        self.cycles_to_clear = snake_size
        self.change = True

    def update(self):
        if self.cycles_to_clear > 0:
            if self.cycles_to_clear == 1:
                self.cycles_to_clear = 0
                self.content = Content.void
            else:
                self.cycles_to_clear -= 1
                if self.change:
                    self.content = Content.snake
                    self.change = False


class Board:
    def __init__(self):
        self.block_board = None
        self._build_board()

        self.snake_head = SnakeHead()
        snake_block = self.block_board[self.snake_head.i_pos][self.snake_head.j_pos]
        snake_block.set_snake_head(self.snake_head.size)

        self.apple_pos = (-1, -1)
        self.place_apple()

    def _build_board(self):
        self.block_board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=Block)
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                if i == 0 or i == BOARD_HEIGHT - 1 or j == 0 or j == BOARD_WIDTH - 1:
                    content = Content.wall
                else:
                    content = Content.void
                self.block_board[i][j] = Block(content=content)

    def get_features(self, normalize=True):
        s_i, s_j = self.snake_head.get_pos()
        block_dict = {Direction.up: self.block_board[s_i - 1][s_j],
                      Direction.right: self.block_board[s_i][s_j + 1],
                      Direction.down: self.block_board[s_i + 1][s_j],
                      Direction.left: self.block_board[s_i][s_j - 1]}
        l_f_r_blocks = [block_dict[self.snake_head.snakedir_to_worldref(Direction.left)],
                        block_dict[self.snake_head.direction],
                        block_dict[self.snake_head.snakedir_to_worldref(Direction.right)]]
        l_f_r_obst = [1 if b.content != Content.void else 0 for b in l_f_r_blocks]

        alpha = utils.angle_between(np.subtract(self.apple_pos, (s_i, s_j)),
                                    self.snake_head.direction_vector[self.snake_head.direction])
        print('s_i, s_j =', s_i, s_j)
        print('apple pos =', self.apple_pos)
        print('translation =', np.subtract(self.apple_pos, (s_i, s_j)))
        print('snake_dir =', self.snake_head.direction_vector[self.snake_head.direction])

        if normalize:
            factor = 360.0
        else:
            factor = 1
        l_f_r_obst.append(alpha / factor)
        return l_f_r_obst

    def place_apple(self):
        while True:
            apple_j_pos = randint(1, BOARD_WIDTH - 2)
            apple_i_pos = randint(1, BOARD_HEIGHT - 2)
            curr_block = self.block_board[apple_i_pos][apple_j_pos]
            if curr_block.content == Content.void:
                curr_block.content = Content.apple
                self.apple_pos = (apple_i_pos, apple_j_pos)
                break

    def get_snake_pos_ji_list(self):
        temp_list = []
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                if self.block_board[i][j].content == Content.snake or \
                        self.block_board[i][j].content == Content.snake_head:
                    temp_list.append((j, i))
        return temp_list

    def get_flattenned_board(self):
        temp_flat = self.block_board.flatten()
        int_flat = []
        for i in range(BOARD_HEIGHT * BOARD_WIDTH):
            int_flat.append(temp_flat[i].content.value)

        return int_flat

    def update(self, snake_next_direction):
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                self.block_board[i][j].update()

        self.snake_head.update_direction(snake_next_direction)
        self.snake_head.move()
        s_pos = self.snake_head.get_pos()

        curr_snake_block = self.block_board[s_pos[0]][s_pos[1]]

        if curr_snake_block.content == Content.apple:
            self.snake_head.increase_size()
            curr_snake_block.set_snake_head(self.snake_head.size)
            self.place_apple()
        elif curr_snake_block.content == Content.wall:
            return False
        elif curr_snake_block.content == Content.snake or curr_snake_block.content == Content.snake_head:
            return False
        else:
            curr_snake_block.set_snake_head(self.snake_head.size)

        return True


class SnakeHead:
    def __init__(self):
        self.i_pos = BOARD_HEIGHT // 2
        self.j_pos = BOARD_WIDTH // 2
        self.direction = Direction.right
        self.size = 2
        self._move_actions = {Direction.left: self._move_left,
                              Direction.right: self._move_right,
                              Direction.up: self._move_up,
                              Direction.down: self._move_down}
        self._impossible_state_changes = {Direction.left: Direction.right,
                                          Direction.right: Direction.left,
                                          Direction.up: Direction.down,
                                          Direction.down: Direction.up}
        self._to_snakeref = {Direction.left: {Direction.left: Direction.down,
                                              Direction.right: Direction.up},
                             Direction.right: {Direction.left: Direction.up,
                                               Direction.right: Direction.down},
                             Direction.up: {Direction.left: Direction.left,
                                            Direction.right: Direction.right},
                             Direction.down: {Direction.left: Direction.right,
                                              Direction.right: Direction.left}}
        self.direction_vector = {Direction.up: [-1, 0],
                                 Direction.down: [1, 0],
                                 Direction.left: [0, -1],
                                 Direction.right: [0, 1]}

    def snakedir_to_worldref(self, dir):
        if dir is None:
            return None
        else:
            return self._to_snakeref[self.direction][dir]

    def update_direction(self, new_direction):
        if new_direction is not None and self._impossible_state_changes[self.direction] != new_direction:
            self.direction = new_direction

    def increase_size(self):
        self.size += 1

    def get_pos(self):
        return (self.i_pos, self.j_pos)

    def move(self):
        self._move_actions[self.direction]()

    def _move_left(self):
        self.j_pos -= 1

    def _move_right(self):
        self.j_pos += 1

    def _move_up(self):
        self.i_pos -= 1

    def _move_down(self):
        self.i_pos += 1
