from typing import List, Dict
import numpy as np


def intervals_overlap(a : List[float], b : List[float]):
	'''
	Determine Two Provided Intervals Overlap
	
	Params
	-----------
	a : List[float]
		List, or list-like object, with numeric values of length 2
	b : List[float]
		List, or list-like object, with numeric values of length 2
	
	Returns
	-----------
	overlap : bool
		True if intervals a and b overlap, False if not
	
	Examples
	-----------
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


def interval_is_subset(a : List[float], b : List[float]):
	'''
	Determine First Interval is a Subset of the Second
	
	Params
	-----------
	a : List
		List, or list-like object, with numeric values of length 2
	b : List
		List, or list-like object, with numeric values of length 2
	
	Returns
	-----------
	overlap : bool
		True if interval a is a subset of b, False if not
	
	Examples
	-----------
	interval_is_subset([1,2],[0,3]) # returns True
	interval_is_subset([0,2],[0,3]) # returns True
	interval_is_subset([0,2],[1,3]) # returns False
	interval_is_subset([1,4],[0,3]) # returns False
	'''
	return a[0] >= b[0] and a[1] <= b[1]


def rotation_matrix(theta : float):
	'''
	Construct a 3x3 Rotation Matrix Rotating Counter-Clockwise in the First Two Dimensions

	Parameters
	--------------
	theta : float
		Degrees of rotation in radians
	
	Returns
	--------------
	rot_matrix
		3 x 3 rotation matrix - rotation of theta degrees counter-clockwise in the x-y plane (orthogonal to the third dimension)
	'''
	return np.array([
		[np.cos(theta), -np.sin(theta), 0],
		[np.sin(theta), np.cos(theta), 0],
		[0, 0, 1],
	])


def list_remove(idx : int, allocated : List, available : List):
	'''
	Remove Element from List While Managing Available/Unavailable Selections

	Params
	----------
	idx : int
		Index of value to be removed
	
	Returns
	----------
	None
	'''
	allocated.remove(idx)
	available += [idx]


def list_allocate(idx : int, allocated : List, available : List):
	'''
	Allocate Element from List While Managing Available/Unavailable Selections

	Params
	----------
	idx : int
		Index of value to be allocated
	
	Returns
	----------
	None
	'''
	available.remove(idx)
	allocated += [idx]

def get_current_trailer_configuration(trailer):
	'''
	Get Piece Location Details for Current Trailer Configuration
	
	Get the details of the current configuration for a trailer object
	to be used as a backup to be restored at a later time.  To be 
	used in conjunction with `restore_trailer_configuration`.

	Params
	---------
	trailer : logistics_objects.Trailer
		Trailer object for which to save current configuration
	
	Returns
	---------
	shipment_arrangement : List[Dict]
		List of dictionaries detailing the location of pieces in the current trailer load plan
	'''
	return [(s, s.position, s.is_rotated) for s in trailer.shipments]


def restore_trailer_configuration(shipment_arrangement : List[Dict]):
	'''
	Restore Provided Piece Location Configuration
	
	Restore a piece configuration inside a trailer.  To be used
	in conjuction with `get_current_trailer_configuration` to 
	restore a previous state of the trailer object.

	Params
	---------
	shipment_arrangement : List[Dict]
		Shipment arrangment list - typically, this would be a value returned by `get_current_trailer_configuration`
	
	Returns
	---------
	None
	'''
	for s, pos, rot in shipment_arrangement:
		s.position = pos
		if rot != s.is_rotated:
			s.rotate()
		s._set_dims()
