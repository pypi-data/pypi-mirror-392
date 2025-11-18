import sys, os
import numpy as np
import scipy as sp


try:
    from zoopt import Dimension, Objective, Parameter, Opt

except ImportError as e:
    print('\033[91m' + f'Failed at importing optional module: {e.msg}')
    print('Code will continue but optimization using zoopt is not possible.' + '\033[0m')


def single_zoopt_run(problem_dict, optimizer_dict, instance_label):
    if 'class' in problem_dict.keys():
        instance = problem_dict['class'](problem_dict['case'], problem_dict['dimensions'], instance_label=instance_label)

    def f_wrap(solution):
        x = np.array(solution.get_x())
        value = instance(x)
        return value

    sys.stdout = open(os.devnull, 'w')  # null umjesto filename
    np.random.seed()
    bounds = np.append([instance.lb], [instance.ub], axis=0).T
    dim = Dimension(instance.dimensions, bounds, [True] * instance.dimensions)
    obj = Objective(f_wrap, dim)
    solution = Opt.min(obj, Parameter(budget=problem_dict['max_evaluations'],
                                      seed=np.random.randint(0, 1e6)))

    fitness = np.array(obj.get_history())
    for i in range(fitness.size):
        fitness[i] = np.min(fitness[:i + 1])
    evals = np.arange(len(fitness)) + 1

    # f_interp = sp.interpolate.interp1d(evals, fitness,
    #                                    bounds_error=False,
    #                                    fill_value=(fitness[0], fitness[-1]),
    #                                    )
    # evals = np.linspace(0, 1, 101) * problem_dict['max_evaluations']
    # fit = f_interp(evals).reshape((1, -1))
    # return fit, np.array(solution.get_x())


    # evals = np.arange(len(fitness)) + 1
    ef_conv = np.full((2, evals.size), np.nan)
    ef_conv[0, :] = evals
    ef_conv[1, :] = fitness

    return ef_conv, fitness[-1], np.array(solution.get_x())

zoopt_dict = {'run': single_zoopt_run,
              'label': f'SRACOS',
              }
