import sys

from shapely.predicates import is_valid

sys.path.append('../..')

import indagobench
import numpy as np


def check_shapes(x_best, f_best, f_conv):
    # Check for shape match
    # assert x_best.shape[0] == f_best.size == f_conv.shape[0], f' - {method}: x_best, f_best and f_conv must have the same size'
    eps = 1e-3
    n = 0

    if not (x_best.shape[0] == f_best.size == f_conv.shape[0]):
        print(f'\033[91m   Shapes mismatch! x_best, f_best and f_conv must have the same size\033[0m')

        for i, (fb, fc) in enumerate(zip(f_best, f_conv[:, -1])):
            d = 2 * np.abs(fb - fc) / (np.abs(fb) + np.abs(fc))
            print(f'   run {i:03d}: \033[91m{fb} {fc}     {d:.6e}\033[0m')
            # if d > eps:
            #     break

        print('Remove results')
        while True:
            var = input('Select variable [x_best, f_best, f_conv, exit]: ')
            if var == 'exit':
                break

            if var not in 'x_best f_best f_conv'.split():
                print('Wrong selection!')
                continue

            i1 = int(input('First run index to remove: '))
            i2 = int(input('Last run index to remove: '))

            if var == 'x_best':
                x_best = np.delete(x_best, np.arange(i1, i2+1), axis=0)
                print(f'{x_best.shape=}')
            elif var == 'f_best':
                f_best = np.delete(f_best, np.arange(i1, i2+1), axis=0)
                print(f'{f_best.shape=}')
            elif var == 'f_conv':
                f_conv = np.delete(f_conv, np.arange(i1, i2+1), axis=0)
                print(f'{f_conv.shape=}')

            n += i2 - i1 + 1

        # n = int(input('Number of runs to keep:'))
        # n = i
        # x_best = x_best[:n, :]
        # f_best = f_best[:n]
        # f_conv = f_conv[:n, :]
        # return f_best.size - n, x_best, f_best, f_conv

    return n, x_best, f_best, f_conv

def check_nans(x_best, f_best, f_conv):
    # Check for NaN's
    # assert not np.any(np.isnan(f_best)), f'NaN in f_best!'
    if np.any(np.isnan(f_best)):
        print('\033[91m    NaN in f_best!\033[0m')
        # print(f'{f_best=}')
        input('Press Enter to continue...')
    # assert not np.any(np.isnan(f_conv[:, -1])), f'NaN in f_conv!'
    if f_conv.size > 0:
        if np.any(np.isnan(f_conv[:, -1])):
            print('\033[91m    NaN in f_conv!\033[0m')
            # print(f'{f_conv[:, -1]=}')
            input('Press Enter to continue...')

def check_duplicates(x_best, f_best, f_conv):

    unique_x_best, i_x_best = np.unique(x_best, return_index=True, axis=0)
    unique_f_conv, i_f_conv = np.unique(f_conv, return_index=True, axis=0)
    unique_f_best, i_f_best = np.unique(f_best, return_index=True)

    n_duplicates_f_conv, n_duplicates_x_best = 0, 0
    if i_f_conv.size < f_conv.shape[0]:
        duplicate_mask = np.ones(f_conv.shape[0], np.bool_)
        duplicate_mask[i_f_conv] = 0
        duplicate_f_conv = f_conv[duplicate_mask]
        n_duplicates_f_conv = np.sum(duplicate_mask)
        print(f'\033[91m    Duplicates detected in f_conv {n_duplicates_f_conv}/{f_conv.shape[0]}\033[0m')
        print(f'    {unique_x_best.shape=}, {unique_f_conv.shape=}, {unique_f_best.shape=}')
        input('Press Enter to continue...')

        x_best = x_best[i_f_conv, :]
        f_best = f_best[i_f_conv]
        f_conv = f_conv[i_f_conv, :]

    # if i_x_best.size < x_best.shape[0]:
    #     duplicate_mask = np.ones(x_best.shape[0], np.bool_)
    #     duplicate_mask[i_x_best] = 0
    #     duplicate_x_best = x_best[duplicate_mask]
    #     n_duplicates_x_best = np.sum(duplicate_mask)
    #     print(f'\033[91m    Duplicates detected in x_best {np.sum(duplicate_mask)}/{x_best.shape[0]}\033[0m')
    #     print(f'    {unique_x_best.shape=}, {unique_f_conv.shape=}, {unique_f_best.shape=}')
    #     # input('Press Enter to continue...')

    return n_duplicates_f_conv, n_duplicates_x_best, x_best, f_best, f_conv

