

def naive_shipment_arrangement(trailer, **kwargs):
	'''
	Arrange Shipment in a Naive Packing, End to End without Optimization
	
	Parameters
	------------
	trailer : logistics_objects.Trailer
		Trailer object to have shipment arranged
	
	Returns
	------------
	None
	'''
	length_pos = 0
	for shipment in trailer.shipments:
		shipment.position[0] = length_pos
		length_pos += shipment.length

