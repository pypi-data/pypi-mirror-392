import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import image
from scipy.fftpack import dct, idct

def DCT(field):
    return dct(dct(field.T, norm='ortho').T, norm='ortho')

def IDCT(coefficients):
    return idct(idct(coefficients.T, norm='ortho').T, norm='ortho')


class Ergodic():

    @staticmethod
    def problem_cases_list():
        # problem, dimensions, max_evaluations
        return [
                ('gaussian1', 20, 8_000),
                ('gaussian1', 30, 12_000),
                ('gaussian1', 50, 25_000),
                ('gaussian4', 50, 25_000),
                ('gaussian4+s', 50, 25_000),
                ('phi', 50, 20_000),
                ('phi+s', 50, 20_000),
                ('beta', 50, 15_000),
                ('beta+s', 50, 15_000),
                ('epsilon', 50, 20_000),
                ('epsilon+s', 50, 20_000),
                ]

    def __call__(self, design, label=None):
        return self.evaluate(design)

    def __init__(self, problem, dimensions=None, instance_label=None):

        self.problem = problem
        self.dimensions = dimensions
        if problem.startswith('gaussian1'):
            self.x_min = -10
            self.x_max = 10
            self.y_min = -10
            self.y_max = 10
            self.x = np.linspace(self.x_min, self.x_max, 101)
            self.y = np.linspace(self.y_min, self.y_max, 101)
            self.x, self.y = np.meshgrid(self.x, self.y)
            self.xy0 = [-5, -5]
            # self.m = np.zeros_like(self.x)
            self.m = self.gauss2d(self.x, self.y, 0, 0, 5, 5)
            self.m /= np.sum(self.m)

            self.lb = np.deg2rad([0] + [-20] * (dimensions - 1))
            self.ub = np.deg2rad([360] + [20] * (dimensions - 1))
            self.dx = 0.5


        elif problem.startswith('gaussian4'):
            self.x_min = -10
            self.x_max = 10
            self.y_min = -10
            self.y_max = 10
            self.x = np.linspace(self.x_min, self.x_max, 101)
            self.y = np.linspace(self.y_min, self.y_max, 101)
            self.x, self.y = np.meshgrid(self.x, self.y)
            self.xy0 = [-7, 2]
            self.m = np.zeros_like(self.x)
            xc = [3, -4, 7, -1, 1]
            yc = [4, 0, -2, -5, -1]
            sx = [2, 3, 2, 4, 5]
            sy = [3, 2, 3, 2, 5]
            for i in range(5):
                self.m += self.gauss2d(self.x, self.y, xc[i], yc[i], sx[i], sy[i])
            self.m /= np.sum(self.m)

            self.lb = np.deg2rad([0] + [-20] * (dimensions - 1))
            self.ub = np.deg2rad([360] + [20] * (dimensions - 1))
            self.dx = 1

        elif problem.startswith('phi') or problem.startswith('beta') or problem.startswith('epsilon'):

            img = problem[:-2] if problem.endswith('+s') else problem
            self.m = image.imread(f'{os.path.dirname(os.path.abspath(__file__))}/ergodic_data/{img}.png')[::-1, :]
            self.m = 1 - np.mean(self.m, axis=2)
            # print(f'{np.min(self.m)=}, {np.max(self.m)=}')
            self.m /= np.sum(self.m)

            self.x_min = 0
            self.x_max = self.m.shape[1] - 1
            self.y_min = 0
            self.y_max = self.m.shape[0] - 1
            self.x = np.arange(self.x_max + 1)
            self.y = np.arange(self.y_max + 1)
            self.x, self.y = np.meshgrid(self.x, self.y)
            if problem.startswith('phi'):
                self.xy0 = [57, 13]
                self.dx = 6.6
            if problem.startswith('beta'):
                self.xy0 = [12, 9]
                self.dx = 6.5
            if problem.startswith('epsilon'):
                self.xy0 = [84, 45]
                self.dx = 6

            self.lb = np.deg2rad([0] + [-30] * (dimensions - 1))
            self.ub = np.deg2rad([360] + [30] * (dimensions - 1))

        self.spectral_objective = problem.endswith('+s')
        if self.spectral_objective:
            self.mk = DCT(self.m)

            ky, kx = np.meshgrid(np.arange(self.m.shape[0]), np.arange(self.m.shape[1]))
            self.Las = 1.0 / (1 + kx ** 2 + ky ** 2) ** 1.5

    @staticmethod
    # define normalized 2D gaussian
    def gauss2d(x=0, y=0, mx=0, my=0, sx=1, sy=1):
        return 1. / (2. * np.pi * sx * sy) * np.exp(
            -((x - mx) ** 2. / (2. * sx ** 2.) + (y - my) ** 2. / (2. * sy ** 2.)))

    def evaluate(self, design, plot=False):
        path = self.path(design)
        c = self.calc_c(path)

        if self.spectral_objective:
            ck = DCT(c)
            # o = np.sum(np.abs(self.Las * (ck - self.mk).T))
            o = np.sum(self.Las * (ck - self.mk).T**2)
        else:
            o = np.sum((c - self.m)**2)

            # p = 0
            # c1 = self.x_min - path[:, 0]
            # c1[c1 < 0] = 0
            # c2 = path[:, 0] - self.x_max
            # c2[c2 < 0] = 0
            # c3 = self.y_min - path[:, 1]
            # c3[c3 < 0] = 0
            # c4 = path[:, 1] - self.y_max
            # c4[c4 < 0] = 0
            #
            # for cp in [c1, c2, c3, c4]:
            #     p += np.sum(cp ** 2)
            #
            # if plot:
            #     print(f'{o=}, {p=}')
            #     self.plot(design)
            #
            # if p > 0:
            #     return 2 + p * 1e-2

        return o

    def calc_c(self, path):
        c = np.zeros_like(self.m)
        for i in range(path.shape[0]):
            c += self.gauss2d(self.x, self.y, path[i, 0], path[i, 1], self.dx, self.dx)

        c /= np.sum(c)
        return c

    def path(self, design):
        phi0, *theta = design
        phi = np.cumsum(np.append(0, theta)) + phi0

        path = np.array([self.xy0])
        for p in phi:
            xy = path[-1, :] + np.array([np.cos(p), np.sin(p)]) * self.dx
            path = np.append(path, [xy], axis=0)

        return path

    def plot_m(self, ax):
        ax.contourf(self.x, self.y, self.m, 20, cmap=plt.cm.Oranges, vmin=0, vmax=2*np.max(self.m))

    def plot_trajectory(self, ax, design, c, lw, ls):
        path = self.path(design)
        ax.plot(path[:, 0], path[:, 1], c=c, lw=lw, ls=ls)

    def plot(self, design, filename=None):

        path = self.path(design)
        c = self.calc_c(path)
        #c[c < 1e-5] = np.nan

        fig, axes = plt.subplots(ncols=3, figsize=(30, 10))
        _m = axes[0].contourf(self.x, self.y, self.m, 20)
        plt.colorbar(_m, ax=axes[0])
        _c = axes[1].contourf(self.x, self.y, c, 20)
        plt.colorbar(_c, ax=axes[1])
        _d = axes[2].contourf(self.x, self.y, self.m - c, 20)
        plt.colorbar(_d, ax=axes[2])

        axes[0].plot(path[:, 0], path[:, 1], 'k', lw=2)
        for ax in axes:
            ax.axis('equal')

        if filename is not None:
            fig.savefig(filename)
            plt.close(fig)


