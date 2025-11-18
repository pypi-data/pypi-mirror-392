# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 15:57:13 2017

@author: stefan
"""
import os
import numpy as np
import matplotlib.pyplot as plt

def read_setup_list():
    setups_filename = f'{os.path.dirname(os.path.abspath(__file__))}/shortest_path_data/shortest_path_cases.txt'
    setup = []
    with open(setups_filename) as f:
        lines = f.readlines()
        for line in lines:
            if line.strip()[0] == '#':
                continue
            else:
                problem, dimensions, lb, ub, max_eval, x1, x2, y1, y2 = line.split()
                setup.append([problem, int(dimensions), float(lb), float(ub), int(max_eval), x1, x2, y1, y2])
    return setup

class ShortestPath():
    """Shortest path test function"""

    def __call__(self, x):
        return self._f_call(x)

    def __init__(self, problem, dimensions=None, instance_label=None):

        self._f_call = None
        self.problem = problem
        data_filename = f'{os.path.dirname(os.path.abspath(__file__))}/shortest_path_data/shortest_path_cases.npz'
        if os.path.exists(data_filename):
            npz = np.load(data_filename)
            if problem in npz.files:
                data = npz[problem]
                self.A = data[0, :2]
                self.B = data[1, :2]
                self.XC = data[0, 2:]
                self.YC = data[1, 2:]
                self.R = data[2, 2:]
            else:
                assert False, f'Unknown ShortestPath problem ({problem}) in {data_filename}'
        else:
            assert False, f'Missing ShortestPath data file {data_filename}'

        setup = read_setup_list()
        for s in setup:
            # print(f' - {s=}')
            if s[0] == problem and s[1] == dimensions:
                self.lb = np.full(dimensions, float(s[2]))
                self.ub = np.full(dimensions, float(s[3]))
                self.fmin = np.nan
                self.xmin = np.full(dimensions, np.nan)
                self.dimensions = int(s[1])
                self.__name__ = f'ShortestPath_{problem}_{dimensions}D'
                self._f_call = self.penalty
                self._scene = [float(_) for _ in s[5:]]
                # print(f'{self._scene=}')
                break
        else:
            assert False, 'Unknown problem/dimension combination for ShortestPath'
    
    def save_case(self, case):
        data_filename = f'{os.path.dirname(os.path.abspath(__file__))}/shortest_path_data/shortest_path_cases.npz'
        if os.path.exists(data_filename):
            npz = dict(np.load(data_filename))
        else:
            npz = {}
        data = np.full([3, np.size(self.XC) + 2], np.nan)
        data[0, :2] = self.A
        data[1, :2] = self.B
        data[0, 2:] = self.XC
        data[1, 2:] = self.YC
        data[2, 2:] = self.R
        npz[case] = data
        np.savez_compressed(data_filename, **npz)

    def obj_cnstr(self, phi):
        
        x, y, L, D = self.generate_path(phi)

        return L, D
    
    def penalty(self, phi):

        x, y, L, D = self.generate_path(phi)

        f = L + D

        return f

    def generate_path(self, phi):

        phi = np.deg2rad(phi)
        n = np.size(phi) + 1
        beta = np.zeros(n)
        for i in range(1, n):
            beta[i] = beta[i - 1] + phi[i - 1]

        x1, y1 = np.zeros(n + 1), np.zeros(n + 1)
        x1[0], y1[0] = self.A[0], self.A[1]
        for i in range(1, n + 1):
            x1[i] = x1[i - 1] + np.cos(beta[i - 1])
            y1[i] = y1[i - 1] + np.sin(beta[i - 1])

        alpha = np.arctan2(self.B[1] - self.A[1], self.B[0] - self.A[0])
        # print(np.rad2deg(alpha))

        alpha1 = np.arctan2(y1[-1] - self.A[1], x1[-1] - self.A[0])
        # print(np.rad2deg(alpha1))

        beta2 = np.zeros(n)
        beta2[0] = alpha - alpha1
        for i in range(1, n):
            beta2[i] = beta2[i - 1] + phi[i - 1]

        x2, y2 = np.zeros(n + 1), np.zeros(n + 1)
        x2[0], y2[0] = self.A[0], self.A[1]
        for i in range(1, n + 1):
            x2[i] = x2[i - 1] + np.cos(beta2[i - 1])
            y2[i] = y2[i - 1] + np.sin(beta2[i - 1])

        ll = np.sqrt((self.A[0] - self.B[0])**2 + (self.A[1] - self.B[1])**2)
        l2 = np.sqrt((self.A[0] - x2[-1])**2 + (self.A[1] - y2[-1])**2)
        k = ll / l2

        x, y = np.zeros(n + 1), np.zeros(n + 1)
        x[0], y[0] = self.A[0], self.A[1]
        for i in range(1, n + 1):
            x[i] = x[i - 1] + k * np.cos(beta2[i - 1])
            y[i] = y[i - 1] + k * np.sin(beta2[i - 1])

        # Calculating the length of path inside obstacles

        x1 = x[0:-1]
        y1 = y[0:-1]
        x2 = x[1:]
        y2 = y[1:]

        D = 0.0
        for xc, yc, r in zip(self.XC, self.YC, self.R):
            # print('Circle (%f, %f, %f)' % (xc, yc, r))
            a = (x2 - x1)**2 + (y2 - y1)**2
            b = 2 * (x2 - x1) * (x1 - xc) + 2 * (y2 - y1) * (y1 - yc)
            c = x1**2 + xc**2 - 2 * x1 * xc + y1**2 + yc**2 - 2 * y1 * yc - r**2

            d = b**2 - 4 * a * c
            a = a[d >= 0.0]
            b = b[d >= 0.0]
            d = d[d >= 0.0]

            t1 = (-b - np.sqrt(d)) / (2 * a)
            t2 = (-b + np.sqrt(d)) / (2 * a)

            # print(t1)
            # print(t2)

            t1[t1 < 0] = 0
            t2[t2 < 0] = 0
            t1[t1 > 1] = 1
            t2[t2 > 1] = 1

            # print(t1)
            # print(t2)

            # D += np.sum(np.abs(t2 - t1)) * k
            lo = np.sum(t2 - t1)
            if lo > 0:
                D += lo * k + r
            # print(t2 - t1, D)
            # print()

        L = k * n

        return x, y, L, D

    def plot_solution(self, phi, filename, label):
        x1, x2, y1, y2 = self._scene
        x_span = np.abs(x1 - x2)
        y_span = np.abs(y1 - y2)

        w = 10
        h = w * y_span / x_span
        # print(f'{x_span=}, {y_span=}')
        # print(f'{w=}, {h=}')
        fig, ax = plt.subplots(figsize=(w, h))
        self.draw_obstacles(ax)
        self.draw_path(phi, ax=ax, label=label, lw=2)
        ax.axis('off')
        ax.set_xlim(x1, x2)
        ax.set_ylim(y1, y2)
        ax.axis('equal')
        ax.legend()

        fig.savefig(filename)
        plt.close(fig)

    def draw_obstacles(self, ax):

        ax.plot(self.A[0], self.A[1], 'bo', zorder=10, ms=6)
        ax.plot(self.B[0], self.B[1], 'go', zorder=10, ms=6)

        for xc, yc, r in zip(self.XC, self.YC, self.R):
            circ = plt.Circle((xc, yc), r, color='grey', alpha=0.2)
            ax.add_artist(circ)

    def draw_path(self, phi, ax=None, label=None, c=None, ls='-', lw=1, a=1.0):

        x, y, L, D = self.generate_path(phi)

        if ax is None:
            plt.figure()
            ax = plt.gca()
            self.draw_obstacles(ax)
            ax.set_title('L: %.2f, D: %.2f' % (L, D))

        ax.plot(x, y, label=label, c=c, ls=ls, lw=lw, alpha=a)
        # ax.axis('image')


SP_problems_dict_list = []
for (case, dimensions, lb, ub, max_evaluations, *_) in read_setup_list():
    problem_dict = {'label': f'SP_{case}_{int(dimensions)}D',
                    'class': ShortestPath,
                    'case': case,
                    'dimensions': dimensions,
                    'max_evaluations': max_evaluations,
                    'max_runs': 1000,
                    }
    SP_problems_dict_list.append(problem_dict)


if __name__ == '__main__':

    """
    Code used for designing ShortestPath problems (obstacles, start & end point etc.).
    """
    # sp = ShortestPath('zigzag2')
    # if not hasattr(sp, 'XC'): # or True:
    #     sp.A = np.array([0, 0])
    #     sp.B = np.array([1000, 0])
    #     # # n = 8
    #     # N = 20
    #     # sp.XC, sp.YC = np.meshgrid(np.linspace(100, 500, 5),
    #     #                            np.linspace(-150, 150, 4))
    #     # #
    #     # r = 40
    #     # dr = 0.1 * r
    #     # sp.YC[:, 0::2] += 25
    #     # sp.YC[:, 1::2] -= 25
    #     # sp.XC = np.ravel(sp.XC) + np.random.uniform(-dr, dr, N)
    #     # sp.YC = np.ravel(sp.YC) + np.random.uniform(-dr, dr, N)
    #     # sp.R = np.random.uniform(0.9 * r, 1.1 * r, N)
    #     # n = 200
    #     # sp.XC = np.random.uniform(0, 1000, n)
    #     # sp.YC = np.random.uniform(-200, 200, n)
    #     # sp.R = np.random.uniform(5, 10, n)
    #
    #     sp.XC = np.array([300, 650])
    #     sp.YC = np.array([90, -120])
    #     sp.R = np.array([120, 150])
    #
    #     sp.save_case(sp.case)
    #
    # th = np.random.uniform(-30, 30, 20)
    # print(f'{th=}')
    # fig, ax = plt.subplots(figsize=(10, 6))
    # sp.draw_obstacles(ax)
    # sp.draw_path(th, ax=ax)
    # ax.set_ylim(-300, 300)
    # plt.show()


    import indagobench
    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir,
                                             # convergence_window=10, eps_max=1.0, runs_min=10,
                                             # convergence_window=10, eps_max=0.1, runs_min=100,
                                             convergence_window=50, eps_max=0.01, runs_min=100,
                                             )
    standard_test.optimizers = indagobench.indagobench25_optimizers
    standard_test.problems = SP_problems_dict_list#[15:16]
    # standard_test.run_all()


    # Results postprocessing and visualization
    if not os.path.exists(f'{indagobench._local_paths.indagobench25_results_dir}/SP/'):
        os.mkdir(f'{indagobench._local_paths.indagobench25_results_dir}/SP/')

    for problem_dict in standard_test.problems:
        sp = ShortestPath(problem_dict['case'], problem_dict['dimensions'])
        problem_results = indagobench.ProblemResults(problem_dict)
        results = problem_results.results
        case_name = f'{problem_dict["label"]}_best'
        x_best = results['_x_min']

        problem_results.optimizers = 'PSO BA LSHADE CMAES'.split()
        # problem_results.make_full_convergence_figure(f'{indagobench._local_paths.indagobench25_results_dir}/SP/short_conv_{problem_dict["label"]}.png',
        #                                              header_plots=False)


        # sp.plot_solution(x_best,
        #                  f'{indagobench._local_paths.indagobench25_results_dir}/SP/{case_name}.png',
        #                  label=case_name)

        print(f'{sp._scene=}')
        x1, x2, y1, y2 = sp._scene
        x_span = np.abs(x1 - x2)
        y_span = np.abs(y1 - y2)

        w = 10
        h = 10 #
        # h = w * y_span / x_span
        # print(f'{x_span=}, {y_span=}')
        # print(f'{w=}, {h=}')
        # fig, (ax, ax_legend)= plt.subplots(figsize=(w, h+1), nrows=2, height_ratios=[h, 1])
        fig = plt.figure(figsize=(w, h))
        ax = fig.add_axes([0, 0, 1, 1], frameon=True, facecolor='blue')
        # ax_legend = fig.add_axes([0, 0, 1, 0.1], frameon=True, facecolor='red')
        sp.draw_obstacles(ax)


        C = [f'C{i}' for i in range(5)] * 4
        LS = ['--'] * 5 + ['-.'] * 5 + [':'] * 5 + [(0, (3, 1, 1, 1))] * 5
        for optimizer, c, ls in zip(standard_test.optimizers, C, LS):

            if ('f_best ' + optimizer['label']) not in results.keys():
                continue
            f = results['f_best ' + optimizer['label']]
            i = np.argmin(np.abs(np.median(f) - f))
            x = results[f'x_best ' + optimizer['label']][i, :]

            case_name = f'{problem_dict["label"]}_{optimizer["label"].replace(" ", "-")}_median'
            # sp.plot_solution(x, f'{indagobench._local_paths.indagobench25_results_dir}/SP/{case_name}.png',
            #                  label=f'{case_name}')

            sp.draw_path(x, ax=ax, label=f'{optimizer["label"].replace(" ", "-")}', lw=1, ls=ls, c=c)

        sp.draw_path(x_best, ax=ax, label=f'Best', lw=1.2, c='k')
        ax.axis('off')
        ax.axis('image')
        # legend = ax.legend(ncol=7, frameon=False,
        #           loc='upper center', bbox_to_anchor=(0.5,1.02))
        # legend.get_frame().set_facecolor('none')
        # ax_legend.axis('off')

        ax.set_xlim(x1, x2)
        ax.set_ylim(y1, y2)
        fig.text(0.1,0.9, f'{problem_dict["label"]}', va='top', fontsize=20)
        fig.savefig(f'{indagobench._local_paths.indagobench25_results_dir}/SP/{problem_dict["label"]}_all.png', dpi=200)
        plt.close(fig)
