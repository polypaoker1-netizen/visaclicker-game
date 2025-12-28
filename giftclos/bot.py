import pygame
import random
import time
import sys
from enum import Enum

# Инициализация PyGame
pygame.init()

# Константы
WIDTH, HEIGHT = 1000, 700
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 50)
PURPLE = (180, 70, 220)
DARK_BLUE = (20, 20, 40)
LIGHT_BLUE = (100, 150, 255)

class GameState(Enum):
    MAIN_MENU = 1
    PLAYING = 2
    UPGRADES = 3
    INFO = 4
    MAXIM = 5

class ShapeType(Enum):
    CIRCLE = 1
    TRIANGLE = 2
    SQUARE = 3

class NegativeEffect(Enum):
    SLOW_CLICKS = 1
    SHRINK_TARGET = 2
    RANDOM_MOVEMENT = 3

class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_BLUE, hover_color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.SysFont('arial', 28)
        self.clicked = False
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=15)
        pygame.draw.rect(screen, WHITE, self.rect, 3, border_radius=15)
        
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.current_color = self.hover_color if self.rect.collidepoint(pos) else self.color
        return self.rect.collidepoint(pos)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class FlyingLetter:
    def __init__(self, letter, x, y):
        self.letter = letter
        self.x = x
        self.y = y
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.size = random.randint(40, 80)
        self.color = random.choice([RED, PURPLE, YELLOW, GREEN, BLUE])
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rotation += self.rotation_speed
        
        # Отскок от краев
        if self.x < 50 or self.x > WIDTH - 50:
            self.speed_x *= -1
        if self.y < 50 or self.y > HEIGHT - 150:
            self.speed_y *= -1
            
    def draw(self, screen):
        font = pygame.font.SysFont('arial', self.size, bold=True)
        text = font.render(self.letter, True, self.color)
        
        # Поворот текста
        rotated_text = pygame.transform.rotate(text, self.rotation)
        text_rect = rotated_text.get_rect(center=(self.x, self.y))
        screen.blit(rotated_text, text_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("VisaClicker")
        self.clock = pygame.time.Clock()
        
        # Состояние игры
        self.state = GameState.MAIN_MENU
        
        # Игровые переменные
        self.score = 0
        self.level = 1
        self.clicks = 0
        self.shape = ShapeType.CIRCLE
        self.shape_size = 120
        self.shape_x = WIDTH // 2
        self.shape_y = HEIGHT // 2
        
        # Улучшения
        self.click_power = 1
        self.click_multiplier = 1
        self.auto_clicker = 0
        self.upgrade_costs = {
            "power": 50,
            "multiplier": 100,
            "auto": 75
        }
        self.upgrade_levels = {
            "power": 0,
            "multiplier": 0,
            "auto": 0
        }
        
        # Негативные эффекты
        self.active_effect = None
        self.effect_timer = 0
        self.effect_start_time = 0
        self.effect_duration = 10
        self.next_effect_time = time.time() + 120
        
        # Таймеры
        self.last_auto_click = time.time()
        self.last_shape_change = time.time()
        self.shape_change_interval = 2.0
        
        # Эффекты UI
        self.show_price_text = None
        self.price_timer = 0
        
        # Снежинки для меню
        self.snowflakes = []
        for _ in range(80):
            self.snowflakes.append([
                random.randint(0, WIDTH),
                random.randint(-100, HEIGHT),
                random.uniform(0.5, 2.0),  # скорость
                random.randint(2, 5)  # размер
            ])
        
        # Летающие буквы для экрана "Максим лох"
        self.flying_letters = []
        self.maxim_letters = ["М", "А", "К", "С", "И", "М", "Л", "О", "Х"]
        self.letters_launched = [False] * len(self.maxim_letters)
        self.letter_launch_timer = 0
        self.letter_launch_index = 0
        
        # Создаем кнопки главного меню
        button_width, button_height = 250, 60
        center_x = WIDTH // 2 - button_width // 2
        self.menu_buttons = [
            Button(center_x, 200, button_width, button_height, "▶ ИГРАТЬ"),
            Button(center_x, 280, button_width, button_height, "⚡ УЛУЧШЕНИЯ"),
            Button(center_x, 360, button_width, button_height, "ℹ ИНФОРМАЦИЯ"),
            Button(center_x, 440, button_width, button_height, "😡 МАКСИМ ЛОХ")
        ]
        
        # Кнопки улучшений (исправленные координаты)
        self.upgrade_buttons = [
            Button(100, 180, 350, 70, f"УСИЛЕНИЕ КЛИКА (Ур. {self.upgrade_levels['power']})"),
            Button(100, 270, 350, 70, f"МНОЖИТЕЛЬ (Ур. {self.upgrade_levels['multiplier']})"),
            Button(100, 360, 350, 70, f"АВТОКЛИКЕР (Ур. {self.upgrade_levels['auto']})"),
            Button(WIDTH - 200, 600, 150, 50, "← НАЗАД")
        ]
        
        # Кнопка назад
        self.back_button = Button(50, 50, 120, 50, "← НАЗАД")
        
        self.running = True
    
    def update_snowflakes(self):
        """Обновление снежинок в меню"""
        for flake in self.snowflakes:
            flake[1] += flake[2]  # двигаем вниз
            flake[0] += random.uniform(-0.5, 0.5)  # немного в сторону
            
            # Если снежинка упала, поднимаем наверх
            if flake[1] > HEIGHT:
                flake[1] = random.randint(-100, -10)
                flake[0] = random.randint(0, WIDTH)
    
    def draw_snowflakes(self):
        """Рисует снежинки"""
        for flake in self.snowflakes:
            size = flake[3]
            brightness = random.randint(200, 255)
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), 
                             (int(flake[0]), int(flake[1])), size)
    
    def update_flying_letters(self):
        """Обновление летающих букв"""
        # Запускаем буквы по одной с задержкой
        current_time = time.time()
        if (self.state == GameState.MAXIM and 
            self.letter_launch_index < len(self.maxim_letters) and
            current_time - self.letter_launch_timer > 0.5):
            
            letter = self.maxim_letters[self.letter_launch_index]
            start_x = WIDTH // 2
            start_y = HEIGHT // 2
            self.flying_letters.append(FlyingLetter(letter, start_x, start_y))
            self.letter_launch_index += 1
            self.letter_launch_timer = current_time
        
        # Обновляем существующие буквы
        for letter in self.flying_letters:
            letter.update()
    
    def draw_main_menu(self):
        """Рисует главное меню"""
        self.screen.fill(DARK_BLUE)
        
        # Рисуем снежинки
        self.draw_snowflakes()
        
        # Название игры вверху
        title_font = pygame.font.SysFont('arial', 72, bold=True)
        title = title_font.render("VisaClicker", True, LIGHT_BLUE)
        title_shadow = title_font.render("VisaClicker", True, (100, 100, 200))
        self.screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 3, 53))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Подзаголовок
        subtitle_font = pygame.font.SysFont('arial', 24)
        subtitle = subtitle_font.render("Игра от команды Visateam", True, WHITE)
        self.screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 130))
        
        # Рисуем кнопки
        for button in self.menu_buttons:
            button.draw(self.screen)
        
        # Текущий счет (если есть) - исправлено положение
        if self.score > 0:
            score_font = pygame.font.SysFont('arial', 32)
            score_text = score_font.render(f"Баланс: {self.score} VISA", True, YELLOW)
            self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT - 150))
        
        # Автор внизу - исправлен год
        footer_font = pygame.font.SysFont('arial', 18)
        footer = footer_font.render("© 2025 Clicker от команды Visateam", True, (150, 150, 200))
        self.screen.blit(footer, (WIDTH//2 - footer.get_width()//2, HEIGHT - 40))
    
    def draw_game_screen(self):
        """Рисует игровой экран"""
        self.screen.fill(DARK_BLUE)
        
        # Рисуем фигуру
        color = RED if self.shape == ShapeType.CIRCLE else GREEN if self.shape == ShapeType.TRIANGLE else YELLOW
        size = self.shape_size
        
        # Эффект уменьшения
        if self.active_effect == NegativeEffect.SHRINK_TARGET:
            size = max(40, size // 2)
        
        # Эффект случайного движения
        if self.active_effect == NegativeEffect.RANDOM_MOVEMENT:
            self.shape_x += random.randint(-5, 5)
            self.shape_y += random.randint(-5, 5)
            self.shape_x = max(size, min(WIDTH - size, self.shape_x))
            self.shape_y = max(size, min(HEIGHT - size, self.shape_y))
        
        # Рисуем фигуру
        if self.shape == ShapeType.CIRCLE:
            pygame.draw.circle(self.screen, color, (self.shape_x, self.shape_y), size)
            pygame.draw.circle(self.screen, WHITE, (self.shape_x, self.shape_y), size, 5)
        elif self.shape == ShapeType.TRIANGLE:
            points = [
                (self.shape_x, self.shape_y - size),
                (self.shape_x - size, self.shape_y + size),
                (self.shape_x + size, self.shape_y + size)
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, WHITE, points, 5)
        elif self.shape == ShapeType.SQUARE:
            rect = pygame.Rect(self.shape_x - size, self.shape_y - size, size * 2, size * 2)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 5)
        
        # Информация сверху - исправлено положение
        font = pygame.font.SysFont('arial', 28)
        score_text = font.render(f"VISA: {self.score}", True, YELLOW)
        level_text = font.render(f"Уровень: {self.level}", True, GREEN)
        clicks_text = font.render(f"Клики: {self.clicks}", True, BLUE)
        
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(level_text, (20, 60))
        self.screen.blit(clicks_text, (20, 100))
        
        # Информация о улучшениях справа - исправлено положение
        upgrade_font = pygame.font.SysFont('arial', 24)
        power_text = upgrade_font.render(f"Сила клика: x{self.click_power}", True, LIGHT_BLUE)
        multi_text = upgrade_font.render(f"Множитель: x{self.click_multiplier}", True, LIGHT_BLUE)
        auto_text = upgrade_font.render(f"Автокликеров: {self.auto_clicker}", True, LIGHT_BLUE)
        
        self.screen.blit(power_text, (WIDTH - 250, 20))
        self.screen.blit(multi_text, (WIDTH - 250, 50))
        self.screen.blit(auto_text, (WIDTH - 250, 80))
        
        # Текущая фигура - исправлено положение
        shape_names = {
            ShapeType.CIRCLE: "КРУГ",
            ShapeType.TRIANGLE: "ТРЕУГОЛЬНИК", 
            ShapeType.SQUARE: "КВАДРАТ"
        }
        shape_text = font.render(f"Фигура: {shape_names[self.shape]}", True, WHITE)
        self.screen.blit(shape_text, (WIDTH//2 - shape_text.get_width()//2, HEIGHT - 120))
        
        # Активный негативный эффект
        if self.active_effect:
            effect_time_left = self.effect_duration - (time.time() - self.effect_start_time)
            if effect_time_left > 0:
                effect_names = {
                    NegativeEffect.SLOW_CLICKS: "⏳ ЗАМЕДЛЕНИЕ",
                    NegativeEffect.SHRINK_TARGET: "📉 МАЛЕНЬКАЯ ЦЕЛЬ",
                    NegativeEffect.RANDOM_MOVEMENT: "🌀 ДВИЖУЩАЯСЯ ЦЕЛЬ"
                }
                effect_text = font.render(f"{effect_names[self.active_effect]} ({int(effect_time_left)}с)", True, RED)
                self.screen.blit(effect_text, (WIDTH//2 - effect_text.get_width()//2, HEIGHT - 80))
        
        # Кнопка назад - исправлена надпись
        self.back_button.text = "← МЕНЮ"
        self.back_button.draw(self.screen)
        
        # Подсказка внизу
        hint_font = pygame.font.SysFont('arial', 20)
        hint = hint_font.render("Кликай по фигуре! Меняется каждые 2 секунды", True, (200, 200, 200))
        self.screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 50))
    
    def draw_upgrades_screen(self):
        """Экран улучшений - ИСПРАВЛЕННЫЙ"""
        self.screen.fill(DARK_BLUE)
        
        # Заголовок
        title_font = pygame.font.SysFont('arial', 48, bold=True)
        title = title_font.render("УЛУЧШЕНИЯ", True, YELLOW)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Текущий баланс - исправлено обрезание текста
        balance_font = pygame.font.SysFont('arial', 32)
        balance_text = f"Ваш баланс: {self.score} VISA"
        balance = balance_font.render(balance_text, True, GREEN)
        
        # Проверяем ширину текста и обрезаем если нужно
        max_width = WIDTH - 200
        if balance.get_width() > max_width:
            # Уменьшаем размер шрифта
            smaller_font = pygame.font.SysFont('arial', 28)
            balance = smaller_font.render(balance_text, True, GREEN)
        
        self.screen.blit(balance, (WIDTH//2 - balance.get_width()//2, 120))
        
        # Обновляем текст кнопок - исправлено чтобы не вылезало
        power_text = f"УСИЛЕНИЕ КЛИКА (Ур. {self.upgrade_levels['power']})"
        multi_text = f"МНОЖИТЕЛЬ (Ур. {self.upgrade_levels['multiplier']})"
        auto_text = f"АВТОКЛИКЕР (Ур. {self.upgrade_levels['auto']})"
        
        # Обрезаем текст если слишком длинный
        test_font = pygame.font.SysFont('arial', 28)
        if test_font.size(power_text + f" - {self.upgrade_costs['power']} VISA")[0] > 350:
            power_text = f"УСИЛЕНИЕ (Ур. {self.upgrade_levels['power']})"
        if test_font.size(multi_text + f" - {self.upgrade_costs['multiplier']} VISA")[0] > 350:
            multi_text = f"МНОЖИТЕЛЬ (Ур. {self.upgrade_levels['multiplier']})"
        if test_font.size(auto_text + f" - {self.upgrade_costs['auto']} VISA")[0] > 350:
            auto_text = f"АВТОКЛИК (Ур. {self.upgrade_levels['auto']})"
        
        self.upgrade_buttons[0].text = f"{power_text} - {self.upgrade_costs['power']} VISA"
        self.upgrade_buttons[1].text = f"{multi_text} - {self.upgrade_costs['multiplier']} VISA"
        self.upgrade_buttons[2].text = f"{auto_text} - {self.upgrade_costs['auto']} VISA"
        
        # Рисуем кнопки улучшений
        for button in self.upgrade_buttons:
            button.draw(self.screen)
        
        # Описания улучшений справа от кнопок - исправлены координаты
        desc_font = pygame.font.SysFont('arial', 20)
        descriptions = [
            "Каждый клик дает больше VISA",
            "Умножает весь получаемый доход",
            "Автоматически кликает за вас"
        ]
        
        for i, desc in enumerate(descriptions):
            desc_text = desc_font.render(desc, True, (200, 200, 255))
            self.screen.blit(desc_text, (500, 190 + i * 90))
        
        # Показываем цену следующего улучшения если была покупка
        if self.show_price_text and time.time() - self.price_timer < 2:
            price_font = pygame.font.SysFont('arial', 24)
            price_surf = price_font.render(self.show_price_text, True, RED)
            self.screen.blit(price_surf, (WIDTH//2 - price_surf.get_width()//2, 500))
        
        # Кнопка назад
        self.back_button.text = "← МЕНЮ"
        self.back_button.draw(self.screen)
    
    def draw_info_screen(self):
        """Экран информации"""
        self.screen.fill(DARK_BLUE)
        
        # Заголовок
        title_font = pygame.font.SysFont('arial', 48, bold=True)
        title = title_font.render("ИНФОРМАЦИЯ ОБ ИГРЕ", True, LIGHT_BLUE)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Текст информации
        info_font = pygame.font.SysFont('arial', 22)
        lines = [
            "VisaClicker - игра про клики и стратегию!",
            "",
            "🎯 ЦЕЛЬ ИГРЫ:",
            "• Кликай по фигурам в центре экрана",
            "• Зарабатывай VISA-очки",
            "• Покупай улучшения в магазине",
            "",
            "⚡ УЛУЧШЕНИЯ:",
            "• Усиление клика - больше очков за клик",
            "• Множитель - умножает весь доход",
            "• Автокликер - автоматические клики",
            "",
            "⚠️ НЕГАТИВНЫЕ ЭФФЕКТЫ:",
            "• Появляются каждые 2 минуты",
            "• Замедление - клики дают меньше",
            "• Маленькая цель - сложнее попасть",
            "• Движущаяся цель - убегает от мыши",
            "",
            "Удачи в игре!"
        ]
        
        y_offset = 120
        for line in lines:
            if line:
                color = WHITE
                if "🎯" in line or "⚡" in line or "⚠️" in line:
                    color = YELLOW
                elif "•" in line:
                    color = (200, 200, 255)
                
                text = info_font.render(line, True, color)
                self.screen.blit(text, (100, y_offset))
            y_offset += 32
        
        # Кнопка назад
        self.back_button.text = "← МЕНЮ"
        self.back_button.draw(self.screen)
        
        # Копирайт внизу
        footer_font = pygame.font.SysFont('arial', 18)
        footer = footer_font.render("© 2025 Clicker от команды Visateam", True, (150, 150, 200))
        self.screen.blit(footer, (WIDTH//2 - footer.get_width()//2, HEIGHT - 40))
    
    def draw_maxim_screen(self):
        """Экран 'Максим лох' - ИСПРАВЛЕННЫЙ"""
        self.screen.fill(DARK_BLUE)
        
        # Заголовок
        title_font = pygame.font.SysFont('arial', 48, bold=True)
        title = title_font.render("МАКСИМ ЛОХ", True, RED)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Инструкция
        inst_font = pygame.font.SysFont('arial', 24)
        instruction = inst_font.render("Буквы начнут летать одна за другой...", True, WHITE)
        self.screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, 120))
        
        # Рисуем летающие буквы
        for letter in self.flying_letters:
            letter.draw(self.screen)
        
        # Если все буквы запущены, показываем сообщение
        if self.letter_launch_index >= len(self.maxim_letters) and len(self.flying_letters) > 0:
            done_font = pygame.font.SysFont('arial', 32)
            done_text = done_font.render("Все буквы в полёте!", True, GREEN)
            self.screen.blit(done_text, (WIDTH//2 - done_text.get_width()//2, HEIGHT - 150))
        
        # Кнопка назад
        self.back_button.text = "← МЕНЮ"
        self.back_button.draw(self.screen)
        
        # Шутка внизу
        joke_font = pygame.font.SysFont('arial', 20)
        joke = joke_font.render("*Это шутка, все совпадения случайны*", True, (150, 150, 150))
        self.screen.blit(joke, (WIDTH//2 - joke.get_width()//2, HEIGHT - 80))
        
        # Копирайт
        footer_font = pygame.font.SysFont('arial', 18)
        footer = footer_font.render("© 2025 Clicker от команды Visateam", True, (150, 150, 200))
        self.screen.blit(footer, (WIDTH//2 - footer.get_width()//2, HEIGHT - 40))
    
    def reset_maxim_screen(self):
        """Сброс экрана 'Максим лох'"""
        self.flying_letters = []
        self.letter_launch_index = 0
        self.letter_launch_timer = time.time()
    
    def handle_shape_click(self, pos):
        """Обработка клика по фигуре"""
        # Проверяем попадание
        distance = ((pos[0] - self.shape_x)**2 + (pos[1] - self.shape_y)**2)**0.5
        
        hit = False
        if self.shape == ShapeType.CIRCLE and distance <= self.shape_size:
            hit = True
        elif self.shape == ShapeType.TRIANGLE:
            if (abs(pos[0] - self.shape_x) < self.shape_size and 
                abs(pos[1] - self.shape_y) < self.shape_size):
                hit = True
        elif self.shape == ShapeType.SQUARE:
            if (abs(pos[0] - self.shape_x) < self.shape_size and 
                abs(pos[1] - self.shape_y) < self.shape_size):
                hit = True
        
        if hit:
            # Рассчет награды
            base_reward = 10
            reward = base_reward * self.click_power * self.click_multiplier
            
            # Эффект замедления
            if self.active_effect == NegativeEffect.SLOW_CLICKS:
                reward = max(1, reward // 2)
            
            self.score += reward
            self.clicks += 1
            
            # Проверка уровня
            if self.clicks % 20 == 0:
                self.level += 1
                self.shape_size = max(60, 150 - self.level * 3)
            
            # Меняем фигуру
            self.change_shape()
            
            return True
        return False
    
    def change_shape(self):
        """Меняет фигуру"""
        if self.level <= 5:
            self.shape = ShapeType.CIRCLE
        elif self.level <= 10:
            self.shape = ShapeType.TRIANGLE
        else:
            self.shape = random.choice(list(ShapeType))
        
        # Сбрасываем позицию в центр
        self.shape_x = WIDTH // 2
        self.shape_y = HEIGHT // 2
        self.last_shape_change = time.time()
    
    def update_auto_clicker(self):
        """Обновление автокликера"""
        if self.auto_clicker > 0 and time.time() - self.last_auto_click > 1.0:
            reward = 5 * self.click_power * self.click_multiplier
            if self.active_effect == NegativeEffect.SLOW_CLICKS:
                reward = max(1, reward // 2)
            
            self.score += reward * self.auto_clicker
            self.last_auto_click = time.time()
    
    def update_negative_effects(self):
        """Обновление негативных эффектов"""
        current_time = time.time()
        
        # Проверяем время для нового эффекта
        if current_time >= self.next_effect_time and self.state == GameState.PLAYING:
            self.active_effect = random.choice(list(NegativeEffect))
            self.effect_start_time = current_time
            self.next_effect_time = current_time + 120
            print(f"⚠️  Появился эффект: {self.active_effect}")
        
        # Проверяем длительность текущего эффекта
        if self.active_effect and current_time - self.effect_start_time > self.effect_duration:
            self.active_effect = None
            print("✅ Эффект закончился")
    
    def buy_upgrade(self, upgrade_type):
        """Покупка улучшения"""
        cost = self.upgrade_costs[upgrade_type]
        
        if self.score >= cost:
            self.score -= cost
            
            # Применяем улучшение
            if upgrade_type == "power":
                self.click_power += 1
                self.upgrade_levels["power"] += 1
                self.upgrade_costs["power"] = int(cost * 1.5)
                self.show_price_text = f"Следующее улучшение: {self.upgrade_costs['power']} VISA"
                
            elif upgrade_type == "multiplier":
                self.click_multiplier += 1
                self.upgrade_levels["multiplier"] += 1
                self.upgrade_costs["multiplier"] = int(cost * 1.8)
                self.show_price_text = f"Следующее улучшение: {self.upgrade_costs['multiplier']} VISA"
                
            elif upgrade_type == "auto":
                self.auto_clicker += 1
                self.upgrade_levels["auto"] += 1
                self.upgrade_costs["auto"] = int(cost * 1.6)
                self.show_price_text = f"Следующее улучшение: {self.upgrade_costs['auto']} VISA"
            
            self.price_timer = time.time()
            return True
        
        return False
    
    def run(self):
        """Главный игровой цикл"""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            current_time = time.time()
            
            # Обновляем снежинки в меню
            if self.state == GameState.MAIN_MENU:
                self.update_snowflakes()
            
            # Обновляем летающие буквы
            if self.state == GameState.MAXIM:
                self.update_flying_letters()
            
            # Проверяем таймер смены фигуры
            if self.state == GameState.PLAYING and current_time - self.last_shape_change > self.shape_change_interval:
                self.change_shape()
            
            # Обновляем автокликер
            self.update_auto_clicker()
            
            # Обновляем негативные эффекты
            self.update_negative_effects()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # ЛКМ
                        if self.state == GameState.MAIN_MENU:
                            for i, button in enumerate(self.menu_buttons):
                                if button.is_clicked(mouse_pos):
                                    if i == 0:
                                        self.state = GameState.PLAYING
                                        self.shape_x = WIDTH // 2
                                        self.shape_y = HEIGHT // 2
                                    elif i == 1:
                                        self.state = GameState.UPGRADES
                                    elif i == 2:
                                        self.state = GameState.INFO
                                    elif i == 3:
                                        self.state = GameState.MAXIM
                                        self.reset_maxim_screen()
                        
                        elif self.state == GameState.PLAYING:
                            if self.back_button.is_clicked(mouse_pos):
                                self.state = GameState.MAIN_MENU
                            else:
                                self.handle_shape_click(mouse_pos)
                        
                        elif self.state == GameState.UPGRADES:
                            if self.back_button.is_clicked(mouse_pos):
                                self.state = GameState.MAIN_MENU
                            elif self.upgrade_buttons[0].is_clicked(mouse_pos):
                                self.buy_upgrade("power")
                            elif self.upgrade_buttons[1].is_clicked(mouse_pos):
                                self.buy_upgrade("multiplier")
                            elif self.upgrade_buttons[2].is_clicked(mouse_pos):
                                self.buy_upgrade("auto")
                            elif self.upgrade_buttons[3].is_clicked(mouse_pos):
                                self.state = GameState.MAIN_MENU
                        
                        elif self.state in [GameState.INFO, GameState.MAXIM]:
                            if self.back_button.is_clicked(mouse_pos):
                                self.state = GameState.MAIN_MENU
            
            # Проверяем наведение на кнопки
            if self.state == GameState.MAIN_MENU:
                for button in self.menu_buttons:
                    button.check_hover(mouse_pos)
            elif self.state == GameState.UPGRADES:
                for button in self.upgrade_buttons:
                    button.check_hover(mouse_pos)
                self.back_button.check_hover(mouse_pos)
            elif self.state in [GameState.PLAYING, GameState.INFO, GameState.MAXIM]:
                self.back_button.check_hover(mouse_pos)
            
            # Отрисовка
            if self.state == GameState.MAIN_MENU:
                self.draw_main_menu()
            elif self.state == GameState.PLAYING:
                self.draw_game_screen()
            elif self.state == GameState.UPGRADES:
                self.draw_upgrades_screen()
            elif self.state == GameState.INFO:
                self.draw_info_screen()
            elif self.state == GameState.MAXIM:
                self.draw_maxim_screen()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Запуск игры
if __name__ == "__main__":
    print("=" * 50)
    print("VisaClicker - Игра запущена!")
    print("=" * 50)
    
    game = Game()
    game.run()