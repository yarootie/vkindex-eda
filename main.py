import pygame, random, ctypes, os
app_id = "yarootie.vkindex_eda.game.v1"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
pygame.init()
pygame.mixer.init()

# Состояние игры
game_state = "playing"
player_name = ""
name_input_active = False
max_name_length = 20
pygame.display.set_caption("ВКИндекс.Еда")
logo_img = pygame.image.load("logo.png")
pygame.display.set_icon(logo_img)
clock = pygame.time.Clock()
FPS = 60

menu_font = pygame.font.Font("font.otf", 25)
menu_font_big = pygame.font.Font("font.otf", 35)

# Экран
screen_width = 1920
screen_height = 1080
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

# Звуки
sound_bonus = pygame.mixer.Sound("sounds/bonus.mp3")
sound_hit = pygame.mixer.Sound("sounds/hit.mp3")
sound_game_over = pygame.mixer.Sound("sounds/lose.mp3")
sound_boom = pygame.mixer.Sound("sounds/boom.mp3")
fon = pygame.mixer.Sound("sounds/fon.mp3")
hit_sound_timer = 0
hit_sound_cooldown = 0.30

# Настройка громкости
sound_boom.set_volume(1)
sound_bonus.set_volume(1)
fon.set_volume(0.5)
sound_bonus.set_volume(1)
sound_hit.set_volume(1)
sound_game_over.set_volume(1)

# Загрузка картинки
def load_img(path, size_x, size_y):
    img = pygame.image.load(path)
    img = pygame.transform.scale(img, (size_x, size_y))
    return img

# Игрок
player_img1 = load_img("character.png", 64, 64)
player_img2 = load_img("character2.png", 64, 64)
anim_frame = 0
player_x = screen_width // 2 - 64
player_y = screen_height - 256
player_speed_min = 8
player_speed = 10
current_img = player_img1

# Взрыв
boom_frames = [
    load_img("boom/boom1.png", 128, 128),
    load_img("boom/boom2.png", 128, 128),
    load_img("boom/boom3.png", 128, 128),
    load_img("boom/boom4.png", 128, 128),
    load_img("boom/boom5.png", 128, 128),
    load_img("boom/boom6.png", 128, 128),
    load_img("boom/boom7.png", 128, 128),
    load_img("boom/boom8.png", 128, 128),
    load_img("boom/boom9.png", 128, 128),
    load_img("boom/boom10.png", 128, 128),
    load_img("boom/boom11.png", 128, 128),
    load_img("boom/boom12.png", 128, 128),
]
boom_active = False
boom_frame_index = 0
boom_frame_timer = 0
boom_frame_delay = 0.1

# Хулиганы
hyligan1 = load_img("hyligan1.png", 128, 128)
hyligan2 = load_img("hyligan2.png", 128, 128)
hyligan_nap = load_img("hyligan_nap.png", 128, 128)
HYLIGAN_SIZE_W = 100
HYLIGAN_SIZE_H = 100
hyligans = []
hyligan_count = 1
hyligan_speed_base = 5
attacked_by_hyligan = False
e_press_count = 0
e_press_needed = 15
current_attacker = None
attack_timer = 0
attack_time_limit = 5

# Расстояние
total_distance_pixels = 0
last_player_x = screen_width // 2 - 64

# Сложность
cycles_completed = 0
bonus_spawn_min = 1024
bonus_spawn_max = 1920 * 5
hp_bonus_spawn_min = 1500
hp_bonus_spawn_max = 1920 * 4

# Шанс спавна бонусов
bonus_spawn_chance = 100
hp_bonus_spawn_chance = 100

def spawn_hyligans():
    hyligans.clear()
    for i in range(hyligan_count):
        hx = random.randint(player_x + 1920, player_x + 1920 * 4)
        hy = random.randint(650, screen_height - 400)
        hyligans.append(
            {
                "x": hx,
                "y": hy,
                "speed": random.randint(4, 7),
                "state": "walk",
                "anim_frame": 0,
                "current_img": hyligan1,
                "rect": pygame.Rect(hx, hy, HYLIGAN_SIZE_W, HYLIGAN_SIZE_H),
            }
        )

