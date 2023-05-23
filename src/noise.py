
import random
import numpy as np
import scipy
from matplotlib import pyplot as plt


def value_noise_lerp(my_len, n_octaves=6):
    powers_of_2 = tuple(pow(2, i) for i in range(n_octaves))
    xs = [np.arange(0, my_len, i) for i in powers_of_2]
    random_ys = [[random.uniform(0, power_of_2) for _ in range(0, my_len, power_of_2)] for power_of_2 in powers_of_2]
    x = np.arange(0, my_len, 0.1)
    lerp_ys = [np.interp(x, xp, random_y) for xp, random_y in zip(xs, random_ys)]

    fig, axs = plt.subplots(n_octaves + 1, 1, sharex="all", sharey="all")
    fig.suptitle(f"Value noise, CubicSpline, {n_octaves} octaves")
    for ax, lerp_y in zip(axs, lerp_ys):
        ax.plot(x, lerp_y)

    ans = sum(x)
    axs[-1].plot(x, ans)
    plt.show()

    plt.plot(x, ans)
    plt.show()
    return ans


def make_cubic_spline_octave(length, interval, height):
    x1 = np.arange(0, length, interval)
    y1 = [random.uniform(0, height) for _ in x1]
    return scipy.interpolate.CubicSpline(x1, y1, bc_type="natural")


def value_noise_cubic_spline(my_len, n_octaves: int = 6, plot: bool = False, return_ans: bool = True):
    powers_of_2 = tuple(pow(2, i) for i in range(n_octaves))
    octaves = [make_cubic_spline_octave(my_len, powers_of_2[i], powers_of_2[i]) for i in range(n_octaves)]

    xs = np.arange(0, my_len, 0.5)
    ys = [octave(xs) for octave in octaves]
    ans = sum(ys)

    if plot:
        fig, axs = plt.subplots(n_octaves+1, 1, sharex="all", sharey="all")
        fig.suptitle(f"Value noise, CubicSpline, {n_octaves} octaves")
        for ax, y in zip(axs, ys):
            ax.plot(xs, y)
        axs[-1].plot(xs, ans)
        plt.show()

        plt.plot(xs, ans, )
        d = np.zeros_like(ans)
        plt.gca().set_aspect("equal")
        plt.gca().fill_between(xs, ans, where=ans >= d, interpolate=True)
        plt.show()

    if return_ans:
        return ans


def two():
    my_len = 256
    noise_list1 = value_noise_cubic_spline(my_len)
    noise_list2 = value_noise_cubic_spline(my_len)
    plt.plot(noise_list1)
    plt.plot(noise_list2)
    plt.gca().set_aspect("equal")
    plt.show()


def noise_list_to_file():
    my_len = 256
    n_octaves = 6
    show = True
    return_ans = True
    noise_list = value_noise_cubic_spline(my_len, n_octaves, show, return_ans)
    # list of lists still needing transposing
    level_map_matrix = []
    for width, gras in enumerate(noise_list):
        new_list = []
        for height in range(64):
            gras = round(gras)
            if height == gras:
                new_list.append("G")
            elif height > gras:
                new_list.append("D")
            else:
                new_list.append("A")
        level_map_matrix.append(new_list)
    # list of strings
    str_list = []
    for i in range(len(level_map_matrix[0])):
        new_str = ""
        for j in range(len(level_map_matrix)):
            new_str += level_map_matrix[j][i]
        str_list.append(new_str)
    # changing dirt with air access to grass
    for i in range(len(str_list)):
        str_list[i] = str_list[i].replace("AD", "AG").replace("DA", "GA")
    # file
    with open("level_map_2.txt", 'w') as level_map_file:
        for i in range(len(level_map_matrix[0])):
            for j in range(len(level_map_matrix)):
                level_map_file.write(level_map_matrix[j][i])
            level_map_file.write("\n")


value_noise_cubic_spline(256, 6, True, False)
# two()
# noise_list_to_file()
