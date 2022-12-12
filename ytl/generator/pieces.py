
import numpy as np


def generate_random_piece(**kwargs):
	length_options = kwargs.get('length_options', list(range(12, 60)))
	width_options = kwargs.get('width_options', list(range(12, 60)))
	height_options = kwargs.get('height_options', list(range(12, 40)))
	weight_options = kwargs.get('weight_options', list(range(100, 2100, 50)))
	stack_options = kwargs.get('weight_options', [1, 2, 3, 4])
	num_pieces_options = kwargs.get('num_pieces_options', [1, 2, 3, 4, 5])
	piece_type_options = kwargs.get('piece_type_options', ['PALLET', 'BOX'])
	length_probs = kwargs.get('length_probs', np.ones(
		len(length_options))/len(length_options))
	width_probs = kwargs.get('width_probs', np.ones(
		len(width_options))/len(width_options))
	height_probs = kwargs.get('height_probs', np.ones(
		len(height_options))/len(height_options))
	weight_probs = kwargs.get('weight_probs', np.ones(
		len(weight_options))/len(weight_options))
	stack_probs = kwargs.get('stack_probs', np.ones(
		len(stack_options))/len(stack_options))
	num_pieces_probs = kwargs.get('num_pieces_probs', np.ones(
		len(num_pieces_options))/len(num_pieces_options))
	piece_type_probs = kwargs.get('piece_type_probs', np.ones(
		len(piece_type_options))/len(piece_type_options))
	return {
		'length': np.random.choice(a=length_options, p=length_probs),
		'width': np.random.choice(a=width_options, p=width_probs),
		'height': np.random.choice(a=height_options, p=height_probs),
		'dimension_unit_of_measure': 'IN',
		'weight': np.random.choice(a=weight_options, p=weight_probs),
		'weight_unit_of_measure': 'LBS',
		'packing': np.random.choice(a=piece_type_options, p=piece_type_probs),
		'name': 'Test Package',
		'stack_limit': int(np.random.choice(a=stack_options, p=stack_probs)),
		'desc': None,
		'commodity': None,
		'value': None,
		'num_pieces': int(np.random.choice(a=num_pieces_options, p=num_pieces_probs)),
	}
