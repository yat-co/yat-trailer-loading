
from typing import List
from ...utils import (
	get_current_trailer_configuration,
	restore_trailer_configuration,
)
import time
import numpy as np

greedy_shipment_arrangement_details = {
	'code' : 'GREEDY_LOAD',
	'name' : 'Greedy Shipment Arrangement',
	'desc' : 'A stochastic greedy optimization for efficiently loading shipments onto the trailer',
}

def loss_function(trailer, shipment=None, **kwargs):
	'''
	Loss Function Intended to Score Trailer Load Plan Based on Trailer Linear Feet
	'''
	if trailer.arrangement_is_valid(shipment=shipment):
		return max([s.position[0] + s.length for s in trailer.shipments])
	return np.Infinity

def load_shipment(trailer, shipment, allow_rotations=True):
	'''
	Load Shipment on Trailer
	'''
	ll_candidate_positions = []
	ll_candidate_positions += [
		s.position + np.array([0, s.width, 0])
			for s in trailer.shipments[-5:] if s.position[1] + shipment.width < trailer.width
	]
	ll_candidate_positions += [
		s.position + np.array([s.length, 0, 0])
			for s in trailer.shipments[-5:] if s.position[1] + shipment.width < trailer.width
	]
	ll_candidate_positions += [trailer.position + np.array([0, 0, 0])]
	ul_candidate_positions = []
	ul_candidate_positions += [
		s.position + np.array([s.length, s.width, 0])
			for s in trailer.shipments[-5:] if s.position[1] - shipment.width > 0
	]
	ul_candidate_positions += [
		s.position + np.array([0, 0, 0]) 
			for s in trailer.shipments[-5:] if s.position[1] - shipment.width > 0
	]
	ul_candidate_positions += [trailer.position + np.array([0, trailer.width, 0])]
	trailer.add_shipment(shipment)
	position_loss = []
	for ll_candidate in ll_candidate_positions:
		shipment.position = ll_candidate
		loss = loss_function(trailer, shipment)
		position_loss += [
			(
				ll_candidate, 
				loss, 
				False
			)
		]
	for ul_candidate in ul_candidate_positions:
		shipment.position = ul_candidate - np.array([0, shipment.width, 0])
		loss = loss_function(trailer, shipment)
		position_loss += [
			(
				ul_candidate - np.array([0, shipment.width, 0]), 
				loss, 
				False
			)
		]
	if allow_rotations:
		shipment.rotate()
		for ll_candidate in ll_candidate_positions:
			shipment.position = ll_candidate
			loss = loss_function(trailer, shipment)
			position_loss += [
				(
					ll_candidate, 
					loss, 
					True
				)
			]
		for ul_candidate in ul_candidate_positions:
			shipment.position = ul_candidate - np.array([0, shipment.width, 0])
			loss = loss_function(trailer, shipment)
			position_loss += [
				(
					ul_candidate - np.array([0, shipment.width, 0]), 
					loss, 
					True
				)
			]
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

def tetris_trailer_load(trailer, index_order : List, allow_rotations : bool = True, random : bool = True):
	'''
	Load Trailer with Tetris Style Placement with Random Order or Size Descending Order
	'''
	shipments = trailer.shipments
	for shipment in shipments:
		shipment.position = np.array([0, 0, 0])
	trailer.shipments = []
	for idx in index_order:
		shipment = shipments[idx]
		loss = load_shipment(
			trailer=trailer,
			shipment=shipment,
			allow_rotations=allow_rotations,
		)
	return loss


def get_sort_attr(s,r):
	'''
	Fuzzy Size Descending Sort Attribute for Shipments
	'''
	if r == 0:
		return (s.length * s.width) ** .5
	elif r == 1:
		return s.length
	elif r == 2:
		return s.width

def greedy_trailer_load(trailer, max_iter : int = None, timeout : float = None, allow_rotations : bool=True, **kwargs):
	'''
	Arrange Shipments in Trailer Using a Greedy Loading Algorithm
	
	Parameters
	------------
	trailer : logistics_objects.Trailer
		Trailer to be loaded
	max_iter : int
		Maximum number of iterations to be used for the optimization
	timeout : float 
		Timeout for main loop of optimization
	allow_rotations : bool
		Allow shipments to be rotated when loading
	
	Returns
	------------
	None
	'''
	max_iter = max_iter or 3
	temp_trailer_length = trailer.length
	trailer.length = sum([s.length for s in trailer.shipments])
	min_loss = np.Infinity
	shipment_arrangement = None
	start_time = time.perf_counter()
	for _ in range(max_iter):
		random_ls = np.random.choice(a=[0,1,2],size=len(trailer.shipments),replace=True)
		prob = np.array([get_sort_attr(s,r) for s,r in zip(trailer.shipments,random_ls)])
		prob = prob / np.sum(prob)
		index_order = [
			int(x) for x in np.random.choice(
				a=len(trailer.shipments),
				p=prob,
				size=len(trailer.shipments),
				replace=False
			)
		]
		loss = tetris_trailer_load(
			trailer=trailer,
			allow_rotations=allow_rotations,
			index_order = index_order,
		)
		if loss < min_loss:
			shipment_arrangement = get_current_trailer_configuration(trailer)
			min_loss = loss
		if timeout is not None:
			if time.perf_counter() - start_time > timeout:
				break
	restore_trailer_configuration(shipment_arrangement)
	trailer.length = temp_trailer_length
	for shipment in trailer.shipments:
		shipment._set_dims()

