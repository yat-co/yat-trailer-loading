
import numpy as np


def intervals_overlap(a, b):
	'''
	intervals_overlap([0,1],[1,2]) # don't overlap, return False
	intervals_overlap([1,2],[0,1]) # don't overlap, return False
	intervals_overlap([0,2],[1,3]) # overlap, return True
	intervals_overlap([1,3],[0,2]) # overlap, return True
	intervals_overlap([0,5],[1,2]) # overlap, return True
	intervals_overlap([1,2],[0,5]) # overlap, return True
	'''
	if a[0] < b[1]:
		return a[1] > b[0]
	else:
		return a[0] < b[1]


def interval_is_subset(a, b):
	'''
	interval_is_subset([1,2],[0,3]) # returns True
	interval_is_subset([0,2],[0,3]) # returns True
	interval_is_subset([0,2],[1,3]) # returns False
	interval_is_subset([1,4],[0,3]) # returns False
	'''
	return a[0] >= b[0] and a[1] <= b[1]


def rotation_matrix(theta):
	return np.array([
		[np.cos(theta), -np.sin(theta), 0],
		[np.sin(theta), np.cos(theta), 0],
		[0, 0, 1],
	])


def list_remove(idx, allocated, available):
	_ = pop_value(allocated, idx)
	available += [idx]


def list_allocate(idx, allocated, available):
	_ = pop_value(available, idx)
	allocated += [idx]


def pop_value(L, v):
	for i, vv in enumerate(L):
		if v == vv:
			return L.pop(i)


def store_load_plan(trailer):
	return [(s, s.position, s.is_rotated) for s in trailer.shipments]


def restore_load_plan(shipment_arrangement):
	for s, pos, rot in shipment_arrangement:
		s.position = pos
		if rot != s.is_rotated:
			s.rotate()
		s._set_dims()
