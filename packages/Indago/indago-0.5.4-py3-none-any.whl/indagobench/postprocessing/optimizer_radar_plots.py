"""
A script that creates image containing 6-axis radar plots for all indagobench25 optimizers.
"""

if __name__ == '__main__':

    import indagobench
    import numpy as np
    import matplotlib.pyplot as plt

    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir)
    standard_test.optimizers = indagobench.indagobench25_optimizers
    standard_test.problems = indagobench.indagobench25_problems

    props = dict(boxstyle='square,pad=0.3', facecolor='silver', alpha=0.6, edgecolor='none')

    ncols = 5
    nrows = 4
    fig, axes = plt.subplots(ncols=ncols, nrows=nrows,
                             figsize=(ncols * 2.45, nrows * 2.4 + 1),
                             )
    plt.subplots_adjust(hspace=0, wspace=0,)
    axes = np.ravel(axes)
    print(f'\n\nNumber of functions: {len(standard_test.problems)}')
    print(f'{"Optimizer":20s} {"G10%50%100% avg.":>15s} {"G100%":>12s}')
    for i, opt_dict in enumerate(np.array(standard_test.optimizers)):
        standard_test.prepare_radar_plot(axes[i], cat_labels=True)
        standard_test.optimizer_profile(opt_dict,
                                        ax_radar=axes[i],
                                        axes_hist=None,
                                        optimizer_label=True)
    for ax in axes[len(standard_test.optimizers):]:
        ax.axis('off')
        ax.set_facecolor("whitesmoke")
        for spine in ax.spines.values():
            spine.set_visible(False)
    fig.suptitle(f'Indagobench25 standard test ({len(standard_test.problems)} functions)', fontsize=12) # bbox=props,
    plt.subplots_adjust(bottom=0, top=0.95, left=0, right=1)
    plt.savefig(f'{standard_test.results_dir}/other/radar_plot_all_optimizers.png', dpi=300)