import random
import time
import pygame
pygame.init()


# Colors
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
DARK_BLUE = (68, 68, 140)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PSEUDO_WHITE = tuple(random.randint(200, 255) for _ in range(3))

# Screen
WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect 4")

# Choice Images && Choice Rects
choice_img_size = WIDTH//4
robot_img = pygame.transform.scale(pygame.image.load("assets/robot_icon.png"), (choice_img_size, choice_img_size))
player_img = pygame.transform.scale(pygame.image.load("assets/player_icon.png"), (choice_img_size, choice_img_size))
robot_rect, player_rect = robot_img.get_rect(), player_img.get_rect()
robot_rect.x, player_rect.x = WIDTH*(5/8), WIDTH/8
robot_rect.y = player_rect.y = HEIGHT*(5/8)

# Images
board_size = 370
board_img = pygame.transform.scale(pygame.image.load("assets/board.png"), (board_size*(7/6), board_size))

# Vars
width, height = 7, 6
radius = board_img.get_width() / 17
x_list = [(WIDTH-board_img.get_width())/2*i for i in range(7)]
all_list = [[0 for i in range(width)] for j in range(height)]


# Classes
class Player:
    def __init__(self, color: tuple, id, name: str):
        self.name = name
        self.color = color
        self.rect = pygame.Rect([0, 0, board_img.get_width()/7, board_img.get_height()/6])
        self.is_falling = False
        self.is_settled = False
        self.id = id

    def draw(self):
        pygame.draw.circle(screen, self.color,
                           (self.rect.x, self.rect.y),
                           board_img.get_width() / 17)


# Functions
def random_color(a: int, b: int):
    return tuple(random.randint(a, b) for _ in range(3))


def draw_choice():
    screen.fill(PSEUDO_WHITE)

    # TEXT
    font = pygame.font.SysFont("comicsans", 70)
    wlcmto_txt = font.render("WELCOME TO", True, BLACK)
    title_txt = font.render(pygame.display.get_caption()[0], True, random_color(0, 255))
    game_txt = font.render("GAME", True, BLACK)
    for i in [wlcmto_txt, title_txt, game_txt]:
        index = [wlcmto_txt, title_txt, game_txt].index(i)
        screen.blit(i, ((WIDTH-i.get_width())/2, index*HEIGHT/8))

    # IMAGES
    screen.blit(robot_img, (robot_rect.x, robot_rect.y))
    screen.blit(player_img, (player_rect.x, player_rect.y))

    # Rects
    pygame.draw.rect(screen, BLACK,
                     pygame.Rect([robot_rect.x, robot_rect.y, choice_img_size, choice_img_size]), width=1)
    pygame.draw.rect(screen, BLACK,
                     pygame.Rect([player_rect.x, player_rect.y, choice_img_size, choice_img_size]), width=1)

    pygame.display.flip()


def draw_settled():
    def get_instance(id):
        for instance in [Player1, Player2]:
            if instance.id == id:
                return instance

    nbi = 0
    for i in all_list:
        nbj = 0
        for j in i:
            if get_instance(j):
                pygame.draw.rect(screen, get_instance(j).color,
                                 [(WIDTH-board_img.get_width())/2+board_img.get_width()/width*nbj,
                                  (HEIGHT-board_img.get_height())/2+board_img.get_height()/height*nbi,
                                  board_img.get_width()/width, board_img.get_height()/height])
            nbj += 1
        nbi += 1


def draw_screen():
    screen.fill(PSEUDO_WHITE)

    # Board Surface
    board_surf = pygame.Surface((board_size*(7/6), board_size))
    board_surf.fill(DARK_BLUE)
    screen.blit(board_surf, ((WIDTH-board_surf.get_width())/2, (HEIGHT-board_surf.get_height())/2))

    # Draw where the player is gonna make his move
    current_player.draw()

    # Draw all balls that are already settled no the board
    draw_settled()

    # Board draw
    screen.blit(board_img, ((WIDTH-board_surf.get_width())/2, (HEIGHT-board_surf.get_height())/2))

    # Check or look for eventual victory
    if check_victory():
        draw_line(get_line_pos(check_victory()))

    pygame.display.flip()


def is_mouse_in_rect(mousex, mousey, rect):
    if (rect.x < mousex < rect.x + rect.w) and (rect.y < mousey < rect.y + rect.h):
        return True
    return False


def get_column(mousex):
    x, y = (WIDTH - board_img.get_width()) / 2, (HEIGHT - board_img.get_height()) / 2
    for i in range(7):
        if x+board_img.get_width()*(i/7) < mousex < x+board_img.get_width()*(i+1)/7:
            return i
    return "out"


def show_place(row: int, column: int):
    if isinstance(column, int) and not current_player.is_falling:
        x, y = (WIDTH-board_img.get_width())/2, (HEIGHT-board_img.get_height())/2

        current_player.rect.x = x+(column*board_img.get_width()/width)+33
        current_player.rect.y = y+(row*board_img.get_height()/height)


def has_empty_place(column):
    for i in all_list:
        if i[column] == 0:
            return True


def switch(instance, instances_list):
    if instance == instances_list[0]:
        return instances_list[1]
    elif instance == instances_list[1]:
        return instances_list[0]


