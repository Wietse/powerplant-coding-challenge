from pcc.simplex import simplex, prepare_input


def test1():
    """
    Minimize x_1 + x_2 - 4x_3
    s.t.:
        x_1 + x_2 + 2x_3 <= 9
        x_1 + x_2 -  x_3 <= 2
       -x_1 + x_2 +  x_3 <= 4

       x_i >= 0

    """
    c = [1, 1, -4]
    A = [[ 1, 1,  2],
         [ 1, 1, -1],
         [-1, 1,  1]]
    b = [9, 2, 4]
    expected = {'x_1': 0.3333333333333333, 'x_2': 0.0, 'x_3': 4.333333333333333,
                's_1': 0.0, 's_2': 6.0, 's_3': 0.0,
                'z': -17.0}
    solution = simplex(c, A, b)
    print(solution)
    assert solution == expected


def test2():
    """
    Maximize z = 4x1 + 6x2
    s.t.:
        -x1 +  x2 <= 11
         x1 +  x2 <= 27
        2x1 + 5x2 <= 90
    """
    c = [4, 6]
    A = [[-1, 1],
         [1, 1],
         [2, 5]]
    b = [11, 27, 90]
    expected = {'x_1': 14.999999999999998, 'x_2': 12.0,
                's_1': 13.999999999999998, 's_2': 0.0, 's_3': 0.0,
                'z': 132}
    solution = simplex(c, A, b, minimize=False)
    print(solution)
    assert solution == expected


def test3():
    """
    Maximize z = 2x1 + 5x2
    s.t.:
        x1 +  x2 <= 6
              x2 <= 3
        x1 + 2x2 <= 9
    """
    c = [2, 5]
    A = [[1, 1],
         [0, 1],
         [1, 2]]
    b = [6, 3, 9]
    expected = {'x_1': 3.0, 'x_2': 3.0,
                's_1': 0.0, 's_2': 0.0, 's_3': 0.0,
                'z': 21.0}
    solution = simplex(c, A, b, minimize=False)
    print(solution)
    assert solution == expected


def test4():
    """
    Maximize z = 2x1 - x2 + 2x3
    s.t.:
        2x1 +  x2       <= 10
         x1 + 2x2 - 2x3 <= 20
               x2 + 2x3 <= 5
    """
    c = [2, -1, 2]
    A = [[2, 1, 0],
         [1, 2, -2],
         [0, 1, 2]]
    b = [10, 20, 5]
    expected = {'x_1': 5.0, 'x_2': 0.0, 'x_3': 2.5,
                's_1': 0.0, 's_2': 20.0, 's_3': 0.0,
                'z': 15.0}
    solution = simplex(c, A, b, minimize=False)
    print(solution)
    assert solution == expected


def test5():
    """
    Not a feasible solution from the given...

    Minimize z = x1 - 2x2
    s.t.:
         x1 + x2 >= 2
        -x1 + x2 >= 1
              x2 <= 3
    """
    c = [1, -2]
    A = [[1, 1],
         [-1, 1],
         [0, 1]]
    b = [-2, -1, 3]
    expected = {'x_1': 0.0, 'x_2': 3.0,
                's_1': 1.0, 's_2': 2.0, 's_3': 0.0,
                'z': -6.0}
    solution = simplex(c, A, b)
    print(solution)
    assert solution == expected


def test6():
    """
    Minimize z = 4x1 + 2x2 + x3
    s.t.:
        2x1 + 3x2 + 4x3 <= 14
        3x1 + x2 + 5x3 >= 4
        x1 + 4x2 + 3x3 >= 6
    """
    c = [4, 2, 1]
    A = [[2, 3, 4],
         [3, 1, 5],
         [1, 4, 3]]
    b = [14, -4, -6]
    expected = {'x_1': 0.0, 'x_2': 0.0, 'x_3': 2.0,
                's_1': 6.000000000000001, 's_2': 5.999999999999999, 's_3': 0.0,
                'z': 2.0}
    solution = simplex(c, A, b)
    print(solution)
    assert solution == expected


def test_payload1():
    config = {
        "load": 480,
        "fuels":
        {
            "gas(euro/MWh)": 13.4,
            "kerosine(euro/MWh)": 50.8,
            "co2(euro/ton)": 20,
            "wind(%)": 60
        },
        "powerplants": [
            {
            "name": "gasfiredbig1",
            "type": "gasfired",
            "efficiency": 0.53,
            "pmin": 100,
            "pmax": 460
            },
            {
            "name": "gasfiredbig2",
            "type": "gasfired",
            "efficiency": 0.53,
            "pmin": 100,
            "pmax": 460
            },
            {
            "name": "gasfiredsomewhatsmaller",
            "type": "gasfired",
            "efficiency": 0.37,
            "pmin": 40,
            "pmax": 210
            },
            {
            "name": "tj1",
            "type": "turbojet",
            "efficiency": 0.3,
            "pmin": 0,
            "pmax": 16
            },
            {
            "name": "windpark1",
            "type": "windturbine",
            "efficiency": 1,
            "pmin": 0,
            "pmax": 150
            },
            {
            "name": "windpark2",
            "type": "windturbine",
            "efficiency": 1,
            "pmin": 0,
            "pmax": 36
            }
        ]
    }
    expected = [
        {"name": "gasfiredbig1", "p": 368.4},
        {"name": "gasfiredbig2", "p": 0.0},
        {"name": "gasfiredsomewhatsmaller", "p": 0.0},
        {"name": "tj1", "p": 0.0},
        {"name": "windpark1", "p": 90.0},
        {"name": "windpark2", "p": 21.6}
    ]
    expected = {'x_1': 100.0, 'x_2': 100.0, 'x_3': 40.0, 'x_4': 0.0, 'x_5': 90.0, 'x_6': 21.6,
                's_1': 360.0, 's_2': 0.0, 's_3': 360.0, 's_4': 0.0, 's_5': 170.0, 's_6': 0.0, 's_7': 16.0,
                's_8': 0.0, 's_9': 0.0, 's_10': 128.4, 's_11': 0.0,
                'z': 6505.252422233556}

    load, plants = prepare_input(config)
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
    print(solution)
    assert solution == expected
