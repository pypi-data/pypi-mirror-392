import numpy as np
import pytest
from quantumhall_matrixelements import get_exchange_kernels, get_exchange_kernels_GaussLag
from quantumhall_matrixelements.diagnostic import verify_exchange_kernel_symmetries

def test_cross_backend_consistency():
    """
    Verify that 'gausslag' and 'hankel' backends produce consistent results.
    """
    nmax = 6
    # Use a non-trivial set of G vectors
    # G0=(0,0), G1=(1.5, 0.2), G2=(2.0, pi)
    Gs_dimless = np.array([0.0, 1.5, 2.0])
    thetas = np.array([0.0, 0.2, np.pi])
    
    # Compute with both backends
    X_gl = get_exchange_kernels(Gs_dimless, thetas, nmax, method="gausslag")
    X_hk = get_exchange_kernels(Gs_dimless, thetas, nmax, method="hankel")
    
    # Check for agreement
    # The Hankel transform can be slightly less precise depending on the grid,
    # but should agree well for standard Coulomb potentials.
    assert np.allclose(X_gl, X_hk, rtol=1e-4, atol=1e-4), \
        "Mismatch between Gauss-Laguerre and Hankel backends"

def test_large_n_consistency():
    """
    Verify consistency at larger nmax (e.g. 12) with relaxed tolerance.
    """
    nmax = 12
    Gs_dimless = np.array([0.0, 1.5, 2.0])
    thetas = np.array([0.0, 0.2, np.pi])
    
    X_gl = get_exchange_kernels(Gs_dimless, thetas, nmax, method="gausslag")
    X_hk = get_exchange_kernels(Gs_dimless, thetas, nmax, method="hankel")
    
    # At nmax=12, we expect ~1.3e-4 difference due to Gauss-Laguerre limits
    assert np.allclose(X_gl, X_hk, rtol=2e-4, atol=2e-4), \
        "Mismatch at large nmax exceeded relaxed tolerance"

def test_analytic_coulomb_limit_zero_G():
    """
    Verify the analytic limit for Coulomb interaction at G=0 for lowest Landau level.
    
    Analytic value:
    X_{0000}(0) = \\int d^2q/(2pi)^2 * (2pi/q) * |F_{00}(q)|^2
                = \\int_0^\\inf q dq/(2pi) * (2pi/q) * exp(-q^2/2)
                = \\int_0^\\inf dr * exp(-r^2/2)   (where r=q)
                = sqrt(pi/2)
    """
    nmax = 1
    Gs_dimless = np.array([0.0])
    thetas = np.array([0.0])
    
    # Expected value: sqrt(pi/2)
    expected = np.sqrt(np.pi / 2.0)
    
    # Check Gauss-Laguerre
    X_gl = get_exchange_kernels(Gs_dimless, thetas, nmax, method="gausslag")
    val_gl = X_gl[0, 0, 0, 0, 0]
    assert np.isclose(val_gl, expected, atol=1e-8), \
        f"Gauss-Laguerre failed analytic limit. Got {val_gl}, expected {expected}"
        
    # Check Hankel
    X_hk = get_exchange_kernels(Gs_dimless, thetas, nmax, method="hankel")
    val_hk = X_hk[0, 0, 0, 0, 0]
    assert np.isclose(val_hk, expected, atol=1e-5), \
        f"Hankel failed analytic limit. Got {val_hk}, expected {expected}"

def test_symmetry_checks_extended():
    """
    Run the symmetry diagnostic on a larger set of G vectors.
    """
    nmax = 3
    # A mix of magnitudes and angles
    Gs_dimless = np.array([0.1, 1.0, 2.5, 5.0])
    thetas = np.array([0.0, np.pi/3, np.pi/2, 3*np.pi/4])
    
    # This function asserts internally if symmetries are violated
    verify_exchange_kernel_symmetries(Gs_dimless, thetas, nmax, rtol=1e-6, atol=1e-8)

def test_gausslag_convergence():
    """
    Verify that increasing quadrature points doesn't change the result significantly
    (convergence check).
    """
    nmax = 2
    Gs_dimless = np.array([1.0])
    thetas = np.array([0.0])
    
    X_low = get_exchange_kernels_GaussLag(Gs_dimless, thetas, nmax, nquad=100)
    X_high = get_exchange_kernels_GaussLag(Gs_dimless, thetas, nmax, nquad=200)
    
    assert np.allclose(X_low, X_high, rtol=1e-6, atol=1e-4), \
        "Gauss-Laguerre quadrature not converged between nquad=50 and nquad=200"
