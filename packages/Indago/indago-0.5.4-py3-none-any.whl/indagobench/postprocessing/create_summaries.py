"""
A script that creates text summary files for all indagobench25 problems.
"""
if __name__ == '__main__':

    import indagobench
    import os

    if not os.path.exists(f'{indagobench._local_paths.indagobench25_results_dir}/summary'):
        os.mkdir(f'{indagobench._local_paths.indagobench25_results_dir}/summary')

    # Create summaries
    # for problem_dict in indagobench.indagobench25_problems:
    for problem_dict in [indagobench.get_problem_dict('EC_gaussian1_50D')]:
        fr = indagobench.ProblemResults(problem_dict, verbose=True)
        # fr.optimizers = ['NM']
        fr.write_summary(f'{indagobench._local_paths.indagobench25_results_dir}/summary/summary_{problem_dict["label"]}.txt')