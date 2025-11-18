"""
A script that creates convergence plots for all indagobench25 problems.
"""
if __name__ == '__main__':

    import indagobench
    from indagobench.problems._hydraulic_network import HN_problems_dict_list
    # Create summaries
    # for problem_dict in HN_problems_dict_list:
    for problem_dict in indagobench.indagobench25_problems:
        fr = indagobench.ProblemResults(problem_dict)
        fr.make_full_convergence_figure(f'{indagobench._local_paths.indagobench25_results_dir}/convergence/full_conv_{problem_dict["label"]}.png',
                                        header_plots=True)
