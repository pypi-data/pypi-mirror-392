"""
A script that creates convergence plots for all indagobench25 problems.
"""
if __name__ == '__main__':

    import os
    import indagobench
    # Create summaries

    indagobench_labels = [problem_dict['label'] for problem_dict in indagobench.indagobench25_problems]
    raw_dir = f'{indagobench._local_paths.indagobench25_results_dir}/raw/'

    def check_raw_file(file_name):
        if file_name.endswith('.npz'):
            if file_name[:-4] in indagobench_labels:
                return True
        return False


    for file_name in os.listdir(raw_dir):
        # print(f'{file_name=}', end=' ')

        if check_raw_file(file_name):
            ...
            # print('OK')
        else:
            # print('FAILED')
            print(f'{file_name=}')
            # input('Press Enter to continue...')
            os.remove(raw_dir + file_name)

        # fr.make_full_convergence_figure(f'{indagobench._local_paths.indagobench25_results_dir}/convergence/full_conv_{problem_dict["label"]}.png')
