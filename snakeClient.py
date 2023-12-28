import pygame
from random import randint
from threading import Thread, Lock
import socket
from config import *

def draw_board():
    win.fill((100, 100, 100))

    pygame.draw.rect(win, (0, 0, 0), (0, 0, cell_size, screen_width))
    pygame.draw.rect(win, (0, 0, 0), (0, 0, screen_width, cell_size))
    pygame.draw.rect(win, (0, 0, 0), (screen_width - cell_size, 0, cell_size, screen_width))
    pygame.draw.rect(win, (0, 0, 0), (0, screen_height - cell_size, screen_width, cell_size))

    for i in range(count_cell + 1):
        pygame.draw.line(win, (255, 255, 255), (0, i*(cell_size + 1)), (screen_width, i*(cell_size + 1)))

    for i in range(count_cell + 1):
        pygame.draw.line(win, (255, 255, 255), (i*(cell_size + 1), 0), (i*(cell_size + 1), screen_height))


def draw_snake(snake):
    for cell in snake:
        pygame.draw.rect(win, (0, 255, 0), (cell[0]*(cell_size + 1) + 1, cell[1]*(cell_size + 1) + 1, cell_size, cell_size))


def draw_food(food):
    pygame.draw.rect(win, (255, 0, 0), (food[0]*(cell_size + 1) + 1, food[1]*(cell_size + 1) + 1, cell_size, cell_size))


def recv_snakes():
    snakes = []
    n = int.from_bytes(client_sock.recv(4), "big")
    for i in range(n):
        snake = []
        snake_len = int.from_bytes(client_sock.recv(4), "big")

        for _ in range(snake_len):
            x = int.from_bytes(client_sock.recv(4), "big")
            y = int.from_bytes(client_sock.recv(4), "big")
            snake.append([x, y])

        snakes.append(snake)

    return snakes


def recv_foods():
    foods = []
    n = int.from_bytes(client_sock.recv(4), "big")

    for _ in range(n):
        x = int.from_bytes(client_sock.recv(4), "big")
        y = int.from_bytes(client_sock.recv(4), "big")
        foods.append([x, y])

    return foods


def recv_routine():
    try:
        while True:
            try:
                snakes = recv_snakes()
                foods = recv_foods()
                client_sock.send(int(key).to_bytes(4, "big"))
            except OSError:
                client_sock.close()
                pygame.quit()

            draw_board()

            for snake in snakes:
                draw_snake(snake)

            for food in foods:
                draw_food(food)

            pygame.display.update()

    except KeyboardInterrupt:
        client_sock.close()
        pygame.quit()


pygame.init()

key = NONE

run = True

screen_width = (cell_size + 1) * count_cell + 1
screen_height = (cell_size + 1) * count_cell + 1

win = pygame.display.set_mode((screen_width, screen_height))


client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((server_addr, server_port))
Thread(target=recv_routine).start()

while True:
    pygame.time.delay(150)

    m_event = pygame.event.get()
    for event in m_event:
        if event.type == pygame.QUIT:
            client_sock.close()
            pygame.quit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                key = UP

            elif event.key == pygame.K_DOWN:
                key = DOWN

            elif event.key == pygame.K_RIGHT:
                key = RIGHT

            elif event.key == pygame.K_LEFT:
                key = LEFT
