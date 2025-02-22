import pygame
import random
import math

from enemy import Enemy
from ranged_enemy import RangedEnemy
from boss_enemy import BossEnemy
from audio_manager import AudioManager

class WaveSystem:
    def __init__(self, wave_data, total_game_time=600, screen_width=1200, screen_height=900):
        """
        Inicjalizuje system fal na podstawie przekazanych danych.
        
        :param wave_data: Lista słowników opisujących poszczególne fale. Przykładowy format:
            {
              "duration": 60,          # czas trwania fali w sekundach
              "spawn_rates": {         # tempo spawnienia przeciwników (w sekundach)
                 "basic": 1.0,         # spawn BasicEnemy co 1 sekundę
                 "ranged": 3.0         # spawn RangedEnemy co 3 sekundy
              },
              "boss": False            # flaga określająca, czy w tej fali pojawia się boss
            }
        :param total_game_time: Całkowity czas trwania gry (np. 600 sekund)
        :param screen_width: Szerokość okna gry (w pikselach)
        :param screen_height: Wysokość okna gry (w pikselach)
        """
        self.wave_data = wave_data
        self.total_game_time = total_game_time
        self.current_wave_index = 0
        self.wave_start_time = 0.0  # Czas rozpoczęcia aktualnej fali (w sekundach)
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Timery spawnów przeciwników – będą zwiększane o delta_time
        self.basic_timer = 0.0
        self.ranged_timer = 0.0

        self.boss_spawned = False  # Flaga, czy boss już został zspawniony w tej fali

    def update(self, game_time, delta_time, enemies, all_wall_rects,
               camera_x, camera_y, map_pixel_width, map_pixel_height):
        """
        Aktualizuje system fal na podstawie upływającego czasu.
        
        :param game_time: Aktualny czas gry (w sekundach). Wartość ta może być "zamrożona" podczas menu.
        :param delta_time: Czas, który upłynął od ostatniej klatki (w sekundach)
        :param enemies: Lista aktualnych przeciwników – do której będą dodawane nowe spawnowane jednostki.
        :param all_wall_rects: Lista prostokątów kolizji – używana przy generowaniu pozycji spawnu.
        :param camera_x: Pozycja kamery w osi X (w pikselach)
        :param camera_y: Pozycja kamery w osi Y (w pikselach)
        :param map_pixel_width: Szerokość mapy w pikselach
        :param map_pixel_height: Wysokość mapy w pikselach
        """
        # Jeśli wszystkie fale zostały zakończone, nie wykonujemy dalszej aktualizacji
        if self.current_wave_index >= len(self.wave_data):
            return

        # Pobranie danych aktualnej fali
        wave_info = self.wave_data[self.current_wave_index]
        wave_duration = wave_info["duration"]
        spawn_rates = wave_info.get("spawn_rates", {})
        is_boss_wave = wave_info.get("boss", False)

        # 1) Na początku fali (gdy wave_start_time == 0) wywołujemy start_wave, który m.in. spawnuje bossa
        if self.wave_start_time == 0.0:
            self.start_wave(game_time, wave_info, enemies, all_wall_rects,
                            camera_x, camera_y, map_pixel_width, map_pixel_height)

        # 2) Obliczamy, ile czasu minęło od rozpoczęcia aktualnej fali
        time_in_wave = game_time - self.wave_start_time
        if time_in_wave < 0:
            time_in_wave = 0  # zabezpieczenie

        # 3) Jeśli fala nie jest falą z bossem, sprawdzamy spawn przeciwników według określonych spawn_rates
        if not is_boss_wave and spawn_rates:
            self.basic_timer += delta_time
            self.ranged_timer += delta_time

            # Spawn BasicEnemy
            if "basic" in spawn_rates and self.basic_timer >= spawn_rates["basic"]:
                self.spawn_enemy("basic", enemies, all_wall_rects, camera_x, camera_y, 
                                 map_pixel_width, map_pixel_height)
                self.basic_timer = 0.0

            # Spawn RangedEnemy
            if "ranged" in spawn_rates and self.ranged_timer >= spawn_rates["ranged"]:
                self.spawn_enemy("ranged", enemies, all_wall_rects, camera_x, camera_y, 
                                 map_pixel_width, map_pixel_height)
                self.ranged_timer = 0.0

        # 4) Jeśli czas trwania fali został przekroczony, przechodzimy do kolejnej fali
        if time_in_wave >= wave_duration:
            self.current_wave_index += 1
            if self.current_wave_index < len(self.wave_data):
                self.wave_start_time = 0.0  # Reset, aby w następnej klatce wywołać start_wave
            # Reset timerów i flagi spawnu bossa
            self.basic_timer = 0.0
            self.ranged_timer = 0.0
            self.boss_spawned = False

        # 5) (Opcjonalnie) Można dodać logikę zakończenia gry, gdy game_time przekroczy total_game_time
        if game_time >= self.total_game_time:
            # Koniec gry – można np. ustawić jakiś stan końca gry
            pass

    def get_dt_since_last_frame(self):
        """
        Oblicza delta_time (czas między klatkami) wewnętrznie.
        Ta metoda jest pomocnicza, gdy nie przekazujemy delta_time z głównej pętli.
        
        :return: delta_time w sekundach
        """
        now = pygame.time.get_ticks() / 1000.0
        if not hasattr(self, 'last_frame_time'):
            self.last_frame_time = now
            return 0.0
        dt = now - self.last_frame_time
        self.last_frame_time = now
        return dt

    def start_wave(self, game_time, wave_info, enemies,
                   all_wall_rects, camera_x, camera_y, map_pixel_width, map_pixel_height):
        """
        Rozpoczyna nową falę, ustawiając czas rozpoczęcia oraz ewentualnie spawnując bossa.
        
        :param game_time: Aktualny czas gry (w sekundach)
        :param wave_info: Słownik z danymi o fali (czas trwania, spawn_rates, boss)
        :param enemies: Lista przeciwników – do której dodamy nowego bossa, jeśli dotyczy
        :param all_wall_rects: Lista prostokątów kolizji (używana przy generowaniu pozycji spawnu)
        :param camera_x: Pozycja kamery w osi X
        :param camera_y: Pozycja kamery w osi Y
        :param map_pixel_width: Szerokość mapy w pikselach
        :param map_pixel_height: Wysokość mapy w pikselach
        """
        self.wave_start_time = game_time
        # Jeśli fala zawiera bossa i jeszcze nie został on zspawniony
        if wave_info.get("boss", False) and not self.boss_spawned:
            x, y = self.generate_valid_spawn_position(
                camera_x, camera_y,
                map_pixel_width, map_pixel_height,
                64, 64,
                all_wall_rects
            )
            # Tworzymy obiekt bossa i dodajemy go do listy przeciwników
            boss_enemy = BossEnemy(x, y, wall_rects=all_wall_rects)
            enemies.append(boss_enemy)
            self.boss_spawned = True
            print(">>> BOSS SPAWNED <<<")
            AudioManager.play_boss_appear()
            AudioManager.fade_to_boss_music()
            
        print(f"[WaveSystem] Start fali nr {self.current_wave_index}")

    def spawn_enemy(self, enemy_type, enemies, all_wall_rects,
                    camera_x, camera_y, map_pixel_width, map_pixel_height):
        """
        Spawnuje przeciwnika określonego typu ("basic" lub "ranged") na losowej pozycji.
        
        :param enemy_type: Typ przeciwnika ("basic" lub "ranged")
        :param enemies: Lista aktualnych przeciwników, do której dodamy nowego
        :param all_wall_rects: Lista prostokątów kolizji
        :param camera_x: Pozycja kamery w osi X
        :param camera_y: Pozycja kamery w osi Y
        :param map_pixel_width: Szerokość mapy w pikselach
        :param map_pixel_height: Wysokość mapy w pikselach
        """
        x, y = self.generate_valid_spawn_position(
            camera_x, camera_y,
            map_pixel_width, map_pixel_height,
            64, 64,
            all_wall_rects
        )
        if enemy_type == "basic":
            new_enemy = Enemy(x, y, speed=2, health=50, xp_value=1)
        elif enemy_type == "ranged":
            new_enemy = RangedEnemy(x, y, speed=1.5, health=40, xp_value=3)
        else:
            new_enemy = Enemy(x, y, speed=2, health=50, xp_value=1)
        enemies.append(new_enemy)
    
    def generate_spawn_position(self, camera_x, camera_y,
                                map_pixel_width, map_pixel_height,
                                entity_width, entity_height):
        """
        Generuje losową pozycję spawnu dla jednostki, wybierając losowo jedną z krawędzi widocznego obszaru.
        
        :return: Krotka (x, y) – wyznaczona pozycja spawnu
        """
        edge = random.choice(['top', 'bottom', 'left', 'right'])

        viewport_left = camera_x
        viewport_right = camera_x + self.screen_width
        viewport_top = camera_y
        viewport_bottom = camera_y + self.screen_height

        if edge == 'top':
            x = random.randint(int(viewport_left), int(viewport_right) - entity_width)
            y = viewport_top - entity_height
        elif edge == 'bottom':
            x = random.randint(int(viewport_left), int(viewport_right) - entity_width)
            y = viewport_bottom
        elif edge == 'left':
            x = viewport_left - entity_width
            y = random.randint(int(viewport_top), int(viewport_bottom) - entity_height)
        else:  # edge == 'right'
            x = viewport_right
            y = random.randint(int(viewport_top), int(viewport_bottom) - entity_height)

        # Zapewnienie, że pozycja spawnu nie wychodzi poza mapę
        x = max(0, min(x, map_pixel_width - entity_width))
        y = max(0, min(y, map_pixel_height - entity_height))
        return x, y

    def generate_valid_spawn_position(self, camera_x, camera_y,
                                      map_pixel_width, map_pixel_height,
                                      entity_width, entity_height,
                                      wall_rects, max_tries=100):
        """
        Próbuje wygenerować prawidłową (nie kolidującą) pozycję spawnu dla jednostki.
        Wykonuje do max_tries prób; gdy żadna nie jest poprawna, zwraca (0, 0).
        
        :return: Krotka (x, y) – prawidłowa pozycja spawnu
        """
        for _ in range(max_tries):
            x, y = self.generate_spawn_position(
                camera_x, camera_y,
                map_pixel_width, map_pixel_height,
                entity_width, entity_height
            )
            rect = pygame.Rect(x, y, entity_width, entity_height)
            collision = any(rect.colliderect(w) for w in wall_rects)
            if not collision:
                return x, y
        # Jeśli nie uda się znaleźć poprawnej pozycji po max_tries, zwróć (0, 0)
        return 0, 0
