import numpy as np
from jax.scipy.linalg import expm
import jax.numpy as jnp
from scipy.sparse import csr_matrix, csc_matrix

def commutator(A, B):
    """
    Compute the commutator [A, B] = AB - BA.

    Parameters:
    -----------
    A : array-like or SparsePauliOp
        First operator
    B : array-like or SparsePauliOp
        Second operator

    Returns:
    --------
    array-like or SparsePauliOp
        Commutator [A, B]
    """
    return A @ B - B @ A

def anticommutator(A, B):
    """
    Compute the anticommutator {A, B} = AB + BA.

    Parameters:
    -----------
    A : array-like or SparsePauliOp
        First operator
    B : array-like or SparsePauliOp
        Second operator

    Returns:
    --------
    array-like or SparsePauliOp
        Anticommutator {A, B}
    """
    return A @ B + B @ A

def norm(A, ord='spectral'):
    """
    Compute various norms of an operator.

    Parameters:
    -----------
    A : array-like
        Operator to compute norm of
    ord : str, optional
        Norm type:
        - 'spectral': Operator/spectral norm (2-norm), default
        - 'fro': Frobenius norm
        - '4': Fourth-order norm
        - Other values passed to np.linalg.norm

    Returns:
    --------
    float
        Norm value
    """
    if ord == 'fro':
        return np.linalg.norm(A)
    elif ord == 'spectral':
        return np.linalg.norm(A, ord=2)
    elif ord == '4':
        return np.trace(A @ A.conj().T @ A @ A.conj().T)**(1/4)
    else:
        return np.linalg.norm(A, ord=ord)
