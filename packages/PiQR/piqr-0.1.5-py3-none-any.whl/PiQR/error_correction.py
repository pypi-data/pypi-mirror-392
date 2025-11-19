import math

log_antilog = [
    (0, 1, 0, 0),
    (1, 2, 1, 0),
    (2, 4, 2, 1),
    (3, 8, 3, 25),
    (4, 16, 4, 2),
    (5, 32, 5, 50),
    (6, 64, 6, 26),
    (7, 128, 7, 198),
    (8, 29, 8, 3),
    (9, 58, 9, 223),
    (10, 116, 10, 51),
    (11, 232, 11, 238),
    (12, 205, 12, 27),
    (13, 135, 13, 104),
    (14, 19, 14, 199),
    (15, 38, 15, 75),
    (16, 76, 16, 4),
    (17, 152, 17, 100),
    (18, 45, 18, 224),
    (19, 90, 19, 14),
    (20, 180, 20, 52),
    (21, 117, 21, 141),
    (22, 234, 22, 239),
    (23, 201, 23, 129),
    (24, 143, 24, 28),
    (25, 3, 25, 193),
    (26, 6, 26, 105),
    (27, 12, 27, 248),
    (28, 24, 28, 200),
    (29, 48, 29, 8),
    (30, 96, 30, 76),
    (31, 192, 31, 113),
    (32, 157, 32, 5),
    (33, 39, 33, 138),
    (34, 78, 34, 101),
    (35, 156, 35, 47),
    (36, 37, 36, 225),
    (37, 74, 37, 36),
    (38, 148, 38, 15),
    (39, 53, 39, 33),
    (40, 106, 40, 53),
    (41, 212, 41, 147),
    (42, 181, 42, 142),
    (43, 119, 43, 218),
    (44, 238, 44, 240),
    (45, 193, 45, 18),
    (46, 159, 46, 130),
    (47, 35, 47, 69),
    (48, 70, 48, 29),
    (49, 140, 49, 181),
    (50, 5, 50, 194),
    (51, 10, 51, 125),
    (52, 20, 52, 106),
    (53, 40, 53, 39),
    (54, 80, 54, 249),
    (55, 160, 55, 185),
    (56, 93, 56, 201),
    (57, 186, 57, 154),
    (58, 105, 58, 9),
    (59, 210, 59, 120),
    (60, 185, 60, 77),
    (61, 111, 61, 228),
    (62, 222, 62, 114),
    (63, 161, 63, 166),
    (64, 95, 64, 6),
    (65, 190, 65, 191),
    (66, 97, 66, 139),
    (67, 194, 67, 98),
    (68, 153, 68, 102),
    (69, 47, 69, 221),
    (70, 94, 70, 48),
    (71, 188, 71, 253),
    (72, 101, 72, 226),
    (73, 202, 73, 152),
    (74, 137, 74, 37),
    (75, 15, 75, 179),
    (76, 30, 76, 16),
    (77, 60, 77, 145),
    (78, 120, 78, 34),
    (79, 240, 79, 136),
    (80, 253, 80, 54),
    (81, 231, 81, 208),
    (82, 211, 82, 148),
    (83, 187, 83, 206),
    (84, 107, 84, 143),
    (85, 214, 85, 150),
    (86, 177, 86, 219),
    (87, 127, 87, 189),
    (88, 254, 88, 241),
    (89, 225, 89, 210),
    (90, 223, 90, 19),
    (91, 163, 91, 92),
    (92, 91, 92, 131),
    (93, 182, 93, 56),
    (94, 113, 94, 70),
    (95, 226, 95, 64),
    (96, 217, 96, 30),
    (97, 175, 97, 66),
    (98, 67, 98, 182),
    (99, 134, 99, 163),
    (100, 17, 100, 195),
    (101, 34, 101, 72),
    (102, 68, 102, 126),
    (103, 136, 103, 110),
    (104, 13, 104, 107),
    (105, 26, 105, 58),
    (106, 52, 106, 40),
    (107, 104, 107, 84),
    (108, 208, 108, 250),
    (109, 189, 109, 133),
    (110, 103, 110, 186),
    (111, 206, 111, 61),
    (112, 129, 112, 202),
    (113, 31, 113, 94),
    (114, 62, 114, 155),
    (115, 124, 115, 159),
    (116, 248, 116, 10),
    (117, 237, 117, 21),
    (118, 199, 118, 121),
    (119, 147, 119, 43),
    (120, 59, 120, 78),
    (121, 118, 121, 212),
    (122, 236, 122, 229),
    (123, 197, 123, 172),
    (124, 151, 124, 115),
    (125, 51, 125, 243),
    (126, 102, 126, 167),
    (127, 204, 127, 87),
    (128, 133, 128, 7),
    (129, 23, 129, 112),
    (130, 46, 130, 192),
    (131, 92, 131, 247),
    (132, 184, 132, 140),
    (133, 109, 133, 128),
    (134, 218, 134, 99),
    (135, 169, 135, 13),
    (136, 79, 136, 103),
    (137, 158, 137, 74),
    (138, 33, 138, 222),
    (139, 66, 139, 237),
    (140, 132, 140, 49),
    (141, 21, 141, 197),
    (142, 42, 142, 254),
    (143, 84, 143, 24),
    (144, 168, 144, 227),
    (145, 77, 145, 165),
    (146, 154, 146, 153),
    (147, 41, 147, 119),
    (148, 82, 148, 38),
    (149, 164, 149, 184),
    (150, 85, 150, 180),
    (151, 170, 151, 124),
    (152, 73, 152, 17),
    (153, 146, 153, 68),
    (154, 57, 154, 146),
    (155, 114, 155, 217),
    (156, 228, 156, 35),
    (157, 213, 157, 32),
    (158, 183, 158, 137),
    (159, 115, 159, 46),
    (160, 230, 160, 55),
    (161, 209, 161, 63),
    (162, 191, 162, 209),
    (163, 99, 163, 91),
    (164, 198, 164, 149),
    (165, 145, 165, 188),
    (166, 63, 166, 207),
    (167, 126, 167, 205),
    (168, 252, 168, 144),
    (169, 229, 169, 135),
    (170, 215, 170, 151),
    (171, 179, 171, 178),
    (172, 123, 172, 220),
    (173, 246, 173, 252),
    (174, 241, 174, 190),
    (175, 255, 175, 97),
    (176, 227, 176, 242),
    (177, 219, 177, 86),
    (178, 171, 178, 211),
    (179, 75, 179, 171),
    (180, 150, 180, 20),
    (181, 49, 181, 42),
    (182, 98, 182, 93),
    (183, 196, 183, 158),
    (184, 149, 184, 132),
    (185, 55, 185, 60),
    (186, 110, 186, 57),
    (187, 220, 187, 83),
    (188, 165, 188, 71),
    (189, 87, 189, 109),
    (190, 174, 190, 65),
    (191, 65, 191, 162),
    (192, 130, 192, 31),
    (193, 25, 193, 45),
    (194, 50, 194, 67),
    (195, 100, 195, 216),
    (196, 200, 196, 183),
    (197, 141, 197, 123),
    (198, 7, 198, 164),
    (199, 14, 199, 118),
    (200, 28, 200, 196),
    (201, 56, 201, 23),
    (202, 112, 202, 73),
    (203, 224, 203, 236),
    (204, 221, 204, 127),
    (205, 167, 205, 12),
    (206, 83, 206, 111),
    (207, 166, 207, 246),
    (208, 81, 208, 108),
    (209, 162, 209, 161),
    (210, 89, 210, 59),
    (211, 178, 211, 82),
    (212, 121, 212, 41),
    (213, 242, 213, 157),
    (214, 249, 214, 85),
    (215, 239, 215, 170),
    (216, 195, 216, 251),
    (217, 155, 217, 96),
    (218, 43, 218, 134),
    (219, 86, 219, 177),
    (220, 172, 220, 187),
    (221, 69, 221, 204),
    (222, 138, 222, 62),
    (223, 9, 223, 90),
    (224, 18, 224, 203),
    (225, 36, 225, 89),
    (226, 72, 226, 95),
    (227, 144, 227, 176),
    (228, 61, 228, 156),
    (229, 122, 229, 169),
    (230, 244, 230, 160),
    (231, 245, 231, 81),
    (232, 247, 232, 11),
    (233, 243, 233, 245),
    (234, 251, 234, 22),
    (235, 235, 235, 235),
    (236, 203, 236, 122),
    (237, 139, 237, 117),
    (238, 11, 238, 44),
    (239, 22, 239, 215),
    (240, 44, 240, 79),
    (241, 88, 241, 174),
    (242, 176, 242, 213),
    (243, 125, 243, 233),
    (244, 250, 244, 230),
    (245, 233, 245, 231),
    (246, 207, 246, 173),
    (247, 131, 247, 232),
    (248, 27, 248, 116),
    (249, 54, 249, 214),
    (250, 108, 250, 244),
    (251, 216, 251, 234),
    (252, 173, 252, 168),
    (253, 71, 253, 80),
    (254, 142, 254, 88),
    (255, 1, 255, 175),
]

