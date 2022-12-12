
def check_pieces_valid(piece_list):
    for piece in piece_list:
        for c in ['length', 'width', 'height', 'weight']:
            try:
                float(piece.get(c))
            except:
                raise ValueError(f'Invalid {c} for at least one pieces')


def check_trailer_dims_valid(trailer_dims):
    for c in ['inner_width', 'inner_length', 'inner_height', 'max_weight']:
        try:
            float(trailer_dims.get(c))
        except:
            raise ValueError(f'Invalid {c} for at least one pieces')


def check_piece_length(piece_list, trailer_dims, allow_rotations):
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
    for piece in piece_list:
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
