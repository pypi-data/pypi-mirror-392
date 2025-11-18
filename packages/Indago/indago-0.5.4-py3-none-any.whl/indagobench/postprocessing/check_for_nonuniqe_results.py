"""
A script that creates convergence plots for all indagobench25 problems.
"""

if __name__ == '__main__':

    import os
    import numpy as np
    import indagobench
    from indagobench.problems._flow_fit import FF_problems_dict_list
    # Create summaries
    duplicate_count = {}

    # for problem_dict in FF_problems_dict_list:
    for problem_dict in indagobench.indagobench25_problems:
        fr = indagobench.ProblemResults(problem_dict, verbose=False)
        problem = problem_dict['class'](problem_dict['case'], problem_dict['dimensions'])

        for optimizer in indagobench.indagobench25_optimizers:
            k_new = indagobench.ResultsKeyPrefix.f_conv + optimizer['label']
            k_f_best_old = 'f ' + optimizer['label']
            if k_f_best_old not in fr.results.keys():
                continue

            f_shape = fr.results['f ' + optimizer['label']].shape
            x_shape = fr.results['x ' + optimizer['label']].shape
            if x_shape[0] != f_shape[0]:
                print(f'{optimizer["label"]} on {problem_dict["label"]} => {f_shape=}, {x_shape=}')

            out_of_bounds = 0
            for i in range(x_shape[0]):
                x_best = fr.results['x ' + optimizer['label']][i, :]
                if np.any(x_best < problem.lb) or np.any(x_best > problem.ub):
                    out_of_bounds += 1
            if out_of_bounds > 0:
                print(f'{optimizer["label"]} on {problem_dict["label"]} out of bounds ({out_of_bounds=})!')

            # continue
            a = np.copy(fr.results[k_f_best_old])
            mask = np.isnan(a)
            a[mask] = -2e12

            # for i in range(a.shape[0]):
            #     print(a[i, :])

            # print(f'{a.shape=}')
            unq, count = np.unique(a, axis=0, return_counts=True)
            # print(unq[count>1])
            # print(count)
            #n = np.sum(count>=10)
            if not os.path.exists(f'{indagobench._local_paths.indagobench25_results_dir}/non_unique'):
                os.mkdir(f'{indagobench._local_paths.indagobench25_results_dir}/non_unique')
            if unq.shape[0] < a.shape[0]:
                print(f"{problem_dict['label']:20s} {optimizer['label']:10s} total results: {a.shape[0]:5d}, "
                      f"unique results: {unq.shape[0]:5d}, duplicates:{a.shape[0] - unq.shape[0]:5d}")

                # print(count.shape, ii.shape, ii)
                duplicates = []
                for i1 in np.where(count >= 1)[0]:
                    for i2 in range(a.shape[0]):
                        if np.all(unq[i1, :] == a[i2, :]):
                            duplicates.append(i2)
                # print(len(duplicates), duplicates)

                v = (problem_dict['label'], a.shape[0] - unq.shape[0])
                if optimizer['label'] in duplicate_count.keys():
                    duplicate_count[optimizer['label']].append(v)
                else:
                    duplicate_count[optimizer['label']] = [v]

                if False:
                # if problem_dict['label'] == 'CEC_F3_50D' and
                # if optimizer['label'] == 'MSGD':
                    file_name = f'{indagobench._local_paths.indagobench25_results_dir}/non_unique/{problem_dict["label"]}_{optimizer["label"]}.txt'
                    if k_old in fr.results.keys():
                        np.savetxt(file_name, fr.results[k])

                    # input(f'Press Enter to clean up duplicates from {problem_dict["label"]} + {optimizer["label"]}')
                    unq[unq==-2e12] = np.nan
                    unq[unq==-2] = np.nan
                    fr.results[k] = unq
                    # fr.results.pop(k)
                    fr.save_results()


    print(f'\nMethod    Total duplicates      Sorted occurrences')
    print('-' * 100)
    for method_label, method_data in duplicate_count.items():
        all_duplicates = [duplicates for (problem_label, duplicates) in method_data]
        total_duplicates = np.sum(all_duplicates)
        score = f'{total_duplicates} in {len(method_data)} problem' + ('s' if total_duplicates > 1 else '')
        s = f'{method_label:10s}{score:<22s}'
        i_sort = np.argsort(all_duplicates)[::-1]

        p_list = []
        for i_problem in i_sort:
            #  v = (problem_dict['label'], a.shape[0] - unq.shape[0])
            problem_label, duplicates = method_data[i_problem]
            ss = f'{problem_label}: '
            if duplicates > 50:
                ss += f'\033[91m{duplicates}\033[0m'
            elif duplicates > 20:
                ss += f'\033[93m{duplicates}\033[0m'
            else:
                ss += f'\033[92m{duplicates}\033[0m'
            p_list.append(ss)
        s += ' '.join(p_list)

        print(s)
    print('-' * 100)