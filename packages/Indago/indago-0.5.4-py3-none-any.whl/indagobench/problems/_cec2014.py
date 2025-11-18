#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 12:19:49 2018

@author: stefan
"""

import numpy as np
import os

class CEC2014:
    """CEC 2014 test suite class.
    
    Reference: Liang, J. J., Qu, B. Y., & Suganthan, P. N. (2013). 
    Problem definitions and evaluation criteria for the CEC 2014 special session 
    and competition on single objective real-parameter numerical optimization. 
    Computational Intelligence Laboratory, Zhengzhou University, Zhengzhou China 
    and Technical Report, Nanyang Technological University, Singapore, 635.
    
    Parameters
    ----------
    problem : str
        Name of the test functions. Required initialization parameter.
        Allowed values: 'F1', 'F2', ..., 'F30'.
    dimensions : int
        Dimensionality of the test functions. Required initialization parameter.
        Allowed values: 10, 20, 50, 100.
        
    Attributes
    ----------
    
    M : ndarray
        Rotation matrix. Loaded from CEC 2014 data.
    O : ndarray
        Shifted global optimum vector. Loaded from CEC 2014 data.
    S : ndarray
        Shuffle vector (randperm). Loaded from CEC 2014 data.
    case_definitions : list of str
        A collection of names for all 30 test functions.
    """

    case_definitions = {f'F{i + 1}': [10, 20, 50, 100] for i in range(30)}

    def __call__(self, x):
        """A method that enables a CEC2014 instance to be callable. It evaluates CEC2014._f_call that is set
        in CEC2014.__init__ in order to point to appropriate CEC2014 function."""
        return self._f_call(x)

    def __init__(self, problem, dimensions=None, instance_label=None):
        """Initialize and read all data"""

        self._f_call = None
        functions = [self.F1, self.F2, self.F3, self.F4, self.F5, self.F6,
                     self.F7, self.F8, self.F9, self.F10, self.F11,
                     self.F12, self.F13, self.F14, self.F15, self.F16,
                     self.F17, self.F18, self.F19, self.F20, self.F21,
                     self.F22, self.F23, self.F24, self.F25, self.F26,
                     self.F27, self.F28, self.F29, self.F30]

        assert dimensions in [10, 20, 50, 100], \
            'CEC2014 dimension must be one of the following: 10, 20, 50, 100'

        assert problem in [f.__name__ for f in functions], \
            f'Unknown CEC2014 function {problem}'

        # Load the data
        data_dir = os.path.dirname(os.path.abspath(__file__))
        self.M, self.O, self.S = [], [], []
        for f in range(30):
            self.M.append(np.loadtxt(f'{data_dir}/cec2014_data/M_{f + 1}_D{dimensions}.txt'))
            self.O.append(np.loadtxt(f'{data_dir}/cec2014_data/shift_data_{f + 1}.txt')[:dimensions])
            self.S.append(np.loadtxt(f'{data_dir}/cec2014_data/shuffle_data_{f + 1}_D{dimensions}.txt',
                                     dtype='int') - 1)

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
        self.xmin = np.full(dimensions, np.nan)
        self.__name__ = f'CEC2014_{problem}_{dimensions}D'

    def f1(self, x):
        """High Conditioned Elliptic Function"""
        d = np.size(x)
        return np.sum(np.power(1e6, np.arange(d) / (d - 1)) * np.power(x, 2))

    def f2(self, x):
        """Bent Cigar Function"""
        return x[0] ** 2 + 1e6 * np.sum(x[1:] ** 2)

    def f3(self, x):
        """Discus Function"""
        return 1e6 * x[0] ** 2 + np.sum(x[1:] ** 2)

    def f4(self, x):
        """Rosenbrock’s Function"""
        return np.sum(100.0 * (x[:-1] ** 2 - x[1:]) ** 2 + (x[:-1] - 1.0) ** 2)

    def f5(self, x):
        """Ackley’s Function"""
        d = np.size(x)
        return -20.0 * np.exp(-0.2 * np.sqrt(np.sum(x ** 2) / d)) - \
            np.exp(1.0 / d * np.sum(np.cos(2 * np.pi * x))) + 20 + np.e

    def f6(self, x):
        """Weierstrass Function"""
        a, b, kmax = 0.5, 3.0, 20
        d = np.size(x)
        s1, s2 = 0.0, 0.0
        for k in range(kmax + 1):
            s1 += np.power(a, k) * np.cos(2 * np.pi *
                                          np.power(b, k) * (x + 0.5))
            s2 += np.power(a, k) * np.cos(2 * np.pi * np.power(b, k) * 0.5)
        return np.sum(s1) - d * s2

    def f7(self, x):
        """Griewank’s Function"""
        d = np.size(x)
        return np.sum(x ** 2 / 4000.0) - \
            np.prod(np.cos(x / np.sqrt(np.arange(d) + 1))) + 1.0

    def f8(self, x):
        """Rastrigin's Function"""
        return np.sum(x ** 2 - 10.0 * np.cos(2 * np.pi * x) + 10)

    def f9(self, x):
        """Modified Schwefel’s Function"""
        d = np.size(x)
        z = x + 4.209687462275036e+002
        g = np.empty_like(x)
        g[np.abs(z) <= 500.0] = z[np.abs(z) <= 500.0] * \
                                np.sin(np.sqrt(np.abs(z[np.abs(z) <= 500.0])))
        m500 = 500.0 - np.mod(z[z > 500.0], 500.0)
        g[z > 500.0] = m500 * \
                       np.sin(np.sqrt(np.abs(m500))) - \
                       (z[z > 500.0] - 500) ** 2 / (10000 * d)
        ma500 = np.mod(np.abs(z[z < -500.0]), 500.0) - 500.0
        g[z < -500.0] = ma500 * \
                        np.sin(np.sqrt(np.abs(ma500))) - \
                        (z[z < -500.0] + 500.0) ** 2 / (10000 * d)
        return 418.9829 * d - np.sum(g)

    def f10(self, x):
        """Katsuura Function"""
        d = np.size(x)
        s = np.zeros_like(x, dtype=float)
        for i in range(d):
            for j in range(1, 33):
                s[i] += np.abs(2 ** j * x[i] - np.round(2 ** j * x[i])) / 2 ** j
        return (10 / d ** 2) * np.prod((1 + np.arange(1, d + 1) * s) ** (10 / d ** 1.2), dtype=float) - (10 / d ** 2)

    def f11(self, x):
        """HappyCat Function"""
        d = np.size(x)
        x = x - 1  # undocumented shift to origin
        return np.abs(np.sum(x ** 2) - d) ** (1 / 4) + \
            (0.5 * np.sum(x ** 2) + np.sum(x)) / d + 0.5

    def f12(self, x):
        """HGBat Function"""
        d = np.size(x)
        x = x - 1  # undocumented shift to origin
        return np.abs(np.sum(x ** 2) ** 2 - np.sum(x) ** 2) ** (1 / 2) + \
            (0.5 * np.sum(x ** 2) + np.sum(x)) / d + 0.5

    def f13(self, x):
        """Expanded Griewank’s plus Rosenbrock’s Function"""
        s = 0.0
        for pair in np.array([x, np.roll(x, -1)]).T:
            s += self.f7(self.f4(pair))
        return s

    def f14(self, x):
        """Expanded Scaffer’s F6 Function"""

        def g(X, Y):
            return 0.5 + (np.sin((X ** 2 + Y ** 2) ** 0.5) ** 2 - 0.5) \
                / (1 + 0.001 * (X ** 2 + Y ** 2)) ** 2

        """
        # Possible speedup - needs to be tested
        def g_fast(x, y):
            xy2 = x**2 + y**2
            return 0.5 + (np.sin(np.sqrt(xy2))**2-0.5) / (1 + 0.001 * xy2)**2
        """
        return np.sum(g(x, np.roll(x, -1)))

    def F1(self, x, M=None, O=None):
        """Rotated High Conditioned Elliptic Function"""
        if M is None:
            M = self.M[0]

        if O is None:
            O = self.O[0]
        return self.f1(np.dot(M, x - O))

    def F2(self, x, M=None, O=None):
        """Rotated Bent Cigar Function"""
        if M is None:
            M = self.M[1]

        if O is None:
            O = self.O[1]

        return self.f2(np.dot(M, x - O))

    def F3(self, x, M=None, O=None):
        """Rotated Discus Function"""
        if M is None: M = self.M[2]
        if O is None: O = self.O[2]
        return self.f3(np.dot(M, x - O))

    def F4(self, x, M=None, O=None):
        """Shifted and Rotated Rosenbrock’s Function"""
        if M is None:
            M = self.M[3]

        if O is None:
            O = self.O[3]

        return self.f4(np.dot(M, 2.048 * (x - O) / 100) + 1)

    def F5(self, x, M=None, O=None):
        """Shifted and Rotated Ackley’s Function"""
        if M is None:
            M = self.M[4]

        if O is None:
            O = self.O[4]

        return self.f5(np.dot(M, x - O))

    def F6(self, x, M=None, O=None):
        """Shifted and Rotated Weierstrass Function"""
        if M is None:
            M = self.M[5]

        if O is None:
            O = self.O[5]

        return self.f6(np.dot(M, 0.005 * (x - O)))

    def F7(self, x, M=None, O=None):
        """Shifted and Rotated Griewank’s Function"""
        if M is None:
            M = self.M[6]

        if O is None:
            O = self.O[6]

        return self.f7(np.dot(M, 6.0 * (x - O)))

    def F8(self, x, M=None, O=None):
        """Shifted Rastrigin’s Function"""
        if O is None:
            O = self.O[7]
        return self.f8(0.0512 * (x - O))

    def F9(self, x, M=None, O=None):
        """Shifted and Rotated Rastrigin’s Function"""
        if M is None:
            M = self.M[8]

        if O is None:
            O = self.O[8]
        return self.f8(np.dot(M, 0.0512 * (x - O)))

    def F10(self, x, M=None, O=None):
        """Shifted Schwefel’s Function"""
        if O is None:
            O = self.O[9]
        return self.f9(10.0 * (x - O))

    def F11(self, x, M=None, O=None):
        """Shifted and Rotated Schwefel’s Function"""
        if M is None:
            M = self.M[10]

        if O is None:
            O = self.O[10]
        return self.f9(np.dot(M, 10.0 * (x - O)))

    def F12(self, x, M=None, O=None):
        """Shifted and Rotated Katsuura Function"""
        if M is None:
            M = self.M[11]

        if O is None:
            O = self.O[11]
        return self.f10(np.dot(M, 0.05 * (x - O)))

    def F13(self, x, M=None, O=None):
        """Shifted and Rotated HappyCat Function"""
        if M is None:
            M = self.M[12]

        if O is None:
            O = self.O[12]
        return self.f11(np.dot(M, 0.05 * (x - O)))

    def F14(self, x, M=None, O=None):
        """Shifted and Rotated HGBat Function"""
        if M is None:
            M = self.M[13]

        if O is None:
            O = self.O[13]
        return self.f12(np.dot(M, 0.05 * (x - O)))

    def F15(self, x, M=None, O=None):
        """Shifted and Rotated Expanded Griewank’s plus Rosenbrock’s Function"""
        if M is None:
            M = self.M[14]

        if O is None:
            O = self.O[14]
        return self.f13(np.dot(M, 0.05 * (x - O)) + 1)

    def F16(self, x, M=None, O=None):
        """Shifted and Rotated Expanded Scaffer’s F6 Function"""
        if M is None:
            M = self.M[15]

        if O is None:
            O = self.O[15]
        # return self.f14(np.dot(M, (x - O)) + 1)  # shifting by -1 is documented but not implemented in C++ code
        return self.f14(np.dot(M, x - O))

    def _hybrid_function(self, caller_function, S, p, g, x):
        """Base function for generating hybrid functions"""
        d = np.size(x)
        n = np.cumsum(np.array(p) * d) - np.array(p) * d
        n = np.append(n, d).astype('int')
        s = 0.0
        if caller_function in range(17, 23):
            x_sr = np.dot(self.M[caller_function - 1],
                          x - self.O[caller_function - 1])
            S = self.S[caller_function - 1]
        else:  # called by _composition_function, no need to shift/rotate
            x_sr = x
        for n_start, n_stop, gg in zip(n[:-1], n[1:], g):
            indices = S[n_start:n_stop]
            s += gg(x_sr[indices], M=1.0, O=0.0)
        return s

    def F17(self, x, M=None, O=None, upstream_caller_function=None, S=None):
        """Hybrid Function 1"""
        if M is not None and O is not None:
            x = np.dot(M, x - O)
        function_nr = 17
        if upstream_caller_function is not None:  # called by _composition_function
            function_nr = upstream_caller_function
        return self._hybrid_function(function_nr, S,
                                     [0.3, 0.3, 0.4],
                                     [self.F10, self.F8, self.F1], x)

    def F18(self, x, M=None, O=None, upstream_caller_function=None, S=None):
        """Hybrid Function 2"""
        if M is not None and O is not None:
            x = np.dot(M, x - O)
        function_nr = 18
        if upstream_caller_function is not None:
            function_nr = upstream_caller_function
        return self._hybrid_function(function_nr, S,
                                     [0.3, 0.3, 0.4],
                                     [self.F2, self.F14, self.F8], x)

    def F19(self, x, M=None, O=None, upstream_caller_function=None, S=None):
        """Hybrid Function 3"""
        if M is not None and O is not None:
            x = np.dot(M, x - O)
        function_nr = 19
        if upstream_caller_function is not None:
            function_nr = upstream_caller_function
        return self._hybrid_function(function_nr, S,
                                     [0.2, 0.2, 0.3, 0.3],
                                     [self.F7, self.F6, self.F4, self.F16], x)

    def F20(self, x, M=None, O=None, upstream_caller_function=None, S=None):
        """Hybrid Function 4"""
        if M is not None and O is not None:
            x = np.dot(M, x - O)
        function_nr = 20
        if upstream_caller_function is not None:
            function_nr = upstream_caller_function
        return self._hybrid_function(function_nr, S,
                                     [0.2, 0.2, 0.3, 0.3],
                                     [self.F14, self.F3, self.F15, self.F8], x)

    def F21(self, x, M=None, O=None, upstream_caller_function=None, S=None):
        """Hybrid Function 5"""
        if M is not None and O is not None:
            x = np.dot(M, x - O)
        function_nr = 21
        if upstream_caller_function is not None:
            function_nr = upstream_caller_function
        return self._hybrid_function(function_nr, S,
                                     [0.1, 0.2, 0.2, 0.2, 0.3],
                                     [self.F16, self.F14, self.F4, self.F10, self.F1], x)

    def F22(self, x, M=None, O=None, upstream_caller_function=None, S=None):
        """Hybrid Function 6"""
        if M is not None and O is not None:
            x = np.dot(M, x - O)
        function_nr = 22
        if upstream_caller_function is not None:
            function_nr = upstream_caller_function
        return self._hybrid_function(function_nr, S,
                                     [0.1, 0.2, 0.2, 0.2, 0.3],
                                     [self.F12, self.F13, self.F15, self.F11, self.F5], x)

    def _composition_function(self, caller_function, sigma, lmbd, bias, g, x):
        """Base function for generating composition functions"""
        d = np.size(x)
        w = np.empty(len(g))
        for i in range(len(g)):
            O = self.O[caller_function - 1][i, :d]
            sumsqrd = np.sum((x - O) ** 2) + 1e-300  # added fix for divide by zero
            w[i] = (1 / np.sqrt(sumsqrd)) * \
                   np.exp(-sumsqrd / (2 * d * sigma[i] ** 2))
        omega = w / (np.sum(w) + 1e-300)  # added fix for divide by zero
        s = 0.0
        for i in range(len(g)):
            M = self.M[caller_function - 1][i * d:(i + 1) * d, :]
            O = self.O[caller_function - 1][i, :d]
            # calling a hybrid function asks for shuffling per caller_function
            if g[i] in [self.F17, self.F18, self.F19,
                        self.F20, self.F21, self.F22]:
                S = self.S[caller_function - 1][d * i:d * (i + 1)]
                s += omega[i] * (lmbd[i] * g[i](x, M, O,
                                                caller_function, S) + bias[i])
            else:
                s += omega[i] * (lmbd[i] * g[i](x, M, O) + bias[i])
        return s

    def F23(self, x):
        """Composition Function 1"""
        return self._composition_function(23,
                                          [10, 20, 30, 40, 50],
                                          [1, 1e-6, 1e-26, 1e-6, 1e-6],
                                          [0, 100, 200, 300, 400],
                                          [self.F4, self.F1, self.F2, self.F3,
                                           lambda x, M, O: self.F1(x, 1, O)], x)

    def F24(self, x):
        """Composition Function 2"""
        return self._composition_function(24,
                                          [20, 20, 20],
                                          [1, 1, 1],
                                          [0, 100, 200],
                                          [lambda x, M, O: self.F10(x, 1, O),
                                           self.F9, self.F14], x)

    def F25(self, x):
        """Composition Function 3"""
        return self._composition_function(25,
                                          [10, 30, 50],
                                          [0.25, 1, 1e-7],
                                          [0, 100, 200],
                                          [self.F11, self.F9, self.F1], x)

    def F26(self, x):
        """Composition Function 4"""
        return self._composition_function(26,
                                          [10, 10, 10, 10, 10],
                                          [0.25, 1, 1e-7, 2.5, 10],
                                          [0, 100, 200, 300, 400],
                                          [self.F11, self.F13, self.F1, self.F6, self.F7], x)

    def F27(self, x):
        """Composition Function 5"""
        return self._composition_function(27,
                                          [10, 10, 10, 20, 20],
                                          [10, 10, 2.5, 25, 1e-6],
                                          [0, 100, 200, 300, 400],
                                          [self.F14, self.F9, self.F11, self.F6, self.F1], x)

    def F28(self, x):
        """Composition Function 6"""
        return self._composition_function(28,
                                          [10, 20, 30, 40, 50],
                                          [2.5, 10, 2.5, 5e-4, 1e-6],
                                          [0, 100, 200, 300, 400],
                                          [self.F15, self.F13, self.F11, self.F16, self.F1], x)

    def F29(self, x):
        """Composition Function 7"""
        return self._composition_function(29,
                                          [10, 30, 50],
                                          [1, 1, 1],
                                          [0, 100, 200],
                                          [self.F17, self.F18, self.F19], x)

    def F30(self, x):
        """Composition Function 8"""
        return self._composition_function(30,
                                          [10, 30, 50],
                                          [1, 1, 1],
                                          [0, 100, 200],
                                          [self.F20, self.F21, self.F22], x)


