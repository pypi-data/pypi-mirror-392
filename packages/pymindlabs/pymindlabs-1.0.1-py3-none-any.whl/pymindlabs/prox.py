import numpy
import math
import time
from numpy import matlib

def l2norm_der_ft(f, k):
    """
    Compute L2-norm of k-th derivative of f using Fourier transform
    """

    f = f.flatten('F')
    n = f.size
    w = 2*numpy.pi*numpy.roll(numpy.arange(-math.floor(n/2),math.ceil(n/2)).transpose(), n%2)
    w = numpy.fft.fftshift(numpy.power(w,2*k))
    
    ndf = numpy.abs( numpy.fft.fft(f) / n )
    ndf = numpy.power(ndf, 2)
    ndf = numpy.multiply(w, ndf)
    ndf = numpy.sqrt(numpy.sum(ndf))
    
    return ndf

def num_divergence(W_1, W_2):
    """
    Numerical divergence
    """

    div_W = numpy.zeros(W_1.shape)
    div_W[1:-1,:] = W_1[1:-1,:] - W_1[:-2,:]
    div_W[0,:] = W_1[0,:]
    div_W[-1,:] = -W_1[-2,:]
    div_W[:,1:-1] = div_W[:,1:-1] + W_2[:,1:-1] - W_2[:,:-2]
    div_W[:,0] += W_2[:,0]
    div_W[:,-1] -= W_2[:,-2]
    
    return div_W

def num_grad(g):
    """
    Numerical gradient
    """

    g_x = numpy.zeros(g.shape)
    g_x[:-1,:] = g[1:,:] - g[:-1,:]
    g_y = numpy.zeros(g.shape)
    g_y[:,:-1] = g[:,1:] - g[:,:-1]
    
    return [g_x, g_y]

def proxHk(v, pen, k, verbose = False):
    """
    Proximal operator of Hk
        minimize_{u} 1/2||u - v||_2^2  + lambda/2 ||D^ u||_2^2
    """

    m, n = v.shape
    wr = matlib.repmat(2*numpy.pi*numpy.roll(numpy.arange(-math.floor(m/2), math.ceil(m/2)).reshape(m, 1), m%2), 1, n)
    wc = matlib.repmat(2*numpy.pi*numpy.roll(numpy.arange(-math.floor(n/2), math.ceil(n/2)),n%2), m, 1)
    w = numpy.fft.fftshift(numpy.power(numpy.power(wr, 2)+numpy.power(wc, 2), k))
    
    if verbose:
        print("Sobolev inversion ...\n")
        tic = time.perf_counter()
        
    pen = pen / (m*n)
    u = numpy.fft.ifft2(numpy.divide(numpy.fft.fft2(v), 1+numpy.multiply(pen, w))).real
    
    if verbose:
        print("elapsed {} seconds\n".format(time.perf_counter() - tic))
        
    return u

def proxTV(v, pen, ui = None, maxit = 500, tol = 10e-3, verbose = False):
    """
    Proximal operator of TV
        minimize_{u} 1/2||u - v||_2^2  + lambda||\nabla u||_1
    """

    tau = 0.24
    if ui is None:
        ui = v
        
    w = ui
    W_1 = numpy.zeros(ui.shape)
    W_2 = numpy.zeros(ui.shape)
    v_x, v_y = num_grad(v)
    not_converged = True
    nit = 0
    
    while not_converged:
        w_x, w_y = num_grad(w)
        W_1 = W_1 + tau*(w_x + v_x)
        W_2 = W_2 + tau*(w_y + v_y)
        rescaling_factor = numpy.sqrt(W_1**2 + W_2**2) / pen
        rescaling_factor[rescaling_factor < 1] = 1
        W_1 = W_1 / rescaling_factor
        W_2 = W_2 / rescaling_factor
        w_new = num_divergence(W_1, W_2)

        if (nit >= maxit) or (numpy.max(abs(w_new - w)) <= tol):
            not_converged = False

        w = w_new
        nit += 1
        
    if verbose:
        print("iterations in \"proxTv\": ", nit)
        
    u = w+v
    
    return u


def chTV(g, pen, maxit = 500, tol = 10e-3, verbose = False):
    """
    Proximal operator of TV ('fast' algorithm)
        minimize_{u} 1/2||u - v||_2^2  + lambda||\nabla u||_1
    """

    tau = 0.24
    nit = 0

    p_1 = numpy.zeros(g.shape)
    p_2 = numpy.zeros(g.shape)
    w = g
    not_converged = True
    while not_converged:
        grad_1, grad_2 = num_grad(num_divergence(p_1, p_2) - g/pen)
        rescale = 1 + tau * numpy.sqrt(numpy.power(grad_1, 2) + numpy.power(grad_2, 2))
        p_1 = (p_1 + tau * grad_1) / rescale
        p_2 = (p_2 + tau * grad_2) / rescale
        # match stopping criterion
        w_new = pen * num_divergence(p_1, p_2)
        nit += 1

        if (nit > maxit) or (numpy.max(abs(w_new - w)) < tol):
            not_converged = False

        w = w_new

    if verbose:
        print("iterations in \"chTv\": ", nit)

    return g - w_new

def proxl1(v, pen):
    """
    Proximal operator of l1 norm
        minimize_{u} 1/2||u - v||_2^2  + lambda||u||_1
    """

    if isinstance(v, list):
        u = v.copy()
        for i in range(len(u)):
            u[i] = proxl1(v[i], pen)
    elif isinstance(v, tuple):
        return proxl1(v[0], pen), proxl1(v[1], pen), proxl1(v[2], pen)
    else:
        aux = numpy.abs(v) - pen
        aux = (aux + numpy.abs(aux)) / 2
        u = numpy.multiply(numpy.sign(v), aux)

    return u
