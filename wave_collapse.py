import random
from adjacency_rules import adjacency_rules

class WaveCollapse:
    def __init__(self, width, height, all_tiles):
        """
        Inicjalizacja algorytmu WFC (Wave Function Collapse).

        :param width: Szerokość generowanej siatki (liczba komórek w poziomie)
        :param height: Wysokość generowanej siatki (liczba komórek w pionie)
        :param all_tiles: Lista wszystkich możliwych nazw kafli (np. klucze z adjacency_rules)
        """
        self.width = width
        self.height = height

        # Dla każdej komórki inicjujemy zbiór wszystkich możliwych kafli
        self.possible_tiles = [
            [set(all_tiles) for _ in range(width)]
            for _ in range(height)
        ]

        # Ustalamy wagi dla poszczególnych kafli – wpływają one na losowe wybieranie kafla
        self.tile_weights = {
            "floor": 15.0,
            "wall": 10.0,
            "floor_one_wall_0": 0.2,
            "floor_one_wall_90": 0.2,
            "floor_one_wall_180": 0.2,
            "floor_one_wall_270": 0.2,
            "floor_two_wall_0": 0.2,
            "floor_two_wall_90": 0.2,
            "floor_two_wall_180": 0.2,
            "floor_two_wall_270": 0.2
        }

        # Reguły dopuszczalnych sąsiedztw – pobieramy je z modułu adjacency_rules
        self.rules = adjacency_rules

    def _weighted_random_choice(self, candidates):
        """
        Wykonuje losowanie z listy kandydatów z uwzględnieniem wag.

        :param candidates: Lista możliwych kafli (np. ["floor", "wall", ...])
        :return: Wybrana nazwa kafla
        """
        total_weight = sum(self.tile_weights.get(tile, 1.0) for tile in candidates)
        r = random.uniform(0, total_weight)
        accum = 0.0
        for tile in candidates:
            weight = self.tile_weights.get(tile, 1.0)
            accum += weight
            if r <= accum:
                return tile
        # Zabezpieczenie – powinno się nigdy nie zdarzyć
        return candidates[-1]

    def collapse(self):
        """
        Główna metoda wykonująca algorytm WFC.
        Dopóki istnieje komórka z więcej niż jedną możliwością, wybieramy taką
        o najmniejszej liczbie opcji (najniższa entropia), losujemy kafel i propagujemy
        ograniczenia do sąsiadów.

        :return: Dwuwymiarowa lista (mapa) z wybranymi kaflami
        """
        while True:
            row, col = self._find_lowest_entropy_cell()
            if row is None:
                # Wszystkie komórki mają już jedną możliwość
                break

            # Losujemy kafel dla wybranej komórki przy użyciu ważonego wyboru
            chosen_tile = self._weighted_random_choice(list(self.possible_tiles[row][col]))
            # Ustawiamy, że w tej komórce możliwy jest tylko wybrany kafel
            self.possible_tiles[row][col] = {chosen_tile}

            # Propagujemy ograniczenia na sąsiednie komórki
            self._propagate_constraints(row, col, chosen_tile)

        # Po zakończeniu algorytmu każda komórka ma dokładnie jedną możliwość;
        # budujemy finalną mapę
        collapsed_map = [
            [list(self.possible_tiles[r][c])[0] for c in range(self.width)]
            for r in range(self.height)
        ]
        return collapsed_map

    def _find_lowest_entropy_cell(self):
        """
        Szuka komórki z największym ograniczeniem (liczba możliwych kafli > 1)
        o minimalnej liczbie możliwości (najmniejsza entropia).

        :return: Krotka (row, col) lub (None, None) gdy wszystkie komórki mają tylko jedną możliwość.
        """
        min_count = float('inf')
        chosen = (None, None)
        for r in range(self.height):
            for c in range(self.width):
                count = len(self.possible_tiles[r][c])
                if 1 < count < min_count:
                    min_count = count
                    chosen = (r, c)
        return chosen if min_count != float('inf') else (None, None)

    def _propagate_constraints(self, row, col, chosen_tile):
        """
        Propaguje ograniczenia z wybranej komórki (row, col) do jej sąsiadów.
        Dla każdej sąsiedniej komórki usuwa te kafle, które nie są kompatybilne
        z kaflem z komórki źródłowej wg reguł (side/opposite_side).
        Propagacja jest wykonywana rekurencyjnie.

        :param row: Indeks wiersza komórki źródłowej
        :param col: Indeks kolumny komórki źródłowej
        :param chosen_tile: Wybrany kafel w komórce (row, col)
        """
        stack = [(row, col)]
        while stack:
            r, c = stack.pop()
            tile_set = self.possible_tiles[r][c]
            # Przechodzimy po czterech kierunkach (góra, dół, lewo, prawo)
            for (dr, dc, side, opposite_side) in [
                (-1, 0,  "top",    "bottom"),
                (1, 0,   "bottom", "top"),
                (0, -1,  "left",   "right"),
                (0, 1,   "right",  "left")
            ]:
                nr, nc = r + dr, c + dc
                # Sprawdzamy, czy indeksy są wewnątrz mapy
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    changed = self._update_neighbor(nr, nc, tile_set, side, opposite_side)
                    if changed:
                        stack.append((nr, nc))

    def _update_neighbor(self, nr, nc, tile_set, side, opposite_side):
        """
        Aktualizuje zbiór możliwych kafli w sąsiedniej komórce (nr, nc).
        Dla każdego kafla w tile_set (źródłowym) sprawdzamy, które kafle mogą się z nim sąsiadować
        (wg reguł, po stronie 'side') i zachowujemy w sąsiedniej komórce tylko te opcje,
        które należą do zbioru dozwolonych (valid_options).

        :param nr: Indeks wiersza sąsiedniej komórki
        :param nc: Indeks kolumny sąsiedniej komórki
        :param tile_set: Zbiór kafli w komórce źródłowej
        :param side: Strona źródłowej komórki (np. "top")
        :param opposite_side: Odpowiednia strona sąsiedniej komórki (np. "bottom")
        :return: True, jeśli w zbiorze możliwych kafli sąsiedniej komórki nastąpiła zmiana
        """
        neighbor_set = self.possible_tiles[nr][nc]
        before_tiles = set(neighbor_set)  # Zapamiętujemy poprzedni stan
        valid_options = set()
        debug_details = []

        # Dla każdego kafla w tile_set pobieramy dozwolone sąsiedztwo wg reguł
        for t in tile_set:
            allowed = self.rules[t][side]
            valid_options.update(allowed)
            debug_details.append((t, allowed))

        before_count = len(neighbor_set)
        # Zachowujemy w zbiorze sąsiada jedynie te kafle, które występują w valid_options
        neighbor_set.intersection_update(valid_options)
        after_count = len(neighbor_set)

        # Jeśli zbiór sąsiada stał się pusty – zgłaszamy błąd (konflikt propagacji)
        if after_count == 0:
            print(f"[DEBUG] Komórka ({nr},{nc}) stała się pusta.")
            print(f"  Dla komórki źródłowej z kaflami: {tile_set} (strona: {side})")
            print("  Dozwolone opcje dla każdego kafla:")
            for (k, al) in debug_details:
                print(f"    {k} -> {al}")
            print(f"  Początkowy zbiór sąsiada: {before_tiles}")
            print(f"  Oczekiwane valid_options: {valid_options}")
            raise ValueError(f"Konflikt WFC w komórce {(nr, nc)}. Brak możliwych kafli.")

        return (after_count < before_count)
