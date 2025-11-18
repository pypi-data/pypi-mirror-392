import numpy as np
import scipy as sp

try:
    from pymoo.core.problem import Problem
    from pymoo.algorithms.soo.nonconvex.ga import GA
    from pymoo.algorithms.soo.nonconvex.cmaes import CMAES
    from pymoo.optimize import minimize
    from pymoo.termination import get_termination
    from pymoo.core.callback import Callback

except ImportError as e:
    print('\033[91m' + f'Failed at importing optional module: {e.msg}')
    print('Code will continue but optimization using pymoo is not possible.' + '\033[0m')


def single_pymoo_run(problem_dict, optimizer_dict, instance_label):

    class PymooIndagoProblemWrapper(Problem):
        def __init__(self, problem_dict):
            self.f = problem_dict['class'](problem_dict['case'], problem_dict['dimensions'], instance_label)
            super().__init__(n_var=self.f.lb.size, n_obj=1, n_ieq_constr=0, xl=self.f.lb, xu=self.f.ub)

        def _evaluate(self, x, out, *args, **kwargs):
            n = x.shape[0]
            F = np.full(n, np.nan)
            for i in range(n):
                F[i] = self.f(x[i, :])
            out["F"] = F

    class MyCallback(Callback):

        def __init__(self) -> None:
            super().__init__()
            self.evaluation = []
            self.fitness = []

        def notify(self, algorithm):
            self.evaluation.append(algorithm.evaluator.n_eval)
            self.fitness.append(algorithm.opt[0].F[0])

    problem = PymooIndagoProblemWrapper(problem_dict)
    callback = MyCallback()
    """
    Algorithm
    """
    algorithm = None
    if optimizer_dict['label'] == 'GA':
        algorithm = GA(
            pop_size=problem.f.lb.size * 2,
            eliminate_duplicates=True)
    if optimizer_dict['label'] == 'CMAES':
        algorithm = CMAES(
            # pop_size=problem.f.lb.size * 2,
            )

    termination = get_termination("n_eval", problem_dict['max_evaluations'])
    res = minimize(problem,
                   algorithm,
                   termination=termination,
                   # seed=1,
                   verbose=False,
                   # save_history=True,
                   callback=callback)

    evals = np.array(callback.evaluation)
    fitness = np.array(callback.fitness)

    # true_evals = evals[-1]  # sinisa execution time

    if evals[-1] < problem_dict['max_evaluations']:
        evals = np.append(evals, problem_dict['max_evaluations'])
        fitness = np.append(fitness, fitness[-1])

    # f_interp = sp.interpolate.interp1d(evals, fitness,
    #                                    bounds_error=False,
    #                                    fill_value=np.nan)
    # evals = np.linspace(0, 1, 101) * problem_dict['max_evaluations']
    # fit = f_interp(evals).reshape((1, -1))

    # return fit, res.X, true_evals  # sinisa execution time
    # return fit, res.X

    # evals = np.arange(len(fitness)) + 1
    ef_conv = np.full((2, evals.size), np.nan)
    ef_conv[0, :] = evals
    ef_conv[1, :] = fitness

    return ef_conv, res.f, res.X

pymoo_ga_dict = {'run': single_pymoo_run,
                 'label': f'GA',
                 }
pymoo_cmaes_dict = {'run': single_pymoo_run,
                    'label': f'CMAES',
                    }

