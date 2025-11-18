
import numpy as np
import scipy as sp

def single_scipy_run(problem_dict, optimizer_dict, instance_label):
    if 'class' in problem_dict.keys():
        instance = problem_dict['class'](problem_dict['case'], problem_dict['dimensions'], instance_label=instance_label)



    fitness = []
    best = [np.inf, None]
    def f_log(x, uniqe_str=None):
        fit = instance(x)
        fitness.append(fit)
        if fit <= best[0]:
            best[0] = fit
            best[1] = x.copy()
        return fit

    np.random.seed()
    x0 = np.random.uniform(instance.lb, instance.ub)

    if optimizer_dict['label'] == 'LBFGSB':
        eps = 1e-3 * (instance.ub - instance.lb)
        f_best = np.inf
        while True:
            res = sp.optimize.minimize(f_log, x0,
                                       method='L-BFGS-B',
                                       bounds=np.array([instance.lb, instance.ub]).T,
                                       options={'maxfun': problem_dict['max_evaluations'] - len(fitness),
                                                # 'tol': 0,
                                                'ftol': 0,
                                                'gtol': 0,
                                                # 'eps': 1e-20,
                                                'eps': eps,
                                                },
                                       )
            if res.fun < f_best:
                # print(f'{res.fun=}')
                f_best = res.fun
                x0 = res.x
                eps /= 10
            else:
                break
            if problem_dict['max_evaluations'] < len(fitness):
                break

    elif optimizer_dict['label'] == 'DA':
        res = sp.optimize.dual_annealing(f_log, x0=x0,
                                         bounds=list(zip(instance.lb, instance.ub)),
                                         maxfun=problem_dict['max_evaluations'],
                                         maxiter=problem_dict['max_evaluations'],
                                         )

    else:
        raise ValueError(f'Optimizer {optimizer_dict["label"]} is not implemented.')

    # print(res.success, res.status, res.message)
    # print(f'{len(fitness)=}, {res.nfev}, {res.fun}, {res.x}')
    for i in range(len(fitness)):
        fitness[i] = np.min(fitness[:i + 1])


    assert best[0] == instance(best[1]), f'f_best[{best[0]}] == f(x_best)[{instance(best[1])}] breach'
    # assert res.fun == instance(res.x), f'res.fun[{res.fun}] == f(res.f)[{instance(res.x)}] breach {res.status=} {res.success=} {res.message=}'
    # assert best[0] == res.fun, f'f_best[{best[0]}] == res.fun[{res.fun}] breach {res.status=} {res.success=} {res.message=}'
    # assert best[0] == instance(res.x), f'f_best[{best[0]}] == f(res.x)[{instance(res.x)}] breach {res.status=} {res.success=} {res.message=}'


    evals = np.arange(len(fitness)) + 1
    ef_conv = np.full((2, evals.size), np.nan)
    ef_conv[0, :] = evals
    ef_conv[1, :] = fitness

    return ef_conv, best[0], best[1]

scipy_lbfgsb_dict = {'run': single_scipy_run,
                'label': f'LBFGSB',
                     }
# st24_optimizers_list.insert(1, scipy_lbfgsb)
scipy_dual_annealing_dict = {'run': single_scipy_run,
                'label': f'DA',
                             }
# st24_optimizers_list.insert(2, scipy_dual_annealing)