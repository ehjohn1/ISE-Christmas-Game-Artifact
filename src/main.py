import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Screen Setup
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ISE: North Pole Protocol")

# Colors
WHITE, GOLD = (255, 255, 255), (255, 215, 0)
DARK_NAVY, RED = (10, 10, 30), (255, 0, 0)
NEON_PINK, GLOW_BLUE = (173, 216, 230), (100, 200, 255)
GREEN, GRAY, ORANGE = (0, 255, 0), (100, 100, 100), (255, 165, 0)

# Fonts
font_main = pygame.font.SysFont("arial", 60, bold=True)
font_story = pygame.font.SysFont("verdana", 24, italic=True)
font_instr = pygame.font.SysFont("arial", 22, bold=True)

# Game States
STATE_MENU, STATE_STORY, STATE_TUTORIAL = "MENU", "STORY", "TUTORIAL"
STATE_LEVEL_SELECT, STATE_GAME, STATE_CUTSCENE = "LEVEL_SELECT", "GAME", "CUTSCENE"
STATE_GAME_OVER, STATE_VICTORY = "GAME_OVER", "VICTORY"
current_state = STATE_MENU

# Player Stats
player_pos = [WIDTH // 2, HEIGHT // 2]
health, stamina = 100, 100
sugar_rush = False
sugar_rush_timer = 0
active_level, unlocked_levels = 0, 0
score, story_index = 0, 0
snowballs, enemies, particles = [], [], []

# Level Logic Tracking
rockets = []
rocket_timer, warning_timer = 0, 0
piston_y, piston_active, piston_timer = -300, False, 0
piston_rand_x = random.randint(100, WIDTH - 200)

# LVL 5 Expert Tracking
geyser_timer = 0
homing_cloud_pos = [0, 0]

# --- NEW LVL 6 LOGIC TRACKING ---
flamethrower_unlocked = False
flamethrower_active = False

# Full Narrative Data
mission_data = {
    1: {"story": ["The Snowy Courtyard is the first line of defense.",
                  "Ice Slimes are draining the Spirit of Christmas."],
        "instructions": "LEVEL 1: CLEAR 10 SLIMES TO UNLOCK THE MAIL ROOM."},
    2: {"story": ["The sorting machines are possessed by rogue code!",
                  "GRAB 10 packages with your body while dodging rockets!"],
        "instructions": "LEVEL 2: GRAB 10 LETTERS! DODGE THE HOMING ROCKETS!"},
    3: {"story": ["The Assembly Line is building a robotic army.", "Avoid the heavy pistons and destroy 10 Coal-Bots."],
        "instructions": "LEVEL 3: WATCH THE PISTONS! BELTS PUSH YOU AUTOMATICALLY."},
    4: {"story": ["The Wrapping Station is full of sticky traps."],
        "instructions": "LEVEL 4: DODGE STICKY TAPE AND CLEAR 10 ENEMIES."},
    5: {"story": ["The Engine Room heat is extreme."],
        "instructions": "LEVEL 5: STAMINA DRAINS RAPIDLY! CLEAR 10 FAST."},
    6: {"story": ["The Main Vault: The final stand against the hack."],
        "instructions": "FINAL BOSS: DESTROY THE NUTCRACKER TO SAVE CHRISTMAS!"}
}


class Snowball:
    def __init__(self, x, y, tx, ty, is_flame=False):
        self.pos = [x, y]
        self.is_flame = is_flame
        dist = ((tx - x) ** 2 + (ty - y) ** 2) ** 0.5
        speed = 25 if is_flame else 18
        self.vel = [(tx - x) / dist * speed, (ty - y) / dist * speed] if dist != 0 else [speed, 0]

    def update(self):
        self.pos[0] += self.vel[0];
        self.pos[1] += self.vel[1]


class Rocket:
    def __init__(self, x, y):
        self.pos = [float(x), float(y)]
        self.speed = 3.0
        self.rect = pygame.Rect(x, y, 20, 20)

    def update(self, p_pos):
        dx, dy = p_pos[0] - self.pos[0], p_pos[1] - self.pos[1]
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > 120:
            self.pos[0] += (dx / dist) * self.speed
            self.pos[1] += (dy / dist) * self.speed
        else:
            self.pos[0] += (dx / dist) * self.speed
            self.pos[1] += (dy / dist) * self.speed
        self.rect.topleft = self.pos


class Enemy:
    def __init__(self, x, y, hp=1, size=40, speed=1.2, boss=False):
        self.pos = [x, y];
        self.hp = hp;
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = speed;
        self.boss = boss
        self.hop_timer = random.randint(0, 100)
        self.visual_y_offset = 0
        self.drift_angle = random.uniform(-0.4, 0.4)
        self.hop_frequency = random.randint(120, 180)
        if active_level == 2:
            self.speed = 0
            self.vel = [0, 0]

        # --- HP BALANCE: BOTH LVL 3 AND 4 ARE NOW 3 HITS ---
        if active_level in [3, 4]:
            self.hp = 3
        elif active_level == 5:
            self.hp = 5  # Expert health for Level 5

    def update(self, p_pos):
        dist = ((p_pos[0] - self.pos[0]) ** 2 + (p_pos[1] - self.pos[1]) ** 2) ** 0.5
        current_speed = self.speed
        if current_state == STATE_TUTORIAL:
            current_speed = 0
        elif active_level == 2:
            current_speed = 0
        elif active_level == 1 and not self.boss:
            self.hop_timer += 1;
            current_speed = 0.3;
            hop_phase = self.hop_timer % self.hop_frequency
            if 60 <= hop_phase <= 100:
                current_speed = self.speed * 3;
                self.visual_y_offset = -abs(math.sin((hop_phase - 60) * 0.08) * 35)
                self.pos[0] += math.sin(self.hop_timer * 0.1) * 3 * self.drift_angle
            else:
                self.visual_y_offset = 0
        if dist != 0 and active_level != 2:
            self.pos[0] += (p_pos[0] - self.pos[0]) / dist * current_speed
            self.pos[1] += (p_pos[1] - self.pos[1]) / dist * current_speed
        self.rect.topleft = (self.pos[0], self.pos[1])


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color);
    screen.blit(img, (x - img.get_width() // 2, y))


def reset_game():
    global health, stamina, score, enemies, snowballs, particles, rockets, sugar_rush, sugar_rush_timer, rocket_timer, warning_timer, piston_y, piston_active, piston_timer, piston_rand_x, geyser_timer, flamethrower_active, flamethrower_unlocked
    health, stamina, score, sugar_rush, sugar_rush_timer = 100, 100, 0, False, 0
    enemies, snowballs, particles, rockets = [], [], [], [];
    rocket_timer, warning_timer, piston_y, piston_active, piston_timer = 0, 0, -300, False, 0
    piston_rand_x = random.randint(100, WIDTH - 200)
    geyser_timer = 0
    flamethrower_active = False
    flamethrower_unlocked = False


# --- Main Game Loop ---
running, clock = True, pygame.time.Clock()
while running:
    screen.fill(DARK_NAVY)
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_state == STATE_MENU:
                if pygame.Rect(WIDTH // 2 - 150, 400, 300, 70).collidepoint(event.pos): current_state = STATE_STORY
            elif current_state in [STATE_TUTORIAL, STATE_GAME]:
                if active_level != 2:
                    snowballs.append(
                        Snowball(player_pos[0] + 25, player_pos[1] + 25, mx, my, is_flame=flamethrower_active))
            elif current_state == STATE_LEVEL_SELECT:
                for i in range(1, 7):
                    rect = pygame.Rect(300 + ((i - 1) % 3) * 350 - 100, 300 + ((i - 1) // 3) * 180, 200, 100)
                    if rect.collidepoint(event.pos) and i <= unlocked_levels:
                        active_level, current_state, story_index = i, STATE_CUTSCENE, 0;
                        reset_game()
            elif current_state == STATE_GAME_OVER:
                if pygame.Rect(WIDTH // 2 - 100, 350, 200, 50).collidepoint(
                        event.pos): reset_game(); current_state = STATE_GAME
                if pygame.Rect(WIDTH // 2 - 100, 420, 200, 50).collidepoint(
                        event.pos): current_state = STATE_LEVEL_SELECT
                if pygame.Rect(WIDTH // 2 - 100, 490, 200, 50).collidepoint(event.pos): current_state = STATE_MENU
            elif current_state == STATE_VICTORY:
                if pygame.Rect(WIDTH // 2 - 100, 500, 200, 60).collidepoint(event.pos): current_state = STATE_MENU

        if event.type == pygame.KEYDOWN:
            if current_state == STATE_STORY and event.key == pygame.K_SPACE:
                current_state = STATE_TUTORIAL;
                reset_game();
                enemies = [Enemy(WIDTH - 200, HEIGHT // 2, speed=0)]
            if current_state == STATE_TUTORIAL and event.key == pygame.K_e and not enemies:
                unlocked_levels = max(unlocked_levels, 1);
                current_state = STATE_LEVEL_SELECT
            if current_state == STATE_CUTSCENE and event.key == pygame.K_SPACE:
                story_index += 1
                if story_index >= len(mission_data[active_level]["story"]): current_state = STATE_GAME

    if current_state in [STATE_TUTORIAL, STATE_GAME]:
        move_speed = 12 if sugar_rush else 7
        if stamina <= 0: move_speed = 2  # EXHAUSTION PENALTY

        keys = pygame.key.get_pressed()
        moving = False

        if active_level == 3:
            pygame.draw.rect(screen, (20, 20, 40), (0, 60, WIDTH, 260))
            pygame.draw.rect(screen, (20, 20, 40), (0, 390, WIDTH, 260))
            if 60 < player_pos[1] < 320: player_pos[0] += 4
            if 390 < player_pos[1] < 650: player_pos[0] -= 4

        if active_level == 4:
            traps = [
                pygame.Rect(0, 0, WIDTH, 100), pygame.Rect(0, HEIGHT - 100, WIDTH, 100),
                pygame.Rect(100, 100, 250, 500), pygame.Rect(450, 100, 350, 200),
                pygame.Rect(450, 400, 350, 220), pygame.Rect(900, 100, 300, 500)
            ]
            p_rect_lvl4 = pygame.Rect(player_pos[0], player_pos[1], 50, 50)
            for t in traps:
                pygame.draw.rect(screen, (130, 130, 90), t)
                if p_rect_lvl4.colliderect(t): move_speed = 2.5

            p_timer_limit = 80
            piston_timer += 1
            if piston_timer > p_timer_limit:
                piston_active = True;
                piston_y += 50
                if piston_y > HEIGHT:
                    piston_timer = 0;
                    piston_y = -300;
                    piston_active = False
                    piston_rand_x = random.randint(100, WIDTH - 200)

            pist_rect = pygame.Rect(piston_rand_x, piston_y, 180, 400)
            pygame.draw.rect(screen, GRAY, pist_rect)
            if pist_rect.colliderect(p_rect_lvl4) and piston_active: health -= 35; stamina = 0; piston_active = False

        # --- LEVEL 5: ENGINE ROOM (ANTI-CAMPING LOGIC) ---
        if active_level == 5:
            if moving: stamina -= 1.0  # Passive Heat Drain

            # 1. Homing Heat Cloud
            dx, dy = player_pos[0] - homing_cloud_pos[0], player_pos[1] - homing_cloud_pos[1]
            dist_cloud = (dx ** 2 + dy ** 2) ** 0.5
            if dist_cloud != 0:
                homing_cloud_pos[0] += (dx / dist_cloud) * 2.8
                homing_cloud_pos[1] += (dy / dist_cloud) * 2.8

            # Draw Homing Cloud Particles
            for _ in range(3):
                particles.append(
                    [[homing_cloud_pos[0] + random.randint(-35, 35), homing_cloud_pos[1] + random.randint(-35, 35)],
                     [0, -1.5], random.randint(10, 18)])

            if dist_cloud < 65:
                health -= 0.8
                stamina -= 2.5

            # 2. Random Steam Geysers
            geyser_timer += 1
            if geyser_timer % 45 == 0:
                gx, gy = random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)
                for _ in range(20):
                    particles.append([[gx, gy], [random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5)], 12])
                if math.sqrt((player_pos[0] - gx) ** 2 + (player_pos[1] - gy) ** 2) < 90:
                    health -= 12

        # --- LEVEL 6: FINAL BOSS FLAMETHROWER LOGIC ---
        if active_level == 6:
            player_rect = pygame.Rect(player_pos[0], player_pos[1], 50, 50)
            # Phase 1: Hunt minions
            if score < 10:
                draw_text(f"SCORE: {score}/10 TO UNLOCK FLAMETHROWER", font_instr, WHITE, WIDTH // 2, 100)
            # Phase 2: Item spawns
            elif score >= 10 and not flamethrower_unlocked:
                flame_item = pygame.Rect(WIDTH // 2 - 25, HEIGHT // 2 - 25, 50, 50)
                pygame.draw.rect(screen, ORANGE, flame_item)
                draw_text("COLLECT THE FLAMETHROWER!", font_instr, GOLD, WIDTH // 2, HEIGHT // 2 - 60)
                if player_rect.colliderect(flame_item):
                    flamethrower_unlocked = True
                    flamethrower_active = True
                    # Spawn Boss Nutcracker
                    enemies = [Enemy(WIDTH // 2 - 60, 120, hp=50, size=120, speed=2, boss=True)]
                    score = 0
            # Phase 3: Boss fight
            if flamethrower_unlocked and enemies:
                pygame.draw.rect(screen, RED, (WIDTH // 2 - 250, 20, 500, 25))
                pygame.draw.rect(screen, GREEN, (WIDTH // 2 - 250, 20, enemies[0].hp * 10, 25))
                draw_text("ROBOTIC NUTCRACKER", font_instr, WHITE, WIDTH // 2, 55)
                # Rapid rockets
                rocket_timer += 1
                if rocket_timer > 60:
                    rockets.append(Rocket(random.randint(0, WIDTH), 0))
                    rocket_timer = 0

        if stamina > 0:
            if keys[pygame.K_w] and player_pos[1] > 0: player_pos[1] -= move_speed; moving = True
            if keys[pygame.K_s] and player_pos[1] < HEIGHT - 50: player_pos[1] += move_speed; moving = True
            if keys[pygame.K_a] and player_pos[0] > 0: player_pos[0] -= move_speed; moving = True
            if keys[pygame.K_d] and player_pos[0] < WIDTH - 50: player_pos[0] += move_speed; moving = True

        if sugar_rush:
            particles.append(
                [[player_pos[0] + 25, player_pos[1] + 25], [random.uniform(-1, 1), random.uniform(-1, 1)], 10])
            sugar_rush_timer -= 1
            if sugar_rush_timer <= 0: sugar_rush = False

        if moving and not sugar_rush:
            stamina -= 0.5
        elif not moving:
            stamina = min(100, stamina + 0.3)

        if active_level == 3:
            piston_timer += 1
            if 60 < piston_timer < 100:
                for i in range(200, WIDTH, 400): pygame.draw.rect(screen, (30, 30, 50), (i, 0, 180, HEIGHT))
            if piston_timer > 100:
                piston_active = True;
                piston_y += 45
                if piston_y > HEIGHT: piston_timer = 0; piston_y = -300; piston_active = False
            for i in range(200, WIDTH, 400):
                pist_rect = pygame.Rect(i, piston_y, 180, 400);
                pygame.draw.rect(screen, GRAY, pist_rect)
                if pist_rect.colliderect(pygame.Rect(player_pos[0], player_pos[1], 50,
                                                     50)) and piston_active: health -= 30; stamina = 0; piston_active = False

        if active_level == 2:
            rocket_timer += 1
            if 150 <= rocket_timer < 180: warning_timer = 30
            if rocket_timer >= 180:
                rc = 5 if score < 4 else (6 if score < 8 else 7)
                for _ in range(rc): rockets.append(Rocket(random.choice([-50, WIDTH + 50]), random.randint(0, HEIGHT)))
                rocket_timer, warning_timer = 0, 0
            if warning_timer > 0: pygame.draw.circle(screen, RED, (int(player_pos[0] + 25), int(player_pos[1] + 25)),
                                                     60, 2); warning_timer -= 1

        p_rect = pygame.Rect(player_pos[0], player_pos[1], 50, 50)
        for r in rockets[:]:
            r.update(player_pos);
            pygame.draw.rect(screen, NEON_PINK, r.rect)
            if p_rect.colliderect(r.rect): health -= 15; rockets.remove(r)

        pygame.draw.rect(screen, GREEN, p_rect)
        for e in enemies[:]:
            e.update(player_pos);
            draw_r = e.rect.copy();
            pygame.draw.rect(screen, RED, draw_r)
            if active_level == 2 and p_rect.colliderect(e.rect):
                enemies.remove(e);
                score += 1;
                sugar_rush, sugar_rush_timer = True, 120;
                stamina = min(100, stamina + 15)
            elif active_level != 2 and p_rect.colliderect(e.rect):
                health -= 1
            for s in snowballs[:]:
                if e.rect.collidepoint(s.pos):
                    # Flamethrower deals more damage
                    e.hp -= (3 if s.is_flame else 1);
                    if s in snowballs: snowballs.remove(s)
                    if e.hp <= 0:
                        if e.boss:
                            current_state = STATE_VICTORY
                            unlocked_levels = 7
                        enemies.remove(e);
                        score += 1;
                        stamina = min(100, stamina + 15)
                        if active_level == 6 and flamethrower_unlocked and not e.boss: pass  # continue loop if not boss

        if score < 10 and len(enemies) < 4 and not (active_level == 6 and flamethrower_unlocked):
            enemies.append(Enemy(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)))
        if score >= 10 and active_level != 6: unlocked_levels = max(unlocked_levels,
                                                                    active_level + 1); current_state = STATE_LEVEL_SELECT
        if health <= 0: current_state = STATE_GAME_OVER

    # --- RENDERING (ALL ORIGINAL DETAILS) ---
    if current_state == STATE_MENU:
        for _ in range(2): particles.append(
            [[random.randint(0, WIDTH), 0], [random.uniform(-1, 1), random.uniform(2, 5)], random.randint(2, 5)])
        for p in particles[:]:
            p[0][0] += p[1][0];
            p[0][1] += p[1][1];
            pygame.draw.circle(screen, WHITE, (int(p[0][0]), int(p[0][1])), int(p[2]))
            if p[0][1] > HEIGHT: particles.remove(p)
        draw_text("NORTH POLE PROTOCOL", font_main, GLOW_BLUE, WIDTH // 2, 150)
        draw_text("SYSTEM STATUS: COMPROMISED", font_instr, RED, WIDTH // 2, 220)
        draw_text("OBJECTIVE: RESTORE THE SPIRIT OF CHRISTMAS ENERGY", font_instr, GOLD, WIDTH // 2, 250)
        btn_rect = pygame.Rect(WIDTH // 2 - 150, 400, 300, 70);
        btn_color = (0, 255, 0) if btn_rect.collidepoint(mx, my) else (0, 200, 0)
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=15)
        if btn_rect.collidepoint(mx, my): pygame.draw.rect(screen, WHITE, btn_rect, 3, border_radius=15)
        draw_text("INITIALIZE MISSION", font_story, DARK_NAVY, WIDTH // 2, 432)
        draw_text("v1.0.4 - SECURE CONNECTION ACTIVE", font_instr, GRAY, WIDTH // 2, 680)

    elif current_state == STATE_STORY:
        draw_text("THE NORTH POLE HAS BEEN HACKED BY A ROGUE ELF.", font_story, WHITE, WIDTH // 2, 250)
        draw_text("[ PRESS SPACE TO START ELF BOOTCAMP ]", font_story, GOLD, WIDTH // 2, 450)

    elif current_state == STATE_TUTORIAL:
        draw_text("ELF BOOTCAMP: TARGET PRACTICE", font_instr, WHITE, WIDTH // 2, 50)
        draw_text("INSTRUCTIONS: USE 'WASD' TO MOVE | CLICK TO SHOOT TARGET", font_instr, WHITE, WIDTH // 2, 650)
        if not enemies: draw_text("BOOTCAMP COMPLETE! PRESS 'E' TO EXIT", font_story, GOLD, WIDTH // 2, HEIGHT // 2)

    elif current_state == STATE_CUTSCENE:
        screen.fill((5, 15, 5))
        for i in range(0, HEIGHT, 4): pygame.draw.line(screen, (0, 20, 0), (0, i), (WIDTH, i))
        draw_text(mission_data[active_level]["story"][story_index], font_story, WHITE, WIDTH // 2, 330)
        draw_text("[ PRESS SPACE TO CONTINUE ]", font_instr, GOLD, WIDTH // 2, 600)

    elif current_state == STATE_LEVEL_SELECT:
        draw_text("MISSION SELECTOR", font_main, GLOW_BLUE, WIDTH // 2, 80)
        for i in range(1, 7):
            col, row = (i - 1) % 3, (i - 1) // 3;
            color = GREEN if i <= unlocked_levels else GRAY
            pygame.draw.rect(screen, color, (300 + (col * 350) - 100, 300 + (row * 180), 200, 100), border_radius=15)
            draw_text(f"LEVEL {i}" if i <= unlocked_levels else "LOCKED", font_story, WHITE, 300 + (col * 350),
                      300 + (row * 180) + 35)

    elif current_state == STATE_GAME_OVER:
        draw_text("MISSION COMPROMISED", font_main, RED, WIDTH // 2, 200)
        opts = [("RESTART", 350), ("LEVEL SELECT", 420), ("HOME", 490)]
        for text, y in opts:
            r = pygame.Rect(WIDTH // 2 - 100, y, 200, 50);
            pygame.draw.rect(screen, (150, 150, 150) if r.collidepoint(mx, my) else GRAY, r, border_radius=10)
            draw_text(text, font_instr, WHITE, WIDTH // 2, y + 12)

    elif current_state == STATE_VICTORY:
        # Victory Page Logic
        draw_text("MISSION ACCOMPLISHED", font_main, GOLD, WIDTH // 2, 200)
        draw_text("THE HACK HAS BEEN PURGED. THE NORTH POLE IS SAFE!", font_story, WHITE, WIDTH // 2, 300)
        draw_text("YOU ARE THE ULTIMATE GUARDIAN ELF.", font_instr, GREEN, WIDTH // 2, 360)

        # Christmas Spirit Particles (rising up)
        for _ in range(2):
            particles.append([[random.randint(0, WIDTH), HEIGHT], [random.uniform(-1, 1), -random.uniform(2, 6)], 8])

        v_btn = pygame.Rect(WIDTH // 2 - 100, 500, 200, 60)
        pygame.draw.rect(screen, GOLD if v_btn.collidepoint(mx, my) else GREEN, v_btn, border_radius=15)
        draw_text("MAIN MENU", font_instr, DARK_NAVY, WIDTH // 2, 518)

    elif current_state == STATE_GAME:
        draw_text(mission_data[active_level]["instructions"], font_instr, GOLD, WIDTH // 2, 680)
        draw_text(f"HP: {int(health)} | STAMINA: {int(stamina)} | SCORE: {score}/10", font_instr, WHITE, 250, 30)

    for s in snowballs: s.update(); pygame.draw.circle(screen, ORANGE if s.is_flame else WHITE,
                                                       (int(s.pos[0]), int(s.pos[1])), 8)
    for p in particles[:]:
        if current_state != STATE_MENU:
            p[0][0] += p[1][0];
            p[0][1] += p[1][1];
            p[2] -= 0.1  # Slower shrink for victory/game trail
            # RENDER: Gold for victory, Gray smoke for Engine Room, Neon Pink for others
            if current_state == STATE_VICTORY:
                trail_color = GOLD
            else:
                trail_color = (200, 210, 210) if active_level in [5, 6] else NEON_PINK

            pygame.draw.circle(screen, trail_color, (int(p[0][0]), int(p[0][1])), int(max(1, p[2])))
            if p[2] <= 0 or p[0][1] < -50: particles.remove(p)

    pygame.display.flip();
    clock.tick(60)
pygame.quit()
