
import subprocess
import numpy as np
import os
from pathlib import Path


try:
    from indagobench._local_paths import calculix_binary_path, calculix_tmp_dir
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection


except ImportError as e:
    print('\033[91m' + f'Failed at importing optional module: {e.msg}')
    print('Code will continue but evaluation using StructuralFrame class is not possible.' + '\033[0m')

def _read_structural_frame_cases_dict():
    setups_filename = f'{os.path.dirname(os.path.abspath(__file__))}/structural_frame_data/structural_frame_cases.txt'
    setup = {}
    with open(setups_filename) as f:
        lines = f.readlines()
        for line in lines:
            if line.strip()[0] == '#':
                continue
            else:
                case_name, dims, max_eval = line.split()
                setup[case_name] = [int(dims), int(max_eval)]
    return setup


class StructuralFrame:
    case_definitions = _read_structural_frame_cases_dict()

    def __call__(self, x, case_name='simulation'):
        return self.simulate(x, case_name)

    def __init__(self, problem, dimensions=None, instance_label=None):
        self._parametrization = None
        self.problem = problem

        self.working_dir = Path(f'{calculix_tmp_dir}/StructuralFrame_{instance_label}')
        # if os.path.exists(self.working_dir):
        #     shutil.rmtree(self.working_dir)
        if not os.path.exists(self.working_dir):
            os.mkdir(self.working_dir)

        if problem in 'bridge1 bridge2 archbridgex bridge3'.split():
            self._parametrization = self._archbridge_parametrization
            # X = [h, a1, a2, a3]
            self.lb = np.array([1e-1, 1e-3, 1e-3, 1e-3])
            self.ub = np.array([25, 0.5, 0.5, 0.5])
            self.dimensions = self.lb.size

            # Referentne vrijednosti
            self.m_ref = 150_000  # m^3
            self.u_ref = 0.05  # m (dopušteni pomak)
            self.s_ref = 30e6  # Pa (dopušteno naprezanje)

        elif problem in 'bridge4 bridge5'.split():
            self._parametrization = self._suspensionbridge_parametrization
            # X = [h, a1, a2, a3]
            self.lb = np.array([1e-1, 1e-3, 1e-3, 1e-3, 1e-3])
            self.ub = np.array([25, 0.5, 0.5, 0.5, 0.1])
            self.dimensions = self.lb.size

            # Referentne vrijednosti
            self.m_ref = 150_000  # m^3
            self.u_ref = 0.05  # m (dopušteni pomak)
            self.s_ref = 30e6  # Pa (dopušteno naprezanje)

        elif problem == 'corner3':
            self._parametrization = self._corner_parametrization
            #              X = [y3,     a1,     a2,     a3, ]
            self.lb = np.array([-0.5,   1e-3,   1e-3,   1e-3])
            self.ub = np.array([-0.01,  0.1,    0.1,    0.1])
            self.dimensions = self.lb.size

            # Referentne vrijednosti
            self.m_ref = 500 # kg
            self.u_ref = 0.0005  # m (dopušteni pomak)
            self.s_ref = 30e6  # Pa (dopušteno naprezanje)

        elif problem == 'corner5':
            self._parametrization = self._corner_parametrization
            #              X = [x3,     y3,     y4,     a1,     a2,     a3,     a4,     a5]
            self.lb = np.array([0.01,   -0.5,   -0.5,   1e-3,   1e-3,   1e-3,   1e-3,   1e-3])
            self.ub = np.array([0.5,    -0.01,  -0.01,  0.1,   0.1,   0.1,   0.1,   0.1])
            self.dimensions = self.lb.size

            # Referentne vrijednosti
            self.m_ref = 500 # kg
            self.u_ref = 0.0005  # m (dopušteni pomak)
            self.s_ref = 30e6  # Pa (dopušteno naprezanje)

        elif problem == 'cabeam8':
            self._parametrization = self._cantileverbeam_parametrization

            #              X = [nx2,    nx4,    nx6,     a1 - a8]
            self.lb = np.array([0.001,  0.001,  0.001] + [1e-3] * 8)
            self.ub = np.array([0.6,    0.6,    0.599] + [0.1] * 8)
            self.dimensions = self.lb.size

            # Referentne vrijednosti
            self.m_ref = 1000 # kg
            self.u_ref = 0.0005  # m (dopušteni pomak)
            self.s_ref = 30e6  # Pa (dopušteno naprezanje)

        elif problem == 'cabeam14':
            self._parametrization = self._cantileverbeam_parametrization

            #              X = [nx2,    nx3,    nx5,    nx6,    nx8,    ny8,    nx9,    ny9,    *A]
            self.lb = np.array([0,      0.4,    0.4,    0.0,    0.0,    -0.099,   0.3,    -0.074] + [1e-3] * 14)
            self.ub = np.array([0.4,    0.6,    0.6,    0.4,    0.3,    0.099,    0.6,    0.074] + [0.08] * 14)
            self.dimensions = self.lb.size

            # Referentne vrijednosti
            self.m_ref = 2_000 # kg
            self.u_ref = 0.0003  # m (dopušteni pomak)
            self.s_ref = 30e6  # Pa (dopušteno naprezanje)

        elif problem.startswith('box'):
            self._parametrization = self._box_parametrization
            nx, ny = [int(n) for n in problem[3:].split('x')]
            dims = nx * (ny - 1) + ny * (nx - 1)
            self.lb = np.array([1e-3] * dims)
            self.ub = np.array([0.08] * dims)
            self.dimensions = self.lb.size

            # Referentne vrijednosti
            self.m_ref = 1_500 # kg
            self.u_ref = 0.005  # m (dopušteni pomak)
            self.s_ref = 30e6  # Pa (dopušteno naprezanje)

        else:
            assert False, f'Unknown problem {problem}'
    def __del__(self):
        # Destructor deletes working_dir
        # if os.path.exists(self.working_dir):
        #     shutil.rmtree(self.working_dir)
        pass

    def simulate(self, design, case_name, keep_files=False, ax=None):

        case_definition_dict = self._parametrization(design)
        n_nodes = case_definition_dict['nodes'].shape[0]
        n_elements = 0
        elset = 0
        while f'elements_{elset + 1}' in case_definition_dict.keys():
            elset += 1
            n_elements += case_definition_dict[f'elements_{elset}'].shape[0]

        self.delete_files(case_name)
        self.write_inp(case_definition_dict, case_name)
        self.run_simulation(case_name)

        results = self.read_results(case_name, n_nodes, n_elements)
        if results:
            U, R, S = results
        else:
            return 1e20

        m = self.calculate_mass(case_definition_dict)
        u_max = np.max(np.abs(U))
        s_max = np.max(S)

        # Normirani ciljevi i ograničenja
        # o ~= 1, c <= 0 - feasible/izvedivo
        o_m = m / self.m_ref
        c_u = 2 * (u_max - self.u_ref) / self.u_ref
        c_s = 2 * (s_max - self.s_ref) / self.s_ref

        c_u = (0 if c_u <= 0 else 1 + c_u)
        c_s = (0 if c_s <= 0 else 1 + c_s)
        f = o_m + c_u + c_s

        design_lines = []
        row = 8
        for i in range(0, case_definition_dict["design"].size, row):
            design_lines.append(f'{", ".join([f"{x:.3f}" for x in case_definition_dict["design"][i:i + row]])}')
        design_lines = ',\n'.join(design_lines)
        case_definition_dict['label'] = (#rf'$\mathbf{{X}}$=[{design_lines}]' +
                                         f'$m$={m:.3e}, $u_{{max}}$={u_max:.3e}, $s_{{max}}$={s_max:.3e}\n' +
                                         f'$o_m$={o_m:.5e}, $c_u$={c_u:.5e}, $c_s$={c_s:.5e}\n' +
                                         f'$f$={f:.5e}')

        if keep_files:
            self.visualize(case_definition_dict, U, S, case_name, ax=ax)
            print('='*30)
            print(f'{case_name=}')
            print(f'{design=}')
            print(f'{m=}, {u_max=}, {s_max=}')
            print(f'{o_m=}, {c_u=}, {c_s=}')
            print(f'{f=}')
            print('-' * 30)
        else:
            self.delete_files(case_name)

        # return o_v, c_u, c_s
        return f

    def write_inp(self, case_definition_dict, case_name):

        # Open .inp file
        inp_file = open(f'{self.working_dir}/{case_name}.inp', 'w')

        # Nodes
        nodes = case_definition_dict['nodes']
        inp_file.write('*NODE, NSET=nodes_all\n')
        for i in range(nodes.shape[0]):
            inp_file.write(f'{i + 1:5d}, ' +
                           f'{nodes[i, 0]:10f}, ' +
                           f'{nodes[i, 1]:10f}\n')

        # Elements
        elset = 0
        el_cnt = 0
        while f'elements_{elset + 1}' in case_definition_dict.keys():
            elset += 1
            elements = case_definition_dict[f'elements_{elset}']
            inp_file.write(f'*ELEMENT, TYPE=B31, ELSET=elements_{elset}\n')
            for i in range(elements.shape[0]):
                inp_file.write(f'{el_cnt + i + 1:5d}, ' +
                               f'{elements[i, 0] + 1:5d}, ' +
                               f'{elements[i, 1] + 1:5d}\n')
            el_cnt += elements.shape[0]

        # Element set for all elements
        inp_file.write('*ELSET, ELSET=elements_all\n')
        for i in range(elset):
            inp_file.write(f'elements_{i + 1},\n')

        # Material
        inp_file.write('*MATERIAL, NAME=steel\n')
        inp_file.write('*ELASTIC\n')
        inp_file.write('210e9, 0.3\n')
        inp_file.write('*DENSITY\n')
        inp_file.write('7800\n')

        # Beam cross sections
        elset = 0
        while f'section_{elset + 1}' in case_definition_dict.keys():
            elset += 1
            section = case_definition_dict[f'section_{elset}']
            inp_file.write(section)

        # Boundary conditions (supports)
        inp_file.write(case_definition_dict['boundary'])

        # Korak simulacije
        inp_file.write('*STEP\n') # , NLGEOM
        inp_file.write('*STATIC\n')

        # Opterećenja
        if 'dload' in case_definition_dict:
            inp_file.write(case_definition_dict['dload'])
        if 'cload' in case_definition_dict.keys():
            inp_file.write(case_definition_dict['cload'])

        # Rezultati
        # PRINT piše ASCII rezultate u .dat datoteku
        inp_file.write('*NODE PRINT, NSET=nodes_all\n')
        inp_file.write('U, RF\n')
        inp_file.write('*EL PRINT, ELSET=elements_all\n')
        inp_file.write('S\n')

        # FILE piše ASCII/binarne rezultate u .frd datoteku
        inp_file.write('*NODE FILE\n')
        inp_file.write('U\n')
        inp_file.write('*EL FILE\n')
        inp_file.write('S\n')

        inp_file.write('*END STEP')

        # Close .inp file
        inp_file.close()
        # print(f'{inp_file=}')

    def run_simulation(self, case_name):
        process = subprocess.Popen([calculix_binary_path, case_name],
                                   cwd=self.working_dir,  # Current Working Directory
                                   universal_newlines=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   )
        # Run the process and wait to finish
        # Standard output and error stored to variables stdout i stderr
        stdout, stderr = process.communicate()
        # print(f'{stdout=}')
        # print(f'{stderr=}')

    def read_results(self, file_name, n_nodes, n_elements):
        # Reading calculix results from .dat file
        results_path = f'{self.working_dir}/{file_name}.dat'

        if not os.path.exists(results_path):
            return False
        if os.stat(results_path).st_size == 0:
            return False

        # Displacmeent
        l1 = 3  # Header lines of result file (skip)
        U = np.loadtxt(results_path,
                       skiprows=l1,
                       max_rows=n_nodes,
                       usecols=(1, 2))

        # Reactions
        l1 = 3 + n_nodes + 3
        R = np.loadtxt(results_path,
                       skiprows=l1,
                       max_rows=n_nodes,
                       usecols=(1, 2))

        # Stress
        l1 = (3 + n_nodes) * 2 + 3
        S = np.loadtxt(results_path,
                       skiprows=l1,
                       max_rows=n_elements * 8,
                       usecols=(2, 3, 4, 5, 6, 7))

        # Mises stress in integration points
        S_misses = np.sqrt(0.5) * np.sqrt(
            (S[:, 0] - S[:, 1]) ** 2 +  # (s_xx - s_yy)^2
            (S[:, 1] - S[:, 2]) ** 2 +  # (s_yy - s_zz)^2
            (S[:, 2] - S[:, 0]) ** 2 +  # (s_zz - s_xx)^2
            + 6 * np.sum(S[:, 3:] ** 2, axis=1)
        )

        S = np.zeros(n_elements)
        for i in range(n_elements):
            S[i] = np.max(S_misses[i * 8: (i + 1) * 8])

        return U, R, S

    def visualize(self, case_definition_dict, U, S, case_name, ax=None):

        if ax is None:
            fig, ax = plt.subplots(
                figsize=(6, 6 * case_definition_dict['yspan'][2] / case_definition_dict['xspan'][2]))
            fig.set_layout_engine('compressed')
        else:
            fig = None

        props = dict(boxstyle='square,pad=0.3', facecolor='silver', alpha=0.6, edgecolor='none')
        if fig:
            ax.text(*case_definition_dict['titlexy'], case_name,
                fontsize='x-large',  # fontweight='bold',
                horizontalalignment='left',
                verticalalignment='top',
                # bbox=props,
                transform=ax.transAxes)
            # ax.text(*case_definition_dict['labelxy'],
            #     case_definition_dict['label'],
            #     fontsize='small',  # fontweight='bold',
            #     horizontalalignment='left',
            #     verticalalignment='top',
            #     # bbox=props,
            #     transform=ax.transAxes)

        # Drawing nodes
        nodes = case_definition_dict['nodes']
        ax.plot(nodes[:, 0], nodes[:, 1], '.', c='k', ms=1)
        # for i in range(nodes.shape[0]):
        #     ax.text(nodes[i, 0], nodes[i, 1], f'n{i + 1}', fontsize='x-small')

        # Drawing elements elemenata
        elset = 0
        while f'elements_{elset + 1}' in case_definition_dict.keys():
            elset += 1

            elements = case_definition_dict[f'elements_{elset}']
            for i in range(elements.shape[0]):
                n1, n2 = elements[i, :]
                ax.plot(nodes[[n1, n2], 0],
                        nodes[[n1, n2], 1],
                        c='grey', lw=1, ls='--', zorder=-1)

        segments = []
        segment_widths = []
        segment_values = []
        # Q = np.abs(results['link_flow'])
        Q = []
        # print(f'{Q.min()=}, {Q.max()=}')
        # print(results['link_flow'])
        el_cnt = 0
        A = case_definition_dict['A']
        elset = 0
        while f'elements_{elset + 1}' in case_definition_dict.keys():
            elset += 1

            elements = case_definition_dict[f'elements_{elset}']
            for i in range(elements.shape[0]):
                n1, n2 = elements[i, :]
                points = nodes[[n1, n2], :] + case_definition_dict['uscale'] * U[[n1, n2],:]
                segments.append(points)
                # segment_widths.append(2)
                segment_widths.append(case_definition_dict['lwscale'] * A[elset - 1])
                segment_values.append(S[el_cnt + i])

            el_cnt += elements.shape[0]

        pipe_segments = LineCollection(segments, linewidths=segment_widths,
                                       cmap=plt.cm.plasma,
                                       # norm='log',
                                       zorder=1)
        pipe_segments.set_array(segment_values)
        pipe_segments.set_clim(0, case_definition_dict['smax'])
        ax.add_collection(pipe_segments)

        if fig:
            cbax = fig.add_axes(case_definition_dict['scbar'],
                                transform=ax.transAxes)
            cbar = fig.colorbar(pipe_segments, cax=cbax,
                                orientation='horizontal', )
            # # pipe_segments.set_clim(Q.min(), Q.max())
            cbar.ax.tick_params(labelsize=6)
            cbax.text(0.01, 1.5, 'von Mises stress',
                      fontsize=8,
                      ha='left', va='bottom',
                      transform=cbax.transAxes,
                      bbox=props)
            for spine in cbax.spines.values():
                spine.set_visible(False)


        for sup_type, orientation, node in case_definition_dict['supports']:
            c = 'steelblue'
            if sup_type in 'slide pinned'.split():
                ax.plot(*node, 'o', color=c, ms=10, zorder=1)
            if sup_type == 'fixed':
                ax.plot(*node, 's', color=c, ms=10, zorder=1)

            if orientation == 'down' or orientation == 'up':
                dy = -1 if orientation == 'down' else 1
                lx = node[0] + 0.02 * np.array([-1, 1]) * case_definition_dict['xspan'][2]
                ly = node[1] + 0.01 * dy * np.array([1, 1]) * case_definition_dict['xspan'][2]
                ax.plot(lx, ly, c=c, lw=5)

                dy = (-0.02 if sup_type == 'slide' else -0.018)
                lx = node[0] + 0.02 * np.array([-1, 1]) * case_definition_dict['xspan'][2]
                ly = node[1] + dy * np.array([1, 1]) * case_definition_dict['xspan'][2]
                ax.plot(lx, ly, c=c, lw=5)

            if orientation == 'left' or orientation == 'right':
                dx = -1 if orientation == 'left' else 1
                lx = node[0] + 0.01 * dx * np.array([1, 1]) * case_definition_dict['xspan'][2]
                ly = node[1] + 0.02 * np.array([-1, 1]) * case_definition_dict['xspan'][2]
                ax.plot(lx, ly, c=c, lw=5)

                dx = (-0.02 if sup_type == 'slide' else -0.018)
                lx = node[0] + dx * np.array([1, 1]) * case_definition_dict['xspan'][2]
                ly = node[1] + 0.02 * np.array([-1, 1]) * case_definition_dict['xspan'][2]
                ax.plot(lx, ly, c=c, lw=5)

        for load in case_definition_dict['loads']:
            load_type, Fx, Fy, x, y = load
            ax.quiver(x, y,
                      np.full(x.shape, Fx), np.full(y.shape, Fy),
                      units='width',
                      scale_units='width',
                      scale=20,
                      # headlength=1,
                      width=0.007,
                      color='k',
                      zorder=5,
                      )

        ax.axis('image')
        ax.tick_params(left=False, labelleft=False)
        ax.tick_params(bottom=False, labelbottom=False)
        ax.axis('off')
        ax.set_aspect('equal')

        if fig:
            ax.set_xlim(case_definition_dict['xspan'][:2] +
                        0.05 * case_definition_dict['xspan'][2] * np.array([-1, 1]))
            ax.set_ylim(case_definition_dict['yspan'][:2] +
                        0.05 * case_definition_dict['yspan'][2] * np.array([-1, 1]))

        # ax.patch.set_edgecolor('black')
        # ax.patch.set_linewidth(1)
        # ax.set_facecolor("violet")
        # fig.patch.set_facecolor('ivory')
        # plt.tight_layout()
        # ax.axis('image')

        if fig:
            fig.patch.set_facecolor('whitesmoke')
            fig.savefig(f'{self.working_dir}/{case_name}.png', dpi=300)
            plt.close(fig)

    @staticmethod
    def calculate_mass(case_definition_dict):
        # Izračun volumena konstrukcije kao sume volumena svih greda
        V = 0
        A = case_definition_dict['xsec']
        # ELSET = [elements_1, elements_2, elements_3]
        nodes = case_definition_dict['nodes']

        elset = 0
        while f'elements_{elset + 1}' in case_definition_dict.keys():
            elset += 1

            elements = case_definition_dict[f'elements_{elset}']
            for i in range(elements.shape[0]):
                n1, n2 = elements[i, :]
                # n1, n2 = el_set[i, :]
                l = np.linalg.norm(nodes[n1, :] - nodes[n2, :])
                V += l * A[elset - 1]
        return V * case_definition_dict['density']

    def delete_files(self, case_name):
        # Deleting existing input and output files
        for ext in 'inp sta frd dat cvg 12d'.split():
            fpath = f'{self.working_dir}/{case_name}.{ext}'
            if os.path.exists(fpath):
                os.remove(fpath)

    @staticmethod
    def mesh_line(nodes, n1, n2, elements=np.full([0, 2], 0), dx=0.1):

        l = np.linalg.norm(nodes[n1] - nodes[n2])
        nn = int(np.ceil(l / dx))
        _nodes = np.full([nn, 2], np.nan)
        _nodes[:, 0] = np.linspace(nodes[n1, 0], nodes[n2, 0], nn + 2)[1:-1]
        _nodes[:, 1] = np.linspace(nodes[n1, 1], nodes[n2, 1], nn + 2)[1:-1]

        _elements = np.full([nn + 1, 2], -1)
        _elements[:, 0] = nodes.shape[0] + np.arange(nn + 1) - 1
        _elements[:, 1] = nodes.shape[0] + np.arange(nn + 1)
        _elements[0, 0] = n1
        _elements[-1, 1] = n2

        nodes = np.append(nodes, _nodes, axis=0)
        elements = np.append(elements, _elements, axis=0)

        return elements, nodes

    def _archbridge_parametrization(self, design):
        """
        Implementing parametrization for bridge1, bridge2, bridge3 cases
        """


        H, a1, a2, a3 = design
        case_definition_dict = {'design': design}
        L = 40  # m (Span)
        # H = 30  # m (Height)
        n = 101  # Number of nodes in horizontal direction
        dn = 10  # Number of nodes between vertical ropes
        if self.problem == 'bridge3':
            n = 111
            dn = 10
        dx = L / (n - 1)

        # Node coordinates
        x = np.array([])
        y = np.array([])
        # All beam elements
        elements = np.zeros([0, 2], dtype=int)

        # Road beam (horizontal)
        x1 = np.linspace(-0.5 * L, 0.5 * L, n)
        y1 = np.zeros(n)
        x = np.append(x, x1)
        y = np.append(y, y1)
        elements_1 = np.array([np.arange(0, n - 1),
                               np.arange(1, n)]).T
        elements = np.append(elements,
                             elements_1,
                             axis=0)

        # Arch beam
        x2 = x1[1:-1]
        y2 = H * (1 - x2 ** 2 / (0.5 * L) ** 2)
        x = np.append(x, x2)
        y = np.append(y, y2)
        elements_2 = elements_1.copy()
        elements_2 += n - 1
        elements_2[0, 0] = 0
        elements_2[-1, 1] = n - 1
        elements = np.append(elements,
                             elements_2,
                             axis=0)

        # Rope elements
        elements_3 = np.zeros([0, 2], dtype=int)
        for i in range(dn, n - dn, dn):
            if self.problem == 'bridge1':
                n1 = i
                n2 = i + n - 1
            elif self.problem == 'bridge2':
                n1 = i
                n2 = i + n - 1
                if i < (n - 1) / 2:
                    n2 += -dn // 2
                elif i > (n - 1) / 2:
                    n2 += dn // 2
            elif self.problem == 'archbridgex':
                n1 = i
                n2 = i + n - 1
                if i < (n - 1) / 2:
                    n2 += n // 2
                elif i > (n - 1) / 2:
                    n2 += - n // 2
                else:
                    continue
            elif self.problem == 'bridge3':
                n1 = i
                n2 = i + n - 1
                if int(i / dn) % 2 == 0:
                    pass
                    n2 += -dn // 2
                elif int(i / dn) % 2 == 1:
                    pass
                    n2 += dn // 2
                else:
                    continue

            l = np.linalg.norm([x[n1] - x[n2],
                               y[n1] - y[n2]])
            ne = int(np.max([np.floor(l / dx), 2]))
            # print(f'{n1=}, {n2=}, {l=}, {ne=}')
            for j in range(ne):
                elements_3 = np.append(elements_3,
                                       [[j + x.size - 1, j + x.size]],
                                       axis=0)
            elements_3[-ne, 0] = n1
            elements_3[-1, 1] = n2
            x3 = np.linspace(x[n1], x[n2], ne + 1)[1:-1]
            y3 = np.linspace(y[n1], y[n2], ne + 1)[1:-1]
            x = np.append(x, x3)
            y = np.append(y, y3)

        elements = np.append(elements,
                             elements_3,
                             axis=0)

        # All nodes (coordinates) in a single matrix
        nodes = np.zeros([x.size, 2])
        nodes[:, 0] = x
        nodes[:, 1] = y

        case_definition_dict['nodes'] = nodes
        case_definition_dict['elements_1'] = elements_1
        case_definition_dict['elements_2'] = elements_2
        case_definition_dict['elements_3'] = elements_3
        case_definition_dict['density'] = 7800

        case_definition_dict['xspan'] = (-0.5 * L, 0.5 * L, L)
        case_definition_dict['yspan'] = (-2, 10, 12)
        case_definition_dict['lwscale'] = 30
        case_definition_dict['smax'] = 30e6
        case_definition_dict['uscale'] = 100
        ryx = case_definition_dict['xspan'][2] / case_definition_dict['yspan'][2]
        case_definition_dict['scbar'] = (0.65, 0.85, 0.3, 0.01 * ryx)
        case_definition_dict['titlexy'] = (0.02, 0.95)
        case_definition_dict['labelxy'] = (0.02, 0.85)
        case_definition_dict['supports'] = [('pinned', 'down', nodes[elements_1[0, 0], :]),
                                            ('pinned', 'down', nodes[elements_1[-1, 1], :])]
        load_xy = nodes[[elements_1[0, 0], elements_1[-1, 1]], :]
        n = int(30 * np.linalg.norm(load_xy[1, :] - load_xy[0, :]) / case_definition_dict['xspan'][2])
        case_definition_dict['loads'] = [('dload', 0, -1, np.linspace(load_xy[0, 0], load_xy[1, 0], n),
                                          np.linspace(load_xy[0, 1], load_xy[1, 1], n)),
                                         ]

        case_definition_dict['A'] = np.array([a1, a2, a3])
        case_definition_dict['section_1'] = ('*BEAM SECTION, ELSET=elements_1, ' +
                                             'MATERIAL=steel, SECTION=RECT\n' +
                                             f'{a1}, {a1}\n' +
                                             '0.d0, 0.d0, 1.d0\n')
        case_definition_dict['section_2'] = ('*BEAM SECTION, ELSET=elements_2, ' +
                                             'MATERIAL=steel, SECTION=RECT\n' +
                                             f'{a2}, {a2}\n' +
                                             '0.d0, 0.d0, 1.d0\n')
        case_definition_dict['section_3'] = ('*BEAM SECTION, ELSET=elements_3, ' +
                                             'MATERIAL=steel, SECTION=RECT\n' +
                                             f'{a3}, {a3}\n' +
                                             '0.d0, 0.d0, 1.d0\n')
        case_definition_dict['xsec'] = np.array([a1, a2, a3])

        # Boundray conditions (supports)
        case_definition_dict['boundary'] = ('*BOUNDARY\n' +
                                            f'{elements_1[0, 0] + 1}, 1, 6\n' +  # Left support
                                            f'{elements_1[-1, 1] + 1}, 1, 6\n')  # Right support

        # Loads
        case_definition_dict['dload'] = ('*DLOAD\n' +
                                         'elements_all, GRAV, 9.81, 0, -1, 0\n' +  # Own weight of the structure
                                         f'elements_1, P2, {2e5 / a1}\n')  # load on the road [N/m]

        return case_definition_dict


    def _suspensionbridge_parametrization(self, design):

        H, a1, a2, a3, a4 = design
        case_definition_dict = {'design': design}
        L = 80  # m (Span)
        # H = 30  # m (Height)
        n = 128+1  # (has to be int * 4 + 1) Number of nodes in horizontal direction
        n_ropes = 16
        if self.problem == 'bridge5':
             n_ropes = 32

        dx = L / (n - 1)

        # Node coordinates
        x = np.array([])
        y = np.array([])

        # Road beam (horizontal)
        x1 = np.linspace(-0.5 * L, 0.5 * L, n)
        y1 = np.zeros(n)
        x = np.append(x, x1)
        y = np.append(y, y1)
        elements_1 = np.array([np.arange(0, n - 1),
                               np.arange(1, n)]).T


        # Cable beams
        x2 = x1[1:-1]
        y2 = H * (x2 / L * 4) ** 2
        y2[x2 < -0.25 * L] = H * ((x2[x2 < -0.25 * L] + 0.5 * L) / L * 4) ** 2
        y2[x2 > 0.25 * L] = H * ((x2[x2 > 0.25 * L] - 0.5 * L) / L * 4) ** 2
        x = np.append(x, x2)
        y = np.append(y, y2)
        # print(f'{np.max(y2)=}')
        elements_2 = elements_1.copy()
        elements_2 += n - 1
        elements_2[0, 0] = 0
        elements_2[-1, 1] = n - 1

        # Column elements
        elements_3 = np.zeros([0, 2], dtype=int)
        nodes_road_col3 = [(n - 1) // 4, 3 * (n - 1) // 4]
        for n_road, x_column in zip(nodes_road_col3, np.array([-1, 1]) * L * 0.25):
            y3 = np.linspace(0, H, int(np.max([np.ceil(H / dx), 3])))[1:-1]
            x3 = np.full(y3.size, x_column)
            x = np.append(x, x3)
            y = np.append(y, y3)
            _elements = np.array([np.arange(0, x3.size + 1),
                                  np.arange(1, x3.size + 2)]).T + (x.size - x3.size - 1)
            _elements[0, 0] = n_road
            _elements[-1, 1] = n_road + n - 1
            elements_3 = np.append(elements_3, _elements, axis=0)

        # Rope elements
        elements_4 = np.zeros([0, 2], dtype=int)
        XR = np.linspace(-0.5 * L, 0.5 * L, n_ropes + 1)[:-1]
        XR += 0.5 * (XR[1] - XR[0])
        for xr in XR:
            n_road = np.where(x == xr)[0][0]
            # print(n_road, n_road + n - 1)
            y4 = np.linspace(0, y[n_road + n - 1], int(np.max([np.ceil(y[n_road + n - 1] / dx), 3])))[1:-1]
            x4 = np.full(y4.size, x[n_road])
            x = np.append(x, x4)
            y = np.append(y, y4)
            _elements = np.array([np.arange(0, x4.size + 1),
                                  np.arange(1, x4.size + 2)]).T + (x.size - x4.size - 1)
            _elements[0, 0] = n_road
            _elements[-1, 1] = n_road + n - 1
            # print(_elements)
            elements_4 = np.append(elements_4, _elements, axis=0)

        # All nodes (coordinates) in a single matrix
        nodes = np.zeros([x.size, 2])
        nodes[:, 0] = x
        nodes[:, 1] = y

        case_definition_dict['nodes'] = nodes
        case_definition_dict['elements_1'] = elements_1
        case_definition_dict['elements_2'] = elements_2
        case_definition_dict['elements_3'] = elements_3
        case_definition_dict['elements_4'] = elements_4
        case_definition_dict['density'] = 7800

        case_definition_dict['xspan'] = (-0.5 * L, 0.5 * L, L)
        case_definition_dict['yspan'] = (-3, 14, 17)
        case_definition_dict['lwscale'] = 20
        case_definition_dict['smax'] = 30e6
        case_definition_dict['uscale'] = 100
        ryx = case_definition_dict['xspan'][2] / case_definition_dict['yspan'][2]
        case_definition_dict['scbar'] = (0.35, 0.85, 0.3, 0.01 * ryx)
        case_definition_dict['titlexy'] = (0.02, 0.95)
        case_definition_dict['labelxy'] = (0.02, 0.8)
        case_definition_dict['supports'] = [('fixed', 'down', nodes[elements_1[0, 0], :]),
                                            ('fixed', 'down', nodes[elements_1[-1, 1], :]),
                                            ('fixed', 'down', nodes[nodes_road_col3[0], :]),
                                            ('fixed', 'down', nodes[nodes_road_col3[1], :])]
        load_xy = nodes[[elements_1[0, 0], elements_1[-1, 1]], :]
        n = int(30 * np.linalg.norm(load_xy[1, :] - load_xy[0, :]) / case_definition_dict['xspan'][2])
        case_definition_dict['loads'] = [('dload', 0, -1, np.linspace(load_xy[0, 0], load_xy[1, 0], n),
                                          np.linspace(load_xy[0, 1], load_xy[1, 1], n)),
                                         ]

        case_definition_dict['A'] = np.array([a1, a2, a3, a4])
        case_definition_dict['section_1'] = ('*BEAM SECTION, ELSET=elements_1, ' +
                                             'MATERIAL=steel, SECTION=RECT\n' +
                                             f'{a1}, {a1}\n' +
                                             '0.d0, 0.d0, 1.d0\n')
        case_definition_dict['section_2'] = ('*BEAM SECTION, ELSET=elements_2, ' +
                                             'MATERIAL=steel, SECTION=RECT\n' +
                                             f'{a2}, {a2}\n' +
                                             '0.d0, 0.d0, 1.d0\n')
        case_definition_dict['section_3'] = ('*BEAM SECTION, ELSET=elements_3, ' +
                                             'MATERIAL=steel, SECTION=RECT\n' +
                                             f'{a3}, {a3}\n' +
                                             '0.d0, 0.d0, 1.d0\n')
        case_definition_dict['section_4'] = ('*BEAM SECTION, ELSET=elements_4, ' +
                                             'MATERIAL=steel, SECTION=RECT\n' +
                                             f'{a4}, {a4}\n' +
                                             '0.d0, 0.d0, 1.d0\n')
        case_definition_dict['xsec'] = np.array([a1, a2, a3, a4])

        # Boundray conditions (supports)
        case_definition_dict['boundary'] = ('*BOUNDARY\n' +
                                            f'{elements_1[0, 0] + 1}, 1, 6\n' +  # Left support
                                            f'{elements_1[-1, 1] + 1}, 1, 6\n' +  # Right support
                                            f'{nodes_road_col3[0] + 1}, 1, 6\n'  # Right column support
                                            f'{nodes_road_col3[1] + 1}, 1, 6\n'  # Right column support
                                            )

        # Loads
        case_definition_dict['dload'] = ('*DLOAD\n' +
                                         'elements_all, GRAV, 9.81, 0, -1, 0\n' +  # Own weight of the structure
                                         'elements_1, P2, 2e5\n')  # load on the road [N/m]

        return case_definition_dict

    def _corner_parametrization(self, design):

        variant = self.problem
        if variant == 'corner3':
            ny3, a1, a2, a3 = design
        if variant == 'corner5':
            nx3, ny3, ny4, a1, a2, a3, a4, a5 = design
        case_definition_dict = {'design': design}

        max_dx = 0.025
        # Node coordinates
        x = np.array([])
        y = np.array([])
        # All beam elements
        elements = np.zeros([0, 2], dtype=int)

        # beam 1 (1-2)
        n12 = int(np.max([3, np.ceil(0.5 / max_dx + 1)]))
        x12 = np.linspace(0, 0.5, n12)
        y12 = np.linspace(0, 0, n12)
        x = np.append(x, x12)
        y = np.append(y, y12)
        elements_1 = np.array([np.arange(0, n12 - 1),
                               np.arange(1, n12)]).T
        elements = np.append(elements,
                             elements_1,
                             axis=0)

        # beam 2 (2-3)
        if variant == 'corner3':
            n23 = int(np.max([3, np.ceil(np.sqrt(0.5**2 + ny3**2) / max_dx + 1)]))
            x23 = np.linspace(0.5, 0, n23)[1:]
            y23 = np.linspace(0, ny3, n23)[1:]
        if variant == 'corner5':
            n23 = int(np.max([3, np.ceil(np.sqrt((0.5 - nx3)**2 + ny3**2) / max_dx + 1)]))
            x23 = np.linspace(0.5, nx3, n23)[1:]
            y23 = np.linspace(0, ny3, n23)[1:]
        x = np.append(x, x23)
        y = np.append(y, y23)
        elements_2 = np.array([np.arange(0, n23 - 1),
                               np.arange(1, n23)]).T + elements.shape[0]
        elements = np.append(elements,
                             elements_2,
                             axis=0)

        # beam 3 (3-4)
        if variant == 'corner3':
            n34 = int(np.max([3, np.ceil(np.abs(ny3 / max_dx) + 1)]))
            x34 = np.linspace(0, 0,n34)[1:-1]
            y34 = np.linspace(ny3, 0, n34)[1:-1]
            x = np.append(x, x34)
            y = np.append(y, y34)
            elements_3 = np.array([np.arange(0, n34 - 2),
                                   np.arange(1, n34 - 1)]).T + elements.shape[0]
            elements_3 = np.append(elements_3,
                                 np.array([[x.size - 1, 0]]),
                                 axis=0)
            elements = np.append(elements,
                                 elements_3,
                                 axis=0)
        if variant == 'corner5':
            n34 = int(np.max([3, np.ceil(np.sqrt(nx3**2 + (ny4 - ny3)**2) / max_dx + 1)]))
            x34 = np.linspace(nx3, 0,n34)[1:]
            y34 = np.linspace(ny3, ny4, n34)[1:]
            x = np.append(x, x34)
            y = np.append(y, y34)
            elements_3 = np.array([np.arange(0, n34 - 1),
                                   np.arange(1, n34)]).T + elements.shape[0]
            elements = np.append(elements,
                                 elements_3,
                                 axis=0)

        if variant == 'corner5':
            # beam 4 (4-1)
            n41 = int(np.max([3, np.ceil(-ny4 / max_dx + 1)]))
            x41 = np.linspace(0,0, n41)[1:-1]
            y41 = np.linspace(ny4, 0, n41)[1:-1]
            x = np.append(x, x41)
            y = np.append(y, y41)
            elements_4 = np.array([np.arange(0, n41 - 2),
                                   np.arange(1, n41 - 1)]).T + elements.shape[0]
            elements_4 = np.append(elements_4,
                                 np.array([[x.size - 1, 0]]),
                                 axis=0)
            elements = np.append(elements,
                                 elements_4,
                                 axis=0)

        if variant == 'corner5':
            # beam 5 (1-3)
            n13 = int(np.max([3, np.ceil(np.sqrt(nx3**2 + ny3**2) / max_dx + 1)]))
            x13 = np.linspace(0,nx3, n13)[1:-1]
            y13 = np.linspace(0, ny3, n13)[1:-1]
            x = np.append(x, x13)
            y = np.append(y, y13)
            elements_5 = np.array([np.arange(0, n13 - 1),
                                   np.arange(1, n13)]).T + elements.shape[0] - 1
            elements_5[0, 0] = elements_1[0, 0]
            elements_5[-1, 1] = elements_2[-1, 1]
            elements = np.append(elements,
                                 elements_5,
                                 axis=0)


        # All nodes (coordinates) in a single matrix
        nodes = np.zeros([x.size, 2])
        nodes[:, 0] = x
        nodes[:, 1] = y

        case_definition_dict['nodes'] = nodes
        case_definition_dict['elements_1'] = elements_1
        case_definition_dict['elements_2'] = elements_2
        case_definition_dict['elements_3'] = elements_3
        if variant == 'corner5':
            case_definition_dict['elements_4'] = elements_4
            case_definition_dict['elements_5'] = elements_5
        case_definition_dict['density'] = 7800

        case_definition_dict['xspan'] = (0, 0.5, 0.5)
        case_definition_dict['yspan'] = (-0.35, 0, 0.35)
        case_definition_dict['lwscale'] = 100
        case_definition_dict['smax'] = 30e6
        case_definition_dict['uscale'] = 100
        ryx = case_definition_dict['xspan'][2] / case_definition_dict['yspan'][2]
        case_definition_dict['scbar'] = (0.6, 0.05 * ryx, 0.3, 0.01 * ryx)
        case_definition_dict['titlexy'] = (0.604, 0.2 * ryx)
        case_definition_dict['labelxy'] = (0.604, 0.15 * ryx)
        if variant == 'corner3':
            case_definition_dict['supports'] = [('slide', 'left', nodes[elements_3[0, 0], :]),
                                                ('pinned', 'left', nodes[elements_3[-1, 1], :])]
        if variant == 'corner5':
            case_definition_dict['supports'] = [('slide', 'left', nodes[elements_4[0, 0], :]),
                                                ('pinned', 'left', nodes[elements_4[-1, 1], :])]
        load_xy = nodes[[elements_1[0, 0], elements_1[-1, 1]], :]
        n = int(30 * np.linalg.norm(load_xy[1, :] - load_xy[0, :]) / case_definition_dict['xspan'][2])
        case_definition_dict['loads'] = [('dload', 0, -1, np.linspace(load_xy[0, 0], load_xy[1, 0], n),
                                          np.linspace(load_xy[0, 1], load_xy[1, 1], n)),
                                         ]

        if variant == 'corner3':
            A = np.array([a1, a2, a3])
        if variant == 'corner5':
            A = np.array([a1, a2, a3, a4, a5])
        case_definition_dict['A'] = A
        for sec, a in enumerate(A):
            case_definition_dict[f'section_{sec + 1}'] = (f'*BEAM SECTION, ELSET=elements_{sec + 1}, ' +
                                                            'MATERIAL=steel, SECTION=RECT\n' +
                                                            f'{a}, {a}\n' +
                                                            '0.d0, 0.d0, 1.d0\n')
        case_definition_dict['xsec'] = A

        # Boundray conditions (supports)
        if variant == 'corner3':
            case_definition_dict['boundary'] = ('*BOUNDARY\n' +
                                                f'{elements_1[0, 0] + 1}, 1, 3\n' +
                                                f'{elements_3[0, 0] + 0}, 1, 1\n' +
                                                f'{elements_3[0, 0] + 0}, 3, 3\n'
                                                )
        if variant == 'corner5':
            case_definition_dict['boundary'] = ('*BOUNDARY\n' +
                                                f'{elements_1[0, 0] + 1}, 1, 3\n' +
                                                f'{elements_4[0, 0] + 0}, 1, 1\n' +
                                                f'{elements_4[0, 0] + 0}, 3, 3\n'
                                                )

        # Loads
        case_definition_dict['dload'] = ('*DLOAD\n' +
                                         'elements_all, GRAV, 9.81, 0, -1, 0\n' +  # Own weight of the structure
                                         f'elements_1, P2, {1e5 / a1}\n')  # load  [N/m]

        return case_definition_dict


    def _box_parametrization(self, design):

        variant: str = self.problem
        case_definition_dict = {'design': design}

        nx, ny = [int(n) for n in variant[3:].split('x')]

        x = np.linspace(0, 1, nx)
        y = np.linspace(0, 1, ny)

        # Nodes
        nodes = np.full([0, 2], 0.0, dtype=float)
        for iy, _y in enumerate(y):
            for ix, _x in enumerate(x):
                nodes = np.append(nodes, np.array([[_x, _y]]), axis=0)

        # Elements and elsets
        max_dx = 0.05
        elsets = []
        for iy in range(ny):
            for ix in range(nx - 1):
                # print(iy * nx + ix, iy * nx + ix + 1)
                _elements, nodes = self.mesh_line(nodes, iy * nx + ix, iy * nx + ix + 1, dx=max_dx)
                elsets.append(_elements)

        for ix in range(nx):
            for iy in range(ny - 1):
                # print(iy * nx + ix, (iy + 1) * nx + ix)
                _elements, nodes = self.mesh_line(nodes, iy * nx + ix, (iy + 1) * nx + ix, dx=max_dx)
                elsets.append(_elements)


        # nx2, nx3, nx5, nx6, nx8, ny8, nx9, ny9, *A = design
        A = design

        # Supports
        case_definition_dict['supports'] = [('pinned', 'down', nodes[0, :]),
                                            ('pinned', 'down', nodes[nx - 1, :])]

        case_definition_dict['boundary'] = ('*BOUNDARY\n' +
                                            f'{0 + 1}, 1, 3\n' +
                                            f'{nx}, 1, 3\n'
                                            )

        i_load1 = nx * (ny - 1) + int(np.floor(nx / 2))
        i_load2 = nx * int(np.floor(ny / 2))
        case_definition_dict['cload'] = (f'*CLOAD\n{i_load1 + 1}, 2, -2.1e4\n'
                                         f'*CLOAD\n{i_load2 + 1}, 1, 1e4\n')  # load  [N]

        # load_type, Fx, Fy, x, y = load
        case_definition_dict['loads'] = [(f'cload', 0, -2.1*2, nodes[i_load1, 0], nodes[i_load1, 1]),
                                         (f'cload', 1*1, 0, nodes[i_load2, 0], nodes[i_load2, 1]),
                                         ]



        case_definition_dict['nodes'] = nodes
        for i, elset in enumerate(elsets):
            case_definition_dict[f'elements_{i + 1}'] = elset
        case_definition_dict['density'] = 7800

        case_definition_dict['xspan'] = (-0.05, 1.05, 1.1)
        case_definition_dict['yspan'] = (-0.05, 1.05, 1.1)
        case_definition_dict['lwscale'] = 200
        case_definition_dict['smax'] = 30e6
        case_definition_dict['uscale'] = 50
        ryx = case_definition_dict['xspan'][2] / case_definition_dict['yspan'][2]
        case_definition_dict['scbar'] = (0.15, 0.2 * ryx, 0.3, 0.01 * ryx)
        case_definition_dict['titlexy'] = (0.02, 0.98)
        case_definition_dict['labelxy'] = (0.15, 0.7)

        load_xy = nodes[[0, 2 * nx], :]
        n = int(30 * np.linalg.norm(load_xy[1, :] - load_xy[0, :]) / case_definition_dict['xspan'][2])

        case_definition_dict['A'] = A
        for sec, a in enumerate(A):
            case_definition_dict[f'section_{sec + 1}'] = (f'*BEAM SECTION, ELSET=elements_{sec + 1}, ' +
                                                            'MATERIAL=steel, SECTION=RECT\n' +
                                                            f'{a}, {a}\n' +
                                                            '0.d0, 0.d0, 1.d0\n')
        case_definition_dict['xsec'] = A


        return case_definition_dict

    def _cantileverbeam_parametrization(self, design):

        variant = self.problem
        case_definition_dict = {'design': design}

        if variant == 'cabeam8':
            # nx2, nx4, nx6, a1, a2, a3, a4, a5, a6, a7, a8 = design
            nx2, nx4, nx6, *A = design

            # Nodes            x,   y
            nodes = np.array([[0.0, -0.1], # 0
                              [nx2, -0.1], # 1
                              [0.6,  0.0], # 2
                              [nx4,  0.1], # 3
                              [0.0,  0.1], # 4
                              [nx6,  0.0], # 5
                              ])

            # Elements
            max_dx = 0.025
            elements1, nodes = self.mesh_line(nodes, 0, 1, dx=max_dx)
            elements2, nodes = self.mesh_line(nodes, 1, 2, dx=max_dx)
            elements3, nodes = self.mesh_line(nodes, 2, 3, dx=max_dx)
            elements4, nodes = self.mesh_line(nodes, 3, 4, dx=max_dx)
            elements5, nodes = self.mesh_line(nodes, 4, 5, dx=max_dx)
            elements6, nodes = self.mesh_line(nodes, 5, 0, dx=max_dx)
            elements7, nodes = self.mesh_line(nodes, 5, 3, dx=max_dx)
            elements8, nodes = self.mesh_line(nodes, 5, 1, dx=max_dx)
            elsets = [elements1, elements2, elements3, elements4,
                      elements5, elements6, elements7, elements8]
        elif variant == 'cabeam14':
            # nx2, nx4, nx6, a1, a2, a3, a4, a5, a6, a7, a8 = design
            nx2, nx3, nx5, nx6, nx8, ny8, nx9, ny9, *A = design

            y0 = 0.1
            # Nodes            x,      y
            nodes = np.array([[0, -y0],  # 0
                              [nx2, -y0],  # 1
                              [nx3, -y0],  # 2
                              [0.6, 0.0],  # 3
                              [nx5, y0],  # 4
                              [nx6, y0],  # 5
                              [0.0, y0],  # 6
                              [nx8, ny8],  # 7
                              [nx9, ny9],  # 8
                              ])

            # Elements
            max_dx = 0.025
            elements1, nodes = self.mesh_line(nodes, 0, 1, dx=max_dx)
            elements2, nodes = self.mesh_line(nodes, 1, 2, dx=max_dx)
            elements3, nodes = self.mesh_line(nodes, 2, 3, dx=max_dx)
            elements4, nodes = self.mesh_line(nodes, 3, 4, dx=max_dx)
            elements5, nodes = self.mesh_line(nodes, 4, 5, dx=max_dx)
            elements6, nodes = self.mesh_line(nodes, 5, 6, dx=max_dx)
            elements7, nodes = self.mesh_line(nodes, 7, 0, dx=max_dx)
            elements8, nodes = self.mesh_line(nodes, 7, 6, dx=max_dx)
            elements9, nodes = self.mesh_line(nodes, 7, 1, dx=max_dx)
            elements10, nodes = self.mesh_line(nodes, 7, 5, dx=max_dx)
            elements11, nodes = self.mesh_line(nodes, 8, 1, dx=max_dx)
            elements12, nodes = self.mesh_line(nodes, 8, 2, dx=max_dx)
            elements13, nodes = self.mesh_line(nodes, 8, 4, dx=max_dx)
            elements14, nodes = self.mesh_line(nodes, 8, 5, dx=max_dx)

            elsets = [elements1, elements2, elements3, elements4, elements5, elements6, elements7,
                      elements8, elements9, elements10, elements11, elements12, elements13, elements14]

        case_definition_dict['nodes'] = nodes
        for i, elset in enumerate(elsets):
            case_definition_dict[f'elements_{i + 1}'] = elset
        case_definition_dict['density'] = 7800

        case_definition_dict['xspan'] = (-0.05, 0.65, 0.7)
        case_definition_dict['yspan'] = (-0.15, 0.15, 0.3)
        case_definition_dict['lwscale'] = 200
        case_definition_dict['smax'] = 30e6
        case_definition_dict['uscale'] = 100
        ryx = case_definition_dict['xspan'][2] / case_definition_dict['yspan'][2]
        case_definition_dict['scbar'] = (0.7, 0.1, 0.27, 0.01 * ryx)
        case_definition_dict['titlexy'] = (0.02, 0.42 * ryx)
        case_definition_dict['labelxy'] = (0.5, 0.42 * ryx)
        if variant == 'cabeam8':
            case_definition_dict['supports'] = [('fixed', 'left', nodes[elements1[0, 0], :]),
                                                ('fixed', 'left', nodes[elements4[-1, 1], :])]
        if variant == 'cabeam14':
            case_definition_dict['supports'] = [('fixed', 'left', nodes[0, :]),
                                                ('fixed', 'left', nodes[6, :])]
        load_xy = nodes[[elements1[0, 0], elements1[-1, 1]], :]
        n = int(30 * np.linalg.norm(load_xy[1, :] - load_xy[0, :]) / case_definition_dict['xspan'][2])
        case_definition_dict['loads'] = [('cload', 0, -2, np.array([0.6]), np.array([0])),
                                         ]

        # if variant == 'cabeam8':
        #     A = np.array([a1, a2, a3, a4, a5, a6, a7, a8])
        case_definition_dict['A'] = A
        for sec, a in enumerate(A):
            case_definition_dict[f'section_{sec + 1}'] = (f'*BEAM SECTION, ELSET=elements_{sec + 1}, ' +
                                                            'MATERIAL=steel, SECTION=RECT\n' +
                                                            f'{a}, {a}\n' +
                                                            '0.d0, 0.d0, 1.d0\n')
        case_definition_dict['xsec'] = A

        # Boundray conditions (supports)
        if variant == 'cabeam8':
            case_definition_dict['boundary'] = ('*BOUNDARY\n' +
                                                f'{elements1[0, 0] + 1}, 1, 6\n' +
                                                f'{elements4[-1, 1] + 1}, 1, 6\n'
                                                )
        if variant == 'cabeam14':
            case_definition_dict['boundary'] = ('*BOUNDARY\n' +
                                                f'1, 1, 6\n' +
                                                f'7, 1, 6\n'
                                                )


        # Loads
        # case_definition_dict['dload'] = ('*DLOAD\n' +
        #                                  'elements_all, GRAV, 9.81, 0, -1, 0\n' +  # Own weight of the structure
        #                                  f'elements_1, P2, {1e5 / a1 / 0.5}\n')  # load  [N/m]

        if variant == 'cabeam8':
            case_definition_dict['cload'] = ('*CLOAD\n' +
                                         '3, 2, -1e5\n')  # load  [N]
        if variant == 'cabeam14':
            case_definition_dict['cload'] = ('*CLOAD\n' +
                                         '4, 2, -1e5\n')  # load  [N]

        return case_definition_dict


SFD_problems_dict_list = []
for case, (dimensions, max_evals) in _read_structural_frame_cases_dict().items():
    problem_dict = {'label': f'SFD_{case}_{int(dimensions)}D',
                    'class': StructuralFrame,
                    'case': case,
                    'dimensions': None,
                    'max_evaluations': max_evals,
                    'max_runs': 1000,
                    'forward_unique_str': True,
                    }
    SFD_problems_dict_list.append(problem_dict)

if __name__ == '__main__':

    # Trying out StructuralFrame
    # for problem in ['box3x3', 'box4x3', 'box3x4', 'box4x4', 'box5x4', 'box4x5', 'box5x5']:
    # # for problem in ['box4x4']:
    # # for problem in _read_structural_frame_cases_dict():
    #     print(f'*** Testing {problem}')
    #     sf = StructuralFrame(problem=problem)
    #     design0 = np.random.uniform(sf.lb, sf.ub)
    #     sf.simulate(design0, f'test_{problem}', keep_files=True)
    #
    #     # Trying simple optimization
    #     import indago
    #     optimizer = indago.DE()
    #     optimizer.evaluation_function = sf
    #     optimizer.lb = sf.lb
    #     optimizer.ub = sf.ub
    #     # optimizer.max_evaluations = 40_000
    #     # optimizer.X0 = design0
    #     optimizer.monitoring = 'dashboard'
    #     optimizer.forward_unique_str = True
    #     optimizer.processes = 8
    #     optimizer.convergence_log_file = f'{sf.working_dir}/convergence_{problem}.log'
    #     best = optimizer.optimize()
    #     optimizer.plot_history(f'{sf.working_dir}/convergence_{problem}.png')
    #     sf.simulate(best.X, f'{problem}_best', keep_files=True)

    # Run standard test
    import indagobench, shutil
    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir,
                                             processes=10)
    standard_test.optimizers = indagobench.indagobench25_optimizers
    standard_test.problems = SFD_problems_dict_list
    # standard_test.run_all()


    """Results postprocessing and visualization"""
    class_results_dir = f'{indagobench._local_paths.indagobench25_results_dir}/SFD/'
    if not os.path.exists(class_results_dir):
        os.mkdir(class_results_dir)

    # Manuscript figures
    for problem_dict in [indagobench.get_problem_dict('SFD_cabeam8_11D')]:
        fr = indagobench.ProblemResults(problem_dict)
        fr.optimizers = ['LSHADE', 'GA', 'CMAES']
        fr.make_full_convergence_figure(f'{class_results_dir}/short_conv_{problem_dict["label"]}.png',
                                        header_plots=False)

    # problem_dict = indagobench.get_problem_dict('SFD_bridge5_5D')
    # sf = StructuralFrame(problem_dict['case'])
    # results = indagobench.ProblemResults(problem_dict)
    # results.update_referent_values(verbose=True)
    # results.optimizers = ['CMAES', 'GA', 'MSGD']
    # results.make_full_convergence_figure(
    #     f'{indagobench._local_paths.indagobench25_results_dir}/SFD/short_conv_{problem_dict["label"]}.png',
    #     header_plots=False)

    for problem_dict in standard_test.problems:
    # for problem_dict in [indagobench.get_problem_dict('SFD_bridge1_4D')]:
        sf = StructuralFrame(problem_dict['case'])
        results = indagobench.ProblemResults(problem_dict)
        # results.update_referent_values(verbose=True)
        results.make_full_convergence_figure(f'{indagobench._local_paths.indagobench25_results_dir}/convergence/full_conv_{problem_dict["label"]}.png',
                                             header_plots=True)

        case_name = f'{problem_dict["label"]}_best'
        x_min = results.results[indagobench.ResultsKeyPrefix._x_min]
        print(f'{x_min=}')
        sf.simulate(x_min, case_name, keep_files=True)
        shutil.copyfile(f'{sf.working_dir}/{case_name}.png',
                        f'{indagobench._local_paths.indagobench25_results_dir}/SFD/{case_name}.png')

        for optimizer in standard_test.optimizers:
            if indagobench.ResultsKeyPrefix.f_best + optimizer['label'] not in results.results.keys():
                continue
            f_best = results.results[indagobench.ResultsKeyPrefix.f_best + optimizer['label']]
            i = np.argmin(np.abs(np.median(f_best) - f_best))
            x = results.results[indagobench.ResultsKeyPrefix.x_best + optimizer['label']][i, :]
            # print(f[:, -1])
            # print(f'best_i={i}')
            case_name = f'{problem_dict["label"]}_{optimizer["label"].replace(" ", "-")}_median'
            sf.simulate(x, case_name, keep_files=True)
            shutil.copyfile(f'{sf.working_dir}/{case_name}.png',
                            f'{indagobench._local_paths.indagobench25_results_dir}/SFD/{case_name}.png')


        # # fig, axes = plt.subplots(figsize=(15, 30),
        # #                          nrows=4, ncols=3, tight_layout=True)
        # X2 = np.arange(2) / 2
        # X3 = np.arange(3) / 3
        # W2 = 0.5
        # W3 = 0.3
        # # Y = np.arange(6)[::-1] / 6
        # H = np.array([3, 2.4, 2.2, 2., 3, 3.4], dtype=float)#[::-1]
        # fig = plt.figure(figsize=(10, np.sum(H)))
        # # fig.patch.set_facecolor('xkcd:mint green')
        # H /= np.sum(H)
        # Y = 1 - np.cumsum(H)
        # print(f'{H=}')
        # print(f'{Y=}')
        #
        # axes = []
        # for row in range(6):
        #     for col in range(2 if row < 5 else 3):
        #         ax = fig.add_axes([X2[col] if row < 5 else X3[col],
        #                            Y[row],
        #                            W2 if row < 5 else W3,
        #                            H[row]], frameon=True, facecolor='r')
        #         # ax.text(0, 1, f'row={row}, col={col}', transform=ax.transAxes, va='top')
        #         axes.append(ax)
        #
        #
        # for problem_dict,ax  in zip(SFD_problems_dict_list, axes):
        #     sf = StructuralFrame(problem_dict['case'])
        #     case_name = f'{problem_dict["label"]}_x0'
        #     x = 0.5 * (sf.lb + sf.ub)
        #     sf.simulate(x, case_name, keep_files=True, ax=ax)
        #     ax.text(0, 1.06, problem_dict['case'],
        #             fontsize=16,
        #             va='top', transform=ax.transAxes,)
        #
        # plt.savefig(f'{indagobench._local_paths.indagobench25_results_dir}/SFD/SFD_all_cases.png')
        # plt.close(fig)
        # # plt.show()