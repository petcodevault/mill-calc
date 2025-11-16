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

# Original
# neighbors = {
#     A1: [A2, B1, B2],
#     A2: [A1, A3, B1, B2, B3],
#     A3: [A2, B2, B3],
#     B1: [A1, A2, B2, C1, C2],
#     B2: [A1, A2, A3, B1, B3, C1, C2, C3],
#     B3: [A2, A3, B2, C2, C3],
#     C1: [B1, B2, C2],
#     C2: [B1, B2, B3, C1, C3],
#     C3: [B2, B3, C2]
# }

# Classic
neighbors = {
    A1: [A2, B1, B2],
    A2: [A1, A3, B2],
    A3: [A2, B2, B3],
    B1: [A1, B2, C1],
    B2: [A1, A2, A3, B1, B3, C1, C2, C3],
    B3: [A3, B2, C3],
    C1: [B1, B2, C2],
    C2: [B2, C1, C3],
    C3: [B2, B3, C2]
}


# =====================================
#  Формирование словаря (с фильтрацией)
# =====================================

def generate_forbidden_options(stones):
    """
    Возвращает список допустимых запрещённых ходов для данного набора камней.
    None означает, что запрета нет.
    """
    options = [None]
    seen = set()
    stone_set = set(stones)
    for cur in stones:
        for prev in neighbors[cur]:
            if prev in stone_set:
                continue
            pair = (cur, prev)
            if pair not in seen:
                seen.add(pair)
                options.append(pair)
    return options


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

        red_forbidden_options = generate_forbidden_options(r)
        black_forbidden_options = generate_forbidden_options(b)

        for red_forbidden in red_forbidden_options:
            for black_forbidden in black_forbidden_options:
                state = (r, b, red_forbidden, black_forbidden)
                position_to_index[state] = idx
                index_to_position.append(state)
                idx += 1


def lookup_state_index(red_cells, black_cells, red_forbidden=None, black_forbidden=None):
    r = tuple(sorted(red_cells))
    b = tuple(sorted(black_cells))
    state = (r, b, red_forbidden, black_forbidden)
    return position_to_index.get(state)

print("Размер словаря после фильтрации:", len(position_to_index))



# ========================
#  Генерация ходов
# ========================

def generate_moves_for_color(r, b, red_forbidden, black_forbidden, color, position_to_index):
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
        forbidden_move = red_forbidden
    else:
        my_stones = black_set
        opp_stones = red_set
        forbidden_move = black_forbidden

    for src in my_stones:
        for dst in neighbors[src]:

            # если занято — пропустить
            if dst in red_set or dst in black_set:
                continue

            # запрещаем немедленно отменять предыдущий ход
            if forbidden_move and src == forbidden_move[0] and dst == forbidden_move[1]:
                continue

            # перемещаем src → dst
            new_my = set(my_stones)
            new_my.remove(src)
            new_my.add(dst)

            # формируем новую позицию
            if color == COLOR_RED:
                new_r = tuple(sorted(new_my))
                new_b = tuple(sorted(opp_stones))
                new_red_forbidden = (dst, src)
                new_black_forbidden = black_forbidden
            else:
                new_r = tuple(sorted(opp_stones))
                new_b = tuple(sorted(new_my))
                new_red_forbidden = red_forbidden
                new_black_forbidden = (dst, src)

            pos = (new_r, new_b, new_red_forbidden, new_black_forbidden)

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

    for idx, (r, b, red_forbidden, black_forbidden) in enumerate(index_to_position):
        red_moves = generate_moves_for_color(r, b, red_forbidden, black_forbidden, COLOR_RED, position_to_index)
        outgoing_red[idx] = red_moves
        for next_idx in red_moves:
            incoming_red[next_idx].append(idx)

        black_moves = generate_moves_for_color(r, b, red_forbidden, black_forbidden, COLOR_BLACK, position_to_index)
        outgoing_black[idx] = black_moves
        for next_idx in black_moves:
            incoming_black[next_idx].append(idx)

    return outgoing_red, outgoing_black, incoming_red, incoming_black


outgoing_red, outgoing_black, predecessor_map_red, predecessor_map_black = build_transition_maps(index_to_position, position_to_index)


def forbidden_to_labels(forbidden):
    if forbidden is None:
        return None
    return (cell_to_label[forbidden[0]], cell_to_label[forbidden[1]])


def format_forbidden_field(forbidden_labels):
    if forbidden_labels is None:
        return "null"
    return f"[{forbidden_labels[0]}, {forbidden_labels[1]}]"


