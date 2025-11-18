import numpy as np
import matplotlib.pyplot as plt
import os
import indagobench

from _local_paths import indagobench25_results_dir as PATH
from _problem_results import ProblemResults

import warnings
warnings.filterwarnings('ignore', r'Input line 1*')
warnings.filterwarnings('ignore', r'All-NaN slice encountered')

# Define your custom linear colormap
import matplotlib as mpl
cmap_custom = mpl.colors.LinearSegmentedColormap.from_list('indigo-indianred-olivedrab',
                                                           ['indigo', 'indianred', 'olivedrab'])
cmap_custom_half = mpl.colors.LinearSegmentedColormap.from_list('firebrick-greenyellow',
                                                           ['firebrick', 'greenyellow'])


METHODS_OLDORDER = ['RS', 'L-BFGS-B', 'ZOOpt', 'DA', 'ESCH', 'CRS', 'STOGO', 'NM GaoHan', 'MSGD', 'PSO',
           'FWA', 'SSA', 'BA', 'GWO', 'EFO', 'MRFO', 'ABC', 'DE LSHADE', 'GA', 'CMAES']

METHODS = ['RS', 'L-BFGS-B', 'NM GaoHan', 'MSGD', 'ZOOpt', 'DA', 'CRS', 'STOGO', 'EFO', 'PSO', 'ABC',
           'SSA', 'BA', 'GWO', 'MRFO', 'FWA', 'DE LSHADE', 'GA', 'ESCH', 'CMAES']

M_NAME = {'RS': 'RS', 'L-BFGS-B': 'LBFGSB', 'ZOOpt': 'SRACOS', 'DA': 'DA', 'ESCH': 'ESCH', 'CRS': 'CRS',
          'STOGO': 'STOGO', 'NM GaoHan': 'NM', 'MSGD': 'MSGD', 'PSO': 'PSO', 'FWA': 'FWA', 'SSA': 'SSA', 'BA': 'BA',
          'GWO': 'GWO', 'EFO': 'EFO', 'MRFO': 'MRFO', 'ABC': 'ABC', 'DE LSHADE': 'LSHADE', 'GA': 'GA', 'CMAES': 'CMAES'}

SIMULATION_BASED = 'AD HN SFD FF'.split(' ')

DATA = {fname: {'name': fname[8:-4], 'D': int(fname[:-5].split('_')[-1])} for fname in os.listdir(PATH + r"\summary")}

M_REORDER = [METHODS_OLDORDER.index(m) for m in METHODS]


def G_of_D():

    print('\n*** G(D) plot')

    res = {m: {'G_100': [], 'D': []} for m in METHODS}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            res[METHODS[i]]['G_100'].append(G_100[i])
            res[METHODS[i]]['D'].append(info['D'])

    x = np.min(res['RS']['D'])
    colors = plt.cm.jet(np.linspace(0, 1, len(METHODS)))
    plt.figure(figsize=(8, 16))
    for m, c in zip(METHODS, colors):
        pearson = np.corrcoef(res[m]['D'], res[m]['G_100'])[0, 1]
        reg = np.polynomial.Polynomial.fit(res[m]['D'], res[m]['G_100'], deg=1)
        # plt.plot(res[m]['D'], res[m]['G_100'], 'o', alpha=0.9, color=c)
        d = np.linspace(np.min(res[m]['D']), np.max(res[m]['D']), 50)
        plt.plot(d, reg(d), label=M_NAME[m], color=c)
        plt.text(x, reg(x), f'{M_NAME[m]} r={pearson:.2f}', color=c, fontsize=8,
                 bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))
        x += (d[-1] - d[0]) / len(METHODS)
    # plt.legend()
    plt.xlabel(r'$D$')
    plt.ylabel(r'$\mathbb{G}$')
    plt.title(r'$\mathbb{G}$ vs. $D$')
    plt.tight_layout()
    plt.savefig('post_analysis_G(D).png')


def G_of_M():

    print('\n*** G(M) plot')

    res = {m: {'G_100': [], 'M': []} for m in METHODS}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            res[METHODS[i]]['G_100'].append(G_100[i])
            res[METHODS[i]]['M'].append((1 - G_100[1]) / 2)

    fig, axes = plt.subplots(ncols=5, nrows=4, figsize=(5 * 0.84, 4 * 0.84 + 1), dpi=300)
    for i in range(len(METHODS)):
        m = METHODS[i]
        ax = axes.flat[i]
        pearson = np.corrcoef(res[m]['M'], res[m]['G_100'])[0, 1]
        reg = np.polynomial.Polynomial.fit(res[m]['M'], res[m]['G_100'], deg=1)
        ax.scatter(res[m]['M'], res[m]['G_100'], s=1.5, alpha=0.4,
                   norm=plt.Normalize(vmin=-1, vmax=1),
                   c=np.array(res[m]['G_100']), cmap=cmap_custom) # 'RdYlGn'
        m_ = np.linspace(np.min(res[m]['M']), np.max(res[m]['M']), 50)
        ax.plot(m_, reg(m_), label=fr'{M_NAME[m]}\n $r={pearson:.2f}$', color='black', linewidth=1)
        ax.text(0, -0.9, f'$r={pearson:.2f}$' if m != 'RS' else '', fontsize=6)
        ax.axhline(0, color='grey', linestyle=':')
        ax.set_title(f'{M_NAME[m]}', fontsize=8)
        ax.set_ylim(-1, 1)
        ax.tick_params(bottom=False, labelbottom=False, left=False, labelleft=False)
    # fig.suptitle(r'$G_{100}$ vs. $M$')
    fig.tight_layout()
    fig.savefig('post_analysis_G(M).png')


