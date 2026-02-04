"""
Unit tests for eigenvector module.
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.app.ahp.eigenvector import (
    calculate_priority_weights,
    calculate_lambda_max,
    calculate_consistency_index,
    calculate_consistency_ratio,
    validate_matrix_consistency,
    RANDOM_INDEX,
)


class TestPriorityWeights:
    """Tests for priority weight calculation."""
    
    def test_identity_matrix_equal_weights(self):
        """Test that identity matrix gives equal weights."""
        matrix = np.ones((3, 3))
        
        weights = calculate_priority_weights(matrix)
        
        expected = np.array([1/3, 1/3, 1/3])
        assert np.allclose(weights, expected, atol=0.01)
    
    def test_weights_sum_to_one(self):
        """Test that weights always sum to 1."""
        # Create a valid pairwise matrix
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 3],
            [1/5, 1/3, 1]
        ])
        
        weights = calculate_priority_weights(matrix)
        
        assert np.isclose(np.sum(weights), 1.0)
    
    def test_weights_are_positive(self):
        """Test that all weights are positive."""
        matrix = np.array([
            [1, 5, 7],
            [1/5, 1, 3],
            [1/7, 1/3, 1]
        ])
        
        weights = calculate_priority_weights(matrix)
        
        assert np.all(weights > 0)
    
    def test_dominant_criterion_gets_highest_weight(self):
        """Test that more important criteria get higher weights."""
        # A is much more important than B and C
        matrix = np.array([
            [1, 9, 9],
            [1/9, 1, 1],
            [1/9, 1, 1]
        ])
        
        weights = calculate_priority_weights(matrix)
        
        # A should have the highest weight
        assert weights[0] > weights[1]
        assert weights[0] > weights[2]
    
    def test_eigenvector_method(self):
        """Test eigenvector method specifically."""
        matrix = np.array([
            [1, 2, 4],
            [1/2, 1, 2],
            [1/4, 1/2, 1]
        ])
        
        weights = calculate_priority_weights(matrix, method="eigenvector")
        
        # This is a perfectly consistent matrix, weights should be exact
        assert np.isclose(np.sum(weights), 1.0)
    
    def test_geometric_mean_method(self):
        """Test geometric mean method."""
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 3],
            [1/5, 1/3, 1]
        ])
        
        weights = calculate_priority_weights(matrix, method="geometric_mean")
        
        assert np.isclose(np.sum(weights), 1.0)
        assert np.all(weights > 0)
    
    def test_normalized_sum_method(self):
        """Test normalized sum method."""
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 3],
            [1/5, 1/3, 1]
        ])
        
        weights = calculate_priority_weights(matrix, method="normalized_sum")
        
        assert np.isclose(np.sum(weights), 1.0)
    
    def test_invalid_method(self):
        """Test error for invalid method."""
        matrix = np.ones((3, 3))
        
        with pytest.raises(ValueError):
            calculate_priority_weights(matrix, method="invalid")
    
    def test_non_square_matrix_error(self):
        """Test error for non-square matrix."""
        matrix = np.ones((3, 4))
        
        with pytest.raises(ValueError):
            calculate_priority_weights(matrix)


class TestLambdaMax:
    """Tests for maximum eigenvalue calculation."""
    
    def test_consistent_matrix_lambda_equals_n(self):
        """Test that λmax = n for perfectly consistent matrix."""
        # Perfectly consistent 3x3 matrix
        matrix = np.array([
            [1, 2, 4],
            [1/2, 1, 2],
            [1/4, 1/2, 1]
        ])
        
        weights = calculate_priority_weights(matrix)
        lambda_max = calculate_lambda_max(matrix, weights)
        
        # For consistent matrix, λmax should be very close to n
        assert np.isclose(lambda_max, 3.0, atol=0.1)
    
    def test_lambda_max_at_least_n(self):
        """Test that λmax >= n for any valid matrix."""
        # Slightly inconsistent matrix
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 3],
            [1/5, 1/3, 1]
        ])
        
        weights = calculate_priority_weights(matrix)
        lambda_max = calculate_lambda_max(matrix, weights)
        
        assert lambda_max >= 3.0


class TestConsistencyIndex:
    """Tests for Consistency Index calculation."""
    
    def test_ci_zero_for_consistent_matrix(self):
        """Test that CI ≈ 0 for consistent matrix."""
        matrix = np.array([
            [1, 2, 4],
            [1/2, 1, 2],
            [1/4, 1/2, 1]
        ])
        
        ci = calculate_consistency_index(matrix)
        
        assert ci < 0.05  # Should be very small
    
    def test_ci_positive_for_inconsistent(self):
        """Test that CI > 0 for inconsistent matrix."""
        # Deliberately inconsistent
        matrix = np.array([
            [1, 3, 1],
            [1/3, 1, 5],
            [1, 1/5, 1]
        ])
        
        ci = calculate_consistency_index(matrix)
        
        assert ci > 0


class TestConsistencyRatio:
    """Tests for Consistency Ratio calculation."""
    
    def test_cr_acceptable_for_consistent_matrix(self):
        """Test CR < 0.1 for reasonably consistent matrix."""
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 3],
            [1/5, 1/3, 1]
        ])
        
        cr, is_acceptable = calculate_consistency_ratio(matrix)
        
        assert is_acceptable
        assert cr < 0.1
    
    def test_cr_unacceptable_for_inconsistent_matrix(self):
        """Test CR >= 0.1 for highly inconsistent matrix."""
        # Highly inconsistent matrix
        matrix = np.array([
            [1, 9, 1/9],
            [1/9, 1, 9],
            [9, 1/9, 1]
        ])
        
        cr, is_acceptable = calculate_consistency_ratio(matrix)
        
        assert not is_acceptable
        assert cr > 0.1
    
    def test_cr_zero_for_2x2_matrix(self):
        """Test that 2x2 matrices are always consistent."""
        matrix = np.array([
            [1, 5],
            [1/5, 1]
        ])
        
        cr, is_acceptable = calculate_consistency_ratio(matrix)
        
        assert cr == 0.0
        assert is_acceptable
    
    def test_cr_matrix_too_large(self):
        """Test error for matrix larger than RI table."""
        matrix = np.ones((16, 16))
        
        with pytest.raises(ValueError):
            calculate_consistency_ratio(matrix)


class TestRandomIndex:
    """Tests for Random Index lookup table."""
    
    def test_ri_values_exist(self):
        """Test that RI values exist for sizes 1-15."""
        for n in range(1, 16):
            assert n in RANDOM_INDEX
    
    def test_ri_zero_for_small_matrices(self):
        """Test that RI = 0 for n = 1, 2."""
        assert RANDOM_INDEX[1] == 0.0
        assert RANDOM_INDEX[2] == 0.0
    
    def test_ri_increases_with_size(self):
        """Test that RI generally increases with matrix size."""
        for n in range(3, 15):
            assert RANDOM_INDEX[n] <= RANDOM_INDEX[n + 1]


class TestValidateMatrixConsistency:
    """Tests for full validation function."""
    
    def test_returns_details_dict(self):
        """Test that validation returns expected details."""
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 3],
            [1/5, 1/3, 1]
        ])
        
        is_consistent, details = validate_matrix_consistency(matrix)
        
        assert "weights" in details
        assert "lambda_max" in details
        assert "ci" in details
        assert "cr" in details
        assert "is_consistent" in details
        assert "n" in details
    
    def test_weights_returned_correctly(self):
        """Test that weights are returned in details."""
        matrix = np.ones((3, 3))
        
        _, details = validate_matrix_consistency(matrix)
        
        assert len(details["weights"]) == 3
        assert np.isclose(np.sum(details["weights"]), 1.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
