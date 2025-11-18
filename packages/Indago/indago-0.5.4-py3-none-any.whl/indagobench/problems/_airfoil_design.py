#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Airfoil Design

@author: luka, sinisa
"""

import numpy as np
import shutil, os
import random
import string
import subprocess
import warnings
import time

try:
    import scipy.interpolate as interp
    import matplotlib.pyplot as plt
    from indagobench._local_paths import xfoil_tmp_dir, xfoil_binary_path

except ImportError as e:
    print('\033[91m' + f'Failed at importing optional module: {e.msg}')
    print('Code will continue but evaluation using PP class is not possible.' + '\033[0m')




class AirfoilDesign:
    """Airfoil Design test suite class.

    Problem definitions and evaluation criteria for the airfoil design problems
    (single objective).

    Parameters
    ----------
    problem : str
        Name of the test function. Required initialization parameter.
    dimensions : int or None
        Dimensionality of the test functions. ``None`` allowed for problems with
        fixed dimensionality.

    Attributes
    ----------
    case_definitions : dict
        Dict of problem names (key) and corresponding available dimensions (value).
    _prepare_xfoil_process : callable
        Private function for preparing xfoil process with the prepared input data.
    _xfoil_run_inverse : callable
        Private function for conducting a run of xfoil for the inverse problem.
    _xfoil_run_design : callable
        Private function for conducting a run of xfoil for the design problem.
    _baseinverse, _inverseflow, _design3 : callable
        Private evaluation functions corresponding to airfoil design problems.
    _eval_fail_fitness : float
        Fitness value returned for failed evaluation.
    AOA : float
        Angle of attack problem parameter for problems where it is fixed.
    Re : float
        Reynolds number problem parameter for problems where it is fixed.
    _os_name : str
        Operating system name.
    _k : int
        Spline interpolation parameter.
    _target_cp : ndarray
        Target cp values.
    _spl1 : ndarray
        Upper spline interpolation definition.
    _spl2 : ndarray
        Lower spline interpolation definition.
    _x_interp : ndarray
        Linearly distributed values for interpolation.
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
    fitness : float
        Fitness of the produced evaluation function.

    """

    case_definitions = {'inv3': [32],
                        'inv2': [32],
                        'inv3flow': [34],
                        'inv2flow': [34],
                        'design3': [3],
                        }

    def __call__(self, x, *args, **kwargs):
        """
        A method that enables an AirfoilDesign instance to be callable. Evaluates 
        AirfoilDesign._f_call that is set in AirfoilDesign.__init__ to point to
        the appropriate AirfoilDesign function.
        """

        return self._f_call(x, *args, **kwargs)

    def __init__(self, problem, dimensions=None, instance_label=None):
        """Initialize case"""

        self._f_call = None

        assert problem in self.case_definitions, \
            f'Problem {problem} not defined in AirfoilDesign problem class'

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

        # (re)create temp dir
        # shutil.rmtree(xfoil_tmp_dir, ignore_errors=True)  # delete temp dir (not a good idea in parallel evaluation)
        if not os.path.exists(xfoil_tmp_dir):
            os.mkdir(xfoil_tmp_dir)

        self._os_name = os.name

        if problem == 'inv3':

            # problem parameters
            self._eval_fail_fitness = 10
            velocity = 30
            self.AOA = 4
            bound_factor = 3  # increase the lower and upper bounds based on a symmetrical airfoil
            base_airfoil_file = 'airfoil_data/naca0012_nasa.dat'

            # derived parameters
            self.Re = int(np.round(velocity / 1e-5))  # Reynolds number calculation

            # spline parameters
            self._k = 5
            s = 1e-2

            # load data
            target_x, self._target_cp = np.loadtxt(f'{os.path.dirname(os.path.abspath(__file__))}/airfoil_data/naca2410_cp_target.txt', unpack=True)
            fname = f'{base_airfoil_file}'
            airfoil_file = np.loadtxt(f'{os.path.dirname(os.path.abspath(__file__))}/{base_airfoil_file}')
            mid = int(len(airfoil_file) / 2)

            # check airfoil type
            if 'nasa' in fname:
                # print('NASA format!')
                lower_x = airfoil_file[:mid][::-1][:, 0]
                upper_x = airfoil_file[mid:][:, 0]
                lower_y = airfoil_file[:mid][::-1][:, 1] * bound_factor
                upper_y = airfoil_file[mid:][:, 1] * bound_factor
            else:
                # print('Airfoiltools format!')
                upper_x = airfoil_file[:mid][::-1][:, 0]
                lower_x = airfoil_file[mid:][:, 0]
                upper_y = airfoil_file[:mid][::-1][:, 1] * bound_factor
                lower_y = airfoil_file[mid:][:, 1] * bound_factor

            # spline
            self._spl1 = interp.splrep(upper_x, upper_y, k=self._k, s=s)
            self._spl2 = interp.splrep(lower_x, lower_y, k=self._k, s=s)

            # prepare bounds
            lb = self._spl2[1]
            ub = self._spl1[1]

            indx_low = np.where(lb == 0)[0]
            indx_upper = np.where(ub == 0)[0]

            lb[indx_low] = lb[indx_low] - 1e-9
            ub[indx_upper] = ub[indx_upper] + 1e-9

            r = min(len(lb), len(ub))

            for i in range(r):
                if ub[i] < lb[i]:
                    ub[i] = 1e-9
                    lb[i] = -1e-9

            len_ub, len_lb = len(ub), len(lb)
            lb = np.hstack((np.ones(len_ub) * -1e-9, lb))
            ub = np.hstack((ub, np.ones(len_lb) * 1e-9))

            self._x_interp = np.linspace(0, 1, 200)

            self._f_call = self._baseinverse

            self.lb = lb
            self.ub = ub
            self.fmin = np.nan
            self.xmin = np.full(dimensions, np.nan)

        elif problem == 'inv2':

            # problem parameters
            self._eval_fail_fitness = 10
            velocity = 30
            self.AOA = 4
            bound_factor = 2  # increase the lower and upper bounds based on a symmetrical airfoil
            base_airfoil_file = 'airfoil_data/naca0012_nasa.dat'

            # derived parameters
            self.Re = int(np.round(velocity / 1e-5))  # Reynolds number calculation

            # spline parameters
            self._k = 5
            s = 2e-3

            # load data
            target_x, self._target_cp = np.loadtxt(f'{os.path.dirname(os.path.abspath(__file__))}/airfoil_data/naca2410_cp_target.txt', unpack=True)
            fname = f'{base_airfoil_file}'
            airfoil_file = np.loadtxt(f'{os.path.dirname(os.path.abspath(__file__))}/{base_airfoil_file}')
            mid = int(len(airfoil_file) / 2)

            # check airfoil type
            if 'nasa' in fname:
                # print('NASA format!')
                lower_x = airfoil_file[:mid][::-1][:, 0]
                upper_x = airfoil_file[mid:][:, 0]
                lower_y = airfoil_file[:mid][::-1][:, 1] * bound_factor
                upper_y = airfoil_file[mid:][:, 1] * bound_factor
            else:
                # print('Airfoiltools format!')
                upper_x = airfoil_file[:mid][::-1][:, 0]
                lower_x = airfoil_file[mid:][:, 0]
                upper_y = airfoil_file[:mid][::-1][:, 1] * bound_factor
                lower_y = airfoil_file[mid:][:, 1] * bound_factor

            # spline
            self._spl1 = interp.splrep(upper_x, upper_y, k=self._k, s=s)
            self._spl2 = interp.splrep(lower_x, lower_y, k=self._k, s=s)

            # prepare bounds
            lb = self._spl2[1]
            ub = self._spl1[1]

            indx_low = np.where(lb == 0)[0]
            indx_upper = np.where(ub == 0)[0]

            lb[indx_low] = lb[indx_low] - 1e-9
            ub[indx_upper] = ub[indx_upper] + 1e-9

            r = min(len(lb), len(ub))

            for i in range(r):
                if ub[i] < lb[i]:
                    ub[i] = 1e-9
                    lb[i] = -1e-9

            len_ub, len_lb = len(ub), len(lb)
            lb = np.hstack((np.ones(len_ub) * -1e-9, lb))
            ub = np.hstack((ub, np.ones(len_lb) * 1e-9))

            self._x_interp = np.linspace(0, 1, 200)

            self._f_call = self._baseinverse

            self.lb = lb
            self.ub = ub
            self.fmin = np.nan
            self.xmin = np.full(dimensions, np.nan)

        elif problem == 'inv3flow':

            # problem parameters
            self._eval_fail_fitness = 10
            bound_factor = 3  # increase the lower and upper bounds based on a symmetrical airfoil
            base_airfoil_file = 'airfoil_data/naca0012_nasa.dat'
            AOA_bounds = [1, 10]
            velocity_bounds = [10, 50]

            # spline parameters
            self._k = 5
            s = 1e-2

            # load data
            target_x, self._target_cp = np.loadtxt(f'{os.path.dirname(os.path.abspath(__file__))}/airfoil_data/naca2410_cp_target.txt', unpack=True)
            fname = f'{base_airfoil_file}'
            airfoil_file = np.loadtxt(f'{os.path.dirname(os.path.abspath(__file__))}/{base_airfoil_file}')
            mid = int(len(airfoil_file) / 2)

            # check airfoil type
            if 'nasa' in fname:
                # print('NASA format!')
                lower_x = airfoil_file[:mid][::-1][:, 0]
                upper_x = airfoil_file[mid:][:, 0]
                lower_y = airfoil_file[:mid][::-1][:, 1] * bound_factor
                upper_y = airfoil_file[mid:][:, 1] * bound_factor
            else:
                # print('Airfoiltools format!')
                upper_x = airfoil_file[:mid][::-1][:, 0]
                lower_x = airfoil_file[mid:][:, 0]
                upper_y = airfoil_file[:mid][::-1][:, 1] * bound_factor
                lower_y = airfoil_file[mid:][:, 1] * bound_factor

            # spline
            self._spl1 = interp.splrep(upper_x, upper_y, k=self._k, s=s)
            self._spl2 = interp.splrep(lower_x, lower_y, k=self._k, s=s)

            # prepare bounds
            lb = self._spl2[1]
            ub = self._spl1[1]

            indx_low = np.where(lb == 0)[0]
            indx_upper = np.where(ub == 0)[0]

            lb[indx_low] = lb[indx_low] - 1e-9
            ub[indx_upper] = ub[indx_upper] + 1e-9

            r = min(len(lb), len(ub))

            for i in range(r):
                if ub[i] < lb[i]:
                    ub[i] = 1e-9
                    lb[i] = -1e-9

            len_ub, len_lb = len(ub), len(lb)
            lb = np.hstack((np.ones(len_ub) * -1e-9, lb))
            ub = np.hstack((ub, np.ones(len_lb) * 1e-9))

            self._x_interp = np.linspace(0, 1, 200)

            self._f_call = self._inverseflow

            self.lb = np.append([AOA_bounds[0], velocity_bounds[0]], lb)
            self.ub = np.append([AOA_bounds[1], velocity_bounds[1]], ub)
            self.fmin = np.nan
            self.xmin = np.full(dimensions, np.nan)
            self.xmin[0], self.xmin[1] = 4, 30

        elif problem == 'inv2flow':

            # problem parameters
            self._eval_fail_fitness = 10
            bound_factor = 2  # increase the lower and upper bounds based on a symmetrical airfoil
            base_airfoil_file = f'naca0012_nasa.dat'
            AOA_bounds = [1, 10]
            velocity_bounds = [10, 50]

            # spline parameters
            self._k = 5
            s = 2e-3

            # load data
            target_x, self._target_cp = np.loadtxt(f'{os.path.dirname(os.path.abspath(__file__))}/airfoil_data/naca2410_cp_target.txt', unpack=True)
            # fname = f'{base_airfoil_file}'
            airfoil_file = np.loadtxt(f'{os.path.dirname(os.path.abspath(__file__))}/airfoil_data/{base_airfoil_file}')
            mid = int(len(airfoil_file) / 2)

            # check airfoil type
            if 'nasa' in base_airfoil_file:
                # print('NASA format!')
                lower_x = airfoil_file[:mid][::-1][:, 0]
                upper_x = airfoil_file[mid:][:, 0]
                lower_y = airfoil_file[:mid][::-1][:, 1] * bound_factor
                upper_y = airfoil_file[mid:][:, 1] * bound_factor
            else:
                # print('Airfoiltools format!')
                upper_x = airfoil_file[:mid][::-1][:, 0]
                lower_x = airfoil_file[mid:][:, 0]
                upper_y = airfoil_file[:mid][::-1][:, 1] * bound_factor
                lower_y = airfoil_file[mid:][:, 1] * bound_factor

            # spline
            self._spl1 = interp.splrep(upper_x, upper_y, k=self._k, s=s)
            self._spl2 = interp.splrep(lower_x, lower_y, k=self._k, s=s)

            # prepare bounds
            lb = self._spl2[1]
            ub = self._spl1[1]

            indx_low = np.where(lb == 0)[0]
            indx_upper = np.where(ub == 0)[0]

            lb[indx_low] = lb[indx_low] - 1e-9
            ub[indx_upper] = ub[indx_upper] + 1e-9

            r = min(len(lb), len(ub))

            for i in range(r):
                if ub[i] < lb[i]:
                    ub[i] = 1e-9
                    lb[i] = -1e-9

            len_ub, len_lb = len(ub), len(lb)
            lb = np.hstack((np.ones(len_ub) * -1e-9, lb))
            ub = np.hstack((ub, np.ones(len_lb) * 1e-9))

            self._x_interp = np.linspace(0, 1, 200)

            self._f_call = self._inverseflow

            self.lb = np.append([AOA_bounds[0], velocity_bounds[0]], lb)
            self.ub = np.append([AOA_bounds[1], velocity_bounds[1]], ub)
            self.fmin = np.nan
            self.xmin = np.full(dimensions, np.nan)
            self.xmin[0], self.xmin[1] = 4, 30

        elif problem == 'design3':

            # problem parameters
            self._eval_fail_fitness = 10
            velocity = 30
            self.AOA = 0

            # derived parameters
            self.Re = int(np.round(velocity / 1e-5))  # Reynolds number calculation

            self._x_interp = np.linspace(0, 1, 160)

            self._f_call = self._design3

            self.lb = np.array([0.01, 0.12, 0.02])
            self.ub = np.array([0.1, 0.86, 0.25])
            self.fmin = np.nan
            self.xmin = np.full(dimensions, np.nan)

        self.dimensions = dimensions

        # add name
        self.__name__ = f"AirfoilDesign_{problem}_{dimensions}D"

    def _plot(self, x, y, AOA, Re):
        """Private function for plotting the airfoil"""

        # plt.figure(figsize=(6, 3), dpi=300)
        plt.plot(x, y)
        plt.fill(x, y, color='grey', alpha=0.5)
        plt.title(f'{self.__name__} (AOA = {AOA:.2f}, Re = {Re:.2e})')
        plt.axis('equal')
        plt.tight_layout()
        # plt.savefig(f'{self.__name__}.png')
        plt.show()

    def _prepare_xfoil_process(self, data, AOA, Re):
        """Private function for preparing xfoil process"""

        characters = string.ascii_letters + string.digits
        airfoil_label = ''.join(random.choice(characters) for i in range(16))
        os.mkdir(f'{xfoil_tmp_dir}/{airfoil_label}')
        np.savetxt(f'{xfoil_tmp_dir}/{airfoil_label}/airfoil_{airfoil_label}.dat', data, fmt='%.6f')

        # prepare xfoil input file
        file = open(f'{xfoil_tmp_dir}/{airfoil_label}/parameters_{airfoil_label}.txt', 'w')

        file.write(f'plop\n')
        file.write(f'g\n\n')

        file.write(f'load airfoil_{airfoil_label}.dat\n')

        file.write(f'gdes\n')
        file.write(f'filt\n\n')
        file.write(f'exec\n\n')

        file.write(f'pane\n')
        file.write(f'oper\n')
        file.write(f'iter 500\n')
        file.write(f'visc {Re}\n')
        file.write(f'alfa {AOA}\n')

        file.write(f'cpwr cp_test.txt\n')
        file.close()

        # prepare a copy of xfoil executable
        shutil.copy2(xfoil_binary_path,
                     f'{xfoil_tmp_dir}/{airfoil_label}/xfoil_{airfoil_label}.exe')

        # prepare process
        process = subprocess.Popen(
            f'"{xfoil_tmp_dir}/{airfoil_label}/xfoil_{airfoil_label}.exe" < parameters_{airfoil_label}.txt',
            shell=True,
            cwd=f'{xfoil_tmp_dir}/{airfoil_label}',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return process, airfoil_label

    def _xfoil_run_inverse(self, data, AOA, Re):
        """Private function for running xfoil for inverse design"""

        process, airfoil_label = self._prepare_xfoil_process(data, AOA, Re)

        # run xfoil process
        # print(f'running xfoil {airfoil_label}...')
        try:
            if self._os_name == 'nt':
                stdout, stderr = process.communicate(timeout=5)
            elif self._os_name == 'posix':
                stdout, stderr = process.communicate(timeout=1)
            # print(stdout, stderr)
        except subprocess.TimeoutExpired:
            # print('- run failed')
            rmse = self._eval_fail_fitness
            # cleanup
            if self._os_name == 'nt':
                subprocess.call(['taskkill', '/F', '/IM', f'xfoil_{airfoil_label}.exe'],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
            elif self._os_name == 'posix':
                subprocess.call(['pkill', f'xfoil_{airfoil_label}.exe'],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        else:
            # print('Read')
            # read output file
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    if self._os_name == 'nt':
                        # Sinisa/Windows
                        cp = np.loadtxt(f'{xfoil_tmp_dir}/{airfoil_label}/cp_test.txt',
                                        usecols=2, skiprows=2)
                    elif self._os_name == 'posix':
                        # Stefan/Linux
                        cp = np.loadtxt(f'{xfoil_tmp_dir}/{airfoil_label}/cp_test.txt',
                                        usecols=1)
                    # print(cp)
                rmse = np.sqrt(np.mean((self._target_cp - cp)**2))
                if np.isnan(rmse):
                    rmse = self._eval_fail_fitness
            except:
                # print('- reading output failed')
                rmse = self._eval_fail_fitness

        process.terminate()
        if self._os_name == 'nt':
            time.sleep(1)
        shutil.rmtree(f'{xfoil_tmp_dir}/{airfoil_label}', ignore_errors=True)

        return rmse

    def _xfoil_run_design(self, data, AOA, Re):
        """Private function for running xfoil for airfoil design"""

        process, airfoil_label = self._prepare_xfoil_process(data, AOA, Re)

        # run xfoil process
        # print(f'running xfoil {airfoil_label}...')
        try:
            if self._os_name == 'nt':
                stdout, stderr = process.communicate(timeout=5)
            elif self._os_name == 'posix':
                stdout, stderr = process.communicate(timeout=1)
            # print(stdout, stderr)
        except subprocess.TimeoutExpired:
            # print('- run failed')
            cl_value = -100
            cd_value = -100
            # cleanup
            if self._os_name == 'nt':
                subprocess.call(['taskkill', '/F', '/IM', f'xfoil_{airfoil_label}.exe'],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
            elif self._os_name == 'posix':
                subprocess.call(['pkill', f'xfoil_{airfoil_label}.exe'],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        else:
            # print('Read')
            # read output file
            try:
                cl_value = stdout[-300:].split('CL = ')[1]
                cl_value = cl_value.lstrip().split(' ')[0]
                cl_value = float(cl_value)

                cd_value = stdout[-300:].split('CD = ')[1]
                cd_value = cd_value.lstrip().split(' ')[0]
                cd_value = float(cd_value)

                if np.isnan(cl_value) or np.isnan(cd_value):
                    cl_value = -100
                    cd_value = -100

            except:
                # print('- reading output failed')
                cl_value = -100
                cd_value = -100

        process.terminate()
        if self._os_name == 'nt':
            time.sleep(1)
        shutil.rmtree(f'{xfoil_tmp_dir}/{airfoil_label}', ignore_errors=True)

        return cl_value, cd_value

    def _baseinverse(self, x, plot=False):
        """Base airfoil inverse design problem"""

        cl_upper = x[:len(self._spl1[1])]
        cl_lower = x[len(self._spl2[1]):]

        if len(cl_upper) > 0:

            t1 = self._spl1[0]
            c1 = cl_upper

            t2 = self._spl2[0]
            c2 = cl_lower

            self._spl1 = (t1, c1, self._k)
            self._spl2 = (t2, c2, self._k)

        spl_upper = interp.splev(self._x_interp, self._spl1)
        spl_lower = interp.splev(self._x_interp, self._spl2)

        x_coords = np.concatenate((self._x_interp[::-1], self._x_interp[1:]), axis=0)
        y_coords = np.concatenate((spl_upper[::-1], spl_lower[1:]), axis=0)

        if plot:
            self._plot(x_coords, y_coords, self.AOA, self.Re)

        # prepare xfoil input data
        data = np.vstack((x_coords, y_coords)).transpose()  # upper - ZERO - lower

        rmse = self._xfoil_run_inverse(data, self.AOA, self.Re)
        return rmse

    def _inverseflow(self, x, plot=False):
        """Airfoil inverse design problem with flow parameter solve"""

        AOA = x[0]
        Re = int(np.round(x[1] / 1e-5))  # Reynolds number calculation
        x = x[2:]

        cl_upper = x[:len(self._spl1[1])]
        cl_lower = x[len(self._spl2[1]):]

        if len(cl_upper) > 0:

            t1 = self._spl1[0]
            c1 = cl_upper

            t2 = self._spl2[0]
            c2 = cl_lower

            self._spl1 = (t1, c1, self._k)
            self._spl2 = (t2, c2, self._k)

        spl_upper = interp.splev(self._x_interp, self._spl1)
        spl_lower = interp.splev(self._x_interp, self._spl2)

        x_coords = np.concatenate((self._x_interp[::-1], self._x_interp[1:]), axis=0)
        y_coords = np.concatenate((spl_upper[::-1], spl_lower[1:]), axis=0)

        if plot:
            self._plot(x_coords, y_coords, AOA, Re)

        # prepare xfoil input data
        data = np.vstack((x_coords, y_coords)).transpose()  # upper - ZERO - lower

        rmse = self._xfoil_run_inverse(data, AOA, Re)
        return rmse

    def _design3(self, x, plot=False):
        """Base 3-parameter airfoil design problem"""

        m = x[0]
        p = x[1]
        t = x[2]

        x = self._x_interp

        yc = np.where(x < p,
                      m / (p ** 2) * (2 * p * x - x ** 2),
                      m / ((1 - p) ** 2) * ((1 - 2 * p) + 2 * p * x - x ** 2))

        dyc_dx = np.where(x < p,
                          2 * m / (p ** 2) * (p - x),
                          2 * m / ((1 - p) ** 2) * (p - x))

        theta = np.arctan(dyc_dx)

        yt = 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1015 * x ** 4)

        xu = x - yt * np.sin(theta)
        yu = yc + yt * np.cos(theta)

        xl = x + yt * np.sin(theta)
        yl = yc - yt * np.cos(theta)

        xy_upper = np.hstack((xu[::-1].reshape(-1, 1), yu[::-1].reshape(-1, 1)))
        xy_lower = np.hstack((xl.reshape(-1, 1), yl.reshape(-1, 1)))
        xy = np.vstack((xy_upper[:-1, :], xy_lower))

        if plot:
            self._plot(xy[:,0], xy[:,1], self.AOA, self.Re)

        cl, cd = self._xfoil_run_design(xy, self.AOA, self.Re)

        if cl < 0 or cd < 0:
            return self._eval_fail_fitness
        else:
            return cd / cl + (m / 0.085 + p / 0.65 + t / 0.05) * 2e-3


AD_problems_dict_list = []
for case, dim in AirfoilDesign.case_definitions.items():
    problem_dict = {'label': f'AD_{case}_{dim[0]}D',
                    'class': AirfoilDesign,
                    'case': case,
                    'dimensions': dim[0],
                    'max_evaluations': 200 * dim[0],
                    'max_runs': 1000,
                    }
    AD_problems_dict_list.append(problem_dict)

if __name__ == '__main__':

    # # demo AirfoilDesign functions
    # print('\n*** demo AirfoilDesign functions')
    # dims = [32, 32, 34, 34, 3]
    # test_functions = [AirfoilDesign(problem=p, dimensions=d) \
    #                   for p, d in zip(AirfoilDesign.case_definitions, dims)]
    # for f in test_functions:
    #     x = np.random.uniform(f.lb, f.ub)
    #     print(f'{f.__name__} \n {f(x, True)}')

    # # test optimization
    # import sys
    # sys.path.append('..')
    # from indago import minimize
    # f = AirfoilDesign(problem='design3')
    # minimize(f, f.lb, f.ub, monitoring='dashboard')

    # # plot
    # f = AirfoilDesign(problem='inv3')
    # f(np.random.uniform(f.lb, f.ub), plot=True)

    # standard test
    import sys
    import _local_paths
    import indagobench

    standard_test = indagobench.StandardTest(_local_paths.indagobench25_results_dir,
                                             convergence_window=50, eps_max=0.01, runs_min=100, )
    standard_test.optimizers = indagobench.indagobench25_optimizers
    if len(sys.argv) > 1:
        for problem_dict in AD_problems_dict_list:
            if sys.argv[1] == problem_dict['label']:
                standard_test.problems = [problem_dict]
                break
        else:
            assert False, (f'Wrong arguments: {sys.argv[1]}\n' +
                           f'Expected values: {[f_dict["label"] for f_dict in AD_problems_dict_list]}')
    else:
        standard_test.problems = AD_problems_dict_list

    standard_test.run_all()