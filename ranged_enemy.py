import pygame
import math
import random
from enemy import Enemy
from projectile_enemy import EnemyProjectile

class RangedEnemy(Enemy):
    """
    Klasa reprezentująca przeciwnika dystansowego, który:
      - porusza się w kierunku gracza,
      - okresowo wystrzeliwuje pociski w jego stronę.
      
    Dziedziczy po klasie Enemy, więc korzysta z jej metod takich jak move_towards_player oraz
    zarządzania kolizjami.
    """
    def __init__(self, x, y, speed, health, attack_cooldown=120, xp_value=3, wall_rects=None):
        """
        Inicjalizacja przeciwnika dystansowego.
        
        :param x: Pozycja początkowa x
        :param y: Pozycja początkowa y
        :param speed: Prędkość ruchu przeciwnika
        :param health: Punkty życia przeciwnika
        :param attack_cooldown: Liczba klatek między atakami
        :param xp_value: Wartość XP przy pokonaniu przeciwnika
        :param wall_rects: Opcjonalna lista prostokątów kolizji (np. ścian)
        """
        # Wywołanie konstruktora klasy bazowej Enemy
        super().__init__(x, y, speed, health, xp_value, wall_rects)

        # Nadpisanie grafiki – wczytujemy obraz przeciwnika dystansowego
        self.image = pygame.image.load("assets/images/Enemy_Dystansowy.png")
        # Ustawienie nowych wymiarów (dostosowane do charakterystyki przeciwnika dystansowego)
        self.width = 40
        self.height = 64
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        # Ustawienia ataku dystansowego:
        self.attack_cooldown = attack_cooldown   # Ilość klatek między atakami
        self.last_attack_time = 0                # Licznik od ostatniego ataku
        self.projectiles = []                    # Lista pocisków wystrzelonych przez przeciwnika

    def update(self, player, screen_width, screen_height, wall_rects=None, map_width=0, map_height=0):
        """
        Aktualizuje przeciwnika dystansowego – wykonuje ruch w kierunku gracza oraz obsługuje atak.
        
        :param player: Obiekt gracza
        :param screen_width: Szerokość ekranu (w pikselach)
        :param screen_height: Wysokość ekranu (w pikselach)
        :param wall_rects: Lista prostokątów kolizji (opcjonalnie)
        :param map_width: Szerokość mapy (w liczbie kafelków)
        :param map_height: Wysokość mapy (w liczbie kafelków)
        """
        # Poruszanie się przeciwnika w kierunku gracza
        self.move_towards_player(player.x, player.y, wall_rects)
        # Obsługa ataku (wystrzeliwanie pocisków)
        self.handle_attack(player, screen_width, screen_height, map_width, map_height)

    def handle_attack(self, player, screen_width, screen_height, map_width, map_height):
        """
        Metoda obsługująca atak dystansowy:
          - Jeśli licznik cooldownu osiągnął 0, przeciwnik wystrzeliwuje pocisk.
          - Po wystrzeleniu resetuje licznik.
          - Aktualizuje pozycje pocisków i sprawdza ich kolizje.
        
        :param player: Obiekt gracza (do określenia kierunku strzału i wykrywania kolizji)
        :param screen_width: Szerokość ekranu
        :param screen_height: Wysokość ekranu
        :param map_width: Szerokość mapy (w liczbie kafelków)
        :param map_height: Wysokość mapy (w liczbie kafelków)
        """
        # Sprawdzenie, czy cooldown minął
        if self.last_attack_time <= 0:
            self.shoot_towards_player(player.x, player.y)
            self.last_attack_time = self.attack_cooldown
        else:
            self.last_attack_time -= 1

        # Aktualizacja pozycji pocisków przeciwnika oraz usuwanie tych, które trafiają gracza
        self.update_projectiles(player, screen_width, screen_height, map_width, map_height)

    def shoot_towards_player(self, player_x, player_y):
        """
        Wystrzeliwuje pocisk w kierunku aktualnej pozycji gracza.
        Oblicza wektor kierunku na podstawie różnicy pozycji i normalizuje go,
        aby wyznaczyć prędkość pocisku.
        
        :param player_x: Pozycja x gracza
        :param player_y: Pozycja y gracza
        """
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            distance = 1  # Zapobieganie dzieleniu przez zero
        speed = 5  # Prędkość pocisku
        vx = speed * (dx / distance)
        vy = speed * (dy / distance)

        # Początek pocisku ustawiamy na środku przeciwnika
        start_x = self.x + self.width // 2
        start_y = self.y + self.height // 2

        projectile = EnemyProjectile(start_x, start_y, vx, vy)
        self.projectiles.append(projectile)

    def update_projectiles(self, player, screen_width, screen_height, map_width, map_height):
        """
        Aktualizuje pozycje pocisków:
          - Każdy pocisk jest przesuwany zgodnie z własną prędkością.
          - Jeżeli pocisk trafia w gracza, gracz otrzymuje obrażenia, a pocisk jest usuwany.
          - Pociski wychodzące poza granice mapy są usuwane.
        
        :param player: Obiekt gracza (do wykrywania kolizji)
        :param screen_width: Szerokość ekranu (w pikselach)
        :param screen_height: Wysokość ekranu (w pikselach)
        :param map_width: Szerokość mapy (w liczbie kafelków)
        :param map_height: Wysokość mapy (w liczbie kafelków)
        """
        # Przeliczanie wymiarów mapy na piksele
        map_w_px = map_width * 64
        map_h_px = map_height * 64
        for p in self.projectiles[:]:
            p.update()
            # Sprawdzenie kolizji z graczem – jeżeli pocisk trafi gracza, usuwamy go i zadajemy obrażenia
            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
            if p.rect.colliderect(player_rect):
                player.take_damage(p.damage)
                self.projectiles.remove(p)
                continue

            # Usuwamy pocisk, gdy wyjdzie poza granice mapy
            if (p.x < 0 or p.x > map_w_px or p.y < 0 or p.y > map_h_px):
                self.projectiles.remove(p)

    def draw(self, screen, camera_x, camera_y):
        """
        Rysuje przeciwnika oraz jego pociski na ekranie, uwzględniając przesunięcie kamery.
        
        :param screen: Powierzchnia do rysowania
        :param camera_x: Przesunięcie kamery w osi X (w pikselach)
        :param camera_y: Przesunięcie kamery w osi Y (w pikselach)
        """
        # Rysujemy przeciwnika – przesuwając jego pozycję o przesunięcia kamery
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        screen.blit(self.image, (screen_x, screen_y))

        # Rysujemy wszystkie pociski przeciwnika
        for p in self.projectiles:
            p.draw(screen, camera_x, camera_y)
