from .. import optimize_trailer_load_plan, optimize_trailer_load_plan_wrapper
from ..standard_logistic_dims import STANDARD_TRAILER_DIMS
from .pieces import generate_random_piece

from copy import deepcopy
import numpy as np


def generate_random_trailer_load_plan(**kwargs):
	trailer_idx_options = kwargs.get('trailer_idx_options', [0])
	trailer_idx_probs = kwargs.get('trailer_idx_probs', np.ones(len(trailer_idx_options))/len(trailer_idx_options))
	trailer_idx = int(np.random.choice(a=trailer_idx_options, p=trailer_idx_probs))

	num_piece_selection_options = kwargs.get('num_piece_selection_options', [3, 4, 5])
	num_piece_selection_probs = kwargs.get('num_piece_selection_probs', np.ones(len(num_piece_selection_options))/len(num_piece_selection_options))
	num_piece_selections = int(np.random.choice(a=num_piece_selection_options, p=num_piece_selection_probs))

	allow_rotations_options = kwargs.get('allow_rotations', [True, False])
	allow_rotations_probs = kwargs.get('allow_rotations_probs', np.ones(len(allow_rotations_options))/len(allow_rotations_options))
	allow_rotations = np.random.choice(a=allow_rotations_options, p=allow_rotations_probs)

	trailer_dims = {
		'inner_width': STANDARD_TRAILER_DIMS[trailer_idx].get('inner_width'),
		'inner_length': STANDARD_TRAILER_DIMS[trailer_idx].get('inner_length'),
		'inner_height': STANDARD_TRAILER_DIMS[trailer_idx].get('inner_height'),
		'max_weight': STANDARD_TRAILER_DIMS[trailer_idx].get('max_weight'),
	}

	shipment_list = []
	for _ in range(num_piece_selections):
		piece_dict = generate_random_piece(**kwargs)
		shipment_list += [piece_dict]
	
	trailer = optimize_trailer_load_plan(
		shipment_list=deepcopy(shipment_list),
		trailer_dims=trailer_dims,
		allow_rotations=allow_rotations,
		piece_arrangement_algorithm=kwargs.get('piece_arrangement_algorithm'),
		shipment_optimization_ls=kwargs.get('shipment_optimization_ls'),
		overweight_shipment_threshold=kwargs.get('overweight_shipment_threshold'),
	)
	return trailer, shipment_list, allow_rotations

def generate_random_trailer_load_plan_wrapper(**kwargs):
	trailer_idx_options = kwargs.get('trailer_idx_options', [0])
	trailer_idx_probs = kwargs.get('trailer_idx_probs', np.ones(len(trailer_idx_options))/len(trailer_idx_options))
	trailer_idx = int(np.random.choice(a=trailer_idx_options, p=trailer_idx_probs))

	num_piece_selection_options = kwargs.get('num_piece_selection_options', [3, 4, 5])
	num_piece_selection_probs = kwargs.get('num_piece_selection_probs', np.ones(len(num_piece_selection_options))/len(num_piece_selection_options))
	num_piece_selections = int(np.random.choice(a=num_piece_selection_options, p=num_piece_selection_probs))

	allow_rotations_options = kwargs.get('allow_rotations', [True, False])
	allow_rotations_probs = kwargs.get('allow_rotations_probs', np.ones(len(allow_rotations_options))/len(allow_rotations_options))
	allow_rotations = np.random.choice(a=allow_rotations_options, p=allow_rotations_probs)

	trailer_dims = {
		'inner_width': STANDARD_TRAILER_DIMS[trailer_idx].get('inner_width'),
		'inner_length': STANDARD_TRAILER_DIMS[trailer_idx].get('inner_length'),
		'inner_height': STANDARD_TRAILER_DIMS[trailer_idx].get('inner_height'),
		'max_weight': STANDARD_TRAILER_DIMS[trailer_idx].get('max_weight'),
	}

	shipment_list = []
	for _ in range(num_piece_selections):
		piece_dict = generate_random_piece(**kwargs)
		shipment_list += [piece_dict]
	
	request_data = {
		'shipment_list' : deepcopy(shipment_list),
		'trailer_dims' : trailer_dims,
		'allow_rotations' : allow_rotations,
	}

	# Add optional algorithm/settings parameters as needed
	if kwargs.get('piece_arrangement_algorithm') is not None:
		request_data.update({'piece_arrangement_algorithm' : kwargs['piece_arrangement_algorithm']})

	if kwargs.get('shipment_optimization_ls') is not None:
		request_data.update({'shipment_optimization_ls' : kwargs['shipment_optimization_ls']})

	if kwargs.get('overweight_shipment_threshold') is not None:
		request_data.update({'overweight_shipment_threshold' : kwargs.get('overweight_shipment_threshold')})
	
	status_code,response = optimize_trailer_load_plan_wrapper(request_data=request_data)
	return status_code, response, shipment_list, allow_rotations
