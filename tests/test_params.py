
PIECE_ARRANGEMENT_ALGORITHM_TEST_OPTIONS = [None,'NAIVE','GREEDY_STACK']
SHIPMENT_ARRANGEMENT_ALGORITHM_TEST_OPTIONS = [
	None,
	[
		{
			'algorithm' : 'NAIVE',
			'max_iter' : None,
			'timeout' : None,
		},
	],
	[
		{
			'algorithm' : 'NAIVE',
			'max_iter' : 3,
			'timeout' : 5,
		},
	],
	[
		{
			'algorithm' : 'NO_STACK_BIN_PACK',
			'max_iter' : None,
			'timeout' : None,
		},
	],
	[
		{
			'algorithm' : 'NO_STACK_BIN_PACK',
			'max_iter' : 3,
			'timeout' : 5,
		},
	],
	[
		{
			'algorithm' : 'GREEDY_LOAD',
			'max_iter' : None,
			'timeout' : None,
		},
	],
	[
		{
			'algorithm' : 'GREEDY_LOAD',
			'max_iter' : 3,
			'timeout' : 5,
		},
	],
	[
		{
			'algorithm' : 'NO_STACK_BIN_PACK',
			'max_iter' : None,
			'timeout' : None,
		},
		{
			'algorithm' : 'SLIDE_BACK',
			'max_iter' : None,
			'timeout' : None,
		},
		{
			'algorithm' : 'GREEDY_LOAD',
			'max_iter' : None,
			'timeout' : None,
		},
	],
	[
		{
			'algorithm' : 'NO_STACK_BIN_PACK',
			'max_iter' : 3,
			'timeout' : 5,
		},
		{
			'algorithm' : 'SLIDE_BACK',
			'max_iter' : 3,
			'timeout' : 5,
		},
		{
			'algorithm' : 'GREEDY_LOAD',
			'max_iter' : 3,
			'timeout' : 5,
		},
	],
]
