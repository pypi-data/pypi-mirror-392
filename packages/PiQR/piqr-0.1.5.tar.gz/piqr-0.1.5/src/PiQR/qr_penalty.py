def make_rows(mask_data, qr_size):
    rows = qr_size
    row_start = 0
    row_end = qr_size
    row_list = []
    for i in range(rows):
        states = [i[1] for i in mask_data[row_start:row_end]]
        row_list.append(states)
        row_end += rows
        row_start += rows
    return row_list

def transpose(input_list):
    output_list = []
    for i in range(len(input_list[0])):
        row = []
        for item in input_list:
            # appending to new list with values and index positions
            # i contains index position and item contains values
            row.append(item[i])
        output_list.append(row)
    return output_list

def condition_1(mask_data, qr_size):

    def count_penalty_2(input_list):
        all_runs = []
        for row in input_list:
            last_module = 0
            module_index = 0
            current_run = []
            row_run = []
            for module in row:
                if module_index == 0:
                    current_run.append(module)
                    pass
                else:
                    if module == last_module:
                        current_run.append(module)
                    else:
                        if len(current_run) == 5:
                            row_run.append(3)
                        if len(current_run) > 5:
                            row_run.append(3)
                            row_run.append(len(current_run) - 5)
                        current_run = []
                        current_run.append(module)
                module_index += 1
                last_module = module
            all_runs.append(row_run)
        return sum([sum(i) for i in all_runs])

    horizontal = make_rows(mask_data, qr_size)
    total_h_penalty = count_penalty_2(horizontal)

    vertical = []
    col_index = 0
    for i in range(qr_size):
        col_list = []
        for row in horizontal:
            col_list.append(row[col_index])
        col_index += 1
        vertical.append(col_list)
    total_v_penalty = count_penalty_2(vertical)
    return total_v_penalty + total_h_penalty

def condition_2(mask_data, qr_size):
    rows = qr_size
    row_start = 0
    row_end = qr_size
    array = []
    array_2 = []
    for i in range(rows):
        states = [i[1] for i in mask_data[row_start:row_end]]
        array.append(states)
        states_2 = []
        for state in states:
            if state == 1:
                states_2.append(0)
            else:
                states_2.append(1)
        row_end += rows
        row_start += rows
        array_2.append(states_2)

    def square_check(array):
        count = 0
        for i in range(len(array) - 1):
            for j in range(len(array[i]) - 1):
                if array[i][j] == array[i][j+1] == array[i+1][j] == array[i+1][j+1] == 1:
                    count += 1
        return count

    total_black_squares = square_check(array)
    total_white_squares = square_check(array_2)
    return (total_black_squares + total_white_squares) * 3

def condition_3(mask_data, qr_size):
    horizontals = make_rows(mask_data, qr_size)
    horizontals = transpose(horizontals)

    def count_pattern_occurrences(pattern, sequence):
        pattern_length = len(pattern)
        count = 0
        for i in range(len(sequence) - pattern_length + 1):
            if sequence[i:i + pattern_length] == pattern:
                count += 1
        return count

    pattern_occurances = 0
    for row in horizontals:
        if count_pattern_occurrences([1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0], row) != 0:
            pattern_occurances += 40
        if count_pattern_occurrences([0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1], row) != 0:
            pattern_occurances += 40

    vertical = []
    col_index = 0
    horizontals = make_rows(mask_data, qr_size)
    for i in range(qr_size):
        col_list = []
        for row in horizontals:
            col_list.append(row[col_index])
        col_index += 1
        vertical.append(col_list)

    for row in vertical:
        [row.append(0) for i in range(4)]
        [row.insert(0, 0) for i in range(4)]

    for row in vertical:
        if count_pattern_occurrences([1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0], row) != 0:
            pattern_occurances += 40
        if count_pattern_occurrences([0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1], row) != 0:
            pattern_occurances += 40

    return pattern_occurances

def condition_4(mask_data):
    total_on = [i[1] for i in mask_data if i[1] == 1]

    ratio = (len(total_on) / len(mask_data)) * 100
    prev_multiple = (ratio // 5) * 5
    next_multiple = ((ratio // 5) * 5) + 5

    abs_1 = int(abs(prev_multiple - 50) / 5)
    abs_2 = int(abs(next_multiple - 50) / 5)
    penalty = min([abs_1, abs_2]) * 10
    return penalty

def get_penalty(mask_data, reserve_data, qr_size):
    total_data = mask_data
    [total_data.append(i) for i in reserve_data]

    sorted_list = sorted(total_data, key=lambda x: (x[0][1], x[0][0]))

    total_penalty_1 = condition_1(sorted_list, qr_size)
    total_penalty_2 = condition_2(sorted_list, qr_size)
    total_penalty_3 = condition_3(sorted_list, qr_size)
    total_penalty_4 = condition_4(sorted_list)
    total_penalty = total_penalty_1 + total_penalty_2 + total_penalty_3 + total_penalty_4
    return total_penalty
