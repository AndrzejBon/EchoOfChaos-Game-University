import pygame

class EnemyProjectile:
    """
    Klasa reprezentująca pocisk wroga.
    Pocisk porusza się w ustalonym kierunku (z określoną prędkością) i zadaje obrażenia graczowi,
    jeśli dojdzie do kolizji.
    """
    def __init__(self, x, y, vx, vy, damage=10):
        """
        Inicjalizuje pocisk wroga.
        
        :param x: Początkowa pozycja x pocisku (w pikselach)
        :param y: Początkowa pozycja y pocisku (w pikselach)
        :param vx: Składowa prędkości pocisku w osi X
        :param vy: Składowa prędkości pocisku w osi Y
        :param damage: Ilość obrażeń, jakie pocisk zadaje przy trafieniu (domyślnie 10)
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        
        # Ustalony rozmiar pocisku – tutaj 16x16 pikseli
        self.size = 16
        
        # Kolor pocisku – ustawiony na czerwony (można zmienić lub zastąpić grafiką)
        self.color = (255, 50, 50)
        
        # Wczytanie grafiki pocisku z podanej ścieżki
        self.image = pygame.image.load("assets/images/Ranged_Projectile.png")
        
        # Inicjalizacja prostokąta kolizji na podstawie początkowej pozycji i rozmiaru
        self.rect = pygame.Rect(x, y, self.size, self.size)

    def update(self):
        """
        Aktualizuje pozycję pocisku na podstawie prędkości.
        Pozycja pocisku jest aktualizowana, a następnie prostokąt kolizji (self.rect)
        jest synchronizowany z nową pozycją.
        """
        self.x += self.vx
        self.y += self.vy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, screen, camera_x, camera_y):
        """
        Rysuje pocisk na ekranie.
        
        :param screen: Powierzchnia, na której rysujemy (pygame.Surface)
        :param camera_x: Przesunięcie kamery w osi X (w pikselach)
        :param camera_y: Przesunięcie kamery w osi Y (w pikselach)
        """
        # Obliczamy pozycję pocisku na ekranie uwzględniając przesunięcie kamery
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        screen.blit(self.image, (draw_x, draw_y))