def check_pairs(x_best, f_best, f_conv):
    eps_max = 0.01
    eps_min = -2.0
    discard_count_max = 0
    discard_count_min = 0
    # d = np.array([2 * (f1 - f2) / (np.abs(f1) + np.abs(f2)) for f1, f2 in zip(f_best, f_conv[:, -1])])
    d = np.array([2 * (f1 - f2) / (np.average(np.abs(f_best))) for f1, f2 in zip(f_best, f_conv[:, -1])])

    is_valid = np.ones_like(d, dtype=bool)
    # if np.max(d) > eps_max:
    #     print(f'\033[93m    Convergence f_conv is better (smaller) than f_best value\033[0m')
    #     print(f'   {d.min()=:.6e}, {d.max()=:.6e}, {np.sum(d > 0)=}')
    #     # input(d)
    #
    #     for i in range(d.size):
    #         if d[i] <= eps_max:
    #             continue
    #         # D = 2 * (f_conv[i, :] - f_best[i]) / (np.abs(f_conv[i, :]) + np.abs(f_best[i]))
    #         D = 2 * (f_conv[i, :] - f_best[i]) / (np.average(np.abs(f_best)))
    #         i_invalid = D > 0
    #
    #         if np.sum(i_invalid) > 5:
    #             discard_count_max += 1
    #             print(f'   run {i:03d}: {f_best[i]}, {f_conv[i, -1]} [\033[91m{d[i]:.6e}\033[0m] invalid values {np.sum(i_invalid)}')
    #             is_valid[i] = False
    #
    #         # input('Press Enter to continue.')
    #
    #     if discard_count_max > 0:
    #         print(f'\033[91m    Sever f_best/f_conv mismatch ({eps_max=})! Number of runs to be discarded: {discard_count_max}\033[0m')
    #         # input('Press Enter to continue.')

    if np.min(d[:-1]) < eps_min:
        print(f'\033[93m    Convergence f_conv is greater than f_best value\033[0m')
        print(f'   {d.min()=:.6e}, {d.max()=:.6e}, {np.sum(d > 0)=}')


        for i in range(d.size):
            if d[i] >= eps_min:
                continue
            D = 2 * (f_conv[i, :] - f_best[i]) / (np.abs(f_conv[i, :]) + np.abs(f_best[i]))
            i_invalid = D < eps_min

            # if np.sum(i_invalid) > 0:
            discard_count_min += 1
            print(f'   run {i:03d}: {f_best[i]}, {f_conv[i, -1]} [\033[91m{d[i]:.6e}\033[0m] invalid values {np.sum(i_invalid)}')
            is_valid[i] = False
            # input('Press Enter to continue.')

        if discard_count_min > 0:
            print(f'\033[91m    Sever f_best/f_conv mismatch ({eps_min=})! Number of runs to be discarded: {discard_count_min}\033[0m')
            # input('Press Enter to continue.')

    x_best = x_best[is_valid, :]
    f_best = f_best[is_valid]
    f_conv = f_conv[is_valid, :]

    return discard_count_max, discard_count_min, x_best, f_best, f_conv


