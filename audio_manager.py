import pygame

class AudioManager:
    """
    Klasa AudioManager – zarządza inicjalizacją miksera Pygame,
    wczytywaniem efektów dźwiękowych i ścieżek muzycznych oraz ich odtwarzaniem.
    
    Wszystkie metody są statyczne, dzięki czemu można je wywoływać bez tworzenia instancji klasy.
    """
    _initialized = False  # Flaga zapobiegająca wielokrotnej inicjalizacji

    @staticmethod
    def init():
        """
        Inicjalizuje mikser Pygame, wczytuje efekty dźwiękowe oraz ścieżki muzyczne.
        Metodę należy wywołać raz, np. na początku gry (po pygame.init()).
        """
        # Zapobiegamy wielokrotnej inicjalizacji
        if AudioManager._initialized:
            return

        pygame.mixer.init()
        AudioManager._initialized = True

        # --------------------------------------------------
        # Wczytanie efektów dźwiękowych
        # --------------------------------------------------
        AudioManager.shoot_sfx        = pygame.mixer.Sound("assets/sounds/shoot.ogg")
        AudioManager.shoot_sfx.set_volume(0.85)

        AudioManager.explosion_sfx    = pygame.mixer.Sound("assets/sounds/explosion.ogg")
        AudioManager.explosion_sfx.set_volume(0.65)

        AudioManager.satellite_sfx    = pygame.mixer.Sound("assets/sounds/satellite_loop.ogg")
        AudioManager.player_death_sfx = pygame.mixer.Sound("assets/sounds/player_death.ogg")
        
        AudioManager.level_up_sfx     = pygame.mixer.Sound("assets/sounds/level_up.ogg")
        AudioManager.level_up_sfx.set_volume(0.6)
        
        AudioManager.shockwave_sfx    = pygame.mixer.Sound("assets/sounds/shockwave.ogg")
        AudioManager.shockwave_sfx.set_volume(0.8)
        
        AudioManager.start_game_sfx   = pygame.mixer.Sound("assets/sounds/start_game.ogg")
        AudioManager.boss_appear_sfx  = pygame.mixer.Sound("assets/sounds/boss_appear.ogg")

        # --------------------------------------------------
        # Ścieżki do muzyki
        # --------------------------------------------------
        AudioManager.normal_bgm    = "assets/sounds/bgm_normal.wav"
        AudioManager.boss_bgm      = "assets/sounds/bgm_boss.wav"
        AudioManager.gameover_bgm  = "assets/sounds/bgm_gameover.wav"

        # Flaga określająca, czy dźwięk satelity (loop) aktualnie gra
        AudioManager.satellite_playing = False

        # Opcjonalnie: można od razu wczytać i rozpocząć odtwarzanie normalnej ścieżki
        # pygame.mixer.music.load(AudioManager.normal_bgm)
        # pygame.mixer.music.play(-1)  # Odtwarzanie zapętlone

        # Odtwarzamy dźwięk startowy – informujący o rozpoczęciu gry
        AudioManager.start_game_sfx.play()

    # -------------------------------
    # Metody odtwarzania efektów dźwiękowych
    # -------------------------------

    @staticmethod
    def play_shoot():
        """Odtwarza efekt dźwiękowy strzału głównej broni."""
        AudioManager.shoot_sfx.play()

    @staticmethod
    def play_explosion():
        """Odtwarza efekt dźwiękowy wybuchu (np. broni dodatkowej)."""
        AudioManager.explosion_sfx.play()

    @staticmethod
    def play_satellite_loop():
        """
        Odtwarza pętlę dźwiękową satelity (np. efekt latania satelit).
        Dźwięk jest odtwarzany tylko, gdy nie gra aktualnie (zapobiega nakładaniu się).
        """
        if not AudioManager.satellite_playing:
            AudioManager.satellite_sfx.play(-1)  # -1 = odtwarzanie w pętli
            AudioManager.satellite_playing = True

    @staticmethod
    def stop_satellite_loop():
        """
        Zatrzymuje dźwięk satelity, jeżeli aktualnie jest odtwarzany.
        """
        if AudioManager.satellite_playing:
            AudioManager.satellite_sfx.stop()
            AudioManager.satellite_playing = False

    @staticmethod
    def play_player_death():
        """Odtwarza efekt dźwiękowy śmierci gracza."""
        AudioManager.player_death_sfx.play()

    @staticmethod
    def play_level_up():
        """Odtwarza efekt dźwiękowy przy zdobyciu nowego poziomu."""
        AudioManager.level_up_sfx.play()

    @staticmethod
    def play_shockwave():
        """Odtwarza efekt dźwiękowy fali uderzeniowej bossa."""
        AudioManager.shockwave_sfx.play()

    @staticmethod
    def play_boss_appear():
        """Odtwarza efekt dźwiękowy pojawienia się bossa."""
        AudioManager.boss_appear_sfx.play()

    # -------------------------------
    # Metody przejść między ścieżkami muzycznymi
    # -------------------------------

    @staticmethod
    def fade_to_boss_music():
        """
        Płynnie przełącza muzykę do ścieżki bossowej.
        Ładuje nową ścieżkę, ustawia głośność i odtwarza ją w pętli.
        """
        pygame.mixer.music.load(AudioManager.boss_bgm)
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)

    @staticmethod
    def fade_to_gameover_music():
        """
        Płynnie przełącza muzykę do ścieżki game over.
        Odtwarza muzykę w pętli z efektem zanikania (fade-out) trwającym 2000 ms.
        """
        pygame.mixer.music.load(AudioManager.gameover_bgm)
        pygame.mixer.music.play(-1, fade_ms=2000)
