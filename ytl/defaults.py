
OVERWEIGHT_SHIPMENT_THRESHOLD = 2000
DEFAULT_PIECE_ARRANGEMENT_ALGORITHM = 'GREEDY_STACK'
DEFAULT_SHIPMENT_ARRANGEMENT_ALGORITHM = [
    {
        'algorithm' : 'NO_STACK_BIN_PACK',
        'max_iter' : None,
        'timeout' : None,
    },
    {
        'algorithm' : 'SLIDE_BACK',
        'max_iter' : 2,
        'timeout' : 2,
    },
    {
        'algorithm' : 'GREEDY_LOAD',
        'max_iter' : 3,
        'timeout' : None,
    },
]
