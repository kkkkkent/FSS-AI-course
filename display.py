import pygame
import sys
import math
import perlin_noise
import copy
import colorsys

current_player = [1]

def float_to_rainbow_rgb(val):
    val %= 1
    val = max(0.0, min(1.0, val))

    # Map 0.0-1.0 to Hue (0.0 to 1.0 covers the full rainbow)
    # Saturation = 1.0 (vibrant), Value = 1.0 (bright)
    rgb_floats = colorsys.hsv_to_rgb(val, 1.0, 1.0)

    # Convert from 0.0-1.0 floats to 0-255 integers
    return tuple(int(c * 255) for c in rgb_floats)


class InteractiveTicTacToe9x9:
    def __init__(self, matrix, click_callback, square_size=60, color1=(240, 217, 181), color2=(181, 136, 99)):
        """
        Initializes an interactive 9x9 board using Pygame.
        :param matrix: A 9x9 list of lists containing 0, 1, or 2.
        :param click_callback: A function/lambda that accepts (row, col) when a square is clicked.
        :param square_size: The pixel width/height of each square.
        :param color1: RGB tuple for light squares.
        :param color2: RGB tuple for dark squares.
        """
        self.matrix = matrix
        self.click_callback = click_callback
        self.square_size = square_size
        self.color1 = color1
        self.color2 = color2

        self.board_size = 9 * self.square_size

        # Line color for the grid overlay
        self.grid_color = (122, 154, 96)
        self.tick = 0
        self.ax = 0
        self.ay = 0
        self.amp = 0
        self.noise = perlin_noise.PerlinNoise(seed=12893, octaves=.4)
        self.nn = 0
        self.s1 = 0
        self.s2 = 0


    def draw(self, surface):
        self.tick += 1
        self.ax = self.noise((12891038101, self.tick)) * self.amp
        self.ay = self.noise((12138103881, self.tick)) * self.amp
        self.amp /= 1.2
        """Draws the board and symbols onto the provided Pygame surface."""
        for row in range(9):
            for col in range(9):
                # 1. Calculate screen coordinates
                x1 = col * self.square_size
                y1 = row * self.square_size
                color = float_to_rainbow_rgb(self.tick / 10000 + current_player[0] / 4) if (row + col) % 2 == 0 else (
                    float_to_rainbow_rgb(self.tick / 10000 + .5 + current_player[0] / 4))
                pygame.draw.rect(surface, color, (x1 + self.ax, y1 + self.ay, self.square_size, self.square_size))
                # Draw grid border
                pygame.draw.rect(surface, color, (x1 + self.ax, y1 + self.ay, self.square_size, self.square_size), 1)

                # 3. Draw X or O based on the matrix value
                value = self.matrix[row][col]
                pad = self.square_size * 0.2  # Padding inside the square

                if value == 1:  # Draw 'X' (Blue)
                    c1 = float_to_rainbow_rgb(self.tick / 30)
                    ax = math.sin(self.tick / 5) * 20
                    ay = math.cos(self.tick / 5) * 20
                    cx = x1 + self.square_size / 2 + self.ax
                    cy = y1 + self.square_size / 2 + self.ay
                    pygame.draw.line(surface, c1, (cx + ax, cy + ay), (cx - ax, cy - ay), 4)
                    pygame.draw.line(surface, c1, (cx + ay, cy - ax), (cx - ay, cy + ax), 4)
                elif value == 2:  # Draw 'O' (Red)
                    c1 = float_to_rainbow_rgb(self.tick / 30 + .5)
                    center_x = int(x1 + self.square_size / 2)
                    center_y = int(y1 + self.square_size / 2)
                    radius = int((self.square_size / 2) - pad)
                    pygame.draw.circle(surface, c1, (center_x + self.ax, center_y + self.ay), radius * (1 + math.sin(self.tick / 15)), 4)
                    pygame.draw.circle(surface, c1, (center_x + self.ax, center_y + self.ay), radius * (1 + math.cos(self.tick / 15)), 4)
                    pygame.draw.circle(surface, c1, (center_x + self.ax, center_y + self.ay), radius * (1 + math.sin(self.tick / 15 + math.pi)), 4)
                    pygame.draw.circle(surface, c1, (center_x + self.ax, center_y + self.ay), radius * (1 + math.cos(self.tick / 15 + math.pi)), 4)

    def handle_click(self, mouse_pos):
        x, y = mouse_pos
        x -= self.ax
        y -= self.ay
        x = int(x)
        y = int(y)
        col = x // self.square_size
        row = y // self.square_size
        col = (col - self.s2 % 9 + 9) % 9
        row = (row - self.s1 % 9 + 9) % 9

        # Ensure click is inside the bounds of our 9x9 board
        if 0 <= row < 9 and 0 <= col < 9:
            self.click_callback(row, col)


cc = 0
# --- Example Usage (Game Loop Setup) ---
def main():
    pygame.init()

    square_size = 60
    board_dimension = 9 * square_size

    # Setup Pygame Window Display
    screen = pygame.display.set_set_mode if hasattr(pygame.display, 'set_set_mode') else pygame.display.set_mode(
        (board_dimension, board_dimension))
    pygame.display.set_caption("9x9 Pygame Tic-Tac-Toe")

    # Start with a completely empty 9x9 board matrix
    game_matrix = [[0 for _ in range(9)] for _ in range(9)]

    # Track whose turn it is: 1 = X, 2 = O

    # Define interaction logic via a lambda hook
    on_square_clicked = lambda r, c: handle_move(r, c)
    board: InteractiveTicTacToe9x9 | None = None

    def handle_move(row, col):
        global cc
        if game_matrix[row][col] == 0:
            game_matrix[row][col] = current_player[0]
            if cc:
                cc = False
                current_player[0] = 2 if current_player[0] == 1 else 1
            else:
                cc = 1
            print(f"Placed move at [{row}, {col}]. Next player: {current_player[0]}")
            board.amp += 100
        else:
            print(f"Square [{row}, {col}] is already filled!")

    board = InteractiveTicTacToe9x9(game_matrix, click_callback=on_square_clicked, square_size=square_size)

    clock = pygame.time.Clock()

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    board.handle_click(event.pos)

        # Drawing Logic
        screen.fill((255, 255, 255))
        board.draw(screen)

        pygame.display.flip()
        clock.tick(60)  # Maintain 60 FPS frame rate limit

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()