def check_victory():  # Will return a list -> [instance, way_it_won, (i, j)] with pos in all_list as i and j
    def get_instance(id):
        for i in [Player1, Player2]:
            if i.id == id:
                return i

    # Horizontal
    for j in range(height):
        for i in range(width-3):
            if all_list[j][i] == all_list[j][i + 1] == all_list[j][i + 2] == all_list[j][i + 3] != 0:
                return [get_instance(all_list[j][i]), "horizontal", (j, i)]

    # Vertical
    for i in range(width):
        for j in range(height-3):
            if all_list[j][i] == all_list[j + 1][i] == all_list[j + 2][i] == all_list[j + 3][i] != 0:
                return [get_instance(all_list[j][i]), "vertical", (j, i)]

    # /DIAGONAL
    for i in range(3, 7):
        for j in range(3):
            if all_list[j][i] == all_list[j + 1][i - 1] == all_list[j + 2][i - 2] == all_list[j + 3][i - 3] != 0:
                return [get_instance(all_list[j][i]), "/diagonal", (j, i)]

    # \DIAGONAL
    for i in range(4):
        for j in range(3):
            if all_list[j][i] == all_list[j + 1][i + 1] == all_list[j + 2][i + 2] == all_list[j + 3][i + 3] != 0:
                return [get_instance(all_list[j][i]), "\\diagonal", (j, i)]


def get_line_pos(victory):
    winning_way = victory[1]
    j, i = victory[2]

    start_x = (WIDTH-board_img.get_width())/2 + board_img.get_width()/width * i
    start_y = (HEIGHT-board_img.get_height())/2 + board_img.get_height()/height * j

    if winning_way == "horizontal":
        end_x = start_x + board_img.get_height()/height * 4 - (radius + 5)
        end_y = start_y + radius + 5
        start_x += radius + 5
        start_y += radius + 5
    elif winning_way == "vertical":
        end_x = start_x + (radius + 5)
        end_y = start_y + board_img.get_height()/height * 4 - radius
        start_x += radius + 5
        start_y += radius
    elif winning_way == "/diagonal":
        end_x = start_x - board_img.get_width()/width * 4 + 3*radius + 15
        end_y = start_y + board_img.get_height()/height * 4 - (radius + 5)
        start_x += radius + 5
        start_y += radius
    elif winning_way == "\\diagonal":
        end_x = start_x + board_img.get_width()/width * 4 - (radius + 5)
        end_y = start_y + board_img.get_height()/height * 4 - (radius + 5)
        start_x += radius + 5
        start_y += radius + 5

    return start_x, start_y, end_x, end_y


def draw_line(all_pos: tuple):
    startx, starty, endx, endy = all_pos

    pygame.draw.line(screen, BLACK, (startx, starty), (endx, endy), width=8)


def draw_victory(instance):
    screen.fill(PSEUDO_WHITE)

    font = pygame.font.SysFont("comicsans", 70)
    thewinneris_txt = font.render("The Winner Is", True, BLACK)
    player_txt = font.render(instance.name, True, instance.color)

    screen.blit(thewinneris_txt, ((WIDTH-thewinneris_txt.get_width())/2, HEIGHT/3))
    screen.blit(player_txt, ((WIDTH-player_txt.get_width())/2, HEIGHT/2))

    pygame.display.flip()


def draw_tie():
    screen.fill(PSEUDO_WHITE)

    font = pygame.font.SysFont("comicsans", 80)
    tie_txt = font.render("TIE", True, random_color(0, 255))

    screen.blit(tie_txt, ((WIDTH-tie_txt.get_width())/2, HEIGHT/2))

    pygame.display.flip()


# Instances
Player1 = Player(RED, 1, "Player1")
Player2 = Player(BLUE, 2, "Player2")

# Mainloop
current_player = Player1
run = True
is_started = False
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN and not is_started:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if is_mouse_in_rect(mouse_x, mouse_y, player_rect):
                player_bool = True
                robot_bool = False
                is_started = True
            elif is_mouse_in_rect(mouse_x, mouse_y, robot_rect):
                player_bool = False
                robot_bool = True
                is_started = True

        elif event.type == pygame.MOUSEBUTTONDOWN and is_started:
            if player_bool or (robot_bool and current_player != Player2):
                mouse_x = pygame.mouse.get_pos()[0]
                if has_empty_place(get_column(mouse_x)):
                    nbi = len(all_list)
                    for_run = True
                    for i in all_list[len(all_list):: -1]:
                        nbj = 0
                        for j in i:
                            if nbj == get_column(mouse_x):
                                if j == 0:
                                    all_list[nbi-1][nbj] = current_player.id
                                    for_run = False
                                    break

                            nbj += 1
                        nbi -= 1
                        if not for_run:
                            current_player = switch(current_player, [Player1, Player2])
                            break

    if not is_started:
        draw_choice()
        continue

    mouse_x = pygame.mouse.get_pos()[0]
    show_place(0, get_column(mouse_x))

    if robot_bool and current_player == Player2:
        for_run = True
        while for_run:
            rand = random.randint(0, width-1)
            if has_empty_place(rand):
                nbi = len(all_list)
                for i in all_list[len(all_list):: -1]:
                    nbj = 0
                    for j in i:
                        if nbj == rand:
                            if j == 0:
                                all_list[nbi-1][nbj] = current_player.id
                                for_run = False
                                break

                        nbj += 1
                    nbi -= 1
                    if not for_run:
                        current_player = switch(current_player, [Player1, Player2])
                        break

    draw_screen()

    # Handle eventual victory
    if check_victory():
        pygame.time.wait(3000)

        draw_victory(check_victory()[0])

        pygame.time.wait(2500)

        all_list = [[0 for i in range(width)] for j in range(height)]
        is_started = False

    # Handle the case of draw
    is_tie = True
    for i in range(width):
        if has_empty_place(i):
            is_tie = False
    if is_tie:
        pygame.time.wait(3000)
        draw_tie()
        pygame.time.wait(3000)

        all_list = [[0 for i in range(width)] for j in range(height)]
        is_started = False
