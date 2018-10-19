import numpy as np
from enum import Enum
from random import randint
import threading
import os
from subprocess import call
from pynput.keyboard import Key, Listener


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


class Game:
    def __init__(self):
        self.board = Board()
        self.printer = Printer(self.board.block_board)
        self.keyboard_handler = KeyboardHandler()
        a = open('log.txt', 'w')
        a.close()

    def run(self):
        log = open('log.txt', 'a+')
        log.write(''.join(str(e) for e in self.board.get_flattenned_board()))

        keyboard_direction = self.keyboard_handler.get_dir()
        log.write(str(keyboard_direction.value) if keyboard_direction is not None else str(
            self.board.snake_head.direction.value))
        log.write('\n')
        log.close()
        to_return = self.board.update(keyboard_direction)
        self.printer.update_print()
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

        print(self.matrix_draw)

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
