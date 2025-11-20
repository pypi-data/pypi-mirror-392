import numpy as np
import pytest
from quantumhall_matrixelements import get_exchange_kernels_GaussLegendre, get_exchange_kernels

def test_legendre_basic_shape():
    nmax = 2
    Gs_dimless = np.array([0.0, 1.0])
    thetas = np.array([0.0, np.pi])
    X = get_exchange_kernels_GaussLegendre(Gs_dimless, thetas, nmax, nquad=100)
    assert X.shape == (2, nmax, nmax, nmax, nmax)
    assert np.isfinite(X).all()

def test_legendre_vs_hankel_small_n():
    """Verify agreement with Hankel for small n."""
    nmax = 2
    Gs_dimless = np.array([0.5, 1.5])
    thetas = np.array([0.0, 0.2])
    
    X_leg = get_exchange_kernels(Gs_dimless, thetas, nmax, method="gausslegendre", nquad=500)
    X_hk = get_exchange_kernels(Gs_dimless, thetas, nmax, method="hankel")
    
    assert np.allclose(X_leg, X_hk, rtol=1e-3, atol=1e-3)

def test_legendre_large_n_stability():
    """Verify that it runs without error for large n (where gausslag fails)."""
    nmax = 15
    Gs_dimless = np.array([1.0])
    thetas = np.array([0.0])
    
    # This should not raise an error
    X = get_exchange_kernels_GaussLegendre(Gs_dimless, thetas, nmax, nquad=500)
    assert np.isfinite(X).all()
