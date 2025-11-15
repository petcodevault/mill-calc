from itertools import combinations

# ========================
#  Константы + линии
# ========================

A1, A2, A3 = 1, 2, 3
B1, B2, B3 = 4, 5, 6
C1, C2, C3 = 7, 8, 9

cells = [A1, A2, A3,
         B1, B2, B3,
         C1, C2, C3]

winning_lines = [
    [A1, A2, A3],
    [B1, B2, B3],
    [C1, C2, C3],
    [A1, B1, C1],
    [A2, B2, C2],
    [A3, B3, C3],
    [A1, B2, C3],
    [A3, B2, C1]
]

# Стартовые линии – НЕ считаются выигрышем
RED_FORBIDDEN   = (1,2,3)
BLACK_FORBIDDEN = (7,8,9)

def has_valid_mill(player, color):
    """Проверяет, что у игрока есть настоящая (не стартовая) линия."""
    s = set(player)
    base = any(all(x in s for x in line) for line in winning_lines)
    if not base:
        return False

    if color == "R" and tuple(player) == RED_FORBIDDEN:
        return False
    if color == "B" and tuple(player) == BLACK_FORBIDDEN:
        return False

    return True


# =====================================
#  Формирование словаря (с фильтрацией)
# =====================================

position_to_index = {}
index_to_position = []

idx = 0

for red in combinations(cells, 3):
    red_set = set(red)
    remaining = set(cells) - red_set

    for black in combinations(remaining, 3):
        black_set = set(black)

        r = tuple(sorted(red_set))
        b = tuple(sorted(black_set))

        red_m   = has_valid_mill(r, "R")
        black_m = has_valid_mill(b, "B")

        # impossible: оба выиграли
        if red_m and black_m:
            continue

        position_to_index[(r, b)] = idx
        index_to_position.append((r, b))
        idx += 1

print("Размер словаря после фильтрации:", len(position_to_index))


# ============================
#  Полный вывод всех позиций
# ============================

print("\n=== Список всех позиций ===\n")

for index, (r, b) in enumerate(index_to_position):

    red_m   = has_valid_mill(r, "R")
    black_m = has_valid_mill(b, "B")

    line = f"{index:4d}: Red={r}  Black={b}"

    if red_m and not black_m:
        line += "  -> Red wins"
    elif black_m and not red_m:
        line += "  -> Black wins"

    print(line)
