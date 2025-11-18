"""
A script that renames the optimizer (optimizer label) for all indagobench25 problems.
"""
if __name__ == '__main__':

    import indagobench
    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir)
    standard_test.optimizers = indagobench.indagobench25_optimizers
    standard_test.problems = indagobench.indagobench25_problems

    M_NAME = {'RS': 'RS', 'L-BFGS-B': 'LBFGSB', 'ZOOpt': 'SRACOS', 'DA': 'DA', 'ESCH': 'ESCH', 'CRS': 'CRS',
              'STOGO': 'STOGO', 'NM GaoHan': 'NM', 'MSGD': 'MSGD', 'PSO': 'PSO', 'FWA': 'FWA', 'SSA': 'SSA', 'BA': 'BA',
              'GWO': 'GWO', 'EFO': 'EFO', 'MRFO': 'MRFO', 'ABC': 'ABC', 'DE LSHADE': 'LSHADE', 'GA': 'GA',
              'CMAES': 'CMAES'}

    for old, new in M_NAME.items():
        # print(f'Replacing {old} with {new}')
        standard_test.rename_optimizer(old, new)
        # print(f'Done replacing {old} with {new}')
        # input('?')


     # Create summaries
    # for problem_dict in indagobench.indagobench25_problems:
    #     fr = indagobench.ProblemResults(problem_dict, verbose=False)
    #     fr.write_summary(f'{indagobench._local_paths.indagobench25_results_dir}/summary/summary_{problem_dict["label"]}.txt')