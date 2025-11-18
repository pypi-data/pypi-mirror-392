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

File content: Definition of Escape optimizer.
Usage: from indago import ESC

"""


import numpy as np
from ._optimizer import Optimizer, Candidate, Status


class ESC(Optimizer):
    """Escape method class.
    
    Attributes
    ----------
    variant : str
        Name of the Escape variant. Default (and the only available option): ``Vanilla``.
    params : dict
        A dictionary of Escape parameters.
    _points : ndarray
        Solution candidates.
        
    Returns
    -------
    optimizer : ESC
        ESC optimizer instance.
    """
    

    def __init__(self):
        super().__init__()


    def _check_params(self):
        """Private method which performs some RS-specific parameter checks
        and prepares the parameters to be validated by Optimizer._check_params.

        Returns
        -------
        None
            Nothing
            
        """

        if not self.variant:
            self.variant = 'Vanilla'

        defined_params = list(self.params.keys())
        mandatory_params = ['population_size',
                            'elite_size',
                            'beta_base',
                            'mask_probability']
        optional_params = []
        
        if 'population_size' in self.params:
            self.params['population_size'] = int(self.params['population_size'])
            assert self.params['population_size'] > 0, \
                "population_size parameter should be positive integer"
        else:
            self.params['population_size'] = max(10, self.dimensions)
            defined_params += 'population_size'.split()

        if 'elite_size' in self.params:
            self.params['elite_size'] = int(self.params['elite_size'])
            assert self.params['elite_size'] > 0, \
                "elite_size parameter should be positive integer"
        else:
            self.params['elite_size'] = 5 # max(self.dimensions)
            defined_params += 'elite_size'.split()

        if 'beta_base' in self.params:
            self.params['beta_base'] = float(self.params['beta_base'])
            assert self.params['beta_base'] > 0, \
                "beta_base parameter should be positive number"
        else:
            self.params['beta_base'] = 1.5
            defined_params += 'beta_base'.split()

        if 'mask_probability' in self.params:
            self.params['mask_probability'] = float(self.params['mask_probability'])
            assert 0 <= self.params['mask_probability'] <= 1, \
                "mask_probability parameter should be in range [0, 1]"
        else:
            self.params['mask_probability'] = 0.5
            defined_params += 'mask_probability'.split()

        if self.variant == 'Vanilla':
            pass
    
        else:
            assert False, f'Unknown variant! {self.variant}'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)


    def _init_method(self):
        """Private method for initializing the ESC optimizer instance.
        Initializes and evaluates optimizer.max_evaluations number of candidates.

        Returns
        -------
        None
            Nothing
            
        """
        
        self._evaluate_initial_candidates()

        # Generate all candidates
        n0 = 0 if self._initial_candidates is None else self._initial_candidates.size
        self._population = np.array([Candidate(self) for _ in range(self.params['population_size'])], dtype=Candidate)
        self._initialize_X(self._population[n0:])
        
        # Using specified particles initial positions
        for p in range(np.size(self._population)):
            if p < n0:
                self._population[p] = self._initial_candidates[p].copy()
            
        # Evaluate
        if n0 < self.params['population_size']:
            self._collective_evaluation(self._population[n0:])

        # if all candidates are NaNs
        if np.isnan([point.f for point in self._population]).all():
            self._err_msg = 'ALL CANDIDATES FAILED TO EVALUATE'

        self._finalize_iteration()
    
        
    def _run(self):
        """Run procedure for the ESC method.

        Returns
        -------
        optimum: Candidate
            Best solution found during the ESC optimization.
            
        """

        self._check_params()

        if self.status == Status.RESUMED:
            if self._stopping_criteria():
                return self.best
            # TODO inspect why this is necessary for resume to work:
            self.it += 1
        else:
            self._init_method()

        while True:

            panic_index = np.cos(np.pi / 6 * self._progress_factor())
            self._population = np.sort(self._population)
            calm_count = int(round(0.15 * self.params['population_size']))
            conform_count = int(round(0.35 * self.params['population_size']))
            calm_X = np.array([c.X for c in self._population[:calm_count]])
            conform_X = np.array([c.X for c in self._population[calm_count:calm_count + conform_count]])
            panic_X = np.array([c.X for c in self._population[calm_count + conform_count:]])
            calm_center = np.mean(calm_X, axis=0)

            new_population = self._population.copy()

            for i, individual in enumerate(self._population):

                if self._progress_factor() <= 0.5:
                    if i < calm_count:
                        mask1 = np.random.rand(self.dimensions) > self.params['mask_probability']
                        weight_vector1 = self._adaptive_levy_weight()
                        random_position = np.min(calm_X, axis=0) + np.random.rand(self.dimensions) * (
                                np.max(calm_X, axis=0) - np.min(calm_X, axis=0))
                        new_population[i].X += mask1 * (weight_vector1 * (calm_center - self._population[i].X) +
                                                         (random_position - self._population[i].X + np.random.randn(
                                                             self.dimensions) / 50)) * panic_index
                    elif i < calm_count + conform_count:
                        mask1 = np.random.rand(self.dimensions) > self.params['mask_probability']
                        mask2 = np.random.rand(self.dimensions) > self.params['mask_probability']
                        weight_vector1 = self._adaptive_levy_weight()
                        weight_vector2 = self._adaptive_levy_weight()
                        random_position = np.min(conform_X, axis=0) + np.random.rand(self.dimensions) * (
                                np.max(conform_X, axis=0) - np.min(conform_X, axis=0))
                        panic_individual = panic_X[np.random.randint(panic_X.shape[0])] if panic_X.size > 0 \
                            else np.zeros(self.dimensions)
                        new_population[i].X += mask1 * (weight_vector1 * (calm_center - self._population[i].X) +
                                                         mask2 * weight_vector2 * (
                                                                     panic_individual - self._population[i].X) +
                                                         (random_position - self._population[i].X + np.random.randn(
                                                             self.dimensions) / 50) * panic_index)
                    else:
                        mask1 = np.random.rand(self.dimensions) > self.params['mask_probability']
                        mask2 = np.random.rand(self.dimensions) > self.params['mask_probability']
                        weight_vector1 = self._adaptive_levy_weight()
                        weight_vector2 = self._adaptive_levy_weight()
                        elite = np.random.choice(self._population[:self.params['elite_size']])
                        random_individual = np.random.choice(self._population)
                        random_position = elite.X + weight_vector1 * (random_individual.X - elite.X)
                        new_population[i].X += mask1 * (weight_vector1 * (elite.X - self._population[i].X) +
                                                         mask2 * weight_vector2 * (
                                                                     random_individual.X - self._population[i].X) +
                                                         (random_position - self._population[i].X + np.random.randn(
                                                             self.dimensions) / 50) * panic_index)
                else:
                    mask1 = np.random.rand(self.dimensions) > self.params['mask_probability']
                    mask2 = np.random.rand(self.dimensions) > self.params['mask_probability']
                    weight_vector1 = self._adaptive_levy_weight()
                    weight_vector2 = self._adaptive_levy_weight()
                    elite = np.random.choice(self._population[:self.params['elite_size']])
                    random_individual = np.random.choice(self._population)
                    new_population[i].X += mask1 * weight_vector1 * (elite.X - self._population[i].X) + \
                                            mask2 * weight_vector2 * (random_individual.X - self._population[i].X)

                new_population[i].clip(self)

            self._collective_evaluation(new_population)

            # Replace individuals with better fitness
            for i, (old, new) in enumerate(zip(self._population, new_population)):
                if old.f < new.f:
                    self._population[i] = new.copy()

            if self._finalize_iteration():
                break

        return self.best


    def _adaptive_levy_weight(self):
        beta = self.params['beta_base'] + 0.5 * np.sin(np.pi / 2 * self._progress_factor())
        beta = np.clip(beta, 0.1, 2)
        sigma = (np.math.gamma(1 + beta) * np.sin(np.pi * beta / 2) /
                 (np.math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
        u = np.random.normal(0, sigma, self.dimensions)
        v = np.random.normal(0, 1, self.dimensions)
        w = np.abs(u / np.abs(v) ** (1 / beta))
        return w / (np.max(w) + np.finfo(float).eps)