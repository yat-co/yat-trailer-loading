

class TooManyPiecesException(Exception):
    pass


class NoPiecesException(Exception):
    pass


class PiecesTooLongForServiceException(Exception):
    pass


class OptimizationFailedServiceException(Exception):
    pass


class TrailerLoadingException(Exception):
    pass


class InvalidTrailerDimensionsException(Exception):
    pass


class InvalidPiecesException(Exception):
    pass


class InvalidOptimizationResultException(Exception):
    pass
