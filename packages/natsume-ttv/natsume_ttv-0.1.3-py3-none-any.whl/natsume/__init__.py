# Near-resonant Analytic TTV Solver for Unknown Mass Estimation
from .classes import TTVSineCurve, ComplexEccentricities
from .common import get_MMR
from .Lithwick import LithwickOuterInversion, LithwickInnerInversion
from .DeckAgol import DeckAgolOuterInversion, DeckAgolInnerInversion

# Create classes (Cannot define classes here due to circular import)
def get_ComplexEccentricities(inner_e=0, inner_periastron=0,
                              outer_e=0, outer_periastron=0):
    return ComplexEccentricities(inner_e, inner_periastron, outer_e, outer_periastron)

def get_TTVSineCurve(amplitude: float, superperiod: float):
    return TTVSineCurve(amplitude, superperiod)


### Mass estimation functions -- returns array of 2 if outer_period='none'
def EstimateOuterMass(innerTTV: TTVSineCurve, inner_period: float, mmr: str,
                      eccentricity=ComplexEccentricities(), outer_period='none'):
    j, N = get_MMR(mmr)

    if N == 1:
        mass = LithwickOuterInversion(innerTTV, inner_period, j,
                                      eccentricity, outerPeriod=outer_period)
    else:
        mass = DeckAgolOuterInversion(innerTTV, inner_period, j, N,
                                      eccentricity, outerPeriod=outer_period)
    return mass

def EstimateInnerMass(outerTTV: TTVSineCurve, outer_period: float, mmr: str,
                      eccentricity=ComplexEccentricities(), inner_period='none'):
    j, N = get_MMR(mmr)
    
    if N == 1:
        mass = LithwickInnerInversion(outerTTV, outer_period, j,
                                      eccentricity, innerPeriod=inner_period)
    else:
        mass = DeckAgolInnerInversion(outerTTV, outer_period, j, N,
                                      eccentricity, innerPeriod=inner_period)
    return mass
