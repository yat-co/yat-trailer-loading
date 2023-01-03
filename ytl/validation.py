from typing import List, Dict
import numpy as np

def validate_pieces(shipment_list : List[Dict]):
    '''
    Validate Provided List of Pieces is Valid

    Parameters
    ------------
    shipment_list : List[Dict]
        List of dictionaries describing piece dimensions
        Valid piece dictionaries require positive numeric values for keys `length`, `width`, `height`, and `weight`.

    Returns
    ------------
    None

    Raises
    ------------
    ValueError
        Raised when non-numeric, infinite, or NaN values are present for requried keys.
    '''
    for piece in shipment_list:
        for c in ['length', 'width', 'height', 'weight']:
            try:
                float(piece.get(c)) 
            except:
                raise ValueError(f'Invalid {c} for at least one pieces - Numeric values required')
            if float(piece.get(c))  <= 0:
                raise ValueError(f'Invalid {c} for at least one pieces - Positive values required')
            if piece.get(c) == np.inf:
                raise ValueError(f'Invalid {c} for at least one pieces - Infinity not allowed')
            if piece.get(c) is np.nan:
                raise ValueError(f'Invalid {c} for at least one pieces - NaN not allowed')


def validate_trailer_dims(trailer_dims : Dict):
    '''
    Validate Provided Trailer Dimensions are Valid

    Parameters
    ------------
    trailer_dims : Dict
        Dictionary of trailer dimension values
        Valid trailer dimensions require positive values for keys `inner_width`, inner_length`, `inner_height`, and `max_weight`

    Returns
    ------------
    None

    Raises
    ------------
    ValueError
        Raised when non-numeric, infinite, or NaN values are present for requried keys.
    '''
    for c in ['inner_width', 'inner_length', 'inner_height', 'max_weight']:
        try:
            float(trailer_dims.get(c))
        except:
            raise ValueError(f'Invalid {c} for trailer dimensions - Numeric values required')
        if float(trailer_dims.get(c)) <= 0:
            raise ValueError(f'Invalid {c} for trailer dimensions - Positive values required')
        if trailer_dims.get(c) == np.inf:
            raise ValueError(f'Invalid {c} for trailer dimensions - Infinity not allowed')
        if trailer_dims.get(c) is np.nan:
            raise ValueError(f'Invalid {c} for trailer dimensions - NaN not allowed')


def validate_piece_length(shipment_list : List[Dict], trailer_dims : Dict, allow_rotations : bool):
    '''
    Validate Provided Trailer Dimensions are Valid

    Parameters
    ------------
    shipment_list : List[Dict]
        List of dictionaries describing piece dimensions
        Checks that each provided piece individually fits on the trailer
    trailer_dims : Dict
        Dictionary of trailer dimension values

    Returns
    ------------
    None

    Raises
    ------------
    AssertionError
        Raised when piece and trailer dimension combination is invalid
    '''
    if allow_rotations:
        trailer_dim_ls = sorted([
            trailer_dims.get('inner_length'),
            trailer_dims.get('inner_width'),
        ]) + [trailer_dims.get('inner_height')]
    else:
        trailer_dim_ls = [
            trailer_dims.get('inner_length'),
            trailer_dims.get('inner_width'),
            trailer_dims.get('inner_height'),
        ]
    for piece in shipment_list:
        if allow_rotations:
            dims = sorted([
                piece.get('length'),
                piece.get('width'),
            ]) + [piece.get('height')]
        else:
            dims = [
                piece.get('length'),
                piece.get('width'),
                piece.get('height'),
            ]
        assert(all([x <= y for x, y in zip(dims, trailer_dim_ls)]))
