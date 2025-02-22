import pygame
import math
from audio_manager import AudioManager

class Weapon:
    """
    Klasa reprezentująca broń. Obsługuje różne tryby działania:
      - "projectile": standardowy tryb strzelania pociskami,
      - "satellite": tryb, w którym broń generuje orbitujące satelity,
      - "explosion": tryb, w którym broń wywołuje eksplozje zadające obrażenia w zasięgu.
    """
    def __init__(self, name, damage, projectile_speed, cooldown, projectile_image, mode="projectile"):
        """
        Inicjalizuje broń.

        :param name: Nazwa broni
        :param damage: Bazowe obrażenia zadawane przez broń
        :param projectile_speed: Prędkość pocisku
        :param cooldown: Czas odnowienia między strzałami (w klatkach)
        :param projectile_image: Ścieżka do obrazu pocisku (lub efektu eksplozji)
        :param mode: Tryb działania broni – "projectile", "satellite" lub "explosion"
        """
        self.name = name
        self.damage = damage
        self.projectile_speed = projectile_speed
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.projectiles = []            # Lista aktywnych pocisków (dla trybu "projectile")
        self.level = 0                   # Poziom broni (domyślnie 0 – broń nieaktywna)
        self.mode = mode                 # Tryb działania broni
        self.damaged_enemies = set()     # W trybie satelitów – przeciwnicy, którzy już zostali uszkodzeni
        self.was_updated_this_frame = False  # Flaga pomocnicza (można wykorzystać przy synchronizacji aktualizacji)

        # Wczytujemy obraz pocisku; na potrzeby różnych trybów obraz ten może być później przeskalowany
        self.projectile_image = pygame.image.load(projectile_image)
        
        # Tryb "satellite": inicjalizacja parametrów orbity
        if self.mode == "satellite":
            self.satellites = []         # Lista kątów (w stopniach) dla satelitów
            self.max_satellites = 1      # Maksymalna liczba satelitów – może się zmieniać przy ulepszaniu
            self.radius = 100            # Promień orbity
            self.speed = 2               # Prędkość obrotu satelitów (w stopniach na aktualizację)
            self._initialize_satellites()  # Ustalenie początkowych kątów

        # Tryb "explosion": ustawienia dotyczące efektu wybuchu
        if self.mode == "explosion":
            explosion_cooldown_seconds = 15   # Cooldown wybuchu (liczba klatek lub sekund – zależy od implementacji)
            explosion_duration_seconds = 2    # Czas trwania wybuchu (w jednostkach czasu, np. klatkach)
            self.explosion_cooldown = explosion_cooldown_seconds
            self.explosion_duration = explosion_duration_seconds
            self.current_explosion_cooldown = 0
            self.explosion_radius = 100          # Promień wybuchu (obszar, w którym zadaje obrażenia)
            # Wczytujemy grafikę wybuchu i skalujemy ją według promienia
            self.explosion_image = pygame.image.load(projectile_image)
            self.explosion_image = pygame.transform.scale(self.explosion_image, (self.explosion_radius * 2, self.explosion_radius * 2))
            self.active_explosions = []          # Lista aktywnych efektów wybuchu
            print(f"Tworzenie broni wybuchowej: cooldown={self.explosion_cooldown}, damage={self.damage}")
        else:
            # Dla trybów innych niż "explosion"
            self.active_explosions = []
            self.explosion_image = None

        # Tryb "projectile": ustawienie obrazu pocisku na odpowiedni rozmiar
        if self.mode == "projectile":
            self.projectile_image = pygame.transform.scale(self.projectile_image, (17, 32))
        else:
            # W trybach "satellite" i "explosion" można wykorzystać inny rozmiar lub pozostawić domyślny
            pass

    def _initialize_satellites(self):
        """
        Inicjalizuje listę satelitów, ustawiając równomiernie rozmieszczone kąty startowe.
        """
        self.satellites = []
        for i in range(self.max_satellites):
            angle = (360 / self.max_satellites) * i
            self.satellites.append(angle)

    def trigger_explosion(self, player, enemies, level_system):
        """
        Wyzwala eksplozję w pozycji gracza, zadając obrażenia wszystkim przeciwnikom znajdującym się w zasięgu.
        Dodaje efekt wybuchu do listy aktywnych wybuchów oraz odtwarza dźwięk.
        
        :param player: Obiekt gracza (używany do określenia środka eksplozji)
        :param enemies: Lista przeciwników – sprawdzamy ich pozycje względem eksplozji
        :param level_system: Obiekt systemu poziomów – służy do przyznawania punktów za zabicie przeciwników
        """
        kills = 0
        player_center_x = player.x + player.width // 2
        player_center_y = player.y + player.height // 2
        print("1. Nowa eksplozja dodana")  # Debugowanie

        # Dodaj efekt eksplozji z timerem
        self.active_explosions.append({
            "x": player_center_x,
            "y": player_center_y,
            "timer": self.explosion_duration
        })
        AudioManager.play_explosion()
        print(f"2. Nowa eksplozja dodana: {self.active_explosions[-1]}")

        # Sprawdzanie przeciwników w promieniu eksplozji
        for enemy in list(enemies):  # Iterujemy po kopii listy, aby móc usuwać elementy
            enemy_center_x = enemy.x + enemy.width // 2
            enemy_center_y = enemy.y + enemy.height // 2
            distance = math.sqrt((enemy_center_x - player_center_x) ** 2 +
                                 (enemy_center_y - player_center_y) ** 2)
            print(f"Dystans do przeciwnika: {distance}, Promień eksplozji: {self.explosion_radius}")
            if distance <= self.explosion_radius:
                print(f"Przeciwnik w zasięgu eksplozji! Zdrowie przed: {enemy.health}")
                enemy.take_damage(self.damage)
                print(f"Zdrowie przeciwnika po eksplozji: {enemy.health}")
                if enemy.health <= 0:
                    print("Przeciwnik zniszczony przez eksplozję!")
                    enemy.to_remove = True
                    kills += 1
        level_system.add_chaos_points(kills)

    def level_up(self):
        """
        Zwiększa poziom broni i modyfikuje jej parametry w zależności od trybu działania.
        Ulepszenie może dotyczyć obrażeń, cooldownu, liczby satelitów, promienia wybuchu itp.
        """
        self.level += 1
        # Przykładowa logika ulepszania dla trybu "satellite"
        if self.mode == "satellite":
            if self.level == 1:
                self.damage = 10
                self.max_satellites = 1
                self.radius = 100
                self.speed = 2
            elif self.level == 2:
                self.damage = 15
                self.radius = 120
            elif self.level == 3:
                self.max_satellites = 2
                self._initialize_satellites()
            elif self.level == 4:
                self.damage = 20
                self.radius = 140
                self.speed = 3
            elif self.level == 5:
                self.max_satellites = 3
                self._initialize_satellites()
            elif self.level == 6:
                self.damage = 25
                self.radius = 160
                self.speed = 4

        elif self.mode == "projectile":
            if self.level == 1:
                self.damage = 20
            elif self.level == 2:
                self.damage = 35
            elif self.level == 4:
                self.damage = 50
            elif self.level == 5:
                self.cooldown = max(1, self.cooldown - 8)

        elif self.mode == "explosion":
            if self.level == 1:
                self.damage = 50
                self.explosion_radius = 160
                self.explosion_cooldown = 12
                self.explosion_duration = 1
            elif self.level == 2:
                self.damage = 75
                self.explosion_radius = 180
            elif self.level == 3:
                self.damage = 100
                self.explosion_radius = 200
                self.explosion_cooldown = 10
            elif self.level == 4:
                self.damage = 125
                self.explosion_radius = 220
            elif self.level == 5:
                self.damage = 150
                self.explosion_radius = 240
                self.explosion_cooldown = 8
            elif self.level == 6:
                self.damage = 200
                self.explosion_radius = 260
                self.explosion_cooldown = 6

            # Aktualizacja obrazu eksplozji zgodnie z nowym promieniem
            self.explosion_image = pygame.image.load("assets/images/explosion.png")
            self.explosion_image = pygame.transform.scale(
                self.explosion_image, (self.explosion_radius * 2, self.explosion_radius * 2)
            )

    def set_parameters(self, damage, max_satellites, radius, speed):
        """
        Ustawia parametry broni – przydatne przy specyficznych zmianach lub resetowaniu.
        """
        self.damage = damage
        self.max_satellites = max_satellites
        self.radius = radius
        self.speed = speed
        self._initialize_satellites()

    def shoot(self, x, y, velocity_x=0, velocity_y=-10):
        """
        W trybie "projectile" wykonuje strzał, tworząc główny pocisk i ewentualnie dodatkowe,
        obracając je o określone kąty przy wyższych poziomach.
        W trybie "satellite" metoda nie wykonuje żadnej akcji.
        
        :param x: Pozycja startowa pocisku
        :param y: Pozycja startowa pocisku
        :param velocity_x: Składowa prędkości w osi X
        :param velocity_y: Składowa prędkości w osi Y
        """
        if self.mode == "projectile" and self.current_cooldown == 0:
            # Tworzymy centralny pocisk
            central_projectile = Projectile(
                x, y, 
                self.damage, 
                self.projectile_speed, 
                self.projectile_image,
                velocity_x, 
                velocity_y
            )
            self.projectiles.append(central_projectile)
            AudioManager.play_shoot()

            # Przy poziomie >= 3 dodajemy dodatkowe pociski pod różnymi kątami
            if self.level >= 3:
                self.add_projectile_at_angle(x, y, velocity_x, velocity_y, 30)
                self.add_projectile_at_angle(x, y, velocity_x, velocity_y, -30)
            if self.level >= 6:
                self.add_projectile_at_angle(x, y, velocity_x, velocity_y, 60)
                self.add_projectile_at_angle(x, y, velocity_x, velocity_y, -60)

            self.current_cooldown = max(1, self.cooldown)

    def add_projectile_at_angle(self, x, y, vx, vy, angle_degrees):
        """
        Dodaje dodatkowy pocisk wystrzelony pod określonym kątem względem głównego kierunku.
        
        :param x: Pozycja startowa
        :param y: Pozycja startowa
        :param vx: Składowa prędkości początkowej X
        :param vy: Składowa prędkości początkowej Y
        :param angle_degrees: Kąt obrotu w stopniach
        """
        length = math.hypot(vx, vy) or 1
        nx, ny = vx / length, vy / length
        angle_radians = math.radians(angle_degrees)
        cosA = math.cos(angle_radians)
        sinA = math.sin(angle_radians)
        rx = nx * cosA - ny * sinA
        ry = nx * sinA + ny * cosA
        rx *= self.projectile_speed
        ry *= self.projectile_speed

        angled_projectile = Projectile(
            x, y, 
            self.damage, 
            self.projectile_speed, 
            self.projectile_image,
            velocity_x=rx, 
            velocity_y=ry
        )
        self.projectiles.append(angled_projectile)

    def update(self, player, enemies, screen, level_system, delta_time):
        """
        Aktualizuje stan broni w zależności od trybu:
          - W trybie "projectile" aktualizuje cooldown i pozycje pocisków.
          - W trybie "satellite" obraca satelity, sprawdza kolizje z przeciwnikami i zadaje obrażenia.
          - W trybie "explosion" zarządza wybuchami, aktualizując cooldown oraz wyświetlając efekty.
        
        :param player: Obiekt gracza
        :param enemies: Lista przeciwników
        :param screen: Powierzchnia do rysowania
        :param level_system: System poziomów – do przyznawania punktów
        :param delta_time: Czas między klatkami (w sekundach)
        """
        if self.mode == "projectile":
            self.update_cooldown()
            self.update_projectiles(player, screen.get_width(), screen.get_height())  # Przekazujemy rozmiar mapy w pikselach
        if self.mode == "satellite" and self.level > 0:
            AudioManager.play_satellite_loop()
            for i in range(len(self.satellites)):
                self.satellites[i] = (self.satellites[i] + self.speed) % 360
                # Resetujemy listę uszkodzonych przeciwników po pełnym obrocie
                if self.satellites[i] < self.speed:
                    self.damaged_enemies.clear()
            for enemy in enemies:
                enemy_rect = enemy.rect
                for pos in self.get_satellite_positions(player):
                    satellite_rect = pygame.Rect(pos[0], pos[1], self.projectile_image.get_width(), self.projectile_image.get_height())
                    if satellite_rect.colliderect(enemy_rect) and enemy not in self.damaged_enemies:
                        enemy.take_damage(self.damage)
                        self.damaged_enemies.add(enemy)
                        if enemy.health <= 0:
                            enemies.remove(enemy)
                            level_system.add_chaos_points(1)
        if self.mode == "explosion" and self.level > 0:
            if not hasattr(self, "explosion_updated"):
                self.explosion_updated = False
            if self.explosion_updated:
                return
            self.explosion_updated = True
            if self.current_explosion_cooldown > 0:
                self.current_explosion_cooldown -= delta_time
            else:
                self.trigger_explosion(player, enemies, level_system)
                self.current_explosion_cooldown = self.explosion_cooldown

        # Aktualizacja czasu trwania efektów wybuchu oraz ich rysowanie
        for explosion in self.active_explosions[:]:
            explosion["timer"] -= delta_time
            if explosion["timer"] <= 0:
                self.active_explosions.remove(explosion)
            else:
                screen.blit(self.explosion_image, (explosion["x"], explosion["y"]))
        print(f"Liczba aktywnych wybuchów: {len(self.active_explosions)}")

    def update_cooldown(self):
        """
        Zmniejsza licznik cooldownu dla strzału, jeśli jest aktywny.
        """
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def update_projectiles(self, map_width_px, map_height_px):
        """
        Aktualizuje pozycje pocisków i usuwa te, które wychodzą poza granice mapy.
        
        :param map_width_px: Szerokość mapy w pikselach
        :param map_height_px: Wysokość mapy w pikselach
        """
        for projectile in self.projectiles[:]:
            projectile.move()
            if (projectile.x < 0 or projectile.x > map_width_px or
                projectile.y < 0 or projectile.y > map_height_px):
                self.projectiles.remove(projectile)

    def get_satellite_positions(self, player):
        """
        Oblicza pozycje satelitów orbitujących wokół gracza.
        
        :param player: Obiekt gracza
        :return: Lista krotek (x, y) pozycji satelitów
        """
        positions = []
        for angle in self.satellites:
            rad = math.radians(angle)
            x = player.x + player.width // 2 + self.radius * math.cos(rad) - self.projectile_image.get_width() // 2
            y = player.y + player.height // 2 + self.radius * math.sin(rad) - self.projectile_image.get_height() // 2
            positions.append((x, y))
        return positions

    def draw_projectiles(self, screen, camera_x, camera_y):
        """
        Rysuje pociski (tryb "projectile") z uwzględnieniem przesunięcia kamery.
        """
        for projectile in self.projectiles:
            draw_x = projectile.x - camera_x
            draw_y = projectile.y - camera_y
            screen.blit(projectile.image, (draw_x, draw_y))

    def draw_satellites(self, screen, player, camera_x, camera_y):
        """
        Rysuje satelity (tryb "satellite") z uwzględnieniem przesunięcia kamery.
        """
        for pos in self.get_satellite_positions(player):
            x = pos[0] - camera_x
            y = pos[1] - camera_y
            screen.blit(self.projectile_image, (x, y))

    def draw_explosions(self, screen, camera_x, camera_y):
        """
        Rysuje efekty wybuchu (tryb "explosion") z uwzględnieniem przesunięcia kamery.
        """
        if self.mode == "explosion":
            for explosion in self.active_explosions:
                x = explosion["x"] - camera_x - self.explosion_image.get_width() // 2
                y = explosion["y"] - camera_y - self.explosion_image.get_height() // 2
                screen.blit(self.explosion_image, (x, y))

    def draw(self, screen, player, camera_x=0, camera_y=0):
        """
        Wybiera metodę rysowania odpowiednią dla aktualnego trybu broni.
        """
        if self.mode == "projectile":
            self.draw_projectiles(screen, camera_x, camera_y)
        elif self.mode == "satellite" and self.level > 0:
            self.draw_satellites(screen, player, camera_x, camera_y)
        elif self.mode == "explosion":
            self.draw_explosions(screen, camera_x, camera_y)

class Projectile:
    """
    Klasa reprezentująca pojedynczy pocisk wystrzelony przez broń.
    Oblicza kąt rotacji pocisku na podstawie jego prędkości.
    """
    def __init__(self, x, y, damage, speed, image, velocity_x=0, velocity_y=-10):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed
        # Inicjalizacja prostokąta kolizji na podstawie obrazu
        self.rect = pygame.Rect(x, y, image.get_width(), image.get_height())
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

        # Obliczenie kąta rotacji na podstawie prędkości
        angle = math.degrees(math.atan2(-self.velocity_y, self.velocity_x)) - 90
        self.image = pygame.transform.rotate(image, angle)
        self.rotated_rect = self.image.get_rect(center=(x, y))

    def move(self):
        """
        Przesuwa pocisk zgodnie z prędkością i aktualizuje pozycję prostokąta kolizji.
        """
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.rotated_rect.center = (self.x, self.y)

    def draw(self, screen):
        """
        Rysuje pocisk na ekranie.
        """
        screen.blit(self.image, self.rotated_rect.topleft)
