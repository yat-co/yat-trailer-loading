
from typing import List, Dict
from ..logistics_objects import (
	Piece, Shipment, Trailer
)
from ..utils import (
	get_current_trailer_configuration, restore_trailer_configuration
)
from ..exceptions import (
	NoPiecesException,
	PiecesTooLongForServiceException,
	OptimizationFailedServiceException,
	InvalidTrailerDimensionsException,
	InvalidPiecesException,
)
from ..validation import (
	validate_piece_length, validate_pieces, validate_trailer_dims
)
from ..optimizer_functions import (
	optimize_pieces_arrangement, optimize_shipment_arrangement,
)
from .. import options
from ..defaults import (
	OVERWEIGHT_SHIPMENT_THRESHOLD,
	DEFAULT_PIECE_ARRANGEMENT_ALGORITHM,
	DEFAULT_SHIPMENT_ARRANGEMENT_ALGORITHM,
)

def optimize_trailer_load_plan(shipment_list : List[Dict], trailer_dims : Dict, allow_rotations : bool = True, **kwargs):
	# Validation of Pieces and Trailer Dimensions
	try:
		validate_trailer_dims(trailer_dims=trailer_dims)
	except Exception as e:
		raise InvalidTrailerDimensionsException('Invalid trailer dimensions passed') from e
	if len(shipment_list) == 0:
		raise NoPiecesException('No pieces provided for trailer load optimization')
	try:
		validate_pieces(shipment_list=shipment_list)
	except Exception as e:
		raise InvalidPiecesException from e
	try:
		validate_piece_length(
			shipment_list=shipment_list,
			trailer_dims=trailer_dims,
			allow_rotations=allow_rotations,
		)
	except Exception as e:
		raise PiecesTooLongForServiceException('At least one of the pieces provided is too large to fit on the trailer') from e
	
	# Get default and overriden parameters
	dimension_unit_of_measure = options.DimUomInches
	weight_unit_of_measure = options.WeightUomPounds
	overweight_shipment_threshold = OVERWEIGHT_SHIPMENT_THRESHOLD if kwargs.get('overweight_shipment_threshold') is None else kwargs.get('overweight_shipment_threshold')
	piece_arrangement_algorithm = DEFAULT_PIECE_ARRANGEMENT_ALGORITHM if kwargs.get('piece_arrangement_algorithm') is None else kwargs.get('piece_arrangement_algorithm')
	shipment_optimization_ls = DEFAULT_SHIPMENT_ARRANGEMENT_ALGORITHM if kwargs.get('shipment_optimization_ls') is None else kwargs.get('shipment_optimization_ls')
	
	# Create pieces for all provided shipments
	pieces = []
	for i, shipment_dict in enumerate(shipment_list):
		num_items = shipment_dict.pop('num_pieces', 1)
		for j in range(num_items):
			shipment_dict.update(
				{
					'name': f'Shipment {i+1}:  Piece {j+1}',
					'id' : shipment_dict.get('id'),
					'desc' : shipment_dict.get('desc'),
				}
			)
			pieces += [Piece(**shipment_dict)]
	
	# Identify overweight shipments
	overweight_pieces = [piece for piece in pieces if piece.weight > overweight_shipment_threshold]
	pieces = [piece for piece in pieces if not piece in overweight_pieces]
	
	# Orient overweight shipments to maximally distribute weight in the length dimension, if allowed
	if allow_rotations:
		for piece in overweight_pieces:
			if piece.length < piece.width:
				piece.rotate()
	
	# Arrange non-overweight pieces into shipments
	if len(pieces) > 0:
		try:
			shipments = optimize_pieces_arrangement(
				pieces=pieces,
				algorithm=piece_arrangement_algorithm,
				trailer_height=trailer_dims.get('inner_height'),
				allow_rotations=allow_rotations,
			)
		except Exception as e:
			raise OptimizationFailedServiceException('Optimization failed during arrangment of pieces into shipments') from e
	else:
		shipments = []
	
	# Create trailer object associated to shipments made up of non-overweight pieces
	trailer = Trailer(
		shipments=shipments,
		width=trailer_dims.get('inner_width'),
		length=trailer_dims.get('inner_length'),
		height=trailer_dims.get('inner_height'),
		dimension_unit_of_measure=dimension_unit_of_measure,
		weight=0,
		weight_unit_of_measure=weight_unit_of_measure,
		max_weight=trailer_dims.get('max_weight'),
	)

	# Optimize shipment arrangement within trailer
	results = []
	if len(pieces) > 0:
		try:
			for opt_kwargs in shipment_optimization_ls:
				optimize_shipment_arrangement(
					trailer=trailer,
					allow_rotations=allow_rotations,
					**opt_kwargs,
				)
				trailer._set_weight()
				results += [
					{
						'linear_feet' : trailer.get_linear_feet(),
						'configuration' : get_current_trailer_configuration(trailer),
						'valid' : trailer.arrangement_is_valid(),
						'request_kwargs' : opt_kwargs,
					}
				]
			assert len([result for result in results if result.get('valid')]) > 0
			result = sorted([result for result in results if result.get('valid')],key=lambda x : x.get('linear_feet'))[0]
			restore_trailer_configuration(result['configuration'])
		except Exception as e:
			raise OptimizationFailedServiceException('Optimization failed during shipment arrangement optimization') from e
	
	# Handle overweight pieces/shipments
	overweight_shipments = [Shipment(pieces=piece) for piece in overweight_pieces]
	boundaries = trailer.get_boundaries()
	try:
		linear_inches = boundaries[0, 1]
		for shipment in overweight_shipments:
			shipment._set_dims()
			shipment.position[0] = linear_inches
			shipment.position[1] = trailer.width / 2 - shipment.width / 2
			trailer.add_shipment(shipment)
			linear_inches += shipment.length
			shipment._set_dims()
			trailer._set_weight()
	except Exception as e:
		raise OptimizationFailedServiceException('Optimization failed during overwieght piece load optimization') from e
	return trailer
