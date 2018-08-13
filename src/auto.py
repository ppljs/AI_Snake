from src import main
import numpy as np


class GameLogger:
    def __init__(self, board, file_path_name, file_mode):
        self.board = board
        self.log_file = open(file_path_name, file_mode)
        self.obstacles_list = {main.Content.wall, main.Content.snake}

    def update_log(self, snake_dead):
        if not snake_dead:
            dist_vec = self.calc_distances()
            snake_dir = self.board.snake_head.direction.value
            snake_head_pos = self.board.snake_head.get_pos()
            snake_i_pos, snake_j_pos = snake_head_pos[0], snake_head_pos[1]
            apple_pos = self.board.apple_pos
            apple_i_pos, apple_j_pos = apple_pos[0], apple_pos[1]
            snake_apple_dist = self.calc_distance(snake_head_pos, apple_pos)

            dist_vec.append(snake_dir)
            dist_vec.append(snake_i_pos)
            dist_vec.append(snake_j_pos)
            dist_vec.append(apple_i_pos)
            dist_vec.append(apple_j_pos)
            dist_vec.append(snake_apple_dist)

            self.log_file.write(' '.join(str(e) for e in dist_vec))


    def calc_distances(self):
        dist_vec = []
        dist_vec[0] = self.find_north_dist()
        dist_vec[1] = self.find_northeast_dist()
        dist_vec[2] = self.find_east_dist()
        dist_vec[3] = self.find_southeast_dist()
        dist_vec[4] = self.find_south_dist()
        dist_vec[5] = self.find_southwest_dist()
        dist_vec[6] = self.find_west_dist()
        dist_vec[7] = self.find_northwest_dist()

        return dist_vec

    def find_north_dist(self):
        snake_i, snake_j = self.board.snake_head.get_pos()
        for i in range(1, main.BOARD_HEIGHT):
            if self.board.block_board[snake_i+i][snake_j].content == self.obstacles_list:
                return i

    def find_northeast_dist(self):
        snake_i, snake_j = self.board.snake_head.get_pos()
        i = j = 1
        while i < main.BOARD_HEIGHT and j < main.BOARD_WIDTH:
            if self.board.block_board[snake_i+i][snake_j+j].content == self.obstacles_list:
                return i+j
            i += 1
            j = i

    def find_east_dist(self):
        snake_i, snake_j = self.board.snake_head.get_pos()
        for j in range(1, main.BOARD_WIDTH):
            if self.board.block_board[snake_i][snake_j+j].content == self.obstacles_list:
                return j

    def find_southeast_dist(self):
        snake_i, snake_j = self.board.snake_head.get_pos()
        i = j = 1
        while i < main.BOARD_HEIGHT and j < main.BOARD_WIDTH:
            if self.board.block_board[snake_i - i][snake_j + j].content == self.obstacles_list:
                return i+j
            i += 1
            j = i

    def find_south_dist(self):
        snake_i, snake_j = self.board.snake_head.get_pos()
        for i in range(1, main.BOARD_HEIGHT):
            if self.board.block_board[snake_i - i][snake_j].content == self.obstacles_list:
                return i

    def find_southwest_dist(self):
        snake_i, snake_j = self.board.snake_head.get_pos()
        i = j = 1
        while i < main.BOARD_HEIGHT and j < main.BOARD_WIDTH:
            if self.board.block_board[snake_i - i][snake_j - j].content == self.obstacles_list:
                return i + j
            i += 1
            j = i

    def find_west_dist(self):
        snake_i, snake_j = self.board.snake_head.get_pos()
        for j in range(1, main.BOARD_WIDTH):
            if self.board.block_board[snake_i][snake_j-j].content == self.obstacles_list:
                return j

    def find_northwest_dist(self):
        snake_i, snake_j = self.board.snake_head.get_pos()
        i = j = 1
        while i < main.BOARD_HEIGHT and j < main.BOARD_WIDTH:
            if self.board.block_board[snake_i + i][snake_j - j].content == self.obstacles_list:
                return i + j
            i += 1
            j = i

    def calc_distance(self, a, b):
        return (abs(a[0] - b[0]) + abs(a[1] - b[1]))

    def close(self):
        self.log_file.close()