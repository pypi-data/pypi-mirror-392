import numpy as np

def density_to_cholesky(rho_array):
    """Convert density matrices to Cholesky vector representation."""
    num_states = rho_array.shape[0]
    dim = rho_array.shape[1]
    cholesky_vectors = np.zeros((num_states, dim**2))

    for n in range(num_states):
        L = np.linalg.cholesky(rho_array[n])
        imL = np.imag(L)
        reL = np.real(L)

        k_i = 0
        for i in range(dim):
            for j in range(0, i+1):
                cholesky_vectors[n, k_i] = reL[i, j]
                k_i += 1

        for i in range(1, dim):
            for j in range(i):
                cholesky_vectors[n, k_i] = imL[i, j]
                k_i += 1

    return cholesky_vectors

def cholesky_to_density(cholesky_vec, dim):
    """Convert Cholesky vector back to density matrix."""
    rhoC = np.zeros((dim, dim), dtype=complex)

    k_i = 0
    for i in range(dim):
        for j in range(0, i+1):
            rhoC[i, j] += cholesky_vec[k_i]
            k_i += 1

    for i in range(1, dim):
        for j in range(i):
            rhoC[i, j] += 1j * cholesky_vec[k_i]
            k_i += 1

    rho = np.dot(rhoC, rhoC.T.conj())
    rho /= np.trace(rho)
    return rho
