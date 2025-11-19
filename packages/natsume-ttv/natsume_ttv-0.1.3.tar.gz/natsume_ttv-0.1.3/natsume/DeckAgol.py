# Functions that only exist in the Deck-Agol (2016) literature
import numpy as np

from .classes import ComplexEccentricities, TTVSineCurve
from .Lithwick import get_f, get_g, get_Zfree
from .common import get_outerPeriods, get_innerPeriods, get_alpha, get_NormalizedResonanceDistance
from .common import get_b, get_Db

# Source: Dermott & Murray 1999, Appendix B
# Disturbing function coefficients (2nd order)
def get_g_j45(alpha, j): # k=N=2
    return 1/8 * ((-5*j + 4*j**2) * get_b(alpha, j) + \
                  (4*j - 2) * alpha * get_Db(alpha, j, order=1) + \
                  alpha**2 * get_Db(alpha, j, order=2))

def get_g_j49(alpha, j): # k=1
    return 1/4 * ((-2 + 6*j - 4*j**2) * get_b(alpha, j-1) - \
                  (4*j - 2) * alpha * get_Db(alpha, j-1, order=1) - \
                  alpha**2 * get_Db(alpha, j-1, order=2))

def get_g_j53(alpha, j): # k=0
    if j == 3:
        correction = -1.6225307666
        # -3/(8 * alpha^2) s.t. alpha ~ (1/3)**(2/3) for inner perturber,
        # -27/8 * alpha for outer perturber, which are identical!
    else:
        correction = 0
    return 1/8 * ((2 - 7*j + 4*j**2) * get_b(alpha, j-2) + \
                  (4*j - 2) * alpha * get_Db(alpha, j-2, order=1) + \
                  alpha**2 * get_Db(alpha, j-2, order=2)) + correction

# Disturbing function coefficients (3rd order)
def get_g_j82(alpha, j): # k=N=3
    return 1/48 * ((-26*j + 30*j**2 - 8*j**3) * get_b(alpha, j) + \
                   (-9 + 27*j - 12*j**2) * alpha * get_Db(alpha, j ,order=1) + \
                   (6 - 6*j) * alpha**2 * get_Db(alpha, j, order=2) - \
                   alpha**3 * get_Db(alpha,j , order=3))

def get_g_j83(alpha, j): # k=2
    return 1/16 * ((-9 + 31*j - 30*j**2 + 8*j**3) * get_b(alpha, j-1) + \
                   (9 - 25*j + 12*j**2) * alpha * get_Db(alpha, j-1, order=1) + \
                   (-5 + 6*j) * alpha**2 * get_Db(alpha, j-1, order=2) + \
                   alpha**3 * get_Db(alpha, j-1, order=3))

def get_g_j84(alpha, j): # k=1
    return 1/16 * ((8 - 32*j + 30*j**2 - 8*j**3) * get_b(alpha, j-2) + \
                   (-8 + 23*j - 12*j**2) * alpha * get_Db(alpha, j-2, order=1) + \
                   (4 - 6*j) * alpha**2 * get_Db(alpha, j-2, order=2) - \
                   alpha**3 * get_Db(alpha, j-2, order=3))

def get_g_j85(alpha, j): # k=0
    if j == 4:
        # -1/(3 * alpha^2) s.t. alpha ~ (1/4)**(2/3) for inner perturber,
        # -16/3 * alpha for outer perturber, which are identical!
        correction = -2.11653473596
    else:
        correction = 0
    return 1/48 * ((-6 + 29*j - 30*j**2 + 8*j**3) * get_b(alpha, j-3) + \
                   (6 - 21*j + 12*j**2) * alpha * get_Db(alpha, j-3, order=1) + \
                   (-3 + 6*j) * alpha**2 * get_Db(alpha, j-3, order=2) + \
                   alpha**3 * get_Db(alpha, j-3, order=3)) + correction

# Disturbing function coefficients (4th order)
def get_g_j90(alpha, j): # k=N=4
    return 1/384 * ((-206*j + 283*j**2 - 120*j**3 + 16*j**4) * get_b(alpha, j) + \
                    (-64 + 236*j - 168*j**2 + 32*j**3) * alpha * get_Db(alpha, j, order=1) + \
                    (48 - 78*j + 24*j**2) * alpha**2 * get_Db(alpha, j, order=2) + \
                    (-12 + 8*j) * alpha**3 * get_Db(alpha, j, order=3) + 
                    alpha**4 * get_Db(alpha, j, order=4))

