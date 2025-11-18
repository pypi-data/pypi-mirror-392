import sys
from time import sleep

import numpy as np
import scipy as sp

try:
    import nlopt

except ImportError as e:
    print('\033[91m' + f'Failed at importing optional module: {e.msg}')
    print('Code will continue but optimization using nlopt is not possible.' + '\033[0m')


def single_nlopt_run(problem_dict, optimizer_dict, instance_label):
    if 'class' in problem_dict.keys():
        instance = problem_dict['class'](problem_dict['case'], problem_dict['dimensions'], instance_label=instance_label)

    fitness = []
    best = [np.inf, None]
    def f_log(x, grad):
        fit = float(instance(x))
        fitness.append(fit)
        if fit <= best[0]:
            best[0] = fit
            best[1] = x.copy()
        return fit

    if optimizer_dict['label'] == 'STOGO':
        opt = nlopt.opt(nlopt.GD_STOGO_RAND, instance.dimensions)
    if optimizer_dict['label'] == 'CRS':
        opt = nlopt.opt(nlopt.GN_CRS2_LM, instance.dimensions)
    if optimizer_dict['label'] == 'ISRES':
        opt = nlopt.opt(nlopt.GN_ISRES, instance.dimensions)
    if optimizer_dict['label'] == 'ESCH':
        opt = nlopt.opt(nlopt.GN_ESCH, instance.dimensions)

    np.random.seed()
    opt.set_lower_bounds(instance.lb)
    opt.set_upper_bounds(instance.ub)
    x0 = np.random.uniform(instance.lb, instance.ub)
    opt.set_min_objective(f_log)
    opt.set_maxeval(problem_dict['max_evaluations'])

    res = opt.optimize(x0)

    for i in range(len(fitness)):
        fitness[i] = np.min(fitness[:i + 1])

    evals = np.arange(len(fitness)) + 1
    ef_conv = np.full((2, evals.size), np.nan)
    ef_conv[0, :] = evals
    ef_conv[1, :] = fitness

    assert best[0] == instance(best[1]), f'f_best[{best[0]}] == f(x_best)[{instance(best[1])}] breach'
    # assert best[0] == instance(res), f'f_best[{best[0]}] == f(res)[{instance(res)}] breach'
    # assert best[0] == opt.last_optimum_value(), f'f_best[{best[0]}] == opt.last_optimum_value()[{opt.last_optimum_value()}] breach {opt.last_optimize_result()=}'

    return ef_conv, best[0], best[1]


nlopt_stogo_dict = {'run': single_nlopt_run,
                   'label': f'STOGO',
                   }

nlopt_crs_dict = {'run': single_nlopt_run,
                   'label': f'CRS',
                   }

nlopt_esch_dict = {'run': single_nlopt_run,
                   'label': f'ESCH',
                   }