get_antilog = {
    0: 0,
    1: 0,
    2: 1,
    3: 25,
    4: 2,
    5: 50,
    6: 26,
    7: 198,
    8: 3,
    9: 223,
    10: 51,
    11: 238,
    12: 27,
    13: 104,
    14: 199,
    15: 75,
    16: 4,
    17: 100,
    18: 224,
    19: 14,
    20: 52,
    21: 141,
    22: 239,
    23: 129,
    24: 28,
    25: 193,
    26: 105,
    27: 248,
    28: 200,
    29: 8,
    30: 76,
    31: 113,
    32: 5,
    33: 138,
    34: 101,
    35: 47,
    36: 225,
    37: 36,
    38: 15,
    39: 33,
    40: 53,
    41: 147,
    42: 142,
    43: 218,
    44: 240,
    45: 18,
    46: 130,
    47: 69,
    48: 29,
    49: 181,
    50: 194,
    51: 125,
    52: 106,
    53: 39,
    54: 249,
    55: 185,
    56: 201,
    57: 154,
    58: 9,
    59: 120,
    60: 77,
    61: 228,
    62: 114,
    63: 166,
    64: 6,
    65: 191,
    66: 139,
    67: 98,
    68: 102,
    69: 221,
    70: 48,
    71: 253,
    72: 226,
    73: 152,
    74: 37,
    75: 179,
    76: 16,
    77: 145,
    78: 34,
    79: 136,
    80: 54,
    81: 208,
    82: 148,
    83: 206,
    84: 143,
    85: 150,
    86: 219,
    87: 189,
    88: 241,
    89: 210,
    90: 19,
    91: 92,
    92: 131,
    93: 56,
    94: 70,
    95: 64,
    96: 30,
    97: 66,
    98: 182,
    99: 163,
    100: 195,
    101: 72,
    102: 126,
    103: 110,
    104: 107,
    105: 58,
    106: 40,
    107: 84,
    108: 250,
    109: 133,
    110: 186,
    111: 61,
    112: 202,
    113: 94,
    114: 155,
    115: 159,
    116: 10,
    117: 21,
    118: 121,
    119: 43,
    120: 78,
    121: 212,
    122: 229,
    123: 172,
    124: 115,
    125: 243,
    126: 167,
    127: 87,
    128: 7,
    129: 112,
    130: 192,
    131: 247,
    132: 140,
    133: 128,
    134: 99,
    135: 13,
    136: 103,
    137: 74,
    138: 222,
    139: 237,
    140: 49,
    141: 197,
    142: 254,
    143: 24,
    144: 227,
    145: 165,
    146: 153,
    147: 119,
    148: 38,
    149: 184,
    150: 180,
    151: 124,
    152: 17,
    153: 68,
    154: 146,
    155: 217,
    156: 35,
    157: 32,
    158: 137,
    159: 46,
    160: 55,
    161: 63,
    162: 209,
    163: 91,
    164: 149,
    165: 188,
    166: 207,
    167: 205,
    168: 144,
    169: 135,
    170: 151,
    171: 178,
    172: 220,
    173: 252,
    174: 190,
    175: 97,
    176: 242,
    177: 86,
    178: 211,
    179: 171,
    180: 20,
    181: 42,
    182: 93,
    183: 158,
    184: 132,
    185: 60,
    186: 57,
    187: 83,
    188: 71,
    189: 109,
    190: 65,
    191: 162,
    192: 31,
    193: 45,
    194: 67,
    195: 216,
    196: 183,
    197: 123,
    198: 164,
    199: 118,
    200: 196,
    201: 23,
    202: 73,
    203: 236,
    204: 127,
    205: 12,
    206: 111,
    207: 246,
    208: 108,
    209: 161,
    210: 59,
    211: 82,
    212: 41,
    213: 157,
    214: 85,
    215: 170,
    216: 251,
    217: 96,
    218: 134,
    219: 177,
    220: 187,
    221: 204,
    222: 62,
    223: 90,
    224: 203,
    225: 89,
    226: 95,
    227: 176,
    228: 156,
    229: 169,
    230: 160,
    231: 81,
    232: 11,
    233: 245,
    234: 22,
    235: 235,
    236: 122,
    237: 117,
    238: 44,
    239: 215,
    240: 79,
    241: 174,
    242: 213,
    243: 233,
    244: 230,
    245: 231,
    246: 173,
    247: 232,
    248: 116,
    249: 214,
    250: 244,
    251: 234,
    252: 168,
    253: 80,
    254: 88,
    255: 175,
}

