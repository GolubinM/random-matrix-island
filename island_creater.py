import sys
from random import randint, choice, seed

# увеличивает глубину рекурсии для больших карт > 30x30(глубины по умолчанию хватало только на такую карту)
# для карты 100*100 потребовалось установить sys.setrecursionlimit(8500)
sys.setrecursionlimit(6500)
r = randint(0, 5000)  # для контроля(сохранения) случайно-сгенерированного острова
seed(r)

cols = range(40)  # ширина карты (массива)
rows = range(40)  # высота карты (массива)

# можно в список добавлять или убавлять 0/1 для регулирования распределения 0 и 1 [0,0,0,1,1]
list_distribution = [0, 0, 0, 1, 1]
matrix = [[choice(list_distribution) for _ in cols] for _ in rows]


def print_grid_color(matrix: list[[]] = matrix):
    """вывод матрицы с раскрашиванием воды(0) и почвы(1) и заменой 0 на "~" и 1 на "*" """
    GROUND_CLR = '\u001b[38;5;' + '106' + 'm'
    GROUND_CLR_PAD = '\u001b[48;5;' + '22' + 'm'
    OCEAN_CLR = '\u001b[38;5;' + '4' + 'm'
    OCEAN_CLR_PAD = '\u001b[48;5;' + '23' + 'm'
    RESET_COLOR = '\033[0m'

    [[print(
        (GROUND_CLR + GROUND_CLR_PAD) * (el[1]) + (OCEAN_CLR_PAD + OCEAN_CLR) * (el[1] == 0) + f"{'*':^3}" * el[
            1] + f"{'':~^3}" * (
                el[1] == 0) + RESET_COLOR,
        end="\n" * (el[0] == len(row) - 1)) for el in enumerate(row)] for row in matrix]


def print_grid(grid: list[[]], cell_width=3):
    """
    вывод матрицы с форматированием, cell_width - ширина поля одного элемента матрицы
    :param grid:
    :param cell_width:
    :return:
    """
    [[print(f"{el:>{cell_width}}", end="") for el in row + ["\n"]] for row in grid]


