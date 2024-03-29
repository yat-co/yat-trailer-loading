
from .shipment_arrangement.naive import naive_shipment_arrangement, naive_shipment_arrangement_details
from .shipment_arrangement.bin_packing import no_stack_trailer_arrange, no_stack_bin_pack_shipment_arrangement_details
from .shipment_arrangement.simple_movements import slide_shipments_back, simple_movement_slide_back_shipment_arrangement_details
from .shipment_arrangement.greedy import greedy_trailer_load, greedy_shipment_arrangement_details

from .piece_arrangement.naive import naive_piece_arrangement, naive_piece_arrangement_details
from .piece_arrangement.greedy import greedy_stack_pieces, greedy_stack_piece_arrangement_details


PIECE_ARRANGEMENT_ROUTER = {
	'NAIVE': (naive_piece_arrangement, naive_piece_arrangement_details),
	'GREEDY_STACK': (greedy_stack_pieces, greedy_stack_piece_arrangement_details),
}

SHIPMENT_ARRANGEMENT_ROUTER = {
	'NAIVE': (naive_shipment_arrangement, naive_shipment_arrangement_details),
	'NO_STACK_BIN_PACK': (no_stack_trailer_arrange, no_stack_bin_pack_shipment_arrangement_details),
	'SLIDE_BACK': (slide_shipments_back, simple_movement_slide_back_shipment_arrangement_details),
	'GREEDY_LOAD': (greedy_trailer_load, greedy_shipment_arrangement_details),
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
	return PIECE_ARRANGEMENT_ROUTER[algorithm][0](pieces=pieces,**kwargs)


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
	return SHIPMENT_ARRANGEMENT_ROUTER[algorithm][0](trailer=trailer,**kwargs)
