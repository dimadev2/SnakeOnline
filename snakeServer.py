import threading
import socket
import time
import uuid
from random import randrange
from config import *


fieldSync = threading.Lock()


class Snake:
    def __init__(self, id):
        self.body = [[1, 1], [0, 1]]
        self.direction = [0, 1]
        self.id = id
        self.isDead = False

    def move(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i][0] = self.body[i - 1][0]
            self.body[i][1] = self.body[i - 1][1]
        self.body[0][0] += self.direction[0]
        self.body[0][1] += self.direction[1]

        for cell in self.body:
            cell[0] = (cell[0] + count_cell) % count_cell
            cell[1] = (cell[1] + count_cell) % count_cell

    def addCell(self):
        self.body += [[self.body[-1][0], self.body[-1][1] + 1]]


class ClientHandler:
    def __init__(self, clientSocket, snakes, foods):
        self.clientSocket = clientSocket
        self.snakes = snakes
        self.foods = foods
        self.me: Snake

    def handle(self):
        id = uuid.uuid4()
        with fieldSync:
            self.snakes.append(Snake(id))
        self.me = self.snakes[-1]

        while not self.me.isDead:
            try:
                time.sleep(network_time)
                with fieldSync:
                    self.sendSnakes()
                    self.sendFoods()
                action = int.from_bytes(self.clientSocket.recv(4), "big")
                for snake in self.snakes:
                    if snake.id == id:
                        if action == UP:
                            snake.direction = [0, -1]
                        elif action == RIGHT:
                            snake.direction = [1, 0]
                        elif action == LEFT:
                            snake.direction = [-1, 0]
                        elif action == DOWN:
                            snake.direction = [0, 1]
            except Exception:
                with fieldSync:
                    self.removeSnake(id)
                self.clientSocket.close()
                break
        
        self.removeSnake(id)
        self.clientSocket.close()

    def sendSnakes(self):
        self.clientSocket.sendall(int(len(self.snakes)).to_bytes(4, "big"))
        for snake in self.snakes:
            self.clientSocket.sendall(int(len(snake.body)).to_bytes(4, "big"))
            for cell in snake.body:
                self.clientSocket.sendall(int(cell[0]).to_bytes(4, "big"))
                self.clientSocket.sendall(int(cell[1]).to_bytes(4, "big"))

    def sendFoods(self):
        self.clientSocket.sendall(int(len(self.foods)).to_bytes(4, "big"))
        for food in self.foods:
            self.clientSocket.sendall(int(food[0]).to_bytes(4, "big"))
            self.clientSocket.sendall(int(food[1]).to_bytes(4, "big"))

    def removeSnake(self, id):
        for i in range(len(self.snakes)):
            if self.snakes[i].id == id:
                for cell in self.snakes[i].body:
                    if randrange(100) > FOOD_AFTER_DEAD_FREQ* 100:
                        self.foods.append(cell[:])
                del self.snakes[i]
                break


class SnakeServer:
    def __init__(self):
        self.clientHandlers = []
        self.snakes = []
        self.foods = []
        self.scores = []

    def start(self):
        threading.Thread(target=self.clientConnectMainLoop).start()
        self.initFood()
        self.startGame()

    def startGame(self):
        try:
            while True:
                self.checkCollision()
                with fieldSync:
                    while len(self.foods) < len(self.snakes) * FOOD_FOR_ONE + START_FOOD:
                        self.generateFood()
                
                with fieldSync:
                    self.moveSnakes()
                time.sleep(business_time)

        except KeyboardInterrupt:
            self.closeConnections()
            exit(0)

    def closeConnections(self):
        for client in self.clientHandlers:
            client.clientSocket.close()

    def generateFood(self):
        x = randrange(1, count_cell - 2)
        y = randrange(1, count_cell - 2)
        
        for snake in self.snakes:
            for i in range(1, len(snake.body)):
                if snake.body[i][0] == x:
                    if snake.body[i][1] == y:
                        return self.generateFood()
                    
        for food in self.foods:
            if x == food[0] and y == food[1]:
                return self.generateFood()

        self.foods.append([x, y])

    def initFood(self):
        for i in range(START_FOOD):
            self.generateFood()


    def clientConnectMainLoop(self):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            serverSocket.bind((server_addr, server_port))
        except Exception:
            serverSocket.close()
            serverSocket.bind((server_addr, server_port))
        
        serverSocket.listen(1)

        while True:
            print("wait connection")
            clientSocket, _ = serverSocket.accept()
            print("client connected")
            clientHandler = ClientHandler(clientSocket, self.snakes, self.foods)
            threading.Thread(target=clientHandler.handle).start()
            self.clientHandlers.append(clientHandler)

    def checkCollision(self):
        for i in range(len(self.snakes) - 1):
            # for j in range(i, len(self.snakes)):
            for j in range(i + 1, len(self.snakes)):
                snake1 = self.snakes[i]
                snake2 = self.snakes[j]

                if self.collisionWithSnake(snake1.body, snake2.body):
                    self.snakes[i].isDead = True
                if self.collisionWithSnake(snake2.body, snake1.body):
                    self.snakes[j].isDead = True

        for snake in self.snakes:
            if snake.isDead:
                continue
            
            deleted_food = []
            for i in range(len(self.foods)):
                if self.collisionWithFood(snake.body, self.foods[i]):
                    deleted_food.append(i)
                    snake.addCell()

            with fieldSync:
                for deleted_food_id in deleted_food[::-1]:
                    del self.foods[deleted_food_id]
                    while len(self.foods) < len(self.snakes) * FOOD_FOR_ONE + START_FOOD:
                        self.generateFood()
        

    def collisionWithSnake(self, snake1, snake2):
        head1 = snake1[0]
        for cell in snake2:
            if head1[0] == cell[0] and head1[1] == cell[1]:
                return True

        return False
    
    def collisionWithFood(self, snake, food):
        for cell in snake:
            if cell[0] == food[0] and cell[1] == food[1]:
                return True
        
        return False
        

                

        pass
        #generateFood

    def moveSnakes(self):
        for snake in self.snakes:
            snake.move()

if __name__ == "__main__":
    server = SnakeServer()
    server.start()
