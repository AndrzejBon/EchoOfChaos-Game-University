import pygame
import sys
import random

class TitleScreen:
    """
    Ekran tytułowy z animowanym tłem (poruszające się cząsteczki) oraz przyciskami "Start" i "Wyjście".
    """
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Czcionki używane do tytułu i menu
        self.title_font = pygame.font.SysFont("Arial", 72)
        self.menu_font = pygame.font.SysFont("Arial", 40)

        # Lista cząsteczek animowanych tła
        self.background_particles = []
        self._init_background_particles(count=80)

        # Definicje przycisków – pozycje i wymiary
        self.start_button_rect = pygame.Rect(
            (screen_width // 2) - 100, (screen_height // 2) + 40, 200, 50
        )
        self.exit_button_rect = pygame.Rect(
            (screen_width // 2) - 100, (screen_height // 2) + 110, 200, 50
        )

        # Flagi sterujące stanem ekranu
        self.running = True            # Ekran jest aktywny
        self.clicked_option = None     # "start" lub "exit" – wybór użytkownika

    def _init_background_particles(self, count):
        """
        Inicjalizuje cząsteczki animowane, które będą stanowiły tło ekranu tytułowego.
        Każda cząsteczka ma losową pozycję, prędkość oraz rozmiar.
        """
        for _ in range(count):
            x = random.uniform(0, self.screen_width)
            y = random.uniform(0, self.screen_height)
            speed = random.uniform(0.3, 1.0)
            size = random.randint(2, 4)
            self.background_particles.append({"x": x, "y": y, "speed": speed, "size": size})

    def handle_event(self, event):
        """
        Obsługuje zdarzenia wejścia (kliknięcia myszy oraz naciśnięcia klawisza ESC).
        Jeżeli użytkownik kliknie przycisk "Start" lub "Wyjście", odpowiednia flaga zostanie ustawiona.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.start_button_rect.collidepoint(mouse_pos):
                self.clicked_option = "start"
                self.running = False
            elif self.exit_button_rect.collidepoint(mouse_pos):
                self.clicked_option = "exit"
                self.running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.clicked_option = "exit"
                self.running = False

    def update(self):
        """
        Aktualizuje pozycje cząsteczek tła – każda cząsteczka porusza się w dół.
        Gdy cząsteczka opuszcza dolną krawędź ekranu, jest resetowana do góry.
        """
        for p in self.background_particles:
            p["y"] += p["speed"]
            if p["y"] > self.screen_height:
                p["y"] = -5
                p["x"] = random.uniform(0, self.screen_width)

    def draw(self, screen):
        """
        Rysuje ekran tytułowy:
          - Wypełnienie tła
          - Animowane cząsteczki
          - Tytuł gry
          - Przyciski "Start" i "Wyjście" wraz z podpisami
        """
        # Tło
        screen.fill((0, 0, 50))

        # Rysowanie cząsteczek
        for p in self.background_particles:
            pygame.draw.circle(
                screen, (100, 100, 255),
                (int(p["x"]), int(p["y"])), p["size"]
            )

        # Rysowanie tytułu gry
        title_surface = self.title_font.render("Echo of Chaos", True, (255, 215, 0))
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        screen.blit(title_surface, title_rect)

        # Rysowanie przycisków
        pygame.draw.rect(screen, (200, 200, 200), self.start_button_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.exit_button_rect)

        # Rysowanie tekstu na przyciskach
        start_surf = self.menu_font.render("Start", True, (0, 0, 0))
        exit_surf  = self.menu_font.render("Wyjście", True, (0, 0, 0))

        screen.blit(start_surf, start_surf.get_rect(center=self.start_button_rect.center))
        screen.blit(exit_surf, exit_surf.get_rect(center=self.exit_button_rect.center))


class IntroScreen:
    """
    Ekran wprowadzający z efektem "typewriter" – tekst wyświetlany jest stopniowo.
    Użytkownik może nacisnąć dowolny klawisz lub kliknąć myszą, aby natychmiast zakończyć efekt.
    """
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.intro_font = pygame.font.SysFont("Arial", 30)
        self.story_text = (
            "Echo budzi się w świecie chaosu – miejscu, gdzie czas i przestrzeń przestają istnieć. \n"
            "Gdzie każda chwila to walka o przetrwanie, a każdy krok prowadzi w nieznane. \n"
            "Oświetlony bladym światłem kryształów, Echo dostrzega tylko fragmenty swojej przeszłości, \n"
            "jakby dryfujące w otchłani. Być może to kara, być może próba – lecz jedno jest pewne: \n"
            "aby uciec, musi zmierzyć się z tym światem na własnych zasadach. \n\n"
            "Serce Chaosu – starożytny artefakt, będący kluczem do rzeczywistości, \n"
            "spoczywa głęboko w wymiarze chaosu, strzeżone przez potężną istotę znaną jako Król Chaosu. \n"
            "Pokonanie go to jedyny sposób, by uwolnić się z tego koszmaru. \n\n"
            "Echo, zdeterminowany, rusza w mrok – by przetrwać, znaleźć odpowiedzi \n"
            "i powrócić do życia, które być może już dawno przestało istnieć... \n"
        )
        self.displayed_characters = 0
        self.running = True
        self.finished = False  # Czy cały tekst został już wyświetlony
        self.lines = self.story_text.split("\n")

        # Parametr kontrolujący prędkość efektu "typewriter"
        self.typewriter_speed = 12  # Co ile klatek dodawany jest nowy znak
        self.typewriter_counter = 0

    def handle_event(self, event):
        """
        Jeśli użytkownik naciśnie dowolny klawisz lub kliknie myszą, efekt jest przerywany,
        a ekran kończy się natychmiastowo.
        """
        if event.type == pygame.KEYDOWN:
            self.finished = True
            self.running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.finished = True
            self.running = False

    def update(self):
        """
        Aktualizuje stan ekranu, dodając kolejne znaki tekstu zgodnie z efektem "typewriter".
        Gdy cały tekst zostanie wyświetlony, flaga finished zostaje ustawiona.
        """
        if not self.finished:
            self.typewriter_counter += 1
            if self.typewriter_counter >= self.typewriter_speed:
                self.typewriter_counter = 0
                self.displayed_characters += 1
                if self.displayed_characters >= len(self.story_text):
                    self.finished = True
        else:
            # Możesz dodać opóźnienie przed automatycznym zakończeniem ekranu
            pass

    def draw(self, screen):
        """
        Rysuje ekran wprowadzający – wyświetla tekst do aktualnie dostępnej liczby znaków.
        Tekst jest podzielony na linie, aby uzyskać efekt wielolinijkowy.
        """
        screen.fill((10, 10, 30))
        text_to_draw = self.story_text[:self.displayed_characters]
        lines = text_to_draw.split("\n")

        # Pozycja początkowa wyświetlania tekstu
        current_y = self.screen_height // 2 - 230
        for line in lines:
            surf = self.intro_font.render(line, True, (200, 200, 255))
            rect = surf.get_rect(center=(self.screen_width // 2, current_y))
            screen.blit(surf, rect)
            current_y += 40


class BossVictoryScreen:
    """
    Ekran zwycięstwa po pokonaniu bossa. Może zawierać dodatkowe animacje, np. konfetti,
    oraz tekst gratulacyjny. Użytkownik może nacisnąć odpowiedni klawisz, aby rozpocząć restart gry.
    """
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.font = pygame.font.SysFont("Arial", 48)
        self.small_font = pygame.font.SysFont("Arial", 30)
        self.running = True

        # Inicjalizacja konfetti – lista obiektów z losowymi parametrami
        self.confetti = []
        self._init_confetti(count=80)

        self.victory_text = (
            "Gdy Król Chaosu upada, a jego kryształowa istota rozpada się w oszałamiającym błysku światła, \n"
            "Echo stoi pośród ciszy, której nie zaznał od czasu wejścia w ten wymiar. \n\n"
            "Serce Chaosu – pulsujące energią, jakby śpiewające do niego – leży przed nim. \n"
            "Echo wyciąga rękę i dotyka artefaktu, czując, jak świat wokół niego zaczyna się rozmywać. \n"
            "Obrazy przeszłości i przyszłości przelatują przed jego oczami. \n\n"
            "Kiedy chaos zanika, Echo budzi się w świecie, który zdaje się obcy, a jednak znajomy. \n"
            "Wolny, lecz zmieniony. Żaden koszmar nie jest w stanie go już złamać – przeżył to, co niemożliwe. \n\n"
            "Choć świat chaosu przepadł, Echo wie, że jego wpływ może nigdy nie zostać całkowicie wymazany... \n"
        )

    def _init_confetti(self, count):
        """
        Inicjalizuje listę konfetti – każdy element posiada losową pozycję, prędkość, kolor i rozmiar.
        """
        for _ in range(count):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            speed = random.uniform(0.1, 1.0)
            color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
            size = random.randint(4, 8)
            self.confetti.append({"x": x, "y": y, "speed": speed, "color": color, "size": size})

    def handle_event(self, event):
        """
        Obsługuje zdarzenia – naciskając klawisz R, użytkownik może zainicjować restart gry.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.running = False

    def update(self):
        """
        Aktualizuje pozycję konfetti – każda cząsteczka porusza się w dół. Gdy przekroczy dolną granicę,
        jest resetowana do góry z nową losową pozycją.
        """
        for c in self.confetti:
            c["y"] += c["speed"]
            if c["y"] > self.screen_height:
                c["x"] = random.randint(0, self.screen_width)
                c["y"] = -10

    def draw(self, screen):
        """
        Rysuje ekran zwycięstwa:
          1. Rysuje tło i konfetti.
          2. Rysuje wielolinijkowy tekst zwycięstwa.
          3. Wyświetla informację o możliwości restartu.
        """
        # Rysowanie tła i konfetti – najpierw wypełnienie tła
        screen.fill((0, 0, 0))
        for c in self.confetti:
            pygame.draw.rect(
                screen,
                c["color"],
                pygame.Rect(c["x"], c["y"], c["size"], c["size"])
            )

        # Rysowanie tekstu zwycięstwa
        lines = self.victory_text.split("\n")
        current_y = self.screen_height // 2 - 260  # pozycja początkowa tekstu
        for line in lines:
            line_surf = self.small_font.render(line, True, (255, 255, 255))
            line_rect = line_surf.get_rect(center=(self.screen_width // 2, current_y))
            screen.blit(line_surf, line_rect)
            current_y += 40

        # Rysowanie informacji o restartowaniu gry
        info_surf = self.small_font.render("[R] - zagraj ponownie", True, (200, 200, 0))
        info_rect = info_surf.get_rect(center=(self.screen_width // 2, current_y + 60))
        screen.blit(info_surf, info_rect)


class GameOverScreen:
    """
    Ekran końca gry wyświetlany po śmierci gracza. Zawiera animację pulsującego tła
    oraz instrukcje dotyczące restartu lub wyjścia z gry.
    """
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.font = pygame.font.SysFont("Arial", 60)
        self.small_font = pygame.font.SysFont("Arial", 32)
        self.running = True

        # Parametry animacji pulsacji tła
        self.pulse_value = 0
        self.pulse_direction = 1  # 1: wzrost, -1: spadek

    def handle_event(self, event):
        """
        Obsługuje zdarzenia – naciśnięcie R inicjuje restart, a ESC kończy grę.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.running = False  # Restart gry
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def update(self):
        """
        Aktualizuje wartość pulsacji, która wpływa na intensywność koloru tła.
        """
        self.pulse_value += 0.05 * self.pulse_direction
        if self.pulse_value > 100:
            self.pulse_value = 100
            self.pulse_direction = -1
        elif self.pulse_value < 0:
            self.pulse_value = 0
            self.pulse_direction = 1

    def draw(self, screen):
        """
        Rysuje ekran końca gry:
          - Tło z pulsującym czerwonym odcieniem.
          - Napis "KONIEC GRY!" oraz informacje o restartowaniu/wyjściu.
        """
        red_strength = 50 + self.pulse_value
        screen.fill((red_strength, 0, 0))

        text_surf = self.font.render("KONIEC GRY!", True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        screen.blit(text_surf, text_rect)

        info_surf = self.small_font.render("[R] - restart  |  [ESC] - wyjście", True, (255, 255, 255))
        info_rect = info_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        screen.blit(info_surf, info_rect)