get_log = {
    0: 1,
    1: 2,
    2: 4,
    3: 8,
    4: 16,
    5: 32,
    6: 64,
    7: 128,
    8: 29,
    9: 58,
    10: 116,
    11: 232,
    12: 205,
    13: 135,
    14: 19,
    15: 38,
    16: 76,
    17: 152,
    18: 45,
    19: 90,
    20: 180,
    21: 117,
    22: 234,
    23: 201,
    24: 143,
    25: 3,
    26: 6,
    27: 12,
    28: 24,
    29: 48,
    30: 96,
    31: 192,
    32: 157,
    33: 39,
    34: 78,
    35: 156,
    36: 37,
    37: 74,
    38: 148,
    39: 53,
    40: 106,
    41: 212,
    42: 181,
    43: 119,
    44: 238,
    45: 193,
    46: 159,
    47: 35,
    48: 70,
    49: 140,
    50: 5,
    51: 10,
    52: 20,
    53: 40,
    54: 80,
    55: 160,
    56: 93,
    57: 186,
    58: 105,
    59: 210,
    60: 185,
    61: 111,
    62: 222,
    63: 161,
    64: 95,
    65: 190,
    66: 97,
    67: 194,
    68: 153,
    69: 47,
    70: 94,
    71: 188,
    72: 101,
    73: 202,
    74: 137,
    75: 15,
    76: 30,
    77: 60,
    78: 120,
    79: 240,
    80: 253,
    81: 231,
    82: 211,
    83: 187,
    84: 107,
    85: 214,
    86: 177,
    87: 127,
    88: 254,
    89: 225,
    90: 223,
    91: 163,
    92: 91,
    93: 182,
    94: 113,
    95: 226,
    96: 217,
    97: 175,
    98: 67,
    99: 134,
    100: 17,
    101: 34,
    102: 68,
    103: 136,
    104: 13,
    105: 26,
    106: 52,
    107: 104,
    108: 208,
    109: 189,
    110: 103,
    111: 206,
    112: 129,
    113: 31,
    114: 62,
    115: 124,
    116: 248,
    117: 237,
    118: 199,
    119: 147,
    120: 59,
    121: 118,
    122: 236,
    123: 197,
    124: 151,
    125: 51,
    126: 102,
    127: 204,
    128: 133,
    129: 23,
    130: 46,
    131: 92,
    132: 184,
    133: 109,
    134: 218,
    135: 169,
    136: 79,
    137: 158,
    138: 33,
    139: 66,
    140: 132,
    141: 21,
    142: 42,
    143: 84,
    144: 168,
    145: 77,
    146: 154,
    147: 41,
    148: 82,
    149: 164,
    150: 85,
    151: 170,
    152: 73,
    153: 146,
    154: 57,
    155: 114,
    156: 228,
    157: 213,
    158: 183,
    159: 115,
    160: 230,
    161: 209,
    162: 191,
    163: 99,
    164: 198,
    165: 145,
    166: 63,
    167: 126,
    168: 252,
    169: 229,
    170: 215,
    171: 179,
    172: 123,
    173: 246,
    174: 241,
    175: 255,
    176: 227,
    177: 219,
    178: 171,
    179: 75,
    180: 150,
    181: 49,
    182: 98,
    183: 196,
    184: 149,
    185: 55,
    186: 110,
    187: 220,
    188: 165,
    189: 87,
    190: 174,
    191: 65,
    192: 130,
    193: 25,
    194: 50,
    195: 100,
    196: 200,
    197: 141,
    198: 7,
    199: 14,
    200: 28,
    201: 56,
    202: 112,
    203: 224,
    204: 221,
    205: 167,
    206: 83,
    207: 166,
    208: 81,
    209: 162,
    210: 89,
    211: 178,
    212: 121,
    213: 242,
    214: 249,
    215: 239,
    216: 195,
    217: 155,
    218: 43,
    219: 86,
    220: 172,
    221: 69,
    222: 138,
    223: 9,
    224: 18,
    225: 36,
    226: 72,
    227: 144,
    228: 61,
    229: 122,
    230: 244,
    231: 245,
    232: 247,
    233: 243,
    234: 251,
    235: 235,
    236: 203,
    237: 139,
    238: 11,
    239: 22,
    240: 44,
    241: 88,
    242: 176,
    243: 125,
    244: 250,
    245: 233,
    246: 207,
    247: 131,
    248: 27,
    249: 54,
    250: 108,
    251: 216,
    252: 173,
    253: 71,
    254: 142,
    255: 1,
}

