
from .py3dbp import Packer
from .utils import (
	list_allocate,
	store_load_plan,
	restore_load_plan,
)

import numpy as np
import time


def try_to_stack(shipment, idx, trailer_height, allocated_pieces, available_pieces, stackable_pieces, allow_rotations=True):
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


def naive_shipment_arrangement(trailer, *args, **kwargs):
	length_pos = 0
	for shipment in trailer.shipments:
		shipment.position[0] = length_pos
		length_pos += shipment.length


def no_stack_pack_trailer(trailer, trailer_occupy_length, allow_rotations=True):
	trailer._update_binpack_bin(
		height=1.5,
		length=trailer_occupy_length,
		allow_rotations=allow_rotations,
	)

	packer = Packer()
	packer.add_bin(trailer.binpack_bin)

	for shipment in trailer.shipments:
		packer.add_item(shipment.binpack_item)

	packer.pack(
		distribute_items=False,
		bigger_first=True
	)
	b = packer.bins[0]
	return len(b.unfitted_items) == 0


def no_stack_trailer_arrange(trailer, allow_rotations=True):
	trailer_occupy_length = min(
		[shipment.length for shipment in trailer.shipments]) - 12

	for shipment in trailer.shipments:
		shipment.position[0] = 0
		shipment.position[1] = 0

	all_shipment_loaded = False
	count = 0
	for shipment in trailer.shipments:
		shipment._update_binpack_item(height=1)

	for _ in range(100):
		trailer_occupy_length += 12
		count += 1
		all_shipment_loaded = no_stack_pack_trailer(
			trailer=trailer,
			trailer_occupy_length=trailer_occupy_length,
			allow_rotations=allow_rotations,
		)

		if all_shipment_loaded:
			break

	for shipment in trailer.shipments:
		if shipment.binpack_item.rotation_type == 1:
			shipment.rotate()
		shipment.position[0] = float(shipment.binpack_item.position[1])
		shipment.position[1] = float(shipment.binpack_item.position[0])


def slide_shipments_back(trailer, max_iter=5, timeout=2, *args, **kwargs):
	start_time = time.perf_counter()
	break_loop = False
	index_order = np.argsort([shipment.position[0]
	                         for shipment in trailer.shipments])
	for count in range(max_iter):
		for i in index_order:
			shipment = trailer.shipments[i]
			directions = np.random.choice(a=['left', 'right'], replace=False, size=2)
			shipment.slide_back(trailer)
			for d in directions:
				if d == 'left':
					shipment.slide_left(trailer)
				else:
					shipment.slide_right(trailer)
				shipment.slide_back(trailer)

			if time.perf_counter() - start_time > timeout and count > 0:
				break_loop = True
				break
		if break_loop:
			break
	shipment._set_dims()
	trailer.balance()


def naive_piece_arrangement(pieces, trailer_height, *args, **kwargs):
	from .bin_packing import Shipment
	shipments = [Shipment(pieces=piece) for piece in pieces]
	for shipment in shipments:
		shipment._set_dims()
	return shipments


def binpack_stack_pieces(pieces, trailer_height, *args, **kwargs):
	from .bin_packing import Shipment
	num_stack_bottoms = int(3*len(pieces) / 4)
	stackable_pieces = [p for p in pieces if p.stack_limit > 1]
	sorted_indices = np.argsort([p.length * p.width for p in stackable_pieces])
	packer = Packer()
	shipments = []
	for j, i in enumerate(sorted_indices[:num_stack_bottoms]):
		piece = pieces[i]
		shipment = Shipment(pieces=piece)
		shipment._update_binpack_bin(
			height=trailer_height,
			name=j,
			max_weight=4000
		)
		packer.add_bin(shipment.binpack_bin)
		shipment.list_remove(piece)
		shipments += [shipment]

	for i, piece in enumerate(stackable_pieces):
		piece._update_binpack_item(name=i)
		packer.add_item(piece.binpack_item)

	packer.pack(
		distribute_items=True,
		bigger_first=False
	)

	allocated_piece_indices = []
	for b in packer.bins:
		for item in b.items:
			piece = pieces[item.name]
			if piece.binpack_item.rotation_type == 1:
				piece.rotate()
			piece.position[0] = float(piece.binpack_item.position[1])
			piece.position[1] = float(piece.binpack_item.position[0])
			piece.position[2] = float(piece.binpack_item.position[2])
			shipments[b.name].list_allocate(piece)
			allocated_piece_indices += [item.name]

	remaining_pieces = [p for i, p in enumerate(
		pieces) if not i in allocated_piece_indices]

	for piece in remaining_pieces:
		if piece.binpack_item.rotation_type == 1:
			piece.rotate()
		piece.position[0] = float(piece.binpack_item.position[1])
		piece.position[1] = float(piece.binpack_item.position[0])
		piece.position[2] = float(piece.binpack_item.position[2])
		shipments += [Shipment(pieces=piece)]

	shipments = [shipment for shipment in shipments if len(shipment.pieces) > 0]

	for shipment in shipments:
		shipment._set_dims()
	return shipments


