
# from ytl import optimize_trailer_load_plan, defaults, STANDARD_TRAILER_DIMS
# import numpy as np
# import time


# def generate_random_piece(single_piece_only=True):
#     return {
#         'length': np.random.choice(a=[i for i in range(20, 40, 1) if i >= 6]),
#         'width': np.random.choice(a=[i for i in range(20, 40, 1) if i >= 6]),
#         'height': np.random.choice(a=list(range(24, 40))),
#         'dimension_unit_of_measure': 'IN',
#         'weight': np.random.choice(a=list(range(75, 400, 25))+[750]),
#         'weight_unit_of_measure': 'LBS',
#         'packing': 'PALLET',
#         'name': 'Test Package',
#         'stack_limit': int(np.random.choice(a=[1, 2, 3, 4], p=[0, .1, .7, .2])),
#         'desc': None,
#         'commodity': None,
#         'value': None,
#         'num_pieces': 1 if single_piece_only else int(np.random.choice(a=list(range(1, 6)))),
#     }

# ###########################################
# ########### Select Trailer Type ###########
# ###########################################

# print('')
# print('')
# for i,d in enumerate(STANDARD_TRAILER_DIMS):
#     print(i,d.get('name'))

# print('')
# print('')
# trailer_selection = input('Select a trailer type: ')
# trailer_selection = int(trailer_selection)

# trailer_dims = STANDARD_TRAILER_DIMS[trailer_selection]


# ###########################################
# ######### Select Number of Pieces #########
# ###########################################

# print('')
# num_pieces = input('Select number of pieces: ')
# num_pieces = int(num_pieces)

# ###########################################
# ######## Generate Shipment Pieces #########
# ###########################################

# shipment_list = []
# for _ in range(num_pieces):
#     piece_dict = generate_random_piece(single_piece_only=False) 
#     shipment_list += [piece_dict]
#     if sum([s.get('num_pieces') for s in shipment_list]) >= num_pieces:
#         shipment_list[-1].update(
#             {
#                 'num_pieces' : num_pieces - sum(
#                     [s.get('num_pieces') for s in shipment_list[:-1]]
#                 )
#             }
#         )
#         break

# trailer_dims = {
#     'inner_width' : trailer_dims.get('inner_width'),
#     'inner_length' : trailer_dims.get('inner_length'),
#     'inner_height' : trailer_dims.get('inner_height'),
#     'max_weight' : trailer_dims.get('max_weight'),
# }

# allow_rotations = True

# start_time = time.perf_counter()
# trailer = optimize_trailer_load_plan(
#     shipment_list = shipment_list,
#     trailer_dims = trailer_dims,
#     allow_rotations = allow_rotations,
#     piece_arrangement_algorithm=defaults.DEFAULT_PIECE_ARRANGEMENT_ALGORITHM,
#     shipment_optimization_ls=defaults.DEFAULT_SHIPMENT_ARRANGEMENT_ALGORITHM
# )
# runtime = time.perf_counter() - start_time

# trailer_stats = trailer.get_summary()


# print('')
# print('')
# for k,v in trailer_stats.get('load_order').items():
#     print(
#         '{name:30} location: {x:3.0f} x {y:3.0f} x {z:3.0f}    size: {l:3.0f}" x {w:3.0f}" x {h:3.0f}"   weight: {weight:5,.0f} Lbs    {rotated:10}'.format(
#             name=v.get('name'),
#             x=v.get('position')[0],
#             y=v.get('position')[1],
#             z=v.get('position')[2],
#             l=v.get('piece_length'),
#             w=v.get('piece_width'),
#             h=v.get('piece_height'),
#             weight=v.get('piece_weight'),
#             rotated='Rotated' if v.get('piece_is_rotated') else 'Not Rotated',
#         )
#     )


# print(f'Runtime: {runtime:.2f}')
# trailer.plot()
