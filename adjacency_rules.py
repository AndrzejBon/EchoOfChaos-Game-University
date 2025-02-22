# adjacency_rules.py
#
# Słownik 'adjacency_rules' definiuje reguły sąsiedztwa dla poszczególnych typów kafelków.
# Klucz główny to nazwa kafelka, a wartość to słownik określający, jakie kafelki mogą
# znajdować się po określonych stronach (top, right, bottom, left).
#
# Przykładowo, reguła dla kafelka "wall" definiuje, że po górnej stronie mogą się pojawić
# takie kafelki jak "wall", "floor_one_wall_270", "floor_two_wall_0" oraz "floor_two_wall_270".
# Dzięki tym regułom algorytm WFC generuje mapę, w której rozmieszczenie kafelków (np. ścian i podłóg)
# jest logicznie spójne.

adjacency_rules = {
    "wall": {
        "top":    ["wall", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_270"],
        "right":  ["wall", "floor_one_wall_180", "floor_two_wall_180", "floor_two_wall_270", "floor_one_wall_90"],
        "bottom": ["wall", "floor_one_wall_90", "floor_two_wall_90", "floor_two_wall_180"],
        "left":   ["wall", "floor_one_wall_0", "floor_two_wall_0", "floor_two_wall_90"]
    },
    "floor": {
        "top":    ["floor", "floor_one_wall_0", "floor_one_wall_90", "floor_one_wall_180", "floor_two_wall_90", "floor_two_wall_180"],
        "right":  ["floor", "floor_one_wall_0", "floor_one_wall_90", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_90"],
        "bottom": ["floor", "floor_one_wall_0", "floor_one_wall_180", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_270"],
        "left":   ["floor", "floor_one_wall_90", "floor_one_wall_180", "floor_one_wall_270", "floor_two_wall_180", "floor_two_wall_270"]
    },
    "floor_one_wall_0": {
        "top":    ["floor", "floor_one_wall_0", "floor_one_wall_90", "floor_one_wall_180", "floor_two_wall_90", "floor_two_wall_180"],
        "right":  ["wall", "floor_one_wall_180", "floor_two_wall_180", "floor_two_wall_270"],
        "bottom": ["floor", "floor_one_wall_0", "floor_one_wall_180", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_270"],
        "left":   ["floor", "floor_one_wall_90", "floor_one_wall_180", "floor_one_wall_270", "floor_two_wall_180", "floor_two_wall_270"]
    },
    "floor_one_wall_90": {
        "top":    ["wall", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_270"],
        "right":  ["floor", "floor_one_wall_0", "floor_one_wall_90", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_90"],
        "bottom": ["floor", "floor_one_wall_0", "floor_one_wall_180", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_270"],
        "left":   ["wall", "floor", "floor_one_wall_90", "floor_one_wall_180", "floor_one_wall_270", "floor_two_wall_180", "floor_two_wall_270"]
    },
    "floor_one_wall_180": {
        "top":    ["floor", "floor_one_wall_0", "floor_one_wall_90", "floor_one_wall_180", "floor_two_wall_90", "floor_two_wall_180"],
        "right":  ["floor", "floor_one_wall_0", "floor_one_wall_90", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_90"],
        "bottom": ["floor", "floor_one_wall_0", "floor_one_wall_180", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_270"],
        "left":   ["wall", "floor_one_wall_0", "floor_two_wall_0", "floor_two_wall_90"]
    },
    "floor_one_wall_270": {
        "top":    ["floor", "floor_one_wall_0", "floor_one_wall_90", "floor_one_wall_180", "floor_two_wall_90", "floor_two_wall_180"],
        "right":  ["floor", "floor_one_wall_0", "floor_one_wall_90", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_90"],
        "bottom": ["wall", "floor_one_wall_90", "floor_two_wall_90", "floor_two_wall_180"],
        "left":   ["floor", "floor_one_wall_90", "floor_one_wall_180", "floor_one_wall_270", "floor_two_wall_180", "floor_two_wall_270"]
    },
    "floor_two_wall_0": {
        "top":    ["floor", "floor_one_wall_0", "floor_one_wall_90", "floor_one_wall_180", "floor_two_wall_90", "floor_two_wall_180"],
        "right":  ["wall", "floor_one_wall_180", "floor_two_wall_180", "floor_two_wall_270"],
        "bottom": ["wall", "floor_one_wall_90", "floor_two_wall_90", "floor_two_wall_180"],
        "left":   ["floor", "floor_one_wall_90", "floor_one_wall_180", "floor_one_wall_270", "floor_two_wall_180", "floor_two_wall_270"]
    },
    "floor_two_wall_90": {
        "top":    ["wall", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_270"],
        "right":  ["wall", "floor_one_wall_180", "floor_two_wall_180", "floor_two_wall_270"],
        "bottom": ["floor", "floor_one_wall_0", "floor_one_wall_180", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_270"],
        "left":   ["floor", "floor_one_wall_90", "floor_one_wall_180", "floor_one_wall_270", "floor_two_wall_180", "floor_two_wall_270"]
    },
    "floor_two_wall_180": {
        "top":    ["wall", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_270"],
        "right":  ["floor", "floor_one_wall_0", "floor_one_wall_90", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_90"],
        "bottom": ["floor", "floor_one_wall_0", "floor_one_wall_180", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_270"],
        "left":   ["wall", "floor_one_wall_0", "floor_two_wall_0", "floor_two_wall_90"]
    },
    "floor_two_wall_270": {
        "top":    ["floor", "floor_one_wall_0", "floor_one_wall_90", "floor_one_wall_180", "floor_two_wall_90", "floor_two_wall_180"],
        "right":  ["floor", "floor_one_wall_0", "floor_one_wall_90", "floor_one_wall_270", "floor_two_wall_0", "floor_two_wall_90"],
        "bottom": ["wall", "floor_one_wall_90", "floor_two_wall_90", "floor_two_wall_180"],
        "left":   ["wall", "floor_one_wall_0", "floor_two_wall_0", "floor_two_wall_90"]
    }
}
