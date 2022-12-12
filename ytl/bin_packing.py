
from .py3dbp import (
	Bin,
	NoRotateBin,
	Item,
)
from .options import (
	PACKING_OPTIONS,
	DIMENSION_UNIT_OF_MEASURE_OPTIONS,
	WEIGHT_UNIT_OF_MEASURE_OPTIONS,
)
from .unit_converters import (
	DIMENSION_CONVERTER,VOLUME_CONVERTER,WEIGHT_CONVERTER,
)
from .utils import intervals_overlap,interval_is_subset
from .optimizer_functions import SHIPMENT_ARRANGEMENT_ROUTER

import numpy as np
from matplotlib import pyplot

'''
OOP inheritance structure

LogisticsObject
	ShippingObject
		Piece - non-divisible shipment items
		Shipment - collections of Piece objects, treated as single items to be arranged in Trailer
	Trailer
'''


class LogisticsObject:
	'''
	Generalized shipment item, piece, or trailer, associated to py3dbp.Item or py3dbp.Bin
	'''

	default_dimension_units = 'IN'
	default_volume_units = 'CUBIC_FT'
	default_weight_units = 'LBS'

	def __init__(self,length,height,width,dimension_unit_of_measure,weight,weight_unit_of_measure,*args,**kwargs):
		assert dimension_unit_of_measure in list(map(lambda x : x[0],DIMENSION_UNIT_OF_MEASURE_OPTIONS))
		assert weight_unit_of_measure in list(map(lambda x : x[0],WEIGHT_UNIT_OF_MEASURE_OPTIONS))

		self.dimension_unit_of_measure = dimension_unit_of_measure

		self.length_raw = length
		self.width_raw = width
		self.height_raw = height
		
		self.length = DIMENSION_CONVERTER[dimension_unit_of_measure][self.default_dimension_units](length)
		self.width = DIMENSION_CONVERTER[dimension_unit_of_measure][self.default_dimension_units](width)
		self.height = DIMENSION_CONVERTER[dimension_unit_of_measure][self.default_dimension_units](height)

		self.weight_unit_of_measure = weight_unit_of_measure
		self.weight_raw = weight
		self.weight = WEIGHT_CONVERTER[weight_unit_of_measure][self.default_weight_units](weight)

		self.is_rotated = False
		# (length,width,height)
		self.position = np.array([0,0,0])
		self.set_var_types()
	
	def set_var_types(self,variables=None,dtype=float):
		if isinstance(variables,str):
			variables = [variables]
		if variables is None:
			variables = ['length','width','height','weight','length_raw','width_raw','height_raw','weight_raw']
		for var in variables:
			setattr(self,var,dtype(getattr(self,var)))
			
	def get_volume(self,units=None):
		volume = self.length * self.width * self.height
		if units is None:
			return VOLUME_CONVERTER[f'CUBIC_{self.default_dimension_units}'][self.default_volume_units](volume)
		return VOLUME_CONVERTER[self.default_volume_units][units](volume)
	
	def get_boundaries(self):
		boundaries = np.array([
			self.position[0],
			self.position[0] + self.length,
			self.position[1],
			self.position[1] + self.width,
			self.position[2],
			self.position[2] + self.height,
		])
		boundaries.shape = (3,2)
		return boundaries
	
	def rotate(self):
		self.length, self.width = self.width, self.length
		self.length_raw, self.width_raw = self.width_raw, self.length_raw
		self.is_rotated = not self.is_rotated
	
	def get_weight(self,units=None):
		if units is None:
			return self.weight
		return VOLUME_CONVERTER[self.default_weight_units][units](self.weight)


