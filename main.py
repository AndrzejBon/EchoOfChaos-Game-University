import pygame
import random
import sys

# Importy modułów gry
from player import Player
from enemy import Enemy
from level_system import LevelSystem
from ranged_enemy import RangedEnemy
from projectile_enemy import EnemyProjectile
from tile_manager import TileManager
from wave_collapse import WaveCollapse
from adjacency_rules import adjacency_rules
from wave_system import WaveSystem
from boss_enemy import BossEnemy
from audio_manager import AudioManager
from screens import TitleScreen, IntroScreen, BossVictoryScreen, GameOverScreen

# ============================
# KONFIGURACJA I STAŁE
# ============================
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 900
FPS = 60
BLACK = (0, 0, 0)

# Wczytanie kafelka tła (placeholder)
tile = pygame.image.load("assets/images/tile_placeholder.png")
tile = pygame.transform.scale(tile, (32, 32))

# Konfiguracja fal – przykładowe dane dla systemu fal
WAVE_DATA = [
    {
        "duration": 30,  # fala trwa 20 sekund
        "spawn_rates": {
            "basic": 1.0,   # BasicEnemy pojawia się co 1 sekundę
            "ranged": 3.0   # RangedEnemy co 3 sekundy
        },
        "boss": False
    },
    {
        "duration": 30,
        "spawn_rates": {
            "basic": 0.8,
            "ranged": 2.5
        },
        "boss": False
    },
    # Kolejne fale – analogicznie
    {
        "duration": 30,
        "spawn_rates": {
            "basic": 0.7,
            "ranged": 2.25
        },
        "boss": False
    },
    {
        "duration": 30,
        "spawn_rates": {
            "basic": 0.6,
            "ranged": 2.0
        },
        "boss": False
    },
    {
        "duration": 30,
        "spawn_rates": {
            "basic": 0.5,
            "ranged": 1.75
        },
        "boss": False
    },
    {
        "duration": 30,
        "spawn_rates": {
            "basic": 0.4,
            "ranged": 1.5
        },
        "boss": False
    },
    {
        "duration": 30,
        "spawn_rates": {
            "basic": 0.3,
            "ranged": 1.25
        },
        "boss": False
    },
    {
        "duration": 30,
        "spawn_rates": {
            "basic": 0.2,
            "ranged": 1.00
        },
        "boss": False
    },
    {
        "duration": 30,
        "spawn_rates": {
            "basic": 0.1,
            "ranged": 0.75
        },
        "boss": False
    },
    {
        "duration": 120,
        "spawn_rates": {},  # Pusta lista spawnów – tylko boss
        "boss": True
    },
]

