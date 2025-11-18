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

File content: Definition of Multi-Scale Grid Descent optimizer.
Usage: from indago import MSGD

"""
import numpy as np
from ._optimizer import Optimizer, Candidate, Status




class MSGD(Optimizer):
    """Multi-Scale Grid Descent method class.

    Attributes
    ----------
    variant : str
        Name of the MSGD variant. Default (and the only available option): ``Vanilla``.
    params : dict
        A dictionary of MSGD parameters.
    _points : ndarray
        Solution candidates.

    Returns
    -------
    optimizer : MSGD
        MSGD optimizer instance.
    """

    def __init__(self):
        super().__init__()

    def _check_params(self):
        """Private method which performs some MSGD-specific parameter checks
        and prepares the parameters to be validated by Optimizer._check_params.

        Returns
        -------
        None
            Nothing

        """

        if not self.variant:
            self.variant = 'Vanilla'

        defined_params = list(self.params.keys())
        mandatory_params, optional_params = ['divisions', 'base', 'max_scale'], []

        if 'divisions' in self.params:
            assert isinstance(self.params['divisions'], (np.ndarray, np.generic, int) ), \
                "divisions parameter should be positive integer or ndarray"
            assert np.size(self.params['divisions']) == 1 or np.size(self.params['divisions']) == self.dimensions, \
                f"divisions parameter should be array of size {self.dimensions} or 1"
            if np.size(self.params['divisions']) == 1:
                self.params['divisions'] = np.full(self.dimensions, self.params['divisions'], dtype=np.int64)
        else:
            self.params['divisions'] = np.full(self.dimensions, 10, dtype=np.int64)
        defined_params += 'divisions'.split()

        if 'base' in self.params:
            assert isinstance(self.params['base'], (int,) ), \
                "base parameter should be positive integer"
        else:
            self.params['base'] = 4
        defined_params += 'base'.split()

        if 'max_scale' in self.params:
            assert isinstance(self.params['max_scale'], (int,) ), \
                "max_scale parameter should be positive integer"
        else:
            self.params['max_scale'] = 15
        defined_params += 'max_scale'.split()

        # if 'trials' in self.params:
        #     assert isinstance(self.params['trials'], (int,) ), \
        #         "trials parameter should be positive integer"
        # else:
        #     self.params['trials'] = 5
        # defined_params += 'trials'.split()

        # if 'init_trials' in self.params:
        #     assert isinstance(self.params['init_trials'], (int,) ), \
        #         "init_trials parameter should be positive integer"
        # else:
        #     self.params['init_trials'] = self.dimensions

        if self.variant == 'Vanilla':
            pass

        else:
            assert False, f'Unknown variant! {self.variant}'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)

    def _init_method(self):
        """Private method for initializing the MSGD optimizer instance.
        Initializes and evaluates optimizer.max_evaluations number of candidates.

        Returns
        -------
        None
            Nothing

        """

        self._evaluate_initial_candidates()

        self._rescale(0)
        self._z = np.random.randint(self.params['divisions'] + 1, size=self.dimensions)

        self._evaluate_z(self._z)
        self._z_best = self._z.copy()

        self._finalize_iteration()

    def _evaluate_z(self, z):
        """Private method that evaluates integer candidate or list of integer candidates.
        It transforms integer coordinates into real (float) coordinates with respect to
        the grid for current scale.

        Parameters
        ----------
        z : ndarray int
            A list of candidates represented by ndarray of integers.

        Returns
        -------
        candidates : list of Candidate
            A list of Candidate instances with set results (O, C and f) attributes.
        """

        assert np.ndim(z) in [1, 2], 'Unexpected dimensions for argument z'
        if np.ndim(z) == 1:
            z = np.reshape(z, (1, self.dimensions))

        candidates = []
        for i in range(z.shape[0]):
            if tuple(z[i, :]) in self._calc_history.keys():
                c = self._calc_history[tuple(z[i, :])]
            else:
                x = self.lb + (self.ub - self.lb) * z[i, :] / self._m
                x[z[i, :] == 0] = self.lb[z[i, :] == 0]
                x[z[i, :] == self._m] = self.lb[z[i, :] == self._m]
                c = Candidate(self)
                c.X = x
                candidates.append(c)

        best_exist = self.best is not None
        if best_exist:
            c_old = self.best.copy()

        self._collective_evaluation(candidates)

        if best_exist:
            for i, c in enumerate(candidates):
                # self._log(f'   !eval {c.X=} ({z[i, :]}) {c.f=}')
                if c < c_old:
                    self._z_best = z[i, :].copy()

        if len(candidates) == 1:
            return candidates[0]
        return candidates

    def _rescale(self, scale=None):
        """Private method for rescaling the grid over the search domain. The calculation history is
        deleted after each rescale.

        Parameters
        ----------
        scale : int or None
            Scale used for making m equidistant grid divisions, where m = m0 * base ** scale.

        Returns
        -------
        None
            Nothing.
        """
        if scale is not None:
            self._scale = scale
        self._m = self.params['divisions'] * self.params['base'] ** self._scale
        self._calc_history = {}
        self._log(f'_rescale, {self._scale=}, {self._m=}')
        # input('Press Enter to continue...')

    def _find_gradient(self, _z):
        """Private method for determining the gradient using full finite difference stencil
        (central + 2 points per dimension) on a current grid.

        Parameters
        ----------
        _z : ndarray[int]
            Integer coordinates of the central point.

        Returns
        -------
        dz : ndarray[int]
            Approximated integer gradient (contains only -1, 0 and 1 values).
        df : ndarray[float]
            Relative (to central point f) fitnesses in directions dz.
        """
        z_fwd = np.full([self.dimensions, self.dimensions], -10, dtype=np.int64)
        z_bck = np.full([self.dimensions, self.dimensions], -10, dtype=np.int64)
        fwd_valid_msk = np.full([self.dimensions], False, dtype=bool)
        bck_valid_msk = np.full([self.dimensions], False, dtype=bool)
        for i_dim in range(self.dimensions):

            for dir in [-1, +1]:
                dz = np.zeros(self.dimensions, dtype=np.int64)
                dz[i_dim] = dir
                z_i = _z + dz

                if dir < 0 and z_i[i_dim] > 0:
                    z_bck[i_dim, :] = z_i
                    bck_valid_msk[i_dim] = True
                if dir > 0 and z_i[i_dim] < self._m[i_dim] + 1:
                    z_fwd[i_dim, :] = z_i
                    fwd_valid_msk[i_dim] = True

        z_bck_stencil = z_bck[bck_valid_msk]
        z_fwd_stencil = z_fwd[fwd_valid_msk]
        z_all = np.append(z_bck_stencil, z_fwd_stencil, axis=0)
        # self._log(f'{bck_valid_msk.shape=},'
        #           f'{z_bck_stencil.shape=},'
        #           f' {z_fwd_stencil.shape=},'
        #           f'{fwd_valid_msk.shape=}'
        #           f' {z_all.shape=}')
        z_all = np.append(z_all, [_z], axis=0)

        x_stencil = self._evaluate_z(z_all)

        f = np.array([x.f for x in x_stencil], dtype=float)
        f_bck = np.full(self.dimensions, np.nan, dtype=float)
        f_fwd = np.full(self.dimensions, np.nan, dtype=float)
        # self._log(f'{bck_valid_msk.shape=}, {fwd_valid_msk.shape=}, {f.shape=}')
        f_bck[bck_valid_msk] = f[:z_bck_stencil.shape[0]]
        f_fwd[fwd_valid_msk] = f[z_bck_stencil.shape[0]:-1]
        f0 = f[-1]

        df = np.full(self.dimensions, np.nan, dtype=float)
        for i_dim in range(self.dimensions):
            f_stencil = np.array([f_bck[i_dim], f0, f_fwd[i_dim]])
            dz[i_dim] = np.nanargmin(f_stencil) - 1

            dz[i_dim] = 0
            if f_bck[i_dim] < f0:
                dz[i_dim] = -1
            if f_fwd[i_dim] < f0:
                dz[i_dim] = +1
            df[i_dim] = np.nanmin(f_stencil) - f_stencil[1]

        # self._log(f'Finding gradient at {_z=}'
        #           f'    {dz=}\n'
        #           f'    {df=}')
        return dz, df

    def _descent(self):
        """Private method for iteratively performing the grid descent from the best point.
        Descent happens until converges to a zero gradient point and hence can't continue
        the descent.

        Returns
        -------
        z : ndarray[int]
            Integer coordinates of the last point of the descent.
        """
        z = self._z_best.copy()
        # z = z0.copy()
        c0 = self.best.copy()

        while True:
            dz, df = self._find_gradient(z)

            if np.all(dz == 0):
                return z

            n_trials = np.min([self.dimensions // 2, np.count_nonzero(dz != 0)])
            # self._log(f'{n_trials=}')
            z_trial, dy = [], []

            for i in range(n_trials):
                w = np.abs(df) / np.max(np.abs(df))
                _dy = dz * (np.round((i + 1) * w)).astype(np.int64)
                # self._log(f' trial {_dy=}')
                _z = z + _dy
                # self._log(f'{_z=}')
                # self._log(f'{(_z >= 0)=}')
                # self._log(f'{(_z <= self._m )=}')
                if np.all(_z >= 0) and np.all(_z <= self._m):
                    z_trial.append(_z)
                    dy.append(_dy)

            if len(z_trial) > 0:
                trial_candidates = np.reshape(self._evaluate_z(np.array(z_trial)), -1)
                # f_trial = np.array([p.f for p in trial_candidates], dtype=float)

                i_best = np.argmin(trial_candidates)
                if trial_candidates[i_best] < c0:
                    # dz = z_trial[i_best] - self._z
                    z = z_trial[i_best].copy()
                    c0 = trial_candidates[i_best].copy()
                else:
                    return z
            else:
                # dz = np.zeros(self.dimensions, dtype=np.int64)
                self._log('   No feasible trial points')
                self._err_msg = 'NO FEASIBLE TRIAL POINTS'

            if self._finalize_iteration():
                return z

    def _run(self):
        """Run procedure for the MSGD method.

        Returns
        -------
        optimum: Candidate
            Best solution found during the MSGD optimization.
        """

        self._check_params()

        if self.status == Status.RESUMED:
            if self._stopping_criteria():
                return self.best
            # TODO inspect why this is necessary for resume to work:
            self.it += 1
        else:
            self._init_method()

        for self._scale in range(self.params['max_scale']):

            self._rescale()
            if self._scale > 0:
                self._z_best *= self.params['base']
                self._z = self._z_best.copy()

            while True:
                z = self._descent()
                # self._log(f'{z - self._z_best=}')
                if np.all(z == self._z_best):
                    # print('z == self._z_best')
                    # print('Press Enter to continue...')
                    break

            if self._finalize_iteration():
                break
        else:
            self.status = Status.FINISHED
            status_str = f'{Status.FINISHED.value}: maximum refinement scale reached ({self._scale:d}).'
            self._log(status_str)
            # print('quiting MSGD because max_scale reached')


        return self.best