# Машины(горизонтальные)
bg4_active = False
car_assets = {
    "white": load_img("white_car.png", 300, 150),
}
CAR_SPEED = 20
CAR_Y = [900, 780]
CAR_SIZE_W = 300
CAR_SIZE_H = 150
MAX_CARS = 3
MIN_CAR_DISTANCE = 450
cars_list = []
spawn_timer = 0
next_spawn_time = random.uniform(0.7, 1.8)

# Машины(вертикальные)
zad_img = load_img("zad.png", 250, 180)
ZAD_SIZE_W = 120
ZAD_SIZE_H = 150
zad_lanes_x = [100, 350, 1350, 1600]
CARS_PER_LANE = 3
START_Y_BASE = 2600
END_Y = 600
STOP_LINE_Y = 920
SAFE_DISTANCE = 220
zad_cars = []

def init_zad_cars():
    zad_cars.clear()
    for lane_x in zad_lanes_x:
        for i in range(CARS_PER_LANE):
            start_y = START_Y_BASE + (i * 300) + random.randint(0, 200)
            speed = random.randint(15, 22)
            zad_cars.append(
                {
                    "x": lane_x,
                    "y": start_y,
                    "speed": speed,
                    "rect": pygame.Rect(lane_x, start_y, ZAD_SIZE_W, ZAD_SIZE_H),
                }
            )
init_zad_cars()

# Уведомления
notif_font = pygame.font.Font("font.otf", 12)
notif_x = -1000
notif_y = 20
notif_w = 0
notif_h = 0
notif_text = ""
notif_timer = 0

def notify(text, w, h):
    global notif_text, notif_timer, notif_w, notif_h, notif_x
    notif_text = text
    notif_w = w
    notif_h = h
    notif_x = -w
    notif_timer = 300

