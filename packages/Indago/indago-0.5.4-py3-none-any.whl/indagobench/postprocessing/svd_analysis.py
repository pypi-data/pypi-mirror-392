"""
A script that creates plots of convergence.
"""
import numpy as np
from matplotlib import pyplot as plt

if __name__ == '__main__':

    import indagobench
    from indagobench.problems._flow_fit import FF_problems_dict_list
    from sklearn.decomposition import PCA

    # Create summaries
    for problem_dict in FF_problems_dict_list:
    # for problem_dict in indagobench.indagobench25_problems:
        pr = indagobench.ProblemResults(problem_dict)

        # fig, ax = plt.subplots()
        fig = plt.figure(figsize=(12, 12))
        ax3 = fig.add_axes([0, 0, 1, 1], projection='3d')
        # ax_sampling_convergence = fig.add_axes([X[0], Y[0], W[0], H[0]], frameon=True, facecolor='r')

        for optimizer_dict in indagobench.indagobench25_optimizers:
            x_best = pr.results[indagobench.ResultsKeyPrefix.x_best + optimizer_dict['label']]
            f_best = pr.results[indagobench.ResultsKeyPrefix.f_best + optimizer_dict['label']]
            G_best = pr.calc_g(f_best)
            print(f'{x_best.shape=}')

            pca = PCA(n_components=3)
            pca.fit(x_best)
            print((f'{G_best.min()=}, {G_best.max()=}'))
            y_best = pca.transform(x_best)
            print(f'{y_best.shape=}')
            G_best[G_best<-1] = -1
            scatter = ax3.scatter(y_best[:,0], y_best[:,1], y_best[:,2],
                                 c=G_best, cmap=plt.cm.Spectral_r, vmin=-1, vmax=1,
                                 s= 2*(1+G_best),
                                 alpha=0.5*(1+G_best),
                                 label=optimizer_dict['label'])
            ax3.axis('equal')

        ax3.plot(np.array([-1, 1]) * pca.explained_variance_ratio_[0], [0, 0], [0, 0], lw=2, c='r')
        ax3.plot([0, 0], np.array([-1, 1]) * pca.explained_variance_ratio_[1], [0, 0], lw=2, c='b')
        ax3.plot([0, 0], [0, 0], np.array([-1, 1]) * pca.explained_variance_ratio_[2], lw=2, c='g')
        plt.colorbar(scatter, ax=ax3)
        # ax3.set_axis_off()
        RADIUS = 1
        ax3.set_xlim3d(-RADIUS / 2, RADIUS / 2)
        ax3.set_zlim3d(-RADIUS / 2, RADIUS / 2)
        ax3.set_ylim3d(-RADIUS / 2, RADIUS / 2)
        # break
    plt.show()
    # break



"""
Old SVD anaylsis
"""