if __name__ == '__main__':

    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir)
    standard_test.optimizers = indagobench.indagobench25_optimizers
    standard_test.problems = indagobench.indagobench25_problems

    discard_dict = {}

    for problem_dict in standard_test.problems:
        print()
        print(problem_dict['label'])

        problem_results = indagobench.ProblemResults(problem_dict, verbose=False)
        problem = problem_dict['class'](problem_dict['case'], problem_dict['dimensions'])
        print(f'   f_min:    {problem_results.results[indagobench.ResultsKeyPrefix._f_min]:.6e}')
        print(f'   f_rs_med: {problem_results.results[indagobench.ResultsKeyPrefix._f_rs_med]:.6e}')
        print(f'   f_med:    {problem_results.results[indagobench.ResultsKeyPrefix._f_med]:.6e}')

        total_runs, valid_runs = 0, 0
        new_results = {}

        for optimizer_dict in indagobench.indagobench25_optimizers:

            method = optimizer_dict['label']
            x_best = problem_results.results.get(indagobench.ResultsKeyPrefix.x_best + method, np.full((0, 0), np.nan))
            f_conv = problem_results.results.get(indagobench.ResultsKeyPrefix.f_conv + method, np.full((0, 0), np.nan))
            f_best = problem_results.results.get(indagobench.ResultsKeyPrefix.f_best + method, np.full((0,), np.nan))
            print(f' - {method}: {x_best.shape=}, {f_best.shape=}, {f_conv.shape=},')

            discard_items = discard_dict.get(method, [])
            if f_best.size == 0:
                print(f' - no results, skipping.')
                continue

            n, x_best, f_best, f_conv = check_shapes(x_best, f_best, f_conv)
            if n > 0:
                discard_items.append((problem_dict['label'], 'shape', n))
                print(f' - {method}: {x_best.shape=}, {f_best.shape=}, {f_conv.shape=},')

            check_nans(x_best, f_best, f_conv)

            if method not in 'STOGO SRACOS':
                dupf, dupx, x_best, f_best, f_conv = check_duplicates(x_best, f_best, f_conv)
            if dupf > 0:
                discard_items.append((problem_dict['label'], 'dupf', dupf))
            if dupx > 0:
                discard_items.append((problem_dict['label'], 'dupx', dupx))

            dmax, dmin, x_best, f_best, f_conv = check_pairs(x_best, f_best, f_conv)
            # dmax, dmin = 0, 0

            if dmax > 0:
                discard_items.append((problem_dict['label'], 'dmax', dmax))
            if dmin > 0:
                discard_items.append((problem_dict['label'], 'dmmin', dmin))

            if len(discard_items) > 0:
                discard_dict[method] = discard_items

            new_results[indagobench.ResultsKeyPrefix.x_best + method] = x_best
            new_results[indagobench.ResultsKeyPrefix.f_best + method] = f_best
            new_results[indagobench.ResultsKeyPrefix.f_conv + method] = f_conv
            if indagobench.ResultsKeyPrefix.t_cpu + method in problem_results.results.keys():
                new_results[indagobench.ResultsKeyPrefix.t_cpu + method] =  problem_results.results[indagobench.ResultsKeyPrefix.t_cpu + method]

            # print(f'{n=}, {dupf=}, {dmax=}, {dmin=}')
            # if n + dupf + dmax + dmin > 0:
            #     print(f' - New shapes: \033[94m{x_best.shape=}\033[0m, \033[94m{f_best.shape=}\033[0m, \033[94m{f_conv.shape=}\033[0m,')

        new_results[indagobench.ResultsKeyPrefix.f_sampling] = problem_results.results[indagobench.ResultsKeyPrefix.f_sampling]
        new_results[indagobench.ResultsKeyPrefix.t_sampling] = problem_results.results[indagobench.ResultsKeyPrefix.t_sampling]

        problem_results.results = new_results
        problem_results.update_referent_values()
        # problem_results.save_results()
        # input('?')

    problem_runs_discarded = {}
    print('Summary:')
    if len(discard_dict) == 0:
        print('\033[92mNo problems discarded.\033[0m')
    for k, v in discard_dict.items():
        print(f'   \033[93m{k}\033[0m: \033[93m{np.sum([vv[2] for vv in v])}\033[0m in \033[93m{len(v)}\033[0m problems {v}')

        for vv in v:
            d = problem_runs_discarded.get(vv[0], 0)
            problem_runs_discarded[vv[0]] = d + vv[2]

    for k, v in problem_runs_discarded.items():
        print(k, v)
