
from .common import LogisticsObject
from .shipment import Shipment
from ..py3dbp import (
	Bin,
	NoRotateBin,
)
from ..unit_converters import (
	DIMENSION_CONVERTER,VOLUME_CONVERTER,
)
from ..utils import intervals_overlap,interval_is_subset

import numpy as np
from matplotlib import pyplot

class Trailer(LogisticsObject):
	'''
	Generalized Trailer Object
	'''
	
	def __init__(self,max_weight,shipments=[],name='Unnamed Trailer',*args,**kwargs):
		if isinstance(shipments,Shipment):
			shipments = [shipments]
		super(Trailer,self).__init__(*args,**kwargs)

		self.max_weight = max_weight
		self.name = name
		self.shipments = []
		self.add_shipment(shipments)

		self._binpack_bin_exists = False
		self.set_var_types(variables='max_weight',dtype=float)

	def get_boundaries(self):
		'''
		Get Trailer Profile
		'''
		if len(self.shipments) == 0:
			boundaries = np.array([0,0,0,0,0,0])
			boundaries.shape = (3,2)
			return boundaries
		boundaries = np.array([np.inf,-np.inf,np.inf,-np.inf,np.inf,-np.inf])
		boundaries.shape = (3,2)
		for shipment in self.shipments:
			shipment_boundaries = shipment.get_boundaries()
			for i in range(3):
				boundaries[i,0] = min([boundaries[i,0],shipment_boundaries[i,0]])
				boundaries[i,1] = max([boundaries[i,1],shipment_boundaries[i,1]])
		for i in range(3):
			boundaries[i,0] += self.position[i]
			boundaries[i,1] += self.position[i]
		return boundaries
	
	def add_shipment(self,shipment):
		'''
		Add Shipment to Trailer
		'''
		if isinstance(shipment,Shipment):
			shipment = [shipment]
		assert all([isinstance(s,Shipment) for s in shipment])
		self.shipments += shipment

	def remove_shipment(self,shipment):
		'''
		Remove Shipment from Trailer
		'''
		if isinstance(shipment,Shipment):
			self.shipments = [s for s in self.shipments if s != shipment]
			return shipment
		elif isinstance(shipment,int):
			return self.shipments.pop(shipment)
		else:
			raise Exception(f'Data type for {shipment} not recognized')

	def _set_binpack_bin(self,allow_rotations=True,*args,**kwargs):
		'''
		Set Bin Packing Object
		'''
		if not self._binpack_bin_exists:
			width = kwargs.get('width',self.width)
			height = kwargs.get('height',self.height)
			length = kwargs.get('length',self.length)
			max_weight = kwargs.get('max_weight',self.max_weight)
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
		Delete and Recreate Bid Pack Item
		'''
		self._delete_binpack_bin()
		self._set_binpack_bin(allow_rotations=allow_rotations,*args,**kwargs)
	
	def arrangement_is_valid(self,shipment=None):
		'''
		Validate that the Arrangement of Shipments in Trailer is Physically Possible
		'''
		trailer_boundaries = np.array([[0,self.length],[0,self.width],[0,self.height]])
		if shipment is None:
			shipment_boundaries_list = [shipment.get_boundaries() for shipment in self.shipments]
			for i in range(len(shipment_boundaries_list)):
				s_i = shipment_boundaries_list[i]
				# Validate shipment is inside the trailer
				in_trailer = all(
					[interval_is_subset(s_i[k],trailer_boundaries[k]) for k in range(3)]
				)
				if not in_trailer:
					return False
				for j in range(i):
					s_j = shipment_boundaries_list[j]
					# Validate shipment does not occupy the same space as any other previous shipment
					overlap = all(
						[intervals_overlap(s_i[k],s_j[k]) for k in range(3)]
					)
					if overlap:
						return False
			return True
		else:
			shipment_boundaries_list = [s.get_boundaries() for s in self.shipments if s != shipment]
			s_i = shipment.get_boundaries()
			in_trailer = all([interval_is_subset(s_i[k],trailer_boundaries[k]) for k in range(3)])
			if not in_trailer:
				return False
			for s_j in shipment_boundaries_list:
				overlap = all([intervals_overlap(s_i[k],s_j[k]) for k in range(3)])
				if overlap:
					return False
			return True

	def balance(self):
		'''
		Move Shipments to the Side Walls of the Trailer
		'''
		trailer_center = self.width / 2
		for shipment in self.shipments:
			boundaries = shipment.get_boundaries()
			center = np.mean(boundaries[1,:])
			if center < trailer_center:
				shipment.slide_left(self)
			else:
				shipment.slide_right(self)

	def plot(self):
		'''
		Plot an Overview of the Trailer Load Plan
		'''
		ll = self.position
		ur = [self.length,self.width,self.height]
		trailer_padding = 3
		
		pyplot.figure(figsize=(self.length/25,self.width/25))
		pyplot.plot(
			[
				ll[0]-trailer_padding,
				ur[0]+trailer_padding,
				ur[0]+trailer_padding,
				ll[0]-trailer_padding,
				ll[0]-trailer_padding
			],
			[
				ll[1]-trailer_padding,
				ll[1]-trailer_padding,
				ur[1]+trailer_padding,
				ur[1]+trailer_padding,
				ll[1]-trailer_padding
			],
			color='black',
			linewidth=6
		)
		
		for shipment in self.shipments:
			s_ll = shipment.position
			for piece in shipment.pieces:
				piece.plot(
					h_offset=s_ll,
					v_offset=s_ll,
					h_padding=-2,
					v_padding=-2,
					color='red',
					linewidth=2
				)
				piece.fill(
					h_offset=s_ll,
					v_offset=s_ll,
					h_padding=-2,
					v_padding=-2,
					color='red',
					alpha=.2
				)
			shipment.plot(
				h_offset=ll,
				v_offset=ll,
				h_padding=-1,
				v_padding=0,
				color='blue',
				linewidth=2
			)
			shipment.fill(
				h_offset=ll,
				v_offset=ll,
				h_padding=-1,
				v_padding=0,
				color='blue',
				alpha=.2
			)
			boundaries = shipment.get_boundaries()
			x = .5 * boundaries[0,0] + .5 * boundaries[0,1]
			y = .5 * boundaries[1,0] + .5 * boundaries[1,1]
			shipment_str = str(len(shipment.pieces))
			pyplot.text(x,y,shipment_str)
		pyplot.title('Trailer Load Plan',fontsize=20)
		pyplot.xticks(
			[i for i in range(0,int(self.length)+1,12*4)],
			[int(i/12) for i in range(0,int(self.length)+1,12*4)]
		)
		pyplot.xlabel('Feet',fontsize=18)
		pyplot.ylabel('Inches',fontsize=18)
		pyplot.show()

	def get_linear_feet(self):
		'''
		Get Linear Feet for Trailer Load Plan
		'''
		boundaries = self.get_boundaries()
		return DIMENSION_CONVERTER[self.default_dimension_units]['FT'](boundaries[0,1] - boundaries[0,0])

	def _set_weight(self):
		'''
		Calculate and Update Trailer Total Weight
		'''
		if len(self.shipments) == 0:
			self.weight = 0
		else:
			self.weight = sum([shipment.weight for shipment in self.shipments])

	def get_load_order(self):
		'''
		Get Load Plan in the Order They Need to be Loaded
		'''
		load_order = {}
		idx = 1
		for shipment in sorted(self.shipments,key=lambda x : x.position[0] * 10000 + x.position[1]):
			for piece in sorted(shipment.pieces,key=lambda x : x.position[2]):
				load_order.update({
					idx : {
						'name' : piece.name,
						'position' : list(shipment.position + piece.position),
						'piece_width' : piece.width,
						'piece_length' : piece.length,
						'piece_height' : piece.height,
						'piece_weight' : piece.weight,
						'piece_packing' : piece.packing,
						'piece_is_rotated' : piece.is_rotated,
						'piece_is_stacked' : piece.position[2] > 0,
					}
				})
				idx += 1
		return load_order

	def get_summary(self):
		'''
		Get Summary of Optimized Trailer Load Plan
		'''
		num_pieces = sum([len(shipment.pieces) for shipment in self.shipments])
		volume = 0
		for shipment in self.shipments:
			for piece in shipment.pieces:
				volume += piece.length * piece.width * piece.height

		actual_cube = 0
		for shipment in self.shipments:
			shipment._set_dims()
			actual_cube += sum([piece.length * piece.width * piece.height for piece in shipment.pieces])

		stacked_cube = sum([shipment.length * shipment.width * shipment.height for shipment in self.shipments])
		trailer_cube = sum([shipment.length * shipment.width * self.height for shipment in self.shipments])

		linear_feet = self.get_linear_feet()

		linear_feet_portion_of_trailer = DIMENSION_CONVERTER['FT'][self.default_dimension_units](linear_feet) / self.length
		actual_cube_portion_of_trailer = actual_cube / self.length / self.width / self.height
		stacked_cube_portion_of_trailer = stacked_cube / self.length / self.width / self.height
		trailer_cube_portion_of_trailer = trailer_cube / self.length / self.width / self.height
		weight_portion_of_trailer = self.weight / self.max_weight

		trailer_stats = {
			'trailer_max_weight' : self.max_weight,
			'trailer_length' : self.length,
			'trailer_width' : self.width,
			'trailer_height' : self.height,
			'arrangement_is_valid' : self.arrangement_is_valid(),
			'trailer_is_overweight' : self.is_overweight(),
			'trailer_capacity_cube' : VOLUME_CONVERTER['CUBIC_IN']['CUBIC_FT'](self.length * self.width * self.height),

			'num_pieces' : num_pieces,

			'total_weight' : self.weight,
			'linear_feet' : linear_feet,
			'actual_cube' : VOLUME_CONVERTER['CUBIC_IN']['CUBIC_FT'](actual_cube),
			'stacked_cube' : VOLUME_CONVERTER['CUBIC_IN']['CUBIC_FT'](stacked_cube),
			'trailer_cube' : VOLUME_CONVERTER['CUBIC_IN']['CUBIC_FT'](trailer_cube),

			'weight_portion_of_trailer' : weight_portion_of_trailer,
			'linear_feet_portion_of_trailer' : linear_feet_portion_of_trailer,
			'actual_cube_portion_of_trailer' : actual_cube_portion_of_trailer,
			'stacked_cube_portion_of_trailer' : stacked_cube_portion_of_trailer,
			'trailer_cube_portion_of_trailer' : trailer_cube_portion_of_trailer,

			'load_order' : self.get_load_order()
		}
		return trailer_stats

	def is_overweight(self):
		'''
		Check if Loaded Trailer is Overweight
		'''
		self._set_weight()
		return self.weight > self.max_weight
		