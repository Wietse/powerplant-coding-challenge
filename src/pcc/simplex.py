import logging
import math

from .util import Plant


logger = logging.getLogger(__name__)


class EmptyFeasibleRegionError(Exception):
    pass


def distribute_load(config):
    load, plants = prepare_input(config)
    logger.debug('distribute_load: load=%s', load)
    load_plan = allocate_load(load, plants)
    logger.debug('load_plan = %s', load_plan)
    allocated = sum(load_plan.values())
    if not math.isclose(allocated, load):
        raise Exception('Unable to distribute load: load=%s, allocated=%s' % (load, allocated))
    return [{'name': name, 'p': p} for name, p in load_plan.items()]


def prepare_input(config):
    fuels = config['fuels']
    plants = {d['name']: Plant(**d, fuels=fuels) for d in config['powerplants']}
    logger.debug('plants: %s', plants)
    return config['load'], plants


def allocate_load(load, plants):
    plant_list = [p for p in plants.values() if p.pmax > 0]

    c = [p.cost for p in plant_list]

    constraints = []
    b = []
    templ = [0 for _ in plant_list]
    for i, p in enumerate(plant_list):
        # p_i <= pmax_i
        row = templ[:]
        row[i] = 1
        constraints.append(row)
        b.append(p.pmax)
        # p_i >= pmin_i
        if p.pmin > 0:
            row = templ[:]
            row[i] = 1
            constraints.append(row)
            b.append(-p.pmin)  # indicate ">=" with "-"

    # make the Sum(p_i) = load 2 inequalities
    constraints.append([1 for _ in plant_list])
    b.append(load)
    constraints.append([1 for _ in plant_list])
    b.append(-load)

    solution = simplex(c, constraints, b)
    load_plan = {name: solution.get(f'x_{i+1}', 0.0) for i, name in enumerate(plants)}

    return load_plan


def simplex(c, A, b, minimize=True):
    """
    c are the coefficients of the objective function
    A is m x n matrix of rank m
    b is the RHS of the inequalities represented by A
      b > 0 BUT:
      convention: if b_i < 0 it means sum(a_ij, j: 0 -> n) >= b_i (i.e. a "greater than").
    """
    # Convert to equalities by introducing slack variables:
    m = len(A)
    n = len(c)
    # Basic variables
    B = list(range(n, n + m, 1))
    print(f'{B=}')

    a = []
    for i, row in enumerate(A):
        s = -1 if b[i] < 0 else 1
        a_i = row[:] + [0 if j != i else s for j in range(m)]
        a.append(a_i)

    print('Phase 1')
    B, T = initialize_tableau(a, b, c, B, m, n, minimize)

    print('Phase 2')
    solution = inner_simplex(T, B, n)
    if not minimize:
        solution['z'] = -solution['z']
    print(f'{solution=}')
    return solution


def initialize_tableau(a, b, c, B, m, n, minimize):
    T = []
    # Choose a starting basic feasible solution with basis B
    # diagonal = [row[n + i] for i, row in enumerate(a)]
    diag = diagonal(a, B)
    print(f'{diag=}')
    if not all(e == 1 for e in diag):
        # for the diagonal values not equal to 1 we add artificial variables
        art_var_cnt = sum(1 for e in diag if e != 1)
        print(f'{art_var_cnt=}')
        art_vars = list(range(len(a[0]), len(a[0]) + art_var_cnt, 1))
        print(f'{art_vars=}')
        B_art = []
        v_i = 0
        for i, row in enumerate(a):
            v = [0 for _ in range(art_var_cnt)]
            if diag[i] == 1:
                # no need for an artificial variable, just use this slack variable
                B_art.append(n + i)
            else:
                # add an artificial variable
                v[v_i] = 1
                B_art.append(art_vars[v_i])
                v_i += 1
            b_i = b[i]
            if b_i < 0:
                b_i = -b_i
            T.append(row[:] + v + [b_i])
        # now the (z_0 - c_i) coefficients
        # TODO: check for maximizing problems!
        T.append([0 for _ in range(m + n)] + [-1 for _ in range(art_var_cnt)] + [0])
        # make the (z_j - c_j) coefficients 0 for the artificial variables
        # easily done by adding the row corresponding to the var to the last row
        for av_i in art_vars:
            # find the row in T:
            i = B_art.index(av_i)
            # TODO: check for maximizing problems!
            add_rows(T, i, -1)

        try:
            solution = inner_simplex(T, B_art, n + m)
        except:
            raise Exception('No initial feasible solution found')
        print('Phase 1 solution:', solution)
        print(f'   {B_art=}')
        # Assert that the artificial variables have been reduced to 0
        if not all(v == 0 for varname, v in solution.items() if varname[0] == 's'):
            raise EmptyFeasibleRegionError('No initial feasible solution found, problem set is empty')

        # if any of the artificial variables remain in the basis, try to move them out
        remaining_art_vars = [(i, vi) for i, vi in enumerate(B_art) if vi in art_vars]
        if remaining_art_vars:
            # if row(v) corresponds to the row of artificial var v in the basis:
            # - we look for a nonzero element corresponding to a nonbasic legitimate variable
            # - on this element we do a pivot.
            candidate_vars = sorted(set(range(m + n)) - set(B_art) - set(art_vars))
            remove_rows = []
            for leave_i, vi in remaining_art_vars:
                row = T[leave_i]
                for enter_j in candidate_vars:
                    if row[enter_j] != 0:
                        pivot(T, B_art, leave_i, enter_j)
                        break
                else:
                    # if they're all 0 this row is "algebraically redundant"
                    # remove it from the problem
                    remove_rows.append(leave_i)
            for i in sorted(remove_rows, reverse=True):
                T.pop(i)
                B_art.pop(i)

        # now we can discart everyting "artificial"
        # - the variables
        for j in reversed(art_vars):
            remove_column(T, j)
        # - replace the objective function with the original
        T.pop(-1)
        if minimize:
            T.append([-e for e in c] + [0 for _ in range(m)] + [0])
        else:
            T.append([e for e in c] + [0 for _ in range(m)] + [0])
        # finally, eliminate the z coefficients for the non slack variables
        for i, var_i in enumerate(B_art):
            if var_i < n:
                assert T[i][var_i] == 1
                row = T[i]
                factor = -T[-1][var_i]
                for j, value in enumerate(row):
                    T[-1][j] += factor * value

        B = B_art
    else:
        # We have a feasible solution where all non basic variables are 0 and
        # the basic variables == b
        for i, row in enumerate(a):
            b_i = b[i]
            if b_i < 0:
                b_i = -b_i
            T.append(row[:] + [b_i])

        # now the (z_0 - c_i) coefficients (z_0 == 0??)
        if minimize:
            T.append([-e for e in c] + [0 for _ in range(m)] + [0])
        else:
            T.append([e for e in c] + [0 for _ in range(m)] + [0])

    return B, T


