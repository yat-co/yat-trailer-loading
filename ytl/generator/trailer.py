from .. import optimize_trailer_load_plan
from ..standard_logistic_dims import STANDARD_TRAILER_DIMS
from .pieces import generate_random_piece

from copy import deepcopy
import numpy as np


def generate_random_trailer_load_plan(**kwargs):
	trailer_idx_options = kwargs.get('trailer_idx_options', [0])
	num_piece_selection_options = kwargs.get('num_piece_selection_options', [3, 4, 5])
	allow_rotations_options = kwargs.get('allow_rotations', [True, False])
	trailer_idx_probs = kwargs.get('trailer_idx_probs', np.ones(len(trailer_idx_options))/len(trailer_idx_options))
	num_piece_selection_probs = kwargs.get('num_piece_selection_probs', np.ones(len(num_piece_selection_options))/len(num_piece_selection_options))
	allow_rotations_probs = kwargs.get('allow_rotations_probs', np.ones(len(allow_rotations_options))/len(allow_rotations_options))
	trailer_idx = int(np.random.choice(a=trailer_idx_options, p=trailer_idx_probs))
	num_piece_selections = int(np.random.choice(a=num_piece_selection_options, p=num_piece_selection_probs))
	allow_rotations = np.random.choice(a=allow_rotations_options, p=allow_rotations_probs)
	trailer_dims = {
		'inner_width': STANDARD_TRAILER_DIMS[trailer_idx].get('inner_width'),
		'inner_length': STANDARD_TRAILER_DIMS[trailer_idx].get('inner_length'),
		'inner_height': STANDARD_TRAILER_DIMS[trailer_idx].get('inner_height'),
		'max_weight': STANDARD_TRAILER_DIMS[trailer_idx].get('max_weight'),
	}
	piece_list = []
	for _ in range(num_piece_selections):
		piece_dict = generate_random_piece(**kwargs)
		piece_list += [piece_dict]
	trailer = optimize_trailer_load_plan(
		piece_list=deepcopy(piece_list),
		trailer_dims=trailer_dims,
		allow_rotations=allow_rotations
	)
	return trailer, piece_list, allow_rotations
