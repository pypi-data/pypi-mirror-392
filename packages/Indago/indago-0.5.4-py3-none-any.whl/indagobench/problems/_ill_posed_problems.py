#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ill-posed Problems test functions
"""

import numpy as np
import sys
sys.path.append('../..')


class IPP:
    """Ill-posed Problems test suite class.
      
    Parameters
    ----------
    problem : str
        Name of the test function. Required initialization parameter.
        Allowed values: 'invpar', 'invparsh', 'steppar', 'offprod',
        'offprodex', 'noisypar'.
    dimensions : int
        Dimensionality of the test functions.
        
    Attributes
    ----------
    case_definitions : dict
        Dict of problem names (key) and corresponding available dimensions (value).
    dimensions : int
        Dimensionality of the regression model parameter space.
    lb : ndarray
        Vector of lower bounds.
    ub : ndarray
        Vector of upper bounds.
    xmin : ndarray
        Design vector at function minimum.
    fmin : float
        Function minimum.
    
    Returns
    -------
    fitness: float
        Fitness of the input design vector on the chosen goal function.
    """

    case_definitions = {
                        'invpar': None,
                        'invparsh': None,
                        'steppar': None,
                        'offprod': None,
                        'offprodex': None,
                        'noisypar': None
                        }
    
    def __call__(self, x):
        """A method that enables an IPP instance to be callable."""
        return self._f_call(x)
    
    def __init__(self, problem, dimensions=None, instance_label=None):
        """Initialize case"""

        assert problem in self.case_definitions, \
            f'Problem {problem} not defined in IPP problem class'

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

        self._f_call = None
        functions = [self.invpar,
                     self.invparsh,
                     self.steppar, 
                     self.offprod, 
                     self.offprodex, 
                     self.noisypar
                     ]

        for f in functions:
            if problem == f.__name__:
                self._f_call = f
                break
        else:
            assert False, f'Cannot find {problem} function'
            
        self.dimensions = int(dimensions)
        self.lb = np.full(dimensions, -100)
        self.ub = np.full(dimensions, 100)
        self.fmin = 0.0
        if problem in ['noisypar', 'steppar']:
            self.xmin = np.linspace(1, dimensions, dimensions)
        else:
            self.xmin = np.full(dimensions, np.nan)
        self.__name__ = f'IPP_{problem}_{dimensions}D'

    def invpar(self, x):
        """
        Inverse hyperparabola.

        The problem is ill-posed because it has many (2^d) global optima,
        and the function is concave.
        """
        return -np.sum(x**2) / np.size(x) + 100**2

    def invparsh(self, x):
        """
        Shifted inverse hyperparabola.

        The problem is ill-posed because its global optimum is on the bound,
        and the function is concave.
        """
        offset = np.linspace(1, np.size(x), np.size(x))
        x = x - offset  # shift
        return -np.sum(x ** 2) / np.size(x) + np.sum((100 + offset) ** 2) / np.size(x)
    
    def steppar(self, x):
        """
        Stepped (rounded) hyperparabola.

        The problem is ill-posed because it has infinite number of local
        optima and has a gradient of zero everywhere.
        """
        x = x - np.linspace(1, np.size(x), np.size(x))  # shift
        return np.sum(np.round(x)**2)
    
    def offprod(self, x):
        """
        Offset product of design vector.

        The problem is ill-posed because it has infinite number of global
        optima which are far apart.
        """
        x = x - np.linspace(1, np.size(x), np.size(x))  # shift
        return np.log10(np.abs(np.prod(np.abs(x)) - 1) + 1)
    
    def offprodex(self, x):
        """
        Offset product of exponential design vector.

        The problem is ill-posed because it has infinite number of global
        optima which are far apart.
        """
        x = x - np.linspace(1, np.size(x), np.size(x))  # shift
        return np.log10(np.abs(np.prod(np.exp(x/100)) - 1) + 1)
    
    def noisypar(self, x):
        """
        Noisy (chaotic) hyperparabola.

        The problem is ill-posed because the function is chaotic, although
        having only one global optimum.
        """
        ksi = (x + 100) / 200  # starting position for logistic map (ub/lb = +/-100)
        for _ in range(30):
            ksi = 3.99 * ksi * (1 - ksi)
        x = x - np.linspace(1, np.size(x), np.size(x))  # shift
        return np.sum(x ** 2 + 100 * np.abs(x) * ksi)


IPP_5d_problems_dict_list = []
for case in IPP.case_definitions:
    f_dict = {'label': f'IPP_{case}_5D',
              'class': IPP,
              'case': case,
              'dimensions': 5,
              'max_evaluations': 100 * 5 ** 2,
              'max_runs': 1000,
              }
    IPP_5d_problems_dict_list.append(f_dict)

IPP_10d_problems_dict_list = []
for case in IPP.case_definitions:
    f_dict = {'label': f'IPP_{case}_10D',
              'class': IPP,
              'case': case,
              'dimensions': 10,
              'max_evaluations': 100 * 10 ** 2,
              'max_runs': 1000,
              }
    IPP_10d_problems_dict_list.append(f_dict)

IPP_20d_problems_dict_list = []
for case in IPP.case_definitions:
    f_dict = {'label': f'IPP_{case}_20D',
              'class': IPP,
              'case': case,
              'dimensions': 20,
              'max_evaluations': 80 * 20 ** 2,
              'max_runs': 1000,
              }
    IPP_20d_problems_dict_list.append(f_dict)

IPP_50d_problems_dict_list = []
for case in IPP.case_definitions:
    f_dict = {'label': f'IPP_{case}_50D',
              'class': IPP,
              'case': case,
              'dimensions': 50,
              'max_evaluations': 70 * 50 ** 2,
              'max_runs': 1000,
              }
    IPP_50d_problems_dict_list.append(f_dict)

IPP_problems_dict_list = IPP_5d_problems_dict_list + \
                         IPP_10d_problems_dict_list + \
                         IPP_20d_problems_dict_list + \
                         IPP_50d_problems_dict_list


if __name__ == '__main__':

    """
    # demo noisypar
    fun = IPP(problem='noisypar', dimensions=1)
    import matplotlib.pyplot as plt
    X = np.linspace(fun.lb[0], fun.ub[0], 200)
    Y = np.empty_like(X)
    for i, x in enumerate(X):
        Y[i] = fun(x)
    plt.plot(X, Y)
    plt.show()
    """

    import _local_paths
    import indagobench
    standard_test = indagobench.StandardTest(_local_paths.indagobench25_results_dir,
                                             convergence_window=50, eps_max=0.01, runs_min=100)
    standard_test.optimizers = indagobench.indagobench25_optimizers
    standard_test.problems = IPP_problems_dict_list

    standard_test.run_all()
