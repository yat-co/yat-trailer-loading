
naive_shipment_arrangement_details = {
	'code' : 'NAIVE',
	'name' : 'Naive Shipment Arrangement',
	'desc' : 'The trivial shipment arrangement - put each shipment in the trailer end to end',
}

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

