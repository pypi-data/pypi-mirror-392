#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
packing Problems

@author: sinisa
"""


import numpy as np

try:
    import matplotlib.pyplot as plt
    import shapely as shp
    from shapely import affinity as shp_affinity

except ImportError as e:
    print('\033[91m' + f'Failed at importing optional module: {e.msg}')
    print('Code will continue but evaluation using PP class is not possible.' + '\033[0m')

class PP():
    """Packing Problems test suite class.

    Problem definitions and evaluation criteria for the packing problems.
    
    Parameters
    ----------
    problem : str
        Name of the test function. Required initialization parameter.
        
    Attributes
    ----------
    case_definitions : dict
        Dict of problem names (key) and corresponding available dimensions (value).
    _setup : callable
        Private function for setting up the pieces in the packing space.
    lb : ndarray
        Vector of lower bounds.
    ub : ndarray
        Vector of upper bounds.
    xmin : ndarray
        Design vector at function minimum.
    fmin : float
        Function minimum.
    dimensions : int
        Dimensionality of the test functions.

    Returns
    -------
    fitness: float or tuple
        Fitness of the produced evaluation function. If called with plot=True, returns
        a tuple with the figure of the result visualization.
        
    """
    
    case_definitions = {'fr5c': [10],
                        'fr10c': [20],
                        'fr5t': [15],
                        'fr10t': [30],
                        'fr5s': [15],
                        'fr10s': [30],
                        'fr1c1t1s': [8],
                        'fr3c3t3s': [24],
                        'fr6c6t6s': [48],
                        'ctr5c': [10],
                        'ctr10c': [20],
                        'ctr5t': [15],
                        'ctr10t': [30],
                        'ctr5s': [15],
                        'ctr10s': [30],
                        'ctr1c1t1s': [8],
                        'ctr3c3t3s': [24],
                        'ctr6c6t6s': [48]
                        }

    def __call__(self, x, *args, **kwargs):
        """
        A method that enables an PP instance to be callable. Evaluates
        PP._f_call that is set in PP.__init__ in order to point to the
        appropriate PP function.
        """
        
        return self._f_call(x, *args, **kwargs)
    
    def __init__(self, problem, dimensions=None, instance_label=None):
        """Initialize case"""

        assert problem in self.case_definitions, \
            f'Problem {problem} not defined in PP problem class'

        if problem.startswith('fr'):
            config = problem[2:]
        elif problem.startswith('ctr'):
            config = problem[3:]

        c_count, t_count, s_count = 0, 0, 0
        if 'c' in config:
            config_split = config.split('c')
            c_count = int(config_split[0])
            config = config_split[1]
        if 't' in config:
            config_split = config.split('t')
            t_count = int(config_split[0])
            config = config_split[1]
        if 's' in config:
            config_split = config.split('s')
            s_count = int(config_split[0])

        packing_space_size = (c_count + t_count + s_count)

        def goalfun(x, plot=False):

            # setup pieces
            collection = self._setup(x, (c_count, t_count, s_count))

            fig = None
            if plot:
                fig = plt.figure(figsize=(6, 6), dpi=300)

                for object in collection:
                    XY = np.array(shp.get_coordinates(object))
                    if np.size(XY[:, 0]) == 4:  # triangle
                        color = 'coral'
                    elif np.size(XY[:, 0]) == 5:  # square
                        color = 'royalblue'
                    else:  # circle
                        color = 'seagreen'
                    fig.gca().plot(XY[:, 0], XY[:, 1], color=color, linewidth=2)
                    fig.gca().fill(XY[:, 0], XY[:, 1], color=color, alpha=0.3)

                fig.gca().fill([0, len(collection), len(collection), 0, 0],
                               [0, 0, len(collection), len(collection), 0],
                               color='lightgrey', alpha=0.5, zorder=-1)

                BND = shp.GeometryCollection(collection).bounds
                BND_x = [BND[0], BND[2], BND[2], BND[0], BND[0]]
                BND_y = [BND[1], BND[1], BND[3], BND[3], BND[1]]
                fig.gca().plot(BND_x, BND_y, color='grey', linestyle='--', linewidth=1.5)

                plt.plot([len(collection)/2, len(collection)/2], [len(collection)/2, len(collection)/2],
                         'o', color='grey', ms=5)
                plt.plot(np.mean(BND_x[:4]), np.mean(BND_y[:4]), '+', color='black', ms=10)

                # uncomment these when manuscript figures are done
                fig.gca().title(f'{self.__name__}')
                fig.gca().axis('equal')
                fig.tight_layout()
                fig.show()

            # compute bounding box area
            shp_collection = shp.GeometryCollection(collection)
            area = shp.envelope(shp_collection).area

            penalty_step = shp_collection.area ** 2

            # measure overlaps
            overlaps = 0
            for object1 in collection:
                for object2 in collection:
                    if object1 is not object2:
                        overlaps += shp.intersection(object1, object2).area
            if overlaps > 0:
                overlaps += penalty_step

            # measure pack centering
            offcenter = 0
            if problem.startswith('ctr'):
                area_center = shp.Point(packing_space_size / 2, packing_space_size / 2)
                offcenter = shp.distance(shp_collection.centroid, area_center)
                offcenter *= penalty_step

            # print(f'fitness={area + overlaps:.2f}, \
            #     {area=:.2f}, \
            #     overlapping={max(overlaps - penalty_step, 0):.2f}, \
            #     offcentered={offcenter / penalty_step:.2f}')

            fitness = area + overlaps + offcenter

            if plot:
                return fitness, fig
            else:
                return fitness

        self._f_call = goalfun

        self.lb = np.zeros(c_count * 2 + t_count * 3 + s_count * 3)
        c_ub = [packing_space_size, packing_space_size]
        t_ub = [packing_space_size, packing_space_size, 120]
        s_ub = [packing_space_size, packing_space_size, 90]
        self.ub = np.array(c_ub * c_count + t_ub * t_count + s_ub * s_count)
        self.xmin = np.full_like(self.lb, np.nan)
        self.fmin = np.nan
        self.dimensions = np.size(self.lb)
        
        # add name
        self.__name__ = f"PP_{problem}_{self.dimensions}D"

    def _setup(self, x, problem_config):
        """
        Private function for setting up the pieces in the packing space.

        Parameters
        ----------
        x : ndarray
            Design vector (shape coordinates and rotation angles).

        Returns
        -------
        collection : list
            List of shapely objects.

        """

        c_count, t_count, s_count = problem_config

        # separate variables
        Cxy, Txya, Sxya = [], [], []
        if c_count != 0:
            Cxy = x[:c_count * 2]
            Cxy = Cxy.reshape([-1, 2])
            x = x[c_count * 2:]
        if t_count != 0:
            Txya = x[:t_count * 3]
            Txya = Txya.reshape([-1, 3])
            x = x[t_count * 3:]
        if s_count != 0:
            Sxya = x[:s_count * 3]
            Sxya = Sxya.reshape([-1, 3])

        # create pieces
        collection = []

        for xy in Cxy:
            center = shp.Point(*xy)
            collection.append(shp.buffer(center, 0.5))

        for xya in Txya:
            center_x, center_y, angle = xya
            height = (np.sqrt(3) / 2) * 1  # side length is 1
            centroid_to_vertex = (2 / 3) * height
            centroid_to_base = (1 / 3) * height
            half_base = 1 / 2  # side length is 1
            # vertices
            v1 = (center_x, center_y + centroid_to_vertex)
            v2 = (center_x - half_base, center_y - centroid_to_base)
            v3 = (center_x + half_base, center_y - centroid_to_base)
            # create and rotate
            T = shp.Polygon([v1, v2, v3])
            T = shp_affinity.rotate(T, angle, origin='centroid')
            collection.append(T)

        for xya in Sxya:
            center_x, center_y, angle = xya
            # vertices
            v1 = (center_x - 0.5, center_y - 0.5)
            v2 = (center_x - 0.5, center_y + 0.5)
            v3 = (center_x + 0.5, center_y + 0.5)
            v4 = (center_x + 0.5, center_y - 0.5)
            # create and rotate
            T = shp.Polygon([v1, v2, v3, v4])
            T = shp_affinity.rotate(T, angle, origin='centroid')
            collection.append(T)

        return collection


#### standardized tests
PP_problems_dict_list = []
for case in PP.case_definitions:
    d = PP.case_definitions[case][0]
    problem_dict = {'label': f'PP_{case}_{d}D',
                    'class': PP,
                    'case': case,
                    'dimensions': d,
                    'max_evaluations': 130 * d ** 2,
                    'max_runs': 1000,
                    }
    PP_problems_dict_list.append(problem_dict)


if __name__ == '__main__':

    """
    # demo PP functions
    print('\n*** demo PP functions')
    test_functions = [PP(problem=p) \
                      for p in PP.case_definitions.keys()]
    for f in test_functions:
        x = np.random.uniform(f.lb, f.ub)
        print(f'{f.__name__} \n {f(x)}')
    """

    """
    # test optimization
    from indago import minimize
    fun = PP('ctr3c3t3s')
    print(f'solving {fun.__name__}')
    X, _ = minimize(fun, fun.lb, fun.ub,
                    'DE', variant='LSHADE',
                    max_evaluations=200*fun.dimensions**2)
    fun(X, plot=True)
    """

    """
    # standard test
    import indagobench
    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir,
                                             convergence_window=50, eps_max=0.01, runs_min=100,
                                             # convergence_window=10, eps_max=0.1, runs_min=10,
                                             )
    standard_test.optimizers = indagobench.indagobench25_optimizers
    standard_test.problems = PP_problems_dict_list

    standard_test.run_all()
    """

    """
    # extract example results
    import indagobench
    fun = PP('ctr3c3t3s')
    problem_dict = indagobench.get_problem_dict('PP_ctr3c3t3s_24D')
    problem_results = indagobench.ProblemResults(problem_dict)
    problem_results.optimizers = 'SRACOS EFO GWO'.split()
    problem_results.make_full_convergence_figure(
        f'{indagobench._local_paths.indagobench25_results_dir}/PP/short_conv{problem_dict["label"]}.png',
        header_plots=False)
    plt.close('all')

    for optimizer in problem_results.optimizers:
        i_best = np.argmin(problem_results.results['f ' + optimizer][:, -1])
        x_best = problem_results.results['x ' + optimizer][i_best, :]
        print(optimizer, fun(x_best))
        _, fig = fun(x_best, plot=True)
        fig.gca().set_xlim([-1, 9])
        fig.gca().set_ylim([-1, 9])
        fig.gca().text(0.2, 8.8, optimizer, fontsize=15, verticalalignment='top')
        fig.gca().axis('off')
        fig.savefig(f'PP_ctr3c3t3s_24D_{optimizer}.png')
    problem_results.update_referent_values()
    x_best_all = problem_results.results['x_best']
    print('best', fun(x_best_all))
    _, fig = fun(x_best_all, plot=True)
    fig.gca().set_xlim([-1, 9])
    fig.gca().set_ylim([-1, 9])
    fig.gca().text(0.2, 8.8, 'Best', fontsize=15, verticalalignment='top')
    fig.gca().axis('off')
    fig.savefig(f'PP_ctr3c3t3s_24D_best.png')
    """
    