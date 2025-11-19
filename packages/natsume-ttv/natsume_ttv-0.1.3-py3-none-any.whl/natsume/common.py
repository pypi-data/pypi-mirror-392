# Functions shared by Lithwick (2012) and Deck & Agol (2016) literatures
import numpy as np
from scipy.integrate import quad
from scipy.special import comb as nCr

# Determine MMR for string input
def get_MMR(MMRstr: str):
    try: 
        j, i = MMRstr.split(':')
        jj, ii = int(j), int(i)
        if (jj == float(j)) and (ii == float(i)) and (jj > ii) and (ii > 0):
            N = jj - ii
            return jj, N
        else:
            raise ValueError(f"MMR argument must be in 'j:i' format, where i, j are integers such that j > i > 0.")

    except ValueError:
        raise ValueError(f"MMR argument must be in 'j:i' format, where i, j are integers such that j > i > 0.")
    
# Semi-major axis ratio
def get_alpha(innerPeriod, outerPeriod):
    return (innerPeriod / outerPeriod)**(2/3)

# Period calculation from superperiod; Will return two possible solutions
def get_innerPeriods(outerPeriod, superperiod: float, j: int, N: int):
    innerPeriod = (j-N) / (j / outerPeriod + 1 / np.array([superperiod, -superperiod]))
    return innerPeriod

def get_outerPeriods(innerPeriod, superperiod: float, j: int, N: int):
    outerPeriod = j / ((j-N) / innerPeriod + 1 / np.array([superperiod, -superperiod]))
    return outerPeriod

# Normalized distance to resonance
def get_NormalizedResonanceDistance(innerPeriod, outerPeriod, j: int, N: int):
    Delta = outerPeriod/innerPeriod * (j-N)/j - 1
    return Delta

# Laplace coefficient and their numerical derivatives
def get_b(alpha, j: int, epsrel=1e-5, method='powerseries'):
    if method == 'integrate': # Numerical integration, ~2x slower
        def func(theta, alpha, j): # Function to integrate
            return np.cos(j*theta) / np.sqrt(1 - 2*alpha*np.cos(theta) + alpha**2)

        if isinstance(alpha, np.ndarray):
            integral = np.array([])
            for a in alpha:
                int, err = quad(func, 0, 2*np.pi, args=(a, j), epsrel=epsrel)
                integral = np.append(integral, int)
        else:
            integral, err = quad(func, 0, 2*np.pi, args=(alpha, j), epsrel=epsrel)

        return integral / np.pi
    
    elif method == 'powerseries': # Power series (Mardling 2013, Appendix C)
        # This method has relative error epsrel = alpha^(2p) where p is the number of iterations
        p_to_epsrel = np.ceil(0.5 * np.log(epsrel) / np.log(alpha))
        p_list = range(round(np.max(p_to_epsrel)) + 1) # p=0 to p=p_to_epsrel.max
        summation = 0
        for p in p_list:
            summation += 2**(1 - 4*p - 2*j) * nCr(2*p, p) * nCr(2*(j+p), j+p) * alpha**(2*p)
        
        laplace_coeff = alpha**j * summation
        return laplace_coeff

    else:
        raise ValueError(f'Laplace coefficient retrieval method {method} does not exist!')

# Central finite difference numerical differentiation (Fornberg 1988)
# All has O(eps^2) error
def get_Db(alpha, j: int, order=1, eps=1e-5):
    if order == 1:
        return (get_b(alpha + eps, j) - get_b(alpha - eps, j)) / (2 * eps)
    elif order == 2:
        return (get_b(alpha + eps, j) - 2*get_b(alpha, j) + get_b(alpha - eps, j)) / (eps**2)
    elif order == 3:
        return (0.5*get_b(alpha + 2*eps, j) - get_b(alpha + eps, j) + \
                get_b(alpha - eps, j) - 0.5*get_b(alpha - 2*eps, j)) / (eps**3)
    elif order == 4:
        return (get_b(alpha + 2*eps, j) - 4*get_b(alpha + eps, j) + 6*get_b(alpha, j) - \
                4*get_b(alpha - eps, j) + get_b(alpha - 2*eps, j)) / (eps**4)
    else:
        raise ValueError(f'NATSUME does not support numerical differentation of Laplace coefficients at order {order} (N > 4)')
