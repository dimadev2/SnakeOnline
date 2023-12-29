import pygame
from random import randint
from threading import Thread, Lock
from random import randrange
from pygame.locals import *
import socket
from config import *
import sys


def draw_board():
    win.fill((100, 100, 100))

    for i in range(count_cell + 1):
        pygame.draw.line(win, (255, 255, 255), (0, i*(cell_size + 1)), (screen_width, i*(cell_size + 1)))

    for i in range(count_cell + 1):
        pygame.draw.line(win, (255, 255, 255), (i*(cell_size + 1), 0), (i*(cell_size + 1), screen_height))


def draw_snake(snake, color):
    for cell in snake:
        pygame.draw.rect(win, color, (cell[0]*(cell_size + 1), cell[1]*(cell_size + 1), cell_size + 2, cell_size + 2))


def draw_food(food):
    pygame.draw.rect(win, (255, 0, 0), (food[0]*(cell_size + 1) + 1, food[1]*(cell_size + 1) + 1, cell_size, cell_size))


def recv_snakes():
    snakes = []
    colors = []
    n = int.from_bytes(client_sock.recv(4), "big")
    for i in range(n):
        snake = []
        snake_len = int.from_bytes(client_sock.recv(4), "big")
        color = []
        color.append(int.from_bytes(client_sock.recv(4), "big"))
        color.append(int.from_bytes(client_sock.recv(4), "big"))
        color.append(int.from_bytes(client_sock.recv(4), "big"))

        for _ in range(snake_len):
            x = int.from_bytes(client_sock.recv(4), "big")
            y = int.from_bytes(client_sock.recv(4), "big")
            snake.append([x, y])

        colors.append(color)
        snakes.append(snake)

    return [snakes, colors]


def recv_foods():
    foods = []
    n = int.from_bytes(client_sock.recv(4), "big")

    for _ in range(n):
        x = int.from_bytes(client_sock.recv(4), "big")
        y = int.from_bytes(client_sock.recv(4), "big")
        foods.append([x, y])

    return foods


def recv_routine():
    global game_ended
    try:
        while not game_ended:
            try:
                [snakes, colors] = recv_snakes()
                foods = recv_foods()
                client_sock.send(int(key).to_bytes(4, "big"))
            except OSError:
                client_sock.close()
                game_ended = True
                break

            draw_board()

            for i in range(len(snakes)):
                draw_snake(snakes[i], colors[i])

            for food in foods:
                draw_food(food)

            pygame.display.update()

    except KeyboardInterrupt:
        client_sock.close()
        game_ended = True


def start_game():
    global key
    global win
    global client_sock

    run = True
    game_ended = False

    win = pygame.display.set_mode((screen_width, screen_height))

    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if (len(sys.argv) == 1):
            client_sock.connect((server_addr, server_port))
        else:
            client_sock.connect((sys.argv[1], server_port))
    except ConnectionRefusedError:
        print('Server is not reachable')
        return

    Thread(target=recv_routine).start()

    while not game_ended:
        pygame.time.delay(150)

        m_event = pygame.event.get()
        for event in m_event:
            if event.type == pygame.QUIT:
                client_sock.close()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    key = UP

                elif event.key == pygame.K_DOWN:
                    key = DOWN

                elif event.key == pygame.K_RIGHT:
                    key = RIGHT

                elif event.key == pygame.K_LEFT:
                    key = LEFT

                if event.key == pygame.K_ESCAPE:
                    client_sock.close()
                    game_ended = True
                    break


def draw_text(text, x, y, font, screen, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


def draw_menu():
    global win

    win = pygame.display.set_mode((WIDTH, HEIGHT))

    pygame.display.set_caption("ЯЗМЕЯ")

    background = pygame.image.load("background.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    button1_rect = pygame.Rect(50, 50, 300, 450)
    button2_rect = pygame.Rect(450, 5, 350, 400)

    running = True

    pygame.mixer.music.load("song.mp3")
    pygame.mixer.music.play(-1)

    pygame.font.init()
    font = pygame.font.Font(None, 36)

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                client_sock.close()
                running = False

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = pygame.mouse.get_pos()

                    if button1_rect.collidepoint(pos):
                        pygame.quit()
                        client_sock.close()
                        sys.exit()

                    elif button2_rect.collidepoint(pos):
                        start_game()
                        win = pygame.display.set_mode((WIDTH, HEIGHT))

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    client_sock.close()
                    sys.exit()

        win.blit(background, (0, 0))
        draw_text("Vlad", int(WIDTH*0.875), int(HEIGHT*0.875), font, win)

        # pygame.draw.rect(win, (255, 0, 0, 128), button1_rect)
        # pygame.draw.rect(win, (0, 255, 0, 128), button2_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
key = NONE
game_ended = False

screen_width = (cell_size + 1) * count_cell + 1
screen_height = (cell_size + 1) * count_cell + 1

win = pygame.display


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("ЯЗМЕЯ")

    draw_menu()
