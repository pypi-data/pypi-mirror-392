import sys

sys.path.append('../../indago')
sys.path.append('..')
import indago
from indagobench.optimizers._optimizers_scipy import scipy_lbfgsb_dict, scipy_dual_annealing_dict
from indagobench.optimizers._optimizers_zoopt import zoopt_dict
from indagobench.optimizers._optimizers_nlopt import nlopt_crs_dict, nlopt_esch_dict, nlopt_stogo_dict
from indagobench.optimizers._optimizers_pymoo import pymoo_ga_dict, pymoo_cmaes_dict



indagobench25_optimizers = []

# 1 Random search
indagobench25_optimizers.append({'optimizer_class': indago.RS,
                             'variant': 'Vanilla',
                             'params': None,  # Default parameters
                             'label': f'RS'},
                                )

# 2 Limited-memory BFGS (SciPy)
indagobench25_optimizers.append(scipy_lbfgsb_dict)

# 3 Nelder Mead
indagobench25_optimizers.append({'optimizer_class': indago.NM,
                             'variant': 'GaoHan',
                             'params': None,
                             'label': 'NM'})

# 4 Multi-Scale Grid Search
indagobench25_optimizers.append({'optimizer_class': indago.MSGD,
                             'variant': 'Vanilla',
                             'params': None,
                             'label': 'MSGD'})

# 5 Zeroth Order Optimization
indagobench25_optimizers.append(zoopt_dict)

# 6 Dual Annealing (scipy)
indagobench25_optimizers.append(scipy_dual_annealing_dict)

# 7 Coordinated Random Search (nlopt)
indagobench25_optimizers.append(nlopt_crs_dict)

# 8 Stochastic Global Optimization (nlopt)
indagobench25_optimizers.append(nlopt_stogo_dict)

# 9 Electromagnetic Field Optimization
indagobench25_optimizers.append({'optimizer_class': indago.EFO,
                             'variant': 'Vanilla',
                             'params': None,
                             'label': 'EFO'})

# 10 Particle Swarm Optimization
indagobench25_optimizers.append({'optimizer_class': indago.PSO,
                             'variant': 'Vanilla',
                             'params': None,  # Default parameters
                             'label': 'PSO',
                                 })

# 11 Artificial Bee Colony
indagobench25_optimizers.append({'optimizer_class': indago.ABC,
                             'variant': 'Vanilla',
                             'params': None,  # Default parameters
                                 # 'old_label': 'ABC Vanilla',
                             'label': 'ABC'})

# 12 Squirrel Search Algorithm
indagobench25_optimizers.append({'optimizer_class': indago.SSA,
                             'variant': 'Vanilla',
                             'params': None,  # Default parameters
                                 # 'old_label': 'SSA Vanilla',
                             'label': 'SSA'})

# 13 Bat Algorithm
indagobench25_optimizers.append({'optimizer_class': indago.BA,
                             'variant': 'Vanilla',
                             'params': None,  # Default parameters
                                 # 'old_label': 'BA Vanilla',
                             'label': 'BA'})

# 14 Grey Wolf Optimizer
indagobench25_optimizers.append({'optimizer_class': indago.GWO,
                             'variant': 'Vanilla',
                             'params': None,
                             'label': 'GWO'})

# 15 Manta Ray Foraging Optimization
indagobench25_optimizers.append({'optimizer_class': indago.MRFO,
                             'variant': 'Vanilla',
                             'params': None,  # Default parameters
                                 # 'old_label': 'MRFO Vanilla',
                             'label': 'MRFO'})

# 16 Fireworks Algorithm
indagobench25_optimizers.append({'optimizer_class': indago.FWA,
                             'variant': 'Vanilla',
                             'params': None,  # Default parameters
                             'label': 'FWA',
                                 # 'old_label': 'FWA Vanilla',  # For changing optimizer label and keeping existing results)
                                 })

# 17 Differential Evolution LSHADE
indagobench25_optimizers.append({'optimizer_class': indago.DE,
                             'variant': 'LSHADE',
                             'params': None,
                             'label': 'LSHADE'})

# 18 Genetic Algorithm (pymoo)
indagobench25_optimizers.append(pymoo_ga_dict)

# 19 CH Evolutionary Strategy (nlopt)
indagobench25_optimizers.append(nlopt_esch_dict)

# 20 Covariance matrix adaptation evolution strategy (pymoo)
indagobench25_optimizers.append(pymoo_cmaes_dict)

