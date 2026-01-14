import pygame, random, ctypes, subprocess, sys, os
app_id = "yarootie.vkindex_eda.game.v1"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
pygame.init()
pygame.mixer.init()

# Размеры экрана
W = 1920
H = 1080
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
pygame.display.set_caption("ВКИндекс.Еда")
logo_img = pygame.image.load("logo.png")
pygame.display.set_icon(logo_img)
clock = pygame.time.Clock()
FPS = 60

# Звуки
fon = pygame.mixer.Sound("sounds/fon_menu.mp3")
open_menu = pygame.mixer.Sound("sounds/pop.mp3")
fon.set_volume(0.5)
open_menu.set_volume(0.5)

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
BLUE = (70, 140, 220)
DARK_GRAY = (50, 50, 50)
GREEN = (70, 200, 70)
RED = (200, 70, 70)
YELLOW = (220, 200, 70)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)

# Загрузка картинок
def load_img(name, size_x, size_y):
    img = pygame.image.load(name)
    img = pygame.transform.scale(img, (size_x, size_y))
    return img

player_img1 = load_img("character.png", 256, 256)
player_img2 = load_img("character2.png", 256, 256)
player_x = -256
player_y = H // 2
player_speed = 5
move_x = player_speed
move_y = 0
anim_frame = 0
current_img = player_img1

# Состояние меню
menu_state = "main"

# Таблица лидеров
leaderboard_file = "leaderboard.txt"
leaderboard_data = []

# Функция чтения таблицы лидеров
def load_leaderboard():
    global leaderboard_data
    leaderboard_data = []
    
    file = open(leaderboard_file, "r", encoding="utf-8")
    lines = file.readlines()
    file.close()
        
    for line in lines:
        line = line.strip()
        if line:
            parts = line.split(":")
            if len(parts) == 2:
                name = parts[0]
                score_str = parts[1]
                try:
                    score = int(score_str)
                    leaderboard_data.append([name, score])
                except:
                    pass
    n = len(leaderboard_data)
    for i in range(n):
        for j in range(0, n - i - 1):
            if leaderboard_data[j][1] < leaderboard_data[j + 1][1]:
                temp = leaderboard_data[j]
                leaderboard_data[j] = leaderboard_data[j + 1]
                leaderboard_data[j + 1] = temp

# Кнопки главного меню
btn1_text = "Играть"
btn1_x = W // 2 - 250
btn1_y = H // 2 - 225
btn1_w = 500
btn1_h = 100

btn2_text = "Помощь"
btn2_x = W // 2 - 250
btn2_y = H // 2 - 100
btn2_w = 500
btn2_h = 100

btn3_text = "Таблица лидеров"
btn3_x = W // 2 - 250
btn3_y = H // 2 + 25
btn3_w = 500
btn3_h = 100

btn4_text = "Выход"
btn4_x = W // 2 - 250
btn4_y = H // 2 + 150
btn4_w = 500
btn4_h = 100

# Кнопка назад
back_btn_text = "← Назад"
back_btn_x = 50
back_btn_y = H - 100
back_btn_w = 200
back_btn_h = 60

# Страницы помощи
page1_title = "ОСНОВЫ ИГРЫ"
page1_lines = [
    "",
    "Вы - робот-курьер ВКИндекс.Еда!",
    "Ваша задача - доставить заказ как можно дальше.",
    "",
    "УПРАВЛЕНИЕ:",
    "",
    " W / ↑  - движение вверх",
    " S / ↓  - движение вниз",
    " D / →  - ускорение вперёд",
    " P - показать пройденное расстояние",
    " ESC - выход из игры",
    "",
    "Робот автоматически едет вперёд.",
    "Вы можете ускоряться и маневрировать.",
]

page2_title = "БАТАРЕЯ И ЭНЕРГИЯ"
page2_lines = [
    "",
    "Робот работает от батареи!",
    "",
    "Батарея отображается в правом нижнем углу",
    "При движении батарея разряжается быстрее",
    "В покое разряд медленнее",
    "",
    "БОНУС ЭНЕРГИИ:",
    "",
    " Голубая иконка с белой батареей на дороге",
    " Восстанавливает +25% заряда",
    " Подберите, проехав через него",
    "",
    "Если батарея сядет - игра окончена!",
]