alpha_numberic = {
    'Chars': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', ' ', '$', '%', '*', '+', '-', '.', '/', ':'],
    0: '0', 
    1: '1', 
    2: '2', 
    3: '3', 
    4: '4', 
    5: '5', 
    6: '6', 
    7: '7', 
    8: '8', 
    9: '9', 
    10: 'A', 
    11: 'B', 
    12: 'C', 
    13: 'D', 
    14: 'E', 
    15: 'F', 
    16: 'G', 
    17: 'H', 
    18: 'I', 
    19: 'J', 
    20: 'K', 
    21: 'L', 
    22: 'M', 
    23: 'N', 
    24: 'O', 
    25: 'P', 
    26: 'Q', 
    27: 'R', 
    28: 'S', 
    29: 'T', 
    30: 'U', 
    31: 'V', 
    32: 'W', 
    33: 'X', 
    34: 'Y', 
    35: 'Z', 
    36: ' ', 
    37: '$', 
    38: '%', 
    39: '*', 
    40: '+', 
    41: '-', 
    42: '.', 
    43: '/', 
    44: ':',
}
                      


def get_message_polynomial(input_text, ec_codewords_per_block):
    # Getting the decimal value of each character
    x = 8
    bits = [input_text[y - x:y] for y in range(x, len(input_text) + x, x)]

    decimal_values = []
    for item in bits:
        decimal_value = int(item, 2)
        decimal_values.append(decimal_value)
    poly_count = len(decimal_values) - 1
    message_polynomial = []
    for item in decimal_values:
        message_polynomial.append([item, poly_count + ec_codewords_per_block]) # adding number of codewords to make sure leading exponent isnt too small
        poly_count -= 1
    return message_polynomial

