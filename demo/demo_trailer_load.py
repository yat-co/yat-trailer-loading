from ytl.standard_logistic_dims import STANDARD_TRAILER_DIMS
from ytl import optimize_trailer_load_plan

import numpy as np
import time


def generate_random_piece(blockout):
    return {
        'length': np.random.choice(a=[i for i in range(blockout, 60, 1) if i >= 14]),
        'width': np.random.choice(a=[i for i in range(blockout, 60, 1) if i >= 14]),
        'height': np.random.choice(a=list(range(24, 48))),
        'dimension_unit_of_measure': 'IN',
        'weight': np.random.choice(a=list(range(75, 400, 25))+[750]),
        'weight_unit_of_measure': 'LBS',
        'packing': 'PALLET',
        'name': 'Test Package',
        'stack_limit': int(np.random.choice(a=[1, 2, 3, 4], p=[.2, .3, .3, .2])),
        'desc': None,
        'commodity': None,
        'value': None,
        'num_pieces': int(np.random.choice(a=list(range(1, 6)))),
    }

###########################################
########### Select Trailer Type ###########
###########################################

print('')
print('')
for i,d in enumerate(STANDARD_TRAILER_DIMS):
    print(i,d.get('name'))

print('')
print('')
trailer_selection = input('Select a trailer type: ')
trailer_selection = int(trailer_selection)

# trailer_selection = 0
trailer_dims = STANDARD_TRAILER_DIMS[trailer_selection]


###########################################
######### Select Number of Pieces #########
###########################################

print('')
num_pieces = input('Select number of pieces: ')
num_pieces = int(num_pieces)

# num_pieces = 5
###########################################
######## Generate Shipment Pieces #########
###########################################

blockout = trailer_dims.get('blockout_options')[0]
piece_list = []
for _ in range(num_pieces):
    piece_dict = generate_random_piece(blockout) 
    piece_list += [piece_dict]

trailer_dims = {
    'inner_width' : trailer_dims.get('inner_width'),
    'inner_length' : trailer_dims.get('inner_length'),
    'inner_height' : trailer_dims.get('inner_height'),
    'max_weight' : trailer_dims.get('max_weight'),
}

allow_rotations = True

start_time = time.perf_counter()
trailer = optimize_trailer_load_plan(
    piece_list          = piece_list,
    trailer_dims        = trailer_dims,
    allow_rotations     = allow_rotations
)
runtime = time.perf_counter() - start_time

trailer_stats = trailer.get_summary()


print('')
print('')
for i,shipment in enumerate(trailer.shipments):
    shipment._set_dims()
    print(f'Shipment {i+1}: {shipment.length}"x{shipment.width}"x{shipment.height} - {shipment.weight} Lbs')
    for j,piece in enumerate(shipment.pieces):
        print(f'\tPiece {j+1}: {piece.length}"x{piece.width}"x{piece.height} - {piece.weight} Lbs')



# print(_json_dumps(trailer_stats,indent=2))
print(runtime)
trailer.plot()