page3_title = "ЗДОРОВЬЕ(ХП)"
page3_lines = [
    "",
    "У вас 3 ХП.",
    "",
    "ХП отображаются рядом с батареей",
    "",
    "БОНУС ХП:",
    "",
    " Голубая иконка с молнией на дороге",
    " Восстанавливает 1 ХП",
    "",
    "Если ХП закончится - игра окончена!",
]

page4_title = "ХУЛИГАНЫ"
page4_lines = [
    "",
    "На улицах бродят хулиганы!",
    "",
    "Они идут навстречу вам",
    "Подпустите близко - нападут!",
    "",
    "КАК ОТБИТЬСЯ:",
    "",
    " Быстро нажимайте клавишу E",
    " Заполните шкалу за 5 секунд",
    " Успели = -половина ХП (лёгкий урон)",
    " Не успели = -полное ХП (тяжёлый урон)",
    "",
    "С каждым циклом хулиганов больше!",
]

page5_title = "ПЕШЕХОДНЫЙ ПЕРЕХОД"
page5_lines = [
    "",
    "Иногда вы попадаете на пешеходный перехо!",
    "",
    " Камера переключается на обзор всего перехода",
    " Машины едут вертикально вверх",
    " Столкновение с машиной = МГНОВЕННАЯ СМЕРТЬ!",
    "",
    "СВЕТОФОРЫ:",
    "",
    " Зелёный — машины стоят, можно ехать",
    " Жёлтый — приготовьтесь",
    " Красный — машины едут, ОПАСНО!",
    "",
    "Маневрируйте между машинами, или дождитесь!",
]

page6_title = "СЛОЖНОСТЬ"
page6_lines = [
    "",
    "Игра становится сложнее с каждым циклом!",
    "",
    "КАЖДЫЕ 2 ЦИКЛА:",
    "",
    " +1 хулиган (максимум 6)",
    " Меньше шанс появления бонуса энергии",
    "",
    "КАЖДЫЕ 3 ЦИКЛА:",
    "",
    " Увеличивается скорость робота",
    " Меньше шанс появления бонуса ХП",
    "",
    "КАЖДЫЕ 4 ЦИКЛА:",
    "",
    " Батарея разряжается быстрее",
    "",
]

# Все страницы помощи
all_help_titles = [
    page1_title,
    page2_title,
    page3_title,
    page4_title,
    page5_title,
    page6_title,
]
all_help_pages = [
    page1_lines,
    page2_lines,
    page3_lines,
    page4_lines,
    page5_lines,
    page6_lines,
]
current_help_page = 0
total_help_pages = 6

def reset_player():
    global player_x, player_y, move_x, move_y
    side = random.randint(0, 3)
    if side == 0:
        player_x = -256
        player_y = random.randint(0, H - 256)
        move_x = player_speed
        move_y = 0
    if side == 1:
        player_x = W
        player_y = random.randint(0, H - 256)
        move_x = -player_speed
        move_y = 0
    if side == 2:
        player_x = random.randint(0, W - 256)
        player_y = -256
        move_x = 0
        move_y = player_speed
    if side == 3:
        player_x = random.randint(0, W - 256)
        player_y = H
        move_x = 0
        move_y = -player_speed

def draw_background():
    cell = 120
    y = 0
    while y < H:
        x = 0
        while x < W:
            row = y // cell
            col = x // cell
            sum_val = row + col
            if sum_val % 2 == 0:
                color = LIGHT_GRAY
            else:
                color = GRAY
            pygame.draw.rect(screen, color, (x, y, cell, cell))
            x = x + cell
        y = y + cell

def draw_overlay():
    overlay = pygame.Surface((W, H))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(150)
    screen.blit(overlay, (0, 0))

