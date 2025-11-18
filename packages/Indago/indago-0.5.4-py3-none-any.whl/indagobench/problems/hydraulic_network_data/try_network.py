import sys
sys.path.append('../../../indago')
sys.path.append('../../..')
sys.path.append('../../../tests')
import numpy as np
import wntr
import indagobench


#import _local_paths

# network database: https://uknowledge.uky.edu/wdsrd/

def generate(name, nx, ny, dx, dy):

    wn_new = wntr.network.WaterNetworkModel()


    wn_new.add_reservoir('reservoir',
                             base_head=75,
                             coordinates=(-0.5 * dx,-0.5 * dy),
                         )


    for iy in range(ny):
        for ix in range(nx):

            x = ix * dx + 0.5 * np.random.uniform(-dx, dx)
            y = iy * dy + 0.5 * np.random.uniform(-dy, dy)
            z = (1000 * x + y**2) * 1e-4
            q = np.round(np.random.uniform(0, 0.02), 3)

            wn_new.add_junction(f'{iy}_{ix}',
                                base_demand=q,
                                elevation=z,
                                coordinates=(x, y),
                                )

    npipe = 1
    n0 = wn_new.get_node(f'reservoir')
    n1 = wn_new.get_node(f'0_0')
    wn_new.add_pipe(f'{npipe}',
                    start_node_name='reservoir',
                    end_node_name='0_0',
                    length=np.linalg.norm(np.array(n0.coordinates) - np.array(n1.coordinates)),
                    diameter=1,
                    roughness=1,
                    minor_loss=0,
                    initial_status=1,
                    )

    for iy in range(ny):
        for ix in range(nx):

            n0 = wn_new.get_node(f'{iy}_{ix}')
            print(n0.coordinates)

            if ix > 0: # connect to the left
                n1 = wn_new.get_node(f'{iy}_{ix - 1}')
                npipe += 1
                wn_new.add_pipe(f'{npipe}',
                                start_node_name=n0.name,
                                end_node_name=n1.name,
                                length=np.linalg.norm(np.array(n0.coordinates) - np.array(n1.coordinates)),
                                diameter=1,
                                roughness=1,
                                minor_loss=0,
                                initial_status=1,
                                )

            if iy > 0: # connect to the bottom
                n1 = wn_new.get_node(f'{iy - 1}_{ix}')
                npipe += 1
                wn_new.add_pipe(f'{npipe}',
                                start_node_name=n0.name,
                                end_node_name=n1.name,
                                length=np.linalg.norm(np.array(n0.coordinates) - np.array(n1.coordinates)),
                                diameter=1,
                                roughness=1,
                                minor_loss=0,
                                initial_status=1,
                                )

    wntr.network.write_inpfile(wn_new, f'{name}.inp', units='LPM', version=2.2)

def convert(name_old, name_new):
    wn_old = wntr.network.WaterNetworkModel(f'original_networks/{name_old}.inp')


    wn_new = wntr.network.WaterNetworkModel()
    for name, junction in wn_old.junctions():
        wn_new.add_junction(name,
                            # base_demand=junction.base_demand,
                            base_demand=np.round(np.random.uniform(0, 0.05), 3),
                            elevation=junction.elevation,
                            coordinates=junction.coordinates)

    for name, reservoir in wn_old.reservoirs():
        wn_new.add_reservoir(name,
                             base_head=reservoir.base_head,
                             coordinates=reservoir.coordinates)

    for name, tank in wn_old.tanks():
        # wn_new.add_tank(name,
        #                 elevation=tank.elevation,
        #                 init_level=tank.init_level,
        #                 min_level=tank.min_level,
        #                 max_level=tank.max_level,
        #                 diameter=tank.diameter,
        #                 coordinates=tank.coordinates)
        wn_new.add_reservoir(name,
                             base_head=tank.elevation + tank.init_level,
                             coordinates=tank.coordinates)

    for name, pipe in wn_old.pipes():
        wn_new.add_pipe(name,
                        start_node_name=pipe.start_node_name,
                        end_node_name=pipe.end_node_name,
                        length=pipe.length,
                        diameter=pipe.diameter,
                        roughness=pipe.roughness,
                        minor_loss=pipe.minor_loss,
                        initial_status=pipe.initial_status,
                        )

    wn_new.name = name_new
    wntr.network.write_inpfile(wn_new, f'{name_new}.inp', units='LPM', version=2.2)

if __name__ == '__main__':

    # convert('net1', 'net1')
    name_new = 'network_4x3'
    # generate(name_new, 4, 3, 100, 100)
    #
    # hn = indagobench.HydraulicNetwork(problem=name_new)
    # hn.results_dir = indagobench._local_paths.st24_results_dir + '/HydraulicNetwork/'
    # if not os.path.exists(hn.results_dir):
    #     os.mkdir(hn.results_dir)
    # hn.run_simulation(np.random.uniform(hn.lb, hn.ub), f'res_{name_new}_rnd_test', plot=True)
    #
    # optimizer = indago.PSO()
    # optimizer.evaluation_function = hn
    # optimizer.lb = hn.lb
    # optimizer.ub = hn.ub
    # # optimizer.max_evaluations = 10_000
    # optimizer.processes = 'max'
    # optimizer.forward_unique_str = True
    # optimizer.monitoring = 'dashboard'
    # optimizer.optimize()
    # # optimizer.plot_history(filename=f'conv_{name_new}_{optimizer.__class__.__name__}.png')
    # hn.run_simulation(optimizer.best.X, f'res_{name_new}_{optimizer.__class__.__name__}', plot=True)


    from indagobench.problems._hydraulic_network import HN_problems_dict_list

    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir,
                                             convergence_window=20, eps_max=0.1, runs_min=20,
                                             )
    standard_test.optimizers = indagobench.indagobench25_optimizers
    standard_test.problems = HN_problems_dict_list[-1:]
    standard_test.run_all()


    # i_case = ([h['case'] for h in HN_problems_dict_list]).index(name_new)
    # print(i_case)
    # results = standard_test.read_results(HN_problems_dict_list[i_case])
    #
    # x_best = results['x_min']
    # print(results['f_min'])
    # hn.run_simulation(x_best, f'res_{name_new}_best', plot=True)
    #
    # optimizers = [o['label'] for o in standard_test.optimizers]
    # # print(optimizers)
    # # optimizers = ['NM GaoHan', 'LBFGSB', 'MSGD']
    # for optimizer in optimizers:
    #     # print(f'{optimizer=}')
    #     f = results[f'f {optimizer}']
    #     i = np.argmin(np.abs(np.median(f[:, -1]) - f[:, -1]))
    #     # print(f'{f.shape=}, {i=}')
    #     x = results[f'x {optimizer}'][i, :]
    #     # print(x.shape)
    #     hn.run_simulation(x, f'res_{name_new}_{optimizer.replace(" ", "_")}_median', plot=True)
