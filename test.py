import pygame
import sys

# Инициализация Pygame
pygame.init()

# Размеры окна
WIDTH, HEIGHT = 800, 600

# Цвета
WHITE = (255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)  # Прозрачный цвет

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Простое меню")

# Загрузка фонового изображения
background_image = pygame.image.load('background.png')
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Шрифты
font = pygame.font.Font(None, 36)

# Создание прозрачных кнопок
class TransparentButton(pygame.sprite.Sprite):
    def __init__(self, text, x, y, width, height, callback):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.callback = callback
        self.render_text(text)

    def render_text(self, text):
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        self.image.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def on_connect_clicked():
    print("Выбран пункт 'Подсоединиться'")

def on_exit_clicked():
    pygame.quit()
    sys.exit()

def main_menu():
    connect_button = TransparentButton("Подсоединиться", WIDTH // 3, HEIGHT // 2, 200, 50, on_connect_clicked)
    exit_button = TransparentButton("Выход", 2 * WIDTH // 3, HEIGHT // 2, 200, 50, on_exit_clicked)
    buttons = pygame.sprite.Group(connect_button, exit_button)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            # Передача событий кнопкам
            buttons.update(event)

        # Отрисовка фона
        screen.blit(background_image, (0, 0))

        # Отрисовка текста меню
        draw_text("Простое меню", font, WHITE, WIDTH // 2, HEIGHT // 4)

        # Отрисовка кнопок
        buttons.draw(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()