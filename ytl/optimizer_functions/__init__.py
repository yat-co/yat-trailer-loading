
from .shipment_arrangement.naive import naive_shipment_arrangement
from .shipment_arrangement.bin_packing import no_stack_trailer_arrange
from .shipment_arrangement.simple_movements import slide_shipments_back
from .shipment_arrangement.greedy import greedy_trailer_load

from .piece_arrangement.naive import naive_piece_arrangement
from .piece_arrangement.bin_packing import binpack_stack_pieces
from .piece_arrangement.greedy import greedy_stack_pieces


PIECE_ARRANGEMENT_ROUTER = {
	'NAIVE': naive_piece_arrangement,
	# TODO: Address invalid stacking results prior to making this available
	# 'BIN_PACK_SHIPMENT_STACK': binpack_stack_pieces,
	'GREEDY_STACK': greedy_stack_pieces,
}

SHIPMENT_ARRANGEMENT_ROUTER = {
	'NAIVE': naive_shipment_arrangement,
	'NO_STACK_BIN_PACK': no_stack_trailer_arrange,
	'SLIDE_BACK': slide_shipments_back,
	'GREEDY_LOAD': greedy_trailer_load,
}

def optimize_pieces_arrangement(pieces,algorithm : str,**kwargs):
	'''
	Piece Arrangement Optimization Router Function

	Optimizes the arrangement of provided pieces in to shipments by 
	collecting and stacking pieces into shipments to be loaded into
	a trailer.  Router function leverages `PIECE_ARRANGEMENT_ROUTER`
	to allow for various algorithm options.  All functions in the 
	piece arrangement router require `pieces` and algorithm 
	parameters, and return a list of shipments of type 
	List[logistics_objects.Shipment].  See individual functions in piece 
	arrangement router for additional required parameters.

	Parameters
	-------------
	pieces : List[logistics_objects.Piece]
		List of pieces to be arranged into shipments
	algorithm : str
		Algorithm key, options are the keys of `PIECE_ARRANGEMENT_ROUTER`

	Returns
	-------------
	shipments : List[logistics_objects.Shipment]
		List of shipments made up of provided pieces

	'''
	if not algorithm in PIECE_ARRANGEMENT_ROUTER.keys():
		raise NotImplementedError(f'Algorithm `{algorithm}` has not been implemented')
	return PIECE_ARRANGEMENT_ROUTER[algorithm](pieces=pieces,**kwargs)


def optimize_shipment_arrangement(trailer,algorithm,**kwargs):
	'''
	Shipment Arrangement Optimization Router Function

	Optimizes the arrangement of shipment associated to the provided
	logistics_objects.Trailer object.  Router function leverages 
	`SHIPMENT_ARRANGEMENT_ROUTER` to allow for various algoirthm
	options.  All functions in the shipment arrangement router require
	`trailer` and `algorithm` parameters, update the shipment 
	arrangement stored in the trailer object, and return None.
	
	Parameters
	-------------
	trailer : logistics_objects.Trailer
		Trailer object with shipments to be optimally loaded
	algorithm : str
		Algorithm key, options are the keys of `SHIPMENT_ARRANGEMENT_ROUTER`

	Returns
	-------------
	None
	'''
	if not algorithm in SHIPMENT_ARRANGEMENT_ROUTER.keys():
		raise NotImplementedError(f'Algorithm `{algorithm}` has not been implemented')
	return SHIPMENT_ARRANGEMENT_ROUTER[algorithm](trailer=trailer,**kwargs)