def draw_main_menu():
    draw_overlay()

    title_font = pygame.font.Font("font.otf", 50)
    title = title_font.render("ВКИндекс.Еда", False, WHITE)
    title_x = W // 2 - title.get_width() // 2
    screen.blit(title, (title_x, 100))

    # Подзаголовок
    sub_font = pygame.font.Font("font.otf", 20)
    subtitle = sub_font.render("Симулятор робота-курьера", False, LIGHT_GRAY)
    subtitle_x = W // 2 - subtitle.get_width() // 2
    screen.blit(subtitle, (subtitle_x, 200))

    # Кнопки
    font = pygame.font.Font("font.otf", 25)
    mx, my = pygame.mouse.get_pos()

    # Кнопка 1 - Играть
    hover1 = False
    if mx > btn1_x and mx < btn1_x + btn1_w:
        if my > btn1_y and my < btn1_y + btn1_h:
            hover1 = True

    if hover1:
        pygame.draw.rect(screen, BLUE, (btn1_x, btn1_y, btn1_w, btn1_h), 0, 10)
    else:
        pygame.draw.rect(screen, DARK_GRAY, (btn1_x, btn1_y, btn1_w, btn1_h), 0, 10)
    pygame.draw.rect(screen, BLUE, (btn1_x, btn1_y, btn1_w, btn1_h), 3, 10)
    text1 = font.render(btn1_text, False, WHITE)
    text1_x = btn1_x + btn1_w // 2 - text1.get_width() // 2
    text1_y = btn1_y + btn1_h // 2 - text1.get_height() // 2
    screen.blit(text1, (text1_x, text1_y))

    # Кнопка 2 - Помощь
    hover2 = False
    if mx > btn2_x and mx < btn2_x + btn2_w:
        if my > btn2_y and my < btn2_y + btn2_h:
            hover2 = True

    if hover2:
        pygame.draw.rect(screen, BLUE, (btn2_x, btn2_y, btn2_w, btn2_h), 0, 10)
    else:
        pygame.draw.rect(screen, DARK_GRAY, (btn2_x, btn2_y, btn2_w, btn2_h), 0, 10)
    pygame.draw.rect(screen, BLUE, (btn2_x, btn2_y, btn2_w, btn2_h), 3, 10)
    text2 = font.render(btn2_text, False, WHITE)
    text2_x = btn2_x + btn2_w // 2 - text2.get_width() // 2
    text2_y = btn2_y + btn2_h // 2 - text2.get_height() // 2
    screen.blit(text2, (text2_x, text2_y))

    # Кнопка 3 - Таблица лидеров
    hover3 = False
    if mx > btn3_x and mx < btn3_x + btn3_w:
        if my > btn3_y and my < btn3_y + btn3_h:
            hover3 = True

    if hover3:
        pygame.draw.rect(screen, BLUE, (btn3_x, btn3_y, btn3_w, btn3_h), 0, 10)
    else:
        pygame.draw.rect(screen, DARK_GRAY, (btn3_x, btn3_y, btn3_w, btn3_h), 0, 10)
    pygame.draw.rect(screen, BLUE, (btn3_x, btn3_y, btn3_w, btn3_h), 3, 10)
    text3 = font.render(btn3_text, False, WHITE)
    text3_x = btn3_x + btn3_w // 2 - text3.get_width() // 2
    text3_y = btn3_y + btn3_h // 2 - text3.get_height() // 2
    screen.blit(text3, (text3_x, text3_y))

    # Кнопка 4 - Выход
    hover4 = False
    if mx > btn4_x and mx < btn4_x + btn4_w:
        if my > btn4_y and my < btn4_y + btn4_h:
            hover4 = True
    if hover4:
        pygame.draw.rect(screen, BLUE, (btn4_x, btn4_y, btn4_w, btn4_h), 0, 10)
    else:
        pygame.draw.rect(screen, DARK_GRAY, (btn4_x, btn4_y, btn4_w, btn4_h), 0, 10)
    pygame.draw.rect(screen, BLUE, (btn4_x, btn4_y, btn4_w, btn4_h), 3, 10)
    text4 = font.render(btn4_text, False, WHITE)
    text4_x = btn4_x + btn4_w // 2 - text4.get_width() // 2
    text4_y = btn4_y + btn4_h // 2 - text4.get_height() // 2
    screen.blit(text4, (text4_x, text4_y))

