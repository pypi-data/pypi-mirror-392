from PiQR.conversions import *
import json
# Subdict indexs refer to the following
# Code Word Qty,  Code Words Per Block,  Group1 Blocks,  Block1 Code Word Qty,  Group2 Blocks,  Block2 Code Word Qty

def load_data():
    with open('qr_variables.json', 'r') as f:
        file_data = json.load(f)
    return file_data

qr_variables = load_data()

ecc_dict = qr_variables['ECC']

character_capacities = qr_variables['CharacterCapacities']

alpha_numeric = qr_variables['AlphaNumeric']

mode_indicators = qr_variables['ModeIndicators']

char_fill = qr_variables['CharFill']

def place_data_codewords(qr_size, binary, reserve_pixels):
    start_x, start_y = qr_size - 1, 0
    orientation = 'Up'
    last_direction = ''
    next_direction = 'Left'
    dir_change = False

    total_coords = qr_size * qr_size
    bit_coords = []
    bit_coords.append((start_x, start_y))

    while start_x >= 0:
        if last_direction == 'Left':
            if dir_change:
                next_direction = 'Left'
                start_x -= 1
                if start_x == 6:
                    start_x -= 1
                dir_change = False
            else:
                next_direction = 'Right'
        elif last_direction == 'Right':
            next_direction = 'Left'

        if orientation == 'Up':
            if next_direction == 'Left':
                start_x -= 1
                if (start_x, start_y) in [i[0] for i in reserve_pixels]:
                    pass
                else:
                    if start_x >= 0:
                        bit_coords.append((start_x, start_y))

                last_direction = next_direction
                if start_y == qr_size - 1:
                    # start heading down
                    if (start_x + 1, start_y) in bit_coords:
                        if (start_x + 1, start_y) not in [i[0] for i in reserve_pixels]:
                            bit_coords.append((start_x - 1, start_y))
                    orientation = 'Down'
                    dir_change = True
            elif next_direction == 'Right':
                start_x += 1
                start_y += 1
                if (start_x, start_y) in [i[0] for i in reserve_pixels]:
                    pass
                else:
                    if start_x >= 0:
                        bit_coords.append((start_x, start_y))
                last_direction = next_direction
        else:
            if next_direction == 'Left':
                start_x -= 1
                if (start_x, start_y) in [i[0] for i in reserve_pixels]:
                    pass
                else:
                    if start_x >= 0:
                        bit_coords.append((start_x, start_y))
                last_direction = next_direction
                if start_y == 0:
                    # start heading down
                    if (start_x - 1, start_y) not in [i[0] for i in reserve_pixels]:
                        bit_coords.append((start_x - 1, start_y))
                    orientation = 'Up'
                    dir_change = True
            elif next_direction == 'Right':
                start_x += 1
                start_y -= 1
                if (start_x, start_y) in [i[0] for i in reserve_pixels]:
                    pass
                else:
                    if start_x >= 0:
                        bit_coords.append((start_x, start_y))
                last_direction = next_direction

    data_pixels = []
    binary_index = 0
    for io in binary:
        line = bit_coords[binary_index]
        if io == '1':
            state_bit = 1
        else:
            state_bit = 0
        binary_index += 1
        data_pixels.append((line, state_bit))

    return data_pixels

def get_block_data(group_1_blocks, data_codewords_per_block_1, group_2_blocks, data_codewords_per_block_2, binary_values):
    block_list = []
    codeword_index = 0
    for group in range(group_1_blocks):
        codeword_list = []
        for codeword in range(data_codewords_per_block_1):
            codeword_list.append(binary_values[codeword_index])
            codeword_index += 1
        block_list.append(codeword_list)

    if group_2_blocks != '':
        for group in range(group_2_blocks):
            codeword_list = []
            for codeword in range(data_codewords_per_block_2):
                codeword_list.append(binary_values[codeword_index])
                codeword_index += 1
            block_list.append(codeword_list)

    return block_list

def equalize_list(list_of_lists):
    max_length = max(len(sublist) for sublist in list_of_lists)
    for sublist in list_of_lists:
        sublist.extend([''] * (max_length - len(sublist)))
    return list_of_lists

def interlace_lists(lists):
    interlaced = [[i[x] for i in lists] for x in range(len(lists[0]))]
    flattened_list = [item for sublist in interlaced for item in sublist]
    x = len(lists[0])
    split_list = [flattened_list[i:i + x] for i in range(0, len(flattened_list), x)]

    return split_list

def interlace_data(block_ecc_codewords, block_list):
    full_codeword_list = []
    int_blocks = [[binary_to_decimal(b) for b in i] for i in block_list]
    int_blocks = equalize_list(int_blocks)
    interlaced_codewords = interlace_lists(int_blocks)
    for sublist in interlaced_codewords:
        if '' in sublist:
            while '' in sublist:
                sublist.remove('')

    interlaced_ecc_codewords = interlace_lists(block_ecc_codewords)
    full_interlaced_codewords = [format(int(item), 'b').zfill(8) for sublist in interlaced_codewords for item in sublist]
    full_interlaced_ecc_codewords = [format(int(item), 'b').zfill(8) for sublist in interlaced_ecc_codewords for item in sublist]
    [full_codeword_list.append(i) for i in full_interlaced_codewords]
    [full_codeword_list.append(i) for i in full_interlaced_ecc_codewords]
    return full_codeword_list

