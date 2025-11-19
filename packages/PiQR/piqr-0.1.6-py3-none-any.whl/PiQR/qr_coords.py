alignment_placements = {
    2: [6, 18, 0, 0, 0, 0, 0],
    3: [6, 22, 0, 0, 0, 0, 0],
    4: [6, 26, 0, 0, 0, 0, 0],
    5: [6, 30, 0, 0, 0, 0, 0],
    6: [6, 34, 0, 0, 0, 0, 0],
    7: [6, 22, 38, 0, 0, 0, 0],
    8: [6, 24, 42, 0, 0, 0, 0],
    9: [6, 26, 46, 0, 0, 0, 0],
    10: [6, 28, 50, 0, 0, 0, 0],
    11: [6, 30, 54, 0, 0, 0, 0],
    12: [6, 32, 58, 0, 0, 0, 0],
    13: [6, 34, 62, 0, 0, 0, 0],
    14: [6, 26, 46, 66, 0, 0, 0],
    15: [6, 26, 48, 70, 0, 0, 0],
    16: [6, 26, 50, 74, 0, 0, 0],
    17: [6, 30, 54, 78, 0, 0, 0],
    18: [6, 30, 56, 82, 0, 0, 0],
    19: [6, 30, 58, 86, 0, 0, 0],
    20: [6, 34, 62, 90, 0, 0, 0],
    21: [6, 28, 50, 72, 94, 0, 0],
    22: [6, 26, 50, 74, 98, 0, 0],
    23: [6, 30, 54, 78, 102, 0, 0],
    24: [6, 28, 54, 80, 106, 0, 0],
    25: [6, 32, 58, 84, 110, 0, 0],
    26: [6, 30, 58, 86, 114, 0, 0],
    27: [6, 34, 62, 90, 118, 0, 0],
    28: [6, 26, 50, 74, 98, 122, 0],
    29: [6, 30, 54, 78, 102, 126, 0],
    30: [6, 26, 52, 78, 104, 130, 0],
    31: [6, 30, 56, 82, 108, 134, 0],
    32: [6, 34, 60, 86, 112, 138, 0],
    33: [6, 30, 58, 86, 114, 142, 0],
    34: [6, 34, 62, 90, 118, 146, 0],
    35: [6, 30, 54, 78, 102, 126, 150],
    36: [6, 24, 50, 76, 102, 128, 154],
    37: [6, 28, 54, 80, 106, 132, 158],
    38: [6, 32, 58, 84, 110, 136, 162],
    39: [6, 26, 54, 82, 110, 138, 166],
    40: [6, 30, 58, 86, 114, 142, 170],
}


def get_coords(x, y, shape):
    updated_shape = []
    for coord in shape:
        updated_x = coord[0][0] + x
        updated_y = coord[0][1] + y
        state = coord[1]
        updated_shape.append(((updated_x, updated_y), state))
    return updated_shape


def get_timing_coords(qr_size, reserve_pixels):
    finder_dim = 8
    current = qr_size - 1
    verticals = []
    for i in range(qr_size):
        y = current
        x = 6
        current = current - 1
        if (x, y) not in [i[0] for i in reserve_pixels]:
            if y % 2 == 0:
                reserve_pixels.append(((x, y), 1))
            else:
                reserve_pixels.append(((x, y), 0))

    current = 0
    for i in range(qr_size):
        x = current
        y = qr_size - finder_dim + 1
        current = current + 1
        if (x, y) not in [i[0] for i in reserve_pixels]:
            if x % 2 == 0:
                reserve_pixels.append(((x, y), 1))
            else:
                reserve_pixels.append(((x, y), 0))

    return reserve_pixels


def get_alignment_placements(version, reserve_pixels, qr_size):
    tuple_list = alignment_placements[int(version)]

    all_combinations = []
    for number_1 in tuple_list:
        if number_1 != 0:
            for number_2 in tuple_list:
                if number_2 != 0:
                    all_combinations.append((number_1, number_2))

    alignment_shapes = []

    pattern_shape = [
        ((0, 4), 1), ((1, 4), 1), ((2, 4), 1), ((3, 4), 1), ((4, 4), 1),
        ((0, 3), 1), ((1, 3), 0), ((2, 3), 0), ((3, 3), 0), ((4, 3), 1),
        ((0, 2), 1), ((1, 2), 0), ((2, 2), 1), ((3, 2), 0), ((4, 2), 1),
        ((0, 1), 1), ((1, 1), 0), ((2, 1), 0), ((3, 1), 0), ((4, 1), 1),
        ((0, 0), 1), ((1, 0), 1), ((2, 0), 1), ((3, 0), 1), ((4, 0), 1),
    ]

    for coords in all_combinations:
        x = coords[0]
        y = qr_size - coords[1]
        alignment_shapes.append(((x, y), pattern_shape))

    total_data = []
    for pattern in alignment_shapes:
        x, y = pattern[0]
        alignment_shape = pattern[1]
        data = get_coords(x-2, y-3, alignment_shape)
        total_data.append([i for i in data])

        match_count = 0
        for coord, state in data:
            if coord in [i[0] for i in reserve_pixels]:
                match_count += 1
        if match_count == 0:
            [reserve_pixels.append(i) for i in data]

    return reserve_pixels
