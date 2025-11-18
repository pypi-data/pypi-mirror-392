#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Empirical Regression test functions
"""

import numpy as np
import os
import matplotlib.pyplot as plt


class EmpReg:
    """Empirical Regression test suite class.
      
    Parameters
    ----------
    problem : str
        Name of the test function. Required initialization parameter.
        Allowed values: 'drag2' (two-parameter drag coefficient regression), 
        'rab' (regression of bathymetric data), 'nylon' (regression of strain-
        stress curve).
    dimensions : int
        Dimensionality of the test functions.
        
    Attributes
    ----------
    case_definitions : dict
        Dict of problem names (key) and corresponding available dimensions (value).
    _evaluate_model : callable
        Private function for evaluating a regression model.
    _model_gen : callable
        Private function for generating regression evaluation function.
    _model1_design : tuple
        1D model design descriptor. Used in **_model_gen**. A tuple of two 
        numbers: number of coefficients a, number of exponents.
    _model2_design : tuple
        2D model design descriptor. Used in **_model_gen**. A tuple of four 
        numbers: number of coefficients a, number of coefficients b, number of 
        coefficients c, number of exponents e.
    inputs : ndarray
        Input data for regression model.
    outputs : ndarray
        Output data for regression model.
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
        Fitness (RMSE) of the regression model of the chosen **problem** and **dimensions**.
    """

    case_definitions = {
                        'drag2': [3, 4, 6, 9],
                        'rab': [3, 4, 6, 9],
                        'nylon': [3, 5, 7]
                        }
    
    def __call__(self, x, plot=False):
        """
        A method that enables an EmpReg instance to be callable. Evaluates a regression model.

        """
        
        return self._evaluate_model(x, plot)
    
    def __init__(self, problem, dimensions=None, instance_label=None):
        """Initialize case"""

        assert problem in self.case_definitions, \
            f'Problem {problem} not defined in EmpReg problem class'

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

        self._model1_design = False
        self._model2_design = False

        if problem == 'drag2':
            """
            Two-parameter drag coefficient regression test functions.
            
            Reference: Holjević T, Družeta S, Grbčić L, Alvir M. Empirical Shape-Based 
            Estimation of Settling Microplastic Particles Drag Coefficient. Journal of 
            Marine Science and Engineering. 2023; 11(11):2166. 
            https://doi.org/10.3390/jmse11112166 
                
            Specific attributes:
            --------------------
            inputs : ndarray
                Reynolds number values and sphericity values packed in a 2d array.
            outputs : ndarray
                Drag coefficient values in a vector.
                   
            """
    
            # prepare data
            Re = np.array([54, 72, 93, 106, 276, 207, 133, 78, 262, 182, 123, 66])
            S = np.array([0.69, 0.64, 0.59, 0.55, 0.81, 0.81, 0.81, 0.81, 1, 1, 1, 1])
            Cd = np.array([1.5, 1.4, 1.39, 1.37, 0.97, 1.01, 1.31, 1.6, 0.69, 0.86, 1.02, 1.48])
    
            self.inputs = np.vstack((Re, S)).T
            self.outputs = Cd

            # regression model param bounds
            c_lb, c_ub = -100, 100
            exp_lb, exp_ub = -5, 5
            off_lb, off_ub = -2, 2
            
            self._model2_design = True

        elif problem == 'rab':
            """
            Regression of seabed elevation for the area near island of Rab, Croatia.

            Specific attributes:
            --------------------
            inputs : ndarray
                Latitude and longitude values packed in a 2d array.
            outputs : ndarray
                Bathymetry data (seabed elevation).
    
            """

            # load data
            data_dir = os.path.dirname(os.path.abspath(__file__))
            data = np.loadtxt(f'{data_dir}/empirical_regression_data/rab.txt')
            self.inputs = data[:, :2]
            self.outputs = data[:, 2]

            # regression model param bounds
            c_lb, c_ub = -100, 100
            exp_lb, exp_ub = -5, 5
            off_lb, off_ub = -200, 200
            
            self._model2_design = True
            
        elif problem == 'nylon':
            """
            Regression of strain-stress curve for nylon.

            Specific attributes:
            --------------------
            inputs : ndarray
                Strain data in 1d array.
            outputs : ndarray
                Stress data in 1d array.
    
            """

            # load data
            data_dir = os.path.dirname(os.path.abspath(__file__))
            data = np.loadtxt(f'{data_dir}/empirical_regression_data/nylon.txt')
            self.inputs = data[:, 0]
            self.outputs = data[:, 1]

            # regression model param bounds
            c_lb, c_ub = -100, 100
            exp_lb, exp_ub = -5, 5
            off_lb, off_ub = -100, 100
            
            self._model1_design = True
        
        if self._model1_design:
            
            # setting model1 design (n_a, n_e)
            if dimensions == 3:
                # f(x) = a1*x^e1 + offset
                self._model1_design = (1, 1)
            elif dimensions == 5:
                # f(x) = a1*x^e1 + a2*x^e2 + offset
                self._model1_design = (2, 2)
            elif dimensions == 7:
                # f(x) = a1*x^e1 + a2*x^e2 + a3*x^e3 + offset
                self._model1_design = (3, 3)
                
            # set bounds as attributes
            self.lb = np.array(self._model1_design[0]*[c_lb] \
                                 + self._model1_design[1]*[exp_lb] \
                                 + [off_lb])
            self.ub = np.array(self._model1_design[0]*[c_ub] \
                                 + self._model1_design[1]*[exp_ub] \
                                 + [off_ub])

        elif self._model2_design:
            
            # setting model2 design (n_a, n_b, n_c, n_e)
            if dimensions == 3:
                # f(x) = a1*x1 + a2*x2 + offset
                self._model2_design = (2, 0, 0, 0)
            elif dimensions == 4:
                # f(x) = a1*x1 + a2*x2 + b*x1*x2 + offset
                self._model2_design = (2, 1, 0, 0)
            elif dimensions == 6:
                # f(x) = a1*x1^e1 + a2*x2^e2 + b*x1*x2 + offset
                self._model2_design = (2, 1, 0, 2)
            elif dimensions == 9:
                # f(x) = a1*x1^e1 + a2*x2^e2 + b*x1*x2 + (c1*x1 + c2*x2)^e3 + offset
                self._model2_design = (2, 1, 2, 3)
    
            # set bounds as attributes
            self.lb = np.array(self._model2_design[0]*[c_lb] \
                                 + self._model2_design[1]*[c_lb] \
                                 + self._model2_design[2]*[c_lb] \
                                 + self._model2_design[3]*[exp_lb] \
                                 + [off_lb])
            self.ub = np.array(self._model2_design[0]*[c_ub] \
                                 + self._model2_design[1]*[c_ub] \
                                 + self._model2_design[2]*[c_ub] \
                                 + self._model2_design[3]*[exp_ub] \
                                 + [off_ub])

        # add remaining attributes
        self.dimensions = int(dimensions)
        self.fmin = np.nan
        self.xmin = np.full(dimensions, np.nan)
        self.__name__ = f'EmpReg_{problem}_{dimensions}D'

    def _evaluate_model(self, a, plot=False):
        """
        Private function for evaluating a regression model.
        
        Parameters
        ----------
        a : ndarray
            Regression model parameters.
        plot : bool
            If True, plot the regression function.

        Returns
        -------
        fitness: float
            Fitness (RMSE) of the regression model.

        """

        f = self._model_gen(a)

        if plot:
            # plt.figure(figsize=(6, 4), dpi=300)
            plt.plot(self.inputs, self.outputs,
                     'o', ms=2, color='darkgreen', label='data')
            plt.plot(self.inputs, [f(x) for x in self.inputs],
                     linewidth=3, color='violet', label='regression')
            plt.title(self.__name__)
            plt.legend()
            plt.tight_layout()
            # plt.savefig(f'{self.__name__}.png')
            plt.show()

        errs = []
        for x, val in zip(self.inputs, self.outputs):
            errs.append(np.abs(f(x) - val))

        return np.sqrt(np.average(np.array(errs) ** 2))
    
    def _model_gen(self, A):
        """
        Private function for generating regression evaluation function.
        
        Parameters
        ----------
        A : ndarray
            Regression model parameters.

        Returns
        -------
        f : callable
            Regression function.

        """
        
        if self._model1_design:
            n_a, n_e = self._model1_design
            
            # prepare model parameters
            a, e = 1, 1
            
            if n_a > 0:
                a = A[:n_a]
            if n_e > 0:
                e = A[n_a:(n_a+n_e)]
            offset = A[-1]
            
            # f(x) = a1*x1^e1 + a2*x2^e2 + a3*x3^e3 + offset 
            f = lambda x: np.sum(a * x**e) + offset
            
        elif self._model2_design:
            n_a, n_b, n_c, n_e = self._model2_design
        
            # prepare model parameters
            a, b, c, e = 0, 0, 0, np.array([1, 1, 1])
            
            if n_a > 0:
                a = A[:n_a]
            if n_b > 0:
                b = A[n_a:(n_a+n_b)]
            if n_c > 0:
                c = A[(n_a+n_b):(n_a+n_b+n_c)]
            if n_e > 0:
                e[:n_e] = A[(n_a+n_b+n_c):(n_a+n_b+n_c+n_e)]
            offset = A[-1]
            
            # f(x) = a1*x1^e1 + a2*x2^e2 + b*x1*x2 + (c1*x1 + c2*x2)^e3 + offset
            f = lambda x: np.sum(a * x**e[:-1]) + b * np.prod(x) + np.sum(c * x)**e[-1] + offset

        return f


drag2_evals = {3: 1_200,
               4: 2_000,
               6: 3_600,
               9: 2_000}
nylon_evals = {3: 1_200,
               5: 2_500,
               7: 6_000}
rab_evals = {3: 1_200,
             4: 2_000,
             6: 3_000,
             9: 6_000}
empreg_evals = {'drag2': drag2_evals,
                'nylon': nylon_evals,
                'rab': rab_evals}

#### standardized tests
ER_problems_dict_list = []
for case in EmpReg.case_definitions:
    for d in EmpReg.case_definitions[case]:
        problem_dict = {'label': f'ER_{case}_{d}D',
                        'class': EmpReg,
                        'case': case,
                        'dimensions': d,
                        # 'max_evaluations': 100 * d ** 2,
                        'max_evaluations': empreg_evals[case][d],
                        'max_runs': 1000,
                        }
        ER_problems_dict_list.append(problem_dict)


if __name__ == '__main__':

    # import sys
    # sys.path.append('../..')

    """
    # drag2 VALIDATION
    prob = EmpReg(problem='drag2', dimensions=6)
    bounds = [(l, u) for l, u in zip(prob.lb, prob.ub)]
    from scipy.optimize import minimize
    r = minimize(prob, np.ones_like(prob.lb),
                 method='SLSQP', bounds=bounds, options={'maxiter':100000})
    print('validation: ', r.fun, 'should be (close to) 0.072024697\n')
    # drag2 TEST FUNCTIONS
    test_functions = [EmpReg(problem='drag2', dimensions=d) for d in EmpReg.case_definitions['drag2']]
    for f in test_functions:
        x = np.random.uniform(f.lb, f.ub)
        print(f'{f.__name__} \n {f(x)}')
        
    # rab VALIDATION
    prob = EmpReg(problem='rab', dimensions=3)
    bounds = [(l, u) for l, u in zip(prob.lb, prob.ub)]
    from scipy.optimize import minimize
    r = minimize(prob, np.ones_like(prob.lb),
                 method='SLSQP', bounds=bounds, options={'maxiter':100000})
    print('validation: ', r.fun, 'should be (close to) 29.7\n')
    # rab TEST FUNCTIONS
    test_functions = [EmpReg(problem='rab', dimensions=d) for d in EmpReg.case_definitions['rab']]
    for f in test_functions:
        x = np.random.uniform(f.lb, f.ub)
        print(f'{f.__name__} \n {f(x)}')

    # nylon VALIDATION
    prob = EmpReg(problem='nylon', dimensions=7)
    bounds = [(l, u) for l, u in zip(prob.lb, prob.ub)]
    from scipy.optimize import minimize
    r = minimize(prob, np.ones_like(prob.lb),
                 method='SLSQP', bounds=bounds, options={'maxiter':100000})
    print('validation: ', r.fun, 'should be (close to) 7')
    nylon_good_x = [1.53e-05, -0.007268, 1.04, 3, 2, 1, 11.12]
    print('good solution: ', prob(nylon_good_x), '\n')
    
    # nylon TEST FUNCTIONS
    test_functions = [EmpReg(problem='nylon', dimensions=d) for d in EmpReg.case_definitions['nylon']]
    for f in test_functions:
        x = np.random.uniform(f.lb, f.ub)
        print(f'{f.__name__} \n {f(x)}')
    """

    """
    # nylon solution plot
    from indago import minimize
    fun = EmpReg(problem='nylon', dimensions=7)
    print(f'solving {fun.__name__}')
    X, _ = minimize(fun, fun.lb, fun.ub,
                    'DE', variant='LSHADE',
                    max_evaluations=100 * fun.dimensions ** 2)
    print(fun(X, plot=True))
    """

    # """
    import indagobench
    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir,
                                             convergence_window=50, eps_max=0.01, runs_min=100, )
    standard_test.optimizers = indagobench.indagobench25_optimizers
    standard_test.problems = ER_problems_dict_list

    standard_test.run_all()
    # """