def draw_help_menu():
    draw_overlay()

    # Панель
    panel_w = 1200
    panel_h = 800
    panel_x = W // 2 - panel_w // 2
    panel_y = H // 2 - panel_h // 2

    pygame.draw.rect(screen, DARK_GRAY, (panel_x, panel_y, panel_w, panel_h), 0, 15)
    pygame.draw.rect(screen, BLUE, (panel_x, panel_y, panel_w, panel_h), 3, 15)

    # Заголовок страницы
    title_text = all_help_titles[current_help_page]
    title_font = pygame.font.Font("font.otf", 35)
    title = title_font.render(title_text, False, WHITE)
    title_x = W // 2 - title.get_width() // 2
    screen.blit(title, (title_x, panel_y + 30))

    # Контент
    content_font = pygame.font.Font("font.otf", 18)
    lines = all_help_pages[current_help_page]
    y_offset = panel_y + 100
    for line in lines:
        color = WHITE
        text = content_font.render(line, False, color)
        screen.blit(text, (panel_x + 50, y_offset))
        y_offset = y_offset + 35

    # Навигация страниц
    nav_font = pygame.font.Font("font.otf", 20)
    mx, my = pygame.mouse.get_pos()

    # Кнопка "Назад" (страница)
    if current_help_page > 0:
        prev_x = panel_x
        prev_y = panel_y + panel_h - 60
        prev_w = 200
        prev_h = 50

        hover_prev = False
        if mx > prev_x and mx < prev_x + prev_w:
            if my > prev_y and my < prev_y + prev_h:
                hover_prev = True

        if hover_prev:
            pygame.draw.rect(screen, BLUE, (prev_x, prev_y, prev_w, prev_h), 0, 5)
        pygame.draw.rect(screen, BLUE, (prev_x, prev_y, prev_w, prev_h), 2, 5)

        prev_text = nav_font.render("< Назад", False, WHITE)
        prev_text_x = prev_x + prev_w // 2 - prev_text.get_width() // 2
        prev_text_y = prev_y + prev_h // 2 - prev_text.get_height() // 2
        screen.blit(prev_text, (prev_text_x, prev_text_y))

    # Кнопка "Далее" (страница)
    if current_help_page < total_help_pages - 1:
        next_x = panel_x + panel_w - 200
        next_y = panel_y + panel_h - 60
        next_w = 200
        next_h = 50

        hover_next = False
        if mx > next_x and mx < next_x + next_w:
            if my > next_y and my < next_y + next_h:
                hover_next = True

        if hover_next:
            pygame.draw.rect(screen, BLUE, (next_x, next_y, next_w, next_h), 0, 5)
        pygame.draw.rect(screen, BLUE, (next_x, next_y, next_w, next_h), 2, 5)

        next_text = nav_font.render("Далее >", False, WHITE)
        next_text_x = next_x + next_w // 2 - next_text.get_width() // 2
        next_text_y = next_y + next_h // 2 - next_text.get_height() // 2
        screen.blit(next_text, (next_text_x, next_text_y))

    # Индикатор страниц
    page_num = current_help_page + 1
    page_str = "Страница " + str(page_num) + " / " + str(total_help_pages)
    page_text = nav_font.render(page_str, False, LIGHT_GRAY)
    page_text_x = W // 2 - page_text.get_width() // 2
    screen.blit(page_text, (page_text_x, panel_y + panel_h - 50))

    # Кнопка "В меню"
    font = pygame.font.Font("font.otf", 20)
    hover_back = False
    if mx > back_btn_x and mx < back_btn_x + back_btn_w:
        if my > back_btn_y and my < back_btn_y + back_btn_h:
            hover_back = True

    if hover_back:
        pygame.draw.rect(screen, BLUE, (back_btn_x, back_btn_y, back_btn_w, back_btn_h), 0, 10)
    else:
        pygame.draw.rect(screen, DARK_GRAY, (back_btn_x, back_btn_y, back_btn_w, back_btn_h), 0, 10)
    pygame.draw.rect(screen, BLUE, (back_btn_x, back_btn_y, back_btn_w, back_btn_h), 3, 10)
    text = font.render(back_btn_text, False, WHITE)
    text_x = back_btn_x + back_btn_w // 2 - text.get_width() // 2
    text_y = back_btn_y + back_btn_h // 2 - text.get_height() // 2
    screen.blit(text, (text_x, text_y))