def inner_simplex(T, B, n):
    dump_t(T, B)

    # Iterate towards optimal solution
    finished = False
    iteration = 0
    while not finished:
        print(f'{iteration=}')
        enter_j = max_index(T[-1][:-1])
        if T[-1][enter_j] <= 0:
            print('Found optimal solution')
            finished = True
        elif all(e <= 0 for e in [row[enter_j] for row in T[:-1]]):
            raise Exception('Problem is unbounded')
        else:
            leave_i = determine_leaving_variable(T, enter_j)
            print(f'{leave_i=}')
            print(f'{enter_j=}')
            pivot(T, B, leave_i, enter_j)
            dump_t(T, B)
            iteration += 1

    # gather results
    solution = {}
    result = dict(((B[i], T[i][-1]) for i in range(len(B))))
    for i in range(len(T[0]) - 1):
        if i < n:
            variable = f'x_{i+1}'
        else:
            variable = f's_{i-n+1}'
        solution[variable] = result.get(i, 0.0)
    solution['z'] = T[-1][-1]

    return solution


def diagonal(T, B):
    """The diagonal of the current basis in tableau T.

    T: the tableau
    B: the indices of the basis
    """
    # return [row[B[i]] for i, row in enumerate(T[:-1])]
    return [T[i][j] for i, j in enumerate(B)]


def remove_column(T, j):
    """Remove column j from matrix T
    """
    for row in T:
        row.pop(j)


def is_identity(A, n):
    # we know A_n is diagonal, just check the diagonal elements
    for i, row in enumerate(A):
        if row[n + i] != 1:
            return False
        # for j, e in enumerate(row[n:-1]):
        #     if j == i:
        #         if e != 1:
        #             return False
        #     elif e != 0:
        #         return False
    return True


def pivot(T, B, leave_i, enter_j):
    pivot = float(T[leave_i][enter_j])  # make sure we don't do interger division!
    print(f'{pivot=}')
    assert pivot != 0

    # devide row T[leave_i] by pivot
    for j, value in enumerate(T[leave_i]):
        T[leave_i][j] = value / pivot

    # all other rows: subtract
    leaving_row = T[leave_i]
    for i, row in enumerate(T):
        if i == leave_i:
            continue
        factor = row[enter_j]
        for j, value in enumerate(row):
            row[j] = value - factor * leaving_row[j]

    # Keep track of the basic variables
    B[leave_i] = enter_j


def add_rows(T, i1, i2, factor=1):
    """In matrix T do "T[i2] = T[i2] + factor*T[i1]"
    """
    row_i1 = T[i1]
    row_i2 = T[i2]
    for j, value in enumerate(row_i1):
        row_i2[j] += factor * value


def determine_leaving_variable(T, enter_j):
    leave_i = -1
    min_ratio = 0
    for j, row in enumerate(T[:-1]):
        if row[enter_j] > 0:
            ratio = row[-1]/row[enter_j]
            if leave_i == -1 or ratio < min_ratio:
                leave_i = j
                min_ratio = ratio
    if leave_i == -1:
        # This "cannot happen", because we already checked at the calling site
        raise Exception('Unable to determine leaving variable: problem is unbounded')
    return leave_i


def max_index(row):
    j = 0
    m = row[0]
    i = 1
    while i < len(row):
        e = row[i]
        if e > m:
            j = i
            m = e
        i += 1
    return j


def dump_t(T, B):
    l = max(len(f'{e:.2f}') for e in sum(T, []))
    fmt = ''.join(['{:', str(l), '.2f}'])
    print('Tableau:')
    for i, row in enumerate(T[:-1]):
        print(f'{B[i]: >2d}', '|', ' '.join([fmt.format(e) for e in row[:-1]]), '|', fmt.format(row[-1]))
    print(' z', '|', ' '.join([fmt.format(e) for e in T[-1][:-1]]), '|', fmt.format(T[-1][-1]))
    print('')
