
from typing import Dict
from .trailer_load import optimize_trailer_load_plan
from ..exceptions import (
	TooManyPiecesException,
	NoPiecesException,
	PiecesTooLongForServiceException,
	OptimizationFailedServiceException,
	TrailerLoadingException,
	InvalidTrailerDimensionsException,
	InvalidPiecesException,
)
from ..optimizer_functions import PIECE_ARRANGEMENT_ROUTER, SHIPMENT_ARRANGEMENT_ROUTER
from ..standard_logistic_dims import STANDARD_TRAILER_DIMS
from .. import options
from copy import deepcopy
import numpy as np
import json

STANDARD_TRAILER_DIM_MAP = {
	obj.get('code') : obj for obj in STANDARD_TRAILER_DIMS
}

class NumpyArrayEncoder(json.JSONEncoder):
	'''
	Add serialization rules for numpy int, float, and boolean objects
	'''
	def default(self, obj):
		if isinstance(obj, np.int_):
			return int(obj)
		if isinstance(obj, np.float_):
			return float(obj)
		if isinstance(obj, np.bool_):
			return bool(obj)
		return json.JSONEncoder.default(self, obj)

def parse_request_data(request_data : Dict):
	'''
	Parse Request Data for Trailer Load Optimization API Serivce

	Parameters
	-----------
	request_data : Dict
		Dictionary of the form 
	
	Returns
	-----------
	status_code : int
		Status code of 4** for invalid request data, 200 for valid request data
	parsed_request_data : Dict
		Parsed request data, {} if status_code is 4**
	errors : Dict
		Error dictionary, {} if status_code is 200
	'''
	parsed_request_data = {}
	
	# Parse trailer dims/equipment code
	if isinstance(request_data.get('trailer_dims'),dict):
		parsed_request_data.update({'trailer_dims' : request_data['trailer_dims']})
	elif request_data.get('equipment_code') in STANDARD_TRAILER_DIM_MAP:
		# map equipment_code to appropriate trailer_dims
		parsed_request_data.update({'trailer_dims' : STANDARD_TRAILER_DIM_MAP[request_data['equipment_code']]})
	elif isinstance(request_data.get('equipment_code'),str):
		# if equipment code is passed, but not an option return a 400 error
		return 400,{},{
			'error_code' : 'InvalidTrailerDimensionsException',
			'error_message' : 'Equipment code not recognized',
		}
	else:
		return 400,{},{
			'error_code' : 'InvalidTrailerDimensionsException',
			'error_message' : 'Invalid trailer dimensions or equipment type provided',
		}
	
	# Parse shipment list
	if isinstance(request_data.get('shipment_list'),list):
		parsed_request_data.update({'shipment_list' : request_data['shipment_list']})
	elif hasattr(request_data.get('shipment_list'),'__iter__'):
		parsed_request_data.update({'shipment_list' : list(request_data['shipment_list'])})
	else:
		return 400,{},{
			'error_code' : 'InvalidPiecesException',
			'error_message' : 'Invalid pieces provided',
		}
	if not all([isinstance(shipment,dict) for shipment in parsed_request_data['shipment_list']]):
		return 400,{},{
			'error_code' : 'InvalidPiecesException',
			'error_message' : 'Invalid pieces provided',
		}
	for shipment in parsed_request_data['shipment_list']:
		shipment.update({
			"dimension_unit_of_measure": options.DimUomInches,
			"weight_unit_of_measure": options.WeightUomPounds,
		})

	# Parse allow rotations parameter
	if request_data.get('allow_rotations') == False:
		parsed_request_data.update({'allow_rotations' : False})
	elif request_data.get('allow_rotations') == True or request_data.get('allow_rotations') is None:
		# if allow_rotation is passed as True or not provided, set true
		parsed_request_data.update({'allow_rotations' : True})
	else:
		# If allow rotations is not None and non-boolean, raise validation error
		return 400,{},{
			'error_code' : 'InvalidPiecesException',
			'error_message' : 'Invalid allow rotations parameter',
		}
	
	if request_data.get('overweight_shipment_threshold') is not None:
		try:
			parsed_request_data.update({'overweight_shipment_threshold' : float(request_data['overweight_shipment_threshold'])})
		except:
			# If allow rotations is not None and non-boolean, raise validation error
			return 400,{},{
				'error_code' : 'InvalidPiecesException',
				'error_message' : 'Invalid overweight shipment threshold parameter',
			}
	
	if request_data.get('piece_arrangement_algorithm') is not None:
		if request_data.get('piece_arrangement_algorithm') in PIECE_ARRANGEMENT_ROUTER:
			parsed_request_data.update({'piece_arrangement_algorithm' : request_data['piece_arrangement_algorithm']})
		else:
			return 400,{},{
				'error_code' : 'OptimizationFailedServiceException',
				'error_message' : 'Invalid piece arrangement parameter provided',
			}
	
	if request_data.get('shipment_optimization_ls') is not None:
		try:
			for params in request_data.get('shipment_optimization_ls'):
				assert isinstance(params,dict)
				assert params['algorithm'] in SHIPMENT_ARRANGEMENT_ROUTER
				assert isinstance(params.get('max_iter'),(int,type(None)))
				assert isinstance(params.get('timeout'),(int,float,type(None)))
			parsed_request_data.update({'shipment_optimization_ls' : request_data['shipment_optimization_ls']})
		except:
			return 400,{},{
				'error_code' : 'OptimizationFailedServiceException',
				'error_message' : 'Invalid shipment arrangement parameter provided',
			}

	return 200,parsed_request_data,{}