def draw_leaderboard():
    draw_overlay()

    # Панель
    panel_w = 900
    panel_h = 800
    panel_x = W // 2 - panel_w // 2
    panel_y = H // 2 - panel_h // 2

    pygame.draw.rect(screen, DARK_GRAY, (panel_x, panel_y, panel_w, panel_h), 0, 15)
    pygame.draw.rect(screen, BLUE, (panel_x, panel_y, panel_w, panel_h), 3, 15)

    # Заголовок
    title_font = pygame.font.Font("font.otf", 35)
    title = title_font.render("ТАБЛИЦА ЛИДЕРОВ", False, WHITE)
    title_x = W // 2 - title.get_width() // 2
    screen.blit(title, (title_x, panel_y + 30))
    
    # Заголовки колонок
    header_font = pygame.font.Font("font.otf", 22)
    
    pos_header = header_font.render("Место", False, YELLOW)
    name_header = header_font.render("Имя", False, YELLOW)
    score_header = header_font.render("Результат", False, YELLOW)
    
    header_y = panel_y + 100
    screen.blit(pos_header, (panel_x + 50, header_y))
    screen.blit(name_header, (panel_x + 200, header_y))
    screen.blit(score_header, (panel_x + 600, header_y))
    
    # Линия под заголовками
    pygame.draw.line(screen, YELLOW, (panel_x + 40, header_y + 35), (panel_x + panel_w - 40, header_y + 35), 3)
    
    # Отображение результатов
    content_font = pygame.font.Font("font.otf", 20)
    y_offset = header_y + 60
    max_show = 15
    if len(leaderboard_data) < max_show:
        max_show = len(leaderboard_data)
    
    for i in range(max_show):
        place = i + 1
        if place == 1:
            place_color = GOLD
            name_color = GOLD
        elif place == 2:
            place_color = SILVER
            name_color = SILVER
        elif place == 3:
            place_color = BRONZE
            name_color = BRONZE
        else:
            place_color = WHITE
            name_color = LIGHT_GRAY
        
        # Место
        place_text = content_font.render(str(place), False, place_color)
        screen.blit(place_text, (panel_x + 70, y_offset))
        
        # Имя
        name = leaderboard_data[i][0]
        if len(name) > 16:
            name = name[:13] + "..."
        name_text = content_font.render(name, False, name_color)
        screen.blit(name_text, (panel_x + 200, y_offset))
        
        # Результат
        score = leaderboard_data[i][1]
        score_text = content_font.render(str(score), False, WHITE)
        screen.blit(score_text, (panel_x + 650, y_offset))
        
        y_offset = y_offset + 35
    
    # Если нет результатов
    if len(leaderboard_data) == 0:
        no_data_text = content_font.render("Пусто... будете первыми?", False, LIGHT_GRAY)
        no_data_x = W // 2 - no_data_text.get_width() // 2
        screen.blit(no_data_text, (no_data_x, H // 2))

    # Кнопка назад
    font = pygame.font.Font("font.otf", 20)
    mx, my = pygame.mouse.get_pos()
    hover_back = False
    if mx > back_btn_x and mx < back_btn_x + back_btn_w:
        if my > back_btn_y and my < back_btn_y + back_btn_h:
            hover_back = True

    if hover_back:
        pygame.draw.rect(screen, BLUE, (back_btn_x, back_btn_y, back_btn_w, back_btn_h), 0, 10)
    else:
        pygame.draw.rect(screen, DARK_GRAY, (back_btn_x, back_btn_y, back_btn_w, back_btn_h), 0, 10)
    pygame.draw.rect(screen, BLUE, (back_btn_x, back_btn_y, back_btn_w, back_btn_h), 3, 10)
    text = font.render(back_btn_text, False, WHITE)
    text_x = back_btn_x + back_btn_w // 2 - text.get_width() // 2
    text_y = back_btn_y + back_btn_h // 2 - text.get_height() // 2
    screen.blit(text, (text_x, text_y))

def start_game():
    pygame.quit()
    python_exe = sys.executable
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "main.py")
    subprocess.Popen([python_exe, script_path])
    sys.exit()

load_leaderboard()
reset_player()
fon.play(-1)
running = True
while running:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if menu_state == "main":
                    running = False
                else:
                    menu_state = "main"
                    current_help_page = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if menu_state == "main":
                # Кнопка "Играть"
                if mx > btn1_x and mx < btn1_x + btn1_w:
                    if my > btn1_y and my < btn1_y + btn1_h:
                        start_game()

                # Кнопка "Помощь"
                if mx > btn2_x and mx < btn2_x + btn2_w:
                    if my > btn2_y and my < btn2_y + btn2_h:
                        menu_state = "help"
                        open_menu.play()
                        current_help_page = 0

                # Кнопка "Таблица лидеров"
                if mx > btn3_x and mx < btn3_x + btn3_w:
                    if my > btn3_y and my < btn3_y + btn3_h:
                        menu_state = "leaderboard"
                        open_menu.play()
                        load_leaderboard()

                # Кнопка "Выход"
                if mx > btn4_x and mx < btn4_x + btn4_w:
                    if my > btn4_y and my < btn4_y + btn4_h:
                        open_menu.play()
                        running = False

            if menu_state == "help":
                # Кнопка назад в меню
                if mx > back_btn_x and mx < back_btn_x + back_btn_w:
                    if my > back_btn_y and my < back_btn_y + back_btn_h:
                        open_menu.play()
                        menu_state = "main"
                        current_help_page = 0

                # Навигация страниц
                panel_w = 1200
                panel_h = 800
                panel_x = W // 2 - panel_w // 2
                panel_y = H // 2 - panel_h // 2

                prev_x = panel_x + 50
                prev_y = panel_y + panel_h - 60
                prev_w = 150
                prev_h = 40

                next_x = panel_x + panel_w - 200
                next_y = panel_y + panel_h - 60
                next_w = 150
                next_h = 40

                if mx > prev_x and mx < prev_x + prev_w:
                    if my > prev_y and my < prev_y + prev_h:
                        if current_help_page > 0:
                            current_help_page = current_help_page - 1

                if mx > next_x and mx < next_x + next_w:
                    if my > next_y and my < next_y + next_h:
                        if current_help_page < total_help_pages - 1:
                            current_help_page = current_help_page + 1

            if menu_state == "leaderboard":
                if mx > back_btn_x and mx < back_btn_x + back_btn_w:
                    if my > back_btn_y and my < back_btn_y + back_btn_h:
                        menu_state = "main"
                        open_menu.play()

    # Движение персонажа
    player_x = player_x + move_x
    player_y = player_y + move_y

    # Анимация
    anim_frame = anim_frame + 1
    if anim_frame > 40:
        anim_frame = 0

    if anim_frame < 20:
        current_img = player_img1
    else:
        current_img = player_img2

    # Проверка выхода за экран
    out_of_screen = False
    if move_x > 0:
        if player_x > W:
            out_of_screen = True
    if move_x < 0:
        if player_x < -256:
            out_of_screen = True
    if move_y > 0:
        if player_y > H:
            out_of_screen = True
    if move_y < 0:
        if player_y < -256:
            out_of_screen = True

    if out_of_screen:
        reset_player()

    # Отрисовка
    draw_background()
    screen.blit(current_img, (player_x, player_y))

    if menu_state == "main":
        draw_main_menu()
    if menu_state == "help":
        draw_help_menu()
    if menu_state == "leaderboard":
        draw_leaderboard()

    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()