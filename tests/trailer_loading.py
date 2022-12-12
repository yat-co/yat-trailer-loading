import unittest

from ytl.generator import generate_random_trailer_load_plan
from ytl import (
    PiecesTooLongForServiceException, NoPiecesException,
)


class TrailerLinearFeetTest(unittest.TestCase):
	def setUp(self):
		self.some_val = '1'

	def tearDown(self):
		pass

	def test_packing(self):
		for _ in range(50):
			trailer, piece_list, allow_rotations = generate_random_trailer_load_plan()
			trailer_stats = trailer.get_summary()

			num_pieces_in_load_plan = len(trailer_stats.get('load_order'))
			num_pieces_passed = sum([p.get('num_pieces') for p in piece_list])

			piece_weight_in_load_plan = trailer_stats.get('total_weight')
			piece_weight_passed = sum(
				[p.get('weight') * p.get('num_pieces') for p in piece_list])

			# No pieces lost
			self.assertTrue(num_pieces_in_load_plan == num_pieces_passed,
			                'Pieces were lost in trailer load optimization')

			# All weight accounted for
			self.assertTrue(piece_weight_in_load_plan == piece_weight_passed,
			                'Weight is unaccounted for in the trailer load plan')

			# Check that disallowing rotations is functioning
			if not allow_rotations:
				any_piece_rotated = any([p.get('piece_is_rotated')
				                        for p in trailer_stats.get('load_order').values()])
				self.assertFalse(any_piece_rotated,
				                 'Rotated a piece when rotations are not allowed')

	def test_empty_packing(self):
		try:
			trailer, _, _ = generate_random_trailer_load_plan(
				num_piece_selection_options=[0],
			)
		except NoPiecesException:
			val = True
		except:
			val = False

		assert val, 'Failed to raise "NoPiecesException" exception for optimization with no pieces passed'

	def test_all_overweight_packing(self):
		for __ in range(15):
			trailer, piece_list, allow_rotations = generate_random_trailer_load_plan(
				weight_options=[4000],
			)
			trailer_stats = trailer.get_summary()

			num_pieces_in_load_plan = len(trailer_stats.get('load_order'))
			num_pieces_passed = sum([p.get('num_pieces') for p in piece_list])

			piece_weight_in_load_plan = trailer_stats.get('total_weight')
			piece_weight_passed = sum(
				[p.get('weight') * p.get('num_pieces') for p in piece_list])

			# No pieces lost
			self.assertTrue(num_pieces_in_load_plan == num_pieces_passed,
			                'Pieces were lost in trailer load optimization')

			# All weight accounted for
			self.assertTrue(piece_weight_in_load_plan == piece_weight_passed,
			                'Weight is unaccounted for in the trailer load plan')

			# Check that disallowing rotations is functioning
			if not allow_rotations:
				any_piece_rotated = any([p.get('piece_is_rotated')
				                        for p in trailer_stats.get('load_order').values()])
				self.assertFalse(any_piece_rotated,
				                 'Rotated a piece when rotations are not allowed')

	def test_pieces_too_long_packing(self):
		val = False
		try:
			trailer, piece_list, allow_rotations = generate_random_trailer_load_plan(
				length_options=[2000],
				num_piece_selection_options=[1],
			)
		except PiecesTooLongForServiceException:
			val = True
		except:
			val = False
		assert val, 'Failed to raise "PiecesTooLongForServiceException" exception for piece with length 2000 inches'


if __name__ == '__main__':
	unittest.main()
