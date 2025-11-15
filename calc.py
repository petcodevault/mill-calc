from collections import deque
from itertools import combinations

# ========================
#  Константы + линии
# ========================

A1, A2, A3 = 1, 2, 3
B1, B2, B3 = 4, 5, 6
C1, C2, C3 = 7, 8, 9

COLOR_RED = "R"
COLOR_BLACK = "B"

cell_to_label = {
    A1: "A1", A2: "A2", A3: "A3",
    B1: "B1", B2: "B2", B3: "B3",
    C1: "C1", C2: "C2", C3: "C3"
}

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
RED_FORBIDDEN   = (A1, A2, A3)
BLACK_FORBIDDEN = (C1, C2, C3)

def has_valid_mill(player, color):
    """Проверяет, что у игрока есть настоящая (не стартовая) линия."""
    s = set(player)
    base = any(all(x in s for x in line) for line in winning_lines)
    if not base:
        return False

    if color == COLOR_RED and tuple(player) == RED_FORBIDDEN:
        return False
    if color == COLOR_BLACK and tuple(player) == BLACK_FORBIDDEN:
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
    color — COLOR_RED или COLOR_BLACK
    Возвращает список индексов позиций, достижимых одним ходом.
    """

    moves = []

    red_set = set(r)
    black_set = set(b)

    if color == COLOR_RED:
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
            if color == COLOR_RED:
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


# ==================================
#  Переходы (вперёд и назад)
# ==================================

def build_transition_maps(index_to_position, position_to_index):
    """
    Возвращает кортеж словарей:
      - исходящие ходы для красных и чёрных;
      - входящие ходы (откуда пришли) для красных и чёрных.
    """
    outgoing_red = {idx: [] for idx in range(len(index_to_position))}
    outgoing_black = {idx: [] for idx in range(len(index_to_position))}
    incoming_red = {idx: [] for idx in range(len(index_to_position))}
    incoming_black = {idx: [] for idx in range(len(index_to_position))}

    for idx, (r, b) in enumerate(index_to_position):
        red_moves = generate_moves_for_color(r, b, COLOR_RED, position_to_index)
        outgoing_red[idx] = red_moves
        for next_idx in red_moves:
            incoming_red[next_idx].append(idx)

        black_moves = generate_moves_for_color(r, b, COLOR_BLACK, position_to_index)
        outgoing_black[idx] = black_moves
        for next_idx in black_moves:
            incoming_black[next_idx].append(idx)

    return outgoing_red, outgoing_black, incoming_red, incoming_black


outgoing_red, outgoing_black, predecessor_map_red, predecessor_map_black = build_transition_maps(index_to_position, position_to_index)


def print_sources_for_position(index):
    """
    Показывает, из каких позиций можно попасть в указанную (раздельно по цветам).
    """
    r, b = index_to_position[index]
    r_labels = tuple(cell_to_label[c] for c in r)
    b_labels = tuple(cell_to_label[c] for c in b)

    print(f"\nПозиция #{index}:  Red={r_labels}  Black={b_labels}")

    red_sources = predecessor_map_red.get(index, [])
    black_sources = predecessor_map_black.get(index, [])

    if not red_sources and not black_sources:
        print("   В эту позицию нельзя попасть одним ходом")
        return

    if red_sources:
        print(f"   <- Красные ({len(red_sources)}):")
        for src_idx in red_sources:
            sr = tuple(cell_to_label[c] for c in index_to_position[src_idx][0])
            sb = tuple(cell_to_label[c] for c in index_to_position[src_idx][1])
            print(f"      #{src_idx}: Red={sr} Black={sb}")

    if black_sources:
        print(f"   <- Чёрные ({len(black_sources)}):")
        for src_idx in black_sources:
            sr = tuple(cell_to_label[c] for c in index_to_position[src_idx][0])
            sb = tuple(cell_to_label[c] for c in index_to_position[src_idx][1])
            print(f"      #{src_idx}: Red={sr} Black={sb}")


def print_all_positions():
    """
    Полный вывод всех позиций и их индексов.
    """
    print("\nПолный список позиций:")
    for idx, (r, b) in enumerate(index_to_position):
        r_labels = tuple(cell_to_label[c] for c in r)
        b_labels = tuple(cell_to_label[c] for c in b)
        print(f"#{idx}: Red={r_labels}  Black={b_labels}")


# ==============================
#  Ретроградный анализ
# ==============================

def run_retrograde_analysis():
    """
    Вычисляет статусы позиций для каждого игрока, который должен ходить.
    1 = гарантированная победа, -1 = гарантированное поражение, 0 = не определено/ничья.
    """
    total = len(index_to_position)
    status = {
        COLOR_RED: [0] * total,
        COLOR_BLACK: [0] * total
    }

    remaining = {
        COLOR_RED: [len(outgoing_red[idx]) for idx in range(total)],
        COLOR_BLACK: [len(outgoing_black[idx]) for idx in range(total)]
    }

    queue = deque()

    for idx, (r, b) in enumerate(index_to_position):
        red_win = has_valid_mill(r, COLOR_RED)
        black_win = has_valid_mill(b, COLOR_BLACK)

        if red_win:
            if status[COLOR_RED][idx] == 0:
                status[COLOR_RED][idx] = 1
                queue.append((idx, COLOR_RED))
            if status[COLOR_BLACK][idx] == 0:
                status[COLOR_BLACK][idx] = -1
                queue.append((idx, COLOR_BLACK))
            continue

        if black_win:
            if status[COLOR_RED][idx] == 0:
                status[COLOR_RED][idx] = -1
                queue.append((idx, COLOR_RED))
            if status[COLOR_BLACK][idx] == 0:
                status[COLOR_BLACK][idx] = 1
                queue.append((idx, COLOR_BLACK))
            continue

        if remaining[COLOR_RED][idx] == 0 and status[COLOR_RED][idx] == 0:
            status[COLOR_RED][idx] = -1
            queue.append((idx, COLOR_RED))

        if remaining[COLOR_BLACK][idx] == 0 and status[COLOR_BLACK][idx] == 0:
            status[COLOR_BLACK][idx] = -1
            queue.append((idx, COLOR_BLACK))

    while queue:
        idx, turn = queue.popleft()
        current_status = status[turn][idx]

        if turn == COLOR_RED:
            predecessors = predecessor_map_black[idx]
            prev_turn = COLOR_BLACK
        else:
            predecessors = predecessor_map_red[idx]
            prev_turn = COLOR_RED

        for prev_idx in predecessors:
            if status[prev_turn][prev_idx] != 0:
                continue

            if current_status == -1:
                status[prev_turn][prev_idx] = 1
                queue.append((prev_idx, prev_turn))
            else:  # current_status == 1
                remaining[prev_turn][prev_idx] -= 1
                if remaining[prev_turn][prev_idx] == 0:
                    status[prev_turn][prev_idx] = -1
                    queue.append((prev_idx, prev_turn))

    return status


retro_status = run_retrograde_analysis()


def print_retrograde_summary(status_map):
    print("\nРезультаты ретроградного анализа:")
    for label, turn in (("Красные ходят", COLOR_RED), ("Чёрные ходят", COLOR_BLACK)):
        data = status_map[turn]
        wins = sum(1 for val in data if val == 1)
        losses = sum(1 for val in data if val == -1)
        draws = len(data) - wins - losses
        print(f" - {label}: победа {wins}, поражение {losses}, не определено {draws}")

    # показать по нескольку позиций
    for turn in (COLOR_RED, COLOR_BLACK):
        wins = [idx for idx, val in enumerate(status_map[turn]) if val == 1][:5]
        losses = [idx for idx, val in enumerate(status_map[turn]) if val == -1][:5]
        print(f"\nПримеры для {'красных' if turn == COLOR_RED else 'чёрных'} (ход):")
        print(f"   Победа: {wins}")
        print(f"   Поражение: {losses}")


def print_move_outcomes(index, color):
    """
    Показывает статусы всех продолжений из позиции для заданного игрока.
    """
    moves = outgoing_red if color == COLOR_RED else outgoing_black
    next_turn = COLOR_BLACK if color == COLOR_RED else COLOR_RED
    label = 'красных' if color == COLOR_RED else 'чёрных'

    r = tuple(cell_to_label[c] for c in index_to_position[index][0])
    b = tuple(cell_to_label[c] for c in index_to_position[index][1])
    print(f"\nАнализ ходов для позиции #{index} (ход {label}): Red={r} Black={b}")

    options = moves.get(index, [])
    if not options:
        print("   Ходов нет.")
        return

    best_win = []
    forced_loss = []
    undecided = []

    for target in options:
        status_next = retro_status[next_turn][target]
        tr = tuple(cell_to_label[c] for c in index_to_position[target][0])
        tb = tuple(cell_to_label[c] for c in index_to_position[target][1])
        if status_next == -1:
            best_win.append((target, tr, tb))
        elif status_next == 1:
            forced_loss.append((target, tr, tb))
        else:
            undecided.append((target, tr, tb))

    if best_win:
        print("   Гарантированная победа при ходе в:")
        for idx, tr, tb in best_win:
            print(f"      #{idx}: Red={tr} Black={tb}")

    if forced_loss:
        print("   Ходы, ведущие к поражению:")
        for idx, tr, tb in forced_loss:
            print(f"      #{idx}: Red={tr} Black={tb}")

    if undecided:
        print("   Ходы с неопределённым исходом:")
        for idx, tr, tb in undecided:
            print(f"      #{idx}: Red={tr} Black={tb}")


def show_forced_win_moves(index, color):
    """
    Если позиция выигрышна для текущего игрока, выводит ходы, сохраняющие победу.
    color — кто должен ходить в позиции index.
    """
    status_val = retro_status[color][index]
    if status_val != 1:
        print(f"\nПозиция #{index} не является гарантированной победой для {color}.")
        return

    moves = outgoing_red if color == COLOR_RED else outgoing_black
    opponent = COLOR_BLACK if color == COLOR_RED else COLOR_RED
    label = 'красных' if color == COLOR_RED else 'чёрных'

    r = tuple(cell_to_label[c] for c in index_to_position[index][0])
    b = tuple(cell_to_label[c] for c in index_to_position[index][1])
    print(f"\nПозиция #{index}: Red={r} Black={b}")
    print(f"Ходы {label}, сохраняющие форсированную победу:")

    for target in moves[index]:
        if retro_status[opponent][target] == -1:
            tr = tuple(cell_to_label[c] for c in index_to_position[target][0])
            tb = tuple(cell_to_label[c] for c in index_to_position[target][1])
            print(f"   -> #{target}: Red={tr} Black={tb}")


# ==============================
#  Удобная функция для проверки
# ==============================

def print_moves_for_position(index, color):
    """
    Показывает все ходы для позиции с данным индексом.
    color = COLOR_RED или COLOR_BLACK.
    """

    r, b = index_to_position[index]
    r_labels = tuple(cell_to_label[c] for c in r)
    b_labels = tuple(cell_to_label[c] for c in b)
    print(f"\nПозиция #{index}:  Red={r_labels}  Black={b_labels}")
    print(f"Ходы для {color}:")

    result = generate_moves_for_color(r, b, color, position_to_index)

    if not result:
        print("   Нет доступных ходов")
        return

    for idx in result:
        r2 = tuple(cell_to_label[c] for c in index_to_position[idx][0])
        b2 = tuple(cell_to_label[c] for c in index_to_position[idx][1])
        print(f"   -> #{idx}: Red={r2} Black={b2}")


def build_black_transition_rules():
    """
    Формирует список правил переходов для чёрных, исключая ходы,
    после которых красные получают форсированную победу.
    """
    rules = []

    for r, b in index_to_position:
        transitions = []
        red_set = set(r)
        black_set = set(b)

        for src in sorted(black_set):
            for dst in neighbors[src]:
                if dst in red_set or dst in black_set:
                    continue

                new_black = sorted((black_set - {src}) | {dst})
                pos = (tuple(sorted(red_set)), tuple(new_black))
                idx = position_to_index.get(pos)
                if idx is None:
                    continue

                # После хода чёрных ходят красные; пропускаем,
                # если для них позиция является гарантированной победой.
                if retro_status[COLOR_RED][idx] == 1:
                    continue

                transitions.append((cell_to_label[src], cell_to_label[dst]))

        if transitions:
            rule = {
                "red": [cell_to_label[c] for c in r],
                "black": [cell_to_label[c] for c in b],
                "transitions": sorted(transitions)
            }
            rules.append(rule)

    return rules


def print_black_transition_rules(rules):
    """
    Выводит правила переходов для чёрных в виде вызовов addRule({...}).
    """
    print("\n// Чёрные: безопасные переходы")
    for rule in rules:
        red_line = ", ".join(rule["red"])
        black_line = ", ".join(rule["black"])
        print("addRule({")
        print(f"  red: [{red_line}],")
        print(f"  black: [{black_line}],")
        print("  transitions: [")
        for src, dst in rule["transitions"]:
            print(f"    [{src}, {dst}],")
        print("  ],")
        print("});\n")


# ==============================
#  Пример использования
# ==============================

# Проверить ходы для позиции №0 красных:
#print_moves_for_position(1670, COLOR_RED)

# Проверить ходы для позиции №0 чёрных:
#print_moves_for_position(1670, COLOR_BLACK)

# Посмотреть, из каких позиций достижима позиция:
#print_sources_for_position(1670)

# Вывести первые 10 элементов словаря входящих переходов для красных:
#print("\nПервые 10 записей словаря для хода красных:")
#for idx in range(min(10, len(index_to_position))):
#    print(f"#{idx}: {predecessor_map_red.get(idx, [])}")

# Печать результатов ретроградного анализа:
print_retrograde_summary(retro_status)

# Анализ стартовой позиции (Red=(1,2,3) vs Black=(7,8,9)):
print_move_outcomes(19, COLOR_RED)
show_forced_win_moves(59, COLOR_BLACK)
show_forced_win_moves(597, COLOR_BLACK)

# Полный список ходов чёрных, которые не приводят к немедленному поражению:
black_rules = build_black_transition_rules()
print_black_transition_rules(black_rules)

# Полный вывод всех позиций:
#print_all_positions()
