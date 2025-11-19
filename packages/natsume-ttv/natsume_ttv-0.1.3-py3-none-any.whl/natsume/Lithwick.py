# Functions that only exist in the Lithwick (2012) literature
import numpy as np

from .classes import ComplexEccentricities, TTVSineCurve
from .common import get_b, get_Db, get_alpha, get_NormalizedResonanceDistance, get_outerPeriods, get_innerPeriods

# Lithwick disturbing functions
def get_f(alpha, j: int):
    return -(j * get_b(alpha, j)) - (alpha/2 * get_Db(alpha, j, order=1))

def get_g(alpha, j: int):
    if j == 2:
        # -1/(2 * alpha^2) s.t. alpha ~ (1/2)**(2/3) for inner perturber,
        # -2 * alpha for outer perturber, which are identical!
        correction = -1.25992104989
    else:
        correction = 0
    return (j-0.5) * get_b(alpha, j-1) + (alpha/2 * get_Db(alpha, j-1, order=1)) + correction

# Weighted average of free eccentricities
def get_Zfree(f, g, z: ComplexEccentricities):
    return (f * z.inner_e * np.exp(1j * z.inner_periastron)) + \
           (g * z.outer_e * np.exp(1j * z.outer_periastron))


# Inversion functions
def LithwickOuterInversion(innerTTV: TTVSineCurve, innerPeriod: float,
                           j: int, z: ComplexEccentricities, outerPeriod='none'):
    if outerPeriod == 'none':
        outerPeriods = get_outerPeriods(innerPeriod, innerTTV.superperiod, j, N=1)
    else:
        outerPeriods = outerPeriod

    alpha = get_alpha(innerPeriod, outerPeriods)
    f = get_f(alpha, j)
    g = get_g(alpha, j)
    Delta = get_NormalizedResonanceDistance(innerPeriod, outerPeriods, j, N=1)
    Zfree = get_Zfree(f, g, z)

    massRatio = np.pi * innerTTV.amplitude * j**(2/3) * (j-1)**(1/3) * np.abs(Delta) / innerPeriod / \
                np.abs(f + 1.5 * np.conj(Zfree) / Delta)
    return massRatio

def LithwickInnerInversion(outerTTV: TTVSineCurve, outerPeriod: float,
                           j: int, z: ComplexEccentricities, innerPeriod='none'):
    if innerPeriod == 'none':
        innerPeriods = get_innerPeriods(outerPeriod, outerTTV.superperiod, j, N=1)
    else:
        innerPeriods = innerPeriod

    alpha = get_alpha(innerPeriods, outerPeriod)
    f = get_f(alpha, j)
    g = get_g(alpha, j)
    Delta = get_NormalizedResonanceDistance(innerPeriods, outerPeriod, j, N=1)
    Zfree = get_Zfree(f, g, z)

    massRatio = np.pi * outerTTV.amplitude * j * np.abs(Delta) / outerPeriod / \
                np.abs(-g + 1.5 * np.conj(Zfree) / Delta)
    return massRatio
