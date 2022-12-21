
from typing import List
from ...py3dbp import Packer
from ...logistics_objects import Shipment
from ...defaults import OVERWEIGHT_SHIPMENT_THRESHOLD
import numpy as np

def binpack_stack_pieces(pieces : List, trailer_height : float, **kwargs):
	'''
	Stack Pieces into Shipments Using a Bin Packing Algorithm

	Parameters
	-------------
	pieces : List[logistics_objects.Piece]
		Pieces to be arranged into shipments
	trailer_height : float
		Height of trailer
	
	Returns
	-------------
	shipments : List[logistics_objects.Shipment]
		List of shipment objects made composed of provided pieces
	'''
	overweight_shipment_threshold = kwargs.get('overweight_shipment_threshold',OVERWEIGHT_SHIPMENT_THRESHOLD)
	allocated_indices = []
	sorted_indices = list(np.argsort([p.length * p.width for p in pieces]))[::-1]
	shipments = []

	unstackable_idx_ls = [p for p in pieces if p.stack_limit <= 1]
	for idx in unstackable_idx_ls:
		allocated_indices += [idx]
		piece = pieces[idx]
		sorted_indices.remove(idx)
		shipment = Shipment(pieces=initial_piece)
		shipments += [shipment]

	while len(sorted_indices) > 0:
		idx = sorted_indices.pop()
		allocated_indices += [idx]
		initial_piece = pieces[idx]
		shipment = Shipment(pieces=initial_piece)
		shipments += [shipment]
		packer = Packer()
		shipment._update_binpack_bin(
			height=trailer_height - initial_piece.height,
			name=idx,
			max_weight=overweight_shipment_threshold - initial_piece.weight,
		)
		packer.add_bin(shipment.binpack_bin)
		for jdx in sorted_indices:
			piece = pieces[jdx]
			piece._update_binpack_item(name=jdx)
			packer.add_item(piece.binpack_item)
		packer.pack(
			distribute_items=False,
			bigger_first=False,
		)
		for b in packer.bins:
			for item in b.items:
				piece = pieces[item.name]
				allocated_indices += [item.name]
				sorted_indices.remove(item.name)
				if piece.binpack_item.rotation_type == 1:
					piece.rotate()
				piece.position[0] = float(piece.binpack_item.position[1])
				piece.position[1] = float(piece.binpack_item.position[0])
				piece.position[2] = initial_piece.height + float(piece.binpack_item.position[2])
				shipment.add_piece(piece)
				shipment._set_dims()

	shipments = [shipment for shipment in shipments if len(shipment.pieces) > 0]

	for shipment in shipments:
		shipment._set_dims()
	return shipments