def CEC_vs_nonCEC():

    print('\n*** CEC vs non-CEC histogram')

    res = {'G_100_cec': [], 'G_100_noncec': []}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        if info['name'].startswith('CEC'):
            res['G_100_cec'] += G_100[1:].tolist()  # include every result
            # res['G_100_cec'].append(np.average(G_100[1:]))  # take mean result
        else:
            res['G_100_noncec'] += G_100[1:].tolist()  # include every result
            # res['G_100_noncec'].append(np.average(G_100[1:]))  # take mean result

    plt.figure(figsize=(12, 8))
    plt.hist(res['G_100_cec'], bins=50, label='CEC', alpha=0.5, color='green')
    plt.hist(res['G_100_noncec'], bins=50, label='non-CEC', alpha=0.5, color='red')
    med_cec = np.median(res['G_100_cec'])
    med_noncec = np.median(res['G_100_noncec'])
    plt.axvline(med_cec, color='green', linestyle='--', linewidth=3, label='median CEC')
    plt.axvline(med_noncec, color='red', linestyle='--', linewidth=3, label='median non-CEC')
    plt.xlim([-1, 1])
    plt.legend()
    plt.xlabel(r'$\mathbb{G}$')
    plt.ylabel(r'f')
    plt.title(rf'CEC vs non-CEC ($\Delta \mathbb{{G}} = {med_cec - med_noncec:.2f}$)')
    plt.tight_layout()
    plt.savefig('post_analysis_CEC.png')


def D_hist():

    print('\n*** D histogram')

    D = []
    for _, info in DATA.items():
        D.append(info['D'])

    plt.figure(figsize=(6, 2), dpi=300)
    plt.hist(D, bins=50, color='violet')
    plt.xlim(0, 60)
    plt.xlabel(r'$D$')
    plt.ylabel('number of functions')
    plt.tight_layout()
    plt.savefig('post_analysis_Dhist.png')


def H_hist():

    print('\n*** function hardness H = M*D histogram')

    D, M = [], []
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        D.append(info['D'])
        M.append((1 - G_100[1]) / 2)
    H = np.array(M) * np.array(D)

    plt.figure(figsize=(4, 2))
    plt.hist(H, bins=60, color='tomato')
    plt.xlim(0, 60)
    plt.xlabel(r'function hardness $H = M \cdot D$')
    plt.ylabel(r'number of functions')
    plt.tight_layout()
    plt.savefig('post_analysis_Hhist.png')


def G_of_H():

    print('\n*** G(H) plots')

    res = {m: {'G_100': [], 'H': []} for m in METHODS}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            res[METHODS[i]]['G_100'].append(G_100[i])
            res[METHODS[i]]['H'].append(info['D'] * (1 - G_100[1]) / 2)
    fig, axes = plt.subplots(ncols=5, nrows=4, figsize=(5 * 2.4, 4 * 2.4 + 1))
    for i in range(len(METHODS)):
        m = METHODS[i]
        ax = axes.flat[i]
        pearson = np.corrcoef(res[m]['H'], res[m]['G_100'])[0, 1]
        reg = np.polynomial.Polynomial.fit(res[m]['H'], res[m]['G_100'], deg=1)
        ax.scatter(res[m]['H'], res[m]['G_100'], alpha=0.4,
                   norm=plt.Normalize(vmin=-1, vmax=1),
                   c=np.array(res[m]['G_100']), cmap='RdYlGn')
        m_ = np.linspace(np.min(res[m]['H']), np.max(res[m]['H']), 50)
        ax.plot(m_, reg(m_), label=fr'{M_NAME[m]}\n $r={pearson:.2f}$', color='black', linewidth=3)
        ax.axhline(0, color='grey', linestyle=':')
        ax.title.set_text(f'{M_NAME[m]}  $r={pearson:.2f}$' if m != 'RS' else 'RS')
        ax.set_ylim(-1, 1)
        ax.tick_params(bottom=False, labelbottom=False, left=False, labelleft=False)
    # fig.suptitle(r'$\mathbb{G}$ vs. $H$')
    fig.tight_layout()
    fig.savefig('post_analysis_G(H).png')