def get_message_polynomial_string(input_text, ec_codewords_per_block):
    'This will be set up solely to print out a string version of the message polynomial'
    # Getting the decimal value of each character
    x = 8
    bits = [input_text[y - x:y] for y in range(x, len(input_text) + x, x)]
    decimal_values = []
    for item in bits:
        decimal_value = int(item, 2)
        decimal_values.append(decimal_value)

    poly_count = len(decimal_values) - 1
    message_polynomial = ''
    for item in decimal_values:
        if poly_count == 0:
            message = f'{item}x^{poly_count + ec_codewords_per_block}'
        else:
            message = f'{item}x^{poly_count + ec_codewords_per_block}+'  # adding number of codewords to make sure leading exponent isnt too small
        message_polynomial = message_polynomial + message
        poly_count -= 1

    return message_polynomial

def poly_split(poly_string):
    side1, side2 = poly_string.split('*')
    add1 = side1.split('+')
    add2 = side2.split('+')
    items_1 = []
    for item in add1:
        items = item.split('x^')
        items = [i.replace('a^', '') for i in items]
        items_1.append(items)

    items_2 = []
    for item in add2:
        items = item.split('x^')
        items = [i.replace('a^', '') for i in items]
        items_2.append(items)
    return items_1, items_2

def poly_join(poly_list):
    poly_string = ''
    count = 1
    for item in poly_list:
        if count == len(poly_list):
            poly_string = poly_string + f'a^{item[0]}x^{item[1]}'
        else:
            poly_string = poly_string + f'a^{item[0]}x^{item[1]}+'
        count += 1
    return poly_string

def multiply_generator_xor(lead_term, generator_polynomial):
    # convert to alpha
    lead_term = get_antilog[lead_term]
    step_1 = []
    for a_term, x_term in generator_polynomial:
        a_exp = a_term
        output = lead_term + a_exp
        output = (output % 255) if output > 255 else output
        # convert to integer
        int_output = get_log[output]
        step_1.append(int_output)
    return step_1

