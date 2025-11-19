from PiQR.conversions import *

# Subdict indexs refer to the following
# Code Word Qty,  Code Words Per Block,  Group1 Blocks,  Block1 Code Word Qty,  Group2 Blocks,  Block2 Code Word Qty

ecc_dict = {
    '1-L': {
        'CodeQty': 19,
        'BlockQty': 7,
        'G1Blocks': 1,
        'B1CodeQty': 19,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '1-M': {
        'CodeQty': 16,
        'BlockQty': 10,
        'G1Blocks': 1,
        'B1CodeQty': 16,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '1-Q': {
        'CodeQty': 13,
        'BlockQty': 13,
        'G1Blocks': 1,
        'B1CodeQty': 13,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '1-H': {
        'CodeQty': 9,
        'BlockQty': 17,
        'G1Blocks': 1,
        'B1CodeQty': 9,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '2-L': {
        'CodeQty': 34,
        'BlockQty': 10,
        'G1Blocks': 1,
        'B1CodeQty': 34,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '2-M': {
        'CodeQty': 28,
        'BlockQty': 16,
        'G1Blocks': 1,
        'B1CodeQty': 28,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '2-Q': {
        'CodeQty': 22,
        'BlockQty': 22,
        'G1Blocks': 1,
        'B1CodeQty': 22,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '2-H': {
        'CodeQty': 16,
        'BlockQty': 28,
        'G1Blocks': 1,
        'B1CodeQty': 16,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '3-L': {
        'CodeQty': 55,
        'BlockQty': 15,
        'G1Blocks': 1,
        'B1CodeQty': 55,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '3-M': {
        'CodeQty': 44,
        'BlockQty': 26,
        'G1Blocks': 1,
        'B1CodeQty': 44,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '3-Q': {
        'CodeQty': 34,
        'BlockQty': 18,
        'G1Blocks': 2,
        'B1CodeQty': 17,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '3-H': {
        'CodeQty': 26,
        'BlockQty': 22,
        'G1Blocks': 2,
        'B1CodeQty': 13,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '4-L': {
        'CodeQty': 80,
        'BlockQty': 20,
        'G1Blocks': 1,
        'B1CodeQty': 80,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '4-M': {
        'CodeQty': 64,
        'BlockQty': 18,
        'G1Blocks': 2,
        'B1CodeQty': 32,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '4-Q': {
        'CodeQty': 48,
        'BlockQty': 26,
        'G1Blocks': 2,
        'B1CodeQty': 24,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '4-H': {
        'CodeQty': 36,
        'BlockQty': 16,
        'G1Blocks': 4,
        'B1CodeQty': 9,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '5-L': {
        'CodeQty': 108,
        'BlockQty': 26,
        'G1Blocks': 1,
        'B1CodeQty': 108,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '5-M': {
        'CodeQty': 86,
        'BlockQty': 24,
        'G1Blocks': 2,
        'B1CodeQty': 43,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '5-Q': {
        'CodeQty': 62,
        'BlockQty': 18,
        'G1Blocks': 2,
        'B1CodeQty': 15,
        'G2Blocks': 2,
        'B2CodeQty': 16
    },
    '5-H': {
        'CodeQty': 46,
        'BlockQty': 22,
        'G1Blocks': 2,
        'B1CodeQty': 11,
        'G2Blocks': 2,
        'B2CodeQty': 12
    },
    '6-L': {
        'CodeQty': 136,
        'BlockQty': 18,
        'G1Blocks': 2,
        'B1CodeQty': 68,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '6-M': {
        'CodeQty': 108,
        'BlockQty': 16,
        'G1Blocks': 4,
        'B1CodeQty': 27,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '6-Q': {
        'CodeQty': 76,
        'BlockQty': 24,
        'G1Blocks': 4,
        'B1CodeQty': 19,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '6-H': {
        'CodeQty': 60,
        'BlockQty': 28,
        'G1Blocks': 4,
        'B1CodeQty': 15,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '7-L': {
        'CodeQty': 156,
        'BlockQty': 20,
        'G1Blocks': 2,
        'B1CodeQty': 78,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '7-M': {
        'CodeQty': 124,
        'BlockQty': 18,
        'G1Blocks': 4,
        'B1CodeQty': 31,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '7-Q': {
        'CodeQty': 88,
        'BlockQty': 18,
        'G1Blocks': 2,
        'B1CodeQty': 14,
        'G2Blocks': 4,
        'B2CodeQty': 15
    },
    '7-H': {
        'CodeQty': 66,
        'BlockQty': 26,
        'G1Blocks': 4,
        'B1CodeQty': 13,
        'G2Blocks': 1,
        'B2CodeQty': 14
    },
    '8-L': {
        'CodeQty': 194,
        'BlockQty': 24,
        'G1Blocks': 2,
        'B1CodeQty': 97,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '8-M': {
        'CodeQty': 154,
        'BlockQty': 22,
        'G1Blocks': 2,
        'B1CodeQty': 38,
        'G2Blocks': 2,
        'B2CodeQty': 39
    },
    '8-Q': {
        'CodeQty': 110,
        'BlockQty': 22,
        'G1Blocks': 4,
        'B1CodeQty': 18,
        'G2Blocks': 2,
        'B2CodeQty': 19
    },
    '8-H': {
        'CodeQty': 86,
        'BlockQty': 26,
        'G1Blocks': 4,
        'B1CodeQty': 14,
        'G2Blocks': 2,
        'B2CodeQty': 15
    },
    '9-L': {
        'CodeQty': 232,
        'BlockQty': 30,
        'G1Blocks': 2,
        'B1CodeQty': 116,
        'G2Blocks': 0,
        'B2CodeQty': 0
    },
    '9-M': {
        'CodeQty': 182,
        'BlockQty': 22,
        'G1Blocks': 3,
        'B1CodeQty': 36,
        'G2Blocks': 2,
        'B2CodeQty': 37
    },
    '9-Q': {
        'CodeQty': 132,
        'BlockQty': 20,
        'G1Blocks': 4,
        'B1CodeQty': 16,
        'G2Blocks': 4,
        'B2CodeQty': 17
    },
    '9-H': {
        'CodeQty': 100,
        'BlockQty': 24,
        'G1Blocks': 4,
        'B1CodeQty': 12,
        'G2Blocks': 4,
        'B2CodeQty': 13
    },
    '10-L': {
        'CodeQty': 274,
        'BlockQty': 18,
        'G1Blocks': 2,
        'B1CodeQty': 68,
        'G2Blocks': 2,
        'B2CodeQty': 69,
    },
    '10-M': {
        'CodeQty': 216,
        'BlockQty': 26,
        'G1Blocks': 4,
        'B1CodeQty': 43,
        'G2Blocks': 1,
        'B2CodeQty': 44,
    },
    '10-Q': {
        'CodeQty': 154,
        'BlockQty': 24,
        'G1Blocks': 6,
        'B1CodeQty': 19,
        'G2Blocks': 2,
        'B2CodeQty': 20,
    },
    '10-H': {
        'CodeQty': 122,
        'BlockQty': 28,
        'G1Blocks': 6,
        'B1CodeQty': 15,
        'G2Blocks': 2,
        'B2CodeQty': 16,
    },
    '11-L': {
        'CodeQty': 324,
        'BlockQty': 20,
        'G1Blocks': 4,
        'B1CodeQty': 81,
        'G2Blocks': 0,
        'B2CodeQty': 0,
    },
    '11-M': {
        'CodeQty': 254,
        'BlockQty': 30,
        'G1Blocks': 1,
        'B1CodeQty': 50,
        'G2Blocks': 4,
        'B2CodeQty': 51,
    },
    '11-Q': {
        'CodeQty': 180,
        'BlockQty': 28,
        'G1Blocks': 4,
        'B1CodeQty': 22,
        'G2Blocks': 4,
        'B2CodeQty': 23,
    },
    '11-H': {
        'CodeQty': 140,
        'BlockQty': 24,
        'G1Blocks': 3,
        'B1CodeQty': 12,
        'G2Blocks': 8,
        'B2CodeQty': 13,
    },
    '12-L': {
        'CodeQty': 370,
        'BlockQty': 24,
        'G1Blocks': 2,
        'B1CodeQty': 92,
        'G2Blocks': 2,
        'B2CodeQty': 93,
    },
    '12-M': {
        'CodeQty': 290,
        'BlockQty': 22,
        'G1Blocks': 6,
        'B1CodeQty': 36,
        'G2Blocks': 2,
        'B2CodeQty': 37,
    },
    '12-Q': {
        'CodeQty': 206,
        'BlockQty': 26,
        'G1Blocks': 4,
        'B1CodeQty': 20,
        'G2Blocks': 6,
        'B2CodeQty': 21,
    },
    '12-H': {
        'CodeQty': 158,
        'BlockQty': 28,
        'G1Blocks': 7,
        'B1CodeQty': 14,
        'G2Blocks': 4,
        'B2CodeQty': 15,
    },
    '13-L': {
        'CodeQty': 428,
        'BlockQty': 26,
        'G1Blocks': 4,
        'B1CodeQty': 107,
        'G2Blocks': 0,
        'B2CodeQty': 0,
    },
    '13-M': {
        'CodeQty': 334,
        'BlockQty': 22,
        'G1Blocks': 8,
        'B1CodeQty': 37,
        'G2Blocks': 1,
        'B2CodeQty': 38,
    },
    '13-Q': {
        'CodeQty': 244,
        'BlockQty': 24,
        'G1Blocks': 8,
        'B1CodeQty': 20,
        'G2Blocks': 4,
        'B2CodeQty': 21,
    },
    '13-H': {
        'CodeQty': 180,
        'BlockQty': 22,
        'G1Blocks': 12,
        'B1CodeQty': 11,
        'G2Blocks': 4,
        'B2CodeQty': 12,
    },
    '14-L': {
        'CodeQty': 461,
        'BlockQty': 30,
        'G1Blocks': 3,
        'B1CodeQty': 115,
        'G2Blocks': 1,
        'B2CodeQty': 116,
    },
    '14-M': {
        'CodeQty': 365,
        'BlockQty': 24,
        'G1Blocks': 4,
        'B1CodeQty': 40,
        'G2Blocks': 5,
        'B2CodeQty': 41,
    },
    '14-Q': {
        'CodeQty': 261,
        'BlockQty': 20,
        'G1Blocks': 11,
        'B1CodeQty': 16,
        'G2Blocks': 5,
        'B2CodeQty': 17,
    },
    '14-H': {
        'CodeQty': 197,
        'BlockQty': 24,
        'G1Blocks': 11,
        'B1CodeQty': 12,
        'G2Blocks': 5,
        'B2CodeQty': 13,
    },
    '15-L': {
        'CodeQty': 523,
        'BlockQty': 22,
        'G1Blocks': 5,
        'B1CodeQty': 87,
        'G2Blocks': 1,
        'B2CodeQty': 88,
    },
    '15-M': {
        'CodeQty': 415,
        'BlockQty': 24,
        'G1Blocks': 5,
        'B1CodeQty': 41,
        'G2Blocks': 5,
        'B2CodeQty': 42,
    },
    '15-Q': {
        'CodeQty': 295,
        'BlockQty': 30,
        'G1Blocks': 5,
        'B1CodeQty': 24,
        'G2Blocks': 7,
        'B2CodeQty': 25,
    },
    '15-H': {
        'CodeQty': 223,
        'BlockQty': 24,
        'G1Blocks': 11,
        'B1CodeQty': 12,
        'G2Blocks': 7,
        'B2CodeQty': 13,
    },
    '16-L': {
        'CodeQty': 589,
        'BlockQty': 24,
        'G1Blocks': 5,
        'B1CodeQty': 98,
        'G2Blocks': 1,
        'B2CodeQty': 99,
    },
    '16-M': {
        'CodeQty': 453,
        'BlockQty': 28,
        'G1Blocks': 7,
        'B1CodeQty': 45,
        'G2Blocks': 3,
        'B2CodeQty': 46,
    },
    '16-Q': {
        'CodeQty': 325,
        'BlockQty': 24,
        'G1Blocks': 15,
        'B1CodeQty': 19,
        'G2Blocks': 2,
        'B2CodeQty': 20,
    },
    '16-H': {
        'CodeQty': 253,
        'BlockQty': 30,
        'G1Blocks': 3,
        'B1CodeQty': 15,
        'G2Blocks': 13,
        'B2CodeQty': 16,
    },
    '17-L': {
        'CodeQty': 647,
        'BlockQty': 28,
        'G1Blocks': 1,
        'B1CodeQty': 107,
        'G2Blocks': 5,
        'B2CodeQty': 108,
    },
    '17-M': {
        'CodeQty': 507,
        'BlockQty': 28,
        'G1Blocks': 10,
        'B1CodeQty': 46,
        'G2Blocks': 1,
        'B2CodeQty': 47,
    },
    '17-Q': {
        'CodeQty': 367,
        'BlockQty': 28,
        'G1Blocks': 1,
        'B1CodeQty': 22,
        'G2Blocks': 15,
        'B2CodeQty': 23,
    },
    '17-H': {
        'CodeQty': 283,
        'BlockQty': 28,
        'G1Blocks': 2,
        'B1CodeQty': 14,
        'G2Blocks': 17,
        'B2CodeQty': 15,
    },
    '18-L': {
        'CodeQty': 721,
        'BlockQty': 30,
        'G1Blocks': 5,
        'B1CodeQty': 120,
        'G2Blocks': 1,
        'B2CodeQty': 121,
    },
    '18-M': {
        'CodeQty': 563,
        'BlockQty': 26,
        'G1Blocks': 9,
        'B1CodeQty': 43,
        'G2Blocks': 4,
        'B2CodeQty': 44,
    },
    '18-Q': {
        'CodeQty': 397,
        'BlockQty': 28,
        'G1Blocks': 17,
        'B1CodeQty': 22,
        'G2Blocks': 1,
        'B2CodeQty': 23,
    },
    '18-H': {
        'CodeQty': 313,
        'BlockQty': 28,
        'G1Blocks': 2,
        'B1CodeQty': 14,
        'G2Blocks': 19,
        'B2CodeQty': 15,
    },
    '19-L': {
        'CodeQty': 795,
        'BlockQty': 28,
        'G1Blocks': 3,
        'B1CodeQty': 113,
        'G2Blocks': 4,
        'B2CodeQty': 114,
    },
    '19-M': {
        'CodeQty': 627,
        'BlockQty': 26,
        'G1Blocks': 3,
        'B1CodeQty': 44,
        'G2Blocks': 11,
        'B2CodeQty': 45,
    },
    '19-Q': {
        'CodeQty': 445,
        'BlockQty': 26,
        'G1Blocks': 17,
        'B1CodeQty': 21,
        'G2Blocks': 4,
        'B2CodeQty': 22,
    },
    '19-H': {
        'CodeQty': 341,
        'BlockQty': 26,
        'G1Blocks': 9,
        'B1CodeQty': 13,
        'G2Blocks': 16,
        'B2CodeQty': 14,
    },
    '20-L': {
        'CodeQty': 861,
        'BlockQty': 28,
        'G1Blocks': 3,
        'B1CodeQty': 107,
        'G2Blocks': 5,
        'B2CodeQty': 108,
    },
    '20-M': {
        'CodeQty': 669,
        'BlockQty': 26,
        'G1Blocks': 3,
        'B1CodeQty': 41,
        'G2Blocks': 13,
        'B2CodeQty': 42,
    },
    '20-Q': {
        'CodeQty': 485,
        'BlockQty': 30,
        'G1Blocks': 15,
        'B1CodeQty': 24,
        'G2Blocks': 5,
        'B2CodeQty': 25,
    },
    '20-H': {
        'CodeQty': 385,
        'BlockQty': 28,
        'G1Blocks': 15,
        'B1CodeQty': 15,
        'G2Blocks': 10,
        'B2CodeQty': 16,
    },
    '21-L': {
        'CodeQty': 932,
        'BlockQty': 28,
        'G1Blocks': 4,
        'B1CodeQty': 116,
        'G2Blocks': 4,
        'B2CodeQty': 117,
    },
    '21-M': {
        'CodeQty': 714,
        'BlockQty': 26,
        'G1Blocks': 17,
        'B1CodeQty': 42,
        'G2Blocks': 0,
        'B2CodeQty': 0,
    },
    '21-Q': {
        'CodeQty': 512,
        'BlockQty': 28,
        'G1Blocks': 17,
        'B1CodeQty': 22,
        'G2Blocks': 6,
        'B2CodeQty': 23,
    },
    '21-H': {
        'CodeQty': 406,
        'BlockQty': 30,
        'G1Blocks': 19,
        'B1CodeQty': 16,
        'G2Blocks': 6,
        'B2CodeQty': 17,
    },
    '22-L': {
        'CodeQty': 1006,
        'BlockQty': 28,
        'G1Blocks': 2,
        'B1CodeQty': 111,
        'G2Blocks': 7,
        'B2CodeQty': 112,
    },
    '22-M': {
        'CodeQty': 782,
        'BlockQty': 28,
        'G1Blocks': 17,
        'B1CodeQty': 46,
        'G2Blocks': 0,
        'B2CodeQty': 0,
    },
    '22-Q': {
        'CodeQty': 568,
        'BlockQty': 30,
        'G1Blocks': 7,
        'B1CodeQty': 24,
        'G2Blocks': 16,
        'B2CodeQty': 25,
    },
    '22-H': {
        'CodeQty': 442,
        'BlockQty': 24,
        'G1Blocks': 34,
        'B1CodeQty': 13,
        'G2Blocks': 0,
        'B2CodeQty': 0,
    },
    '23-L': {
        'CodeQty': 1094,
        'BlockQty': 30,
        'G1Blocks': 4,
        'B1CodeQty': 121,
        'G2Blocks': 5,
        'B2CodeQty': 122,
    },
    '23-M': {
        'CodeQty': 860,
        'BlockQty': 28,
        'G1Blocks': 4,
        'B1CodeQty': 47,
        'G2Blocks': 14,
        'B2CodeQty': 48,
    },
    '23-Q': {
        'CodeQty': 614,
        'BlockQty': 30,
        'G1Blocks': 11,
        'B1CodeQty': 24,
        'G2Blocks': 14,
        'B2CodeQty': 25,
    },
    '23-H': {
        'CodeQty': 464,
        'BlockQty': 30,
        'G1Blocks': 16,
        'B1CodeQty': 15,
        'G2Blocks': 14,
        'B2CodeQty': 16,
    },
    '24-L': {
        'CodeQty': 1174,
        'BlockQty': 30,
        'G1Blocks': 6,
        'B1CodeQty': 117,
        'G2Blocks': 4,
        'B2CodeQty': 118,
    },
    '24-M': {
        'CodeQty': 914,
        'BlockQty': 28,
        'G1Blocks': 6,
        'B1CodeQty': 45,
        'G2Blocks': 14,
        'B2CodeQty': 46,
    },
    '24-Q': {
        'CodeQty': 664,
        'BlockQty': 30,
        'G1Blocks': 11,
        'B1CodeQty': 24,
        'G2Blocks': 16,
        'B2CodeQty': 25,
    },
    '24-H': {
        'CodeQty': 514,
        'BlockQty': 30,
        'G1Blocks': 30,
        'B1CodeQty': 16,
        'G2Blocks': 2,
        'B2CodeQty': 17,
    },
    '25-L': {
        'CodeQty': 1276,
        'BlockQty': 26,
        'G1Blocks': 8,
        'B1CodeQty': 106,
        'G2Blocks': 4,
        'B2CodeQty': 107,
    },
    '25-M': {
        'CodeQty': 1000,
        'BlockQty': 28,
        'G1Blocks': 8,
        'B1CodeQty': 47,
        'G2Blocks': 13,
        'B2CodeQty': 48,
    },
    '25-Q': {
        'CodeQty': 718,
        'BlockQty': 30,
        'G1Blocks': 7,
        'B1CodeQty': 24,
        'G2Blocks': 22,
        'B2CodeQty': 25,
    },
    '25-H': {
        'CodeQty': 538,
        'BlockQty': 30,
        'G1Blocks': 22,
        'B1CodeQty': 15,
        'G2Blocks': 13,
        'B2CodeQty': 16,
    },
    '26-L': {
        'CodeQty': 1370,
        'BlockQty': 28,
        'G1Blocks': 10,
        'B1CodeQty': 114,
        'G2Blocks': 2,
        'B2CodeQty': 115,
    },
    '26-M': {
        'CodeQty': 1062,
        'BlockQty': 28,
        'G1Blocks': 19,
        'B1CodeQty': 46,
        'G2Blocks': 4,
        'B2CodeQty': 47,
    },
    '26-Q': {
        'CodeQty': 754,
        'BlockQty': 28,
        'G1Blocks': 28,
        'B1CodeQty': 22,
        'G2Blocks': 6,
        'B2CodeQty': 23,
    },
    '26-H': {
        'CodeQty': 596,
        'BlockQty': 30,
        'G1Blocks': 33,
        'B1CodeQty': 16,
        'G2Blocks': 4,
        'B2CodeQty': 17,
    },
    '27-L': {
        'CodeQty': 1468,
        'BlockQty': 30,
        'G1Blocks': 8,
        'B1CodeQty': 122,
        'G2Blocks': 4,
        'B2CodeQty': 123,
    },
    '27-M': {
        'CodeQty': 1128,
        'BlockQty': 28,
        'G1Blocks': 22,
        'B1CodeQty': 45,
        'G2Blocks': 3,
        'B2CodeQty': 46,
    },
    '27-Q': {
        'CodeQty': 808,
        'BlockQty': 30,
        'G1Blocks': 8,
        'B1CodeQty': 23,
        'G2Blocks': 26,
        'B2CodeQty': 24,
    },
    '27-H': {
        'CodeQty': 628,
        'BlockQty': 30,
        'G1Blocks': 12,
        'B1CodeQty': 15,
        'G2Blocks': 28,
        'B2CodeQty': 16,
    },
    '28-L': {
        'CodeQty': 1531,
        'BlockQty': 30,
        'G1Blocks': 3,
        'B1CodeQty': 117,
        'G2Blocks': 10,
        'B2CodeQty': 118,
    },
    '28-M': {
        'CodeQty': 1193,
        'BlockQty': 28,
        'G1Blocks': 3,
        'B1CodeQty': 45,
        'G2Blocks': 23,
        'B2CodeQty': 46,
    },
    '28-Q': {
        'CodeQty': 871,
        'BlockQty': 30,
        'G1Blocks': 4,
        'B1CodeQty': 24,
        'G2Blocks': 31,
        'B2CodeQty': 25,
    },
    '28-H': {
        'CodeQty': 661,
        'BlockQty': 30,
        'G1Blocks': 11,
        'B1CodeQty': 15,
        'G2Blocks': 31,
        'B2CodeQty': 16,
    },
    '29-L': {
        'CodeQty': 1631,
        'BlockQty': 30,
        'G1Blocks': 7,
        'B1CodeQty': 116,
        'G2Blocks': 7,
        'B2CodeQty': 117,
    },
    '29-M': {
        'CodeQty': 1267,
        'BlockQty': 28,
        'G1Blocks': 21,
        'B1CodeQty': 45,
        'G2Blocks': 7,
        'B2CodeQty': 46,
    },
    '29-Q': {
        'CodeQty': 911,
        'BlockQty': 30,
        'G1Blocks': 1,
        'B1CodeQty': 23,
        'G2Blocks': 37,
        'B2CodeQty': 24,
    },
    '29-H': {
        'CodeQty': 701,
        'BlockQty': 30,
        'G1Blocks': 19,
        'B1CodeQty': 15,
        'G2Blocks': 26,
        'B2CodeQty': 16,
    },
    '30-L': {
        'CodeQty': 1735,
        'BlockQty': 30,
        'G1Blocks': 5,
        'B1CodeQty': 115,
        'G2Blocks': 10,
        'B2CodeQty': 116,
    },
    '30-M': {
        'CodeQty': 1373,
        'BlockQty': 28,
        'G1Blocks': 19,
        'B1CodeQty': 47,
        'G2Blocks': 10,
        'B2CodeQty': 48,
    },
    '30-Q': {
        'CodeQty': 985,
        'BlockQty': 30,
        'G1Blocks': 15,
        'B1CodeQty': 24,
        'G2Blocks': 25,
        'B2CodeQty': 25,
    },
    '30-H': {
        'CodeQty': 745,
        'BlockQty': 30,
        'G1Blocks': 23,
        'B1CodeQty': 15,
        'G2Blocks': 25,
        'B2CodeQty': 16,
    },
    '31-L': {
        'CodeQty': 1843,
        'BlockQty': 30,
        'G1Blocks': 13,
        'B1CodeQty': 115,
        'G2Blocks': 3,
        'B2CodeQty': 116,
    },
    '31-M': {
        'CodeQty': 1455,
        'BlockQty': 28,
        'G1Blocks': 2,
        'B1CodeQty': 46,
        'G2Blocks': 29,
        'B2CodeQty': 47,
    },
    '31-Q': {
        'CodeQty': 1033,
        'BlockQty': 30,
        'G1Blocks': 42,
        'B1CodeQty': 24,
        'G2Blocks': 1,
        'B2CodeQty': 25,
    },
    '31-H': {
        'CodeQty': 793,
        'BlockQty': 30,
        'G1Blocks': 23,
        'B1CodeQty': 15,
        'G2Blocks': 28,
        'B2CodeQty': 16,
    },
    '32-L': {
        'CodeQty': 1955,
        'BlockQty': 30,
        'G1Blocks': 17,
        'B1CodeQty': 115,
        'G2Blocks': 0,
        'B2CodeQty': 0,
    },
    '32-M': {
        'CodeQty': 1541,
        'BlockQty': 28,
        'G1Blocks': 10,
        'B1CodeQty': 46,
        'G2Blocks': 23,
        'B2CodeQty': 47,
    },
    '32-Q': {
        'CodeQty': 1115,
        'BlockQty': 30,
        'G1Blocks': 10,
        'B1CodeQty': 24,
        'G2Blocks': 35,
        'B2CodeQty': 25,
    },
    '32-H': {
        'CodeQty': 845,
        'BlockQty': 30,
        'G1Blocks': 19,
        'B1CodeQty': 15,
        'G2Blocks': 35,
        'B2CodeQty': 16,
    },
    '33-L': {
        'CodeQty': 2071,
        'BlockQty': 30,
        'G1Blocks': 17,
        'B1CodeQty': 115,
        'G2Blocks': 1,
        'B2CodeQty': 116,
    },
    '33-M': {
        'CodeQty': 1631,
        'BlockQty': 28,
        'G1Blocks': 14,
        'B1CodeQty': 46,
        'G2Blocks': 21,
        'B2CodeQty': 47,
    },
    '33-Q': {
        'CodeQty': 1171,
        'BlockQty': 30,
        'G1Blocks': 29,
        'B1CodeQty': 24,
        'G2Blocks': 19,
        'B2CodeQty': 25,
    },
    '33-H': {
        'CodeQty': 901,
        'BlockQty': 30,
        'G1Blocks': 11,
        'B1CodeQty': 15,
        'G2Blocks': 46,
        'B2CodeQty': 16,
    },
    '34-L': {
        'CodeQty': 2191,
        'BlockQty': 30,
        'G1Blocks': 13,
        'B1CodeQty': 115,
        'G2Blocks': 6,
        'B2CodeQty': 116,
    },
    '34-M': {
        'CodeQty': 1725,
        'BlockQty': 28,
        'G1Blocks': 14,
        'B1CodeQty': 46,
        'G2Blocks': 23,
        'B2CodeQty': 47,
    },
    '34-Q': {
        'CodeQty': 1231,
        'BlockQty': 30,
        'G1Blocks': 44,
        'B1CodeQty': 24,
        'G2Blocks': 7,
        'B2CodeQty': 25,
    },
    '34-H': {
        'CodeQty': 961,
        'BlockQty': 30,
        'G1Blocks': 59,
        'B1CodeQty': 16,
        'G2Blocks': 1,
        'B2CodeQty': 17,
    },
    '35-L': {
        'CodeQty': 2306,
        'BlockQty': 30,
        'G1Blocks': 12,
        'B1CodeQty': 121,
        'G2Blocks': 7,
        'B2CodeQty': 122,
    },
    '35-M': {
        'CodeQty': 1812,
        'BlockQty': 28,
        'G1Blocks': 12,
        'B1CodeQty': 47,
        'G2Blocks': 26,
        'B2CodeQty': 48,
    },
    '35-Q': {
        'CodeQty': 1286,
        'BlockQty': 30,
        'G1Blocks': 39,
        'B1CodeQty': 24,
        'G2Blocks': 14,
        'B2CodeQty': 25,
    },
    '35-H': {
        'CodeQty': 986,
        'BlockQty': 30,
        'G1Blocks': 22,
        'B1CodeQty': 15,
        'G2Blocks': 41,
        'B2CodeQty': 16,
    },
    '36-L': {
        'CodeQty': 2434,
        'BlockQty': 30,
        'G1Blocks': 6,
        'B1CodeQty': 121,
        'G2Blocks': 14,
        'B2CodeQty': 122,
    },
    '36-M': {
        'CodeQty': 1914,
        'BlockQty': 28,
        'G1Blocks': 6,
        'B1CodeQty': 47,
        'G2Blocks': 34,
        'B2CodeQty': 48,
    },
    '36-Q': {
        'CodeQty': 1354,
        'BlockQty': 30,
        'G1Blocks': 46,
        'B1CodeQty': 24,
        'G2Blocks': 10,
        'B2CodeQty': 25,
    },
    '36-H': {
        'CodeQty': 1054,
        'BlockQty': 30,
        'G1Blocks': 2,
        'B1CodeQty': 15,
        'G2Blocks': 64,
        'B2CodeQty': 16,
    },
    '37-L': {
        'CodeQty': 2566,
        'BlockQty': 30,
        'G1Blocks': 17,
        'B1CodeQty': 122,
        'G2Blocks': 4,
        'B2CodeQty': 123,
    },
    '37-M': {
        'CodeQty': 1992,
        'BlockQty': 28,
        'G1Blocks': 29,
        'B1CodeQty': 46,
        'G2Blocks': 14,
        'B2CodeQty': 47,
    },
    '37-Q': {
        'CodeQty': 1426,
        'BlockQty': 30,
        'G1Blocks': 49,
        'B1CodeQty': 24,
        'G2Blocks': 10,
        'B2CodeQty': 25,
    },
    '37-H': {
        'CodeQty': 1096,
        'BlockQty': 30,
        'G1Blocks': 24,
        'B1CodeQty': 15,
        'G2Blocks': 46,
        'B2CodeQty': 16,
    },
    '38-L': {
        'CodeQty': 2702,
        'BlockQty': 30,
        'G1Blocks': 4,
        'B1CodeQty': 122,
        'G2Blocks': 18,
        'B2CodeQty': 123,
    },
    '38-M': {
        'CodeQty': 2102,
        'BlockQty': 28,
        'G1Blocks': 13,
        'B1CodeQty': 46,
        'G2Blocks': 32,
        'B2CodeQty': 47,
    },
    '38-Q': {
        'CodeQty': 1502,
        'BlockQty': 30,
        'G1Blocks': 48,
        'B1CodeQty': 24,
        'G2Blocks': 14,
        'B2CodeQty': 25,
    },
    '38-H': {
        'CodeQty': 1142,
        'BlockQty': 30,
        'G1Blocks': 42,
        'B1CodeQty': 15,
        'G2Blocks': 32,
        'B2CodeQty': 16,
    },
    '39-L': {
        'CodeQty': 2812,
        'BlockQty': 30,
        'G1Blocks': 20,
        'B1CodeQty': 117,
        'G2Blocks': 4,
        'B2CodeQty': 118,
    },
    '39-M': {
        'CodeQty': 2216,
        'BlockQty': 28,
        'G1Blocks': 40,
        'B1CodeQty': 47,
        'G2Blocks': 7,
        'B2CodeQty': 48,
    },
    '39-Q': {
        'CodeQty': 1582,
        'BlockQty': 30,
        'G1Blocks': 43,
        'B1CodeQty': 24,
        'G2Blocks': 22,
        'B2CodeQty': 25,
    },
    '39-H': {
        'CodeQty': 1222,
        'BlockQty': 30,
        'G1Blocks': 10,
        'B1CodeQty': 15,
        'G2Blocks': 67,
        'B2CodeQty': 16,
    },
    '40-L': {
        'CodeQty': 2956,
        'BlockQty': 30,
        'G1Blocks': 19,
        'B1CodeQty': 118,
        'G2Blocks': 6,
        'B2CodeQty': 119,
    },
    '40-M': {
        'CodeQty': 2334,
        'BlockQty': 28,
        'G1Blocks': 18,
        'B1CodeQty': 47,
        'G2Blocks': 31,
        'B2CodeQty': 48,
    },
    '40-Q': {
        'CodeQty': 1666,
        'BlockQty': 30,
        'G1Blocks': 34,
        'B1CodeQty': 24,
        'G2Blocks': 34,
        'B2CodeQty': 25,
    },
    '40-H': {
        'CodeQty': 1276,
        'BlockQty': 30,
        'G1Blocks': 20,
        'B1CodeQty': 15,
        'G2Blocks': 61,
        'B2CodeQty': 16,
    },
}

character_capacities = {
    "Low": {
        "Value_Data": [
            (1, 41, 25, 17, 10),
            (2, 77, 47, 32, 20),
            (3, 127, 77, 53, 32),
            (4, 187, 114, 78, 48),
            (5, 255, 154, 106, 65),
            (6, 322, 195, 134, 82),
            (7, 370, 224, 154, 95),
            (8, 461, 279, 192, 118),
            (9, 552, 335, 230, 141),
            (10, 652, 395, 271, 167),
            (11, 772, 468, 321, 198),
            (12, 883, 535, 367, 226),
            (13, 1022, 619, 425, 262),
            (14, 1101, 667, 458, 282),
            (15, 1250, 758, 520, 320),
            (16, 1408, 854, 586, 361),
            (17, 1548, 938, 644, 397),
            (18, 1725, 1046, 718, 442),
            (19, 1903, 1153, 792, 488),
            (20, 2061, 1249, 858, 528),
            (21, 2232, 1352, 929, 572),
            (22, 2409, 1460, 1003, 618),
            (23, 2620, 1588, 1091, 672),
            (24, 2812, 1704, 1171, 721),
            (25, 3057, 1853, 1273, 784),
            (26, 3283, 1990, 1367, 842),
            (27, 3517, 2132, 1465, 902),
            (28, 3669, 2223, 1528, 940),
            (29, 3909, 2369, 1628, 1002),
            (30, 4158, 2520, 1732, 1066),
            (31, 4417, 2677, 1840, 1132),
            (32, 4686, 2840, 1952, 1201),
            (33, 4965, 3009, 2068, 1273),
            (34, 5253, 3183, 2188, 1347),
            (35, 5529, 3351, 2303, 1417),
            (36, 5836, 3537, 2431, 1496),
            (37, 6153, 3729, 2563, 1577),
            (38, 6479, 3927, 2699, 1661),
            (39, 6743, 4087, 2809, 1729),
            (40, 7089, 4296, 2953, 1817),
        ]
    },
    "Medium": {
        "Value_Data": [
            (1, 34, 20, 14, 8),
            (2, 63, 38, 26, 16),
            (3, 101, 61, 42, 26),
            (4, 149, 90, 62, 38),
            (5, 202, 122, 84, 52),
            (6, 255, 154, 106, 65),
            (7, 293, 178, 122, 75),
            (8, 365, 221, 152, 93),
            (9, 432, 262, 180, 111),
            (10, 513, 311, 213, 131),
            (11, 604, 366, 251, 155),
            (12, 691, 419, 287, 177),
            (13, 796, 483, 331, 204),
            (14, 871, 528, 362, 223),
            (15, 991, 600, 412, 254),
            (16, 1082, 656, 450, 277),
            (17, 1212, 734, 504, 310),
            (18, 1346, 816, 560, 345),
            (19, 1500, 909, 624, 384),
            (20, 1600, 970, 666, 410),
            (21, 1708, 1035, 711, 438),
            (22, 1872, 1134, 779, 480),
            (23, 2059, 1248, 857, 528),
            (24, 2188, 1326, 911, 561),
            (25, 2395, 1451, 997, 614),
            (26, 2544, 1542, 1059, 652),
            (27, 2701, 1637, 1125, 692),
            (28, 2857, 1732, 1190, 732),
            (29, 3035, 1839, 1264, 778),
            (30, 3289, 1994, 1370, 843),
            (31, 3486, 2113, 1452, 894),
            (32, 3693, 2238, 1538, 947),
            (33, 3909, 2369, 1628, 1002),
            (34, 4134, 2506, 1722, 1060),
            (35, 4343, 2632, 1809, 1113),
            (36, 4588, 2780, 1911, 1176),
            (37, 4775, 2894, 1989, 1224),
            (38, 5039, 3054, 2099, 1292),
            (39, 5313, 3220, 2213, 1362),
            (40, 5596, 3391, 2331, 1435),
        ]
    },
    "Quartile": {
        "Value_Data": [
            (1, 27, 16, 11, 7),
            (2, 48, 29, 20, 12),
            (3, 77, 47, 32, 20),
            (4, 111, 67, 46, 28),
            (5, 144, 87, 60, 37),
            (6, 178, 108, 74, 45),
            (7, 207, 125, 86, 53),
            (8, 259, 157, 108, 66),
            (9, 312, 189, 130, 80),
            (10, 364, 221, 151, 93),
            (11, 427, 259, 177, 109),
            (12, 489, 296, 203, 125),
            (13, 580, 352, 241, 149),
            (14, 621, 376, 258, 159),
            (15, 703, 426, 292, 180),
            (16, 775, 470, 322, 198),
            (17, 876, 531, 364, 224),
            (18, 948, 574, 394, 243),
            (19, 1063, 644, 442, 272),
            (20, 1159, 702, 482, 297),
            (21, 1224, 742, 509, 314),
            (22, 1358, 823, 565, 348),
            (23, 1468, 890, 611, 376),
            (24, 1588, 963, 661, 407),
            (25, 1718, 1041, 715, 440),
            (26, 1804, 1094, 751, 462),
            (27, 1933, 1172, 805, 496),
            (28, 2085, 1263, 868, 534),
            (29, 2181, 1322, 908, 559),
            (30, 2358, 1429, 982, 604),
            (31, 2473, 1499, 1030, 634),
            (32, 2670, 1618, 1112, 684),
            (33, 2805, 1700, 1168, 719),
            (34, 2949, 1787, 1228, 756),
            (35, 3081, 1867, 1283, 790),
            (36, 3244, 1966, 1351, 832),
            (37, 3417, 2071, 1423, 876),
            (38, 3599, 2181, 1499, 923),
            (39, 3791, 2298, 1579, 972),
            (40, 3993, 2420, 1663, 1024),
        ]
    },
    "High": {
        "Value_Data": [
            (1, 17, 10, 7, 4),
            (2, 34, 20, 14, 8),
            (3, 58, 35, 24, 15),
            (4, 82, 50, 34, 21),
            (5, 106, 64, 44, 27),
            (6, 139, 84, 58, 36),
            (7, 154, 93, 64, 39),
            (8, 202, 122, 84, 52),
            (9, 235, 143, 98, 60),
            (10, 288, 174, 119, 74),
            (11, 331, 200, 137, 85),
            (12, 374, 227, 155, 96),
            (13, 427, 259, 177, 109),
            (14, 468, 283, 194, 120),
            (15, 530, 321, 220, 136),
            (16, 602, 365, 250, 154),
            (17, 674, 408, 280, 173),
            (18, 746, 452, 310, 191),
            (19, 813, 493, 338, 208),
            (20, 919, 557, 382, 235),
            (21, 969, 587, 403, 248),
            (22, 1056, 640, 439, 270),
            (23, 1108, 672, 461, 284),
            (24, 1228, 744, 511, 315),
            (25, 1286, 779, 535, 330),
            (26, 1425, 864, 593, 365),
            (27, 1501, 910, 625, 385),
            (28, 1581, 958, 658, 405),
            (29, 1677, 1016, 698, 430),
            (30, 1782, 1080, 742, 457),
            (31, 1897, 1150, 790, 486),
            (32, 2022, 1226, 842, 518),
            (33, 2157, 1307, 898, 553),
            (34, 2301, 1394, 958, 590),
            (35, 2361, 1431, 983, 605),
            (36, 2524, 1530, 1051, 647),
            (37, 2625, 1591, 1093, 673),
            (38, 2735, 1658, 1139, 701),
            (39, 2927, 1774, 1219, 750),
            (40, 3057, 1852, 1273, 784),
        ]
    },
}

alpha_numeric = {
    'Chars': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
              'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', ' ', '$',
              '%', '*', '+', '-', '.', '/', ':'],
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'A': 10,
    'B': 11,
    'C': 12,
    'D': 13,
    'E': 14,
    'F': 15,
    'G': 16,
    'H': 17,
    'I': 18,
    'J': 19,
    'K': 20,
    'L': 21,
    'M': 22,
    'N': 23,
    'O': 24,
    'P': 25,
    'Q': 26,
    'R': 27,
    'S': 28,
    'T': 29,
    'U': 30,
    'V': 31,
    'W': 32,
    'X': 33,
    'Y': 34,
    'Z': 35,
    ' ': 36,
    '$': 37,
    '%': 38,
    '*': 39,
    '+': 40,
    '-': 41,
    '.': 42,
    '/': 43,
    ':': 44,
}

mode_indicators = {
    'Numeric': '0001',
    'Alphanumeric': '0010',
    'Byte': '0100',
    'Kanji': '1000', # not currently configured
    'ECI': '0111', # not currently configured
}

char_fill = {
    'Numeric': {
        '9': 10,
        '26': 12,
        '40': 14
    },
    'Alphanumeric': {
        '9': 9,
        '26': 11,
        '40': 13
    },
    'Byte': {
        '9': 8,
        '26': 16,
        '40': 16
    },
}

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