cec2014_10d_problems_dict_list = []
for case in CEC2014.case_definitions:
    f_dict = {'label': f'CEC_{case}_10D',
              'class': CEC2014,
              'case': case,
              'dimensions': 10,
              'max_evaluations': 100 * 10 ** 2,
              'max_runs': 1000,
              }
    cec2014_10d_problems_dict_list.append(f_dict)

cec2014_20d_problems_dict_list = []
for case in CEC2014.case_definitions:
    f_dict = {'label': f'CEC_{case}_20D',
              'class': CEC2014,
              'case': case,
              'dimensions': 20,
              'max_evaluations': 100 * 20 ** 2,
              'max_runs': 1000,
              }
    cec2014_20d_problems_dict_list.append(f_dict)

cec2014_50d_problems_dict_list = []
for case in CEC2014.case_definitions:
    f_dict = {'label': f'CEC_{case}_50D',
              'class': CEC2014,
              'case': case,
              'dimensions': 50,
              'max_evaluations': 100 * 50 ** 2,
              'max_runs': 1000,
              }
    cec2014_50d_problems_dict_list.append(f_dict)

CEC_problems_dict_list = cec2014_10d_problems_dict_list + cec2014_20d_problems_dict_list + cec2014_50d_problems_dict_list


if __name__ == '__main__':


    import sys
    print(f'{sys.argv=}')
    print(f'Available arguments: 10D, 20D, 50D, all (or no arguments provided)')
    # x = np.random.uniform(-100, 100, 10)
    # for fun in range(30):
    #     f = CEC2014(f'F{fun + 1}', 10)
    #     print(f'{f.__name__}, {f(x)}')

    # import sys
    # sys.path.append('../..')
    # sys.path.append('../../tests')

    import indagobench
    # from indagobench import _local_paths
    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir,
                                             processes=10)
    standard_test.optimizers = indagobench.indagobench25_optimizers

    if len(sys.argv) == 1: # No arguments
        standard_test.problems = CEC_problems_dict_list
    elif '10D' in sys.argv[1:]:
        standard_test.problems = cec2014_10d_problems_dict_list
    elif '20D' in sys.argv[1:]:
        standard_test.problems = cec2014_20d_problems_dict_list
    elif '50D' in sys.argv[1:]:
        standard_test.problems = cec2014_50d_problems_dict_list
    elif 'all' in sys.argv[1:]:
        standard_test.problems = CEC_problems_dict_list

    standard_test.run_all()
