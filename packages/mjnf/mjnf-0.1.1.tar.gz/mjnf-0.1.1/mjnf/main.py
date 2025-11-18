#!.venv/bin/python3

import sympy as sp
from source.calc import *
from source.io import *


def main():
    filename = handle_cli_args()
    check_filename(filename)

    A = read_matrix(filename)

    print("Начальная матрица А:")
    sp.pprint(A)
    print("--------------------------------")

    calculate_eig_vals_and_jnf_params(A)

    print("--------------------------------")

    P, J = A.jordan_form()

    print("Ответ:")
    print("Жорданова нормальная форма:")
    sp.pprint(J)
    print(
        "Возможная матрица перехода к жордановому базису (Данная программа не занимается ее вычислением):"
    )
    sp.pprint(P)


if __name__ == "__main__":
    main()
