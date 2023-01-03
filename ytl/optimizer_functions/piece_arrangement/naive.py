
from typing import List
from ...logistics_objects import Shipment

naive_piece_arrangement_details = {
	'code' : 'NAIVE',
	'desc' : 'The trivial piece packing - make each piece its own shipment with no stacking',
}

def naive_piece_arrangement(pieces : List, **kwargs):
	'''
	Allocate Provided Pieces into Shipments in a Trivia/Naive Manner

	No optimization is done in this piece-shipment allocation, just 
	one shipment per piece with no stacking.

	Parameters
	------------
	pieces : List[logistics_objects.Piece]
		List of pieces to be allocated into shipments
	
	Returns
	-----------
	shipments : List[logistics_objects.Shipment]
		List of shipments composed of provided piece objects
	'''
	shipments = [Shipment(pieces=piece) for piece in pieces]
	for shipment in shipments:
		shipment._set_dims()
	return shipments

