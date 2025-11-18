import pathlib
import shutil
import datetime
import numpy as np
import os
from textwrap import dedent
import subprocess
import sys
sys.path.append('..')

try:
    import scipy as sp
    import pyvista as pv
    import matplotlib.pyplot as plt
    import indagobench

except ImportError as e:
    print('\033[91m' + f'Failed at importing optional module: {e.msg}')
    print('Code will continue but evaluation using FlowFit class is not possible.' + '\033[0m')


class FlowFit:

    def __init__(self, problem, dimensions=None, instance_label=None, keep_results=True):
        self.problem = problem
        self.keep_results = keep_results

        self.working_dir = pathlib.Path(f'{indagobench._local_paths.openfoam_tmp_dir}/FlowFit_{instance_label}')

        if os.path.exists(self.working_dir):
            shutil.rmtree(self.working_dir)
        os.mkdir(self.working_dir)

        self.template_case = f'{os.path.dirname(os.path.abspath(__file__))}/flow_fit_data/{self.problem}'

        self.read_mesh()
        self.process_boundary()
        self.boundary_summary()

        assert dimensions % 2 == 0, 'number of dimensions must be even'
        self.dimensions = dimensions
        self.n_ctrl = [dimensions // 2]

        npz = np.load(f'{self.template_case}/probes.npz')
        self.field_points = npz['field_points']
        self.sample_points = npz['sample_points']
        self.ref_vxy = npz['sample_vxy']

        if problem == 'bay1' or problem == 'bay2':

            if problem == 'bay1':
                self.lb = np.array([-0.3] * int(np.sum(self.n_ctrl)) +  # v_t
                                   [-0.05] * int(np.sum(self.n_ctrl)))  # p
                self.ub = np.array([0.3] * int(np.sum(self.n_ctrl)) +  # v_t
                                   [0.05] * int(np.sum(self.n_ctrl)))  # p

            if problem == 'bay2':
                self.lb = np.array([-0.5] * int(np.sum(self.n_ctrl)) +  # v_t
                                   [-0.1] * int(np.sum(self.n_ctrl)))  # p
                self.ub = np.array([0.5] * int(np.sum(self.n_ctrl)) +  # v_t
                                   [0.1] * int(np.sum(self.n_ctrl)))  # p

            self.ref_residuals = {'Ux': 1e-04,
                                  'Uy': 1e-04,
                                  'k': 1e-04,
                                  'omega': 1e-04,
                                  'p': 1e-03,
                                  }

            self.vis_params = {
                'v_max': 0.3,
                'cbar_n': 5,
                'cbar_x': 0.7,
                'cbar_y': 0.03,
                'cbar_w': 0.25,
                'cbar_h': 0.03,
                'scale_x': 0.02,
                'scale_y': 0.03,
                'scale_size': 1000,
                'legend_x': -0.05,
                'legend_y': 0.1,
            }
        elif problem == 'open1' or problem == 'open2':

            self.lb = np.array([-0.5] * int(np.sum(self.n_ctrl)) +  # v_t
                               [-0.03] * int(np.sum(self.n_ctrl)))   # p
            self.ub = np.array([0.5] * int(np.sum(self.n_ctrl)) +   # v_t
                               [0.03] * int(np.sum(self.n_ctrl)))    # p

            self.ref_residuals = {'Ux': 1e-04,
                                  'Uy': 1e-04,
                                  'k': 1e-04,
                                  'omega': 1e-04,
                                  'p': 5e-03,
}

            self.vis_params = {
                'v_max': 0.4,
                'cbar_n': 5,
                'cbar_x': 0.7,
                'cbar_y': 0.03,
                'cbar_w': 0.25,
                'cbar_h': 0.03,
                'scale_x': 0.02,
                'scale_y': 0.03,
                'scale_size': 1000,
                'legend_x': -0.05,
                'legend_y': 0.1,
            }
        else:
            assert False, f'Unknown problem {problem}'

        # Turbulence setup
        self.turbulence_variables = {
            'turbulence_intensity': 0.05,
            'turbulence_length_scale': 50,
        }

    def __del__(self):
        if not self.keep_results:
            self.delete_results_dir()

    def delete_results_dir(self):
            if os.path.exists(self.working_dir):
                shutil.rmtree(self.working_dir)

    @staticmethod
    def problem_dicts():
        return [{'case': 'bay1', 'dimensions': 6, 'max_evaluations': 1_500}, #0
                {'case': 'bay1', 'dimensions': 10, 'max_evaluations': 1_500}, #1
                {'case': 'bay2', 'dimensions': 6, 'max_evaluations': 1_000}, #2
                {'case': 'bay2', 'dimensions': 8, 'max_evaluations': 1_000}, #3
                {'case': 'bay2', 'dimensions': 10, 'max_evaluations': 1_000}, #4
                {'case': 'bay2', 'dimensions': 12, 'max_evaluations': 1_000}, #5
                {'case': 'open1', 'dimensions': 12, 'max_evaluations': 1_500}, #6
                {'case': 'open1', 'dimensions': 16, 'max_evaluations': 2_000} #7
                ]

    def read_mesh(self):

        # Read points
        points_file = f'{self.template_case}/constant/polyMesh/points'
        with open(points_file) as f:
            lines = f.readlines()
            for i_start, line in enumerate(lines):
                if line.strip().isdigit():
                    n_points = int(line)
                    # print(f'{n_points=}, line={i_start}')
                    break

            self.points = np.full([n_points, 3], np.nan)
            for i_point in range(n_points):
                line = lines[i_start + i_point + 2].strip().strip('(').strip(')')
                # print(line)
                self.points[i_point, :] = [float(n) for n in line.split()]

        # Read faces
        faces_file = f'{self.template_case}/constant/polyMesh/faces'
        with open(faces_file) as f:
            lines = f.readlines()
            for i_start, line in enumerate(lines):
                if line.strip().isdigit():
                    n_faces = int(line)
                    # print(f'{n_faces=}, line={i_start}')
                    break

            self.faces = np.full([n_faces, 4], -1, dtype=int)
            for i_face in range(n_faces):
                line = lines[i_start + i_face + 2].replace('(', ' ').replace(')', ' ').strip()
                # print(line)
                self.faces[i_face, :] = [int(n) for n in line.split()[1:]]
            # print(self.faces)

        # Read boundary
        boundary_file = f'{self.template_case}/constant/polyMesh/boundary'
        with open(boundary_file) as f:
            lines = f.readlines()
            for i_start, line in enumerate(lines):
                if line.strip().isdigit():
                    n_boundary = int(line)
                    # print(f'{n_boundary=}, line={i_start}')
                    break

            self.boundary = []
            i_line = i_start + 2
            for i_boundary in range(n_boundary):

                boundary = {}
                boundary['name'] = lines[i_line].strip()
                i_line += 1
                while True:
                    line = lines[i_line]
                    i_line += 1
                    if line.strip() == '}':
                        break
                    if line.strip() == '{':
                        continue
                    s = line.strip().strip(';').split(' ', 1)
                    boundary[s[0].strip()] = s[1].strip()
                self.boundary.append(boundary)
        # for b in self.boundary:
        #     print(f'{b}')
        # input(' >> Press return to continue.')

    def process_boundary(self):
        for boundary in self.boundary:

            if boundary['type'] not in 'patch wall'.split():
                continue

            start_face = int(boundary['startFace'])
            n_faces = int(boundary['nFaces'])

            boundary_2d = np.full([0, 2], np.nan)
            for i_face in range(start_face, start_face + n_faces):
                i_points = np.asarray(self.faces[i_face], dtype=int)
                # print(i_points)
                points = self.points[i_points]
                z_plus = np.max(points[:, 2])
                points = points[points[:, 2] == z_plus, :2]

                if boundary_2d.shape[0] == 0:
                    boundary_2d = points[:, :2]
                else:
                    if np.all(boundary_2d[0, :] == points[0, :]):
                        boundary_2d = np.append(points[1:, :], boundary_2d, axis=0)
                    elif np.all(boundary_2d[0, :] == points[1, :]):
                        boundary_2d = np.append(points[:1, :], boundary_2d, axis=0)
                    elif np.all(boundary_2d[-1, :] == points[0, :]):
                        boundary_2d = np.append(boundary_2d, points[1:, :], axis=0)
                    elif np.all(boundary_2d[-1, :] == points[1, :]):
                        boundary_2d = np.append(boundary_2d, points[:1, :], axis=0)
                    else:
                        print('Error!')

            boundary['nodes_xy'] = boundary_2d
            boundary['face_lengths'] = np.linalg.norm(boundary_2d[1:, :] - boundary_2d[:-1, :], axis=1)
            s = np.append([0], np.cumsum(boundary['face_lengths']))
            boundary['face_s'] = (s[1:] + s[:-1]) / 2
            boundary['face_tangents'] = (boundary_2d[1:, :] - boundary_2d[:-1, :])
            boundary['face_normals'] = (boundary_2d[1:, :] - boundary_2d[:-1, :])
            for i_face in range(boundary['face_tangents'].shape[0]):
                boundary['face_tangents'][i_face, :] /= boundary['face_lengths'][i_face]
                boundary['face_normals'][i_face, :] = [-boundary['face_tangents'][i_face, 1],
                                                       boundary['face_tangents'][i_face, 0]]

            # print(f'{boundary=}')

    def boundary_summary(self):
        scale = 1000
        fig, ax = plt.subplots()
        for boundary in self.boundary:
            # print(f'{boundary=}')
            if boundary['type'] == 'wall':
                ax.plot(boundary['nodes_xy'][:, 0], boundary['nodes_xy'][:, 1], '.--')
            if boundary['type'] == 'patch':
                ax.plot(boundary['nodes_xy'][:, 0], boundary['nodes_xy'][:, 1], '.-')
                for i_face in range(boundary['face_normals'].shape[0]):
                    n_xy = boundary['face_normals'][i_face, :]
                    b_xy = boundary['nodes_xy'][i_face, :]
                    ax.plot([b_xy[0], b_xy[0] + n_xy[0] * scale],
                             [b_xy[1], b_xy[1] + n_xy[1] * scale], 'k-')
        ax.axis('equal')
        fig.savefig(f'{self.working_dir}/boundary.png')
        plt.close(fig)

    def __call__(self, x, case_name='simulation'):
        return self.simulate(x, case_name)

    def simulate(self, design, case_name, keep_files=False, generate_new_probes=False):

        # print(f'{case_name=} {design=}')

        if not self.keep_results and keep_files:
            print(f'WARNING! FlowFit.simulate is called with argument {keep_files=} but FlowFit is initialized with '
                  f'argument keep_results={self.keep_results}. This will result with deleting all results produced by '
                  f'this instance of FlowFit.')

        if np.sum(np.abs(design)) == 0.0:
            # print('{case_name=} zero design')
            return 1e6

        # Copy the template simulation
        case_dir = f'{self.working_dir}/{case_name}'
        if os.path.exists(case_dir):
            shutil.rmtree(case_dir)
        shutil.copytree(self.template_case, case_dir)
        for f in 'flow.png probes.npz design.txt'.split():
            if os.path.exists(f'{case_dir}/{f}'):
                os.remove(f'{case_dir}/{f}')
        if os.path.exists(f'{case_dir}/postProcessing'):
            shutil.rmtree(f'{case_dir}/postProcessing')
        if os.path.exists(f'{case_dir}/0'):
            shutil.rmtree(f'{case_dir}/0')
        os.mkdir(f'{case_dir}/0')

        # Save the design vector
        if keep_files:
            np.savetxt(f'{case_dir}/design.txt', design)

        # Get BC values or boundary cells
        bc_vtxy, bc_p = self.parametrize_bcs(design)
        # Write BC
        self.write_u(case_dir, bc_vtxy)
        self.write_scalar_bc(case_dir, 'p', bc_p)

        # Estimate velocity magnitude and turbulence variables for patch boundary cells
        patch_index = -1
        vm, k, eps, omega = {}, {}, {}, {}

        for b in self.boundary:
            if not b["type"] == "patch":
                continue
            patch_index += 1

            patch_vm = np.linalg.norm(bc_vtxy[b['name']], axis=1) * np.sqrt(2)
            vm[b['name']] = patch_vm
            patch_k, patch_eps, patch_omega = self.turbulence_variables_calculation(patch_vm)
            k[b['name']] = patch_k
            eps[b['name']] = patch_eps
            omega[b['name']] = patch_omega

        self.write_scalar_bc(case_dir, 'k', k)
        # self.write_scalar_bc(case_dir, 'epsilon', eps)
        self.write_scalar_bc(case_dir, 'omega', omega)
        self.write_scalar_bc(case_dir, 'nut', None)

        # Generate new probes
        if generate_new_probes:
            self.field_points, self.sample_points, self.ref_vxy = self.generate_new_probes(case_dir)
            # print(f'{self.sample_points=}')
        else:
            npz = np.load(f'{self.template_case}/probes.npz')
            self.field_points = npz['field_points']
            self.sample_points = npz['sample_points']
            self.ref_vxy = npz['sample_vxy']

        # Write sample probes
        self.write_sample(case_dir)

        simulation_success = self.run_openfoam(case_dir, keep_files=keep_files)

        # Run the simulations
        if simulation_success:

            # Read the results
            vxy, residuals = self.read_results(case_dir)

            if generate_new_probes:
                self.ref_vxy = vxy

            if generate_new_probes or keep_files:
                np.savez_compressed(f'{case_dir}/probes.npz',
                                    field_points=self.field_points,
                                    sample_points=self.sample_points,
                                    sample_vxy=self.ref_vxy)

            diff_vxy = vxy - self.ref_vxy
            dvm = np.sqrt(diff_vxy[:, 0] ** 2 + diff_vxy[:, 1] ** 2)

            vm = np.linalg.norm(vxy, axis=1)
            # print(f'Min and max velocity: {vm.shape=}, {vm.min()}, {vm.max()}')
            # objective = np.average(dvm)
            # print(f'{dvm.shape=}')
            objective = np.average(np.linalg.norm(diff_vxy, axis=1))

            fitness = objective
            for k, val in residuals.items():
                # print(k, v)
                if val >= self.ref_residuals[k]:
                    fitness += np.log(val / self.ref_residuals[k])

        else:
            fitness = 1e3

            # with open(f'{case_dir}/../iterations.txt', 'a') as f:
            #     f.write(f' x ')

        with open(f'{case_dir}/../evaluations.txt', 'a') as f:

            f.write(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} f={fitness}\n')

        """**************************"""

        # else:
        #     npz = np.load(f'{self.template_case}/probes.npz')
        #     field_points = npz['field_points']
        #     sample_points = npz['sample_points']
        #     ref_vxy = npz['sample_vxy']

        # Save sampling data
        # if keep_files:

        if keep_files:
            # Visualize the flow
            if simulation_success:
                self.visualize_flow(case_dir, case_name)

            # Save fitness
            np.savetxt(f'{case_dir}/fitness.txt', [fitness])

        else:
            # Delete simulation
            if os.path.exists(case_dir):
                shutil.rmtree(case_dir)

        # Calculate fitness
        if np.isinf(fitness) or np.isnan(fitness):
            # print(f'{case_name=} OF inf/nan objective')
            return 1e3

        # print(f'{case_name=} {fitness=}')
        return fitness

    def parametrize_bcs(self, design):
        i_patch = -1
        i_var = 0
        bc_vtxy = {}
        bc_p = {}
        for boundary in self.boundary:
            if boundary['type'] == 'patch':
                i_patch += 1
                closed = np.all(boundary['nodes_xy'][0, :] == boundary['nodes_xy'][-1, :])

                v_t = design[i_var:i_var + self.n_ctrl[i_patch]]
                p = design[int(np.sum(self.n_ctrl)) + i_var:int(np.sum(self.n_ctrl)) + i_var + self.n_ctrl[i_patch]]

                if closed:
                    s = np.linspace(0, np.sum(boundary['face_lengths']), self.n_ctrl[i_patch] + 1)

                    v_t = np.append(v_t, v_t[0])
                    vt_interp = sp.interpolate.CubicSpline(s, v_t, bc_type='periodic')

                    p = np.append(p, p[0])
                    p_interp = sp.interpolate.CubicSpline(s, p, bc_type='periodic')


                else:
                    s = np.linspace(0, np.sum(boundary['face_lengths']), self.n_ctrl[i_patch] + 2)

                    v_t = np.append(np.append(0, v_t), 0)
                    vt_interp = sp.interpolate.CubicSpline(s, v_t, bc_type='periodic')

                    p = np.append(np.append(0, p), 0)
                    p_interp = sp.interpolate.CubicSpline(s, p, bc_type='periodic')

                i_var += self.n_ctrl[i_patch]

                vt_mag = vt_interp(boundary['face_s'])
                bc_vtxy[boundary['name']] = np.array(
                    [tangnt_xy * vt for tangnt_xy, vt in zip(boundary['face_tangents'], vt_mag)])

                bc_p[boundary['name']] = p_interp(boundary['face_s'])

        return bc_vtxy, bc_p
        #     if boundary['type'] == 'wall':
        #         plt.plot(boundary['nodes_xy'][:, 0], boundary['nodes_xy'][:, 1], '.--')
        #     if boundary['type'] == 'patch':
        #         plt.plot(boundary['nodes_xy'][:, 0], boundary['nodes_xy'][:, 1], '.-')
        #         for i_face in range(boundary['face_normals'].shape[0]):
        #             n_xy = boundary['face_normals'][i_face, :]
        #             b_xy = boundary['nodes_xy'][i_face, :]
        #             scale = bc_p[i_face] * 100000
        #             print(scale)
        #             plt.plot([b_xy[0], b_xy[0] + n_xy[0] * scale],
        #                      [b_xy[1], b_xy[1] + n_xy[1] * scale], 'k-')
        # plt.axis('equal')
        # plt.savefig(f'{self.working_dir}/bc.png')
        # plt.close()

    def turbulence_variables_calculation(self, patch_vm):
        # velocity [m/s], turbulence_intensity [%], turbulence_length_scale [m]
        k = (3 / 2) * ((patch_vm * self.turbulence_variables['turbulence_intensity']) ** 2)
        eps = 0.09 * (k ** (3 / 2) / self.turbulence_variables['turbulence_length_scale'])
        omega = k ** (1 / 2) / self.turbulence_variables['turbulence_length_scale']

        return k, eps, omega
    def write_u(self, case_dir, bc_vtxy):

        with open(f'{case_dir}/0/U', 'w') as f:
            f.write(dedent(r"""
            /*--------------------------------*- C++ -*----------------------------------*\
            | =========                 |                                                 |
            | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
            |  \\    /   O peration     | Version:  2312                                  |
            |   \\  /    A nd           | Website:  www.openfoam.com                      |
            |    \\/     M anipulation  |                                                 |
            \*---------------------------------------------------------------------------*/
            FoamFile
            {
                version     2.0;
                format      ascii;
                class       volVectorField;
                object      U;
            }
            // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
            
            dimensions      [0 1 -1 0 0 0 0];
            
            internalField   uniform (0 0 0);
            
            boundaryField
            {
            """))

            for boundary in self.boundary:
                f.write(f'    {boundary["name"]}\n    {{\n')
                if boundary['type'] == 'empty':
                    f.write(f'        type empty;\n')

                elif boundary['type'] == 'patch':
                    f.write(f'        type pressureInletOutletVelocity;\n')

                    f.write(f'        tangentialVelocity nonuniform List<vector>\n')
                    f.write(f'        {boundary["nFaces"]}\n')
                    f.write(f'        (\n')
                    for vt in bc_vtxy[boundary['name']]:
                        f.write(f'            ({vt[0]} {vt[1]} 0)\n')
                    f.write(f'        );\n')

                    f.write(f'        value nonuniform List<vector>\n')
                    f.write(f'        {boundary["nFaces"]}\n')
                    f.write(f'        (\n')
                    for vt in bc_vtxy[boundary['name']]:
                        f.write(f'            ({vt[0]} {vt[1]} 0)\n')
                    f.write(f'        );\n')

                elif boundary['type'] == 'wall':
                    f.write(f'        type noSlip;\n')
                f.write('    }\n')
            f.write('}\n')

    def write_scalar_bc(self, case_dir, bc_type, bc_values):

        assert bc_type in 'p epsilon k omega nut'.split(), f'Unknown boundary type {bc_type}'

        with open(f'{case_dir}/0/{bc_type}', 'w') as f:
            f.write(dedent(r"""
            /*--------------------------------*- C++ -*----------------------------------*\
            | =========                 |                                                 |
            | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
            |  \\    /   O peration     | Version:  2312                                  |
            |   \\  /    A nd           | Website:  www.openfoam.com                      |
            |    \\/     M anipulation  |                                                 |
            \*---------------------------------------------------------------------------*/
            FoamFile
            {
                version     2.0;
                format      ascii;
                class       volScalarField;
            """)[1:])
            f.write(f'    object      {bc_type};')
            f.write(dedent(r"""
            }
            // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
            
            """))
            if bc_type == 'p':
                f.write('dimensions      [0 2 -2 0 0 0 0];\n')
                f.write('internalField   uniform 0;\n')
            elif bc_type == 'epsilon':
                f.write('dimensions      [0 2 -3 0 0 0 0];\n')
                f.write('internalField   uniform 1e-8;\n')
            elif bc_type == 'k':
                f.write('dimensions      [0 2 -2 0 0 0 0];\n')
                f.write('internalField   uniform 1.1039882806761836e-05;\n')
            elif bc_type == 'omega':
                f.write('dimensions      [0 0 -1 0 0 0 0];\n')
                f.write('internalField   uniform 6.645263819220975e-05;\n')
            elif bc_type == 'nut':
                f.write('dimensions      [0 2 -1 0 0 0 0];\n')
                f.write('internalField   uniform 0;\n')


            f.write(dedent(r"""

            boundaryField
            {
            """))

            for boundary in self.boundary:
                f.write(f'    {boundary["name"]}\n    {{\n')
                if boundary['type'] == 'empty':
                    f.write(f'        type empty;\n')

                elif boundary['type'] == 'patch':
                    if bc_type == 'p':
                        f.write(f'        type totalPressure;\n')
                        f.write(f'        p0 nonuniform List<scalar>\n')
                        f.write(f'        {boundary["nFaces"]}\n')
                        f.write(f'        (\n')
                        for p in bc_values[boundary['name']]:
                            f.write(f'            {p}\n')
                        f.write(f'        );\n')

                        f.write(f'        gamma 0.0;\n')
                    else:
                        f.write(f'        type fixedValue;\n')

                    if bc_type == 'nut':
                        f.write(f'        value $internalField;\n')
                    else:
                        f.write(f'        value nonuniform List<scalar>\n')
                        f.write(f'        {boundary["nFaces"]}\n')
                        f.write(f'        (\n')
                        for p in bc_values[boundary['name']]:
                            f.write(f'            {p}\n')
                        f.write(f'        );\n')

                elif boundary['type'] == 'wall':
                    if bc_type == 'p':
                        f.write(f'        type zeroGradient;\n')
                    elif bc_type == 'epsilon':
                        f.write(f'         type epsilonWallFunction;\n')
                        f.write(f'         value $internalField;\n')
                    elif bc_type == 'k':
                        f.write(f'         type kqRWallFunction;\n')
                        f.write(f'         value $internalField;\n')
                    elif bc_type == 'omega':
                        f.write(f'         type omegaWallFunction;\n')
                        f.write(f'         value $internalField;\n')
                    elif bc_type == 'nut':
                        f.write(f'         type nutkWallFunction;\n')
                        f.write(f'         value $internalField;\n')

                f.write('    }\n')
            f.write('}\n')

    def write_sample(self, case_dir, sample_points=None):

        if sample_points is None:
            sample_points = self.sample_points

        with open(f'{case_dir}/system/sample', 'w') as f:
            f.write(dedent(r"""
               /*--------------------------------*- C++ -*----------------------------------*\
               | =========                 |                                                 |
               | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
               |  \\    /   O peration     | Version:  2312                                  |
               |   \\  /    A nd           | Website:  www.openfoam.com                      |
               |    \\/     M anipulation  |                                                 |
               \*---------------------------------------------------------------------------*/
               FoamFile
               {
                   version     2.0;
                   format      ascii;
                   class       dictionary;
                   object      sample;
               }
               // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
               
               type sets;
               libs (sampling);
               interpolationScheme cellPointFace;
               setFormat raw;
               
               fields ( U );
               
               sets
               {
                   samples
                   {
                       type cloud;
                       axis xyz; // write x, y, z co-ordinates
                       points
                       (
               """))

            for i in range(sample_points.shape[0]):
                f.write(f'            ({sample_points[i, 0]} {sample_points[i, 1]} -0.5)\n')

            f.write('        );\n')
            f.write('    }\n')
            f.write('}\n')

    def run_openfoam(self, case_dir, keep_files):
        with open(f'{case_dir}/run.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('#openfoam2312\n')
            f.write(f'export PATH=$PATH:{indagobench._local_paths.openmpi_path}\n')
            f.write(f'source {indagobench._local_paths.openfoam_bashrc}\n')
            if keep_files:
                f.write('simpleFoam > simpleFoam.log\n')
            else:
                f.write('simpleFoam\n')

            if keep_files:
                f.write('postProcess -func sample -latestTime > postProcess.log\n')
            else:
                f.write('postProcess -func sample -latestTime\n')

        p = subprocess.Popen(['bash', 'run.sh'],
                             cwd=case_dir,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        p.kill()

        if keep_files:
            with open(f'{case_dir}/stdouterr.txt', 'w') as f:
                f.write(f'{stdout=}\n')
                f.write(f'{stderr=}\n')
                f.write(f'{len(stderr)=}')

        return len(stderr) == 0

    def read_results(self, case_dir):


        # Reading the residuals
        residuals_history = np.loadtxt(f'{case_dir}/postProcessing/residuals/0/solverInfo.dat',
                                       usecols=[0, 3, 6, 11],  # Ux, Uy, p
                                       # usecols=[0, 3, 6, 11, 16, 21],  #
                                       )
        # fig, ax = plt.subplots()
        residuals = {}
        for i, var in enumerate('Ux Uy p'.split()):
            residuals[var] = residuals_history[-1, i + 1]
            # ax.plot(residuals_history[:, i + 1], label=f'{var} residual: {residuals[var]:.3e}')

        # ax.legend()
        # ax.set_yscale('log')
        # ax.set_xlabel('Iterations')
        # ax.grid(lw=0.2, ls='--')
        # plt.savefig(f'{case_dir}/residuals.png')
        # plt.close(fig)
        # print(residuals)

        # Read samples
        vxy = np.loadtxt(f'{case_dir}/postProcessing/sample/{int(residuals_history[-1, 0])}/samples_U.xy',
                               usecols=[3, 4])


        # with open(f'{case_dir}/../iterations.txt', 'a') as f:
        #     f.write(f'{residuals_history[-1, 0]:.0f} ')

        return vxy, residuals

    def generate_new_probes(self, case_dir):

        # Reading the mesh results
        pathlib.Path(f'{case_dir}/case.foam').touch()
        reader = pv.OpenFOAMReader(f'{case_dir}/case.foam')
        # print(f'Available Time Values: {reader.time_values}')

        reader.set_active_time_value(reader.time_values[-1])
        mesh = reader.read()
        internal_mesh = mesh["internalMesh"]

        domain_w = mesh.bounds[1] - mesh.bounds[0]
        domain_h = mesh.bounds[3] - mesh.bounds[2]
        plot_w = 1500
        plot_h = int(plot_w / domain_w * domain_h)

        n = int(plot_h * 1.6)
        n_samples = 25
        sample_points = np.full([0, 3], np.nan)
        while sample_points.shape[0] < n_samples:
            rnd_points = np.random.uniform(mesh.bounds[0::2], mesh.bounds[1::2])
            if internal_mesh.find_containing_cell(rnd_points) >= 0:
                sample_points = np.append(sample_points, [rnd_points], axis=0)
        # print(f'{sample_points.shape=}')
        field_points = np.random.uniform(0, 1, [n, 3])
        # sample_points = np.random.uniform(0, 1, [15, 3])
        for i in range(3):
            field_points[:, i] = mesh.bounds[i * 2] + field_points[:, i] * (mesh.bounds[i * 2 + 1] - mesh.bounds[i * 2])
            # sample_points[:, i] = mesh.bounds[i * 2] + sample_points[:, i] * (mesh.bounds[i * 2 + 1] - mesh.bounds[i * 2])

        _sample_points = pv.PolyData(sample_points)
        sample_probes = _sample_points.sample(internal_mesh)
        sample_vxy = np.array(sample_probes.point_data["U"][:, :2])
        ref_vxy = sample_vxy
        # print(f'{sample_vxy=}')

        return field_points, sample_points, sample_vxy

    def visualize_flow(self, case_dir, case_name):

        # npz = np.load(f'{self.template_case}/probes.npz')
        # field_points = npz['field_points']
        # sample_points = npz['sample_points']
        # ref_vxy = npz['sample_vxy']

        field_points = self.field_points
        sample_points = self.sample_points
        ref_vxy =self.ref_vxy
        # print(sample_points)

        # Reading the mesh results
        pathlib.Path(f'{case_dir}/case.foam').touch()
        reader = pv.OpenFOAMReader(f'{case_dir}/case.foam')
        # print(f'Available Time Values: {reader.time_values}')

        reader.set_active_time_value(reader.time_values[-1])
        mesh = reader.read()

        internal_mesh = mesh["internalMesh"]  # or internal_mesh = mesh[0]
        mesh_boundaries = mesh['boundary']

        domain_w = mesh.bounds[1] - mesh.bounds[0]
        domain_h = mesh.bounds[3] - mesh.bounds[2]
        plot_w = 1500
        plot_h = int(plot_w / domain_w * domain_h)
        dz = domain_w * 1e-3
        # print(f'Plot canvas size: {plot_w} x {plot_h}')

        # Global pyvista settings
        pv.set_plot_theme("document")
        # pv.set_plot_theme('default')
        pv.global_theme.font.size = 20
        pv.global_theme.font.title_size = 25
        pv.global_theme.font.label_size = 20
        pl = pv.Plotter(off_screen=True, window_size=[plot_w, plot_h])
        pl.parallel_projection = True

        field_points = pv.PolyData(field_points)
        sample_points = pv.PolyData(sample_points)
        field_probes = field_points.sample(internal_mesh)
        sample_probes = sample_points.sample(internal_mesh)

        ref_vxyz = np.full([ref_vxy.shape[0], 3], 0.0)
        ref_vxyz[:, :2] = ref_vxy
        sample_probes.point_data['U'] = ref_vxyz
        # print(f'{ref_vxy.shape=}')
        # print(f'{sample_probes.point_data=}')
        # print(f'{sample_probes.cell_data=}')
        field_probes.set_active_vectors('U')
        sample_probes.set_active_vectors('U')

        # Plotting velocity magnitude contour
        pl.add_mesh(internal_mesh.translate((0, 0, -np.max(internal_mesh.points[:, 2])), inplace=False),
                    scalars="U",
                    cmap="Blues",
                    # cmap="YlOrBr",
                    # cmap=mpl.colors.LinearSegmentedColormap.from_list("", ["#FEE8B0", "#9CA777", "#7C9070"]),
                    clim=(0, self.vis_params['v_max']),
                    show_scalar_bar=False)
        sbar = pl.add_scalar_bar('Velocity [m/s]\n',
                                 position_x=self.vis_params['cbar_x'],
                                 position_y=self.vis_params['cbar_y'],
                                 height=self.vis_params['cbar_h'],
                                 width=self.vis_params['cbar_w'],
                                 interactive=False,
                                 vertical=False,
                                 n_labels=self.vis_params['cbar_n'],
                                 fmt='%.2f',
                                 outline=False)
        sbar.GetLabelTextProperty().SetJustificationToCentered()

        # Plotting vector fields (glyph arrows)
        field_arrows = field_probes.glyph(
            scale='U',  # list(np.linalg.norm(result['U'], axis=1) + 0.01),
            orient='U',
            factor=domain_w * 2e-2 / self.vis_params['v_max'],
            # tolerance=1e-3,
            geom=pv.Arrow(tip_length=1, tip_radius=0.35).translate([-1/3, 0, 0]).scale([0.5, 0.5, 0.5])
        )
        pl.add_mesh(field_arrows.translate((0, 0, dz - 0.5 * (np.min(field_arrows.points[:, 2]) + np.max(field_arrows.points[:, 2]))),
                                     inplace=False),
                    color="dimgray", show_scalar_bar=False, lighting=False)

        sample_arrows = sample_probes.glyph(
            scale='U',  # list(np.linalg.norm(result['U'], axis=1) + 0.01),
            orient='U',
            factor=domain_w * 5e-2 / self.vis_params['v_max'],
            # tolerance=1e-3,
            geom=pv.Arrow(tip_length=1, tip_radius=0.35).translate([-1/3, 0, 0]).scale([0.5, 0.5, 0.5])
        )
        pl.add_mesh(sample_arrows.translate((0, 0, dz*20),
                                     inplace=False),
                    color="red", show_scalar_bar=False, lighting=False)

        for v in sample_probes.points:
            # print(v)
            dx = np.array([0.05 * domain_w, 0, 0])
            dy = np.array([0, 0.05 * domain_w, 0])
            dzz = np.array([0, 0, 20 * dz])
            hline = pv.Line(v - dx + dzz, v + dx + dzz)
            vline = pv.Line(v - dy + dzz, v + dy + dzz)
            pl.add_mesh(hline, color='darkred', line_width=1)
            pl.add_mesh(vline, color='darkred', line_width=1)

        # Plotting streamlines
        streamlines = internal_mesh.streamlines_from_source(field_probes,
                                                            max_time=domain_w / 10,
                                                            integration_direction="backward",
                                                            initial_step_length=1e-3,
                                                            min_step_length=1e-6,
                                                            max_error=1e-9 * domain_w)

        if streamlines.GetNumberOfCells() != 0:
            pl.add_mesh(streamlines.tube(radius=domain_w * 3e-4). \
                        translate(
                (0, 0, dz - 0.5 * (np.min(streamlines.points[:, 2]) + np.max(streamlines.points[:, 2]))),
                inplace=False),
                        lighting=False,
                        color='DimGray',
                        )

        for b in self.boundary:
            if b['type'] == 'wall':
                pl.add_mesh(mesh_boundaries[b['name']],  # .translate((0, 0, 10 * dz)),
                            scalars=None,
                            color='black',
                            line_width=20,
                            style="wireframe",
                            # show_edges=True,
                            split_sharp_edges=True,
                            show_scalar_bar=False,
                            )

            if b['type'] == 'patch':
                pl.add_mesh(mesh_boundaries[b['name']],  # .translate((0, 0, 10 * dz)),
                            scalars=None,
                            color='limegreen',
                            line_width=20,
                            style="wireframe",
                            # show_edges=True,
                            split_sharp_edges=True,
                            show_scalar_bar=False,
                            )

        text_prop = pv.TextProperty()
        text_prop.bold = True
        pl.add_text(case_name, #f'FF_{self.problem}_{self.dimensions:d}D',
            position='upper_left',
            color='black',
            shadow=True,
            font_size=24,
            font='times',
        ).prop.bold=True
        pl.view_xy()
        # pl.camera.zoom(1.5)
        pl.camera.tight(padding=0.05)
        pl.camera.position = pl.camera.position[:2] + (domain_w + domain_h,)
        pl.enable_anti_aliasing('fxaa')
        pl.show(screenshot=f'{case_dir}/flow.png')
        pl.close()


FF_problems_dict_list = []
for problem_dict in FlowFit.problem_dicts():
    problem = {'label': f'FF_{problem_dict["case"]}_{problem_dict["dimensions"]}D',
              #'label': f'FlowFit_{problem_dict["case"]}_{problem_dict["dimensions"]}D',
              'class': FlowFit,
              'case': problem_dict["case"],
              'dimensions': problem_dict["dimensions"],
              'max_evaluations': problem_dict["max_evaluations"],
              'max_runs': 1000,
              }
    FF_problems_dict_list.append(problem)
    
if __name__ == '__main__':

    """Testing FlowFit simulation"""
    # import time
    # flow_fit = FlowFit('open1', 12, keep_results=True)
    # # design0 = np.loadtxt(f'{flow_fit.working_dir}/ref/design.txt')
    # design0 = np.loadtxt(f'{flow_fit.template_case}/design.txt')

    # design0 = np.random.uniform(flow_fit.lb, flow_fit.ub)
    # f = flow_fit.simulate(design0, 'test', keep_files=True, generate_new_probes=True)

    # for i in range(20):
    #     start = time.time()
    #     design = design0 + 0.0005 * np.random.uniform(flow_fit.lb, flow_fit.ub)
    #     design = np.clip(design, flow_fit.lb, flow_fit.ub)
    #     # design = np.random.uniform(flow_fit.lb, flow_fit.ub)
    #
    #     f = flow_fit.simulate(design,
    #                           case_name=f'random{i:03d}',
    #                           keep_files=True,
    #                           generate_new_probes=True,
    #                           )
    #     end = time.time()
    #     print(f'case_name=random{i:03e}, {f=}, t={end - start:.1f}')
    #     shutil.copy(f'{flow_fit.working_dir}/random{i:03d}/flow.png',
    #                 f'{flow_fit.working_dir}/flow_random{i:03d}.png')

    """Testing FlowFit optimization"""
    # import indago
    # flow_fit = FlowFit('open1', 16, keep_results=True)
    # optimizer = indago.PSO()
    # optimizer.evaluation_function = flow_fit
    # optimizer.processes = 10
    # optimizer.monitoring = 'dashboard'
    # optimizer.forward_unique_str = True
    # optimizer.max_evaluations = 2_000
    # optimizer.convergence_log_file = f'{flow_fit.working_dir}/convergence.txt'
    # best = optimizer.optimize()
    # optimizer.plot_history(f'{flow_fit.working_dir}/convergence.png')
    # flow_fit.simulate(best.X, 'best', keep_files=True)

    #print(f'{sys.argv=}')
    #print(f'Available arguments: 10D, 20D, 50D, all (or no arguments provided)')

    """FlowFit indagobench standard test"""
    import indagobench
    standard_test = indagobench.StandardTest(indagobench._local_paths.indagobench25_results_dir,
                                             # convergence_window=10, eps_max=1, runs_min=100, batch_size=100, processes=10,
                                             # convergence_window=50, eps_max=0.01, runs_min=100, batch_size=10,
                                             processes=10
                                             )
    standard_test.problems = FF_problems_dict_list
    standard_test.optimizers = indagobench.indagobench25_optimizers

    # if len(sys.argv) == 1: # No arguments
    #     print(f'No arguments provided, running all avaliable functions ({len(FF_problems_dict_list)})')
    #     standard_test.problems = FF_problems_dict_list
    # else:
    #     print(f'{len(sys.argv) - 1} arguments provided')
    #     standard_test.problems = []
    #     for problem in FF_problems_dict_list:
    #         slbl = problem['case'] + '_' + str(problem['dimensions']) + 'D' # Short label
    #         if problem['label'] in sys.argv[1:] or slbl in sys.argv[1:]:
    #             standard_test.problems.append(problem)
    #             print(f'Matching function found: {problem["label"]}')
    #     print(f'Total benchmark functions: {len(standard_test.problems)}')
    # standard_test.run_all()


    """Results postprocessing and visualization"""
    class_results_dir = f'{indagobench._local_paths.indagobench25_results_dir}/FF/'
    if not os.path.exists(class_results_dir):
        os.mkdir(class_results_dir)

    # Manuscript figures
    for problem_dict in [indagobench.get_problem_dict('FF_bay1_10D')]:
        fr = indagobench.ProblemResults(problem_dict)
        fr.optimizers = ['NM', 'LSHADE', 'CMAES']
        fr.make_full_convergence_figure(f'{class_results_dir}/short_conv_{problem_dict["label"]}.png',
                                        header_plots=False)

    # Make referent flow images
    for problem_dict in [FF_problems_dict_list[1], FF_problems_dict_list[2], FF_problems_dict_list[6]]:
        ff = FlowFit(problem_dict['case'], dimensions=problem_dict["dimensions"])
        results = indagobench.ProblemResults(problem_dict)

        case_name = f'{problem_dict["label"]}_referent'
        x_best = np.loadtxt(f'{ff.template_case}/design.txt')
        ff.simulate(x_best, case_name, keep_files=True)
        shutil.copyfile(f'{ff.working_dir}/{case_name}/flow.png',
                        f'{class_results_dir}/{case_name}.png')

    for problem_dict in standard_test.problems:
        ff = FlowFit(problem_dict['case'], dimensions=problem_dict["dimensions"])
        results = indagobench.ProblemResults(problem_dict)

        case_name = f'{problem_dict["label"]}_best'
        x_best = results.results['_x_min']
        ff.simulate(x_best, case_name, keep_files=True)
        shutil.copyfile(f'{ff.working_dir}/{case_name}/flow.png',
                        f'{class_results_dir}/{case_name}.png')

        for optimizer in standard_test.optimizers:
            f_best = results.results['f_best ' + optimizer['label']]
            i_median = np.argmin(np.abs(np.median(f_best) - f_best))
            x_median = results.results[f'x_best ' + optimizer['label']][i_median, :]
            case_name = f'{problem_dict["label"]}_{optimizer["label"].replace(" ", "-")}_median'
            ff.simulate(x_median, case_name, keep_files=True)
            shutil.copyfile(f'{ff.working_dir}/{case_name}/flow.png',
                            f'{class_results_dir}/{case_name}.png')

