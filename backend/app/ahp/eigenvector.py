"""Eigenvector calculation and consistency ratio for AHP."""

import numpy as np
from typing import Tuple, Optional

RANDOM_INDEX = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
    11: 1.51, 12: 1.53, 13: 1.56, 14: 1.57, 15: 1.59,
}


def calculate_priority_weights(matrix: np.ndarray, method: str = "eigenvector") -> np.ndarray:
    """Calculate priority weights from pairwise comparison matrix."""
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Matrix must be square")
    
    n = matrix.shape[0]
    
    if method == "eigenvector":
        return _eigenvector_method(matrix)
    elif method == "geometric_mean":
        return _geometric_mean_method(matrix)
    elif method == "normalized_sum":
        return _normalized_sum_method(matrix)
    else:
        raise ValueError(f"Unknown method: {method}")


def _eigenvector_method(matrix: np.ndarray) -> np.ndarray:
    """Calculate weights using principal eigenvector."""
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    
    real_eigenvalues = np.real(eigenvalues)
    principal_index = np.argmax(real_eigenvalues)
    
    principal_eigenvector = np.real(eigenvectors[:, principal_index])
    weights = principal_eigenvector / np.sum(principal_eigenvector)
    
    if np.any(weights < 0):
        weights = -weights
    
    return weights


def _geometric_mean_method(matrix: np.ndarray) -> np.ndarray:
    """Calculate weights using row geometric means."""
    n = matrix.shape[0]
    geometric_means = np.power(np.prod(matrix, axis=1), 1.0 / n)
    weights = geometric_means / np.sum(geometric_means)
    return weights


def _normalized_sum_method(matrix: np.ndarray) -> np.ndarray:
    """Calculate weights by normalizing column sums."""
    col_sums = np.sum(matrix, axis=0)
    normalized = matrix / col_sums
    weights = np.mean(normalized, axis=1)
    return weights


def calculate_lambda_max(matrix: np.ndarray, weights: np.ndarray) -> float:
    """Calculate maximum eigenvalue from matrix and weights."""
    n = matrix.shape[0]
    aw = matrix @ weights
    
    with np.errstate(divide='ignore', invalid='ignore'):
        ratios = np.where(weights > 1e-10, aw / weights, n)
    
    return float(np.mean(ratios))


def calculate_consistency_index(matrix: np.ndarray, weights: Optional[np.ndarray] = None) -> float:
    """Calculate Consistency Index (CI)."""
    n = matrix.shape[0]
    
    if n == 1:
        return 0.0
    
    if weights is None:
        weights = calculate_priority_weights(matrix)
    
    lambda_max = calculate_lambda_max(matrix, weights)
    ci = (lambda_max - n) / (n - 1)
    
    return ci


def calculate_consistency_ratio(matrix: np.ndarray, weights: Optional[np.ndarray] = None) -> Tuple[float, bool]:
    """Calculate Consistency Ratio (CR). Returns (CR, is_acceptable). CR < 0.1 is acceptable."""
    n = matrix.shape[0]
    
    if n > 15:
        raise ValueError(f"Matrix size {n} exceeds maximum supported size of 15")
    
    if n <= 2:
        return 0.0, True
    
    ci = calculate_consistency_index(matrix, weights)
    ri = RANDOM_INDEX[n]
    
    if ri == 0:
        return 0.0, True
    
    cr = ci / ri
    is_acceptable = cr < 0.1
    
    return cr, is_acceptable


def validate_matrix_consistency(matrix: np.ndarray, threshold: float = 0.1) -> Tuple[bool, dict]:
    """Validate pairwise comparison matrix consistency."""
    n = matrix.shape[0]
    
    weights = calculate_priority_weights(matrix)
    lambda_max = calculate_lambda_max(matrix, weights)
    ci = calculate_consistency_index(matrix, weights)
    cr, is_consistent = calculate_consistency_ratio(matrix, weights)
    
    details = {
        "weights": weights,
        "lambda_max": lambda_max,
        "ci": ci,
        "cr": cr,
        "is_consistent": is_consistent and cr < threshold,
        "n": n,
        "ri": RANDOM_INDEX.get(n, None),
    }
    
    return details["is_consistent"], details


def format_weights(weights: np.ndarray, criteria_names: list) -> str:
    """Format weights as readable string with percentages."""
    lines = []
    for name, weight in zip(criteria_names, weights):
        lines.append(f"  {name}: {weight:.4f} ({weight*100:.1f}%)")
    return "\n".join(lines)