EC_problems_dict_list = []
for case, dimensions, max_evals in Ergodic.problem_cases_list():
    f_dict = {'label': f'EC_{case}_{int(dimensions)}D',
              'class': Ergodic,
              'case': case,
              'dimensions': dimensions,
              'max_evaluations': max_evals,
              'max_runs': 1000,
              'forward_unique_str': True,
              }
    EC_problems_dict_list.append(f_dict)

if __name__ == '__main__':

    # Testing
    # erg = Ergodic(problem='phi+s', dimensions=50)
    # design0 = np.deg2rad(np.append(np.random.uniform(0, 360, 1),
    #                                np.random.uniform(-20, 20, erg.dimensions - 1)
    #                                ))
    # erg.evaluate(design0, plot=True)
    # erg.plot(design0, f'test_Ergodic_{erg.problem}_{erg.dimensions}D.png')
    #
    # import indago
    #
    # optimizer = indago.DE()
    # optimizer.evaluation_function = erg
    # optimizer.monitoring = 'dashboard'
    # optimizer.max_evaluations = 25_000
    # optimizer.processes = 'max'
    # optimizer.optimize()
    # erg.plot(optimizer.best.X, f'best_EC_{erg.problem}_{erg.dimensions}D.png')
    # optimizer.plot_history(f'conv_EC_{erg.problem}_{erg.dimensions}D.png')

    # Run standard test
    import indagobench
    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir,
                                             # convergence_window=10, eps_max=0.1, runs_min=100, processes=25, batch_size=100,
                                             # convergence_window=50, eps_max=0.01, runs_min=100,
                                             )
    standard_test.optimizers = indagobench.indagobench25_optimizers#[:8]
    standard_test.problems = EC_problems_dict_list#[0:3]
    # standard_test.run_all()

    standard_test.optimizers = [indagobench.indagobench25_optimizers[1],
                                indagobench.indagobench25_optimizers[16],
                                indagobench.indagobench25_optimizers[19]]

    # Results postprocessing and visualization
    if not os.path.exists(f'{indagobench._local_paths.indagobench25_results_dir}/EC/'):
        os.mkdir(f'{indagobench._local_paths.indagobench25_results_dir}/EC/')

    for problem_dict in standard_test.problems:
        erg = Ergodic(problem_dict['case'], problem_dict['dimensions'])
        problem_results = indagobench.ProblemResults(problem_dict)
        problem_results.optimizers = 'LBFGSB LSHADE CMAES'.split()

        case_name = f'{problem_dict["label"]}_best'
        x_best = problem_results.results['_x_min']
        # erg.plot(x_best, f'{indagobench._local_paths.indagobench25_results_dir}/EC/{case_name}.png')

        w = 10
        h = (erg.y_max - erg.y_min) / (erg.x_max - erg.x_min) * w
        fig, ax = plt.subplots(figsize=(w, h))
        erg.plot_m(ax)

        lw = 8
        erg.plot_trajectory(ax, x_best, c='k', lw=lw, ls='-')
        ax.plot([], [], c='k', lw=lw, ls='-', label='Best')

        C = [f'C{i}' for i in range(5, 1, -1)] * 4
        LS = ['--'] * 5 + ['-.'] * 5 + [':'] * 5 + [(0, (3, 1, 1, 1))] * 5
        for optimizer, c, ls in zip(standard_test.optimizers, C, LS):
            f = problem_results.results['f_best ' + optimizer['label']]
            i = np.argmin(np.abs(np.median(f) - f))
            x = problem_results.results[f'x_best ' + optimizer['label']][i, :]
            opt_case_name = f'{problem_dict["label"]}_{optimizer["label"].replace(" ", "-")}_median'
            # erg.plot(x, f'{indagobench._local_paths.indagobench25_results_dir}/EC/{case_name}.png')
            erg.plot_trajectory(ax, x, c=c, lw=lw, ls=ls)
            ax.plot([], [], c=c, lw=lw, ls=ls, label=optimizer['label'])

        ax.set_xlim(erg.x_min, erg.x_max)
        ax.set_ylim(erg.y_min, erg.y_max)
        ax.axis('off')
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        # ax.legend(loc='upper center', ncol=4, fontsize=16)#, bbox_to_anchor=(0.5, -0.05),)
        plt.savefig(f'{indagobench._local_paths.indagobench25_results_dir}/EC/{case_name}.png',
                    bbox_inches='tight', pad_inches=0)
        plt.close(fig)

        problem_results.make_full_convergence_figure(f'{indagobench._local_paths.indagobench25_results_dir}/EC/short_conv_{case_name}.png',
                                                     header_plots=False)