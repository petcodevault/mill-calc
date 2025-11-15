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


# ========================
#  Разрешённые ходы
# ========================

neighbors = {
    1: [2, 4, 5],
    2: [1, 3, 5],
    3: [2, 5, 6],
    4: [1, 5, 7],
    5: [1, 2, 3, 4, 6, 7, 8, 9],
    6: [3, 5, 9],
    7: [4, 5, 8],
    8: [5, 7, 9],
    9: [5, 6, 8]
}


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



# ========================
#  Генерация ходов
# ========================

def generate_moves_for_color(r, b, color, position_to_index):
    """
    r, b — кортежи позиций камней красных и чёрных (например (1,4,7))
    color — 'R' или 'B'
    Возвращает список индексов позиций, достижимых одним ходом.
    """

    moves = []

    red_set = set(r)
    black_set = set(b)

    if color == 'R':
        my_stones = red_set
        opp_stones = black_set
    else:
        my_stones = black_set
        opp_stones = red_set

    for src in my_stones:
        for dst in neighbors[src]:

            # если занято — пропустить
            if dst in red_set or dst in black_set:
                continue

            # перемещаем src → dst
            new_my = set(my_stones)
            new_my.remove(src)
            new_my.add(dst)

            # формируем новую позицию
            if color == 'R':
                new_r = tuple(sorted(new_my))
                new_b = tuple(sorted(opp_stones))
            else:
                new_r = tuple(sorted(opp_stones))
                new_b = tuple(sorted(new_my))

            pos = (new_r, new_b)

            # позиция должна существовать в словаре
            idx = position_to_index.get(pos)
            if idx is not None:
                moves.append(idx)

    return moves


# ==============================
#  Словари входящих переходов
# ==============================

def build_predecessor_maps(index_to_position, position_to_index):
    """
    Создаёт два словаря:
      - для хода красных (ключ: позиция, значение: список индексов источников);
      - для хода чёрных.
    """
    incoming_red = {idx: [] for idx in range(len(index_to_position))}
    incoming_black = {idx: [] for idx in range(len(index_to_position))}

    for idx, (r, b) in enumerate(index_to_position):
        # Ходы красных
        for next_idx in generate_moves_for_color(r, b, "R", position_to_index):
            incoming_red[next_idx].append(idx)

        # Ходы чёрных
        for next_idx in generate_moves_for_color(r, b, "B", position_to_index):
            incoming_black[next_idx].append(idx)

    return incoming_red, incoming_black


predecessor_map_red, predecessor_map_black = build_predecessor_maps(index_to_position, position_to_index)


def print_sources_for_position(index):
    """
    Показывает, из каких позиций можно попасть в указанную (раздельно по цветам).
    """
    r, b = index_to_position[index]

    print(f"\nПозиция #{index}:  Red={r}  Black={b}")

    red_sources = predecessor_map_red.get(index, [])
    black_sources = predecessor_map_black.get(index, [])

    if not red_sources and not black_sources:
        print("   В эту позицию нельзя попасть одним ходом")
        return

    if red_sources:
        print(f"   <- Красные ({len(red_sources)}):")
        for src_idx in red_sources:
            sr, sb = index_to_position[src_idx]
            print(f"      #{src_idx}: Red={sr} Black={sb}")

    if black_sources:
        print(f"   <- Чёрные ({len(black_sources)}):")
        for src_idx in black_sources:
            sr, sb = index_to_position[src_idx]
            print(f"      #{src_idx}: Red={sr} Black={sb}")



# ==============================
#  Удобная функция для проверки
# ==============================

def print_moves_for_position(index, color):
    """
    Показывает все ходы для позиции с данным индексом.
    color = 'R' или 'B'.
    """

    r, b = index_to_position[index]
    print(f"\nПозиция #{index}:  Red={r}  Black={b}")
    print(f"Ходы для {color}:")

    result = generate_moves_for_color(r, b, color, position_to_index)

    if not result:
        print("   Нет доступных ходов")
        return

    for idx in result:
        r2, b2 = index_to_position[idx]
        print(f"   -> #{idx}: Red={r2} Black={b2}")



# ==============================
#  Пример использования
# ==============================

# Проверить ходы для позиции №0 красных:
print_moves_for_position(1670, 'R')

# Проверить ходы для позиции №0 чёрных:
print_moves_for_position(1670, 'B')

# Посмотреть, из каких позиций достижима позиция:
print_sources_for_position(1670)

# Вывести первые 10 элементов словаря входящих переходов для красных:
print("\nПервые 1670 записей словаря для хода красных:")
for idx in range(min(1670, len(index_to_position))):
    print(f"#{idx}: {predecessor_map_red.get(idx, [])}")
