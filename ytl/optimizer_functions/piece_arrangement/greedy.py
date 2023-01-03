
from typing import List
from ...logistics_objects import Shipment
from ...utils import list_allocate
import numpy as np

greedy_stack_piece_arrangement_details = {
	'code' : 'GREEDY_STACK',
	'name' : 'Greedy Stacking Piece Arrangement',
	'desc' : 'Greedy stacking algorithm to stack smaller pieces on top of larger pieces to make shipments',
}

def try_to_stack(shipment, idx : int, trailer_height : float, allocated_pieces : List[int], available_pieces : List[int], stackable_pieces : List, allow_rotations : bool=True):
	'''
	Try to Stack Piece

	Parameters
	------------
	shipment : logistics_objects.Shipment
		Shipment object attemping to be stacked on
	idx : int
		Index of piece proposed to be stacked on shipment
	trailer_height : float
		Height of trailer
	allocated_pieces : List[int]
		List of indices for pieces already allocated to shipments
	available_pieces : List[int]
		List of indices for pieces unallocated and available to be added to shipments
	stackable_pieces : List[logistics_objects.Shipment]
		List of pieces that are stackable
	allow_rotations : bool
		Allow rotation of pieces when attempting to stack
	
	Returns
	------------
	added_piece_to_shipment : bool
		True if piece was added to shipment, False if not
	'''
	if idx in allocated_pieces:
		return False
	piece = stackable_pieces[idx]
	can_stack = shipment.can_stack(
		piece=piece,
		trailer_height=trailer_height
	)
	if can_stack:
		shipment.stack(piece)
		list_allocate(idx, allocated_pieces, available_pieces)
		return True
	elif allow_rotations:
		piece.rotate()
		can_stack = shipment.can_stack(
			piece=piece,
			trailer_height=trailer_height
		)
		if can_stack:
			shipment.stack(piece)
			list_allocate(idx, allocated_pieces, available_pieces)
			return True
		else:
			piece.rotate()
	return False


def greedy_stack_pieces(pieces : List, trailer_height : int, allow_rotations : bool=True, **kwargs):
	'''
	Allocate Provided Pieces into Shipments Using a Simple Greedy Stacking Algorithm

	Parameters
	------------
	pieces : List[logistics_objects.Piece]
		List of pieces to be allocated into shipments
	trailer_height : int
		Trailer height
	allow_rotations : bool
		Allows pieces to be rotated if True, does not allow rotation otherwise.
	
	Returns
	-----------
	shipments : List[logistics_objects.Shipment]
		List of shipments composed of provided piece objects
	'''
	unstackable_pieces = [p for p in pieces if p.stack_limit <= 1]
	stackable_pieces = [p for p in pieces if p.stack_limit > 1]

	shipments = []
	allocated_pieces = []
	available_pieces = list(range(len(stackable_pieces)))

	sorted_indices = np.argsort(
		[p.length ** .5 + p.width ** .5 for p in stackable_pieces]
	)[::-1]
	count = 0
	max_iter = len(available_pieces) + 1
	while len(available_pieces) > 0 and count < max_iter:
		bottom_idx = [i for i in sorted_indices if i in available_pieces][0]
		list_allocate(bottom_idx, allocated_pieces, available_pieces)
		shipment = Shipment(pieces=stackable_pieces[bottom_idx])
		sorted_indices = np.argsort(
			[p.length ** .5 + p.width ** .5 for p in stackable_pieces]
		)[::-1]
		for idx in sorted_indices:
			_ = try_to_stack(
				shipment=shipment,
				idx=idx,
				trailer_height=trailer_height,
				allocated_pieces=allocated_pieces,
				available_pieces=available_pieces,
				stackable_pieces=stackable_pieces,
				allow_rotations=allow_rotations
			)
		shipment._set_dims()
		shipments += [shipment]
	for piece in unstackable_pieces:
		shipment = Shipment(pieces=piece)
		shipment._set_dims()
		shipments += [shipment]
	return shipments
