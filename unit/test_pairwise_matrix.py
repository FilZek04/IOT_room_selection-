"""
Unit tests for pairwise_matrix module.
"""

import pytest
import numpy as np
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.app.ahp.pairwise_matrix import (
    PairwiseMatrix,
    SAATY_SCALE,
    create_default_criteria_matrix,
    create_comfort_subcriteria_matrix,
    create_health_subcriteria_matrix,
    create_usability_subcriteria_matrix,
)


class TestPairwiseMatrix:
    """Tests for PairwiseMatrix class."""
    
    def test_initialization(self):
        """Test matrix initialization with criteria list."""
        criteria = ["A", "B", "C"]
        pm = PairwiseMatrix(criteria)
        
        assert pm.n == 3
        assert pm.criteria == ["A", "B", "C"]
        
        # Initial matrix should be identity (all 1s)
        matrix = pm.get_matrix()
        assert matrix.shape == (3, 3)
        assert np.allclose(matrix, np.ones((3, 3)))
    
    def test_minimum_criteria_requirement(self):
        """Test that at least 2 criteria are required."""
        with pytest.raises(ValueError):
            PairwiseMatrix(["A"])
        
        with pytest.raises(ValueError):
            PairwiseMatrix([])
    
    def test_set_comparison(self):
        """Test setting pairwise comparisons."""
        pm = PairwiseMatrix(["A", "B", "C"])
        
        pm.set_comparison("A", "B", 3)  # A is 3x more important than B
        
        matrix = pm.get_matrix()
        assert matrix[0, 1] == 3.0
        assert np.isclose(matrix[1, 0], 1/3)  # Reciprocal
    
    def test_reciprocity(self):
        """Test that reciprocity is maintained."""
        pm = PairwiseMatrix(["A", "B", "C", "D"])
        
        pm.set_comparison("A", "B", 5)
        pm.set_comparison("A", "C", 7)
        pm.set_comparison("B", "C", 3)
        pm.set_comparison("C", "D", 2)
        
        matrix = pm.get_matrix()
        
        # Check all reciprocals
        for i in range(pm.n):
            for j in range(pm.n):
                if i != j:
                    assert np.isclose(matrix[i, j] * matrix[j, i], 1.0)
    
    def test_diagonal_is_ones(self):
        """Test that diagonal remains 1."""
        pm = PairwiseMatrix(["A", "B", "C"])
        pm.set_comparison("A", "B", 5)
        pm.set_comparison("B", "C", 3)
        
        matrix = pm.get_matrix()
        assert np.allclose(np.diag(matrix), [1.0, 1.0, 1.0])
    
    def test_saaty_scale_limits(self):
        """Test that values outside Saaty scale are rejected."""
        pm = PairwiseMatrix(["A", "B"])
        
        # Valid range: 1/9 to 9
        pm.set_comparison("A", "B", 9)  # Max valid
        pm.set_comparison("A", "B", 1/9)  # Min valid
        
        with pytest.raises(ValueError):
            pm.set_comparison("A", "B", 10)  # Too high
        
        with pytest.raises(ValueError):
            pm.set_comparison("A", "B", 1/10)  # Too low
    
    def test_invalid_criterion_name(self):
        """Test error handling for invalid criterion names."""
        pm = PairwiseMatrix(["A", "B"])
        
        with pytest.raises(ValueError):
            pm.set_comparison("A", "X", 3)  # X doesn't exist
    
    def test_from_flat_upper_triangle(self):
        """Test populating matrix from flat list."""
        pm = PairwiseMatrix(["A", "B", "C"])
        
        # Upper triangle values: A-B, A-C, B-C
        pm.from_flat_upper_triangle([3, 5, 2])
        
        matrix = pm.get_matrix()
        assert matrix[0, 1] == 3
        assert matrix[0, 2] == 5
        assert matrix[1, 2] == 2
        assert np.isclose(matrix[1, 0], 1/3)
    
    def test_from_flat_wrong_length(self):
        """Test error for wrong number of values."""
        pm = PairwiseMatrix(["A", "B", "C"])
        
        with pytest.raises(ValueError):
            pm.from_flat_upper_triangle([3, 5])  # Needs 3 values
    
    def test_is_valid(self):
        """Test validation of matrix properties."""
        pm = PairwiseMatrix(["A", "B", "C"])
        pm.set_comparison("A", "B", 3)
        pm.set_comparison("A", "C", 5)
        pm.set_comparison("B", "C", 2)
        
        is_valid, error = pm.is_valid()
        assert is_valid
        assert error is None
    
    def test_get_comparison(self):
        """Test retrieving comparison values."""
        pm = PairwiseMatrix(["X", "Y"])
        pm.set_comparison("X", "Y", 7)
        
        assert pm.get_comparison("X", "Y") == 7
        assert np.isclose(pm.get_comparison("Y", "X"), 1/7)


class TestDefaultMatrices:
    """Tests for pre-built default matrices."""
    
    def test_default_criteria_matrix(self):
        """Test the default main criteria matrix."""
        pm = create_default_criteria_matrix()
        
        assert pm.criteria == ["Comfort", "Health", "Usability"]
        is_valid, _ = pm.is_valid()
        assert is_valid
    
    def test_comfort_subcriteria_matrix(self):
        """Test default comfort sub-criteria matrix."""
        pm = create_comfort_subcriteria_matrix()
        
        assert "Temperature" in pm.criteria
        assert "Lighting" in pm.criteria
        is_valid, _ = pm.is_valid()
        assert is_valid
    
    def test_health_subcriteria_matrix(self):
        """Test default health sub-criteria matrix."""
        pm = create_health_subcriteria_matrix()
        
        assert "CO2" in pm.criteria
        is_valid, _ = pm.is_valid()
        assert is_valid
    
    def test_usability_subcriteria_matrix(self):
        """Test default usability sub-criteria matrix."""
        pm = create_usability_subcriteria_matrix()
        
        assert "SeatingCapacity" in pm.criteria
        is_valid, _ = pm.is_valid()
        assert is_valid


class TestSaatyScale:
    """Tests for Saaty scale constants."""
    
    def test_saaty_scale_values(self):
        """Test that Saaty scale has expected values."""
        assert 1 in SAATY_SCALE
        assert 9 in SAATY_SCALE
        assert len(SAATY_SCALE) == 9
    
    def test_saaty_scale_descriptions(self):
        """Test Saaty scale descriptions are meaningful."""
        assert "Equal" in SAATY_SCALE[1]
        assert "Absolute" in SAATY_SCALE[9]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
