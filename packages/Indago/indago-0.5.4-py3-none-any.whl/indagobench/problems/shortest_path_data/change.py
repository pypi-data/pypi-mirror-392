
if __name__ == '__main__':
    import numpy as np

    filename = 'shortest_path_cases.npz'
    npz = np.load(filename)

    d = {}
    for f in npz.files:

        # if not f == 'zigzag3':
        #     continue
        M = npz[f]

        # if f == 'zigzag3':
        #     M[0, -3:] = [125, 250, 375]
        #     M[1, -3:] = [35, -45, 40]
        #     M[2, -3:] = [40, 50, 45]

        print('\n' + f)
        print(M)

        d[f] = M

    np.savez_compressed('_' + filename, **d)