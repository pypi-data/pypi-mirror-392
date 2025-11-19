import numpy as np

### Classes
# Complex eccentricities containing the eccentricity and
# longitude of periastron for inner and outer planets (input in deg, kept as rad!) 
class ComplexEccentricities:
    def __init__(self,
                 inner_e=0, inner_periastron=0,
                 outer_e=0, outer_periastron=0):
        try:
            if (inner_e < 0) or (outer_e < 0):
                raise ValueError(f'inner_e and outer_e in ComplexEccentricities must be greater than or equal to 0.')
            self.inner_e = float(inner_e)
            self.inner_periastron = np.deg2rad(float(inner_periastron))
            self.outer_e = float(outer_e)
            self.outer_periastron = np.deg2rad(float(outer_periastron))

        except (TypeError, ValueError):
            raise TypeError(f'All ComplexEccentricities arguments must be a float or integer.')

    @property
    def arr(self):
        return np.array([self.inner_e, self.inner_periastron,
                         self.outer_e, self.outer_periastron])

# TTV Sine curve with amplitude in minutes and superperiod in days
class TTVSineCurve:
    def __init__(self, amplitude: float, superperiod: float):
        try:
            if (amplitude <= 0) or (superperiod <= 0):
                raise ValueError(f'Amplitude and superperiod in TTVSineCurve must be greater than 0.')
            self.amplitude = float(amplitude)
            self.superperiod = float(superperiod)

        except (TypeError, ValueError):
            raise TypeError(f'All TTVSineCurve arguments must be a float or integer.')
        
    @property
    def arr(self):
        return np.array([self.amplitude, self.superperiod])