def greedy_stack_pieces(pieces, trailer_height, allow_rotations=True, *args, **kwargs):
	from .bin_packing import Shipment
	unstackable_pieces = [p for p in pieces if p.stack_limit <= 1]

	stackable_pieces = [p for p in pieces if p.stack_limit > 1]
	sorted_indices = np.argsort(
		[p.length ** .5 + p.width ** .5 for p in stackable_pieces])[::-1]

	shipments = []

	allocated_pieces = []
	available_pieces = list(range(len(stackable_pieces)))

	count = 0
	max_iter = len(available_pieces) + 1
	while len(available_pieces) > 0 and count < max_iter:
		bottom_idx = [i for i in sorted_indices if i in available_pieces][0]
		list_allocate(bottom_idx, allocated_pieces, available_pieces)
		shipment = Shipment(pieces=stackable_pieces[bottom_idx])
		for idx in range(len(stackable_pieces)):
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


def loss_function(trailer, shipment=None, *args, **kwargs):
	if trailer.arrangement_is_valid(shipment=shipment):
		return max([s.position[0] for s in trailer.shipments])
	return np.Infinity


def load_shipment(trailer, shipment, allow_rotations=True):
	ll_candidate_positions = []
	ll_candidate_positions += [s.position + np.array([0, s.width, 0])
                            for s in trailer.shipments[-5:] if s.position[1] + shipment.width < trailer.width]
	ll_candidate_positions += [s.position + np.array([s.length, 0, 0])
                            for s in trailer.shipments[-5:] if s.position[1] + shipment.width < trailer.width]
	ll_candidate_positions += [trailer.position + np.array([0, 0, 0])]
	ul_candidate_positions = []
	ul_candidate_positions += [s.position + np.array([s.length, s.width, 0])
                            for s in trailer.shipments[-5:] if s.position[1] - shipment.width > 0]
	ul_candidate_positions += [s.position + np.array(
		[0, 0, 0]) for s in trailer.shipments[-5:] if s.position[1] - shipment.width > 0]
	ul_candidate_positions += [trailer.position + np.array([0, trailer.width, 0])]
	trailer.add_shipment(shipment)
	position_loss = []
	for ll_candidate in ll_candidate_positions:
		shipment.position = ll_candidate
		loss = loss_function(trailer, shipment)
		position_loss += [(ll_candidate, loss, False)]
	for ul_candidate in ul_candidate_positions:
		shipment.position = ul_candidate - np.array([0, shipment.width, 0])
		loss = loss_function(trailer, shipment)
		position_loss += [(ul_candidate -
		                   np.array([0, shipment.width, 0]), loss, False)]
	if allow_rotations:
		shipment.rotate()
		for ll_candidate in ll_candidate_positions:
			shipment.position = ll_candidate
			loss = loss_function(trailer, shipment)
			position_loss += [(ll_candidate, loss, True)]
		for ul_candidate in ul_candidate_positions:
			shipment.position = ul_candidate - np.array([0, shipment.width, 0])
			loss = loss_function(trailer, shipment)
			position_loss += [(ul_candidate -
			                   np.array([0, shipment.width, 0]), loss, True)]
	if all([loss == np.Infinity for pos, loss, rot in position_loss]):
		if allow_rotations:
			shipment.rotate()
		shipment.position = np.array([trailer.get_boundaries()[0, 1], 0, 0])
		return loss_function(trailer, shipment)
	min_idx = np.argmin([loss for pos, loss, rot in position_loss])
	shipment.position, loss, rot = position_loss[min_idx]
	if allow_rotations and (not rot):
		shipment.rotate()
	shipment.slide_back(trailer)
	return loss_function(trailer, shipment)


def random_trailer_load(trailer, allow_rotations=True, random=True):
	shipments = trailer.shipments
	for shipment in shipments:
		shipment.position = np.array([0, 0, 0])
	trailer.shipments = []
	if random:
		prob = np.array([(s.length * s.width)**1 for s in shipments])
		prob = prob / np.sum(prob)
		index_order = np.random.choice(
			a=range(len(shipments)), p=prob, size=len(shipments), replace=False)
	else:
		index_order = np.argsort([s.length * s.width for s in shipments])[::-1]
	for idx in index_order:
		shipment = shipments[idx]
		loss = load_shipment(
			trailer=trailer,
			shipment=shipment,
			allow_rotations=allow_rotations,
		)
	return loss


def greedy_trailer_load(trailer, max_iter=3, allow_rotations=True, *args, **kwargs):
	temp_trailer_length = trailer.length
	trailer.length = sum([s.length for s in trailer.shipments])
	min_loss = random_trailer_load(
		trailer=trailer,
		random=False,
		allow_rotations=allow_rotations
	)
	shipment_arrangement = store_load_plan(trailer)
	for _ in range(max_iter):
		loss = random_trailer_load(
			trailer=trailer,
			allow_rotations=allow_rotations
		)
		if loss < min_loss:
			shipment_arrangement = store_load_plan(trailer)
			min_loss = loss
	restore_load_plan(shipment_arrangement)
	trailer.length = temp_trailer_length
	for shipment in trailer.shipments:
		shipment._set_dims()


PIECE_ARRANGEMENT_ROUTER = {
	'NAIVE': naive_piece_arrangement,
	'BIN_PACK_SHIPMENT_STACK': binpack_stack_pieces,
	'GREEDY_STACK': greedy_stack_pieces,
}

SHIPMENT_ARRANGEMENT_ROUTER = {
	'NAIVE': naive_shipment_arrangement,
	'NO_STACK_BIN_PACK': no_stack_trailer_arrange,
	'SLIDE_BACK': slide_shipments_back,
	'GREEDY_LOAD': greedy_trailer_load,
}