def create_island(matrix: list[[]] = matrix):
    """ Создает случайный остров из двумерного массива matrix, заполненного  0(вода) и 1(земля),
     засыпая озера почвой и удаляя все острова кроме самого большого"""

    def find_val_in_matrix(matrix: list[[]] = matrix, to_find: int = 1):
        """возвращает строку и столбец первого элемента == to_find в матрице matrix
           если значения в матрице нет, возвращает [-1]
        """
        try:
            found_index = [elm for row in matrix for elm in row].index(to_find)
            row = found_index // count_cols
            col = found_index % count_cols
            return [row, col]
        except ValueError:  # нет такого значения в списке
            return [-1]

    def fill_matrix(matrix=matrix, fill: int = 1, what_to_fill: int = 0):
        """ Заполняет в матрице все значения==what_to_fill значениями fill"""
        for row in range(count_rows):
            for col in range(count_cols):
                matrix[row][col] = fill if matrix[row][col] == what_to_fill else matrix[row][col]

    def put_contrast(matrix: list[[]], row: int, clmn: int, oldValue, newValue):
        """заполняем водой протоки от периметра карты внутрь, оставляя озера.
           рекурсивно проходит по всем соединенным(слева, справа, сверху, снизу)
           ячейкам матрицы с одинаковыми значениями == oldValue и меняет их на newValue)
        """
        matrix[row][clmn] = newValue
        if clmn < count_cols - 1 and matrix[row][clmn + 1] == oldValue:
            put_contrast(matrix, row, clmn + 1, oldValue, newValue)
        if row < count_rows - 1 and matrix[row + 1][clmn] == oldValue:
            put_contrast(matrix, row + 1, clmn, oldValue, newValue)
        if clmn > 0 and matrix[row][clmn - 1] == oldValue:
            put_contrast(matrix, row, clmn - 1, oldValue, newValue)
        if row > 0 and matrix[row - 1][clmn] == oldValue:
            put_contrast(matrix, row - 1, clmn, oldValue, newValue)

    def fill_row(matrix: list[[]], row: int):
        """проверяет есть ли в строке row матрицы matrix 0(океан), если есть, начинает заполнять от этой
            ячейки океан(0) соленой водой(55) по протокам и соседнему пространству == 0.
            функция нужна для отметки всего океана значениями 55, оставляет нетронутыми озера"""
        for i in range(len(matrix[row])):
            if matrix[row][i] == 0:
                put_contrast(matrix, row, i, oldValue=0, newValue=55)

    def fill_col(matrix: list[[]], col: int):
        """проверяет есть ли в колонке col матрицы matrix 0(океан), если есть, начинает заполнять от этой
         ячейки океан(0) соленой водой(55) по протокам и соседнему пространству == 0.
         функция нужна для отметки всего океана значениями 55, оставляет нетронутыми озера"""
        for row in enumerate(matrix):
            if row[1][col] == 0:
                put_contrast(matrix, row[0], col, oldValue=0, newValue=55)

    def flood_islands(islands_to_flood: list):
        """ затопляет нулями все острова из списка islands_to_floodб
         формат списка [[area_island, island_num, found_cell],[area_island, island_num, found_cell]]"""
        for flood in islands_to_flood:
            put_contrast(matrix, flood[2][0], flood[2][1], flood[1], 0)

    def crop_island(ocean_field: int = 2):
        """ ======================== CROP ===============================
        ocean_field - кол-во линий океана которое оставить от крайних точек острова до края карты
        обрезаем лишний океан, оставляя по ocean_field линии с каждой из сторон карты
        считаем индексы крайних точек острова сверху, снизу, слева, справа
        """

        def remove_lines(side: str = "left", lines_remove: int = 0):
            """удаляет строки/столбцы матрицы со стороны side в количестве lines_remove"""
            nonlocal count_rows
            nonlocal count_cols
            if side == "left":
                for row in range(count_rows):
                    matrix[row] = matrix[row][lines_remove:]
            elif side == "right":
                for row in range(count_rows):
                    matrix[row] = matrix[row][:-lines_remove]
            elif side == "up":
                for i in range(lines_remove, 0, -1):
                    matrix.pop(i)
            elif side == "bottom":
                for i in range(count_rows - 1, count_rows - 1 - lines_remove, -1):
                    matrix.pop(i)
            count_rows = len(matrix)
            count_cols = len(matrix[0])

        def add_lines(side: str = "left", lines_add: int = 0):
            """добавляет строки/столбцы матрицы со стороны side в количестве lines_remove"""
            nonlocal count_rows
            nonlocal count_cols
            if side == "left":
                for row in range(count_rows):
                    matrix[row] = [0] * lines_add + matrix[row]
            elif side == "right":
                for row in range(count_rows):
                    matrix[row] = matrix[row] + [0] * lines_add
            elif side == "up":
                for line in range(lines_add):
                    matrix.insert(0, [0] * count_cols)
            elif side == "bottom":
                for i in range(count_rows, count_rows - lines_add, -1):
                    matrix.append([0] * count_cols)
            count_rows = len(matrix)
            count_cols = len(matrix[0])

        def crop_side(side, lines):
            """определяет по значению lines удалять или добавлять линии океана, вызывает соответствующую процедуру """
            if lines < 0:
                add_lines(side, -lines)
            elif lines > 0:
                remove_lines(side, lines)

        # обрезаем лишний океан слева
        left_shore_index = min([elm.index(1) for elm in matrix if 1 in elm])
        crop_side("left", left_shore_index - ocean_field)
        # обрезаем лишний океан справа
        right_shore_index = max([(count_cols - elm[::-1].index(1) - 1) for elm in matrix if 1 in elm])
        crop_side("right", count_cols - 1 - right_shore_index - ocean_field)
        # обрезаем лишний океан сверху
        up_shore_index = [elm[0] for elm in enumerate(matrix) if 1 in elm[1]][0]
        crop_side("up", up_shore_index - ocean_field)
        # обрезаем лишний океан снизу
        btm_shore_index = [elm[0] for elm in enumerate(matrix) if 1 in elm[1]][-1]
        crop_side("bottom", (count_rows - 1) - (btm_shore_index + ocean_field))

    count_rows = len(matrix)
    count_cols = len(matrix[0])
    # заполняем контрастной водой(55) протоки от верха, права, низа, лева карты вглубь по протокам(0)
    fill_row(matrix, 0)
    fill_row(matrix, len(matrix) - 1)
    fill_col(matrix, 0)
    fill_col(matrix, len(matrix[0]) - 1)
    # засыпаем оставшиеся 0(внутренние озера) почвой(1), (просто меняем все 0 в матрице на 1)
    fill_matrix()  # - заполнит озера(0) значением по умолчанию (1)-земля
    fill_matrix(matrix, 0, 55)  # - возвращаем воде ее значение 0 - (меняем весь "контраст"(55) на "воду"(0))
    # обработка островов: составляем список островов: [[площадь острова, имя, начальные координаты(row,col)]],
    # решение: находим первую ячейку с 1(земля) в матрице, запоминаем координату и заполняем все прилегающие
    # земли сверху, снизу, слева, справа номером острова (80+).
    # ищем стартовую координату следующeго острова (1), повторяем его заполнение новым номером (81)
    # когда все острова закончатся, определяем в списке наибольший по площади остров, остальные затопляем водой(0)
    island_num = 80
    island_list = []
    while True:
        # ищем землю
        found_cell = find_val_in_matrix()
        if found_cell[0] != -1:
            put_contrast(matrix, found_cell[0], found_cell[1], 1, island_num)
            area_island = [elm for row in matrix for elm in row].count(island_num)
            # добавляем в список
            island_list.append([area_island, island_num, found_cell])
            island_num += 1
        else:
            # Нет в массиве больше ячеек с искомым значением(все острова добавлены в список)
            break
    island_list.sort(reverse=True)  # сортируем список островов по первому значению набора(площадь), по убыванию
    # затопляем нулями все острова, кроме первого в списке(большего)
    islands_to_flood = island_list[1:]
    flood_islands(islands_to_flood)
    # заполняем оставшийся остров(с индексом 0 в списке островов) почвой(вместо номера острова будет покрыт 1)
    fill_matrix(matrix, 1, island_list[0][1])
    # добавляем по краям острова 2 линии океана(если необходимо) или удаляем океан пока не останется 2 линии по бокам
    crop_island()


create_island()
cols = len(matrix[0])
rows = len(matrix)
print("\nМатрица с островом:")
print("seed=", r, "list_distribution=", list_distribution, "cols=", cols, "rows=", rows, "\n")
print(matrix)
print("\nСлучайный остров без озер:")
print("seed=", r, "list_distribution=", list_distribution, "cols=", cols, "rows=", rows, "\n")
print_grid(matrix)
print("\nРаскрашенный остров")
print("seed=", r, "list_distribution=", list_distribution, "cols=", cols, "rows=", rows, "\n")
print_grid_color(matrix)