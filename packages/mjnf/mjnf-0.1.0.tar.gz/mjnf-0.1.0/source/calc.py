import sympy as sp

def calculate_B_operator(A, eigen_val):
    return A - eigen_val * sp.eye(A.shape[0])


def calculate_gk(B):
    return B.shape[0] - B.rank()


def calculate_t_k(gk_prev, gk, gk_next):
    return - gk_prev + 2*gk - gk_next


def get_info_about_kernels(B):
    gks = []
    Bpow = B
    Bpow_prev = sp.Matrix()    
    pow_ = 1
    
    while True:
        gk = calculate_gk(Bpow)
        gks.append(gk)
        
        print(f"Для степени {pow_} ГК={gk}")
        print(f"Оператор B:")
        sp.pprint(Bpow)
        
        nullspace_basis = Bpow.nullspace()
        print(f"Базис ядра:")
        sp.pprint(nullspace_basis)

        if Bpow == Bpow_prev:
            break

        Bpow_prev = Bpow
        Bpow = Bpow * B
        pow_ += 1

    return gks


def calculate_ts(gks_extended):
    ts = []

    for k in range(1, len(gks_extended) - 1):
        gk_prev = gks_extended[k-1]
        gk = gks_extended[k]
        gk_next = gks_extended[k+1]

        t = calculate_t_k(gk_prev, gk, gk_next)
        if (t > 0):
            ts.append((k, t))

    return ts


def calculate_eig_vals_and_jnf_params(A):
    for lam, ak in A.eigenvals().items():
        B = calculate_B_operator(A, lam)
        gks = get_info_about_kernels(B)
        
        gks_extended = [0] + gks + [gks[-1]]

        ts = calculate_ts(gks_extended)

        print("--------------------------------")

        gk = gks[0]

        print(f"Для СЗ {lam}: АК={ak}; ГК={gk}")
        print(f"Параметры жордановых клеток:")
        print(f"(размер клетки, количество)")
        print(ts)