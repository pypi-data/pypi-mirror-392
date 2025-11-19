import argparse
import matplotlib.pyplot as plt
import numpy as np
from ultranest.plot import PredictionBand

from iocbio.fcs.lib.const import (
    RECTANGULAR,
    DELTA_X,
    DEGREE,
    RES_TXT,
    ULTRANEST,
    GLS,
    WLS,
    OLS,
    ACF_COV,
    ACF_EXP,
    ACF_MODEL,
    ACF_MEAN,
    ACF_MEAN_BEFORE_CUT,
    ACF_STD,
    DELTA_X_LOCAL,
    DELTA_T,
    LINES,
    ANGLE,
    ACF_KEY,
    LINE_TIME,
    TAU,
    ACF_LABEL,
    DELTA_X_LABEL,
    G_DELTA_X_LABEL,
    G_TAU_LABEL,
    TAU_LABEL,
)
from iocbio.fcs.lib.plot_acf_vs_angle import plot_acf_vs_angle
from iocbio.fcs.lib.plot_bayes import add_prediction_band, plot_samples
from iocbio.fcs.lib.plot_cov import plot_2d_cov
from iocbio.fcs.lib.residual import Residual, plot_residuals
from iocbio.fcs.lib.utils import error_structure, get_output_fname, output_suffix