# ============================
# FUNKCJE POMOCNICZE RYSOWANIA
# ============================
def draw_experience_bar_and_timer(screen, level_system, screen_width, game_time):
    """
    Rysuje pasek doświadczenia oraz zegar rozgrywki.
    """
    bar_width = screen_width - 40
    bar_height = 20
    bar_x = 20
    bar_y = 10
    corner_radius = 10

    # Obliczenie postępu doświadczenia
    progress_ratio = level_system.chaos_points / level_system.points_needed
    progress_width = int(bar_width * progress_ratio)

    # Pasek tła, postępu i ramka
    pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), border_radius=corner_radius)
    pygame.draw.rect(screen, (0, 0, 255), (bar_x, bar_y, progress_width, bar_height), border_radius=corner_radius)
    pygame.draw.rect(screen, (255, 215, 0), (bar_x, bar_y, bar_width, bar_height), width=2, border_radius=corner_radius)

    # Rysowanie poziomu gracza (tekst)
    font = pygame.font.SysFont("Arial", 18)
    level_text = f"Poziom {level_system.current_level}"
    level_surf = font.render(level_text, True, (255, 255, 255))
    level_x = bar_x + 40  # przykładowe przesunięcie
    level_y = bar_y + bar_height // 2
    level_rect = level_surf.get_rect(center=(level_x, level_y))
    screen.blit(level_surf, level_rect)

    # Rysowanie zegara – przekształcenie czasu do formatu mm:ss
    timer_y = bar_y + bar_height + 25
    minutes = int(game_time // 60)
    seconds = int(game_time % 60)
    timer_str = f"{minutes:02d}:{seconds:02d}"
    font = pygame.font.SysFont("Arial", 24)
    timer_surf = font.render(timer_str, True, (255, 255, 255))
    timer_rect = timer_surf.get_rect(center=(screen_width // 2, timer_y))
    screen.blit(timer_surf, timer_rect)


def draw_tiled_background(screen, tile, screen_width, screen_height, tile_size):
    """
    Rysuje tło z kafelków – uzupełniając krawędzie.
    """
    tiles_x = (screen_width // tile_size) + 1
    tiles_y = (screen_height // tile_size) + 1
    for row in range(tiles_y):
        for col in range(tiles_x):
            screen.blit(tile, (col * tile_size, row * tile_size))


def update_camera_on_player(player, camera_x, camera_y, screen_width, screen_height, map_width, map_height, tile_size):
    """
    Aktualizuje pozycję kamery, aby gracz był mniej więcej na środku ekranu,
    przy jednoczesnym ograniczeniu ruchu kamery do obszaru mapy.
    """
    desired_cx = player.x - screen_width // 2 + player.width // 2
    desired_cy = player.y - screen_height // 2 + player.height // 2

    max_x = map_width * tile_size - screen_width
    max_y = map_height * tile_size - screen_height

    new_camera_x = max(0, min(desired_cx, max_x))
    new_camera_y = max(0, min(desired_cy, max_y))

    return new_camera_x, new_camera_y


# ============================
# FUNKCJA GŁÓWNA
# ============================
def main():
    pygame.init()
    AudioManager.init()  # Inicjalizacja audio
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Echo of Chaos")
    clock = pygame.time.Clock()

    # ----------------------------
    # Inicjalizacja ekranów i stanów gry
    # ----------------------------
    game_state = "title"  # możliwe stany: title, intro, running, boss_defeated, game_over
    title_screen = TitleScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
    intro_screen = IntroScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
    boss_victory_screen = BossVictoryScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
    game_over_screen = GameOverScreen(SCREEN_WIDTH, SCREEN_HEIGHT)

    # ----------------------------
    # Generowanie terenu
    # ----------------------------
    tile_manager = TileManager("assets/images/tileset.png")
    all_tiles = list(adjacency_rules.keys())
    # Ustawienia wymiarów mapy – tutaj 60x60 kafelków
    map_width, map_height = 60, 60

    # Wykonujemy Wave Function Collapse dla terenu
    wfc = WaveCollapse(map_width, map_height, all_tiles)
    terrain_map = wfc.collapse()

    # Pobieramy prostokąty kolizji ze wszystkich kafelków
    all_wall_rects = []
    for row in range(map_height):
        for col in range(map_width):
            tile_name = terrain_map[row][col]
            x = col * tile_manager.tile_width()
            y = row * tile_manager.tile_height()
            collision_rects = tile_manager.get_collision_rects(tile_name, x, y)
            all_wall_rects.extend(collision_rects)

    # ----------------------------
    # Inicjalizacja zmiennych gry
    # ----------------------------
    running = True
    game_over = False
    map_pixel_width = map_width * tile_manager.tile_width()
    map_pixel_height = map_height * tile_manager.tile_height()
    camera_x, camera_y = 0, 0
    game_time = 0

    # Inicjalizacja systemu fal
    wave_system = WaveSystem(WAVE_DATA, total_game_time=600, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

    # Inicjalizacja gracza:
    # Wybieramy środek dowolnego kafelka typu "floor"
    candidate_positions = []
    for row in range(map_height):
        for col in range(map_width):
            if terrain_map[row][col] == "floor":
                px = col * tile_manager.tile_width() + tile_manager.tile_width() // 2
                py = row * tile_manager.tile_height() + tile_manager.tile_height() // 2
                candidate_positions.append((px, py))
    mid_idx = len(candidate_positions) // 2
    spawn_x, spawn_y = candidate_positions[mid_idx]
    player = Player(spawn_x - 32, spawn_y - 32)  # centrowanie gracza

    enemies = []  # Lista przeciwników
    # Inicjalizacja systemu poziomów (do ulepszania broni i przyrostu XP)
    level_system = LevelSystem(player)

    frame_count = 0
    start_time = pygame.time.get_ticks()

    # Zmienna służąca do odliczania klatek przy kolizjach przeciwników (używana m.in. w enemy.check_collision_with_player)
    enemy_frame_counter = 0
    boss_defeated = False

    # ----------------------------
    # GŁÓWNA PĘTLA GRY
    # ----------------------------
    while running:
        raw_dt = clock.get_time() / 1000.0
        delta_time = min(raw_dt, 0.1)  # ograniczenie delta_time
        # Jeśli gracz jest w menu ulepszeń, pauzujemy aktualizację fal
        dt_for_wave = 0.0 if level_system.in_level_up_menu else delta_time

        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
        frame_count += 1
        if frame_count % 60 == 0:
            actual_fps = frame_count / elapsed_time
            print(f"Rzeczywiste FPS: {actual_fps:.2f} (logowane co 60 klatek)")

        # ----------------------------
        # Obsługa zdarzeń
        # ----------------------------
        for event in pygame.event.get():
            # Jeśli gracz jest w menu ulepszeń – przekazujemy zdarzenia do obsługi menu
            if level_system.in_level_up_menu:
                level_system.handle_menu_input(event)

            # Obsługa zdarzeń ekranów specjalnych (title, intro, boss_defeated, game_over)
            if game_state == "title":
                title_screen.handle_event(event)
            elif game_state == "intro":
                intro_screen.handle_event(event)
            elif game_state == "boss_defeated":
                boss_victory_screen.handle_event(event)
            elif game_state == "game_over":
                game_over_screen.handle_event(event)
            else:
                # Obsługa standardowych zdarzeń gry
                if event.type == pygame.QUIT:
                    running = False

        # ----------------------------
        # Logika stanów gry
        # ----------------------------
        if game_state == "title":
            title_screen.update()
            title_screen.draw(screen)
            pygame.display.flip()

            if not title_screen.running:
                if title_screen.clicked_option == "start":
                    game_state = "intro"  # przejście do ekranu wprowadzającego
                else:
                    running = False
            continue  # pomijamy dalszą logikę, gdy jesteśmy w ekranie tytułowym

        elif game_state == "intro":
            intro_screen.update()
            intro_screen.draw(screen)
            pygame.display.flip()
            if not intro_screen.running:
                game_state = "running"
            # Uruchamiamy muzykę po zakończeniu intro
            pygame.mixer.music.load(AudioManager.normal_bgm)
            pygame.mixer.music.play(-1)  # zapętlenie muzyki
            continue

        elif game_state == "boss_defeated":
            boss_victory_screen.update()
            boss_victory_screen.draw(screen)
            pygame.display.flip()
            if not boss_victory_screen.running:
                # Restart gry – wywołanie main() ponownie
                main()
                return
            continue

        elif game_state == "game_over":
            game_over_screen.update()
            game_over_screen.draw(screen)
            pygame.display.flip()
            if not game_over_screen.running:
                main()
                return
            continue

        # ----------------------------
        # Główna logika gry (stan "running")
        # ----------------------------
        if level_system.in_level_up_menu:
            # Jeśli aktywne jest menu ulepszeń – renderujemy grę w tle
            screen.fill(BLACK)
            for row in range(map_height):
                for col in range(map_width):
                    tile_name = terrain_map[row][col]
                    tile_surf = tile_manager.get_surface(tile_name)
                    screen_x = col * tile_manager.tile_width() - camera_x
                    screen_y = row * tile_manager.tile_height() - camera_y
                    screen.blit(tile_surf, (screen_x, screen_y))
            player.draw(screen, camera_x, camera_y)
            for enemy in enemies:
                enemy.draw(screen, camera_x, camera_y)
            draw_experience_bar_and_timer(screen, level_system, SCREEN_WIDTH, game_time)
            level_system.draw_level_up_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            pygame.display.flip()

            # Aktualizacja fal – zatrzymujemy ruch przeciwników, gdy gracz wybiera ulepszenie
            wave_system.update(
                game_time=game_time,
                delta_time=0.0,
                enemies=enemies,
                all_wall_rects=all_wall_rects,
                camera_x=camera_x, camera_y=camera_y,
                map_pixel_width=map_pixel_width, map_pixel_height=map_pixel_height
            )
            continue
        else:
            # Aktualizacja czasu i fal
            game_time += delta_time
            wave_system.update(
                game_time=game_time,
                delta_time=delta_time,
                enemies=enemies,
                all_wall_rects=all_wall_rects,
                camera_x=camera_x, camera_y=camera_y,
                map_pixel_width=map_pixel_width, map_pixel_height=map_pixel_height
            )
            enemy_frame_counter += 1

        # Sprawdzenie stanu gracza (koniec gry)
        if player.health <= 0:
            AudioManager.play_player_death()
            AudioManager.fade_to_gameover_music()
            game_state = "game_over"
            continue

        # ----------------------------
        # Aktualizacja gracza oraz broni
        # ----------------------------
        keys = pygame.key.get_pressed()
        player.update(keys, map_width, map_height, all_wall_rects, screen, level_system, delta_time, map_width, map_height)
        player.secondary_weapon_1.update(player, enemies, screen, level_system, delta_time)
        player.secondary_weapon_2.update(player, enemies, screen, level_system, delta_time)

        # ----------------------------
        # Aktualizacja przeciwników
        # ----------------------------
        for enemy in enemies[:]:
            if isinstance(enemy, BossEnemy):
                enemy.update(player, SCREEN_WIDTH, SCREEN_HEIGHT, enemies, all_wall_rects, map_width, map_height)
            elif isinstance(enemy, RangedEnemy):
                enemy.update(player, SCREEN_WIDTH, SCREEN_HEIGHT, all_wall_rects, map_width, map_height)
            else:
                enemy.move_towards_player(player.x, player.y, None)
                enemy.check_collision_with_player(player, enemy_frame_counter)
            # Sprawdzenie kolizji pocisków gracza z przeciwnikami
            for projectile in player.current_weapon.projectiles[:]:
                if enemy.rect.colliderect(projectile.rect):
                    player.current_weapon.projectiles.remove(projectile)
                    if enemy.take_damage(player.current_weapon.damage):
                        enemy.to_remove = True
                        level_system.add_chaos_points(enemy.xp_value)

        # Usuwamy przeciwników oznaczonych do usunięcia
        enemies_to_remove = [enemy for enemy in enemies if enemy.to_remove]
        enemies = [enemy for enemy in enemies if not enemy.to_remove]

        # Jeśli któryś z usuniętych przeciwników był Boss-em, zmieniamy stan gry
        if any(isinstance(enemy, BossEnemy) for enemy in enemies_to_remove):
            boss_defeated = True
            print("Boss został pokonany!")
            AudioManager.fade_to_gameover_music()  # lub odtwarzamy muzykę zwycięstwa
            game_state = "boss_defeated"
            continue

        # Obsługa menu ulepszeń, jeśli gracz awansował
        level_system.handle_possible_level_up()

        # Aktualizacja kamery, aby gracz był na środku
        camera_x, camera_y = update_camera_on_player(
            player,
            camera_x,
            camera_y,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            map_width,
            map_height,
            tile_manager.tile_width()
        )

        # Rysowanie tła (kafelki)
        for row in range(map_height):
            for col in range(map_width):
                tile_name = terrain_map[row][col]
                tile_surf = tile_manager.get_surface(tile_name)
                world_x = col * tile_manager.tile_width()
                world_y = row * tile_manager.tile_height()
                screen_x = world_x - camera_x
                screen_y = world_y - camera_y
                screen.blit(tile_surf, (screen_x, screen_y))

        # Rysowanie efektów wybuchu przed innymi elementami
        player.secondary_weapon_2.draw_explosions(screen, camera_x, camera_y)
        # Rysowanie gracza oraz przeciwników
        player.draw(screen, camera_x, camera_y)
        for enemy in enemies:
            enemy.draw(screen, camera_x, camera_y)

        # Rysowanie paska doświadczenia
        draw_experience_bar_and_timer(screen, level_system, SCREEN_WIDTH, game_time)

        # Jeśli menu ulepszeń jest aktywne – rysujemy je na wierzchu
        if level_system.in_level_up_menu:
            level_system.draw_level_up_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Reset flagi dla broni (np. aktualizacji satelitów czy wybuchów)
        player.secondary_weapon_1.satellite_updated = False
        player.secondary_weapon_2.explosion_updated = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