def xor_results(multiplied_list, last_list):
    step_2 = []
    var_index = 0
    for item in last_list:
        exp_1b = int(item)
        if var_index < len(multiplied_list):
            output = exp_1b ^ int(multiplied_list[var_index])
        else:
            output = exp_1b ^ 0
        step_2.append(output)
        var_index += 1

    # discard the lead zero
    if step_2[0] == 0:
        step_2.pop(0)
    elif step_2[0] == 1:
        step_2.pop(0)

    return step_2

def make_even(list1, list2):
    if len(list1) < len(list2):
        [list1.append(0) for i in range(len(list2) - len(list1))]
    else:
        [list2.append(0) for i in range(len(list1) - len(list2))]

    return list1, list2

def get_generator_polynomial(ec_codewords_per_block, lead_exponent):
    previous_poly_list = [[0, 1], [0, 0]]
    for step in range(ec_codewords_per_block - 1):
        step = step + 1
        new_poly_list = [[0, 1], [step, 0]]
        grouping = []
        index_2 = 0
        for i in previous_poly_list:
            for a in new_poly_list:
                grouping.append((i, a))

        terms = []
        for item in grouping:
            a, x = item
            a1, a2 = a
            x1, x2 = x

            a1 = (a1 % 256) + math.floor(a1 / 256) if a1 > 255 else a1
            a2 = (a2 % 256) + math.floor(a2 / 256) if a2 > 255 else a2
            x1 = (x1 % 256) + math.floor(x1 / 256) if x1 > 255 else x1
            x2 = (x2 % 256) + math.floor(x2 / 256) if x2 > 255 else x2

            exp1 = a1 + x1
            exp2 = a2 + x2
            terms.append((exp1, exp2))

        # combine terms if multiple x^n factors
        single_terms = list(set([i[1] for i in terms]))
        combine_list = []
        for item in single_terms:
            dups = len([i[0] for i in terms if i[1] == item])
            if dups > 1:
                combine_list.append(item)


        for item in combine_list:
            items_to_combine = [i for i in terms if i[1] == item]
            xor_items = []
            for term in items_to_combine:
                terms.remove(term)
                a, x = term
                a = (a % 255) if a > 255 else a
                #tolog = get_log(a)
                tolog = get_log[a]
                xor_items.append(tolog)

            item_no = 0
            last_item = 0
            for item in xor_items:
                if item_no == 0:
                    last_item = item
                else:
                    last_item = last_item ^ item
                item_no += 1
            antilog = get_antilog[last_item]
            terms.append([antilog, x])

        previous_poly_list = terms

    # Need to sort by the exponent on the x value
    sorted_poly_list = sorted(previous_poly_list, key=lambda x: x[1], reverse=True)

    string_count = 1
    # adding number of codewords to make sure leading exponent isnt too small
    exponent_equalizer = lead_exponent - int(sorted_poly_list[0][1])
    new_poly_list = []
    for item in sorted_poly_list:
        new_poly_list.append([item[0], int(item[1]) + exponent_equalizer])
        string_count += 1

    return new_poly_list

def get_generator_polynomial_string(ec_codewords_per_block, lead_exponent):
    'This will be set up solely to print out a string version of the generator polynomial'

    previous_poly_string = 'a^0x^1+a^0x^0'
    for step in range(ec_codewords_per_block - 1):
        step = step + 1
        poly_string = f'{previous_poly_string}*a^0x^1+a^{step}x^0'
        items_1, items_2 = poly_split(poly_string)
        grouping = []
        index_2 = 0
        for i in items_1:
            for a in items_2:
                grouping.append((i, a))

        terms = []
        for item in grouping:
            a, x = item
            a1 = int(a[0])
            a2 = int(a[1])
            x1 = int(x[0])
            x2 = int(x[1])

            a1 = (a1 % 256) + math.floor(a1 / 256) if a1 > 255 else a1
            a2 = (a2 % 256) + math.floor(a2 / 256) if a2 > 255 else a2
            x1 = (x1 % 256) + math.floor(x1 / 256) if x1 > 255 else x1
            x2 = (x2 % 256) + math.floor(x2 / 256) if x2 > 255 else x2

            exp1 = int(a1) + int(x1)
            exp2 = int(a2) + int(x2)
            terms.append((f'{exp1}', f'{exp2}'))

        # combine terms if multiple x^n factors
        single_terms = list(set([i[1] for i in terms]))
        combine_list = []
        for item in single_terms:
            dups = len([i[0] for i in terms if i[1] == item])
            if dups > 1:
                combine_list.append(item)

        for item in combine_list:
            items_to_combine = [i for i in terms if i[1] == item]
            xor_items = []
            for term in items_to_combine:
                terms.remove(term)
                a, x = term
                a = (int(a) % 255) if int(a) > 255 else int(a)
                tolog = get_log[a]
                xor_items.append(tolog)

            item_no = 0
            last_item = 0
            for item in xor_items:
                if item_no == 0:
                    last_item = item
                else:
                    last_item = last_item ^ item
                item_no += 1
            antilog = get_antilog[last_item]
            terms.append((str(antilog), str(x)))

        previous_poly_string = poly_join(terms)

    # Need to sort by the exponent on the x value
    sorted_poly = sorted([i.split('x^') for i in previous_poly_string.split('+')], key=lambda x: int(x[1]),
                         reverse=True)
    new_poly_string = ''
    string_count = 1
    # adding number of codewords to make sure leading exponent isnt too small
    exponent_equalizer = lead_exponent - int(sorted_poly[0][1])
    for item in sorted_poly:
        if string_count == len(sorted_poly):
            new_poly_string = new_poly_string + f'{item[0]}x^{int(item[1])+exponent_equalizer}'
        else:
            new_poly_string = new_poly_string + f'{item[0]}x^{int(item[1])+exponent_equalizer}+'
        string_count += 1
    return new_poly_string