class ShippingObject(LogisticsObject):
	'''
	Generalized shipment item or piece, associated to py3dbp.Item
	'''

	def __init__(self,*args,**kwargs):
		super(ShippingObject,self).__init__(*args,**kwargs)
		self._binpack_item_exists = False
	
	def _set_binpack_item(self,*args,**kwargs):
		if not self._binpack_item_exists:
			width = kwargs.get('width',self.width)
			height = kwargs.get('height',self.height)
			length = kwargs.get('length',self.length)
			weight = kwargs.get('weight',self.weight)
			self.binpack_item = Item(
				name        = kwargs.get('name',getattr(self,'name','Unnamed Shipping Object')),
				width       = width, 
				height      = length,
				depth       = height,
				weight      = weight
			)
			self._binpack_item_exists = True
	
	def _delete_binpack_item(self):
		if hasattr(self,'binpack_item'):
			delattr(self,'binpack_item')
		self._binpack_item_exists = False
	
	def _update_binpack_item(self,*args,**kwargs):
		self._delete_binpack_item()
		self._set_binpack_item(*args,**kwargs)
	
	def plot(self,*args,**kwargs):
		h_padding = kwargs.pop('h_padding',0)
		v_padding = kwargs.pop('v_padding',0)
		h_offset = kwargs.pop('h_offset',0)
		v_offset = kwargs.pop('v_offset',0)
		boundaries = self.get_boundaries()
		ll = h_offset + boundaries[:,0]
		ur = v_offset + boundaries[:,1]
		pyplot.plot(
			[ll[0]-h_padding,ur[0]+h_padding,ur[0]+h_padding,ll[0]-h_padding,ll[0]-h_padding],
			[ll[1]-v_padding,ll[1]-v_padding,ur[1]+v_padding,ur[1]+v_padding,ll[1]-v_padding],
			**kwargs
		)

	def fill(self,*args,**kwargs):
		h_padding = kwargs.pop('h_padding',0)
		v_padding = kwargs.pop('v_padding',0)
		h_offset = kwargs.pop('h_offset',0)
		v_offset = kwargs.pop('v_offset',0)
		boundaries = self.get_boundaries()
		ll = h_offset + boundaries[:,0]
		ur = v_offset + boundaries[:,1]
		pyplot.fill(
			[ll[0]-h_padding,ur[0]+h_padding,ur[0]+h_padding,ll[0]-h_padding,ll[0]-h_padding],
			[ll[1]-v_padding,ll[1]-v_padding,ur[1]+v_padding,ur[1]+v_padding,ll[1]-v_padding],
			**kwargs
		)

class Piece(ShippingObject):
	'''
	Individual box or pallet, not to be separated for stacking/storing - the atomic element of this model, not to be split
	'''
	def __init__(self,packing,name,stack_limit,desc=None,commodity=None,value=None,*args,**kwargs):
		super(Piece,self).__init__(*args,**kwargs)
		assert packing in list(map(lambda x : x[0],PACKING_OPTIONS))
		assert stack_limit > 0

		self.packing = packing
		self.name = name
		self.desc = desc
		self.commodity = commodity
		self.value = value
		self.stack_limit = stack_limit

		self._set_binpack_item()


