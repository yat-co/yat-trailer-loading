
import time
import numpy as np

simple_movement_slide_back_shipment_arrangement_details = {
	'code' : 'SLIDE_BACK',
	'name' : 'Slide Back Shipment Arrangement',
	'desc' : 'Attempt to slide shipments back in the trailer where space is available - Cannot be run stand-alone, intended to be run after `NO_STACK_BIN_PACK`',
}

def slide_shipments_back(trailer, max_iter : int = None, timeout : float = None, **kwargs):
	'''
	Slide Shipment Back in Trailer

	Parameters
	------------
	trailer : logistics_objects.Trailer
		Trailer object for shipments to be arranged
	max_iter : int
		Number of iterations to run
	timeout : float 
		Timeout for main loop of optimization
	
	Returns
	------------
	None
	'''
	max_iter = max_iter or 5
	start_time = time.perf_counter()
	break_loop = False
	index_order = np.argsort([
        shipment.position[0] for shipment in trailer.shipments
    ])
	for count in range(max_iter):
		for i in index_order:
			shipment = trailer.shipments[i]
			directions = np.random.choice(a=['left', 'right'], replace=False, size=2)
			shipment.slide_back(trailer)
			for d in directions:
				if d == 'left':
					shipment.slide_left(trailer)
				else:
					shipment.slide_right(trailer)
				shipment.slide_back(trailer)
			
			if timeout is not None:
				if time.perf_counter() - start_time > timeout and count > 0:
					break_loop = True
					break
		if break_loop:
			break
	shipment._set_dims()
	trailer.balance()