def get_remainder_bits(version):
    # remainder bits are pre-defined and dependent on the qr version
    remainder_bits = [
        (1, 0),
        (2, 7),
        (3, 7),
        (4, 7),
        (5, 7),
        (6, 7),
        (7, 0),
        (8, 0),
        (9, 0),
        (10, 0),
        (11, 0),
        (12, 0),
        (13, 0),
        (14, 3),
        (15, 3),
        (16, 3),
        (17, 3),
        (18, 3),
        (19, 3),
        (20, 3),
        (21, 4),
        (22, 4),
        (23, 4),
        (24, 4),
        (25, 4),
        (26, 4),
        (27, 4),
        (28, 3),
        (29, 3),
        (30, 3),
        (31, 3),
        (32, 3),
        (33, 3),
        (34, 3),
        (35, 0),
        (36, 0),
        (37, 0),
        (38, 0),
        (39, 0),
        (40, 0),
    ]
    return [i[1] for i in remainder_bits if i[0] == int(version)][0]

def analyze_data(input_text, ecc_level):
    Numeric = False
    Byte = False
    Alphanumeric = True
    ecc_type = ''
    binary_values = []

    try:
        numbers = [int(i) for i in input_text]
        Numeric = True
        Alphanumeric = False
        ecc_type = 'Numeric'
        cc_index = 1
    except:
        for i in input_text:
            if i in alpha_numeric['Chars']:
                Alphanumeric = True
                ecc_type = 'Alphanumeric'
                cc_index = 2
            else:
                Byte = True
                Alphanumeric = False
                ecc_type = 'Byte'
                cc_index = 3
                break

    if Numeric:
        x = 3
        input_text_list = [input_text[y - x:y] for y in range(x, len(input_text) + x, x)]

        code_words = len(input_text_list)

        for i in input_text_list:
            if len(str(i)) == 2:
                binary = format(int(i), 'b').zfill(7)
            elif len(str(i)) == 1:
                binary = format(int(i), 'b').zfill(4)
            else:
                binary = format(int(i), 'b').zfill(10)
            binary_values.append(binary)

    if Alphanumeric:
        # split string into segments of length 2
        x = 2
        input_text_list = [input_text[y - x:y] for y in range(x, len(input_text) + x, x)]

        char_values = []
        code_words = len(input_text_list)
        # determine alphanumeric binary value
        for segment in input_text_list:
            char_num = 0
            char_value = 0
            if len(segment) == 2:
                char1value = alpha_numeric[segment[0]]
                char2value = alpha_numeric[segment[1]]
                char_value = (char1value * 45) + char2value
            else:
                char_value = alpha_numeric[segment]
            char_values.append(char_value)
        # convert each value to binary

        value_index = 0
        for item in char_values:
            segment = input_text_list[value_index]
            if len(input_text) % 2 != 0:
                #if item == char_values[-1]:
                if value_index == len(char_values) - 1:
                    binary = format(int(item), 'b').zfill(6)
                else:
                    binary = format(int(item), 'b').zfill(11)
            else:
                binary = format(int(item), 'b').zfill(11)
            binary_values.append(binary)
            value_index += 1

    if Byte:
        code_words = 0
        for i in input_text:
            try:
                i.encode('utf-8')
                binary = bin(int(ord(i)))[2:].zfill(8)
            except:
                break
            code_words += 1
            binary_values.append(binary)

    mode = mode_indicators[ecc_type]
    version_capacity_data = character_capacities[ecc_level]['Value_Data']
    version = min([i[0] for i in version_capacity_data if i[cc_index] > len(input_text)])
    capacity = [i[cc_index] for i in version_capacity_data if i[0] == version][0]
    ecc_code = f'{version}-{ecc_level[0]}'
    ec_codewords_per_block = ecc_dict[ecc_code]['BlockQty'] #[i[2] for i in ecc_list if i[0] == ecc_code][0]
    char_len = '9' if version <= 9 else ('26' if version <= 26 else '40')
    character_count = format(len(input_text), 'b').zfill(char_fill[ecc_type][char_len])

    group_1_blocks = ecc_dict[ecc_code]['G1Blocks'] #[i[3] for i in ecc_list if i[0] == ecc_code][0]
    data_codewords_per_block_1 = ecc_dict[ecc_code]['B1CodeQty'] #[i[4] for i in ecc_list if i[0] == ecc_code][0]
    group_2_blocks = ecc_dict[ecc_code]['G2Blocks'] #[i[5] for i in ecc_list if i[0] == ecc_code][0]
    data_codewords_per_block_2 = ecc_dict[ecc_code]['B2CodeQty'] #[i[6] for i in ecc_list if i[0] == ecc_code][0]

    total_blocks = int(group_1_blocks) + int(group_2_blocks) if group_2_blocks != '' else group_1_blocks
    total_codewords = int(int(data_codewords_per_block_1)*int(group_1_blocks)) + (int(int(data_codewords_per_block_2)*int(group_2_blocks)) if group_2_blocks != '' else 0)

    return version, capacity, ecc_code, mode, character_count, ec_codewords_per_block, group_1_blocks, data_codewords_per_block_1, group_2_blocks, data_codewords_per_block_2, total_blocks, binary_values, total_codewords