def print_sources_for_position(index):
    """
    Показывает, из каких позиций можно попасть в указанную (раздельно по цветам).
    """
    r, b, red_forbidden, black_forbidden = index_to_position[index]
    r_labels = tuple(cell_to_label[c] for c in r)
    b_labels = tuple(cell_to_label[c] for c in b)
    red_forbidden_labels = forbidden_to_labels(red_forbidden)
    black_forbidden_labels = forbidden_to_labels(black_forbidden)

    print(f"\nПозиция #{index}:  Red={r_labels}  Black={b_labels}")
    print(f"   Запрет красных: {red_forbidden_labels}")
    print(f"   Запрет чёрных: {black_forbidden_labels}")

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
    for idx, (r, b, red_forbidden, black_forbidden) in enumerate(index_to_position):
        r_labels = tuple(cell_to_label[c] for c in r)
        b_labels = tuple(cell_to_label[c] for c in b)
        print(f"#{idx}: Red={r_labels}  Black={b_labels}  R-ban={forbidden_to_labels(red_forbidden)}  B-ban={forbidden_to_labels(black_forbidden)}")


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

    for idx, (r, b, _, _) in enumerate(index_to_position):
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

    r_tuple, b_tuple, red_forbidden, black_forbidden = index_to_position[index]
    r = tuple(cell_to_label[c] for c in r_tuple)
    b = tuple(cell_to_label[c] for c in b_tuple)
    print(f"\nАнализ ходов для позиции #{index} (ход {label}): Red={r} Black={b}")
    print(f"   Запрет красных: {forbidden_to_labels(red_forbidden)}")
    print(f"   Запрет чёрных: {forbidden_to_labels(black_forbidden)}")

    options = moves.get(index, [])
    if not options:
        print("   Ходов нет.")
        return

    best_win = []
    forced_loss = []
    undecided = []

    for target in options:
        status_next = retro_status[next_turn][target]
        target_state = index_to_position[target]
        tr = tuple(cell_to_label[c] for c in target_state[0])
        tb = tuple(cell_to_label[c] for c in target_state[1])
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

    state = index_to_position[index]
    r = tuple(cell_to_label[c] for c in state[0])
    b = tuple(cell_to_label[c] for c in state[1])
    print(f"\nПозиция #{index}: Red={r} Black={b}")
    print(f"Запрет красных: {forbidden_to_labels(state[2])}")
    print(f"Запрет чёрных: {forbidden_to_labels(state[3])}")
    print(f"Ходы {label}, сохраняющие форсированную победу:")

    for target in moves[index]:
        if retro_status[opponent][target] == -1:
            target_state = index_to_position[target]
            tr = tuple(cell_to_label[c] for c in target_state[0])
            tb = tuple(cell_to_label[c] for c in target_state[1])
            print(f"   -> #{target}: Red={tr} Black={tb}  R-ban={forbidden_to_labels(target_state[2])}  B-ban={forbidden_to_labels(target_state[3])}")


# ==============================
#  Удобная функция для проверки
# ==============================

def print_moves_for_position(index, color):
    """
    Показывает все ходы для позиции с данным индексом.
    color = COLOR_RED или COLOR_BLACK.
    """

    r, b, red_forbidden, black_forbidden = index_to_position[index]
    r_labels = tuple(cell_to_label[c] for c in r)
    b_labels = tuple(cell_to_label[c] for c in b)
    print(f"\nПозиция #{index}:  Red={r_labels}  Black={b_labels}")
    print(f"Запрет красных: {forbidden_to_labels(red_forbidden)}")
    print(f"Запрет чёрных: {forbidden_to_labels(black_forbidden)}")
    print(f"Ходы для {color}:")

    result = generate_moves_for_color(r, b, red_forbidden, black_forbidden, color, position_to_index)

    if not result:
        print("   Нет доступных ходов")
        return

    for idx in result:
        st = index_to_position[idx]
        r2 = tuple(cell_to_label[c] for c in st[0])
        b2 = tuple(cell_to_label[c] for c in st[1])
        print(f"   -> #{idx}: Red={r2} Black={b2}  R-ban={forbidden_to_labels(st[2])}  B-ban={forbidden_to_labels(st[3])}")


def build_black_transition_rules():
    """
    Формирует список правил переходов для чёрных, исключая ходы,
    после которых красные получают форсированную победу.
    """
    rules = []

    for r, b, red_forbidden, black_forbidden in index_to_position:
        transitions = []
        red_set = set(r)
        black_set = set(b)

        for src in sorted(black_set):
            for dst in neighbors[src]:
                if dst in red_set or dst in black_set:
                    continue

                if black_forbidden and src == black_forbidden[0] and dst == black_forbidden[1]:
                    continue

                new_black = sorted((black_set - {src}) | {dst})
                pos = (
                    tuple(sorted(red_set)),
                    tuple(new_black),
                    red_forbidden,
                    (dst, src)
                )
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
                "red_forbidden": forbidden_to_labels(red_forbidden),
                "black_forbidden": forbidden_to_labels(black_forbidden),
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
        print(f"  redForbidden: {format_forbidden_field(rule['red_forbidden'])},")
        print(f"  blackForbidden: {format_forbidden_field(rule['black_forbidden'])},")
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
# start_index = lookup_state_index((A1, A2, A3), (C1, C2, C3))
# if start_index is not None:
#     print_move_outcomes(start_index, COLOR_RED)

# Полный список ходов чёрных, которые не приводят к немедленному поражению:
black_rules = build_black_transition_rules()
print_black_transition_rules(black_rules)

# Полный вывод всех позиций:
#print_all_positions()
