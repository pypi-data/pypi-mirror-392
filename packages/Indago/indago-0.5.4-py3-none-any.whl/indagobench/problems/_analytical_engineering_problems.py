#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analytical Engineering Problems

@author: sinisa
"""

import numpy as np
import os


def unconstrain(f, f0, p0=0.1):
    """
    Utility function (decorator) for creating unconstrained version of a
    single-objective constrained evaluation function.

    Parameters
    ----------
    f : callable
        Evaluation function for which the unconstrained penalty-based version
        is to be created.
    f0 : float
        Reference value of function minimum.
    p0 : float
        Relative size of penalty step. Penalty for each constrain (c) is
        computed as **f0** * **p0** + c

    Returns
    -------
    f_penalty : callable
        Penalty-based single-objective evaluation function.
    """

    def f_penalty(x, *args, **kwargs):
        fit, *constr = f(x, *args, **kwargs)

        penalty = 0
        for c in constr:
            penalty += 0 if c <= 0 else np.abs(f0 * p0) + c

        return fit + penalty

    # append doc
    f_penalty.__doc__ = f.__doc__ + ' (unconstrained)'

    return f_penalty


def _round_smooth(x, true_round=False):
    """
    Private utility function for producing smooth piecewise-constant (rounded) values
    by use of sigmoid function. Useful for rounding variables for the purpose
    of converting discrete or mixed variables optimization problems into
    continuous variable problems. Can do true (not smoothed) rounding if needed.

    Parameters
    ----------
    x : ndarray
        Design vector to smoothly round.
    true_round : bool
        If **True**, normal rounding is performed.

    Returns
    -------
    x : ndarray
        Smoothly rounded values.

    """

    if true_round:
        x = np.round(x)
    else:
        decimals = x - np.floor(x)
        x_sigmoid = decimals - 0.5
        y_sigmoid = 1 / (1 + np.exp(-100 * (x_sigmoid)))
        x = np.floor(x) + y_sigmoid

    return x


class AEP():
    """Analytical Engineering Problems test suite class.

    Problem definitions and evaluation criteria for the analytical engineering problems
    (single objective).
    
    Parameters
    ----------
    problem : str
        Name of the test function. Required initialization parameter.
    dimensions : int or None
        Dimensionality of the test functions. ``None`` allowed for problems with 
        fixed dimensionality.
    unconstrained : bool
        If ``False``, base evaluation functions (mostly constrained) are used. 
        If ``True``, an unconstrained version of the evaluation function is
        produced using penalty function. Default: ``True``.
        
    Attributes
    ----------
    case_definitions : dict
        Dict of problem names (key) and corresponding available dimensions (value).
    _spring, _vessel, ... , _springmass : callable
        Private base evaluation functions corresponding to the analytical 
        engineering problems.
    constraints : int
        Number of constraints of the produced evaluation function.
    lb : ndarray
        Vector of lower bounds.
    ub : ndarray
        Vector of upper bounds.
    xmin : ndarray
        Design vector at function minimum.
    fmin : float
        Function minimum.
    dimensions : int
        Dimensionality of the test functions.

    Returns
    -------
    fitness: float or tuple
        Fitness (or a tuple of fitness and constraint values) of the produced 
        evaluation function.
        
    """
    
    case_definitions = {'spring': [3],
                        'vessel': [4],
                        'calever': [5],
                        'welbeam': [4],
                        'reducer': [7],
                        'sound': [6],
                        'stepped': None,
                        'potent': None,  # in CEC2011 used with dimensions=30
                        'radar': None,  # in CEC2011 used with dimensions=20
                        'sprmass': None,
                        'solar': None
                        }

    def __call__(self, x, *args, **kwargs):
        """
        A method that enables an AEP instance to be callable. Evaluates 
        AEP._f_call that is set in AEP.__init__ in order to point to the
        appropriate AEP function.
        """
        
        return self._f_call(x, *args, **kwargs)
    
    def __init__(self, problem, dimensions=None, unconstrained=True, instance_label=None):
        """Initialize case"""

        self._f_call = None
        
        assert problem in self.case_definitions, \
            f'Problem {problem} not defined in AEP problem class'

        if dimensions is None:
            assert len(self.case_definitions[problem]) == 1, \
                'Problem {problem} is defined for more than one number of dimensions'
            dimensions = self.case_definitions[problem][0]
        
        if not self.case_definitions[problem]:
            assert isinstance(dimensions, int) and dimensions > 0, \
                'dimensions should be positive integer'
        else:
            assert dimensions in self.case_definitions[problem], \
                f'Problem {problem} dimension must be one of the following: {self.case_definitions[problem]}'

        if problem == 'spring':
            
            if unconstrained:
                self._f_call = unconstrain(self._spring, 0.013)
            else:
                self._f_call = self._spring
                self.constraints = 4
            
            self.lb = np.array([0.05, 0.25, 2])
            self.ub = np.array([2, 1.3, 15])
            self.fmin = np.nan
            self.xmin = np.full(dimensions, np.nan)

        elif problem == 'vessel':
            
            if unconstrained:
                self._f_call = unconstrain(self._vessel, 6000)
            else:
                self._f_call = self._vessel
                self.constraints = 4
            
            self.lb = np.array([1, 1, 10, 10])
            self.ub = np.array([99, 99, 200, 240])
            self.fmin = np.nan
            self.xmin = np.full(dimensions, np.nan)

        elif problem == 'calever':
            
            if unconstrained:
                self._f_call = unconstrain(self._cantilever, 1.34)
            else:
                self._f_call = self._cantilever
                self.constraints = 1
            
            self.lb = np.full(dimensions, 0.01)
            self.ub = np.full(dimensions, 100)
            self.fmin = np.nan
            self.xmin = np.full(dimensions, np.nan)

        elif problem == 'welbeam':
            
            if unconstrained:
                self._f_call = unconstrain(self._weldedbeam, 1.74)
            else:
                self._f_call = self._weldedbeam
                self.constraints = 7
            
            self.lb = np.full(dimensions, 0.1)
            self.ub = np.array([2, 10, 10, 2])
            self.fmin = np.nan
            self.xmin = np.full(dimensions, np.nan)

        elif problem == 'reducer':
            
            if unconstrained:
                self._f_call = unconstrain(self._reducer, 3000)
            else:
                self._f_call = self._reducer
                self.constraints = 9
            
            self.lb = np.array([2.6, 0.7, 17, 7.3, 7.3, 2.9, 5.0])
            self.ub = np.array([3.6, 0.8, 28, 8.3, 8.3, 3.9, 5.5])
            self.fmin = np.nan
            self.xmin = np.full(dimensions, np.nan)

        elif problem == 'sound':
            
            # constants
            self._sound_phi = 2 * np.pi / 100
            self._sound_T = np.arange(0, 101)
            
            self._f_call = self._sound
            unconstrained = False
            
            self.lb = np.full(dimensions, -6.4)
            self.ub = np.full(dimensions, 6.35)
            self.fmin = 0.0
            self.xmin = np.array([1, 5, -1.5, 4.8, 2, 4.9])
        
        elif problem == 'stepped':
            
            assert isinstance(dimensions, int) and dimensions >= 2 \
                and dimensions % 2 == 0, \
                "Number of dimensions should be even integer"
            
            # constants
            N = dimensions // 2
            P = 50_000
            L = 500
            li = L / N
            
            self._stepped_M = np.array([P * (L + li - li * i) \
                                  for i in range(1, N+1)])
            self._stepped_N = N
            self._stepped_li = li
            self._stepped_sigma_ = 14_000
            
            if unconstrained:
                self._f_call = unconstrain(self._stepped, 54_000)
            else:
                self._f_call = self._stepped
                self.constraints = 2 * N
            
            self.lb = np.array(N * [1] + N * [5])
            self.ub = np.full(dimensions, L)
            self.fmin = np.nan
            self.xmin = np.full(dimensions, np.nan)
        
        elif problem == 'potent':
            
            assert isinstance(dimensions, int) and dimensions >= 3 \
                and dimensions % 3 == 0, \
                "Number of dimensions should be integer multiple of 3"
            
            # constants
            N = dimensions // 3
            
            self._potential_N = N
            self._potential_R = np.full([N, N], np.nan)
            
            self._f_call = self._potential
            unconstrained = False
            
            self.lb = np.array(3 * [-4 - 1/4 * np.floor((i+1 - 4) / 3) \
                                                for i in range(0, N)])
            self.ub = np.array(3 * [4 + 1/4 * np.floor((i+1 - 4) / 3) \
                                                for i in range(0, N)])
            self.fmin = np.nan
            self.xmin = np.full(dimensions, np.nan)
            # fref = -100
        
        elif problem == 'radar':
            
            # constants
            self._radar_n = dimensions           
            self._radar_m = 2 * self._radar_n - 1
            
            self._f_call = self._radar
            unconstrained = False
            
            self.lb = np.full(dimensions, 0.0)
            self.ub = np.full(dimensions, 2 * np.pi)
            self.fmin = np.nan
            self.xmin = np.full(dimensions, np.nan)
            
        elif problem == 'sprmass':
            
            assert isinstance(dimensions, int) and dimensions >= 2 \
                and dimensions % 2 == 0, \
                "Number of dimensions should be even integer"
            
            # constants
            N = dimensions // 2
            L = 1
            
            self._springmass_L = L
            self._springmass_N = N
            
            self._f_call = self._springmass
            unconstrained = False
            
            self.lb = np.array(N * [0] + N * [-10 * L])
            self.ub = np.array(N * [L] + N * [0])
            self.xmin = np.full(dimensions, np.nan)
            self.fmin = np.nan
            
        elif problem == 'solar':
            
            assert isinstance(dimensions, int) and dimensions >= 10 \
                and dimensions <= 8760, \
                "Number of dimensions should be integer in the interval [10, 8760]"
            
            # load data
            data_dir = os.path.dirname(os.path.abspath(__file__))
            self._solar_output = np.loadtxt(f'{data_dir}/aep_data/solar_output.txt')[:dimensions]
            self._solar_price = np.loadtxt(f'{data_dir}/aep_data/solar_price.txt')[:dimensions]
            
            # constants
            B_DELTA_MAX = 50
            self._solar_B_max = 200 # max BESS capacity
            self._solar_C_PV = 50 * 0.93 # PV cost
            self._solar_C_B = 25 * 0.93 # battery cost
            
            if unconstrained:
                self._f_call = unconstrain(self._solar, -40_000 * dimensions/24)
            else:
                self._f_call = self._solar
                self.constraints = 2 * dimensions
            
            self.lb = -B_DELTA_MAX * np.ones(dimensions)
            self.ub = np.minimum(B_DELTA_MAX, self._solar_output)
            self.xmin = np.full(dimensions, np.nan)
            self.fmin = np.nan

        self.dimensions = int(dimensions)
        
        # add name
        name = problem + '+u' if unconstrained else problem
        self.__name__ = f"AEP_{name}_{dimensions}D"
            
    def _spring(self, x):
        """Tension/Compression Spring Design Problem"""
        
        f = (x[2] + 2) * x[1] * x[0]**2
        
        g1 = 1 - x[1]**3 * x[2] / (71_785 * x[0]**4)
        g2 = (4 * x[1]**2 - x[0] * x[1]) / (12_566 * (x[1] * x[0]**3 - x[0]**4)) + 1 / (5_108 * x[0]**2) - 1
        g3 = 1 - 140.45 * x[0] / (x[1]**2 * x[2])
        g4 = (x[0] + x[1]) / 1.5 - 1
        
        return f, g1, g2, g3, g4
    
    def _vessel(self, x, true_round=False):
        """Pressure Vessel Design Problem"""
        
        # first two variables are supposed to be multiples of 0.0625
        _x = np.copy(x)
        _x[0:2] = _round_smooth(_x[0:2], true_round) * 0.0625
               
        f = 0.6224 * _x[0] * _x[2] * _x[3] + 1.7781 * _x[1] * _x[2]**2 \
            + 3.1661 * _x[0]**2 * _x[3] + 19.84 * _x[0]**2 * _x[2]
            
        g1 = -_x[0] + 0.0193 * _x[2]
        g2 = -_x[1] + 0.00954 * _x[2]
        g3 = -np.pi * _x[2]**2 * _x[3] - (4/3) * np.pi * _x[2]**3 + 1_296_000
        
        # implemented in bounds
        # g4 = x[3] - 240 
        
        return f, g1, g2, g3 #, g4
    
    def _cantilever(self, x):
        """Cantilever Beam Design Problem"""
        
        f = 0.0624 * np.sum(x)
        
        g = np.sum(np.array([61, 37, 19, 7, 1]) / x**3) - 1
        
        return f, g
    
    def _weldedbeam(self, x):
        """Welded Beam Design Problem"""
        
        f = 1.10471 * x[0]**2 * x[1] + 0.04811 * x[2] * x[3] * (14 + x[1])
        
        P, L, E, G = 6000, 14, 30e6, 12e6
        tau_max, sigma_max, delta_max = 13_600, 30_000, 0.25
        
        M = P * (L + x[1] / 2)
        R = np.sqrt(x[1]**2 / 4 + ((x[0] + x[2]) / 2)**2)
        sigma_x = 6 * P * L / (x[3] * x[2]**2)
        delta_x = 4 * P * L**3 / (E * x[2]**3 * x[3])
        J = 2 * (np.sqrt(2) * x[0] * x[1] * (x[1]**2 / 12 + ((x[0] + x[2]) / 2)**2))
        Pc_x = 4.013 * E * np.sqrt(x[2]**2 * x[3]**6) / (6 * L**2) \
                * (1 - x[2] / (2 * L) * np.sqrt(E / (4 * G)))
        tau_p = P / (np.sqrt(2) * x[0] * x[1])
        tau_pp = M * R / J
        tau_x = np.sqrt(tau_p**2 + 2 * tau_p * tau_pp * x[1] / (2 * R) + tau_pp**2)
        
        g1 = tau_x - tau_max
        g2 = sigma_x - sigma_max
        g3 = x[0] - x[3]
        g4 = f - 5
        g5 = 0.125 - x[0]
        g6 = delta_x - delta_max
        g7 = P - Pc_x
        
        return f, g1, g2, g3, g4, g5, g6, g7
    
    def _reducer(self, x, true_round=False):
        """Speed Reducer Design Problem"""

        b, m, z, l1, l2, d1, d2 = x
        
        # z is supposed to be integer
        z = _round_smooth(z, true_round)
        
        f = 0.7854 * b * m**2 * (3.3333 * z**2 + 14.9334 * z - 43.0934) \
            - 1.508 * b * (d1**2 + d2**2) + 7.477 * (d1**3 + d2**3) \
            + 0.7854 * (l1 * d1**2 + l2 * d2**2)
        
        g1 = 27 / (b * m**2 * z) - 1
        g2 = 397.5 / (b * m**2 * z**2) - 1
        g3 = 1.93 / (m * z * l1**3 * d1**4) - 1
        g4 = 1.93 / (m * z * l2**3 * d2**4) - 1
        g5 = np.sqrt((745 * l1 / (m * z))**2 + 1.69e6) / (110 * d1**3) - 1
        g6 = np.sqrt((745 * l2 / (m * z))**2 + 157.5e6) / (85 * d2**3) - 1
        g7 = m * z / 40 - 1
        g8 = 5 * m / b - 1
        g9 = b / (12 * m) - 1
        
        return f, g1, g2, g3, g4, g5, g6, g7, g8, g9
    
    def _sound(self, x):
        """Parameter Estimation for FM Sound Waves"""
        
        a1, w1, a2, w2, a3, w3 = x
        
        phi = self._sound_phi
        
        y = lambda t: a1 * np.sin(w1 * t * phi \
                                  + a2 * np.sin(w2 * t * phi \
                                            + a3 * np.sin(w3 * t * phi)))
        y0 = lambda t: 1 * np.sin(5 * t * phi \
                                  - 1.5 * np.sin(4.8 * t * phi \
                                            + 2 * np.sin(4.9 * t * phi)))
        
        return np.sum((y(self._sound_T) - y0(self._sound_T))**2)

    def _stepped(self, x, true_round=False):
        """Stepped Cantilever Beam Problem"""
        
        # Reference: Vanderplaats, G.N., Very Large Scale Optimization. 
        # NASA/CR-2002, 211768, 2002
            
        b, h = x[:self._stepped_N], x[self._stepped_N:]
        
        # design variables are discrete values in increments of 0.1 
        b = 0.1 * _round_smooth(10 * b, true_round)
        h = 0.1 * _round_smooth(10 * h, true_round)
        
        f = np.sum(b * h * self._stepped_li)
        
        I = b * h**3 / 12
        
        G1 = (self._stepped_M * h / (2 * I)) / self._stepped_sigma_ - 1
        G2 = h - 20 * b
        
        # the following two sets of constraints are implemented in bounds
        # G3 = -(b - 1) # b >= 1
        # G4 = -(h - 5) # h >= 5
        
        return f, *G1, *G2 #, *G3, *G4
        
    def _potential(self, x):
        """Lennard-Jones Potential Problem"""
        
        # Reference: Swagatam Das and P. N. Suganthan, Problem Definitions and 
        # Evaluation Criteria for CEC 2011 Competition on Testing Evolutionary 
        # Algorithms on Real World Optimization Problems, Technical Report, 2010
        
        N = self._potential_N
        
        X = np.reshape(x, [N, 3])
        R = self._potential_R
        
        for i in range(0, N-1):
            for j in range(i+1, N):
                R[i,j] = np.linalg.norm(X[j,:] - X[i,:])

        # avoiding division by zero in R**-12
        R[R < 1e-20] = 1e-20
        
        return np.nansum(R**-12 - 2 * R**-6)

    def _radar(self, x):
        """Spread Spectrum Radar Polly Phase Code Design Problem"""
        
        # Reference: Swagatam Das and P. N. Suganthan, Problem Definitions and 
        # Evaluation Criteria for CEC 2011 Competition on Testing Evolutionary 
        # Algorithms on Real World Optimization Problems, Technical Report, 2010

        m = self._radar_m
        n = self._radar_n

        # working with 1-based indexing to avoid errors in transcribing from literature
        phi = np.zeros(2 * m + 1)
        phi[0] = np.nan 
        
        phi[2:(2*n + 1):2] += 0.5
        
        for i in range(1, n+1):       
            for j in range(i, n+1):
                phi[2*i - 1] += np.cos(np.sum(x[(abs(2*i - j - 1) + 1):j+1]))       
        for i in range(1, n):
            for j in range(i+1, n+1):    
                phi[2*i] += np.cos(np.sum(x[(abs(2*i - j) + 1):j+1]))   
        phi[m+1:] = -phi[1:m+1]
        
        # returning to 0-based indexing (removing dummy value at index 0)
        phi = phi[1:]

        return np.max(phi)

    def _springmass(self, x):
        """Spring Mass System Problem"""
        
        # Reference: Vanderplaats, G.N., Very Large Scale Optimization. 
        # NASA/CR-2002, 211768, 2002
        
        N = self._springmass_N
        L = self._springmass_L
        
        X = np.hstack(([0], x[:N], [L]))
        Y = np.hstack(([0], x[N:], [0]))
        
        DL = np.sqrt(np.diff(X)**2 + np.diff(Y)**2) - L / (N + 1)
        
        K = 500 + 200 * ((N / 3) - np.arange(1, N+2))**2
        
        W = 50 * np.arange(1, N+1) * N
        
        return 0.5 * np.sum(K * DL**2) + np.sum(W * Y[1:-1])
    
    def _solar(self, X):
        """Solar Energy Production System Problem"""

        e_sale = self._solar_output - X
        sale = self._solar_price * e_sale
        solar_cost = self._solar_C_PV * self._solar_output
        battery_cost = self._solar_C_B * np.abs(X)
        obj = np.sum(sale - (solar_cost + battery_cost))

        B = np.cumsum(X)
        
        obj = obj * 24 / np.size(X)

        c1 = -B # B >= 0
        c2 = B - self._solar_B_max # B <= B_MAX

        return -obj, *c1, *c2


#### standardized tests
AEP_problems_dict_list = []
for case in AEP.case_definitions:
    if AEP.case_definitions[case] is not None:
        for d in AEP.case_definitions[case]:
            if case != 'sound':
                label = f'AEP_{case}+u_{d}D'
            else:
                label = f'AEP_{case}_{d}D'
            f_dict = {'label': label,
                      'class': AEP,
                      'case': case,
                      'dimensions': d,
                      'max_evaluations': 100 * d ** 2,
                      'max_runs': 1000,
                      }
        AEP_problems_dict_list.append(f_dict)
for d in [10, 20]:
    f_dict = {'label': f'AEP_stepped+u_{d}D',
              'class': AEP,
              'case': 'stepped',
              'dimensions': d,
              'max_evaluations': 70 * d ** 2,
              'max_runs': 1000,
              }
    AEP_problems_dict_list.append(f_dict)
for d in [12, 21, 30]:
    f_dict = {'label': f'AEP_potent_{d}D',
              'class': AEP,
              'case': 'potent',
              'dimensions': d,
              'max_evaluations': 100 * d ** 2,
              'max_runs': 1000,
              }
    AEP_problems_dict_list.append(f_dict)
for d in [10, 20, 30]:
    f_dict = {'label': f'AEP_radar_{d}D',
              'class': AEP,
              'case': 'radar',
              'dimensions': d,
              'max_evaluations': 120 * d ** 2,
              'max_runs': 1000,
              }
    AEP_problems_dict_list.append(f_dict)
for d in [10, 20, ]: # 50
    f_dict = {'label': f'AEP_sprmass_{d}D',
              'class': AEP,
              'case': 'sprmass',
              'dimensions': d,
              'max_evaluations': 100 * d ** 2,
              'max_runs': 1000,
              }
    AEP_problems_dict_list.append(f_dict)
for d in [12, 24, 36]:
    f_dict = {'label': f'AEP_solar+u_{d}D',
              'class': AEP,
              'case': 'solar',
              'dimensions': d,
              'max_evaluations': 70 * d ** 2,
              'max_runs': 1000,
              }
    AEP_problems_dict_list.append(f_dict)


if __name__ == '__main__':

    """
    # demo AEP functions
    print('\n*** demo default AEP functions (unconstrained)')    
    dims = 6 * [None] + 5 * [12]
    test_functions = [AEP(problem=p, dimensions=d) \
                      for p, d in zip(AEP.case_definitions, dims)]

    for f in test_functions:
        x = np.random.uniform(f.lb, f.ub)
        print(f'{f.__name__} \n {f(x)}')
        
    print('\n*** demo original AEP functions (mostly constrained)')    
    dims = 6 * [None] + 5 * [12]
    test_functions = [AEP(problem=p, dimensions=d, unconstrained=False) \
                      for p, d in zip(AEP.case_definitions, dims)]

    for f in test_functions:
        x = np.random.uniform(f.lb, f.ub)
        print(f'{f.__name__} \n {f(x)}')
    """
    
    
    """
    # check feasibility of unconstrained solutions
    from indago import minimize
    dims = 6 * [None] + 4 * [12]
    test_functions_unc = [AEP(problem=p, dimensions=d) \
                          for p, d in zip(AEP.case_definitions, dims)]
    test_functions_orig = [AEP(problem=p, dimensions=d, unconstrained=False) \
                           for p, d in zip(AEP.case_definitions, dims)]
    for f_unc, f_orig in zip(test_functions_unc, test_functions_orig):
        d = len(f_unc.xmin)
        if hasattr(f_orig, 'constraints'):  
            print(f'checking {f_orig.__name__}')
            X, _ = minimize(f_unc, f_unc.lb, f_unc.ub, 
                            'DE', variant='LSHADE',
                            max_evaluations=100*d**2)
            _, *G = f_orig(X)
            if (np.array(G)<=0).all():
                print('... ok')
            else:
                print('... NOT ok')
                print(G)
    """


    """
    # standard test
    import indagobench
    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir,
                                             convergence_window=50, eps_max=0.01, runs_min=100)
    standard_test.optimizers = indagobench.indagobench25_optimizers
    standard_test.problems = AEP_problems_dict_list

    standard_test.run_all()
    """


    """
    aep = AEP(problem='vessel', dimensions=None, unconstrained=False)
    print(aep.__name__)
    print(f'{aep.lb=}')
    print(f'{aep.ub=}')
    for lbl, x_test in[
        ('best', np.array([ 1.,     1.,    51.294, 88.403])),
        ('rs_med', np.array([  3.612,  10.489,  40.445, 239.705])),
        ('bfgs_med', np.array([52.884, 42.751, 56.203, 55.664])),
        ]:
        print()
        print(lbl)
        print(f'{x_test=}')
        print(aep(x_test))
    """
