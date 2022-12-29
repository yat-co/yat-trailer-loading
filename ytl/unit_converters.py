
from . import options

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
    options.DimUomInches: {
        options.DimUomInches: lambda x: x,
        options.DimUomFeet: lambda x: x / INCHES_PER_FOOT,
        options.DimUomMeter: lambda x: x / INCHES_PER_METER,
    },
    options.DimUomFeet: {
        options.DimUomInches: lambda x: INCHES_PER_FOOT * x,
        options.DimUomFeet: lambda x: x,
        options.DimUomMeter: lambda x: x * INCHES_PER_FOOT / INCHES_PER_METER,
    },
    options.DimUomMeter: {
        options.DimUomInches: lambda x: INCHES_PER_METER * x,
        options.DimUomFeet: lambda x: x * INCHES_PER_METER / INCHES_PER_FOOT,
        options.DimUomMeter: lambda x: x,
    },
}

VOLUME_CONVERTER = {
    options.VolumeUomCubicInches: {
        options.VolumeUomCubicInches: lambda x: x,
        options.VolumeUomCubicFeet: lambda x: x / INCHES_PER_FOOT ** 3,
        options.VolumeUomCubicMeters: lambda x: x / INCHES_PER_METER ** 3,
    },
    options.VolumeUomCubicFeet: {
        options.VolumeUomCubicInches: lambda x: INCHES_PER_FOOT ** 3 * x,
        options.VolumeUomCubicFeet: lambda x: x,
        options.VolumeUomCubicMeters: lambda x: x * INCHES_PER_FOOT ** 3 / INCHES_PER_METER ** 3,
    },
    options.VolumeUomCubicMeters: {
        options.VolumeUomCubicInches: lambda x: INCHES_PER_METER ** 3 * x,
        options.VolumeUomCubicFeet: lambda x: x * INCHES_PER_METER ** 3 / INCHES_PER_FOOT ** 3,
        options.VolumeUomCubicMeters: lambda x: x,
    },
}

WEIGHT_CONVERTER = {
    options.WeightUomPounds: {
        options.WeightUomPounds: lambda x: x,
        options.WeightUomKilgrams: lambda x: x / POUNDS_PER_KILOGRAM,
        options.WeightUomGrams: lambda x: x / POUNDS_PER_GRAM,
    },
    options.WeightUomKilgrams: {
        options.WeightUomPounds: lambda x: x * POUNDS_PER_KILOGRAM,
        options.WeightUomKilgrams: lambda x: x,
        options.WeightUomGrams: lambda x: x * POUNDS_PER_KILOGRAM / POUNDS_PER_GRAM,
    },
    options.WeightUomGrams: {
        options.WeightUomPounds: lambda x: x * POUNDS_PER_GRAM,
        options.WeightUomKilgrams: lambda x: x * POUNDS_PER_GRAM / POUNDS_PER_KILOGRAM,
        options.WeightUomGrams: lambda x: x,
    },
}
