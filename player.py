import pygame
from weapon import Weapon

class Player:
    """
    Klasa reprezentująca gracza.
    Obsługuje ruch, strzelanie, rysowanie gracza oraz wykrywanie kolizji.
    """
    # Stałe definiujące obszar kolizji gracza
    COLLISION_WIDTH = 38
    COLLISION_HEIGHT = 58
    OFFSET_X = 13
    OFFSET_Y = 6

    def __init__(self, x, y):
        """
        Inicjalizacja gracza.
        :param x: Początkowa pozycja x
        :param y: Początkowa pozycja y
        """
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64
        self.speed = 5
        self.health = 3000
        self.max_health = self.health

        # Wczytanie i skalowanie grafiki gracza
        self.image = pygame.image.load("assets/images/MainCharacter_Echo.png")
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        # Kierunek, w którym patrzy gracz – przydatne przy obracaniu sprite'a
        self.facing_right = True
        self.facing_direction = "up"

        # Inicjalizacja broni podstawowej
        self.current_weapon = Weapon(
            name="Podstawowa Broń",
            damage=15,
            projectile_speed=10,
            cooldown=20,
            projectile_image="assets/images/Projectile_Default.png"
        )

        # Inicjalizacja broni dodatkowych
        self.secondary_weapon_1 = Weapon(
            name="Orbitalny Satelita",
            damage=10,
            projectile_speed=0,  # W trybie "satellite" prędkość nie ma znaczenia
            cooldown=0,
            projectile_image="assets/images/satellite.png",
            mode="satellite"
        )
        self.secondary_weapon_1.level = 0  # Początkowo nieaktywna

        self.secondary_weapon_2 = Weapon(
            name="Obszarowy Wybuch",
            damage=50,  # Obrażenia wybuchu
            projectile_speed=0,  # W trybie wybuchu prędkość nie jest wykorzystywana
            cooldown=15,
            projectile_image="assets/images/explosion.png",
            mode="explosion"
        )
        self.secondary_weapon_2.level = 0  # Początkowo nieaktywna

    def get_collision_rect(self):
        """
        Zwraca prostokąt kolizji gracza przesunięty względem pozycji sprite'a.
        :return: pygame.Rect określający obszar kolizji
        """
        return pygame.Rect(
            self.x + self.OFFSET_X,
            self.y + self.OFFSET_Y,
            self.COLLISION_WIDTH,
            self.COLLISION_HEIGHT
        )

    def move(self, keys, map_width, map_height, wall_rects):
        """
        Aktualizuje pozycję gracza na podstawie wciśniętych klawiszy oraz sprawdza kolizje
        z granicami mapy i przeszkodami (ścianami).
        :param keys: Słownik klawiszy (pygame.key.get_pressed())
        :param map_width: Szerokość mapy (w liczbie kafelków)
        :param map_height: Wysokość mapy (w liczbie kafelków)
        :param wall_rects: Lista prostokątów reprezentujących ściany
        """
        old_x, old_y = self.x, self.y

        # Aktualizacja pozycji na podstawie kierunków
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
            self.facing_direction = "up"
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
            self.facing_direction = "down"
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
            self.facing_direction = "left"
            # Jeśli gracz dotychczas patrzył w prawo, odbij sprite'a
            if self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
                self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            self.facing_direction = "right"
            # Jeśli gracz dotychczas patrzył w lewo, odbij sprite'a
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
                self.facing_right = True

        # Ograniczenie ruchu gracza do granic mapy
        collision_rect = self.get_collision_rect()
        max_x = map_width * 64   # Założenie: każdy kafelek ma 64 piksele
        max_y = map_height * 64

        if collision_rect.left < 0:
            self.x = -self.OFFSET_X
        if collision_rect.right > max_x:
            self.x = max_x - self.COLLISION_WIDTH - self.OFFSET_X
        if collision_rect.top < 0:
            self.y = -self.OFFSET_Y
        if collision_rect.bottom > max_y:
            self.y = max_y - self.COLLISION_HEIGHT - self.OFFSET_Y

        # Sprawdzenie kolizji ze ścianami
        collision_rect = self.get_collision_rect()
        for wall_rect in wall_rects:
            if collision_rect.colliderect(wall_rect):
                # Jeśli wystąpi kolizja, przywracamy poprzednią pozycję
                self.x, self.y = old_x, old_y
                break

    def take_damage(self, damage):
        """
        Odejmuje zadane obrażenia od zdrowia gracza.
        :param damage: Ilość obrażeń
        """
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def shoot(self):
        """
        Strzela przy użyciu broni podstawowej.
        Aktualizuje cooldown oraz ustala kierunek pocisku na podstawie
        aktualnego kierunku gracza.
        """
        self.current_weapon.update_cooldown()

        # Ustal kierunek pocisku
        if self.facing_direction == "left":
            vx, vy = -self.current_weapon.projectile_speed, 0
        elif self.facing_direction == "right":
            vx, vy = self.current_weapon.projectile_speed, 0
        elif self.facing_direction == "down":
            vx, vy = 0, self.current_weapon.projectile_speed
        else:  # Domyślnie "up"
            vx, vy = 0, -self.current_weapon.projectile_speed

        # Punkt startu pocisku – środek gracza
        start_x = self.x + self.width // 2 - 8
        start_y = self.y + self.height // 2 - 8

        self.current_weapon.shoot(start_x, start_y, velocity_x=vx, velocity_y=vy)

    def draw_health_bar(self, screen, screen_x, screen_y):
        """
        Rysuje pasek zdrowia gracza pod jego sprite'em.
        :param screen: Powierzchnia do rysowania
        :param screen_x: Pozycja x na ekranie
        :param screen_y: Pozycja y na ekranie
        """
        bar_width = 64
        bar_height = 5
        bar_x = screen_x
        bar_y = screen_y + self.height + 5
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))

    def draw(self, screen, camera_x, camera_y):
        """
        Rysuje gracza oraz jego broń na ekranie, uwzględniając przesunięcie kamery.
        :param screen: Powierzchnia do rysowania
        :param camera_x: Przesunięcie kamery w osi x
        :param camera_y: Przesunięcie kamery w osi y
        """
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        screen.blit(self.image, (screen_x, screen_y))
        self.draw_health_bar(screen, screen_x, screen_y)
        # Rysowanie broni podstawowej
        self.current_weapon.draw(screen, self, camera_x, camera_y)
        # Rysowanie broni dodatkowej 1 (np. orbitalnego satelity)
        self.secondary_weapon_1.draw(screen, self, camera_x, camera_y)
        # Aby dodać rysowanie broni dodatkowej 2, wystarczy analogicznie wywołać:
        # self.secondary_weapon_2.draw(screen, self, camera_x, camera_y)

    def update(self, keys, screen_width, screen_height, wall_rects, screen, level_system, delta_time, map_width, map_height):
        """
        Główna metoda aktualizująca gracza.
        Wykonuje ruch, strzelanie oraz aktualizację pocisków.
        :param keys: Stan klawiszy (pygame.key.get_pressed())
        :param screen_width: Szerokość ekranu
        :param screen_height: Wysokość ekranu
        :param wall_rects: Lista prostokątów kolizji ścian
        :param screen: Powierzchnia do rysowania
        :param level_system: Obiekt systemu poziomów (do ulepszania itp.)
        :param delta_time: Czas między klatkami
        :param map_width: Szerokość mapy (w liczbie kafelków)
        :param map_height: Wysokość mapy (w liczbie kafelków)
        """
        self.move(keys, map_width, map_height, wall_rects)
        self.shoot()

        # Aktualizacja pocisków broni podstawowej – przeliczamy rozmiary mapy na piksele
        self.current_weapon.update_projectiles(map_width * 64, map_height * 64)

        # Aktualizacja broni dodatkowych – jeśli chcesz, możesz odkomentować poniższe linie:
        # self.secondary_weapon_1.update(self, [], screen, level_system, delta_time)
        # self.secondary_weapon_2.update(self, [], screen, level_system, delta_time)
