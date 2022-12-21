
from .common import ShippingObject
from ..options import PACKING_OPTIONS

class Piece(ShippingObject):
	'''
	Indivisible Box or Pallet

	This shipping object is intended to be an indivisible
	shipping item, i.e. one that must be loaded without
	being taken apart or separated.
	'''

	def __init__(self,packing,stack_limit,commodity=None,value=None,*args,**kwargs):
		super(Piece,self).__init__(*args,**kwargs)
		# Ensure a valid packing type is provided
		assert packing in list(map(lambda x : x[0],PACKING_OPTIONS))
		# Ensure a valid stack_limit is provided
		assert stack_limit > 0

		self.packing = packing
		self.commodity = commodity
		self.value = value
		self.stack_limit = stack_limit

		self._set_binpack_item()

