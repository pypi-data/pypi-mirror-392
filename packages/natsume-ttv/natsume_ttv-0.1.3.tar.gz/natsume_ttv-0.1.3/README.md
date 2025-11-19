# NATSUME  
**N**ear-resonant **A**nalytic **T**TV **S**olver for **U**nknown **M**ass **E**stimates (NATSUME) for Python 3 (Work in progress!)

A python 3 module which aims to quickly estimate non-transiting exoplanet masses in possible near Mean Motion Resonance (MMR) scenarios from approximately sinusoidal Transit Timing Variation (TTV) signals.

The TTV mass inversion estimations are based from Lithwick's model for 1st order near MMR (https://doi.org/10.1088/0004-637X/761/2/122) and Deck-Agol's model for higher order near MMRs (https://doi.org/10.3847/0004-637X/821/2/96).

Installation
=====
Eventually, installation should be as simple as
```
pip install natsume
```

But right now, you can install it from the TestPyPI package index:
```
pip install -i https://test.pypi.org/simple/ natsume
```

Usage
=====

To use NATSUME:
* Build two objects containing TTV signal information (amplitude and "superperiod") and complex orbital eccentricity information (see Lithwick's eqn. 11) via ``natsume.get_TTVSineCurve`` and  ``natsume.get_ComplexEccentricities`` respectively.
* Estimate inner or outer exoplanet masses via ``natsume.EstimateInnerMass`` or ``natsume.EstimateOuterMass`` functions.
* The code will return a list of two possible mass solutions calculated from the input arguments.
  * Remark: There are two solutions, because the perturbing planet's period can be unknown if it is non-transiting, and two periods are possible given the definition of the TTV superperiod (see Lithwick's eqn. 5). You can restrict to one solution by specifying the perturbing planet's period in the estimation functions. This skips the calculation of the perturbing planet's period completely, so make sure the ``mmr`` argument is close enough!

For example, to estimate the outer planet Kepler-32 c's mass assuming zero eccentricity:

```python
import natsume

# We use Kepler-32, all time unit in days (from Lithwick et al. 2012)
# Expected solution: 7.59 Earths for outer planet c

# Setup parameters here
Pb = 5.901    # Inner period (days)
Pc = 8.752    # Outer period (days)
Vb = 0.0062   # Inner TTV Amplitude (days)
PTTV = 1/abs(3/Pc - 2/Pb)  # Calculated TTV "superperiod" (not provided by Lithwick; so we calculate)
mmr = '3:2'   # MMR Scenario
Mstar = 0.49  # Host star mass (solar masses)

# Build object for sinusoidal inner TTV
TTVb = natsume.get_TTVSineCurve(amplitude=Vb, superperiod=PTTV)

# Build object for system complex eccentricity; Assumes zero eccentricity in this case
z = natsume.get_ComplexEccentricities()

# Estimate outer planet mass relative to the host star
mu_c = natsume.EstimateOuterMass(
   innerTTV=TTVb,
   inner_period=Pb,
   mmr=mmr,
   eccentricity=z,
   outer_period=None
)
```
For nonzero eccentricities, let's suppose inner "free eccentricity" is 0.01, inner longitude of periastron is 90 degrees, outer "free eccentricity" is 0.03, and outer longitude of periastron is 200 degrees, the following arguments are to be put in ``natsume.get_ComplexEccentricities``
```python
z = natsume.get_ComplexEccentricities(e1=0.01, w1=90, e2=0.03, w2=200)
```

And if the perturbing outer planet's orbital period is known (``Pc``), modify the ``outer_period=None`` argument in ``natsume.EstimateOuterMass`` as follows:
```python
mu_c = natsume.EstimateOuterMass(
   innerTTV=TTVb,
   inner_period=Pb,
   mmr=mmr,
   eccentricity=z,
   outer_period=Pc
)
```

Finally, conversion from ``mu_c`` in host stellar mass to mass estimate in Earth masses can be done with ``astropy.units``. In-package support may be available in the future.
```python
from astropy import units as u
m_c = (mu_c * Mstar*u.M_sun).to(u.M_earth).value
print(f'Estimated outer planet mass: {m} Earths')
```


For further details, see documentation which hasn't been written yet (It's work in progress code!, or you can just read the source code)