class Plot:
    # static
    @staticmethod
    def config_parser(parser):
        # Plotting options
        parser.add_argument("-t", "--time", action="store_true", help="Plot `ACF` versus `delta t`")
        parser.add_argument("--log", action="store_true", help="Plot `ACF` in logarithmic scale")
        parser.add_argument(
            "--show",
            action=argparse.BooleanOptionalAction,
            default=True,
            help="The fit-plot apps show the results figure (enabled by default); "
            "use `--no-show` to prevent showing the figures",
        )
        parser.add_argument(
            "-fullkey",
            "--show-full-acf-key",
            action="store_true",
            help="Show full ACF keys (line time, angle, pixel size, and pixel time)",
        )
        parser.add_argument(
            "-errbar",
            "--error-bar",
            action="store_true",
            help="Display error bars for ACF data points.",
        )

        # Plot ACF VS scanning angles
        parser.add_argument(
            "-paa",
            "--plot-acf-angle",
            type=int,
            default=0,
            help="Plot ACF VS scanning angles. Determine number of ACF lines",
        )
        parser.add_argument(
            "-dx",
            "--delta-x-list",
            nargs=3,
            type=float,
            default=[0.1, 0.25, 0.5],
            help="3 values of delta_x for plotting ACF VS scanning angles",
        )

        # Calculate and plot residuals
        parser.add_argument(
            "-r",
            "--residuals",
            action="store_true",
            help="Calculate and plot residuals for the selected number of fitted ACF lines",
        )

        # Plot 2D ACF heatmap
        parser.add_argument("-acf", "--acf-2D", action="store_true", help="Plot 2D ACF heatmap")

        # Plot diffusion VS concentration
        parser.add_argument(
            "--dcn",
            action="store_true",
            help="Plot diffusion VS concentration for each image/trace in RICS/FCS experiment",
        )
        parser.add_argument(
            "-mf",
            "--measurement-file",
            default=None,
            help="The name of RICS/FCS file. This option adds the average intensity of the RICS image "
            "or FCS trace as fourth row in the DCN plot, allowing comparison of intensity with "
            "corresponding diffusion and concentration values",
        )

        # Normalize covariance
        parser.add_argument(
            "-norm",
            "--normalized-covariance",
            action="store_true",
            help="Normalize the covariance matrix for plotting.",
        )

        # Output parameters
        parser.add_argument("-o", "--output", default=None, help="Prefix for output files")
        parser.add_argument("--pdf", action="store_true", help="Save figures as `PDF` file")
        parser.add_argument("--svg", action="store_true", help="Save figures as `SVG` file (FCS trace)")

        # Save results
        parser.add_argument(
            "-sr",
            "--save-results",
            action=argparse.BooleanOptionalAction,
            default=True,
            help="Save results to an HDF5. Use '--no-save-results' to disable saving.",
        )
        parser.add_argument("--excel", action="store_true", help="Save result as `xlsx` file")
        parser.add_argument("--csv", action="store_true", help="Save result as `csv` file")

    def __init__(
        self,
        args,  # Arguments
        sector_acf_dict: dict,  # Dictionary from ACF class: sector coordinates -> ACF data
        rlc=None,  # Results List Class
        sector_key: str = None,  # Sector coordinate key (typically from -0.5 to 0.5)
        file_name: str = None,  # Name of input file
    ):
        self.args = args
        self.sector_acf_dict = sector_acf_dict
        self.rlc = rlc
        self.sector_key = sector_key
        self.acf_2D = True if self.args.acf_2D else False  # if True, plot 2D ACF heatmap
        self.f_name = file_name
        self.model = True if rlc else False
        self.ultranest = False
        self.paa = 0  # plot ACF VS scanning angles (0: no plot)
        self.colors = ["r", "b", "olive", "m", "c", "y", "g"]
        self.exp_marker = ["o", "v", "s", "*", "H"]
        self.err_structure = error_structure(args)  # error structure handling
        self.fig_properties()
        self.generate_figure()

    """ ------------ Data Processing ------------ """

    def fig_properties(self):
        first_sector = self.sector_acf_dict[next(iter(self.sector_acf_dict))]
        first_acf = first_sector[next(iter(first_sector))]
        self.n_excl = first_acf.exclude  # number of excluded ACF data
        self.full = first_acf.full  # full x-axis
        if self.model:
            self.get_fit_data()
        self.collect_experimental_data()
        self.sorted_acf_key_list = sorted(list(self.sector_acf_dict[self.sector_key].keys()))
        self.n_key = len(self.sorted_acf_key_list)  # number of conditions (speeds and angles)
        self.fig_size = tuple(np.array(RECTANGULAR) * (self.n_key if self.n_key < 3 else 2))

        # Y-axis limits
        acf_scale = (self.max_acf - self.min_acf) / 10
        self.min_y_axis = -(abs(self.min_acf) + acf_scale)
        self.max_y_axis = self.max_acf + acf_scale

        # Error bar
        self.error_bar = self.args.error_bar
        if self.error_bar:
            if self.err_structure == OLS:
                print(
                    "\nError bars are only available for GLS and WLS fitting methods. "
                    "If multiple datasets are available, use '-err' for WLS or '-cov' for GLS fitting."
                )
            self.max_y_axis += self.max_y_axis / 10
            self.min_y_axis += self.min_y_axis

    # Collecting data for plotting
    def collect_experimental_data(self):
        plot_data_dict = dict()  # a dictionary storing plotting data in each sector
        min_acf, max_acf = [], []

        for acf_key, acf_values in self.sector_acf_dict[self.sector_key].items():
            # Parameters needed for plotting
            plot_obj, acf_cov = acf_values.data_for_plot(), None

            # Plot covariance matrix (used for fitting)
            if self.err_structure == GLS:
                fit_obj = acf_values.data_for_fit()
                acf_cov = fit_obj.cov
                lag_time = fit_obj.dt
                if not self.model:
                    plot_2d_cov(f_name=self.f_name, args=self.args, acf_cov=acf_cov, lag_time=lag_time)
            angle, line_time = acf_values.angle, acf_values.line_time
            min_acf.append(np.min(plot_obj.acf))
            max_acf.append(np.max(plot_obj.acf))

            plot_data_dict[acf_key] = {
                ACF_MEAN: plot_obj.acf,
                ACF_MEAN_BEFORE_CUT: acf_values.acf_mean_before_cut,
                ACF_STD: plot_obj.std,
                DELTA_X_LOCAL: plot_obj.dx_local,
                DELTA_T: plot_obj.dt,
                LINES: plot_obj.line,
                ANGLE: angle,
                LINE_TIME: line_time,
                ACF_KEY: acf_key,
                ACF_COV: acf_cov,
            }
        lines = plot_data_dict[acf_key][LINES]
        self.n_line = int(lines.max() - lines.min()) + 1
        self.min_acf, self.max_acf = min(min_acf), max(max_acf)
        self.experimental_data_dict = plot_data_dict

    def get_fit_data(self):
        self.f_name = self.rlc.f_name
        if not self.sector_key:
            self.sector_key = self.rlc.sectors[0]

        result_cls = self.rlc.get_result(self.sector_key)
        self.parameters_dict = result_cls.prd  # parameter results dictionary (prd)
        self.acf_key_indexes = result_cls.akid  # ACF keys indexes dictionary (akid)
        self.acf = np.array(result_cls.acf)
        self.acf_model = result_cls.acf_model
        self.residuals = result_cls.resid
        self.line_indexes = np.array(result_cls.line_indx)
        fitfile = self.rlc.acf_file_path

        if self.rlc.fit_procedure == ULTRANEST:
            self.ultranest = True
        if fitfile:
            [print(self.parameters_dict[param][RES_TXT]) for param in self.parameters_dict.keys()]
            print()
        if self.ultranest and not fitfile:
            self.plot_ultranest_features(result_cls)

        self.paa = self.args.plot_acf_angle  # plot ACF VS scanning angles. Determine number of ACF lines
        if self.paa > 0:
            self.dxl = self.args.delta_x_list  # list of 3 values of delta_x for plotting ACF VS scanning angles
            if any(v < 0 for v in self.dxl):
                raise ValueError("delta x values must be positive.")
            self.ppa_dict, self.angle_list, self.line_time_list = {}, [], []

    """ ------------ Generate Figure ------------ """

    def generate_figure(self):
        args = self.args
        self.has_residuals = args.residuals
        self.resid_obj = Residual(error_structure=self.err_structure)
        self.is_log_scale, self.use_time = args.log, args.time
        use_pdf, output_base = args.pdf, args.output

        xlabel = TAU_LABEL if self.use_time else DELTA_X_LABEL
        y_label = G_TAU_LABEL if self.use_time else G_DELTA_X_LABEL
        fig_name_base = ACF_LABEL if self.acf_2D else f"{ACF_LABEL}-VS-{TAU if self.use_time else DELTA_X}"
        fig_name = f"{fig_name_base}_Log-scale" if self.is_log_scale else fig_name_base
        xlabel_full = f"{xlabel} (log)" if self.is_log_scale else xlabel

        if self.is_log_scale and self.full:
            raise Exception("\nSuch configuration (logarithmic scale and full-ACF) is not supported")

        # Handle figure creation
        self.fig = plt.figure(figsize=self.fig_size)

        n_row = int(np.ceil(np.sqrt(self.n_key + 1)))  # number of rows
        n_column = int(np.ceil((self.n_key + 1) / n_row))  # number of columns
        font_size = int(13 - 5 * (self.n_key / (self.n_key + 4)))

        # Plot residuals
        if self.has_residuals:
            fig_residuals = plt.figure(figsize=self.fig_size)
            fig_name_residuals = f"residuals-VS-{TAU if self.use_time else DELTA_X}"
            if self.is_log_scale:
                fig_name_residuals += "_Log-scale"

        # Prepare for scanning angle plotting
        if self.paa > 0:
            self.ppa_dict[f"{self.paa - 1}-{ACF_EXP}"] = {}
            self.ppa_dict[f"{self.paa - 1}-{ACF_MODEL}"] = {}

        for k_indx, acf_key in enumerate(self.sorted_acf_key_list):
            data = self.experimental_data_dict[acf_key]
            line_time_ms = round(data[LINE_TIME] * 1000, 1)
            angle = data[ANGLE]
            title = f"Line time: {line_time_ms} [ms]   Angle: {angle}{DEGREE}"
            if args.show_full_acf_key:
                title = data[ACF_KEY]
                font_size = font_size / 1.5

            # Track for angle-vs-ACF analysis
            if self.paa > 0:
                self.line_time_list.append(line_time_ms)
                self.angle_list.append(angle)

            # Create subplots
            if k_indx == 0:
                self.subplt = self.fig.add_subplot(n_row, n_column, 1)
            else:
                self.subplt = self.fig.add_subplot(n_row, n_column, k_indx + 1, sharex=self.subplt, sharey=self.subplt)
            if self.has_residuals:
                self.subplt_residuals = fig_residuals.add_subplot(n_row, n_column, k_indx + 1, sharex=self.subplt)
                self.subplt_residuals.tick_params(axis="both", labelsize=10)

            self.subplt.tick_params(axis="both", labelsize=10)

            # Plot ACF
            if self.acf_2D:  # plot 2D-ACF (RICS)
                self.plot_2d_acf_heatmap(data[ACF_MEAN_BEFORE_CUT])
            else:  # plot acf lines and fitted data in the case of fit is enabled
                self.plot_line(dict_value=data, sorted_acf_key=acf_key, line_time=line_time_ms, angle=angle, ki=k_indx)

                if k_indx % n_column == 0:
                    self.subplt.set_ylabel(y_label, fontweight="bold", fontsize=font_size)
                    if self.has_residuals:
                        self.subplt_residuals.set_ylabel(
                            self.resid_obj.res_y_label, fontweight="bold", fontsize=font_size
                        )

                if self.n_key <= 3 or k_indx > self.n_key - n_column - 1:
                    self.subplt.set_xlabel(xlabel_full, fontweight="bold", fontsize=font_size)
                    if self.has_residuals:
                        self.subplt_residuals.set_xlabel(xlabel_full, fontweight="bold", fontsize=font_size)

            self.subplt.set_title(title, y=1, loc="left", size=font_size)
            if self.has_residuals:
                self.subplt_residuals.set_title(title, y=1, loc="left", size=font_size)

        self.fig.tight_layout()

        # Final ACF line plot legend
        if not self.acf_2D:
            self.subplt.legend(loc="upper right", draggable=True, fontsize=10)

        # Remove spaces and [] from the sector key for use in output filenames
        x_loc, y_loc = self.sector_key.strip("[]").split()
        sector_name = f"X{x_loc[:5]}Y{y_loc[:5]}"

        # Add model parameter results to figure
        if self.model:
            self.add_param_text(self.fig, n_row, n_column, k_indx + 2)
            if self.has_residuals:
                fig_residuals.tight_layout()
                self.add_param_text(fig_residuals, n_row, n_column, k_indx + 2)

            # Plot ACF vs scanning angle
            if self.paa > 0:
                fig_paa = plt.figure(figsize=tuple(np.array(RECTANGULAR) * 2))
                self.subplt_ppa = fig_paa.add_subplot(111)
                self.subplt_ppa.tick_params(axis="both", labelsize=10)
                plot_acf_vs_angle(self)
                fig_paa.tight_layout()

                if use_pdf:
                    fig_name_paa = f"{ACF_LABEL}-{self.paa - 1}-VS-Scanning-angle"
                    args.output = f"{output_base}_{fig_name_paa}" if output_base else None
                    osuf = output_suffix(args, f"sector{sector_name}_{fig_name_paa}")
                    fig_paa.savefig(
                        get_output_fname(self.f_name, args.output, osuf, ".pdf"),
                        pad_inches=0,
                        bbox_inches="tight",
                    )

        # Save PDF outputs
        if use_pdf:
            osuf = output_suffix(args, f"sector{sector_name}_{fig_name}")
            self.fig.savefig(
                get_output_fname(self.f_name, output_base, osuf, ".pdf"),
                pad_inches=0,
                bbox_inches="tight",
            )

            if self.has_residuals:
                args.output = f"{output_base}_residuals" if output_base else None
                osuf = output_suffix(args, f"sector{sector_name}_{fig_name_residuals}")
                fig_residuals.savefig(
                    get_output_fname(self.f_name, args.output, osuf, ".pdf"),
                    pad_inches=0,
                    bbox_inches="tight",
                )

    """ ------------ Line Process ------------ """

    # Plot ACF-lines (FCS: 1, RICS: 3 by default)
    def plot_line(self, dict_value, sorted_acf_key, line_time, angle, ki):
        sub = self.subplt
        lines = dict_value[LINES]

        # Plot v-line: x = 0 if not log
        sub.set_xscale("log") if self.is_log_scale else sub.axvline(x=0, color="grey", linestyle="--", lw=0.5)

        # Plot h-line: ACF = 0
        sub.axhline(y=0, color="grey", linestyle="--", lw=0.5)

        self.exp_color = ["r"] if self.n_line == 1 else self.colors
        if self.model:
            self.fit_color = ["b"] if self.n_line == 1 else self.colors
            acf_indexes = self.acf_key_indexes[f"{sorted_acf_key}"]
            line_indexes = self.line_indexes[acf_indexes[0] : acf_indexes[1]]

            if self.ultranest:
                acf_model = self.acf_model[:, acf_indexes[0] : acf_indexes[1]]
                if self.has_residuals:
                    residuals = self.residuals[:, acf_indexes[0] : acf_indexes[1]]
            else:
                acf_model = self.acf_model[acf_indexes[0] : acf_indexes[1]]
                if self.has_residuals:
                    residuals = self.residuals[acf_indexes[0] : acf_indexes[1]]

            acf = self.acf[acf_indexes[0] : acf_indexes[1]] if self.paa > 0 else None

        for line in range(self.n_line):
            indexes = np.where(lines == line + lines[0])[0]
            acf_mean_line = dict_value[ACF_MEAN][[indexes]][0]
            acf_std_line = dict_value[ACF_STD][[indexes]][0]
            x_local_line = dict_value[DELTA_X_LOCAL][[indexes]][0]
            t_line = dict_value[DELTA_T][[indexes]][0]
            x_axis = t_line - (2 * t_line[0] - t_line[1]) if self.use_time else x_local_line

            # Consider errors for fitting
            yerr = acf_std_line if self.err_structure in (WLS, GLS) else None

            # Plot experiment data (ACF data)
            self.plot_acf_experimental_data(line, x_axis, acf_mean_line, yerr)

            if self.model:
                fit_idxs = np.where(line_indexes == line + line_indexes[0])[0]

                if self.n_excl != 0 and line == 0:
                    x_axis = x_axis[self.n_excl :]

                    if self.paa == line + 1:
                        x_local_line = x_local_line[self.n_excl :]

                # Plot ACF (fitted data by selected model)
                if self.ultranest:
                    plt.sca(sub)  # fit band plot
                    band = PredictionBand(x_axis)

                    for i in range(acf_model.shape[0]):
                        acf_sample = acf_model[i, [fit_idxs][0]]
                        band.add(acf_sample)  # add to fit band
                    add_prediction_band(self, band_y_axis=band, line=line)

                    # Plot residuals
                    if self.has_residuals:
                        plt.sca(self.subplt_residuals)
                        standardized_residual_samples = residuals[:, [fit_idxs][0]]
                        plot_residuals(
                            self, line=line, x_axis=x_axis, residuals=standardized_residual_samples, k_indx=ki
                        )

                    # Save ACF values at specified x-positions for plotting ACF versus scanning angles
                    if self.paa == line + 1:
                        y_axis_fit = acf_model[:, [fit_idxs][0]]
                else:
                    y_axis_fit = acf_model[[fit_idxs]][0]
                    self.plot_acf_fitted_data(line, x_axis, y_axis_fit)

                    # Plot residuals
                    if self.has_residuals:
                        standardized_residual = residuals[[fit_idxs]][0]
                        plot_residuals(self, line=line, x_axis=x_axis, residuals=standardized_residual, k_indx=ki)

                # Save ACF values at specified x-positions for plotting ACF versus scanning angles
                if self.paa == line + 1:
                    y_axis_exp = acf[[fit_idxs]][0]
                    for dx in self.dxl:
                        key = f"{ANGLE}-{angle}-lt-{line_time}-dx-{dx}"
                        x_index = np.where(x_local_line > dx)[0][0]
                        self.ppa_dict[f"{line}-{ACF_EXP}"][key] = y_axis_exp[x_index]
                        self.ppa_dict[f"{line}-{ACF_MODEL}"][key] = (
                            y_axis_fit[:, x_index] if self.ultranest else y_axis_fit[x_index]
                        )

    """ ------------ Plotting Methods ------------ """

    # Plot ACF (experimental data)
    def plot_acf_experimental_data(self, line, x_axis, y_axis, yerr):
        sub = self.subplt
        color = self.exp_color[line % len(self.exp_color)]
        marker = self.exp_marker[line % len(self.exp_marker)]
        label = "ACF (Experimental Data)" if line == 0 else None
        circle_size, excl_size = [30, 50] if self.n_key == 1 else [20, 35]

        # Plot error bars (SD)
        if self.error_bar:
            sub.errorbar(
                x_axis,
                y_axis,
                color=color,
                yerr=yerr,
                fmt="none",
                ecolor="k",
                label="Errors (mean ± SD)" if line == 0 else None,
                capsize=1.8,
                elinewidth=1,
            )
        sub.set_ylim(self.min_y_axis, self.max_y_axis)  # set y-axis limits

        if self.n_excl != 0 and line == 0:
            y = y_axis.copy()
            if self.full:
                half = len(y_axis) // 2
                start, end = half - self.n_excl, half + self.n_excl
            else:
                start, end = 0, self.n_excl
            y[start:end] = np.nan
            x_exc, y_exc = x_axis[start:end], y_axis[start:end]
            sub.scatter(x_axis, y, color=color, s=circle_size, label=label, marker=marker, edgecolors="none")
            sub.scatter(x_exc, y_exc, color=color, marker="x", s=excl_size, label="Excluded ACFs")
        else:
            sub.scatter(x_axis, y_axis, color=color, s=circle_size, label=label, marker=marker, edgecolors="none")

    # Plot ACF (experimental data)
    def plot_acf_fitted_data(self, line, x_axis, y_axis_fit):
        color = self.fit_color[line % len(self.fit_color)]
        linewidth = 1.6 if self.n_line == 1 else 0.9
        label = "Fit" if line == 0 else None
        self.subplt.plot(x_axis, y_axis_fit, color, linestyle="--", lw=linewidth, label=label)

    # Plot 2D-ACF heatmap
    def plot_2d_acf_heatmap(self, avg):
        y, x = avg.shape
        avg[y // 2, x // 2] = np.nan
        cax = self.subplt.imshow(avg, extent=[-x // 2, x // 2, y, -1])
        cb = self.fig.colorbar(cax, ax=self.subplt, shrink=0.6)
        cb.set_label(ACF_LABEL, fontsize=14, fontweight="bold")
        self.subplt.set_xlabel("X", fontweight="bold", fontsize=12)
        self.subplt.set_ylabel("Y", fontweight="bold", fontsize=12)

    # Plot samples and pairwise correlations (fit-bayes)
    def plot_ultranest_features(self, result_cls):
        self.ultranest = result_cls.ultranest_data
        args = self.args

        if args.plot_sample:
            plot_samples(self)

            # Save figure as a PDF file
            if self.args.pdf:
                file_format = ".pdf" if self.args.output is None else "-samples.pdf"
                osuf = output_suffix(self.args, "samples")
                plt.savefig(
                    get_output_fname(self.f_name, self.args.output, osuf, file_format),
                    pad_inches=0,
                    bbox_inches="tight",
                )

    """ ------------ Text (results) ------------ """

    def add_param_text(self, fig, rows, cols, count):
        txt_in_fig = fig.add_subplot(rows, cols, count)
        text = [self.parameters_dict[param][RES_TXT] + "\n" for param in self.parameters_dict]
        txt_in_fig.plot([], [], color="w", label="".join(text))
        txt_in_fig.axis("off")
        txt_in_fig.legend(
            fontsize=14 if count < 5 else (11 if len(text) < 6 else 7),
            alignment="left",
            draggable=True,
            edgecolor="w",
            mode="expand",
            borderpad=-1,
            handletextpad=-1,
            borderaxespad=0,
        )
