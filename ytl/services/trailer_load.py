
from ..bin_packing import Piece, Shipment, Trailer
from ..optimizer_functions import greedy_stack_pieces
from ..utils import store_load_plan, restore_load_plan
from ..exceptions import (
    PiecesTooLongForServiceException,
    NoPiecesException,
    OptimizationFailedServiceException,
    InvalidPiecesException,
    InvalidTrailerDimensionsException,
)
from ..validation import (
    check_piece_length, check_pieces_valid, check_trailer_dims_valid
)

OVERWEIGHT_SHIPMENT_THRESHOLD = 2000
DEFAULT_GREEDY_LOAD_MAX_ITER = 3
DEFAULT_SLIDE_BACK_MAX_ITER = 2
DEFAULT_SLIDE_BACK_TIMEOUT = 2


def optimize_trailer_load_plan(piece_list, trailer_dims, allow_rotations=True, **kwargs):
    try:
        check_trailer_dims_valid(trailer_dims=trailer_dims)
    except Exception as e:
        raise InvalidTrailerDimensionsException(
            'Invalid trailer dimensions passed') from e
    if len(piece_list) == 0:
        raise NoPiecesException(
            'No pieces provided for trailer load optimization')
    try:
        check_pieces_valid(piece_list=piece_list)
    except Exception as e:
        raise InvalidPiecesException from e
    try:
        check_piece_length(
            piece_list=piece_list,
            trailer_dims=trailer_dims,
            allow_rotations=allow_rotations,
        )
    except Exception as e:
        raise PiecesTooLongForServiceException(
            'At least one of the pieces provided is too large to fit on the trailer') from e
    pieces = []
    for i, piece_dict in enumerate(piece_list):
        num_items = piece_dict.pop('num_pieces', 1)
        for j in range(num_items):
            piece_dict.update({'name': f'Line Item {i+1}:  Piece {j+1}'})
            pieces += [Piece(**piece_dict)]

    overweight_pieces = [
        piece for piece in pieces if piece.weight > OVERWEIGHT_SHIPMENT_THRESHOLD]
    pieces = [piece for piece in pieces if not piece in overweight_pieces]

    if allow_rotations:
        for piece in overweight_pieces:
            if piece.length < piece.width:
                piece.rotate()

    if len(pieces) > 0:
        try:
            shipments = greedy_stack_pieces(
                pieces=pieces,
                trailer_height=trailer_dims.get('inner_height'),
                allow_rotations=allow_rotations
            )
        except Exception as e:
            raise OptimizationFailedServiceException(
                'Optimization failed during optimization of piece stacking') from e
    else:
        shipments = []

    trailer = Trailer(
        shipments=shipments,
        width=trailer_dims.get('inner_width'),
        length=trailer_dims.get('inner_length'),
        height=trailer_dims.get('inner_height'),
        dimension_unit_of_measure='IN',
        weight=0,
        weight_unit_of_measure='LBS',
        max_weight=trailer_dims.get('max_weight'),
    )
    if len(pieces) > 0:
        try:
            trailer.arrange_shipments(
                algorithm='NO_STACK_BIN_PACK',
                allow_rotations=allow_rotations
            )
            slide_back_max_iter = kwargs.get(
                'slide_back_max_iter', DEFAULT_SLIDE_BACK_MAX_ITER)
            slide_back_timeout = kwargs.get(
                'slide_back_timeout', DEFAULT_SLIDE_BACK_TIMEOUT)
            trailer.arrange_shipments(
                algorithm='SLIDE_BACK',
                max_iter=slide_back_max_iter,
                timeout=slide_back_timeout
            )
            linear_feet_1 = trailer.get_linear_feet()
            plan_backup = store_load_plan(trailer)

            greedy_load_max_iter = kwargs.get(
                'greedy_load_max_iter', DEFAULT_GREEDY_LOAD_MAX_ITER)
            trailer.arrange_shipments(
                algorithm='GREEDY_LOAD',
                max_iter=greedy_load_max_iter,
                allow_rotations=allow_rotations
            )
            linear_feet_2 = trailer.get_linear_feet()

            if linear_feet_1 < linear_feet_2:
                restore_load_plan(plan_backup)

            if not trailer.arrangement_is_valid():
                if max([s.position[0] for s in trailer.shipments]) < trailer.length:
                    trailer.arrange_shipments(
                        algorithm='GREEDY_LOAD',
                        max_iter=5,
                        allow_rotations=allow_rotations
                    )

            trailer._set_weight()
        except Exception as e:
            raise OptimizationFailedServiceException(
                'Optimization failed during standard weight piece load optimization') from e

    overweight_shipments = [Shipment(pieces=piece)
                            for piece in overweight_pieces]

    boundaries = trailer.get_boundaries()
    try:
        linear_inches = boundaries[0, 1]
        for shipment in overweight_shipments:
            shipment._set_dims()
            shipment.position[0] = linear_inches
            shipment.position[1] = trailer.width / 2 - shipment.width / 2
            trailer.add_shipment(shipment)
            linear_inches += shipment.length
            shipment._set_dims()
            trailer._set_weight()
    except Exception as e:
        raise OptimizationFailedServiceException(
            'Optimization failed during overwieght piece load optimization') from e

    return trailer
