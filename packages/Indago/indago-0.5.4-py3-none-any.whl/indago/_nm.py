#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Indago
Python framework for numerical optimization
https://indago.readthedocs.io/
https://pypi.org/project/Indago/

Description: Indago contains several modern methods for real fitness function optimization over a real parameter domain
and supports multiple objectives and constraints. It was developed at the University of Rijeka, Faculty of Engineering.
Authors: Stefan Ivić, Siniša Družeta, Luka Grbčić
Contact: stefan.ivic@riteh.uniri.hr
License: MIT

File content: Definition of Nelder-Mead (NM).
Usage: from indago import NM

"""


from ._optimizer import Optimizer, Candidate, Status
import numpy as np


class NM(Optimizer):
    """Nelder-Mead method class.
    
    Reference: Gao, F., Han, L. Implementing the Nelder-Mead simplex algorithm 
    with adaptive parameters. Comput Optim Appl 51, 259–277 (2012). 
    https://doi.org/10.1007/s10589-010-9329-3

    Attributes
    ----------
    variant : str
        Name of the NM variant (``Vanilla`` or ``GaoHan``). Default: ``GaoHan``.
    X0 : ???
        ???
    _candidates : ndarray
        Array of Candidate instances.
    
    Returns
    -------
    optimizer : NM
        Nelder-Mead optimizer instance.

    """

    def __init__(self):
        super().__init__()

        self.X0 = 1


    def _check_params(self):
        """Private method which prepares the parameters to be validated by Optimizer._check_params.

        Returns
        -------
        None
            Nothing
            
        """

        if not self.variant:
            self.variant = 'GaoHan'

        defined_params = list(self.params.keys())
        mandatory_params, optional_params = [], []

        if self.variant == 'Vanilla':         
            mandatory_params = 'init_step alpha gamma rho sigma'.split()
            if 'init_step' not in self.params:
                self.params['init_step'] = 0.4
                defined_params += 'init_step'.split()
            if 'alpha' not in self.params:
                self.params['alpha'] = 1.0
                defined_params += 'alpha'.split()                
            if 'gamma' not in self.params:
                self.params['gamma'] = 2.0
                defined_params += 'gamma'.split()
            if 'rho' not in self.params:
                self.params['rho'] = 0.5
                defined_params += 'rho'.split()
            if 'sigma' not in self.params:
                self.params['sigma'] = 0.5
                defined_params += 'sigma'.split()
        elif self.variant == 'GaoHan':
            mandatory_params = 'init_step'.split()
            if 'init_step' not in self.params:
                self.params['init_step'] = 0.4
                defined_params += 'init_step'.split()

        else:
            assert False, f'Unknown variant! {self.variant}'

        for param in mandatory_params:
            # if param not in defined_params:
            #    print('Missing parameter (%s)' % param)
            assert param in defined_params, f'Missing parameter {param}'

        for param in defined_params:
            if param not in mandatory_params and param not in optional_params:
                self._log(f'Warning: Excessive parameter {param}')

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)

    def _init_method(self):
        """Private method for initializing the NelderMead optimizer instance.
        Evaluates given initial candidates, selects starting point, constructs initial polytope/simplex.

        Returns
        -------
        None
            Nothing
            
        """

        self._evaluate_initial_candidates()
        
        # Generate set of points
        self._candidates = np.array([Candidate(self) for _ in range(self.dimensions + 1)], \
                            dtype=Candidate)

        # Generate initial positions
        self._candidates[0] = self._initial_candidates[0].copy()

        for p in range(1, self.dimensions + 1):

            # Random position
            dx = np.zeros([self.dimensions])
            dx[p - 1] = self.params['init_step']
            self._candidates[p].X = self._candidates[0].X + dx * (self.ub - self.lb)
            self._candidates[p].X = np.clip(self._candidates[p].X, self.lb, self.ub)

        # Evaluate
        self._collective_evaluation(self._candidates[1:])
        
        # if all candidates are NaNs       
        if np.isnan([c.f for c in self._candidates]).all():
            self._err_msg = 'ALL CANDIDATES FAILED TO EVALUATE'
        
        self._finalize_iteration()

    def _run(self):
        """Main loop of NelderMead method.

        Returns
        -------
        optimum: Candidate
            Best solution found during the NelderMead optimization.
            
        """

        self._check_params()

        if self.status == Status.RESUMED:
            if self._stopping_criteria():
                return self.best
            # TODO inspect why this is necessary for resume to work:
            self.it += 1
        else:
            self._init_method()
        
        # Prepare parameters
        if self.variant == 'Vanilla':
            alpha = self.params['alpha']
            gamma = self.params['gamma']
            rho = self.params['rho']
            sigma = self.params['sigma']
        elif self.variant == 'GaoHan':
            alpha = 1.0
            gamma = 1 + 2 / self.dimensions
            rho = 0.75 - 1 / 2 / self.dimensions
            sigma = 1 - 1 / self.dimensions

        while True:
            self._candidates = np.sort(self._candidates, kind='stable')
            reduction = False

            self._progress_log()

            # # Check stopping conditions
            # if self._stopping_criteria():
            #     break

            # Center
            X0 = np.zeros(self.dimensions)
            for p in range(self.dimensions):
                X0 += self._candidates[p].X
            X0 /= self.dimensions

            dX = X0 - self._candidates[-1].X

            # Reflection
            Xr = X0 + alpha * dX
            Xr = np.clip(Xr, self.lb, self.ub)
            cR = Candidate(self)
            cR.X = Xr

            self._collective_evaluation([cR])

            if self._candidates[0] <= cR <= self._candidates[-2]:
                self._candidates[-1] = cR.copy()

            elif cR < self._candidates[0]:
                # Expansion
                Xe = X0 + gamma * dX
                Xe = np.clip(Xe, self.lb, self.ub)
                cE = Candidate(self)
                cE.X = Xe

                self._collective_evaluation([cE])

                if cE < cR:
                    self._candidates[-1] = cE.copy()
                else:
                    self._candidates[-1] = cR.copy()

            elif cR < self._candidates[-1]:
                # Contraction
                Xc = X0 + rho * dX
                Xc = np.clip(Xc, self.lb, self.ub)
                cC = Candidate(self)
                cC.X = Xc

                self._collective_evaluation([cC])

                if cC < self._candidates[-1]:
                    self._candidates[-1] = cC.copy()
                else:
                    reduction = True

            else:
                # Internal contraction
                Xc = X0 - rho * dX
                Xc = np.clip(Xc, self.lb, self.ub)
                cC = Candidate(self)
                cC.X = Xc

                self._collective_evaluation([cC])

                if cC < self._candidates[-1]:
                    self._candidates[-1] = cC.copy()
                else:
                    reduction = True

            # Reduction
            if reduction:
                for p in range(1, self.dimensions + 1):
                    self._candidates[p].X = self._candidates[0].X + sigma * (self._candidates[p].X - self._candidates[0].X)
                    # self._candidates[p].evaluate()
                self._collective_evaluation(self._candidates[1:])

            if self._finalize_iteration():
                break

        return self.best