def get_g_j91(alpha, j): # k=3
    return 1/96 * ((-64 + 238*j - 274*j**2 + 116*j**3 - 16*j**4) * get_b(alpha, j-1) + \
                   (64 - 206*j + 156*j**2 - 32*j**3) * alpha * get_Db(alpha, j-1, order=1) + \
                   (-36 + 69*j - 24*j**2) * alpha**2 * get_Db(alpha, j-1, order=2) + \
                   (10 - 8*j) * alpha**3 * get_Db(alpha, j-1, order=3) - \
                   alpha**4 * get_Db(alpha, j-1, order=4))

def get_g_j92(alpha, j): # k=2
    return 1/64 * ((52 - 224*j + 259*j**2 - 112*j**3 + 16*j**4) * get_b(alpha, j-2) + \
                   (-52 + 176*j - 144*j**2 + 32*j**3) * alpha * get_Db(alpha, j-2, order=1) + \
                   (26 - 60*j + 24*j**2) * alpha**2 * get_Db(alpha, j-2, order=2) + \
                   (-8 + 8*j) * alpha**3 * get_Db(alpha, j-2, order=3) + \
                   alpha**4 * get_Db(alpha, j-2, order=4))

def get_g_j93(alpha, j): # k=1
    return 1/96 * ((-36 + 186*j - 238*j**2 + 108*j**3 - 16*j**4) * get_b(alpha, j-3) + \
                   (36 - 146*j + 132*j**2 - 32*j**3) * alpha * get_Db(alpha, j-3, order=1) + \
                   (-18 + 51*j - 24*j**2) * alpha**2 * get_Db(alpha, j-3, order=2) + \
                   (6 - 8*j) * alpha**3 * get_Db(alpha, j-3, order=3) - \
                   alpha**4 * get_Db(alpha, j-3, order=4))

def get_g_j94(alpha, j): # k=0
    if j == 5:
        # -125/(384 * alpha^2) s.t. alpha ~ (1/5)**(2/3) for inner perturber,
        # -3125/384 * alpha for outer perturber, which are identical!
        correction = -2.78316397571
    else:
        correction = 0
    return 1/384 * ((24 - 146*j + 211*j**2 - 104*j**3 + 16*j**4) * get_b(alpha, j-4) + \
                    (-24 + 116*j - 120*j**2 + 32*j**3) * alpha * get_Db(alpha, j-4, order=1) + \
                    (12 - 42*j + 24*j**2) * alpha**2 * get_Db(alpha, j-4, order=2) + \
                    (-4 + 8*j) * alpha**3 * get_Db(alpha, j-4, order=3) + \
                    alpha**4 * get_Db(alpha, j-4, order=4)) + correction

# Get gk == g_j,k;N
def get_gk(N, alpha, j):
    if N == 2:
        gk = [get_g_j53(alpha, j), get_g_j49(alpha, j), get_g_j45(alpha, j)]
    elif N == 3:
        gk = [get_g_j85(alpha, j), get_g_j84(alpha, j), get_g_j83(alpha, j), get_g_j82(alpha, j)]
    elif N == 4: 
        gk = [get_g_j94(alpha, j), get_g_j93(alpha, j), get_g_j92(alpha, j), get_g_j91(alpha, j), get_g_j90(alpha, j)]
    else:
        raise NotImplementedError('NATSUME does not support TTVs of order N > 4 near MMR.')
    return gk
    
# AB functions -- gk is a list of g_j,k;N, with index k (from k=0)
def get_A1(gk, e1, e2, w1, w2):
    N = len(gk) - 1  # No need to input N!
    A1 = 0
    for k in range(N+1):
        phi = k*w1 + (N-k)*w2
        A1 += gk[k] * e2**(N-k) * e1**(k) * np.cos(phi)
    return A1

def get_A2(gk, e1, e2, w1, w2):
    N = len(gk) - 1  # No need to input N!
    A2 = 0
    for k in range(N+1):
        phi = k*w1 + (N-k)*w2
        A2 += gk[k] * e2**(N-k) * e1**(k) * np.sin(phi)
    return -A2

def get_B11(gk, e1, e2, w1, w2):
    N = len(gk) - 1  # No need to input N!
    B11 = 0
    for k in range(N+1):
        phi = k*w1 + (N-k)*w2
        B11 += gk[k] * k * e2**(N-k) * e1**(k-1) * np.cos(phi - w1)
    return B11

def get_B12(gk, e1, e2, w1, w2):
    N = len(gk) - 1  # No need to input N!
    B12 = 0
    for k in range(N+1):
        phi = k*w1 + (N-k)*w2
        B12 += gk[k] * k * e2**(N-k) * e1**(k-1) * np.sin(phi - w1)
    return -B12

