import tkinter
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
import snake


def config_gui():
    root = tkinter.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    side_length = screen_height if screen_height < screen_width else screen_width
    Config.set('graphics', 'width', int(0.7 * side_length))
    Config.set('graphics', 'height', int(0.7 * side_length))
    Config.write()


class Wall(Image):
    pass


class Apple(Image):
    pass


class Snake(Image):
    pass


class SnakeGUI(FloatLayout):

    def __init__(self, **kwargs):
        super(SnakeGUI, self).__init__(**kwargs)

        self.row_number = snake.BOARD_HEIGHT
        self.column_number = snake.BOARD_WIDTH

        self.apple = Apple()
        self.snake_list = []

        self.update_unit_measurements()
        self.bind(size=self.update_unit_measurements)
    
    def update_gui(self, board):
        apple_pos = board.apple_pos
        snake_pos_list = board.get_snake_pos_ji_list()
        self.update_apple_pos(apple_pos[1], apple_pos[0])
        self.update_snake_pos(snake_pos_list)

    def update_unit_measurements(self, *args):
        self.unit_height = self.height / self.row_number
        self.unit_width = self.width / self.column_number
        self.clear_widgets()
        self.add_walls()
        self.update_apple_size()
        self.add_widget(self.apple)
        self.update_snake_size()
        self.add_snake()

    def add_walls(self):
        for i in range(self.row_number):
            for j in range(self.column_number):
                if i == 0 or i == self.row_number - 1 or j == 0 or j == self.column_number - 1:
                    temp_wall = Wall()
                    temp_wall.pos = j * self.unit_width, i * self.unit_height
                    temp_wall.size = self.unit_width, self.unit_height
                    self.add_widget(temp_wall)

    def update_apple_pos(self, pos_j, pos_i):
        self.apple.pos = self.unit_width * pos_j, self.unit_height * ((self.row_number - 1) - pos_i)

    def update_apple_size(self):
        circle_diameter = self.unit_width if self.unit_width < self.unit_height else self.unit_height
        self.apple.size = circle_diameter, circle_diameter

    def add_snake(self):
        for snake_piece in self.snake_list:
            self.add_widget(snake_piece)

    def update_snake_pos(self, pos_list=None):
        snake_size = len(pos_list)
        while snake_size > len(self.snake_list):
            tmp_snake = Snake()
            tmp_snake.size = self.unit_width, self.unit_height

            self.snake_list.append(tmp_snake)
            self.add_widget(tmp_snake)
        for pos, snake_piece in zip(pos_list, self.snake_list):
            snake_piece.pos = self.unit_width * \
                pos[0], self.unit_height * ((self.row_number - 1) - pos[1])

    def update_snake_size(self):
        for snake_piece in self.snake_list:
            snake_piece.size = self.unit_width, self.unit_height
