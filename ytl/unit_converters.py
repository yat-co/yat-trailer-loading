
'''
Generic Unility Functions for Conversting between Various Units

Usage is:

    DIMENSION_CONVERTER[<convert from unit : str>][<convert to unit : str>](<from unit value : float>)
        >> <to unit value : float>
    DIMENSION_CONVERTER['IN']['FT'](12)
        >> 1
    Similar usage for VOLUME_CONVERTER and WEIGHT_CONVERTER
'''

INCHES_PER_FOOT = 12
INCHES_PER_METER = 39.3701

POUNDS_PER_KILOGRAM = 2.20462
POUNDS_PER_GRAM = POUNDS_PER_KILOGRAM / 1000

DIMENSION_CONVERTER = {
    'IN': {
        'IN': lambda x: x,
        'FT': lambda x: x / INCHES_PER_FOOT,
        'METER': lambda x: x / INCHES_PER_METER,
    },
    'FT': {
        'IN': lambda x: INCHES_PER_FOOT * x,
        'FT': lambda x: x,
        'METER': lambda x: x * INCHES_PER_FOOT / INCHES_PER_METER,
    },
    'METER': {
        'IN': lambda x: INCHES_PER_METER * x,
        'FT': lambda x: x * INCHES_PER_METER / INCHES_PER_FOOT,
        'METER': lambda x: x,
    },
}

VOLUME_CONVERTER = {
    'CUBIC_IN': {
        'CUBIC_IN': lambda x: x,
        'CUBIC_FT': lambda x: x / INCHES_PER_FOOT ** 3,
        'CUBIC_METER': lambda x: x / INCHES_PER_METER ** 3,
    },
    'CUBIC_FT': {
        'CUBIC_IN': lambda x: INCHES_PER_FOOT ** 3 * x,
        'CUBIC_FT': lambda x: x,
        'CUBIC_METER': lambda x: x * INCHES_PER_FOOT ** 3 / INCHES_PER_METER ** 3,
    },
    'CUBIC_METER': {
        'CUBIC_IN': lambda x: INCHES_PER_METER ** 3 * x,
        'CUBIC_FT': lambda x: x * INCHES_PER_METER ** 3 / INCHES_PER_FOOT ** 3,
        'CUBIC_METER': lambda x: x,
    },
}

WEIGHT_CONVERTER = {
    'LBS': {
        'LBS': lambda x: x,
        'KG': lambda x: x / POUNDS_PER_KILOGRAM,
        'G': lambda x: x / POUNDS_PER_GRAM,
    },
    'KG': {
        'LBS': lambda x: x * POUNDS_PER_KILOGRAM,
        'KG': lambda x: x,
        'G': lambda x: x * POUNDS_PER_KILOGRAM / POUNDS_PER_GRAM,
    },
    'G': {
        'LBS': lambda x: x * POUNDS_PER_GRAM,
        'KG': lambda x: x * POUNDS_PER_GRAM / POUNDS_PER_KILOGRAM,
        'G': lambda x: x,
    },
}