def get_B21(gk, e1, e2, w1, w2):
    N = len(gk) - 1  # No need to input N!
    B21 = 0
    for k in range(N+1):
        phi = k*w1 + (N-k)*w2
        B21 += gk[k] * (N-k) * e2**(N-k-1) * e1**(k) * np.cos(phi - w2)
    return B21

def get_B22(gk, e1, e2, w1, w2):
    N = len(gk) - 1  # No need to input N!
    B22 = 0
    for k in range(N+1):
        phi = k*w1 + (N-k)*w2
        B22 += gk[k] * (N-k) * e2**(N-k-1) * e1**(k) * np.sin(phi - w2)
    return -B22

# Get 1st order Delta of nearest MMR
# (Not used)
def get_1stOrderDelta(innerPeriod, outerPeriod):
    Pratio = outerPeriod / innerPeriod

    # Get j boundary e.g. 1.66 sits between j=2 and j=3
    jmin = np.ceil(1 / (Pratio - 1)) 
    jmax = jmin + 1

    # Get period threshold between j and j+1
    Pratio_threshold = 0.5 * (jmin/(jmin - 1) + jmax/(jmax - 1))

    # Vectorized selection: choose jmin or jmax per element
    use_jmin = (Pratio >= Pratio_threshold)
    j = np.where(use_jmin, jmin, jmax)

    # Compute Delta directly for all elements
    Delta1o = get_NormalizedResonanceDistance(innerPeriod, outerPeriod, j, N=1)

    # Return scalar if both inputs were scalar
    if np.isscalar(innerPeriod) and np.isscalar(outerPeriod):
        return float(Delta1o)
    return Delta1o


# Inversion functions
# LithwickTerm arg currently does NOT work and will likely be removed in the future
def DeckAgolOuterInversion(innerTTV: TTVSineCurve, innerPeriod: float,
                           j: int, N: int, eccentricity: ComplexEccentricities,
                           outerPeriod='none'):
    if outerPeriod == 'none':
        outerPeriods = get_outerPeriods(innerPeriod, innerTTV.superperiod, j, N)
    else:
        outerPeriods = outerPeriod
    
    alpha = get_alpha(innerPeriod, outerPeriods)
    Delta = get_NormalizedResonanceDistance(innerPeriod, outerPeriods, j, N)
    e1, w1, e2, w2 = eccentricity.arr

    if (e1 == 0) and (e2 == 0):
        raise ValueError('The Deck-Agol model does not provide physical zero-eccentricity mass solutions at N > 1.')

    gk = get_gk(N, alpha, j)
    A1 = get_A1(gk, e1, e2, w1, w2)
    A2 = get_A2(gk, e1, e2, w1, w2)
    B11 = get_B11(gk, e1, e2, w1, w2)
    B12 = get_B12(gk, e1, e2, w1, w2)

    massRatio = np.pi * innerTTV.amplitude * j**(2/3) * (j-N)**(1/3) * np.abs(Delta) / innerPeriod / \
                np.sqrt((1.5 * A1 / Delta + B11)**2 + (1.5 * A2 / Delta + B12)**2)
    return massRatio

def DeckAgolInnerInversion(outerTTV: TTVSineCurve, outerPeriod: float,
                           j: int, N: int, eccentricity: ComplexEccentricities,
                           innerPeriod='none'):
    if innerPeriod == 'none':
        innerPeriods = get_innerPeriods(outerPeriod, outerTTV.superperiod, j, N)
    else:
        innerPeriods = innerPeriod

    alpha = get_alpha(innerPeriods, outerPeriod)
    Delta = get_NormalizedResonanceDistance(innerPeriods, outerPeriod, j, N)
    e1, w1, e2, w2 = eccentricity.arr

    if (e1 == 0) and (e2 == 0):
        raise ValueError('The Deck-Agol model does not provide physical zero-eccentricity mass solutions at N > 1.')
    
    gk = get_gk(N, alpha, j)
    A1 = get_A1(gk, e1, e2, w1, w2)
    A2 = get_A2(gk, e1, e2, w1, w2)
    B21 = get_B21(gk, e1, e2, w1, w2)
    B22 = get_B22(gk, e1, e2, w1, w2)

    massRatio = np.pi * outerTTV.amplitude * j * np.abs(Delta) / outerPeriod / \
                np.sqrt((-1.5 * A1 / Delta + B21)**2 + (-1.5 * A2 / Delta + B22)**2)
    return massRatio