def optimize_trailer_load_plan_wrapper(request_data : Dict):
	'''
	Trailer Load Optimization Function Intended for Use with API

	Parameters
	------------
	request_data : Dict
		Request data for trailer loading optimization
	
	Returns
	------------
	status_code : int 
		Status code to be used for API response
	response_dict : Dict
		Response, trailer loading result when status_code is 200, error summary when status_code is not 200
	'''
	# Parse request data
	try:
		request_status_code,parsed_request_data,errors = parse_request_data(request_data=deepcopy(request_data))
		if request_status_code != 200:
			return request_status_code,errors
	except:
		return 400,{
			'error_code' : 'InvalidRequestException',
			'error_message' : 'Invalid request',
			'request' : request_data,
		}
	
	# Do trailer load optimization
	try:
		trailer = optimize_trailer_load_plan(**parsed_request_data)
		if not trailer.arrangement_is_valid():
			return 500,{
				'error_code' : 'TrailerLoadingException',
				'error_message' : 'Unknown error',
			}
		trailer_load_plan = trailer.get_summary()
		trailer_load_plan = json.loads(json.dumps(trailer_load_plan,cls=NumpyArrayEncoder))
		return 200,trailer_load_plan
	except TooManyPiecesException:
		return 400,{
			'error_code' : 'TooManyPiecesException',
			'error_message' : 'Too many pieces provided',
		}
	except NoPiecesException:
		return 400,{
			'error_code' : 'NoPiecesException',
			'error_message' : 'No pieces provided',
		}
	except PiecesTooLongForServiceException:
		return 400,{
			'error_code' : 'PiecesTooLongForServiceException',
			'error_message' : 'At least one piece is too long for equipment',
		}
	except InvalidTrailerDimensionsException:
		return 400,{
			'error_code' : 'InvalidTrailerDimensionsException',
			'error_message' : 'Invalid trailer dimensions provided',
		}
	except InvalidPiecesException:
		return 400,{
			'error_code' : 'InvalidPiecesException',
			'error_message' : 'One or more pieces have invalid dimensions',
		}
	except OptimizationFailedServiceException:
		return 500,{
			'error_code' : 'OptimizationFailedServiceException',
			'error_message' : 'Optimization failed',
		}
	except TrailerLoadingException:
		return 500,{
			'error_code' : 'TrailerLoadingException',
			'error_message' : 'Unknown error',
		}
	except Exception as e:
		return 500,{
			'error_code' : 'Exception',
			'error_message' : 'Unknown error',
		}
	