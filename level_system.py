import random
import pygame
from audio_manager import AudioManager

class LevelSystem:
    def __init__(self, player, initial_points_needed=2, level_up_increment=6):
        """
        Inicjalizuje system poziomów.
        
        :param player: Obiekt gracza, którego poziom i ulepszenia będą modyfikowane.
        :param initial_points_needed: Punkty chaosu potrzebne do pierwszego awansu.
        :param level_up_increment: Wartość, o którą wzrasta liczba punktów wymaganych do kolejnego awansu.
        """
        self.player = player                  # Referencja do obiektu gracza
        self.current_level = 1                # Początkowy poziom gracza
        self.chaos_points = 0                 # Aktualna liczba punktów chaosu
        self.points_needed = initial_points_needed
        self.level_up_increment = level_up_increment
        self.in_level_up_menu = False         # Flaga informująca, czy obecnie wyświetlane jest menu ulepszeń
        self.level_up_pending = 0             # Liczba oczekujących awansów (poziomów do "odebrania")

        # Pula dostępnych ulepszeń – opcje wyboru ulepszeń przy awansie
        self.upgrade_pool = [
            {"name": "Ulepszenie broni podstawowej", "type": "weapon_upgrade", "weapon": "basic"},
            {"name": "Odblokowanie/ulepszenie broni dodatkowej 1", "type": "weapon_upgrade", "weapon": "secondary_1"},
            {"name": "Odblokowanie/ulepszenie broni dodatkowej 2", "type": "weapon_upgrade", "weapon": "secondary_2"}
        ]
        self.selected_upgrades = []           # Aktualnie wybrane (losowo) opcje ulepszeń

        # Inicjalizacja cząsteczek tła menu – efekt wizualny dla menu ulepszeń
        self.menu_particles = []
        self.initialize_menu_particles(120, 1200, 900)

        # Wczytywanie ikon dla broni – słownik, w którym kluczem jest nazwa broni
        weapon_icon_paths = {
            "basic":       "assets/images/Projectile_Default.png",
            "secondary_1": "assets/images/satellite.png",
            "secondary_2": "assets/images/explosion.png"
        }
        self.weapon_icons = {}
        for key, path in weapon_icon_paths.items():
            icon_surf = pygame.image.load(path).convert_alpha()
            icon_surf = pygame.transform.scale(icon_surf, (32, 32))
            self.weapon_icons[key] = icon_surf
        # Dodanie ikony dla ulepszenia leczenia – prosta zielona ikona
        self.weapon_icons["heal"] = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(self.weapon_icons["heal"], (0, 255, 0), (16, 16), 15)

    def get_upgrade_icon(self, upgrade):
        """
        Zwraca ikonę odpowiadającą ulepszeniu.
        
        :param upgrade: Słownik opisujący ulepszenie (klucze "type" i ewentualnie "weapon").
        :return: pygame.Surface z ikoną lub None.
        """
        if upgrade["type"] == "weapon_upgrade":
            return self.weapon_icons.get(upgrade["weapon"], None)
        elif upgrade["type"] == "heal":
            return self.weapon_icons["heal"]
        return None

    def draw_text_with_shadow(self, screen, font, text, color, shadow_color, pos):
        """
        Rysuje tekst z cieniem – najpierw rysowany jest tekst cieniowany, a potem główny.
        
        :param screen: Powierzchnia do rysowania
        :param font: Obiekt pygame.font.SysFont
        :param text: Tekst do wyświetlenia
        :param color: Kolor głównego tekstu
        :param shadow_color: Kolor cienia
        :param pos: Pozycja centralna tekstu (krotka)
        """
        offset = 2
        shadow_surf = font.render(text, True, shadow_color)
        shadow_rect = shadow_surf.get_rect(center=(pos[0] + offset, pos[1] + offset))
        screen.blit(shadow_surf, shadow_rect)
        main_surf = font.render(text, True, color)
        main_rect = main_surf.get_rect(center=pos)
        screen.blit(main_surf, main_rect)

    def initialize_menu_particles(self, num_particles, screen_width, screen_height):
        """
        Inicjalizuje cząsteczki tła, które będą animowane w menu ulepszeń.
        
        :param num_particles: Liczba cząsteczek do utworzenia.
        :param screen_width: Szerokość ekranu.
        :param screen_height: Wysokość ekranu.
        """
        for _ in range(num_particles):
            x = random.uniform(0, screen_width)
            y = random.uniform(0, screen_height)
            speed = random.uniform(0.2, 1.2)
            self.menu_particles.append({
                "x": x,
                "y": y,
                "speed": speed
            })

    def get_upgrade_text(self, upgrade):
        """
        Zwraca tekst opisujący ulepszenie, który będzie wyświetlany w menu.
        
        :param upgrade: Słownik opisujący ulepszenie.
        :return: Tekst opisowy.
        """
        if upgrade["type"] == "weapon_upgrade":
            if upgrade["weapon"] == "basic":
                return "Ulepsz Broń Podstawową"
            elif upgrade["weapon"] == "secondary_1":
                current_level = self.player.secondary_weapon_1.level
                if current_level == 0:
                    return "Odblokuj Orbitalnego Satelitę"
                else:
                    return "Ulepsz Orbitalnego Satelitę"
            elif upgrade["weapon"] == "secondary_2":
                current_level = self.player.secondary_weapon_2.level
                if current_level == 0:
                    return "Odblokuj Obszarowy Wybuch"
                else:
                    return "Ulepsz Obszarowy Wybuch"
        elif upgrade["type"] == "heal":
            return "Uleczenie gracza (+50 HP)"
        return "Nieznane ulepszenie"

    def add_chaos_points(self, points):
        """
        Dodaje punkty chaosu i sprawdza, czy gracz awansował.
        Jeśli zgromadzona liczba punktów przekroczy próg, gracz awansuje,
        a system zwiększa licznik awansów (level_up_pending) i odtwarza dźwięk level up.
        
        :param points: Ilość punktów do dodania.
        """
        self.chaos_points += points
        while self.chaos_points >= self.points_needed:
            self.chaos_points -= self.points_needed
            self.points_needed += self.level_up_increment
            self.current_level += 1
            self.level_up_pending += 1
            print("level up sound")
            AudioManager.play_level_up()

    def handle_possible_level_up(self):
        """
        Jeśli istnieją oczekujące awanse i gracz nie jest w menu ulepszeń,
        przełącza flagę i wywołuje menu wyboru ulepszeń.
        """
        if self.level_up_pending > 0 and not self.in_level_up_menu:
            self.in_level_up_menu = True
            self.select_upgrades()

    def select_upgrades(self):
        """
        Losuje dostępne ulepszenia w oparciu o aktualne poziomy broni gracza.
        Jeśli gracz nie ma możliwości ulepszenia broni, automatycznie stosowane jest leczenie.
        Upewnia się, że dostępnych opcji jest przynajmniej 2 (opcjonalnie dodając leczenie).
        """
        available_upgrades = []
        if self.player.current_weapon.level < 6:
            available_upgrades.append({"name": "Ulepszenie broni podstawowej", "type": "weapon_upgrade", "weapon": "basic"})
        if self.player.secondary_weapon_1.level < 6:
            available_upgrades.append({"name": "Ulepszenie broni dodatkowej 1", "type": "weapon_upgrade", "weapon": "secondary_1"})
        if self.player.secondary_weapon_2.level < 6:
            available_upgrades.append({"name": "Ulepszenie broni dodatkowej 2", "type": "weapon_upgrade", "weapon": "secondary_2"})

        if not available_upgrades:
            self.apply_upgrade({"name": "Uleczenie gracza", "type": "heal"})
            self.in_level_up_menu = False
            return

        while len(available_upgrades) < 2:
            available_upgrades.append({"name": "Uleczenie gracza", "type": "heal"})

        self.selected_upgrades = random.sample(available_upgrades, min(2, len(available_upgrades)))
        self.in_level_up_menu = True

    def draw_level_up_menu(self, screen, screen_width, screen_height):
        """
        Rysuje menu wyboru ulepszeń z:
          - półprzezroczystym overlaym,
          - animowanymi cząsteczkami tła,
          - oknem z zaokrąglonymi rogami i złotą ramką,
          - cieniowanym tekstem i ikonami ulepszeń.
          
        :param screen: Powierzchnia do rysowania
        :param screen_width: Szerokość ekranu
        :param screen_height: Wysokość ekranu
        """
        # Utworzenie półprzezroczystego overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        for particle in self.menu_particles:
            pygame.draw.circle(overlay, (100, 100, 255), (int(particle["x"]), int(particle["y"])), 3)
            particle["y"] += particle["speed"]
            if particle["y"] > screen_height:
                particle["y"] = -10
                particle["x"] = random.uniform(0, screen_width)
        screen.blit(overlay, (0, 0))

        # Rysowanie okna menu
        menu_width = 600
        menu_height = 300
        menu_x = (screen_width - menu_width) // 2
        menu_y = (screen_height - menu_height) // 2
        pygame.draw.rect(screen, (50, 50, 50), (menu_x, menu_y, menu_width, menu_height), border_radius=15)
        pygame.draw.rect(screen, (255, 215, 0), (menu_x, menu_y, menu_width, menu_height), width=4, border_radius=15)

        # Rysowanie tytułu menu z cieniem
        font = pygame.font.SysFont("Arial", 36)
        title_text = "Wybierz ulepszenie:"
        title_pos = (menu_x + menu_width // 2, menu_y + 50)
        self.draw_text_with_shadow(screen, font, title_text, (255, 255, 255), (0, 0, 0), title_pos)

        # Rysowanie opcji ulepszeń (maksymalnie 2)
        start_y = menu_y + 120
        spacing = 60
        for i, upgrade in enumerate(self.selected_upgrades):
            option_text = self.get_upgrade_text(upgrade)
            line_text = f"{i+1}: {option_text}"
            row_y = start_y + i * spacing
            icon_surf = self.get_upgrade_icon(upgrade)
            if icon_surf:
                icon_rect = icon_surf.get_rect()
                margin_left = menu_x + 50
                icon_rect.left = margin_left
                icon_rect.centery = row_y
                screen.blit(icon_surf, icon_rect)
            else:
                icon_rect = pygame.Rect(menu_x + 50, row_y, 0, 0)
            font = pygame.font.SysFont("Arial", 36)
            text_surface = font.render(line_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.left = icon_rect.right + 10
            text_rect.centery = row_y
            shadow_offset = 2
            shadow_surface = font.render(line_text, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect()
            shadow_rect.center = (text_rect.centerx + shadow_offset, text_rect.centery + shadow_offset)
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)

        pygame.display.flip()

    def handle_menu_input(self, event):
        """
        Obsługuje wejście klawiatury w menu ulepszeń.
        Naciśnięcie klawisza 1 lub 2 wybiera odpowiednią opcję ulepszenia.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 and len(self.selected_upgrades) >= 1:
                self.apply_upgrade(self.selected_upgrades[0])
                self.in_level_up_menu = False
            elif event.key == pygame.K_2 and len(self.selected_upgrades) >= 2:
                self.apply_upgrade(self.selected_upgrades[1])
                self.in_level_up_menu = False

    def apply_upgrade(self, upgrade):
        """
        Aplikuje wybrane ulepszenie do gracza.
        W zależności od typu ulepszenia:
          - dla "weapon_upgrade" wywoływana jest metoda level_up odpowiedniej broni,
          - dla "heal" gracz otrzymuje dodatkowe punkty zdrowia.
        Po zastosowaniu, zmniejszana jest liczba oczekujących awansów.
        
        :param upgrade: Słownik opisujący ulepszenie.
        """
        if upgrade["type"] == "weapon_upgrade":
            if upgrade["weapon"] == "basic":
                self.player.current_weapon.level_up()
                print(f"Ulepszono broń podstawową do poziomu {self.player.current_weapon.level}")
            elif upgrade["weapon"] == "secondary_1":
                self.player.secondary_weapon_1.level_up()
                print(f"Ulepszono broń dodatkową 1 (Orbitalny Satelita) do poziomu {self.player.secondary_weapon_1.level}")
            elif upgrade["weapon"] == "secondary_2":
                self.player.secondary_weapon_2.level_up()
                print(f"Ulepszono broń dodatkową 2 do poziomu {self.player.secondary_weapon_2.level}")
        elif upgrade["type"] == "heal":
            self.player.health = min(self.player.max_health, self.player.health + 50)
            print(f"Uleczono gracza, obecne zdrowie: {self.player.health}")
        self.level_up_pending -= 1
        if self.level_up_pending > 0:
            self.select_upgrades()
        else:
            self.in_level_up_menu = False
