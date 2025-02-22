import pygame

class TileManager:
    def __init__(self, tileset_path="assets/images/tileset.png"):
        """
        Inicjalizuje menedżera kafelków:
          - Wczytuje tileset (obraz zawierający wszystkie kafelki).
          - Zakłada, że tileset zawiera 4 bazowe kafelki umieszczone w jednym rzędzie.
            Indeksy:
              0 – wall,
              1 – floor,
              2 – floor_one_wall,
              3 – floor_two_wall.
          - Ustawia rozmiar kafelka (tutaj 64 piksele).
          - Wycina z tilesetu poszczególne kafelki oraz generuje dla nich rotacje.
        :param tileset_path: Ścieżka do obrazu tilesetu.
        """
        # Wczytanie całego tilesetu z obsługą przezroczystości
        self.tileset = pygame.image.load(tileset_path).convert_alpha()

        # Ustawienie rozmiaru kafelka – założenie: 64x64 piksele
        self.tile_size = 64

        # Lista bazowych nazw kafelków (bez rotacji)
        self.base_tiles = ["wall", "floor", "floor_one_wall", "floor_two_wall"]

        # Słownik przechowujący powierzchnie dla poszczególnych nazw kafelków,
        # np. "floor_one_wall_90", "floor_two_wall_180", lub dla "wall" i "floor" – bez sufiksu.
        self.surfaces = {}

        # Wycinanie kafelków z tilesetu oraz generowanie ich rotacji
        self._load_and_rotate_tiles()

    def _load_and_rotate_tiles(self):
        """
        Dla każdego bazowego kafelka:
          1. Wycinamy kafelek o rozmiarze tile_size x tile_size z tilesetu.
          2. Dla kafelków generujemy rotacje: 0°, 90°, 180°, 270°.
             Jeśli nazwa bazowa to "wall" lub "floor", oryginał zapisujemy bez sufiksu.
          3. Wynik zapisywany jest w słowniku self.surfaces, gdzie kluczem jest nazwa,
             np. "floor_one_wall_90" czy "floor_two_wall_270".
        """
        for i, base_name in enumerate(self.base_tiles):
            # Obliczamy współrzędne wycięcia: każdy kafelek znajduje się kolejno w rzędzie
            x = i * self.tile_size
            y = 0

            # Tworzymy powierzchnię dla danego kafelka z obsługą przezroczystości
            tile_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            tile_surf.blit(
                self.tileset,
                (0, 0),
                pygame.Rect(x, y, self.tile_size, self.tile_size)
            )

            # Dla rotacji 0° – jeżeli kafelek to "wall" lub "floor", zapisujemy oryginał bez sufiksu,
            # w przeciwnym razie zapisujemy nazwę z sufiksem "_0"
            if base_name in ["wall", "floor"]:
                name_0 = base_name
            else:
                name_0 = f"{base_name}_0"
            self.surfaces[name_0] = tile_surf

            # Rotacja 90° – obrót o 90 stopni (w Pygame obrót odbywa się przeciwnie do ruchu wskazówek zegara)
            rotated_90 = pygame.transform.rotate(tile_surf, 90)
            name_90 = f"{base_name}_90"
            self.surfaces[name_90] = rotated_90

            # Rotacja 180°
            rotated_180 = pygame.transform.rotate(tile_surf, -180)
            name_180 = f"{base_name}_180"
            self.surfaces[name_180] = rotated_180

            # Rotacja 270°
            rotated_270 = pygame.transform.rotate(tile_surf, 270)
            name_270 = f"{base_name}_270"
            self.surfaces[name_270] = rotated_270

        # Uwaga: W regułach (adjacency_rules) kafelki "floor" i "wall" są oznaczane bez sufiksu "_0".
        # Dlatego dla tych kafelków zachowujemy oryginalne nazwy.

    def get_surface(self, tile_name):
        """
        Zwraca obiekt pygame.Surface odpowiadający danemu kafelkowi.
        :param tile_name: Nazwa kafelka, np. "floor_two_wall_180"
        :return: pygame.Surface dla podanego tile_name
        """
        return self.surfaces[tile_name]

    def tile_width(self):
        """
        Zwraca szerokość kafelka.
        :return: Szerokość kafelka (w pikselach)
        """
        return self.tile_size

    def tile_height(self):
        """
        Zwraca wysokość kafelka.
        :return: Wysokość kafelka (w pikselach)
        """
        return self.tile_size

    def get_collision_rects(self, tile_name, x, y):
        """
        Zwraca listę obiektów pygame.Rect definiujących obszar kolizji dla kafelka.
        Parametry x i y określają lewy-górny róg kafelka na ekranie.
        
        Dla:
         - "wall": całość kafelka (pełny prostokąt).
         - "floor_one_wall_X": pojedynczy prostokąt odpowiadający 12 pikselom (odpowiednia krawędź).
         - "floor_two_wall_X": dwa prostokąty – np. krawędź prawa oraz dolna (lub inne, zależnie od rotacji).
         - Inne kafelki (np. "floor") – nie posiadają kolizji.
         
        :param tile_name: Nazwa kafelka, np. "wall", "floor_one_wall_90" itp.
        :param x: Pozycja x lewego-górnego rogu kafelka
        :param y: Pozycja y lewego-górnego rogu kafelka
        :return: Lista obiektów pygame.Rect definiujących obszar kolizji dla kafelka.
        """
        tile_size = self.tile_size  # Używamy zdefiniowanego rozmiaru kafelka
        collision_rects = []

        # Kafelek "wall" – pełna kolizja na całym obszarze kafelka
        if tile_name == "wall":
            collision_rects.append(pygame.Rect(x, y, tile_size, tile_size))

        # Kafelki typu "floor_one_wall" – kolizja występuje tylko na jednej krawędzi (12 pikseli)
        elif tile_name.startswith("floor_one_wall"):
            if tile_name.endswith("_0"):
                # Krawędź prawa – 12 pikseli szerokości
                collision_rects.append(pygame.Rect(x + tile_size - 12, y, 12, tile_size))
            elif tile_name.endswith("_90"):
                # Krawędź górna
                collision_rects.append(pygame.Rect(x, y, tile_size, 12))
            elif tile_name.endswith("_180"):
                # Krawędź lewa
                collision_rects.append(pygame.Rect(x, y, 12, tile_size))
            elif tile_name.endswith("_270"):
                # Krawędź dolna
                collision_rects.append(pygame.Rect(x, y + tile_size - 12, tile_size, 12))
            else:
                # Domyślnie traktujemy jako _0
                collision_rects.append(pygame.Rect(x + tile_size - 12, y, 12, tile_size))

        # Kafelki typu "floor_two_wall" – kolizja obejmuje dwie krawędzie (np. prawa i dolna)
        elif tile_name.startswith("floor_two_wall"):
            if tile_name.endswith("_0"):
                rect_right = pygame.Rect(x + tile_size - 12, y, 12, tile_size)
                rect_bottom = pygame.Rect(x, y + tile_size - 12, tile_size, 12)
                collision_rects.extend([rect_right, rect_bottom])
            elif tile_name.endswith("_90"):
                rect_top = pygame.Rect(x, y, tile_size, 12)
                rect_right = pygame.Rect(x + tile_size - 12, y, 12, tile_size)
                collision_rects.extend([rect_top, rect_right])
            elif tile_name.endswith("_180"):
                rect_top = pygame.Rect(x, y, tile_size, 12)
                rect_left = pygame.Rect(x, y, 12, tile_size)
                collision_rects.extend([rect_top, rect_left])
            elif tile_name.endswith("_270"):
                rect_bottom = pygame.Rect(x, y + tile_size - 12, tile_size, 12)
                rect_left = pygame.Rect(x, y, 12, tile_size)
                collision_rects.extend([rect_bottom, rect_left])
            else:
                # Domyślnie traktujemy jako _0
                rect_right = pygame.Rect(x + tile_size - 12, y, 12, tile_size)
                rect_bottom = pygame.Rect(x, y + tile_size - 12, tile_size, 12)
                collision_rects.extend([rect_right, rect_bottom])

        # Inne kafelki (np. "floor") – nie definiujemy kolizji
        return collision_rects