# import os.path
# import sys
# sys.path.append('../..')
#
# import indagobench
# import matplotlib.pyplot as plt
# from matplotlib.gridspec import GridSpec
# import numpy as np
#
# if __name__ == '__main__':
#
#     standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir,
#                                              # convergence_window=10, eps_max=0.1, runs_min=10,
#                                              )
#     standard_test.optimizers = indagobench.indagobench25_optimizers
#     standard_test.problems = indagobench.indagobench25_problems
#
#     n_functions = len(standard_test.problems)
#     n_optimizers = len(standard_test.optimizers)
#     optimizer_labels = [optimizer_dict['label'] for optimizer_dict in standard_test.optimizers]
#     problem_labels = [problem_dict['label'] for problem_dict in standard_test.problems]
#
#     npz_filename = indagobench._local_paths.indagobench25_results_dir + '/svd.npz'
#     if os.path.exists(npz_filename):
#         G = np.load(npz_filename)['G']
#     else:
#         G = np.full([n_functions, n_optimizers], np.nan)
#         for i_problem, problem_dict in enumerate(standard_test.problems):
#             results = indagobench.ProblemResults(problem_dict)
#             # print(results.keys())
#             for i_optimizer, optimizer_dict in enumerate(standard_test.optimizers):
#                 f = results.results[indagobench.ResultsKeyPrefix.f_best + optimizer_dict['label']]
#                 f = f[np.logical_not(np.isnan(f))]
#                 g = results.calc_g(f)
#
#                 g = g[np.logical_not(np.isnan(g))]
#                 # if np.any(np.isnan(f)):
#                 #     print(f'{optimizer_dict["label"]=}')
#                 #     input('Press Enter to continue...')
#                 # if np.any(np.isnan(g)):
#                 #     print(f'{optimizer_dict["label"]=}')
#                 #     print(f'{f.shape=}')
#                 #     print(f'{g.shape=}')
#                 #     for _f, _g in zip(f, g):
#                 #         print(_f, _g)
#                 #     input('Press Enter to continue...')
#                 G[i_problem, i_optimizer] = np.median(g)
#         np.savez_compressed(npz_filename, G=G)
#
#     print(f'{G.shape=}')
#     print(f'{np.any(np.isnan(G))=}')
#     print(f'{np.min(G)=}')
#     print(f'{np.max(G)=}')
#
#     # SVD
#     U, S, V = np.linalg.svd(G, full_matrices=False)
#
#     k = 5
#
#     fig = plt.figure(figsize=(24, (k + 1) * 1.2), layout="constrained")
#     gs = GridSpec(nrows=k+1, ncols=2, figure=fig,
#                   width_ratios=[1, 8])
#
#     ax_s = fig.add_subplot(gs[0, 0])
#     ax_s.bar(np.arange(k) + 1, np.cumsum(S[:k] / np.sum(S)), color='grey')
#     ax_s.bar(np.arange(k) + 1, S[:k] / np.sum(S), color=[f'C{i}' for i in range(k)])
#     # ax_s.axis('off')
#     # ax_s.get_xaxis().set_visible(False)
#     # ax_s.get_yaxis().set_visible(False)
#     ax_s.spines['top'].set_visible(False)
#     ax_s.set_ylim(0, 1)
#     ax_s.tick_params(top='off', bottom='off', left='off', right='off', labelleft='on', labelbottom='on')
#     ax_s.tick_params(labelsize=4)
#     ax_s.grid(ls=':', c='lightgray', lw=0.3)
#
#     ax_s.set_frame_on(False)
#     ax_s.set_facecolor("whitesmoke")
#
#     ax_g = fig.add_subplot(gs[0, 1])
#     ax_g.matshow(G.T)
#     ax_g.axis('off')
#     ax_g.set_facecolor("whitesmoke")
#
#     print(f'{V.shape=}')
#     print(f'{U.shape=}')
#     for i in range(k):
#         if np.sum(V[i, :]) < 0:
#             U[:, i] *= -1
#             V[i, :] *= -1
#         v = V[i, :]
#         u = U[:, i]
#
#         ax_v = fig.add_subplot(gs[1 + i, 0])
#         ax_v.set_xlim(-0.5, n_optimizers - 0.5)
#         ax_v.set_frame_on(False)
#         ax_v.set_facecolor("whitesmoke")
#         ax_v.axhline(lw=0.3, c='k')
#         ax_v.bar(optimizer_labels, v, color=f'C{i}')
#         if i + 1 == k:
#             ax_v.tick_params(axis='x', rotation=90, labelsize=4)
#             ax_v.set_yticks([])
#         else:
#             ax_v.set_xticks([])
#             ax_v.axis('off')
#
#         ax_u = fig.add_subplot(gs[1 + i, 1])
#         ax_u.set_xlim(-0.5, n_functions - 0.5)
#         ax_u.set_frame_on(False)
#         ax_u.set_facecolor("whitesmoke")
#         ax_u.axhline(lw=0.3, c='k')
#         ax_u.bar(problem_labels, u, color=f'C{i}')
#         if i + 1 == k:
#             ax_u.tick_params(axis='x', rotation=90, labelsize=4)
#             ax_u.set_yticks([])
#         else:
#             ax_u.set_xticks([])
#             ax_u.axis('off')
#
#     plt.savefig(indagobench._local_paths.indagobench25_results_dir + '/indagobench_pca.pdf')
#     plt.show()