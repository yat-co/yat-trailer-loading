
from ...py3dbp import Packer

no_stack_bin_pack_shipment_arrangement_details = {
	'code' : 'NO_STACK_BIN_PACK',
	'desc' : 'Bin packing algorithm with stacking dissallowed to load shipments onto the trailer',
}

def no_stack_pack_trailer(trailer, trailer_occupy_length : int, allow_rotations=True):
	'''
	Apply Bin Packing Algorithm to Load a Portion of a Trailer

	Parameters
	------------
	trailer : logistics_objects.Trailer
		Trailer object to attempt to load
	trailer_occupy_length : int
		Number of inches of the trailer to allow for loading
	
	Returns
	------------
	loaded_successfully : bool
		True if all items fit in the trailer, False if not
	'''
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


def no_stack_trailer_arrange(trailer, allow_rotations=True,search_method : str = 'bisection', **kwargs):
	'''
	Allocate Shipments in Trailer using an Incremental Bin Packing Algorithm without Stacking

	Parameters
	------------
	trailer : logistics_objects.Trailer
		Trailer object to be optimally loaded
	allow_rotations : bool
		Allow shipments to be rotated in order to load
	search_method : str
		Method for searching for optimal portion of trailer, options: `bisection`, `foot_increment`

	Returns
	------------
	None
	'''

	for shipment in trailer.shipments:
		shipment.position[0] = 0
		shipment.position[1] = 0

	all_shipment_loaded = False
	for shipment in trailer.shipments:
		shipment._update_binpack_item(height=1)
	
	if search_method == 'foot_increment':
		trailer_occupy_length = min([shipment.length for shipment in trailer.shipments]) - 12
		for _ in range(100):
			trailer_occupy_length += 12
			all_shipment_loaded = no_stack_pack_trailer(
				trailer=trailer,
				trailer_occupy_length=trailer_occupy_length,
				allow_rotations=allow_rotations,
			)
			if all_shipment_loaded:
				break
	else:
		a = 0
		b = sum([shipment.length for shipment in trailer.shipments])
		c = round((a+b)/2)
		count = 0
		while count < 25:
			count += 1
			all_shipment_loaded = no_stack_pack_trailer(
				trailer=trailer,
				trailer_occupy_length=c,
				allow_rotations=allow_rotations,
			)
			if all_shipment_loaded:
				b = c
			else:
				a = c
			c = round((a+b)/2)
			if c in (a,b):
				break
		all_shipment_loaded = no_stack_pack_trailer(
			trailer=trailer,
			trailer_occupy_length=b,
			allow_rotations=allow_rotations,
		)
	for shipment in trailer.shipments:
		if shipment.binpack_item.rotation_type == 1:
			shipment.rotate()
		shipment.position[0] = float(shipment.binpack_item.position[1])
		shipment.position[1] = float(shipment.binpack_item.position[0])
