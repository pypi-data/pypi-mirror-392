import math

def mask_0(data_list, qr_size):
    masked_data = []
    for coords, state in data_list:
        column = coords[0]
        row = (qr_size-1) - int(coords[1])
        if (row + column) % 2 == 0:
            if state == 0:
                state = 1
            else:
                state = 0
        masked_data.append((coords, state))
    return masked_data

def mask_1(data_list, qr_size):
    masked_data = []
    for coords, state in data_list:
        column = coords[0]
        row = (qr_size-1) - int(coords[1])
        if (row) % 2 == 0:
            if state == 0:
                state = 1
            else:
                state = 0
        masked_data.append((coords, state))
    return masked_data

def mask_2(data_list, qr_size):
    masked_data = []
    for coords, state in data_list:
        column = coords[0]
        row = (qr_size-1) - int(coords[1])
        if (column) % 3 == 0:
            if state == 0:
                state = 1
            else:
                state = 0
        masked_data.append((coords, state))
    return masked_data

def mask_3(data_list, qr_size):
    masked_data = []
    for coords, state in data_list:
        column = coords[0]
        row = (qr_size-1) - int(coords[1])
        if (row + column) % 3 == 0:
            if state == 0:
                state = 1
            else:
                state = 0
        masked_data.append((coords, state))
    return masked_data

def mask_4(data_list, qr_size):
    masked_data = []
    for coords, state in data_list:
        column = coords[0]
        row = (qr_size-1) - int(coords[1])
        if 	(math.floor(row / 2) + math.floor(column / 3) ) % 2 == 0:
            if state == 0:
                state = 1
            else:
                state = 0
        masked_data.append((coords, state))
    return masked_data

def mask_5(data_list, qr_size):
    masked_data = []
    for coords, state in data_list:
        column = coords[0]
        row = (qr_size-1) - int(coords[1])
        if ((row * column) % 2) + ((row * column) % 3) == 0:
            if state == 0:
                state = 1
            else:
                state = 0
        masked_data.append((coords, state))
    return masked_data

def mask_6(data_list, qr_size):
    masked_data = []
    for coords, state in data_list:
        column = coords[0]
        row = (qr_size-1) - int(coords[1])
        if (((row * column) % 2) + ((row * column) % 3)) % 2 == 0:
            if state == 0:
                state = 1
            else:
                state = 0
        masked_data.append((coords, state))
    return masked_data

def mask_7(data_list, qr_size):
    masked_data = []
    for coords, state in data_list:
        column = coords[0]
        row = (qr_size-1) - int(coords[1])
        if (((row + column) % 2) + ((row * column) % 3)) % 2 == 0:
            if state == 0:
                state = 1
            else:
                state = 0
        masked_data.append((coords, state))
    return masked_data