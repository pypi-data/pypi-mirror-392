import getopt, sys, os
import sympy as sp


def read_matrix(filename: str):
    lines = []

    with open(filename, mode="r", encoding="utf-8") as file:
        lines = file.read().splitlines()

    return sp.Matrix([[int(num) for num in line.split()] for line in lines])


def check_matrix(A):
    if A.shape[0] != A.shape[1]:
        print("Матрица должна быть квадратной")
        print_help()
        sys.exit(1)


def print_help():
    print(
        "Программа решает 2 номер полностью и 1 номер частично, без построения лестницы"
    )
    print("Возможно допилю потом если будет не лень")
    print("Использование: mjnf [опции] <путь/до/изначальной/матрицы.txt>")
    print("Опции:")
    print("  -h, --help     Показать эту справку")
    print("Как должна выглядеть матрица в файле")
    print("1 0 1 0")
    print("5 6 7 3")
    print("-2 -4 -2 1")
    print("3 2 5 1")


def handle_cli_args():
    args = sys.argv[1:]
    options = "h"
    long_options = ["help"]

    try:
        opts, remainder = getopt.getopt(args, options, long_options)
    except getopt.error as err:
        print(str(err))

    for opt, val in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit(0)

    if len(remainder) != 1:
        print("Ошибка: требуется ровно один аргумент")
        print_help()
        sys.exit(1)

    arg = remainder[0]
    return arg


def check_filename(filename):
    if not os.path.exists(filename):
        print("Введенный файл не существует")
        print_help()
        sys.exit(1)

    if not filename.endswith(".txt"):
        print("Формат файла должен быть .txt")
        print_help()
        sys.exit(1)
