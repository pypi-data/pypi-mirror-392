import getopt, sys, os
import sympy as sp

def read_matrix(filename: str):
    lines = []

    with open(filename, mode="r", encoding="utf-8") as file:
        lines = file.read().splitlines()
        
    return sp.Matrix([[int(num) for num in line.split()] for line in lines])


def print_help():
    print("Использование: mjnf [опции] <path/to/initial/matrix.txt>")
    print("Опции:")
    print("  -h, --help     Показать эту справку")


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