def method_performance():

    print('\n*** method performance bar plots')

    wins, succ, lasts, fail, wins90perc, succ90perc = {m: 0 for m in METHODS}, {m: 0 for m in METHODS}, \
        {m: 0 for m in METHODS}, {m: 0 for m in METHODS}, {m: 0 for m in METHODS}, {m: 0 for m in METHODS}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        wins[METHODS[np.argmax(G_100)]] += 1
        lasts[METHODS[np.argmin(G_100)]] += 1
        for i in range(len(METHODS)):
            if G_100[i] > 0.9:
                succ[METHODS[i]] += 1
            elif G_100[i] < 0:
                fail[METHODS[i]] += 1

    fig, ax = plt.subplots(ncols=2, nrows=1, figsize=(6.4, 4.5), dpi=300)
    fig.subplots_adjust(wspace=0)
    # print('catastrophic %:', list([M_NAME[m] for m in METHODS]), '\n', (100 * np.array(list(fail.values())) / len(DATA)))
    ax[0].barh(list([M_NAME[m] for m in METHODS]), (100 * np.array(list(fail.values())) / len(DATA)),
               color='indigo', alpha=0.3, zorder=3,
               label=r'catastrophic ($\mathbb{G} < 0$)')
    # print('worst %:', list([M_NAME[m] for m in METHODS]), '\n', (100 * np.array(list(lasts.values())) / len(DATA)))
    ax[0].barh(list([M_NAME[m] for m in METHODS]), (100 * np.array(list(lasts.values())) / len(DATA)),
               color='indigo', zorder=3,
               label=r'worst ($\mathbb{G} = \min ~\mathbb{G}$)')
    ax[0].set_xlim(0, 55)
    ax[0].set_xticks(np.arange(0, 55, 10))
    ax[0].invert_xaxis()
    ax[0].invert_yaxis()
    ax[0].grid(axis='x', linestyle=':', linewidth=1, color='lightgrey', zorder=2.5)
    # print('excellent %:', list([M_NAME[m] for m in METHODS]), '\n', (100 * np.array(list(succ.values())) / len(DATA)))
    ax[1].barh(list([M_NAME[m] for m in METHODS]), (100 * np.array(list(succ.values())) / len(DATA)),
               color='olivedrab', alpha=0.3, zorder=3,
               label=r'excellent ($\mathbb{G} > 0.9$)')
    # print('best %:', list([M_NAME[m] for m in METHODS]), '\n', (100 * np.array(list(wins.values())) / len(DATA)))
    ax[1].barh(list([M_NAME[m] for m in METHODS]), (100 * np.array(list(wins.values())) / len(DATA)),
               color='olivedrab', zorder=3,
               label=r'best ($\mathbb{G} = \max ~\mathbb{G}$)')
    ax[1].invert_yaxis()
    ax[1].set_xlim(0, 55)
    ax[1].set_xticks(np.arange(0, 55, 10))
    ax[1].set_yticks([])
    ax[1].grid(axis='x', linestyle=':', linewidth=1, color='lightgrey', zorder=2.5)
    fig.legend(loc='upper center', ncols=2, frameon=False)
    fig.supxlabel(r'relative frequency [%]')
    fig.savefig('post_analysis_method_performance.png')


