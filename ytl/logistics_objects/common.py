
from typing import List
from ..options import (
	DIMENSION_UNIT_OF_MEASURE_OPTIONS,
	WEIGHT_UNIT_OF_MEASURE_OPTIONS,
)
from ..unit_converters import (
	DIMENSION_CONVERTER,VOLUME_CONVERTER,WEIGHT_CONVERTER,
)
from ..py3dbp import Item
from .. import options
import numpy as np
from matplotlib import pyplot


def get_rectangle_plot_lists(ll : List, ur : List, x_padding : float, y_padding : float):
	'''
	Helper Function for Plotting Logistics Objects

	Parameters
	-----------
	ll : List
		List or array of length 2 describing the lower-left corner of the box to be plotted
	ur : List
		List or array of length 2 describing the upper-right corner of the box to be plotted
	x_padding : float
		Padding around the box
	y_padding : float
		Padding around the box
	
	Returns
	----------
	x_list : List
		List of 5 x values to create plot path for the box
	y_list : List
		List of 5 y values to create plot path for the box
	'''
	x_list = [
		ll[0] - x_padding,
		ur[0] + x_padding,
		ur[0] + x_padding,
		ll[0] - x_padding,
		ll[0] - x_padding
	]
	y_list = [
		ll[1] - y_padding,
		ll[1] - y_padding,
		ur[1] + y_padding,
		ur[1] + y_padding,
		ll[1] - y_padding
	]
	return x_list,y_list


class LogisticsObject:
	'''
	Generalized Logistics Object:  Piece, Shipment, or Trailer

	A generic class that handles length, width, and height dimensions
	as well as weight, along with their units.  This is not intended 
	to be a stand-alone object, it is intended to be inherited by 
	other objects to provide basic measurement and weight functionality.
	'''

	default_dimension_units = options.DimUomInches
	default_volume_units = options.VolumeUomCubicFeet
	default_weight_units = options.WeightUomPounds

	def __init__(self,length,height,width,dimension_unit_of_measure,weight,weight_unit_of_measure,**kwargs):
        # Ensure unit of measure are recognized
		assert dimension_unit_of_measure in list(map(lambda x : x[0],DIMENSION_UNIT_OF_MEASURE_OPTIONS))
		assert weight_unit_of_measure in list(map(lambda x : x[0],WEIGHT_UNIT_OF_MEASURE_OPTIONS))
        
        # Set raw and normalized dimensions
		self.dimension_unit_of_measure = dimension_unit_of_measure
		self.length_raw = length
		self.width_raw = width
		self.height_raw = height
		
		self.length = DIMENSION_CONVERTER[dimension_unit_of_measure][self.default_dimension_units](length)
		self.width = DIMENSION_CONVERTER[dimension_unit_of_measure][self.default_dimension_units](width)
		self.height = DIMENSION_CONVERTER[dimension_unit_of_measure][self.default_dimension_units](height)

        # Set raw and normalized weight
		self.weight_unit_of_measure = weight_unit_of_measure
		self.weight_raw = weight
		self.weight = WEIGHT_CONVERTER[weight_unit_of_measure][self.default_weight_units](weight)
        
        # Initialized position as 0,0,0
        # A frame of reference is required to interpret position attribute further
		# The position vector is of the form (length,width,height)
		self.position = np.array([0,0,0])
		self.set_var_types()
		self.is_rotated = False

		# Optional attributes, not used for optimization but for individual object references
		self.id = kwargs.get('id')
		self.name = kwargs.get('name')
		self.desc = kwargs.get('desc')
	
	def set_var_types(self,variables=None,dtype=float):
		'''
		Set Provided Variable Types
		'''
		if isinstance(variables,str):
			variables = [variables]
		if variables is None:
			variables = ['length','width','height','weight','length_raw','width_raw','height_raw','weight_raw']
		for var in variables:
			setattr(self,var,dtype(getattr(self,var)))
			
	def get_volume(self,units=None):
		'''
		Get the Volume of the Logistics Object
		'''
		volume = self.length * self.width * self.height
		if units is None:
			return VOLUME_CONVERTER[f'CUBIC_{self.default_dimension_units}'][self.default_volume_units](volume)
		return VOLUME_CONVERTER[self.default_volume_units][units](volume)
	
	def get_boundaries(self):
		'''
		Get the Profile of the Shipping Object
		'''
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
		'''
		Rotate the Object

		Rotations are treated as 90 degree rotations in the length x width
		plane.  Use the `is_rotated` attribute to determine if the object
		is in its original orientation or has been rotated.
		'''
		self.length, self.width = self.width, self.length
		self.length_raw, self.width_raw = self.width_raw, self.length_raw
		self.is_rotated = not self.is_rotated
	
	def get_weight(self,units=None):
		'''
		Get Weight of Logistics Object
		'''
		if units is None:
			return self.weight
		return VOLUME_CONVERTER[self.default_weight_units][units](self.weight)


class ShippingObject(LogisticsObject):
	'''
	Generalized Piece or Shipment that is Meant to be Moved Around Inside a Parent LogisticsObject
	'''

	def __init__(self,*args,**kwargs):
		super(ShippingObject,self).__init__(*args,**kwargs)
		self._binpack_item_exists = False
	
	def _set_binpack_item(self,**kwargs):
		'''
		Create a Bin Packing Object Associated to This Shipping Object
		'''
		if not self._binpack_item_exists:
			width = kwargs.get('width',self.width)
			height = kwargs.get('height',self.height)
			length = kwargs.get('length',self.length)
			weight = kwargs.get('weight',self.weight)
			self.binpack_item = Item(
				name = kwargs.get('name',getattr(self,'name','Unnamed Shipping Object')),
				width = width, 
				height = length,
				depth = height,
				weight = weight
			)
			self._binpack_item_exists = True
	
	def _delete_binpack_item(self):
		'''
		Delete Bin Packing Object
		'''
		if hasattr(self,'binpack_item'):
			delattr(self,'binpack_item')
		self._binpack_item_exists = False
	
	def _update_binpack_item(self,*args,**kwargs):
		'''
		Delete and Recreate Bin Packing Object
		'''
		self._delete_binpack_item()
		self._set_binpack_item(*args,**kwargs)
	
	def plot(self,*args,**kwargs):
		'''
		Plot the Container in the Length x Width Dimension
		'''
		boundaries = self.get_boundaries()
		x_list,y_list = get_rectangle_plot_lists(
			ll=kwargs.pop('h_offset',0) + boundaries[:,0], 
			ur=kwargs.pop('v_offset',0) + boundaries[:,1], 
			x_padding=kwargs.pop('h_padding',0), 
			y_padding=kwargs.pop('v_padding',0)
		)
		pyplot.plot(x_list,y_list,**kwargs)

	def fill(self,*args,**kwargs):
		'''
		Fill Plot the Container in the Length x Width Dimension
		'''
		boundaries = self.get_boundaries()
		x_list,y_list = get_rectangle_plot_lists(
			ll=kwargs.pop('h_offset',0) + boundaries[:,0], 
			ur=kwargs.pop('v_offset',0) + boundaries[:,1], 
			x_padding=kwargs.pop('h_padding',0), 
			y_padding=kwargs.pop('v_padding',0)
		)
		pyplot.fill(x_list,y_list,**kwargs)