class Shipment(ShippingObject):
	'''
	Individual box or pallet, not to be separated for stacking/storing - the atomic element of this model, not to be split
	'''
	def __init__(self,pieces=[],*args,**kwargs):
		if isinstance(pieces,Piece):
			pieces = [pieces]
		self.pieces = []
		self.add_piece(pieces)
		self.arrange_pieces()
		super(Shipment,self).__init__(
			length                          = self.length,
			width                           = self.width,
			height                          = self.height,
			dimension_unit_of_measure       = self.default_dimension_units,
			weight                          = self.weight,
			weight_unit_of_measure          = self.default_weight_units,
			*args,
			**kwargs
		)
		self._binpack_bin_exists = False
		self.max_weight = 100000

	def arrange_pieces(self,*args,**kwargs):
		length_pos = 0
		for piece in self.pieces:
			piece.position[0] = length_pos
			length_pos += piece.length
		self._set_dims()

	def _set_dims(self):
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
		if isinstance(piece,Piece):
			piece = [piece]
		assert all([isinstance(p,Piece) for p in piece])
		self.pieces += piece

	def remove_piece(self,piece):
		if isinstance(piece,Piece):
			self.pieces = [p for p in self.pieces if p != piece]
			return piece
		elif isinstance(piece,int):
			return self.pieces.pop(piece)
		else:
			raise Exception(f'Data type for {piece} not recognized')

	def get_boundaries(self):
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
	
	def _set_binpack_bin(self,allow_rotations=True,*args,**kwargs):
		if not self._binpack_bin_exists:
			width = kwargs.get('width',self.width)
			height = kwargs.get('height',self.height)
			length = kwargs.get('length',self.length)
			max_weight = kwargs.get('max_weight',self.weight)
			if allow_rotations:
				self.binpack_bin = Bin(
					name            = kwargs.get('name',getattr(self,'name','Unnamed Shipment Object')),
					width           = width, 
					height          = length,
					depth           = height,
					max_weight      = max_weight
				)
			else:
				self.binpack_bin = NoRotateBin(
					name            = kwargs.get('name',getattr(self,'name','Unnamed Shipment Object')),
					width           = width, 
					height          = length,
					depth           = height,
					max_weight      = max_weight
				)
			self._binpack_bin_exists = True
	
	def _delete_binpack_bin(self):
		if hasattr(self,'binpack_item'):
			delattr(self,'binpack_item')
		self._binpack_bin_exists = False
	
	def _update_binpack_bin(self,allow_rotations=True,*args,**kwargs):
		self._delete_binpack_bin()
		self._set_binpack_bin(allow_rotations=allow_rotations,*args,**kwargs)
	
	def arrangement_is_valid(self):
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

		for piece in self.pieces:
			piece.position[0],piece.position[1] = piece.position[1],piece.position[0]
			piece.length, piece.width = piece.width, piece.length
			piece.length_raw, piece.width_raw = piece.width_raw, piece.length_raw
			piece.is_rotated = not piece.is_rotated
	
	def move(self,delta):
		self.position += delta
	
	def slide_back(self,trailer):
		delta = np.array([-1,0,0])
		count = 0
		while trailer.arrangement_is_valid(self) and count < 1000:
			self.move(delta)
			count += 1
		self.move(-delta)

	def slide_right(self,trailer):
		delta = np.array([0,1,0])
		count = 0
		while trailer.arrangement_is_valid(self) and count < 1000:
			self.move(delta)
			count += 1
		self.move(-delta)

	def slide_left(self,trailer):
		delta = np.array([0,-1,0])
		count = 0
		while trailer.arrangement_is_valid(self) and count < 1000:
			self.move(delta)
			count += 1
		self.move(-delta)

	def can_stack(self,piece,trailer_height):
		min_length = min([p.length for p in self.pieces])
		min_width = min([p.width for p in self.pieces])
		
		total_hieght = sum([p.height for p in self.pieces]) + piece.height
		
		current_stack = len(self.pieces)
		stack_limit = min([p.stack_limit for p in self.pieces] + [piece.stack_limit])

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
		self._set_dims()
		bottom_piece = self.pieces[-1]
		piece.position = bottom_piece.position + np.array([0,0,bottom_piece.height])
		self.add_piece(piece)
		self._set_dims()


