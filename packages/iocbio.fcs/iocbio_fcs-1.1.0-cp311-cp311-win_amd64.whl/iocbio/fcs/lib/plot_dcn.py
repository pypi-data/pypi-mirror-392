import matplotlib.pyplot as plt
import numpy as np

from iocbio.fcs.lib.acf import ACF
from iocbio.fcs.lib.const import (
    GROUP_ACF,
    RECTANGULAR,
    UNIT_CONCENTRATION,
    UNIT_DIFF,
    DCN_DIFFUSION,
    DCN_CONCENTRATION,
)
from iocbio.fcs.lib.plot_signal import plot_signals
from iocbio.fcs.lib.utils import get_output_fname, split_indx


def print_stats(data, label):
    print(f"\n{label}:\nmin:    {min(data):.2f}\nmax:    {max(data):.2f}")
    print(f"mean:   {np.mean(data):.2f}\nmedian: {np.median(data):.2f}\nstd:    {np.std(data):.2f}")


def plot_dots(subplot, x, y, ylabel, xlabel="Dataset Index", color="blue", linestyle="."):
    subplot.plot(x, y, linestyle, color=color, markersize=3)
    subplot.set_xlabel(xlabel, fontweight="bold", fontsize=12)
    subplot.set_ylabel(ylabel, fontweight="bold", fontsize=12)
    subplot.tick_params(axis="both", labelsize=10)


def plot_diffusion_vs_concentration(args, input_file, acf_file):
    fig = plt.figure(figsize=(RECTANGULAR[0], RECTANGULAR[1] * 3 if args.measurement_file else 2))
    c_label = f"Concentration [{UNIT_CONCENTRATION}]"
    dc_label = f"Diffusion [{UNIT_DIFF}]"
    sector_acf_dict = ACF.load(input_file, args, individual_acf=True)
    for acf_dict in sector_acf_dict.values():
        concentration, diffusion = [], []
        for key in acf_dict:
            data = acf_file[f"/{GROUP_ACF}/" + key]
            concentration.append(data.attrs[DCN_CONCENTRATION])
            diffusion.append(data.attrs[DCN_DIFFUSION])

        selected_range = args.filter_range
        n_data_dcn = len(diffusion)
        if not selected_range:
            print(f"Number of images/traces: {n_data_dcn}")
        print_stats(concentration, "concentration")
        print_stats(diffusion, "diffusion")
        print("\n==========================================")
        print("Concentration mean - (2 x std): %.2f" % (np.mean(concentration) - 2 * np.std(concentration)))
        print("==========================================\n")
        rows = 4 if args.measurement_file else 3

        # Plot diffusion vs concentration
        ax1 = fig.add_subplot(rows, 1, 1)
        plot_dots(subplot=ax1, x=concentration, y=diffusion, xlabel=c_label, ylabel=dc_label)

        # Plot diffusion vs images
        ax2 = fig.add_subplot(rows, 1, 2)
        selected_indexes = [0]
        if selected_range:
            selected_indexes = split_indx(selected_range)

        start = selected_indexes[0]
        end = n_data_dcn + start
        x_axis = range(start, end)
        plot_dots(subplot=ax2, x=x_axis, y=diffusion, ylabel=dc_label, color="red")

        # Plot concentration vs images
        ax3 = fig.add_subplot(rows, 1, 3, sharex=ax2)
        plot_dots(subplot=ax3, x=x_axis, y=concentration, ylabel=c_label, color="maroon")

        if args.measurement_file:
            filter_range = acf_dict[key].fr
            mean_values = plot_signals(args, args.measurement_file, dcn_fr=filter_range)
            print(f"Selected range used in calc-acf is {np.array(filter_range)} -> {filter_range[1]-filter_range[0]}")

            # Plot intensity vs images
            ax4 = fig.add_subplot(rows, 1, 4, sharex=ax2)
            plot_dots(subplot=ax4, x=x_axis, y=mean_values, ylabel="Average Intensity", color="k", linestyle="-")

        fig_name = "_DCN"
        if args.pdf:
            plt.savefig(
                get_output_fname(input_file, args.output, fig_name, ".pdf"),
                pad_inches=0,
                bbox_inches="tight",
            )