def get_ecc(ec_codewords_per_block, input_text, verbose=False):
    verbose = False
    print(input_text) if verbose else ''
    message_polynomial = get_message_polynomial(input_text, ec_codewords_per_block)
    print(ec_codewords_per_block, [i[0] for i in message_polynomial]) if verbose else ''
    # Verify that the lead term of the generator polynomial has the same exponent as the lead of the message polynomial
    lead_exponent = int(message_polynomial[0][1])
    generator_polynomial = get_generator_polynomial(ec_codewords_per_block, lead_exponent)

    # Step 1a: Multiply the Generator Polynomial by the Lead Term of the Message Polynomial
    lead_term = message_polynomial[0]
    lead_alpha_exponent = get_antilog[int(lead_term[0])]

    int_notations = []
    for a_term, x_term in generator_polynomial:
        a_var = a_term + int(lead_alpha_exponent)
        a_var = (a_var % 255) if a_var > 255 else a_var
        a_var = get_log[a_var]
        int_notations.append([a_var, x_term])

    print('Step 1a', int_notations) if verbose else ''
    total_loops = len(message_polynomial) # get total number of loops before making lists the same length

    # Step 1b: XOR the result with the message polynomial
    int_notations, split_message = make_even(int_notations, message_polynomial)
    step_1b = []
    var_index = 0
    for i in range(len(int_notations)):
        item = split_message[i] if split_message[i] != 0 else [0, 0]
        item_2 = int_notations[i] if int_notations[i] != 0 else [0, 0]

        a_var = int(item[0])
        x_var = int(item_2[0])
        if var_index < len(int_notations):
            output = a_var ^ x_var
        else:
            output = a_var ^ 0

        step_1b.append(output)
        var_index += 1
    print('Step 1b', step_1b) if verbose else ''
    
    # discard the lead zero
    step_1b.pop(0) if step_1b[0] == 0 else ''

    current_loop = 2
    lead_term = step_1b[0]
    last_list = step_1b

    while current_loop <= total_loops:
        # Multiply the Generator Polynomial by the Lead Term of the previous loop
        multiplied_list = multiply_generator_xor(lead_term, generator_polynomial)
        print(f'Step {current_loop}a', multiplied_list) if verbose else ''
        # make the two lists the same length by adding zeros to the lesser
        last_list, multiplied_list = make_even(last_list, multiplied_list)
        # XOR the result with the result from previous loop
        last_list = xor_results(multiplied_list, last_list)
        print(f'Step {current_loop}b', last_list) if verbose else ''

        if last_list[0] == 0:
            # Discard lead term if lead term is still zero
            # this counts as a divistion step
            last_list.pop(0)
            current_loop += 1
            print(f'Step {current_loop}', last_list) if verbose else ''

        lead_term = last_list[0]

        current_loop += 1

    if len(last_list) < ec_codewords_per_block:
        if lead_exponent - len(last_list) - (current_loop - 1) == 0:
            last_list.append(0)
        elif lead_exponent - len(last_list) - (current_loop - 1) == -1:
            last_list.insert(0, 0)

    print('Final Output:', last_list) if verbose else ''
    return last_list

