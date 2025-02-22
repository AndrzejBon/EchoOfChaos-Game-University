import pygame
import math
import random
from enemy import Enemy
from projectile_enemy import EnemyProjectile
from audio_manager import AudioManager

class BossEnemy(Enemy):
    """
    Przykładowy „Chaosowy Boss” z trzema fazami:
    1) Kontakt + fala uderzeniowa
    2) Ataki dystansowe (wachlarze pocisków)
    3) Hybryda: dynamiczne przełączanie + bullet hell
    """

    def __init__(self, x, y, wall_rects=None):
        # wywołujemy konstruktor bazowy Enemy, ale zmieniamy parametry
        self.health_base = 80000
        super().__init__(x, y,
                         speed=3.5,      # faza 1: boss porusza się szybko
                         health=self.health_base,    # duży zapas zdrowia
                         xp_value=2,   # dużo XP za pokonanie
                         wall_rects=wall_rects)

        # Zastąp domyślny sprite
        self.width = 128
        self.height = 128
        self.original_image = pygame.image.load("assets/images/boss.png")
        self.original_image = pygame.transform.scale(self.original_image, (self.width, self.height))
        self.image = self.original_image.copy()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.projectiles = []
        self.shockwave_effects = []
        self.shockwave_image = pygame.image.load("assets/images/shockwave.png")
        self.shockwave_image = pygame.transform.scale(self.shockwave_image, (250, 250))  # Dobierz rozmiar wedle potrzeb

        # fazy bossa i progi zdrowia
        self.phase = 1  # start w fazie 1
        self.phase2_threshold = 0.65  # np. przy 65% HP przechodzi w fazę 2
        self.phase3_threshold = 0.30  # przy 30% HP – faza 3
        # rejestrowanie mechanik (np. cooldown na falę uderzeniową)
        self.shockwave_cooldown = 120
        self.shockwave_timer = 0

        # parametry ataków dystansowych
        self.ranged_cooldown = 90
        self.ranged_timer = 0
        self.ranged_spread_angle = 45  # jak bardzo „rozrzuca” pociski w wachlarzu
        self.num_ranged_projectiles = 5

        # bullet-hell
        self.bullethell_timer = 0
        self.bullethell_cooldown = 60  # np. co 60 klatek strzelamy serią

        # Przykładowa konfiguracja spawnów w fazach:
        self.phase_minion_spawn_rate = {
            1: 300,  # co 300 klatek w fazie 1
            2: 120,  # co 120 klatek w fazie 2
            3: 60    # co 60 klatek w fazie 3
        }
        self.minion_spawn_timer = 0


    def update(self, player, screen_width, screen_height, enemies, wall_rects=None, map_width=0, map_height=0):
        """
        Główna metoda bossa, wywoływana co klatkę.
        Zależnie od fazy bossa, inne zachowania.
        """
        # Najpierw sprawdź, czy należy przejść do innej fazy
        self.check_phase()

        if self.phase == 1:
            self.update_phase_1(player, wall_rects, map_width, map_height)
        elif self.phase == 2:
            self.update_phase_2(player)
        else:
            # faza 3 = hybryda
            self.update_phase_3(player, wall_rects, map_width, map_height)

        # Przesunięcie bossa i ewentualne kolizje
        # (Bazowy Enemy ma move_towards_player, ale tu w poszczególnych fazach
        #  możemy go wywoływać albo nie)
        self.rect.topleft = (self.x, self.y)

        # ewentualnie: self.handle_wall_collisions(wall_rects)
        # lub cokolwiek innego

        # Faza 1, 2, 3 mogą generować pociski (przechowywane w self.projectiles)
        self.update_projectiles(player, screen_width, screen_height, map_width, map_height)

        # Na końcu metody update (boss_enemy.py):
        spawn_rate = self.phase_minion_spawn_rate[self.phase]
        if spawn_rate > 0:
            if self.minion_spawn_timer <= 0:
                self.spawn_minion(enemies)
                self.minion_spawn_timer = spawn_rate
            else:
                self.minion_spawn_timer -= 1


    def check_phase(self):
        """
        Sprawdza, ile procent HP pozostało i ustawia fazę bossa.
        """
        hp_ratio = self.health / self.health_base  # bo daliśmy health=2000
        if hp_ratio <= self.phase3_threshold:
            self.phase = 3
        elif hp_ratio <= self.phase2_threshold:
            self.phase = 2
        else:
            self.phase = 1

    # -------------------------
    # FAZA 1: kontakt + fala uderzeniowa
    # -------------------------
    def update_phase_1(self, player, wall_rects, map_width, map_height):
        # poruszaj się w stronę gracza
        target_x = player.x - player.width // 2
        target_y = player.y - player.height // 2
        self.move_towards_player(target_x, target_y, None)


        # co klatkę odliczaj cooldown fali
        if self.shockwave_timer > 0:
            self.shockwave_timer -= 1
        else:
            # Jeśli boss jest blisko gracza, odpal falę
            dist = math.hypot((player.x - self.x), (player.y - self.y))
            if dist < 80:  # dowolny próg zasięgu
                self.trigger_shockwave(player, wall_rects, map_width, map_height)
                self.shockwave_timer = self.shockwave_cooldown

    def trigger_shockwave(self, player, wall_rects, map_width, map_height):
        """
        Fala uderzeniowa – zadaje obrażenia w promieniu, odpycha gracza
        (opcjonalnie).
        """
        shockwave_radius = 100
        damage = 20
        dist = math.hypot((player.x - self.x), (player.y - self.y))
        if dist < shockwave_radius:
            # Zadaj obrażenia
            player.take_damage(damage)
            AudioManager.play_shockwave()
            # Odpychanie gracza (pushback)
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.hypot(dx, dy)
            if dist != 0:
                push_strength = 160  # Siła odrzutu (dostosuj wedle potrzeb)
                self.attempt_push_player(
                    player,
                    dx, dy,
                    push_strength,# przekazujemy listę ścian i rozmiar mapy,
                    wall_rects,  # to samo, co w update Bossa
                    map_width,
                    map_height
                )

            # Dodanie graficznego efektu fali – przez kilka klatek
            effect_x = self.x + (self.width // 2) - (self.shockwave_image.get_width() // 2)
            effect_y = self.y + (self.height // 2) - (self.shockwave_image.get_height() // 2)
            self.shockwave_effects.append({
                "x": effect_x,
                "y": effect_y,
                "timer": 30  # przez 15 klatek będzie widoczna
            })

    # -------------------------
    # FAZA 2: ataki dystansowe (wachlarz pocisków)
    # -------------------------
    def update_phase_2(self, player):
        # Boss stoi w miejscu (lub wolno się porusza),
        # a jednocześnie strzela serią pocisków co X klatek
        self.speed = 1.0  # wolniejszy ruch
        # ewentualnie minimalne chodzenie w bok:
        # self.x += some_small_value

        # odlicz timer
        if self.ranged_timer > 0:
            self.ranged_timer -= 1
        else:
            # strzelaj wachlarz
            self.ranged_attack(player)
            self.ranged_timer = self.ranged_cooldown

    def ranged_attack(self, player):
        """
        Wystrzelenie kilkunastu pocisków w wachlarzu w stronę gracza.
        """
        dx = player.x - self.x
        dy = player.y - self.y
        base_angle = math.degrees(math.atan2(dy, dx))  # kierunek do gracza
        half_spread = (self.num_ranged_projectiles - 1) * self.ranged_spread_angle / 2

        for i in range(self.num_ranged_projectiles):
            angle = base_angle - half_spread + i * self.ranged_spread_angle
            self.spawn_projectile(angle)

    def spawn_projectile(self, angle_degs):
        """
        Tworzenie pocisku wroga lecącego pod kątem `angle_degs`.
        """
        speed = 6
        rad = math.radians(angle_degs)
        vx = speed * math.cos(rad)
        vy = speed * math.sin(rad)
        start_x = self.x + self.width // 2
        start_y = self.y + self.height // 2

        projectile = EnemyProjectile(start_x, start_y, vx, vy, damage=15)
        self.projectiles.append(projectile)

    # -------------------------
    # FAZA 3: hybryda
    # -------------------------
    def update_phase_3(self, player, wall_rects, map_width, map_height):
        # szybkie przełączanie – np. co 120 klatek wracamy do kontaktu,
        # potem do dystansu, generujemy bullet-hell
        # Tu jest pełna dowolność – przykład:
        self.bullethell_timer += 1
        # Naprzemiennie – co ~2 sekundy biegnij do gracza, potem strzelaj
        if (self.bullethell_timer // 120) % 2 == 0:
            # ruch kontaktowy
            self.speed = 3.0
            target_x = player.x - player.width // 2
            target_y = player.y - player.height // 2
            self.move_towards_player(target_x, target_y, None)            
        else:
            # ostrzał pocisków
            self.speed = 1.5
            if self.ranged_timer > 0:
                self.ranged_timer -= 1
            else:
                self.ranged_attack(player)
                self.ranged_timer = self.ranged_cooldown

        # ewentualnie bullet-hell = np.:
        if self.bullethell_timer % self.bullethell_cooldown == 0:
            # wystrzel serię okrężnych pocisków 360°, np. co 15°
            for angle_deg in range(0, 360, 15):
                self.spawn_projectile(angle_deg)

        # plus ewentualna fala co jakiś czas
        if self.shockwave_timer > 0:
            self.shockwave_timer -= 1
        else:
            dist = math.hypot((player.x - self.x), (player.y - self.y))
            if dist < 80:
                self.trigger_shockwave(player, wall_rects, map_width, map_height)
                self.shockwave_timer = self.shockwave_cooldown

    def update_projectiles(self, player, screen_width, screen_height, map_width, map_height):
        """
        Przesuwanie pocisków i usuwanie tych, które wyleciały poza ekran
        lub trafiły w gracza.
        """
        map_w_px = map_width * 64
        map_h_px = map_height * 64
        for p in self.projectiles[:]:
            p.update()
            # sprawdź kolizję z graczem
            if p.rect.colliderect(pygame.Rect(player.x, player.y, player.width, player.height)):
                player.take_damage(p.damage)
                self.projectiles.remove(p)
                continue

            # sprawdź wyjście poza mapę
            if (p.x < 0 or p.x > map_w_px or
                p.y < 0 or p.y > map_h_px):
                self.projectiles.remove(p)

    def draw(self, screen, camera_x, camera_y):
        """
        Specjalne rysowanie bossa i jego pocisków.
        """
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        screen.blit(self.image, (screen_x, screen_y))
        # Efekt shockwave (fala uderzeniowa)
        for effect in self.shockwave_effects[:]:
            ex = effect["x"] - camera_x
            ey = effect["y"] - camera_y
            screen.blit(self.shockwave_image, (ex, ey))
            effect["timer"] -= 1
            if effect["timer"] <= 0:
                self.shockwave_effects.remove(effect)


        # dorysuj pociski
        for p in self.projectiles:
            draw_x = p.x - camera_x
            draw_y = p.y - camera_y
            screen.blit(p.image, (draw_x, draw_y))

    def spawn_minion(self, enemies):
        # Przykładowe pozycjonowanie miniona w pobliżu bossa:
        offset_x = random.randint(-150, 150)
        offset_y = random.randint(-150, 150)
        minion_x = self.x + offset_x
        minion_y = self.y + offset_y

        # Tworzymy zwykłego Enemy (lub RangedEnemy) – do wyboru
        new_enemy = Enemy(minion_x, minion_y, speed=2, health=30, xp_value=1)
        enemies.append(new_enemy)

    def attempt_push_player(self, player, dx, dy, push_strength, wall_rects, map_width, map_height):
        """
        Odrzuca gracza w kierunku (dx, dy) o 'push_strength' pikseli,
        ale iteracyjnie (co 1 piksel), by uniknąć przenikania przez ściany.
        """
        # Upewnij się, że dx, dy nie jest wektorem (0,0):
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        # Jednostkowy kierunek
        step_x = dx / dist
        step_y = dy / dist

        # Ile "kroków" – np. push_strength pikseli:
        steps = int(push_strength)

        for _ in range(steps):
            old_x, old_y = player.x, player.y
            # Przesuwamy o 1 piksel w danym kierunku
            player.x += step_x
            player.y += step_y

            # Sprawdź kolizję ze ścianą (lub wyjście poza mapę)
            collision_rect = player.get_collision_rect()

            # Sprawdzamy granice mapy:
            map_px_w = map_width * 64
            map_px_h = map_height * 64
            out_of_bounds = (
                collision_rect.left < 0 or
                collision_rect.right > map_px_w or
                collision_rect.top < 0 or
                collision_rect.bottom > map_px_h
            )
            if out_of_bounds:
                # Cofnij ruch i przerwij
                player.x, player.y = old_x, old_y
                break

            # Sprawdzamy kolizje ze ścianami (wall_rects)
            collided = any(collision_rect.colliderect(wrect) for wrect in wall_rects)
            if collided:
                # Cofnij i przerwij
                player.x, player.y = old_x, old_y
                break
