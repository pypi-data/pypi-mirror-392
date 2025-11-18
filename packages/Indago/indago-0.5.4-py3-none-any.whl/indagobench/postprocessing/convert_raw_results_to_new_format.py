import sys
sys.path.append('..')
sys.path.append('../..')
import os
import indagobench
import numpy as np


if __name__ == '__main__':

    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir,
                                             convergence_window=10, eps_max=0.1, runs_min=10,
                                             )
    standard_test.optimizers = indagobench.indagobench25_optimizers
    standard_test.problems = indagobench.indagobench25_problems

    old_raw_dir = f'/home/stefan/tmp/indagobench_results/old_raw/'
    new_raw_dir = f'/home/stefan/tmp/indagobench_results/raw/'

    for problem_dict in standard_test.problems:
        print()
        print(problem_dict['label'])
        new_results_filename = new_raw_dir + problem_dict['label'] + '.npz'
        if os.path.exists(new_results_filename):
            print(f'   Already converted: {new_results_filename}')
            continue

        problem = problem_dict['class'](problem_dict['case'], problem_dict['dimensions'])

        results_filename = old_raw_dir + problem_dict['label'] + '.npz'
        print(f'   Reading {results_filename}')
        raw_results = np.load(results_filename)


        new_results = {}

        if 'f_sampling' in raw_results.keys():
            new_results[indagobench.ResultsKeyPrefix.f_sampling] = raw_results['f_sampling']
            print(f' - f_sampling: {new_results[indagobench.ResultsKeyPrefix.f_sampling].shape}')

        if 't_sampling' in raw_results.keys():
            new_results[indagobench.ResultsKeyPrefix.t_sampling] = raw_results['t_sampling']

        for optimizer_dict in indagobench.indagobench25_optimizers:

            method = optimizer_dict['label']

            x_best = raw_results.get('x ' + method, np.full((0,0), np.nan))
            f_conv = raw_results.get('f ' + method, np.full((0,0), np.nan))
            f_best = np.array([problem(x) for x in x_best])

            new_results[indagobench.ResultsKeyPrefix.x_best + method] = x_best
            new_results[indagobench.ResultsKeyPrefix.f_best + method] = f_best
            new_results[indagobench.ResultsKeyPrefix.f_conv + method] = f_conv
            if 't ' + method in raw_results.keys():
                new_results[indagobench.ResultsKeyPrefix.t_cpu + method] = raw_results['t ' + method]

            print(f' - {method}: {x_best.shape=}, {f_best.shape=}, {f_conv.shape=}')

        problem_results = indagobench.ProblemResults(problem_dict, verbose=False)
        problem_results.results = new_results
        problem_results.update_referent_values(verbose=True)
        problem_results.save_results()

