

import numpy as np
import os
import shutil
import subprocess
import sys

try:
    from indagobench._local_paths import epanet_binary_path, epanet_tmp_dir
    import wntr
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection

except ImportError as e:
    print('\033[91m' + f'Failed at importing optional module: {e.msg}')
    print('Code will continue but evaluation using HydraulicNetwork class is not possible.' + '\033[0m')


def _read_setup_dict():
    setups_filename = f'{os.path.dirname(os.path.abspath(__file__))}/hydraulic_network_data/hydraulic_network_cases.txt'
    setup = {}
    with open(setups_filename) as f:
        lines = f.readlines()
        for line in lines:
            if line.strip()[0] == '#':
                continue
            else:
                case_name, dims, lb, ub, max_eval = line.split()
                setup[case_name] = [int(dims), float(lb), float(ub), int(max_eval)]
    return setup


class HydraulicNetwork:

    case_definitions = _read_setup_dict()

    def __call__(self, x, case_name='simulation'):
        return self._f_call(x, case_name)

    # Deleting (Calling destructor)
    def __del__(self):
        pass
        # if os.path.exists(self.working_dir):
        #     shutil.rmtree(self.working_dir)

    def __init__(self, problem, dimensions=None, instance_label=None):

        if 'wntr' not in sys.modules:
            print('Failed to import wntr module that is not shipped with Indago. HydraulicNetwork class might not work.')

        self.problem = problem
        self.data_filename = f'{os.path.dirname(os.path.abspath(__file__))}/hydraulic_network_data/{problem}.inp'

        self.working_dir = f'{epanet_tmp_dir}/{instance_label}'
        self.results_dir = self.working_dir

        if os.path.exists(self.working_dir):
            shutil.rmtree(self.working_dir)
        os.mkdir(self.working_dir)
        if not os.path.exists(self.results_dir):
            os.mkdir(self.results_dir)


        self._f_call = None

        # self.base_wn = wntr.network.WaterNetworkModel()
        # self.base_wn.options.hydraulic.demand_model = 'DD'
        # self.base_wn.options.hydraulic.headloss = 'H-W'
        #
        # if os.path.exists(self.data_filename):
        #     # print(f'Reading HydraulicNetwork case {self.data_filename}')
        #     # self.wn = wntr.network.WaterNetworkModel(self.data_filename)
        #     self.base_wn = wntr.network.read_inpfile(self.data_filename)
        # else:
        #     # print(f'Missing HydraulicNetwork case {self.data_filename}')
        #     self.rnd_network('new_random_test')
        #
        # dims = self.base_wn.num_pipes

        dims, lb, ub, max_eval = HydraulicNetwork.case_definitions[problem]
        self.consumer_p_min = 26  # m
        self.dimensions = dims
        self.lb = np.full(dims, lb)
        self.ub = np.full(dims, ub)

        self._f_call = self.penalty

    def delete_epanet_files(self, filename):
        for ext in ['.inp', '.out', '.rpt']:
            if os.path.exists(f'{self.working_dir}/{filename}{ext}'):
                os.remove(f'{self.working_dir}/{filename}{ext}')

    def read_results(self, filename):

        with open(f'{filename}.out') as out_file:
            err = out_file.read().find('Error')
            # print(f'Read {err=}')
            if err >= 0:
                return None

        if os.path.exists(f'{filename}.rpt'):
            with open(f'{filename}.rpt') as res_file:
                lines = [l.strip() for l in res_file.readlines()]

                # n1 = lines.index()
                # n1 = next((l for l in lines if l == 'Node Results:'), None)
                n1 = next((i for i, l in enumerate(lines) if l == 'Node Results:'), None)
                l1 = next((i for i, l in enumerate(lines) if l == 'Link Results:'), None)

                # print(f'I have node results {n1=}')
                # print(f'I have link results {l1=}')

                node_label, node_demand, node_head, node_pressure = [], [], [], []
                i = n1 + 5
                while i < len(lines) and lines[i] != '':
                    node_label.append(lines[i][:15].strip())
                    cols = lines[i][15:25], lines[i][25:35], lines[i][35:45]
                    # print(cols)
                    q, h, p = [float(col) for col in cols]
                    node_demand.append(q)
                    node_head.append(h)
                    node_pressure.append(p)
                    i += 1


                link_label, link_flow, link_velocity, link_headloss = [], [], [], []
                i = l1 + 5
                while i < len(lines) and lines[i] != '':
                    link_label.append(lines[i][:15].strip())
                    cols = lines[i][15:25], lines[i][25:35], lines[i][35:45]
                    # print(cols)
                    q, v, l = [float(col) for col in cols]
                    link_flow.append(q)
                    link_velocity.append(v)
                    link_headloss.append(l)
                    i += 1

                R = dict(node_label=node_label,
                         node_demand=np.array(node_demand),
                         node_head=np.array(node_head),
                         node_pressure=np.array(node_pressure),
                         link_label=link_label,
                         link_flow=np.array(link_flow),
                         link_velocity=np.array(link_velocity),
                         link_headloss=np.array(link_headloss))
                # print(R)
                return R

        else:
            return None



    def run_simulation(self, design, case_name=None, plot=False, ax=None, plot_only_layout=False):

        # wn_dict = wntr.network.to_dict(self.base_wn)
        # wn = wntr.network.from_dict(wn_dict)
        wn = wntr.network.read_inpfile(self.data_filename)
        wn.options.hydraulic.demand_model = 'DD'
        wn.options.hydraulic.headloss = 'H-W'

        wn.options.report.report_filename = f'{case_name}.rpt'
        wn.options.report.status = 'FULL'
        wn.options.report.summary = 'YES'
        wn.options.report.nodes = 'ALL'
        wn.options.report.links = 'ALL'

        n_pipes = wn.num_pipes

        # Get pipe lengths
        L = np.full(n_pipes, np.nan)
        for i, (lbl, pipe) in enumerate(wn.pipes()):
            # D[i] = pipe.diameter
            L[i] = pipe.length

        # Adjust diameters and remove pipes from the network
        d_min = 0.01
        diameters = np.copy(design)
        diameters[diameters < d_min] = 0
        # print(diameters)
        names = [n for n, _ in wn.pipes()]
        for d, name in zip(diameters, names):
            if d < d_min:
                wn.get_link(name).initial_status = 0
                # wn.remove_link(name)
            else:
                wn.get_link(name).diameter = d

        # Calculate volume objective
        vol = L * diameters * np.pi
        vol_norm = vol / (L * self.ub * np.pi)
        o1 = np.average(vol_norm)

        # Calculate the share of opened pipes (used as observable, not objective)
        o2 = np.sum(diameters > 0.01) / diameters.size

        self.delete_epanet_files(f'{case_name}')

        # Run hydraulic simulation
        wntr.network.write_inpfile(wn, f'{self.working_dir}/{case_name}.inp', units='LPM', version=2.2)

        commands = [epanet_binary_path, f'{case_name}.inp', f'{case_name}.out']
        p = subprocess.Popen(commands,
                             cwd=self.working_dir,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, errors = p.communicate()
        # print(f'{" ".join(commands)=}')
        # print(f'{output=}')
        # print(f'{errors=}')

        if not os.path.exists(f'{self.working_dir}/{case_name}.inp'):
            print(f'No file: {self.working_dir}/{case_name}.inp')

        if not os.path.exists(f'{self.working_dir}/{case_name}.rpt'):
            print(f'No file: {self.working_dir}/{case_name}.rpt')

        # if output.find("Error") >= 0:
        #     print('ERROR!')

        results = self.read_results(f'{self.working_dir}/{case_name}')
        # print(diameters)
        # print(results)
        # input('?')

        if not plot:
            self.delete_epanet_files(f'{case_name}')

        # # self.wn.options.hydraulic.headloss = 'H-W'
        # # sim = wntr.sim.WNTRSimulator(self.wn)
        # sim = wntr.sim.EpanetSimulator(wn)
        # # results = sim.run_sim()
        # try:
        #     if unique_str:
        #         results = sim.run_sim(file_prefix=f'{self.working_dir}/{unique_str}')
        #     else:
        #         results = sim.run_sim(file_prefix=f'{self.working_dir}/test')
        # except:
        #     # o1, o2, c1, c2
        #     del sim
        #     del wn
        #     return [1e20] * 4
        # # print(results.error_code)

        """
        Process the results
        """
        if results is None:
            return [1e20] * 3

        # Node results
        node_head = results['node_head']
        node_demand = results['node_demand']

        # Consumers results
        consumers_head = node_head[node_demand > 0]
        consumer_p_min = np.full(consumers_head.shape, self.consumer_p_min)

        # consumers_head_diff = consumers_head - consumer_p_min
        # print(f'{consumers_head_diff=}')
        # consumers_head_diff_norm = consumers_head_diff / consumer_p_min
        # c1 = -np.sum(consumers_head_diff_norm[consumers_head_diff_norm < 0])
        violated = consumers_head < consumer_p_min
        consumers_head_factor = np.log(1 + (consumer_p_min[violated] - consumers_head[violated]) / consumer_p_min[violated])
        c1 = np.sum(consumers_head_factor) #[consumers_head_factor < 0])

        if plot:
            # wntr.network.write_inpfile(wn, f'{unique_str}.inp', units='LPM', version=2.2)
            print(f'{o1=}, {o2=}, {c1=}, {self.results_dir}/{case_name}.png')


            x = np.array([n.coordinates[0] for i, n in wn.nodes()])
            y = np.array([n.coordinates[1] for i, n in wn.nodes()])
            width = x.max() - x.min()
            height = y.max() - y.min()
            # print(f'{x.min()=} {x.max()=} {y.min()=} {y.max()=}')
            plot_params = {}
            if self.problem in 'epanet2 epanet2a'.split():
                plot_params = {'figsize': (5, 10),
                               'title_pos': (0.02, 0.95),
                               'res_pos': (0.02, 0.5),
                               'flow_cb_pos': (0.5, 0.05, 0.35, 0.008),
                               'head_cb_pos': (0.5, 0.10, 0.35, 0.008),
                               }
            elif self.problem == 'apulia':
                plot_params = {'figsize': (5, 4),
                               'title_pos': (0.02, 1.07),
                               'res_pos': (0.02, 0.42),
                               'flow_cb_pos': (0.02, 0.05, 0.35, 0.02),
                               'head_cb_pos': (0.02, 0.17, 0.35, 0.02),
                               }
            elif self.problem == 'fossolo':
                plot_params = {'figsize': (5, 4.7),
                               'title_pos': (0.02, 1.05),
                               'res_pos': (0.7, 1.05),
                               'flow_cb_pos': (0.02, 0.035, 0.35, 0.02),
                               'head_cb_pos': (0.42, 0.035, 0.35, 0.02),
                               }
            elif self.problem == 'arlington':
                plot_params = {'figsize': (10, 4.2),
                               'title_pos': (0.15, 0.95),
                               'res_pos': (0.45, 0.95),
                               'flow_cb_pos': (0.02, 0.14, 0.25, 0.02),
                               'head_cb_pos': (0.32, 0.14, 0.25, 0.02),
                               }
            elif self.problem == 'jilin':
                plot_params = {'figsize': (10, 4.2),
                               'title_pos': (0.15, 0.95),
                               'res_pos': (0.45, 0.95),
                               'flow_cb_pos': (0.02, 0.14, 0.25, 0.02),
                               'head_cb_pos': (0.32, 0.14, 0.25, 0.02),
                               }
            elif self.problem in 'net3x2 net3x2f'.split():
                plot_params = {'figsize': (10, 4.2),
                               'title_pos': (0.15, 0.95),
                               'res_pos': (0.45, 0.95),
                               'flow_cb_pos': (0.02, 0.14, 0.25, 0.02),
                               'head_cb_pos': (0.32, 0.14, 0.25, 0.02),
                               }
            elif self.problem == 'net4x2':
                plot_params = {'figsize': (10, 4.2),
                               'title_pos': (0.15, 0.95),
                               'res_pos': (0.45, 0.95),
                               'flow_cb_pos': (0.02, 0.14, 0.25, 0.02),
                               'head_cb_pos': (0.32, 0.14, 0.25, 0.02),
                               }
            elif self.problem == 'net4x3':
                plot_params = {'figsize': (10, 4.2),
                               'title_pos': (0.15, 0.95),
                               'res_pos': (0.45, 0.95),
                               'flow_cb_pos': (0.02, 0.14, 0.25, 0.02),
                               'head_cb_pos': (0.32, 0.14, 0.25, 0.02),
                               }

            print(f'{width=}, {height=}')
            if ax is None:
                fig, ax = plt.subplots(figsize=plot_params['figsize'])
            else:
                fig = None
            ax.tick_params(left=False, labelleft=False)
            ax.tick_params(bottom=False, labelbottom=False)
            props = dict(boxstyle='square,pad=0.3', facecolor='silver', alpha=0.6, edgecolor='none')

            if not plot_only_layout:
                if fig is None:
                    ax.text(0, 0.99, case_name,
                            fontsize=15,  # fontweight='bold',
                            horizontalalignment='left',
                            verticalalignment='top',
                            # bbox=props,
                            transform=ax.transAxes)
                else:
                    ax.text(plot_params['title_pos'][0], plot_params['title_pos'][1], case_name,
                            fontsize='large',  # fontweight='bold',
                            horizontalalignment='left',
                            verticalalignment='top',
                            # bbox=props,
                            transform=ax.transAxes)


            closed = f'{np.sum(diameters < d_min):d}/{diameters.size:d}'
            results_str = \
            f'f=          {o1 + (c1 if c1 <= 0 else 1 + c1):12.5f}\n' + \
            f'o1=         {o1:12.5f}\n' + \
            f'c1=         {c1:12.5f}\n' + \
            f'h_norm_min= {np.min(consumers_head / self.consumer_p_min):12.5f}\n' + \
            f'h_norm_max= {np.max(consumers_head / self.consumer_p_min):12.5f}\n' + \
            f'closed=     {closed:>12s}' #+ \
            #f''.join([f'\n{h}' for h in consumers_head])
            #f'{self.consumer_p_min=:.5f}\n' + \

            if fig is not None:
                ax.text(plot_params['res_pos'][0], plot_params['res_pos'][1], results_str,
                        fontsize='x-small',  # fontweight='bold'
                        fontfamily='monospace',
                        horizontalalignment='left',
                        verticalalignment='top',
                        bbox=props,
                        transform=ax.transAxes)

            for spine in ax.spines.values():
                spine.set_visible(False)

            for lbl, pipe in wn.pipes():
                points = np.array([pipe.start_node.coordinates, pipe.end_node.coordinates]).T
                ax.plot(points[0], points[1], '--', c='grey', lw=1.0 if plot_only_layout else 0.5, zorder=0)

            plt.subplots_adjust(bottom=0, top=1,
                                left=0, right=1)
            ax.set_xlim(x.min(), x.max())
            ax.set_ylim(y.min(), y.max())
            ax.axis('equal')

            xy = np.array([node.coordinates for lbl, node in wn.nodes()]).T


            segments = []
            segment_widths = []
            # Q = np.abs(results['link_flow'])
            Q = []
            # print(f'{Q.min()=}, {Q.max()=}')
            # print(results['link_flow'])
            for i, (lbl, pipe) in enumerate(wn.pipes()):
                points = np.array([pipe.start_node.coordinates, pipe.end_node.coordinates])
                segments.append(points)
                segment_widths.append(30 * pipe.diameter)
                j = results['link_label'].index(lbl)
                Q.append(np.abs(results['link_flow'][j]))
            Q = np.array(Q)
            pipe_segments = LineCollection(segments, linewidths=segment_widths,
                                           cmap=plt.cm.turbo_r,
                                           norm='log',
                                           zorder=1)
            pipe_segments.set_array(np.abs(results['link_flow']))
            pipe_segments.set_clim(1e2, 1e5)
            ax.add_collection(pipe_segments)

            if fig is not None:
                cbax = fig.add_axes(plot_params['flow_cb_pos'])
                cbar = fig.colorbar(pipe_segments, cax=cbax,
                                    orientation='horizontal',)
                # pipe_segments.set_clim(Q.min(), Q.max())
                cbar.ax.tick_params(labelsize=6)
                cbax.text(0.025, 1.5, 'Flowrate [l/s]',
                          fontsize=8,
                          ha='left', va='bottom',
                          transform=cbax.transAxes,
                          bbox=props)
                for spine in cbax.spines.values():
                    spine.set_visible(False)

            # Nodes
            node_markers = ax.scatter(xy[0], xy[1], marker='o',
                                      c=node_head,
                                      s=20,
                                      edgecolors='k',
                                      linewidths=0.2,
                                      cmap=plt.cm.spring,
                                      zorder=3)

            node_markers.set_clim(0, 100)
            if fig is not None:
                cbax = fig.add_axes(plot_params['head_cb_pos'])
                cbar = fig.colorbar(node_markers, cax=cbax,
                                    orientation='horizontal',)
                cbar.ax.tick_params(labelsize=6)
                cbax.text(0.025, 1.5, 'Head [m]',
                          fontsize=8,
                          ha='left', va='bottom',
                          transform=cbax.transAxes,
                          bbox=props)
                for spine in cbax.spines.values():
                    spine.set_visible(False)

            for i, (lbl, node) in enumerate(wn.nodes()):

                # Node labels
                # ax.text(node.coordinates[0], node.coordinates[1], node.name)

                # h = results.node['head'].loc[0, lbl]

                dx = width / 100
                ax.plot([node.coordinates[0] + dx, node.coordinates[0] + dx],
                        [node.coordinates[1], node.coordinates[1] + height / 50],
                        color='darkgrey', lw=1)
                # print(node_head)

                head_ratio = node_head[i] / self.consumer_p_min
                head_diff = node_head[i] - self.consumer_p_min

                if not plot_only_layout:
                    if head_diff >= 0:
                        # ax.plot(node.coordinates[0], node.coordinates[1],
                        #         marker='o', c='olivedrab', ms=8, zorder=-2)
                        ax.plot([node.coordinates[0] + 1.5*dx, node.coordinates[0] + 1.5*dx],
                                [node.coordinates[1], node.coordinates[1] + height / 50 * (node_head[i] / self.consumer_p_min)],
                                color='darkgreen', lw=2)
                    else:
                        # ax.plot(node.coordinates[0], node.coordinates[1],
                        #         marker='x', c='red',
                        #         mew=3, ms=8, zorder=2)

                        ax.plot([node.coordinates[0] + 1.5*dx, node.coordinates[0] + 1.5*dx],
                                [node.coordinates[1], node.coordinates[1] + (height / 50 - 0.2 * np.log(np.abs(head_diff)))],
                                color='red', lw=2)

            for lbl, r in wn.reservoirs():
                # print(lbl, r)
                ax.text(r.coordinates[0], r.coordinates[1], 'R',
                        fontsize=9, color='w',
                        ha='center', va='center',
                        zorder=4,)
                ax.plot(r.coordinates[0], r.coordinates[1],
                        marker='s', c='cornflowerblue',
                        ms=15, zorder=3,
                        mec='royalblue')

            ax.axis('image')

            if fig is not None:
                fig.savefig(f'{self.results_dir}/HN_{self.problem}_{self.dimensions}D_{case_name}.png', dpi=600)
                plt.close(fig)


        else:
            for ext in 'inp rpt bin'.split():
                f = f'{self.working_dir}/{case_name}.{ext}'
                if os.path.exists(f): os.remove(f)

        return o1, o2, c1


    def rnd_network(self, case):
        # this will not work due to base_wn !!!

        print('Creating random case')
        nx = 5
        ny = 4
        X = np.arange(nx) * 500
        Y = np.arange(ny) * 500
        n_reservoirs = 1
        n_consumers = 6

        reservoirs = []
        while len(reservoirs) < n_reservoirs:
            i_res, j_res = np.random.randint(0, [nx, ny])
            if (i_res, j_res) not in reservoirs:
                reservoirs.append((i_res, j_res))
        print(f'{reservoirs=}')

        consumers = []
        while len(consumers) < n_consumers:
            i_con, j_con = np.random.randint(0, [nx, ny])
            if (i_con, j_con) not in consumers and (i_con, j_con) not in reservoirs:
                consumers.append((i_con, j_con))
        print(f'{consumers=}')

        p = 0
        for i in range(nx):
            for j in range(ny):
                rx, ry = np.random.uniform(-1, 1, 2) * 200
                if (i, j) in reservoirs:
                    self.base_wn.add_reservoir(f'{i},{j}',
                                               base_head=30,
                                               # head_pattern='pat1',
                                               coordinates=(X[i] + rx, Y[j] + ry))
                elif (i, j) in consumers:
                    self.base_wn.add_junction(f'{i},{j}',
                                              base_demand=20 * 1e-3,  # *l/s
                                              # head_pattern='pat1',
                                              coordinates=(X[i] + rx, Y[j] + ry))
                else:
                    self.base_wn.add_junction(f'{i},{j}',
                                              # demand_pattern='1', elevation=10,
                                              coordinates=(X[i] + rx, Y[j] + ry)
                                              )
                if i > 0:
                    self.base_wn.add_pipe(f'{p}', start_node_name=f'{i - 1},{j}', end_node_name=f'{i},{j}',
                                          # length=10,
                                          diameter=0.5, roughness=130, minor_loss=0)
                    p += 1
                if j > 0:
                    self.base_wn.add_pipe(f'{p}', start_node_name=f'{i},{j - 1}', end_node_name=f'{i},{j}',
                                          # length=10,
                                          diameter=0.5, roughness=130, minor_loss=0)
                    p += 1

        for i, pipe in self.base_wn.links():
            n1 = np.array(self.base_wn.nodes[pipe.start_node].coordinates)
            n2 = np.array(self.base_wn.nodes[pipe.end_node].coordinates)
            pipe.length = np.linalg.norm(n1 - n2)

        print(f'n_links={len(self.base_wn.links)}')

    def penalty(self, x, unique_str='sim'):
        o1, o2, c1 = self.run_simulation(x, case_name=unique_str)
        if c1 > 0:
            c1 += 1
        else:
            c1 = 0

        return o1 + c1

    def save_case(self, case=None):
        if case:
            self.data_filename = f'{os.path.dirname(os.path.abspath(__file__))}/hydraulic_network_data/{case}.net'
        wntr.network.write_inpfile(self.base_wn, self.data_filename,
                                   units='LPM', version=2.2)


HN_problems_dict_list = []
for case, (dimensions, lb, ub, max_evals) in _read_setup_dict().items():
    f_dict = {'label': f'HN_{case}_{int(dimensions)}D',
              'class': HydraulicNetwork,
              'case': case,
              'dimensions': None,
              'max_evaluations': max_evals,
              'max_runs': 1000,
              }
    HN_problems_dict_list.append(f_dict)

if __name__ == '__main__':

    # hm = HydraulicNetwork(problem='epanet2', dimensions=0, instance_label='test')
    # d = np.random.uniform(hm.lb, hm.ub)
    # hm.run_simulation(d, case_name='random', plot=True)

    import indagobench
    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir,
                                             convergence_window=10, eps_max=0.1, runs_min=10,
                                             # convergence_window=50, eps_max=0.01, runs_min=100,
                                             )
    standard_test.optimizers = indagobench.indagobench25_optimizers
    standard_test.problems = HN_problems_dict_list
    # standard_test.run_all()


    # Preparing figures for manuscript
    print(HydraulicNetwork.case_definitions)
    hn = HydraulicNetwork('fossolo')
    hn.results_dir = hn.working_dir
    problem_dict = indagobench.get_problem_dict('HN_fossolo_58D')
    problem_results = indagobench.ProblemResults(problem_dict, verbose=True)
    results = problem_results.results

    problem_results.optimizers = 'PSO LSHADE CMAES'.split()
    problem_results.make_full_convergence_figure(
        f'{indagobench._local_paths.indagobench25_results_dir}/HN/short_conv_{problem_dict["label"]}.png',
        header_plots=False)

    # width = 5817.15, height = 4461.97

    # fig = plt.figure(figsize=(10, 8.))
    # ax1 = fig.add_axes([0.0, 0.51, 0.49, 0.49], frameon=True, facecolor='white')
    # ax2 = fig.add_axes([0.51, 0.51, 0.49, 0.49], frameon=True, facecolor='white')
    # ax3 = fig.add_axes([0.0, 0.0, 0.49, 0.49], frameon=True, facecolor='white')
    # ax4 = fig.add_axes([0.51, 0.0, 0.49, 0.49], frameon=True, facecolor='white')
    # axes = [ax1, ax2, ax3, ax4]
    #
    # def format_ax(ax):
    #     ax.tick_params(left=False, labelleft=False)
    #     ax.tick_params(bottom=False, labelbottom=False)
    #     for spine in ax.spines.values():
    #         spine.set_visible(False)
    #
    # [format_ax(ax) for ax in axes]
    #
    # def get_x_median(optimizer_label):
    #     f_best = problem_results.results['f_best ' + optimizer_label]
    #     f_median = np.median(f_best)
    #     i = np.argmin(np.abs(f_median - f_best))
    #     x_median = problem_results.results['x_best ' + optimizer_label][i, :]
    #     return x_median
    #
    # hn.run_simulation(problem_results.results['_x_min'], 'Best', plot=True, ax=ax1)
    # hn.run_simulation(get_x_median('PSO'), 'PSO', plot=True, ax=ax2)
    # hn.run_simulation(get_x_median('LSHADE'), 'LSHADE', plot=True, ax=ax3)
    # hn.run_simulation(get_x_median('CMAES'), 'CMAES', plot=True, ax=ax4)
    #
    # for ax in axes:
    #     ax.set_xlim(1800, 7800)
    #     ax.set_ylim(5000, 9600+200)
    #
    # print(f'{indagobench._local_paths.indagobench25_results_dir}/HN.png')
    # plt.savefig(f'{indagobench._local_paths.indagobench25_results_dir}/HN.png')
    # plt.close(fig)


    fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(10, 15), tight_layout=True)
    for problem_dict, ax in zip(HN_problems_dict_list, axes.ravel()):
        hn = HydraulicNetwork(problem_dict['case'])
        hn.results_dir = hn.working_dir

        d0 = np.full(hn.dimensions, 0.0)
        hn.run_simulation(d0, problem_dict['case'], plot=True, ax=ax, plot_only_layout=True)
        ax.text(0, 1, problem_dict['label'],
                fontsize=16, transform=ax.transAxes)



    plt.savefig(f'{indagobench._local_paths.indagobench25_results_dir}/HN_all_cases.png')
    plt.close(fig)

    d_min = 0.01
    p_min = 26.0
    for problem_dict, ax in zip(HN_problems_dict_list, axes.ravel()):
        hn = HydraulicNetwork(problem_dict['case'])
        hn.results_dir = hn.working_dir

        wn = wntr.network.read_inpfile(hn.data_filename)
        XY = np.array([wn.get_node(node).coordinates for node in wn.nodes])
        Z = np.array([j.elevation for _, j in wn.junctions()])
        S = np.array([j.base_demand for _, j in wn.junctions()])
        # D = np.array([wn.get_node(node).discharge for node in wn.junctions])
        R = np.array([j.base_head for _, j in wn.reservoirs()])

        s = r'\texttt{' + problem_dict["label"].replace("_", r"\_") +'}'
        # print(f'{XY.shape=}')
        s += rf' & {np.max(XY[:,0])-np.min(XY[:,0]):.1f} $\times$ {np.max(XY[:,1])-np.min(XY[:,1]):.1f}'
        s += rf' & {R[0]:.1f}'
        s += rf' & {Z.min():.1f} & {Z.max():.1f} \\'
        # print(s)


        s = r'\texttt{' + problem_dict["label"].replace("_", r"\_") +'}'
        s += rf' & {S.min()*1e3:.1f} & {S.max()*1e3:.1f}'
        s += rf' & {hn.lb[0]:.2f} & {hn.ub[0]:.2f}'
        s += rf' & {p_min:.1f} \\'
        print(s)

    """Results postprocessing and visualization"""
    class_results_dir = f'{indagobench._local_paths.indagobench25_results_dir}/HN/'
    if not os.path.exists(class_results_dir):
        os.mkdir(class_results_dir)

    # Manuscript figures
    for problem_dict in [indagobench.get_problem_dict('FF_bay1_10D')]:
        fr = indagobench.ProblemResults(problem_dict)
        fr.optimizers = ['NM', 'LSHADE', 'CMAES']
        fr.make_full_convergence_figure(f'{class_results_dir}/short_conv_{problem_dict["label"]}.png',
                                        header_plots=False)

    # for problem_dict in standard_test.problems:
    #     hn = HydraulicNetwork(problem_dict['case'])
    #     hn.results_dir=hn.working_dir
    #
    #     problem_results = indagobench.ProblemResults(problem_dict, verbose=True)
    #     results = problem_results.results
    #
    #     case_name = f'{problem_dict["label"]}_best'
    #     x_best = results['x_best']
    #     # sf.simulate(x_best, case_name, keep_files=True)
    #     hn.run_simulation(x_best, plot=True, case_name='best')
    #     shutil.copyfile(f'{hn.working_dir}/{case_name}.png',
    #                     f'{indagobench._local_paths.indagobench25_results_dir}/HN/{case_name}.png')
    #
    #     for optimizer in standard_test.optimizers:
    #         f = results['f ' + optimizer['label']]
    #         i = np.argmin(np.abs(np.median(f[:, -1]) - f[:, -1]))
    #         x = results[f'x ' + optimizer['label']][i, :]
    #         # print(f[:, -1])
    #         # print(f'best_i={i}')
    #         case_name = f'{optimizer["label"].replace(" ", "-")}_median'
    #         # sf.simulate(x, case_name, keep_files=True)
    #         hn.run_simulation(x, plot=True, case_name=case_name)
    #         shutil.copyfile(f'{hn.working_dir}/HN_{hn.problem}_{hn.dimensions}D_{case_name}.png',
    #                         f'{indagobench._local_paths.indagobench25_results_dir}/HN/HN_{hn.problem}_{hn.dimensions}D_{case_name}.png')