class Trailer(LogisticsObject):
	'''
	Generalized Trailer object, associated to py3dbp.Bin
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

	def arrange_shipments(self,algorithm='NO_STACK_BIN_PACK',*args,**kwargs):
		SHIPMENT_ARRANGEMENT_ROUTER[algorithm](self,*args,**kwargs)

	def get_boundaries(self):
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
		if isinstance(shipment,Shipment):
			shipment = [shipment]
		assert all([isinstance(s,Shipment) for s in shipment])
		self.shipments += shipment

	def remove_shipment(self,shipment):
		if isinstance(shipment,Shipment):
			self.shipments = [s for s in self.shipments if s != shipment]
			return shipment
		elif isinstance(shipment,int):
			return self.shipments.pop(shipment)
		else:
			raise Exception(f'Data type for {shipment} not recognized')

	def _set_binpack_bin(self,allow_rotations=True,*args,**kwargs):
		if not self._binpack_bin_exists:
			width = kwargs.get('width',self.width)
			height = kwargs.get('height',self.height)
			length = kwargs.get('length',self.length)
			max_weight = kwargs.get('max_weight',self.max_weight)
			if allow_rotations:
				self.binpack_bin = Bin(
					name            = kwargs.get('name',getattr(self,'name','Unnamed Shipment Object')),
					width           = width, 
					height          = length,
					depth           = height,
					max_weight      = max_weight
				)
			else:
				self.binpack_bin = NoRotateBin(
					name            = kwargs.get('name',getattr(self,'name','Unnamed Shipment Object')),
					width           = width, 
					height          = length,
					depth           = height,
					max_weight      = max_weight
				)
			self._binpack_bin_exists = True
	
	def _delete_binpack_bin(self):
		if hasattr(self,'binpack_item'):
			delattr(self,'binpack_item')
		self._binpack_bin_exists = False
	
	def _update_binpack_bin(self,allow_rotations=True,*args,**kwargs):
		self._delete_binpack_bin()
		self._set_binpack_bin(allow_rotations=allow_rotations,*args,**kwargs)
	
	def arrangement_is_valid(self,shipment=None):
		trailer_boundaries = np.array([[0,self.length],[0,self.width],[0,self.height]])
		if shipment is None:
			shipment_boundaries_list = [shipment.get_boundaries() for shipment in self.shipments]
			for i in range(len(shipment_boundaries_list)):
				s_i = shipment_boundaries_list[i]
				in_trailer = all([interval_is_subset(s_i[k],trailer_boundaries[k]) for k in range(3)])
				if not in_trailer:
					return False
				for j in range(i):
					s_j = shipment_boundaries_list[j]
					overlap = all([intervals_overlap(s_i[k],s_j[k]) for k in range(3)])
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
		trailer_center = self.width / 2
		for shipment in self.shipments:
			boundaries = shipment.get_boundaries()
			center = np.mean(boundaries[1,:])
			if center < trailer_center:
				shipment.slide_left(self)
			else:
				shipment.slide_right(self)

	def plot(self):
		ll = self.position
		ur = [self.length,self.width,self.height]
		trailer_padding = 3
		
		pyplot.figure(figsize=(self.length/25,self.width/25))
		pyplot.plot([ll[0]-trailer_padding,ur[0]+trailer_padding,ur[0]+trailer_padding,ll[0]-trailer_padding,ll[0]-trailer_padding],[ll[1]-trailer_padding,ll[1]-trailer_padding,ur[1]+trailer_padding,ur[1]+trailer_padding,ll[1]-trailer_padding],color='black',linewidth=6)
		
		for shipment in self.shipments:
			s_ll = shipment.position
			for piece in shipment.pieces:
				piece.plot(h_offset=s_ll,v_offset=s_ll,h_padding=-2,v_padding=-2,color='red',linewidth=2)
				piece.fill(h_offset=s_ll,v_offset=s_ll,h_padding=-2,v_padding=-2,color='red',alpha=.2)
			shipment.plot(h_offset=ll,v_offset=ll,h_padding=-1,v_padding=0,color='blue',linewidth=2)
			shipment.fill(h_offset=ll,v_offset=ll,h_padding=-1,v_padding=0,color='blue',alpha=.2)
			boundaries = shipment.get_boundaries()
			x = .5 * boundaries[0,0] + .5 * boundaries[0,1]
			y = .5 * boundaries[1,0] + .5 * boundaries[1,1]
			shipment_str = str(len(shipment.pieces))
			pyplot.text(x,y,shipment_str)
		pyplot.title('Trailer Load Plan',fontsize=20)
		pyplot.xticks([i for i in range(0,int(self.length)+1,12*4)],[int(i/12) for i in range(0,int(self.length)+1,12*4)])
		pyplot.xlabel('Feet',fontsize=18)
		pyplot.ylabel('Inches',fontsize=18)
		pyplot.show()

	def get_linear_feet(self):
		boundaries = self.get_boundaries()
		return DIMENSION_CONVERTER[self.default_dimension_units]['FT'](boundaries[0,1] - boundaries[0,0])

	def _set_weight(self):
		if len(self.shipments) == 0:
			self.weight = 0
		else:
			self.weight = sum([shipment.weight for shipment in self.shipments])

	def get_load_order(self):
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

		linear_feet = self.get_linear_feet()
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
		self._set_weight()
		return self.weight > self.max_weight
		