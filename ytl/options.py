
PACKING_OPTIONS = [
    ('PALLET', 'Palletized Freight'),
    ('BOX', 'Box'),
]

DIMENSION_UNIT_OF_MEASURE_OPTIONS = [
    ('IN', 'Inches'),
    ('FT', 'Feet'),
    ('METER', 'Meters'),
]

VOLUME_UNIT_OF_MEASURE_OPTIONS = [
    (f'CUBIC_{k}', f'Cubic {v}') for (k, v) in DIMENSION_UNIT_OF_MEASURE_OPTIONS
]

WEIGHT_UNIT_OF_MEASURE_OPTIONS = [
    ('LBS', 'Pound'),
    ('KG', 'Kilograms'),
    ('G', 'Grams'),
]