def draw_notify():
    global notif_x, notif_timer
    if notif_timer > 0:
        notif_timer -= 1
        if notif_x < 20:
            notif_x += 15
    else:
        if notif_x > -notif_w:
            notif_x -= 15

    if notif_x > -notif_w:
        pygame.draw.rect(screen, (50, 50, 50), (notif_x, notif_y, notif_w, notif_h), border_radius=20)
        pygame.draw.rect(screen, (70, 140, 220), (notif_x, notif_y, notif_w, notif_h), width=3, border_radius=20)
        text_img = notif_font.render(notif_text, False, (255, 255, 255))
        text_x = notif_x + (notif_w // 2) - (text_img.get_width() // 2)
        text_y = notif_y + (notif_h // 2) - (text_img.get_height() // 2)
        screen.blit(text_img, [text_x, text_y])


# Батарея
battery = 100
battery_full = 100
power_draw_move = 1
power_draw_idle = 0.25
battery_images = {
    "full": load_img("full.png", 128, 128),
    "80": load_img("2full.png", 128, 128),
    "60": load_img("1full.png", 128, 128),
    "20": load_img("none.png", 128, 128),
    "none": load_img("none.png", 128, 128),
}

# ХП
hp = 300
hp_full = 300
hp_images = {
    "full": load_img("hp.png", 64, 64),
    "50": load_img("hp2.png", 64, 64),
    "none": load_img("hp_none.png", 64, 64),
}

# Светофоры
sf_w = 60
sf_h = 140
sf_images = {
    "green": load_img("traffic_light_green.png", sf_w, sf_h),
    "yellow": load_img("traffic_light_yellow.png", sf_w, sf_h),
    "red": load_img("traffic_light_red.png", sf_w, sf_h),
    "none": load_img("traffic_light_none.png", sf_w, sf_h),
}
sf_coords = [(21, 718), (598, 718), (1268, 718), (1839, 718)]
sf_timer = 0
sf_state = "green"

# Мир
bg1 = load_img("bg1.jpg", 1920, 1080)
bg2 = load_img("bg2.jpg", 1920, 1080)
bg3 = load_img("bg3.jpg", 1920, 1080)
bg4 = load_img("bg4.jpg", 1920, 1080)
bg5 = load_img("bg5.png", 1920, 1080)

backgrounds = [bg1, bg2, bg3, bg4, bg5]

# Фон пешеходного перехода
bg44 = load_img("bg44.png", 1920, 1080)
bg44_offset_y = 646

# Бонус энергии
bonus = load_img("bonus.png", 32, 32)
bonus_value = 25
bonus_x = random.randint(1024, 1920 * 5)
bonus_y = random.randint(666, screen_height - 295)
bonus_collected = False
bonus_exists = True

# Бонус ХП
hp_bonus = load_img("hp.png", 32, 32)
hp_bonus_value = 100
hp_bonus_x = random.randint(1500, 1920 * 4)
hp_bonus_y = random.randint(666, screen_height - 295)
hp_bonus_collected = False
hp_bonus_exists = True

# Причина проигрыша
lose_reason = ""

def make_world():
    world_list = []
    start_bg = bg1
    end_bg = bg1
    middle_bgs = [bg2, bg3, bg5]
    middle_count = random.randint(4, 6)
    middle = []

    for i in range(middle_count - 1):
        random_bg = random.choice(middle_bgs)
        middle.append(random_bg)

    insert_position = random.randint(0, len(middle))
    middle.insert(insert_position, bg4)
    imgs = [start_bg] + middle + [end_bg]

    x = 0
    for bg in imgs:
        r = bg.get_rect()
        r.x = x
        r.y = 0
        world_list.append((bg, r))
        x = x + 1920

    return world_list

world = make_world()
camera_x = 0
camera_y = 0
can_ride = True

# Функция рестарта
def go_to_start():
    global world, player_x, camera_x, camera_y, bonus_x, bonus_y, bonus_collected
    global sf_timer, cycles_completed, hyligan_count
    global bonus_spawn_min, bonus_spawn_max, attacked_by_hyligan, e_press_count
    global current_attacker, last_player_x, attack_timer
    global hp_bonus_x, hp_bonus_y, hp_bonus_collected, hp_bonus_spawn_min, hp_bonus_spawn_max
    global power_draw_move, power_draw_idle, player_speed_min, player_speed
    global bonus_spawn_chance, hp_bonus_spawn_chance, bonus_exists, hp_bonus_exists

    cycles_completed += 1
    if cycles_completed % 2 == 0:
        hyligan_count = hyligan_count + 1
        if hyligan_count > 6:
            hyligan_count = 6

    if cycles_completed % 2 == 0:
        bonus_spawn_chance = bonus_spawn_chance - 15
        if bonus_spawn_chance < 20:
            bonus_spawn_chance = 20

    if cycles_completed % 3 == 0:
        hp_bonus_spawn_chance = hp_bonus_spawn_chance - 20
        if hp_bonus_spawn_chance < 15:
            hp_bonus_spawn_chance = 15

    if cycles_completed % 4 == 0:
        power_draw_move = power_draw_move + 0.2
        power_draw_idle = power_draw_idle + 0.05

    if cycles_completed % 3 == 0:
        player_speed_min = player_speed_min + 1
        player_speed = player_speed + 1

    world = make_world()
    player_x = screen_width // 2 - 64
    last_player_x = player_x
    camera_x = 0
    camera_y = 0

    roll_bonus = random.randint(1, 100)
    if roll_bonus <= bonus_spawn_chance:
        bonus_exists = True
        bonus_collected = False
        bonus_x = random.randint(bonus_spawn_min, bonus_spawn_max)
        bonus_y = random.randint(666, screen_height - 295)
    else:
        bonus_exists = False
        bonus_collected = True

    roll_hp_bonus = random.randint(1, 100)
    if roll_hp_bonus <= hp_bonus_spawn_chance:
        hp_bonus_exists = True
        hp_bonus_collected = False
        hp_bonus_x = random.randint(hp_bonus_spawn_min, hp_bonus_spawn_max)
        hp_bonus_y = random.randint(666, screen_height - 295)
    else:
        hp_bonus_exists = False
        hp_bonus_collected = True

    sf_timer = 0
    attacked_by_hyligan = False
    e_press_count = 0
    current_attacker = None
    attack_timer = 0
    init_zad_cars()
    spawn_hyligans()
spawn_hyligans()

running = True
fon.play(-1)
while running:
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_e and attacked_by_hyligan:
                e_press_count += 1
                if e_press_count >= e_press_needed:
                    if current_attacker:
                        current_attacker["state"] = "flee"
                    attacked_by_hyligan = False
                    current_attacker = None
                    can_ride = True
                    hp = hp - 51
                    if hp < 0:
                        hp = 0
                    attack_timer = 0
                    notify("Хулиган отпугнут!", 300, 60)
                    sound_bonus.play()
            if event.key == pygame.K_p:
                distance_meters = total_distance_pixels / 1920 * 43
                notify(f"Пройдено: {int(distance_meters)} м", 280, 60)

            # Ввод имени
            if game_state == "game_over":
                if name_input_active:
                    if event.key == pygame.K_RETURN:
                        if len(player_name) >= 3:
                            distance_meters = int(total_distance_pixels / 1920 * 43)
                            file = open("leaderboard.txt", "a", encoding="utf-8")
                            file.write(player_name + ":" + str(distance_meters) + "\n")
                            file.close()
                            pygame.quit()
                            os.system("python index.py")
                            running = False
                        else:
                            notify("Слишком короткий NickName", 400, 60)
                    elif event.key == pygame.K_BACKSPACE:
                        if len(player_name) > 0:
                            player_name = player_name[:-1]
                    else:
                        if len(player_name) < max_name_length:
                            key_name = pygame.key.name(event.key)
                            if len(key_name) == 1:
                                player_name = player_name + key_name

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "game_over":
                mx, my = pygame.mouse.get_pos()
                panel_h = 700
                panel_y = screen_height // 2 - panel_h // 2
                input_box_y = panel_y + 350 + 50
                input_box_w = 800
                input_box_h = 60
                input_box_x = screen_width // 2 - input_box_w // 2

                if mx > input_box_x and mx < input_box_x + input_box_w:
                    if my > input_box_y and my < input_box_y + input_box_h:
                        name_input_active = True
                else:
                    name_input_active = False

    moving = False
    keys = pygame.key.get_pressed()
    if (bg4_active == False and can_ride and not attacked_by_hyligan and game_state == "playing"):
        player_x += player_speed_min

    if can_ride and battery > 0 and not attacked_by_hyligan and game_state == "playing":
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            moving = True
            player_x += player_speed

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_y -= player_speed
            moving = True

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_y += player_speed
            moving = True

    # Таймер атаки хулигана
    if attacked_by_hyligan:
        attack_timer = attack_timer + dt
        if attack_timer >= attack_time_limit:
            if current_attacker:
                current_attacker["state"] = "flee"
            attacked_by_hyligan = False
            current_attacker = None
            can_ride = True
            hp = hp - 100
            if hp < 0:
                hp = 0
            attack_timer = 0
            notify("Не успел отбиться!", 290, 60)

    # Обновление расстояния
    if player_x > last_player_x:
        total_distance_pixels += player_x - last_player_x
    last_player_x = player_x

    world_width = len(world) * 1920
    if player_x + 64 > world_width - 1920 / 2:
        go_to_start()

    # Коллизии игрока
    pr1 = pygame.Rect(player_x + 20, player_y, 12, 20)
    pr2 = pygame.Rect(player_x + 6, player_y + 20, 48, 44)

    # Столкновение с бонусом энергии
    br = pygame.Rect(bonus_x, bonus_y, 32, 32)
    if ((pr1.colliderect(br) or pr2.colliderect(br)) and not bonus_collected and bonus_exists):
        battery = battery + bonus_value
        if battery > battery_full:
            battery = battery_full
        bonus_collected = True
        notify("Бонус энергии +25%", 300, 60)
        sound_bonus.play()

    # Столкновение с бонусом ХП
    hp_br = pygame.Rect(hp_bonus_x, hp_bonus_y, 32, 32)
    if ((pr1.colliderect(hp_br) or pr2.colliderect(hp_br)) and not hp_bonus_collected and hp_bonus_exists):
        hp = hp + hp_bonus_value
        if hp > hp_full:
            hp = hp_full
        hp_bonus_collected = True
        notify("Бонус ХП +100", 250, 60)
        sound_bonus.play()

    if hit_sound_timer > 0:
        hit_sound_timer -= dt

    # Логика хулиганов
    if not bg4_active:
        for hyligan in hyligans:
            if hyligan["state"] == "walk":
                hyligan["x"] -= hyligan["speed"]
                hyligan["anim_frame"] += 1
                if hyligan["anim_frame"] > 40:
                    hyligan["anim_frame"] = 0
                if hyligan["anim_frame"] < 20:
                    hyligan["current_img"] = hyligan1
                else:
                    hyligan["current_img"] = hyligan2

            elif hyligan["state"] == "attack":
                hyligan["anim_frame"] += 1
                if hyligan["anim_frame"] > 15:
                    hyligan["anim_frame"] = 0
                if hyligan["anim_frame"] < 8:
                    hyligan["current_img"] = hyligan1
                else:
                    hyligan["current_img"] = hyligan_nap

                # Звук
                if hit_sound_timer <= 0:
                    sound_hit.play()
                    hit_sound_timer = hit_sound_cooldown

            elif hyligan["state"] == "flee":
                hyligan["x"] -= hyligan["speed"] * 3
                hyligan["anim_frame"] += 1
                if hyligan["anim_frame"] > 20:
                    hyligan["anim_frame"] = 0
                if hyligan["anim_frame"] < 10:
                    hyligan["current_img"] = hyligan1
                else:
                    hyligan["current_img"] = hyligan2

            hyligan["rect"] = pygame.Rect(hyligan["x"], hyligan["y"], HYLIGAN_SIZE_W, HYLIGAN_SIZE_H)

            # Столкновение с хулиганом
            if hyligan["state"] == "walk" and not attacked_by_hyligan:
                if pr1.colliderect(hyligan["rect"]) or pr2.colliderect(hyligan["rect"]):
                    hyligan["state"] = "attack"
                    attacked_by_hyligan = True
                    current_attacker = hyligan
                    can_ride = False
                    e_press_count = 0
                    attack_timer = 0
                    notify("Хулиган напал! Нажимайте E, чтоб отбиться!", 620, 60)

            if hyligan["x"] < player_x - 1920:
                hyligan["x"] = random.randint(player_x + 1920, player_x + 1920 * 3)
                hyligan["y"] = random.randint(666, screen_height - 295)
                hyligan["state"] = "walk"
                hyligan["speed"] = random.randint(4, 7)

    # Логика машин
    if bg4_active == False:
        spawn_timer += dt
        if spawn_timer >= next_spawn_time and len(cars_list) < MAX_CARS:
            img = car_assets["white"]
            spawn_y = random.choice(CAR_Y)
            spawn_x = player_x + screen_width + random.randint(100, 500)

            rect = pygame.Rect(spawn_x, spawn_y, CAR_SIZE_W, CAR_SIZE_H)
            cars_list.append({"rect": rect, "img": img})

            spawn_timer = 0
            next_spawn_time = random.uniform(0.7, 2.0)

        for car in cars_list:
            car["rect"].x -= CAR_SPEED
            if (car["rect"].x < player_x - screen_width or car["rect"].x > player_x + 4000):
                new_y = random.choice(CAR_Y)
                new_x = player_x + screen_width + random.randint(800, 1200)
                car["rect"].x = new_x
                car["rect"].y = new_y

    else:
        for car in cars_list:
            car["rect"].x = 30000

        for car in zad_cars:
            should_move = True

            if sf_state != "red":
                if car["y"] <= STOP_LINE_Y + 20:
                    car["y"] = STOP_LINE_Y
                    should_move = False

            for other in zad_cars:
                if other["x"] == car["x"]:
                    if other["y"] < car["y"]:
                        dist = car["y"] - other["y"]
                        if dist < SAFE_DISTANCE:
                            should_move = False

            if should_move == True:
                car["y"] -= car["speed"]
            else:
                car["y"] = car["y"]

            if car["y"] < END_Y:
                car["y"] = START_Y_BASE + random.randint(100, 600)
                car["speed"] = random.randint(15, 22)

            bg4_rect_x = 0
            for bg, rect in world:
                if bg == backgrounds[3]:
                    bg4_rect_x = rect.x
                    break

            car["rect"] = pygame.Rect(bg4_rect_x + car["x"], car["y"], ZAD_SIZE_W, ZAD_SIZE_H)

            # Столкновение с вертикальными машинами
            if game_state != "game_over":
                if pr1.colliderect(car["rect"]) or pr2.colliderect(car["rect"]):
                    if not boom_active:
                        boom_active = True
                        boom_x = player_x
                        boom_y = player_y
                        boom_timer = 0
                        hp = 0
                        lose_reason = "Вас сбила машина"
                        sound_boom.play()

    # Обновление взрыва
    if boom_active:
        boom_frame_timer += dt
        if boom_frame_timer >= boom_frame_delay:
            boom_frame_timer = 0
            boom_frame_index += 1
            if boom_frame_index >= len(boom_frames):
                boom_active = False
                boom_frame_index = 0

    if can_ride and not attacked_by_hyligan:
        if moving:
            anim_frame += 1
            if anim_frame > 40:
                anim_frame = 0
            if anim_frame < 20:
                current_img = player_img1
            else:
                current_img = player_img2
        else:
            anim_frame += 1
            if anim_frame > 80:
                anim_frame = 0
            if anim_frame < 40:
                current_img = player_img1
            else:
                current_img = player_img2

    # Батарея
    if not attacked_by_hyligan:
        if moving:
            battery -= power_draw_move * dt
        else:
            battery -= power_draw_idle * dt
    if battery < 0:
        battery = 0
    if battery > battery_full:
        battery = battery_full

    # Статус батареи
    if battery > 80:
        battery_img = battery_images["full"]
    elif battery > 60:
        battery_img = battery_images["80"]
    elif battery > 20:
        battery_img = battery_images["60"]
    elif battery > 0:
        battery_img = battery_images["20"]
    else:
        battery_img = battery_images["none"]
        can_ride = False
        if game_state == "playing":
            lose_reason = "Батарея разрядилась"
            game_state = "game_over"
            name_input_active = True
            sound_game_over.play()

    if hp >= 250:
        hp_img = hp_images["full"]
    elif hp > 200:
        hp_img = hp_images["50"]
    else:
        hp_img = hp_images["none"]

    if hp >= 150:
        hp_img2 = hp_images["full"]
    elif hp > 100:
        hp_img2 = hp_images["50"]
    else:
        hp_img2 = hp_images["none"]

    if hp >= 50:
        hp_img3 = hp_images["full"]
    elif hp > 0:
        hp_img3 = hp_images["50"]
    else:
        hp_img3 = hp_images["none"]

    if hp <= 0:
        can_ride = False
        if game_state == "playing":
            if lose_reason == "":
                lose_reason = "Закончились ХП"
            game_state = "game_over"
            name_input_active = True
            sound_game_over.play()

    # Светофоры
    sf_timer += dt
    if sf_timer < 10:
        sf_state = "green"
    elif sf_timer < 12:
        sf_state = "yellow"
    elif sf_timer < 22:
        sf_state = "red"
    else:
        sf_timer = 0
        sf_state = "green"
    current_sf_img = sf_images[sf_state]

    # Камера
    target_camera_x = max(0, player_x + 64 - screen_width // 2)
    bg4_active = False
    bg4_x = 0

    for bg, rect in world:
        if bg == backgrounds[3]:
            bg4_x = rect.x
            if rect.x <= player_x + 64 <= rect.x + 1920:
                bg4_active = True
            break

    if bg4_active:
        target_camera_x = bg4_x
        camera_y = bg44_offset_y
    else:
        target_camera_x = max(0, player_x + 64 - screen_width // 2)
        camera_y = 0

    camera_x = target_camera_x

    if not bg4_active:
        camera_y = 0
        target_camera_x = max(0, player_x + 64 - screen_width // 2)

    # Ограничения позиции игрока
    player_y = max(666, min(player_y, screen_height - 295))
    if camera_x == 0 and not bg4_active:
        player_x = max(player_x, screen_width // 2 - 64)

    # Отрисовка
    screen.fill((0, 0, 0))

    for bg, rect in world:
        if rect.x + 1920 > camera_x and rect.x < camera_x + screen_width:
            screen.blit(bg, (rect.x - camera_x, rect.y - int(camera_y)))
            if bg == backgrounds[3]:
                screen.blit(bg44, (rect.x - camera_x, rect.y + bg44_offset_y - int(camera_y)))

    # Бонус энергии
    if not bonus_collected and bonus_exists:
        screen.blit(bonus, (bonus_x - camera_x, bonus_y - int(camera_y)))

    # Бонус ХП
    if not hp_bonus_collected and hp_bonus_exists:
        screen.blit(hp_bonus, (hp_bonus_x - camera_x, hp_bonus_y - int(camera_y)))

    screen.blit(current_img, (player_x - camera_x, player_y - int(camera_y)))

    # Отрисовка хулиганов
    if not bg4_active:
        for hyligan in hyligans:
            if hyligan["x"] + 128 > camera_x and hyligan["x"] < camera_x + screen_width:
                screen.blit(hyligan["current_img"], (hyligan["x"] - camera_x, hyligan["y"] - int(camera_y)))

    # Отрисовка горизонтальных машин
    for car in cars_list:
        if car["rect"].x + 300 > camera_x and car["rect"].x < camera_x + screen_width:
            screen.blit(car["img"], (car["rect"].x - camera_x, car["rect"].y - int(camera_y)))

    # Отрисовка вертикальных машин
    if bg4_active:
        for bg, rect in world:
            if bg == backgrounds[3]:
                for car in zad_cars:
                    screen.blit(zad_img, (rect.x + car["x"] - camera_x, rect.y + car["y"] - int(camera_y)))

    # Светофоры
    for bg, rect in world:
        if rect.x + 1920 > camera_x and rect.x < camera_x + screen_width:
            if bg == backgrounds[3]:
                for sfx, sfy in sf_coords:
                    screen.blit(current_sf_img, (rect.x + sfx - camera_x, rect.y + sfy - int(camera_y)))

    screen.blit(battery_img, (screen_width - 128 - 20, screen_height - 128 - 20))
    screen.blit(hp_img, (screen_width - 225, screen_height - 105))
    screen.blit(hp_img2, (screen_width - 305, screen_height - 105))
    screen.blit(hp_img3, (screen_width - 385, screen_height - 105))

    # Отрисовка взрыва
    if boom_active:
        screen.blit(boom_frames[boom_frame_index], (boom_x - camera_x - 30, boom_y - int(camera_y) - 30))

    # Прогресс бар при атаке хулигана
    if attacked_by_hyligan:
        bar_w = 270
        bar_h = 30
        bar_x = screen_width // 2 - bar_w // 2
        bar_y = 100

        # Прогресс нажатий E
        progress = e_press_count / e_press_needed
        bar_w_e = int(bar_w * progress)
        if bar_w_e < 30:
            bar_w_e = 30
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=20)
        pygame.draw.rect(screen, (70, 140, 220), (bar_x, bar_y, bar_w_e, bar_h), border_radius=20)
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), width=2, border_radius=20)
        e_text = notif_font.render("Нажимайте E!", False, (255, 255, 255))
        screen.blit(e_text, [bar_x + bar_w // 2 - e_text.get_width() // 2, bar_y + 35])

        # Таймер
        timer_bar_y = bar_y + 70
        time_left = attack_time_limit - attack_timer
        if time_left < 0:
            time_left = 0
        timer_progress = time_left / attack_time_limit
        timer_bar_w = int(bar_w * timer_progress)
        if timer_bar_w < 17:
            timer_bar_w = 17
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, timer_bar_y, bar_w, 20), border_radius=20)
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, timer_bar_y, timer_bar_w, 20), border_radius=20)
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, timer_bar_y, bar_w, 20), width=2, border_radius=20)
        timer_text = notif_font.render(f"Осталось: {time_left:.1f} сек", False, (255, 255, 255))
        screen.blit(timer_text, [bar_x + bar_w // 2 - timer_text.get_width() // 2, timer_bar_y + 25])

    # Экран проигрыша
    if game_state == "game_over":
        # Затемнение
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Панель
        panel_w = 1200
        panel_h = 700
        panel_x = screen_width // 2 - panel_w // 2
        panel_y = screen_height // 2 - panel_h // 2

        pygame.draw.rect(screen, (50, 50, 50), (panel_x, panel_y, panel_w, panel_h), border_radius=20)
        pygame.draw.rect(screen, (70, 140, 220), (panel_x, panel_y, panel_w, panel_h), width=3, border_radius=20)

        # Заголовок
        title_text = menu_font_big.render("ИГРА ОКОНЧЕНА", False, (70, 140, 220))
        title_x = screen_width // 2 - title_text.get_width() // 2
        screen.blit(title_text, (title_x, panel_y + 80))

        # Результат
        distance_meters = int(total_distance_pixels / 1920 * 43)
        result_text = menu_font_big.render("Результат: " + str(distance_meters) + " м", False, (255, 255, 255))
        result_x = screen_width // 2 - result_text.get_width() // 2
        screen.blit(result_text, (result_x, panel_y + 180))

        # Причина
        reason_text = menu_font.render(lose_reason, False, (200, 200, 200))
        reason_x = screen_width // 2 - reason_text.get_width() // 2
        screen.blit(reason_text, (reason_x, panel_y + 265))

        # Поле ввода имени
        input_y = panel_y + 350
        input_text = menu_font.render("Введите ваш ник:", False, (200, 200, 200))
        input_text_x = screen_width // 2 - input_text.get_width() // 2
        screen.blit(input_text, (input_text_x, input_y))

        # Рамка ввода
        input_box_y = input_y + 50
        input_box_w = 800
        input_box_h = 60
        input_box_x = screen_width // 2 - input_box_w // 2

        if name_input_active:
            border_color = (70, 140, 220)
        else:
            border_color = (100, 100, 100)

        pygame.draw.rect(screen, (30, 30, 30), (input_box_x, input_box_y, input_box_w, input_box_h), border_radius=20)
        pygame.draw.rect(screen, border_color, (input_box_x, input_box_y, input_box_w, input_box_h), width=2, border_radius=20)

        # Текст ввода
        if len(player_name) > 0:
            name_render = menu_font.render(player_name, False, (255, 255, 255))
        else:
            name_render = menu_font.render("", False, (100, 100, 100))
        name_x = input_box_x + 20
        name_y = input_box_y + 17
        screen.blit(name_render, (name_x, name_y))

        # Курсор
        if name_input_active:
            cursor_x = name_x + name_render.get_width() + 2
            if pygame.time.get_ticks() % 1000 < 500:
                pygame.draw.rect(screen, (255, 255, 255), (cursor_x, name_y - 2, 5, 30))

        # Подсказка
        hint_text = menu_font.render("Нажмите ENTER для сохранения", False, (150, 150, 150))
        hint_x = screen_width // 2 - hint_text.get_width() // 2
        screen.blit(hint_text, (hint_x, input_box_y + 90))
    draw_notify()
    pygame.display.flip()
pygame.quit()
