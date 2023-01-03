
import unittest
from ytl.generator import generate_random_trailer_load_plan_wrapper
from ytl.standard_logistic_dims import STANDARD_TRAILER_DIMS
from . import test_params

class TrailerLinearFeetTest(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_random_packing(self):
		for _ in range(25):
			for allow_rotations in [True,False]:
				status_code, response_data, piece_list, allow_rotations = generate_random_trailer_load_plan_wrapper(allow_rotations=[allow_rotations])
				
				self.assertTrue(
					status_code == 200, 
					f'Invalid status code {status_code} returned, expected 200'
				)

				self.assertTrue(
					response_data.get('linear_feet') > 0, 
					'Linear feet value is not a positive value'
				)

				num_pieces_in_load_plan = len(response_data.get('load_order'))
				num_pieces_passed = sum([p.get('num_pieces') for p in piece_list])

				piece_weight_in_load_plan = response_data.get('total_weight')
				piece_weight_passed = sum(
					[p.get('weight') * p.get('num_pieces') for p in piece_list]
				)

				# No pieces lost
				self.assertTrue(
					num_pieces_in_load_plan == num_pieces_passed,
					'Pieces were lost in trailer load optimization'
				)

				# All weight accounted for
				self.assertTrue(
					piece_weight_in_load_plan == piece_weight_passed,
					'Weight is unaccounted for in the trailer load plan'
				)

				# Check that disallowing rotations is functioning
				if not allow_rotations:
					any_piece_rotated = any(
						[p.get('piece_is_rotated')for p in response_data.get('load_order').values()]
					)
					self.assertFalse(
						any_piece_rotated,
						'Rotated a piece when rotations are not allowed'
					)

	def test_empty_packing(self):
		status_code, response_data, piece_list, allow_rotations = generate_random_trailer_load_plan_wrapper(
			num_piece_selection_options=[0]
		)
		assert status_code == 400, 'Failed to return 400 status for optimization with no pieces passed'
		assert response_data['error_code'] == 'NoPiecesException', 'Failed to notify "NoPiecesException" exception for optimization with no pieces passed'

	def test_all_overweight_packing(self):
		status_code, response_data, piece_list, allow_rotations = generate_random_trailer_load_plan_wrapper(
			weight_options=[4000],
			num_piece_selection_options=[2],
		)
		
		self.assertTrue(
			status_code,
			f'Invalid status code {status_code} returned, expected 200'
		)
		
		num_pieces_in_load_plan = len(response_data.get('load_order'))
		num_pieces_passed = sum([p.get('num_pieces') for p in piece_list])
		
		piece_weight_in_load_plan = response_data.get('total_weight')
		piece_weight_passed = sum([p.get('weight') * p.get('num_pieces') for p in piece_list])

		# No pieces lost
		self.assertTrue(
			num_pieces_in_load_plan == num_pieces_passed,
			'Pieces were lost in trailer load optimization'
		)

		# All weight accounted for
		self.assertTrue(
			piece_weight_in_load_plan == piece_weight_passed,
			'Weight is unaccounted for in the trailer load plan'
		)

		# Check that disallowing rotations is functioning
		if not allow_rotations:
			any_piece_rotated = any(
				[p.get('piece_is_rotated') for p in response_data.get('load_order').values()]
			)
			self.assertFalse(
				any_piece_rotated,
				'Rotated a piece when rotations are not allowed'
			)

	def test_all_overweight_packing_w_overweight_threshold_override(self):
		status_code, response_data, piece_list, allow_rotations = generate_random_trailer_load_plan_wrapper(
			weight_options=[1800],
			num_piece_selection_options=[2],
			overweight_shipment_threshold=1500,
		)
		
		self.assertTrue(
			status_code,
			f'Invalid status code {status_code} returned, expected 200'
		)
		
		num_pieces_in_load_plan = len(response_data.get('load_order'))
		num_pieces_passed = sum([p.get('num_pieces') for p in piece_list])
		
		piece_weight_in_load_plan = response_data.get('total_weight')
		piece_weight_passed = sum([p.get('weight') * p.get('num_pieces') for p in piece_list])

		# No pieces lost
		self.assertTrue(
			num_pieces_in_load_plan == num_pieces_passed,
			'Pieces were lost in trailer load optimization'
		)

		# All weight accounted for
		self.assertTrue(
			piece_weight_in_load_plan == piece_weight_passed,
			'Weight is unaccounted for in the trailer load plan'
		)

		# Check that disallowing rotations is functioning
		if not allow_rotations:
			any_piece_rotated = any(
				[p.get('piece_is_rotated') for p in response_data.get('load_order').values()]
			)
			self.assertFalse(
				any_piece_rotated,
				'Rotated a piece when rotations are not allowed'
			)

	def test_pieces_too_long_packing(self):
		status_code, response_data, piece_list, allow_rotations = generate_random_trailer_load_plan_wrapper(
			length_options=[2000],
			num_piece_selection_options=[1],
		)
		assert status_code == 400, 'Failed to return 400 status for optimization with pieces that are too long'
		assert response_data['error_code'] == 'PiecesTooLongForServiceException', 'Failed to notify "PiecesTooLongForServiceException" exception for optimization with pieces that are too long'

	def test_all_default_equipment_types(self):
		for i,trailer_dims in enumerate(STANDARD_TRAILER_DIMS):
			for allow_rotations in [True,False]:
				for piece_arrangement_algorithm in test_params.PIECE_ARRANGEMENT_ALGORITHM_TEST_OPTIONS:
					for shipment_optimization_ls in test_params.SHIPMENT_ARRANGEMENT_ALGORITHM_TEST_OPTIONS:
						status_code, response_data, piece_list, allow_rotations = generate_random_trailer_load_plan_wrapper(
							trailer_idx_options=[i],
							num_piece_selection_options=[4],
							length_options = [max(1,int(.05 * trailer_dims.get('inner_width')))],
							width_options = [max(1,int(.05 * trailer_dims.get('inner_length')))],
							height_options = [max(1,int(.05 * trailer_dims.get('inner_height')))],
							weight_options = [max(1,int(.05 * trailer_dims.get('max_weight')))],
							allow_rotations_options=[allow_rotations],
							piece_arrangement_algorithm=piece_arrangement_algorithm,
							shipment_optimization_ls=shipment_optimization_ls,
						)
						self.assertTrue(
							status_code == 200,
							f'Invalid status code {status_code} returned, expected 200'
						)
						
						self.assertTrue(
							response_data.get('linear_feet') > 0, 
							'Linear feet value is not a positive value'
						)

						num_pieces_in_load_plan = len(response_data.get('load_order'))
						num_pieces_passed = sum([p.get('num_pieces') for p in piece_list])

						piece_weight_in_load_plan = response_data.get('total_weight')
						piece_weight_passed = sum([p.get('weight') * p.get('num_pieces') for p in piece_list])

						# No pieces lost
						self.assertTrue(
							num_pieces_in_load_plan == num_pieces_passed,
							'Pieces were lost in trailer load optimization'
						)

						# All weight accounted for
						self.assertTrue(
							piece_weight_in_load_plan == piece_weight_passed,
							'Weight is unaccounted for in the trailer load plan'
						)

						# Check that disallowing rotations is functioning
						if not allow_rotations:
							any_piece_rotated = any(
								[p.get('piece_is_rotated')for p in response_data.get('load_order').values()]
							)
							self.assertFalse(
								any_piece_rotated,
								'Rotated a piece when rotations are not allowed'
							)


if __name__ == '__main__':
	unittest.main()
