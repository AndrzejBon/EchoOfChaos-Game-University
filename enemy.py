import pygame
import random
import math

class Enemy:
    """
    Klasa reprezentująca podstawowego przeciwnika w grze.
    Przeciwnik porusza się w stronę gracza, może zadawać obrażenia przy kolizji
    i posiada metody do przyjmowania obrażeń oraz rysowania.
    """
    def __init__(self, x, y, speed, health, xp_value=1, wall_rects=None):
        """
        Inicjalizuje przeciwnika.

        :param x: Początkowa pozycja x przeciwnika
        :param y: Początkowa pozycja y przeciwnika
        :param speed: Prędkość ruchu
        :param health: Punkty życia przeciwnika
        :param xp_value: Wartość XP przy pokonaniu (domyślnie 1)
        :param wall_rects: Opcjonalna lista prostokątów kolizji (np. ścian)
        """
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64
        self.speed = speed
        self.health = health
        self.xp_value = xp_value

        # Prostokąt kolizji, ustawiony na podstawie pozycji i rozmiaru
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # Obrażenia zadawane graczowi przy kolizji
        self.damage = 10

        # Ustawienia ataku – czas odnowienia i licznik czasu (w klatkach)
        self.attack_cooldown = 120
        self.last_attack_time = 0

        # Flaga określająca kierunek – przydatna przy obracaniu sprite'a
        self.facing_right = True

        # Wczytanie grafiki przeciwnika i skalowanie do ustalonych rozmiarów
        self.image = pygame.image.load("assets/images/Enemy_ChaotycznaBestia.png")
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        # Flaga, która wskazuje, czy przeciwnik ma zostać usunięty (np. po śmierci)
        self.to_remove = False

    def move_towards_player(self, player_x, player_y, wall_rects):
        """
        Porusza przeciwnika w kierunku gracza.

        Oblicza wektor między przeciwnikiem a graczem, normalizuje go i aktualizuje pozycję.
        Dodatkowo, obraca sprite, aby przeciwnik "patrzył" w stronę gracza.

        :param player_x: Pozycja x gracza
        :param player_y: Pozycja y gracza
        :param wall_rects: Lista prostokątów kolizji (może być None, jeśli nie jest używana)
        """
        # Zapamiętanie poprzedniej pozycji
        old_x, old_y = self.x, self.y

        # Obliczenie różnicy pozycji
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.hypot(dx, dy)
        if distance != 0:
            # Aktualizacja pozycji z uwzględnieniem prędkości i normalizacji
            self.x += self.speed * (dx / distance)
            self.y += self.speed * (dy / distance)

        # Aktualizacja prostokąta kolizji
        self.rect.topleft = (self.x, self.y)

        # Obracanie sprite'a: jeśli gracz znajduje się po lewej a przeciwnik dotąd patrzył w prawo – odwracamy
        if dx < 0 and self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
            self.facing_right = False
        elif dx > 0 and not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
            self.facing_right = True

        # Uaktualnienie prostokąta kolizji po ewentualnym obróceniu
        self.rect.topleft = (self.x, self.y)

    def take_damage(self, damage):
        """
        Odejmuje zadane obrażenia od punktów życia przeciwnika.

        :param damage: Ilość obrażeń do odjęcia
        :return: True, jeśli zdrowie spadło do zera lub poniżej (przeciwnik pokonany), False w przeciwnym wypadku.
        """
        self.health -= damage
        return self.health <= 0

    def check_collision_with_player(self, player, current_time):
        """
        Sprawdza, czy przeciwnik koliduje z graczem.
        Jeśli nastąpi kolizja i upłynął wymagany czas od ostatniego ataku, przeciwnik zadaje obrażenia.

        :param player: Obiekt gracza
        :param current_time: Aktualny czas (np. liczba klatek), wykorzystywany do kontroli cooldownu ataku
        """
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        if self.rect.colliderect(player_rect):
            if current_time - self.last_attack_time >= self.attack_cooldown:
                player.take_damage(self.damage)
                self.last_attack_time = current_time

    def draw(self, screen, camera_x, camera_y):
        """
        Rysuje przeciwnika na ekranie z uwzględnieniem przesunięcia kamery.

        :param screen: Powierzchnia do rysowania (pygame.Surface)
        :param camera_x: Przesunięcie kamery w osi x (w pikselach)
        :param camera_y: Przesunięcie kamery w osi y (w pikselach)
        """
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        screen.blit(self.image, (screen_x, screen_y))