def get_final_string():
    final_string_list = [
        ('L', 0, '111011111000100'),
        ('L', 1, '111001011110011'),
        ('L', 2, '111110110101010'),
        ('L', 3, '111100010011101'),
        ('L', 4, '110011000101111'),
        ('L', 5, '110001100011000'),
        ('L', 6, '110110001000001'),
        ('L', 7, '110100101110110'),
        ('M', 0, '101010000010010'),
        ('M', 1, '101000100100101'),
        ('M', 2, '101111001111100'),
        ('M', 3, '101101101001011'),
        ('M', 4, '100010111111001'),
        ('M', 5, '100000011001110'),
        ('M', 6, '100111110010111'),
        ('M', 7, '100101010100000'),
        ('Q', 0, '011010101011111'),
        ('Q', 1, '011000001101000'),
        ('Q', 2, '011111100110001'),
        ('Q', 3, '011101000000110'),
        ('Q', 4, '010010010110100'),
        ('Q', 5, '010000110000011'),
        ('Q', 6, '010111011011010'),
        ('Q', 7, '010101111101101'),
        ('H', 0, '001011010001001'),
        ('H', 1, '001001110111110'),
        ('H', 2, '001110011100111'),
        ('H', 3, '001100111010000'),
        ('H', 4, '000011101100010'),
        ('H', 5, '000001001010101'),
        ('H', 6, '000110100001100'),
        ('H', 7, '000100000111011'),
    ]

def get_format_ecc(ec_codewords_per_block, input_text):
    binary_version = '10100110111' # this is the defined and set binary version of the generator polynomial
    # make input text binary length equal to 15
    while len(input_text) != 15:
        input_text = input_text + '0'
    # then remove any leading zeroes

    for i in input_text:
        if i == '1':
            break
        else:
            input_text = input_text[1:]

    # set generator polynomial bits to same length as current text input
    padded_generator = binary_version
    while len(padded_generator) < len(input_text):
        padded_generator = padded_generator + '0'

    xord = ''
    bit_index = 0
    for bit in input_text:
        xor_result = int(bit) ^ int(padded_generator[bit_index])
        bit_index += 1
        xord = xord + str(xor_result)

    for i in xord:
        if i == '1':
            break
        else:
            xord = xord[1:]

    while len(xord) > 10:
        # remove leading zeroes from the result
        for i in xord:
            if i == '1':
                break
            else:
                xord = xord[1:]
        input_text = xord
        if len(xord) > ec_codewords_per_block:
            # its still too long, add padding to generator polynomial again+
            padded_generator = binary_version
            while len(padded_generator) < len(xord):
                padded_generator = padded_generator + '0'
            # now xor the two strings
            bit_index = 0
            updated_xord = ''
            for bit in xord:
                xor_result = int(bit) ^ int(padded_generator[bit_index])
                bit_index += 1
                updated_xord = updated_xord + str(xor_result)

            xord = updated_xord

    xord = xord.zfill(10)
    return xord

def get_version_ecc(ec_codewords_per_block, input_text):
    binary_version = '1111100100101'  # this is the defined and set binary version of the generator polynomial
    # make input text binary length equal to 15
    while len(input_text) != 18:
        input_text = input_text + '0'
    # then remove any leading zeroes

    for i in input_text:
        if i == '1':
            break
        else:
            input_text = input_text[1:]

    # set generator polynomial bits to same length as current text input
    padded_generator = binary_version
    while len(padded_generator) < len(input_text):
        padded_generator = padded_generator + '0'

    xord = ''
    bit_index = 0
    for bit in input_text:
        xor_result = int(bit) ^ int(padded_generator[bit_index])
        bit_index += 1
        xord = xord + str(xor_result)

    for i in xord:
        if i == '1':
            break
        else:
            xord = xord[1:]

    while len(xord) > ec_codewords_per_block:
        # remove leading zeroes from the result
        for i in xord:
            if i == '1':
                break
            else:
                xord = xord[1:]
        input_text = xord
        if len(xord) > ec_codewords_per_block:
            # its still too long, add padding to generator polynomial again+
            padded_generator = binary_version
            while len(padded_generator) < len(xord):
                padded_generator = padded_generator + '0'
            # now xor the two strings
            bit_index = 0
            updated_xord = ''
            for bit in xord:
                xor_result = int(bit) ^ int(padded_generator[bit_index])
                bit_index += 1
                updated_xord = updated_xord + str(xor_result)

            xord = updated_xord

    xord = xord.zfill(ec_codewords_per_block)
    return xord
