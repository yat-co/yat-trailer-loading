
from .common import ShippingObject
from .piece import Piece
from ..py3dbp import (
	Bin,
	NoRotateBin,
)
from ..utils import intervals_overlap
import numpy as np

class Shipment(ShippingObject):
	'''
	Shipment that May be made up of Multiple Pieces

	This is a shipment unit that may be composed of multiple pieces
	stacked or otherwise put together that are intended to be loaded
	and transported as a single unit.  It may be a single piece or 
	it may be many pieces put together.
	'''
	def __init__(self,pieces=[],*args,**kwargs):
		if isinstance(pieces,Piece):
			pieces = [pieces]
		self.pieces = []
		self.add_piece(pieces)
		self.arrange_pieces()

		super(Shipment,self).__init__(
			length = self.length,
			width = self.width,
			height = self.height,
			dimension_unit_of_measure = self.default_dimension_units,
			weight = self.weight,
			weight_unit_of_measure = self.default_weight_units,
			*args,
			**kwargs
		)
		self._binpack_bin_exists = False
		self.max_weight = 100000

	def arrange_pieces(self,**kwargs):
		'''
		Trivial Piece Arragemet:  Place Shipment End-to-End in the Length direction
		'''
		length_pos = 0
		for piece in self.pieces:
			piece.position[0] = length_pos
			length_pos += piece.length
		# Update shipment dimension/weight attributes
		self._set_dims()

	def _set_dims(self):
		'''
		Update Dimensions, Weight, and Piece Ordering for Shipment
		'''
		if len(self.pieces) == 0:
			self.length = 0
			self.width = 0
			self.height = 0
			self.weight = 0
		else:
			self.length = max([piece.position[0] + piece.length for piece in self.pieces]) - min([piece.position[0] for piece in self.pieces])
			self.width = max([piece.position[1] + piece.width for piece in self.pieces]) - min([piece.position[1] for piece in self.pieces])
			self.height = max([piece.position[2] + piece.height for piece in self.pieces]) - min([piece.position[2] for piece in self.pieces])
			self.weight = sum([piece.weight for piece in self.pieces])
		stack_order = np.argsort([p.position[2] for p in self.pieces])
		self.pieces = [self.pieces[i] for i in stack_order]

	def add_piece(self,piece):
		'''
		Add Piece to Shipment
		'''
		if isinstance(piece,Piece):
			piece = [piece]
		assert all([isinstance(p,Piece) for p in piece])
		self.pieces += piece

	def remove_piece(self,piece):
		'''
		Remove Piece from Shipment
		'''
		if isinstance(piece,Piece):
			self.pieces = [p for p in self.pieces if p != piece]
			return piece
		elif isinstance(piece,int):
			return self.pieces.pop(piece)
		else:
			raise Exception(f'Data type for {piece} not recognized')

	def get_boundaries(self):
		'''
		Get Shipment Profile
		'''
		boundaries = np.array([np.inf,-np.inf,np.inf,-np.inf,np.inf,-np.inf])
		boundaries.shape = (3,2)
		for piece in self.pieces:
			piece_boundaries = piece.get_boundaries()
			for i in range(3):
				boundaries[i,0] = min([boundaries[i,0],piece_boundaries[i,0]])
				boundaries[i,1] = max([boundaries[i,1],piece_boundaries[i,1]])
		for i in range(3):
			boundaries[i,0] += self.position[i]
			boundaries[i,1] += self.position[i]
		return boundaries
	
	def _set_binpack_bin(self,allow_rotations=True,**kwargs):
		'''
		Set Bin Pack Items
		'''
		if not self._binpack_bin_exists:
			width = kwargs.get('width',self.width)
			height = kwargs.get('height',self.height)
			length = kwargs.get('length',self.length)
			max_weight = kwargs.get('max_weight',self.weight)
			if allow_rotations:
				self.binpack_bin = Bin(
					name = kwargs.get('name',getattr(self,'name','Unnamed Shipment Object')),
					width = width, 
					height = length,
					depth = height,
					max_weight = max_weight
				)
			else:
				self.binpack_bin = NoRotateBin(
					name = kwargs.get('name',getattr(self,'name','Unnamed Shipment Object')),
					width = width, 
					height = length,
					depth = height,
					max_weight = max_weight
				)
			self._binpack_bin_exists = True
	
	def _delete_binpack_bin(self):
		'''
		Delete Bin Pack Item
		'''
		if hasattr(self,'binpack_item'):
			delattr(self,'binpack_item')
		self._binpack_bin_exists = False
	
	def _update_binpack_bin(self,allow_rotations=True,*args,**kwargs):
		'''
		Delete and Recreate Bin Pack Item
		'''
		self._delete_binpack_bin()
		self._set_binpack_bin(allow_rotations=allow_rotations,*args,**kwargs)
	
	def arrangement_is_valid(self):
		'''
		Validate Positions of Shipment's Pieces are Physically Valid
		'''
		piece_boundaries_list = [piece.get_boundaries() for piece in self.pieces]
		for i in range(len(piece_boundaries_list)):
			p_i = piece_boundaries_list[i]
			for j in range(i):
				p_j = piece_boundaries_list[j]
				overlap = all([intervals_overlap(p_i[k],p_j[k]) for k in range(3)])
				if overlap:
					return False
		return True

	def rotate(self):
		self.length, self.width = self.width, self.length
		self.length_raw, self.width_raw = self.width_raw, self.length_raw
		self.is_rotated = not self.is_rotated
		
		# Also rotate all pieces within the shipment
		for piece in self.pieces:
			piece.position[0],piece.position[1] = piece.position[1],piece.position[0]
			piece.length, piece.width = piece.width, piece.length
			piece.length_raw, piece.width_raw = piece.width_raw, piece.length_raw
			piece.is_rotated = not piece.is_rotated
	
	def move(self,delta):
		'''
		Move the Shipment
		'''
		self.position += delta
	
	def slide_back(self,trailer):
		'''
		Slide Shipment Back in Length Direction as far as it can Within the Trailer
		'''
		delta = np.array([-1,0,0])
		count = 0
		while trailer.arrangement_is_valid(self) and count < 1000:
			self.move(delta)
			count += 1
		self.move(-delta)

	def slide_right(self,trailer):
		'''
		Slide Shipment to the Right in the Width Direction as far as it can Within the Trailer
		'''
		delta = np.array([0,1,0])
		count = 0
		while trailer.arrangement_is_valid(self) and count < 1000:
			self.move(delta)
			count += 1
		self.move(-delta)

	def slide_left(self,trailer):
		'''
		Slide Shipment to the Left in the Width Direction as far as it can Within the Trailer
		'''
		delta = np.array([0,-1,0])
		count = 0
		while trailer.arrangement_is_valid(self) and count < 1000:
			self.move(delta)
			count += 1
		self.move(-delta)

	def can_stack(self,piece,trailer_height):
		'''
		Check if Provided Piece can be Stacked on top of the Shipment
		'''
		# TODO: Add other stacking options - stack next to on top of
		# TODO: Add maximum weight/pressure restrictions for pieces 
		min_length = min([p.length for p in self.pieces])
		min_width = min([p.width for p in self.pieces])
		
		total_hieght = sum([p.height for p in self.pieces]) + piece.height
		
		current_stack = len(self.pieces)
		stack_limit = min([p.stack_limit for p in self.pieces] + [piece.stack_limit])
		
		# Allow stacking pallets on pallets, boxes on boxes, and boxes on pallets, but not pallets on boxes.
		packing_stackable = not (
			piece.packing == 'PALLET' and 
			any([p.packing == 'BOX' for p in self.pieces])
		)
		return (
			(piece.length <= min_length) and 
			(piece.width <= min_width) and 
			(total_hieght <= trailer_height) and 
			(current_stack < stack_limit) and 
			packing_stackable
		)
		
	def stack(self,piece):
		'''
		Stack Piece on Shipment
		'''
		# Allow stacking in positions other than 0,0 in the length x width dimension
		self._set_dims()
		bottom_piece = self.pieces[-1]
		piece.position = bottom_piece.position + np.array([0,0,bottom_piece.height])
		self.add_piece(piece)
		self._set_dims()
