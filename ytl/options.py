
PackingUnitPallet = 'PALLET'
PackingUnitBox = 'BOX'

PACKING_OPTIONS = [
    (PackingUnitPallet, 'Palletized Freight'),
    (PackingUnitBox, 'Box'),
]

DimUomInches = 'IN'
DimUomFeet = 'FT'
DimUomMeter = 'METER'

DIMENSION_UNIT_OF_MEASURE_OPTIONS = [
    (DimUomInches, 'Inches'),
    (DimUomFeet, 'Feet'),
    (DimUomMeter, 'Meters'),
]

VolumeUomCubicInches = 'CUBIC_IN'
VolumeUomCubicFeet = 'CUBIC_FT'
VolumeUomCubicMeters = 'CUBIC_METER'

VOLUME_UNIT_OF_MEASURE_OPTIONS = [
    (VolumeUomCubicInches, 'Cubic Inches'),
    (VolumeUomCubicFeet, 'Cubic Feet'),
    (VolumeUomCubicMeters, 'Cubic Meters'),
]

WeightUomPounds = 'LBS'
WeightUomKilgrams = 'KG'
WeightUomGrams = 'G'

WEIGHT_UNIT_OF_MEASURE_OPTIONS = [
    (WeightUomPounds, 'Pound'),
    (WeightUomKilgrams, 'Kilograms'),
    (WeightUomGrams, 'Grams'),
]