def method_sets():

    print('\n*** best sets of methods')

    from itertools import combinations

    exc = {m: [] for m in METHODS}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            if G_100[i] > 0.9:
                exc[METHODS[i]].append(info['name'])

    fig = plt.figure(figsize=(6, 3), dpi=300)
    ax = fig.gca()

    scores_list = []
    combs_list = []
    for n in range(1, 6):
        combs = list(combinations(METHODS, n))
        exc_combs = {}
        for comb in combs:
            exc_combs[comb] = []
            for m in comb:
                exc_combs[comb] += exc[m]
            exc_combs[comb] = list(set(exc_combs[comb]))  # remove duplicates
        score_combs = {comb: len(funs) / len(DATA) for comb, funs in exc_combs.items()}
        best_score = 0
        best_comb = None
        for comb, score in score_combs.items():
            if score > best_score:
                best_score = score
                best_comb = comb
        print(f'{best_comb} -> G>0.9 in {best_score:.0%} test functions')
        scores_list.append(best_score)
        combs_list.append([M_NAME[m] for m in best_comb])
    comb_list_bars = [(' + ').join(l) for l in combs_list]
    print(comb_list_bars)

    ax.barh(list(range(len(comb_list_bars))), scores_list, color='indianred', alpha=0.5, zorder=3)
    for y, c in enumerate(comb_list_bars):
        ax.text(0.01, y + 0.05, f'{c} ',
                ha='left', va='center', size=10)

    exc = {m: [] for m in METHODS}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_RW = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(11,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            if G_RW[i] > 0.9:
                exc[METHODS[i]].append(info['name'])

    scores_list = []
    combs_list = []
    for n in range(1, 6):
        combs = list(combinations(METHODS, n))
        exc_combs = {}
        for comb in combs:
            exc_combs[comb] = []
            for m in comb:
                exc_combs[comb] += exc[m]
            exc_combs[comb] = list(set(exc_combs[comb]))  # remove duplicates
        score_combs = {comb: len(funs) / len(DATA) for comb, funs in exc_combs.items()}
        best_score = 0
        best_comb = None
        for comb, score in score_combs.items():
            if score > best_score:
                best_score = score
                best_comb = comb
        print(f'{best_comb} -> G_RW>0.9 in {best_score:.0%} test functions')
        scores_list.append(best_score)
        combs_list.append([M_NAME[m] for m in best_comb])
    comb_list_bars = [(' + ').join(l) for l in combs_list]
    print(comb_list_bars)

    ax.barh(list(range(len(comb_list_bars), 2*len(comb_list_bars))), scores_list, color='olivedrab', alpha=0.5, zorder=3)
    for y, c in enumerate(comb_list_bars):
        ax.text(0.01, y + len(comb_list_bars) + 0.05, f'{c} ',
                ha='left', va='center', size=10, zorder=3)
    ax.invert_yaxis()
    ax.set_xlabel('share of functions solved')
    ax.set_xlim(0, 0.7)
    ax.tick_params(left=False, labelleft=False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.grid(axis='x', linestyle=':', linewidth=1, color='lightgrey', zorder=2.5)

    fig.tight_layout()
    fig.savefig('post_analysis_method_sets.png')


def method_overlap_heatmap():

    print('\n*** method performance overlaps')

    exc = {m: [] for m in METHODS}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            if G_100[i] > 0.9:
                exc[METHODS[i]].append(info['name'])

    overlaps = np.ones((len(METHODS), len(METHODS)))
    for i, m1 in enumerate(METHODS):
        for j, m2 in enumerate(METHODS):
            if m1 != m2:
                # compute the overlap of m1 in m2
                doubles = [f for f in exc[m1] if f in exc[m2]]
                if len(exc[m1]) > 0:
                    overlaps[i, j] = len(doubles) / len(exc[m1])
                else:
                    overlaps[i, j] = 1  # placeholder for 0/0

    import seaborn as sns
    plt.figure(figsize=(6, 5), dpi=300)
    heatmap = sns.heatmap(overlaps, cmap=cmap_custom, annot=overlaps, cbar=False,  # cmap='hot_r'
                          linewidths=0.5, linecolor='k', annot_kws={"fontsize":6},
                          xticklabels=[M_NAME[m] for m in METHODS], yticklabels=[M_NAME[m] for m in METHODS])
    for _, spine in heatmap.spines.items():
        spine.set_visible(True)
    heatmap.set_ylabel('how much is this method...')
    heatmap.set_xlabel('...superseded by this method')
    plt.tight_layout()
    plt.savefig('post_analysis_overlap_heatmap.png')


def method_features():

    print('\n*** method features')

    NCOLS = 6
    pi = -1  # counting ax
    fig, ax = plt.subplots(ncols=NCOLS, nrows=1, figsize=(NCOLS * 2, 4), dpi=300)
    fig.subplots_adjust(wspace=0)
    # color = mpl.colormaps['tab20'](np.linspace(0,1, NCOLS))
    cmap = plt.get_cmap('tab20', 20)
    colors = [cmap(i) for i in range(len(METHODS))]

    ### performance stability (1-std)
    stdG = {m: [] for m in METHODS}  # {m: std(G_100)}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            stdG[METHODS[i]].append(G_100[i])
    res = np.array([1 - np.std(stdG[m]) for m in METHODS])

    pi += 1
    ax[pi].barh(list([M_NAME[m] for m in METHODS]), res,
               color=colors,
               label='performance stability')
    ax[pi].set_xlabel(r'$1 - \sigma \left( \mathbb{G} \right)$', fontsize='small')
    ax[pi].invert_yaxis()
    # ax[pi].set_yticks([])
    ax[pi].set_xlim(0, 1)
    ax[pi].spines['top'].set_visible(False)
    ax[pi].spines['right'].set_visible(False)
    # ax[pi].spines['left'].set_visible(False)
    ax[pi].axvline(0, color='k', linewidth=2 / 3, linestyle='-')
    ax[pi].set_title('performance\nstability', fontsize='small')

    ### multiple run exploitation capability
    MREC = {m: [] for m in METHODS}  # {m: (G_100_10runs - G_100) / 2}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
            G_100_10runs = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(11,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            MREC[METHODS[i]].append(G_100_10runs[i] - G_100[i])
    MREC = np.array([np.average(MREC[m]) for m in METHODS])

    pi += 1
    ax[pi].barh(list([M_NAME[m] for m in METHODS]), MREC,
                color=colors,
                label='multiple run exploitation capability')
    ax[pi].set_xlabel(r'avg $\left( \mathbb{G}_{RW} - \mathbb{G} \right)$', fontsize='small')
    ax[pi].invert_yaxis()
    ax[pi].set_yticks([])
    ax[pi].set_xlim(0, np.nanmax(MREC))
    ax[pi].spines['top'].set_visible(False)
    ax[pi].spines['right'].set_visible(False)
    ax[pi].spines['left'].set_visible(False)
    ax[pi].axvline(0, color='k', linewidth=2 / 3, linestyle='-')
    ax[pi].set_title('multiple run\nexploitation capability', fontsize='small')

    ### convergence speed
    CONSPD = {m: [] for m in METHODS}  # {m: 1 - (G_100 - G_10)}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
            G_10 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(3,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            CONSPD[METHODS[i]].append(1 - (G_100[i] - G_10[i]))
    CONSPD = np.array([np.average(CONSPD[m]) for m in METHODS])

    # fix for incomplete data
    for i in range(len(METHODS)):
        if CONSPD[i] > 2:
            print(f"...illegal convergence speed for {METHODS[i]}, defaulting to nan")
            CONSPD[i] = np.nan

    pi += 1
    ax[pi].barh(list([M_NAME[m] for m in METHODS]), CONSPD,
                color=colors,
                label='convergence speed')
    ax[pi].set_xlabel(r'avg $\left( 1 - \left( \mathbb{G} - \mathbb{G}_{10\%} \right) \right)$', fontsize='small')
    ax[pi].invert_yaxis()
    ax[pi].set_yticks([])
    ax[pi].set_xlim(0, np.nanmax(CONSPD))
    ax[pi].spines['top'].set_visible(False)
    ax[pi].spines['right'].set_visible(False)
    ax[pi].spines['left'].set_visible(False)
    ax[pi].axvline(0, color='k', linewidth=2 / 3, linestyle='-')
    ax[pi].set_title('convergence speed', fontsize='small')

    ### uniqueness
    exc = {m: [] for m in METHODS}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            if G_100[i] > 0.9:
                exc[METHODS[i]].append(info['name'])
    overlaps = np.ones((len(METHODS), len(METHODS)))
    for i, m1 in enumerate(METHODS):
        for j, m2 in enumerate(METHODS):
            if m1 != m2:
                # compute the overlap of m1 in m2
                doubles = [f for f in exc[m1] if f in exc[m2]]
                if len(exc[m1]) > 0:
                    overlaps[i, j] = len(doubles) / len(exc[m1])
                else:
                    overlaps[i, j] = np.nan
    for i in range(len(METHODS)):  # cleanup ones
        overlaps[i, i] = np.nan

    uniq = 1 - np.nanmax(overlaps, axis=1)
    uniq = np.nan_to_num(uniq)

    pi += 1
    ax[pi].barh(list([M_NAME[m] for m in METHODS]), uniq,
                color=colors,
                label='unique specialization')
    ax[pi].set_xlabel(r'$1 - \max ~\left( N_{m, sol} ~/~ N_{sol} \right)$', fontsize='small')
    ax[pi].set_yticks([])
    ax[pi].invert_yaxis()
    ax[pi].spines['top'].set_visible(False)
    ax[pi].spines['right'].set_visible(False)
    ax[pi].spines['left'].set_visible(False)
    ax[pi].axvline(0, color='k', linewidth=2 / 3, linestyle='-')
    ax[pi].set_title('unique\nspecialization', fontsize='small')

    ### sensitivity to problem multimodality
    res = {m: {'G_100': [], 'M': []} for m in METHODS}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            res[METHODS[i]]['G_100'].append(G_100[i])
            res[METHODS[i]]['M'].append((1 - G_100[1]) / 2)
    pearson = np.full(len(METHODS), np.nan)
    for i in range(len(METHODS)):
        pearson[i] = np.corrcoef(res[METHODS[i]]['M'], res[METHODS[i]]['G_100'])[0, 1]
    pearson = np.nan_to_num(pearson)

    pi += 1
    ax[pi].barh(list([M_NAME[m] for m in METHODS]), pearson,
                color=colors,
                label='sensitivity to problem multimodality')
    ax[pi].set_xlabel(r'$r$', fontsize='small')
    ax[pi].invert_yaxis()
    ax[pi].invert_xaxis()
    ax[pi].set_yticks([])
    ax[pi].spines['top'].set_visible(False)
    ax[pi].spines['right'].set_visible(False)
    ax[pi].spines['left'].set_visible(False)
    ax[pi].axvline(0, color='k', linewidth=2 / 3, linestyle='-')
    ax[pi].set_title('sensitivity to problem \nmultimodality', fontsize='small')
    # fig.legend(loc='upper center', ncols=2)

    ### computational complexity
    _, (Cm, _), _ = _computational_complexity_regressions()
    Cavg = [np.mean(Cm_i) for Cm_i in Cm]

    pi += 1
    ax[pi].barh(list([M_NAME[m] for m in METHODS]), Cavg,
               color=colors,
               label='baseline relative computational complexity')
    ax[pi].set_xlabel(r'avg $C_m$', fontsize='small')
    ax[pi].invert_yaxis()
    ax[pi].set_yticks([])
    ax[pi].set_xlim(1, np.max(Cavg))
    ax[pi].set_xscale('log')
    ax[pi].spines['top'].set_visible(False)
    ax[pi].spines['right'].set_visible(False)
    ax[pi].spines['left'].set_visible(False)
    ax[pi].axvline(1, color='k', linewidth=2 / 3, linestyle='-')
    ax[pi].set_title('computational\ncomplexity', fontsize='small')

    ### done
    fig.tight_layout()
    plt.savefig('post_analysis_method_features.png')


def method_clustering():

    print('\n*** method clustering')

    res = {m: [] for m in METHODS}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            res[METHODS[i]].append(G_100[i])

    X = np.empty((len(METHODS), len(res['RS'])))
    for i in range(len(METHODS)):
        X[i, :] = res[METHODS[i]]
    X = X[1:,:]  # remove RS

    from sklearn.cluster import SpectralClustering
    N_CLUSTERS = 7
    clusters = SpectralClustering(n_clusters=N_CLUSTERS,
                                  assign_labels='kmeans').fit(X)
    for c in range(N_CLUSTERS):
        print(f'cluster #{c}')
        for i in range(0, len(METHODS)-1):
            if clusters.labels_[i] == c:
                print(f'  {METHODS[i+1]}')


def function_clustering():

    print('\n*** method clustering')

    res = {}
    funs = []
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        funs.append(info['name'])
        res[info['name']] = G_100

    X = np.empty((len(funs), len(METHODS)))
    for i, f in enumerate(funs):
        X[i, :] = res[f]

    from sklearn.cluster import SpectralClustering
    N_CLUSTERS = 20
    CLUST = [[] for _ in range(N_CLUSTERS)]
    clusters = SpectralClustering(n_clusters=N_CLUSTERS, random_state=1,
                                  assign_labels='discretize').fit(X)
    for c in range(N_CLUSTERS):
        print(f'cluster #{c}')
        for i in range(len(funs)):
            if clusters.labels_[i] == c:
                print(f'  {funs[i]}')
                CLUST[c].append(funs[i])

    TAKE_EVERY_NTH_FUN = 5
    picked_funs = [c[::TAKE_EVERY_NTH_FUN] for c in CLUST]
    picked_funs = [x for xx in picked_funs for x in xx]  # flatten list
    picked_funs.sort()
    resm = {m: [] for m in METHODS}
    resm_reduced = {m: [] for m in METHODS}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            resm[METHODS[i]].append(G_100[i])
            if info['name'] in picked_funs:
                resm_reduced[METHODS[i]].append(G_100[i])

    fig, axes = plt.subplots(ncols=5, nrows=4, figsize=(5 * 2.4, 4 * 2.4 + 1))
    err = np.empty(len(METHODS))
    for i in range(len(METHODS)):
        m = METHODS[i]
        ax = axes.flat[i]
        ax.hist(resm[m], weights=np.ones_like(resm[m]) / len(resm[m]), bins=np.linspace(-1, 1, 20),
                label=r'$\mathbb{G}_{avg}$ = ' + f'{np.mean(resm[m]):.2f}',
                color='green', alpha=0.5)
        ax.hist(resm_reduced[m], weights=np.ones_like(resm_reduced[m]) / len(resm_reduced[m]),  bins=np.linspace(-1, 1, 20),
                label=r'$\mathbb{G}_{avg}$ = ' + f'{np.mean(resm_reduced[m]):.2f}',
                color='crimson', alpha=0.5)
        ax.legend(loc='upper left')
        ax.axvline(0, color='k', linewidth=2/3, linestyle=':')
        ax.title.set_text(f'{M_NAME[m]}')
        ax.set_xlim(-1, 1)
        ax.set_ylim(0, 0.7)
        ax.tick_params(bottom=False, labelbottom=False, left=False, labelleft=False)
        err[i] = np.abs(np.mean(resm[m]) - np.mean(resm_reduced[m]))

    fig.suptitle(f'green - full test ({len(funs)} funs); red - mini test ({len(picked_funs)} funs from {N_CLUSTERS} clusters); avg discrepancy {np.mean(err):.2f}')
    fig.tight_layout()
    fig.savefig('post_analysis_test_reduction_hist.png')

    print('\nmini test functions:')
    print('\n'.join(picked_funs))
    print(f'\ndiscrepancy: avg = {np.mean(err):.2f}; max = {np.max(err):.2f}')


def _computational_complexity_regressions():

    MEASUREMENTS_FILE = os.path.join(PATH, 'other', 'execution_time_measurement.txt')
    analyzed_methods = [M_NAME[m] for m in METHODS]

    Tdata = {}

    with open(MEASUREMENTS_FILE, 'r') as f:
        for line in f.readlines():

            if line.startswith('#'):
                continue

            line = line.strip().split(' ')
            fun_name = line[0]
            eval_time = float(line[1])
            opt_times = np.array([float(t) for t in line[2:]])

            # removing negative overhead cases
            if not np.min(opt_times) < eval_time:
                Tdata[fun_name] = [eval_time, {M_NAME[m]: t for m, t in zip(METHODS, opt_times)}]

    T_REF = Tdata['CEC_F1_10D'][0]

    # extract limits
    min_C_m, max_C_m = np.inf, 0
    for funame in Tdata.keys():
        for m in analyzed_methods:
            c = (Tdata[funame][1][m] - Tdata[funame][0]) / T_REF
            if c > max_C_m:
                max_C_m = c
            elif c < min_C_m:
                min_C_m = c

    # regressions
    from scipy.optimize import curve_fit
    def freg(d, e, C0):
        return d**e + C0
    e, C0 = np.full(len(METHODS), np.nan), np.full(len(METHODS), np.nan)
    Cm = [None] * len(METHODS)

    for i, m in enumerate(analyzed_methods):
        D = [int(funame.split('_')[-1][:-1]) for funame in Tdata.keys()]

        # if skip m: k[i], e[i], C0[i] = 0, 0, 0
        Cm[i] = [(Tdata[funame][1][m] - Tdata[funame][0]) / T_REF for funame in Tdata.keys()]

        (e[i], C0[i]), _ = curve_fit(freg, D, Cm[i],
                                           bounds=([0, 0], [3, max_C_m]))

    return (e, C0), (Cm, D), (min_C_m, max_C_m)


def computational_complexity():

    print('\n*** computational complexity')

    (e, C0), (Cm, D), (min_C_m, max_C_m) = _computational_complexity_regressions()

    # plot C_m(D)
    def freg(d, e_, C0_):
        return d**e_ + C0_
    # colors = plt.cm.rainbow(np.linspace(0, 1, len(METHODS)))
    fig, axes = plt.subplots(ncols=5, nrows=4, figsize=(5 * 2.4, 4 * 2.4 + 1))
    for i in range(len(METHODS)):
        m = METHODS[i]
        # c = colors[i]
        ax = axes.flat[i]
        # pearson = np.corrcoef(D, Cm[i])[0, 1]
        # reg = np.polynomial.Polynomial.fit(D, Cm[i], deg=1)
        ax.scatter(D, Cm[i], alpha=0.4,
                   norm=plt.Normalize(vmin=np.log10(min_C_m), vmax=np.log10(max_C_m)),
                   c=np.log10(Cm[i]), cmap='rainbow')
        m_ = np.linspace(np.min(D), np.max(D), 50)
        ax.plot(m_, freg(m_, e[i], C0[i]),
                label=fr'$C_m = D^{{{e[i]:.3f}}}$ + {C0[i]:.2f}', color='black')
        ax.plot(m_, freg(m_,1, C0[i]), linestyle=':', linewidth=0.5, color='black')
        diff = np.log10(freg(np.max(D), 1, C0[i]) - freg(0.7*np.max(D), 1, C0[i])) / (np.max(D) - 0.7*np.max(D))
        ax.text(np.max(D), 0.8 * freg(np.max(D), 1, C0[i]), 'linear growth',
                rotation=np.rad2deg(np.arctan(diff)),
                horizontalalignment='right', verticalalignment='top' if e[i]>1 else 'bottom',
                fontsize='small', fontstyle='italic', color='grey')
        ax.legend(loc='lower right', fontsize='small', handletextpad=0, handlelength=0)
        # ax.axhline(1, linestyle=':', color='grey')
        ax.set_ylim(min_C_m/1.3, max_C_m*1.3)
        ax.set_yscale('log')
        ax.title.set_text(f'{M_NAME[m]}')
        if i % 5 == 0:
            ax.tick_params(bottom=False, labelbottom=False)
        else:
            ax.tick_params(bottom=False, labelbottom=False, labelleft=False)  # add left=False for non-log-axis
    fig.tight_layout()
    fig.savefig('post_analysis_Cm(D).png')


def function_similarity():

    print('\n*** function similarity')

    import seaborn as sns
    PREFIXI = ['AEP', 'AirfoilDesign', 'EmpReg', 'Ergodic',
               'HydraulicNetwork', 'IPP', 'PP', 'ShortestPath', 'StructuralFrame']

    for pref in PREFIXI:
        print(f'...checking similarity of {pref} functions')
        res = {}

        for fname, info in DATA.items():
            funame = info['name']
            if not funame.startswith(pref):
                continue
            try:  # not all results are complete
                G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
            except:
                print(f"...skipping {funame}")
                continue
            res[funame] = G_100

        funs = list(res.keys())
        sol = np.array([G for G in res.values()])
        dist = np.full([len(funs), len(funs)], np.nan)
        for i in range(len(funs)):
            for j in range(i, len(funs)):
                dist[i,j] = np.linalg.norm(sol[i,:] - sol[j,:])
        dist_max = np.linalg.norm(np.full(len(METHODS), 2))
        simil = (dist_max - dist) / dist_max

        plt.figure(figsize=(13, 10))
        heatmap = sns.heatmap(simil, cmap='hot_r', annot=simil,
                              vmin=0.5, vmax=1,
                              linewidths=0.5, linecolor='k',
                              xticklabels=funs, yticklabels=funs)
        for _, spine in heatmap.spines.items():
            spine.set_visible(True)
        heatmap.set_ylabel('similarity of results for this function...')
        heatmap.set_xlabel('...with the results for this function')
        plt.tight_layout()
        plt.savefig(f'post_analysis_function_similarity_{pref}.png')


def method_scores():

    print('\n*** method scores')

    fig = plt.figure(figsize=(6, 4.2), dpi=300)
    ax = fig.gca()
    # colorfun = mpl.colormaps['rainbow']
    colorfun = plt.get_cmap(cmap_custom_half, 8)

    ### G_RW
    G = {m: [] for m in METHODS}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_RW = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(11,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            G[METHODS[i]].append(G_RW[i])
    G_RW = [np.nanmean(G[m]) for m in METHODS]

    ax.barh(list([M_NAME[m] for m in METHODS]), G_RW,
            color=colorfun(G_RW), alpha=0.3,
            label=r'avg $\mathbb{G}_{RW}$')
    for i, g in enumerate(G_RW):
        ax.text(g, list([M_NAME[m] for m in METHODS])[i], f'  {g:.2f}', color='grey',
                ha='left', va='center', fontsize='small')

    ### G_100
    G = {m: [] for m in METHODS}
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        for i in range(len(METHODS)):
            G[METHODS[i]].append(G_100[i])
        # if G_100[0] < 0: print(fname, G_100[0])
    G = [np.nanmean(G[m]) for m in METHODS]

    ax.barh(list([M_NAME[m] for m in METHODS]), G,
            color=colorfun(G), alpha=1,
            label=r'avg $\mathbb{G}$')
    for i, g in enumerate(G):
        if i != 0:
            ax.text(g, list([M_NAME[m] for m in METHODS])[i], f' {g:.2f}',
                    ha='left', va='center', fontsize='small')

    ax.set_xlabel(r'avg $\mathbb{G}$, avg $\mathbb{G}_{RW}$', fontsize='small')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.invert_yaxis()

    # handles, labels = ax.get_legend_handles_labels()
    # fig.legend([handles[idx] for idx in [1, 0]], [labels[idx] for idx in [1, 0]], loc='upper right')

    fig.tight_layout()
    plt.savefig('post_analysis_method_scores.png')


def benchmark_overview_visualization():

    print('\n*** Benchmark overview visualization')

    D = []
    M = []
    G = []
    F = []
    function_family = 'CEC AEP ER SP EC PP AD FF HN SFD IPP'.split(' ')[::-1]

    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue

        D.append(info['D'])
        M.append((1 - G_100[1]) / 2)
        G.append(np.nanmean(G_100))
        F.append(function_family.index(info['name'].split('_')[0]))

    # for d, m, f in zip(D, M, F):
    #     print(d, m, function_family[f])

    # family_size = [F.count(n) for n in range(len(function_family))]
    # Fs = [family_size[f] / len(F) for f in F]

    cmap = plt.get_cmap('Paired', 11).reversed()  # alt: 'tab20'

    plt.figure(figsize=(6, 4), dpi=300)
    plt.scatter(D, M, s=5 + 120*(1 - np.array(G)),
                alpha=0.7,
                norm=plt.Normalize(vmin=0, vmax=len(function_family)),
                c=np.array(F), cmap=cmap, linewidths=0)

    cbar = plt.colorbar()
    yticks = np.linspace(*cbar.ax.get_ylim(), 12)[:-1]
    yticks += (yticks[1] - yticks[0]) / 2
    cbar.set_ticks(yticks, labels=function_family)
    cbar.ax.tick_params(length=0)
    cbar.outline.set_visible(False)

    plt.xlabel(r'Dimensions $D$')
    plt.ylabel(r'Multimodality $M$')
    plt.tight_layout()
    plt.savefig('post_analysis_benchmark_overview_visualization.png')


def function_hardness_of_M():

    print('\n*** function_hardness(M) plot')

    Gmean, Gstd, M, D, Met = [], [], [], [], []
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        Met.append(np.argmax(G_100))
        Gmean.append(np.mean(G_100))
        Gstd.append(np.std(G_100))
        M.append((1 - G_100[1]) / 2)
        D.append(info['D'])

    Met_names = [M_NAME[METHODS[i]] for i in set(Met)]
    Met_nr = [list(set(Met)).index(i) for i in Met]
    Met_count = [Met_nr.count(i) for i in Met_nr]

    X = np.array(M)
    Y = Gmean

    cmap = plt.get_cmap('rainbow', 12).reversed()
    plt.figure(figsize=(6, 4), dpi=300)
    plt.scatter(X, Y, s=20,
                alpha=0.7,
                norm=plt.Normalize(vmin=0, vmax=max(Y)),
                c=Y, cmap=cmap, linewidths=0)
    plt.axhline(0, color='grey', linestyle=':')

    pearson = np.corrcoef(X, Y)[0, 1]
    reg = np.polynomial.Polynomial.fit(X, Y, deg=1)
    m_ = np.linspace(np.min(X), np.max(X), 50)
    plt.plot(m_, reg(m_), label=fr'$r={pearson:.2f}$', color='black', linewidth=1)
    # plt.text(0, 1, f'$r={pearson:.2f}$', verticalalignment='center')
    plt.legend(loc='lower left')

    # plt.gca().set_yscale('log')

    # cbar = plt.colorbar()
    # yticks = np.linspace(*cbar.ax.get_ylim(), 12+1)[:-1]
    # yticks += (yticks[1] - yticks[0]) / 2
    # cbar.set_ticks(yticks, labels=Met_names)
    # cbar.ax.tick_params(length=0)
    # cbar.outline.set_visible(False)

    plt.xlabel(r'Multimodality $M$')
    plt.ylabel(r'Optimization success $\mathbb{G}_{\text{avg}}$')
    plt.tight_layout()
    plt.savefig('post_analysis_function_hardness_of_M.png')


def exploration_of_sigma():

    print('\n*** exploration vs sigma')

    sigma, D, deltaG = [], [], []
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
            # G_10 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(3,), max_rows=len(METHODS))
            G_RW = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(11,), max_rows=len(METHODS))
            NPZ = np.load(os.path.join(PATH, "raw", info['name'] + '.npz'))
            G_of_f = ProblemResults(info['name']).calc_g
        except:
            print(f"...skipping {info['name']}")
            continue
        Gstd = []
        for m in METHODS:
            f_m = NPZ[indagobench.ResultsKeyPrefix.f_best + m]
            Gstd.append(np.std(G_of_f(f_m)))
        sigma.append(np.nanmedian(Gstd))
        deltaG.append(np.median(G_RW - G_100))
        D.append(info['D'])

    plt.figure(figsize=(6, 4), dpi=300)
    cmap = plt.get_cmap('rainbow', 6)
    plt.scatter(sigma, deltaG, s=15,  # + 2 * np.array(D),
                alpha=1,
                norm=plt.Normalize(vmin=0, vmax=np.max(deltaG)),
                c=np.array(deltaG), cmap=cmap, linewidths=0)

    # cbar = plt.colorbar()
    # cbar.ax.tick_params(length=0)
    # cbar.outline.set_visible(False)
    # cbar.ax.set_ylabel(r'colorbar label')

    reg = np.polynomial.Polynomial.fit(sigma, deltaG, deg=1)
    xreg = np.linspace(np.min(sigma), np.max(sigma), 50)
    plt.plot(xreg, reg(xreg), label='regression', color='black')

    pearson = np.corrcoef(sigma, deltaG)[0, 1]
    plt.text(0, np.max(deltaG), f'$r={pearson:.2f}$', verticalalignment='top')

    plt.xlabel(r'median $\sigma (\mathbb{G})$')
    plt.ylabel(r'median $(\mathbb{G}_{RW} - \mathbb{G}_{100})$')
    plt.tight_layout()
    plt.savefig('post_analysis_exploration_of_sigma.png')


def function_difficulty_assessment():

    print('\n*** function difficulty assessment')

    M, D, medG = [], [], []
    for fname, info in DATA.items():
        try:  # not all results are complete
            G_100 = np.loadtxt(os.path.join(PATH, "summary", fname), usecols=(5,), max_rows=len(METHODS))
        except:
            print(f"...skipping {info['name']}")
            continue
        M.append((1 - G_100[1]) / 2)
        D.append(info['D'])
        medG.append(np.mean(G_100))

    M = np.array(M)
    D = np.array(D)
    H = M #M**0.5 + M/2

    plt.figure(figsize=(6, 4), dpi=300)
    cmap = plt.get_cmap('rainbow', 6)
    plt.scatter(H, medG, s=15,  # + 2 * np.array(D),
                alpha=1,
                norm=plt.Normalize(vmin=np.min(D), vmax=np.max(D)),
                c=np.array(D), cmap=cmap, linewidths=0)

    reg = np.polynomial.Polynomial.fit(H, medG, deg=1)
    xreg = np.linspace(np.min(H), np.max(H), 50)
    plt.plot(xreg, reg(xreg), label='regression', color='black')

    pearson = np.corrcoef(H, medG)[0, 1]
    plt.text(np.min(H), np.min(medG), f'$r={pearson:.2f}$', verticalalignment='bottom', horizontalalignment='left')

    plt.xlabel(r'function difficulty indicator')
    plt.ylabel(r'mean $\mathbb{G}$')
    plt.tight_layout()
    plt.savefig('post_analysis_function_difficulty_assessment.png')


def function_list():

    print('\n*** function list')

    prefix = 'CEC'
    count = 0

    for problem in indagobench.indagobench25_problems:
        name = problem['label']
        if name.startswith(prefix):
            count += 1
        else:
            print(f'...total {prefix} count: {count}')
            count = 1
            prefix = name.split('_')[0]
        print(name, problem['max_evaluations'])
    print(f'...total {prefix} count: {count}')

    print(f'...total benchmark problems count: {len(indagobench.indagobench25_problems)}')


### MAIN

## obsolete
# G_of_D()
# CEC_vs_nonCEC()
# D_hist()
# H_hist()
# G_of_H()
# method_clustering()
# function_clustering()
# function_similarity()
# function_hardness_of_M()
# function_difficulty_assessment()
# function_list()
# exploration_of_sigma()
# computational_complexity()

## final
G_of_M()
method_overlap_heatmap()
benchmark_overview_visualization()
method_sets()
method_scores()
method_performance()
method_features()
