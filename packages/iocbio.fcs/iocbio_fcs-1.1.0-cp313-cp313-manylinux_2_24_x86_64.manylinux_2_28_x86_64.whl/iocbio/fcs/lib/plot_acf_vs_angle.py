import numpy as np
from iocbio.fcs.lib.const import MICROMETER, DELTA_X, ACF_EXP, ACF_MODEL, ACF_LABEL, G_DELTA_X_LABEL, ANGLE
from ultranest.plot import PredictionBand


# Plot ACF versus scanning angles
def plot_acf_vs_angle(self):
    angle_list = sorted(set(self.angle_list))
    line_time_list = sorted(set(self.line_time_list))
    nl = len(line_time_list)  # number of line times (speeds)
    na = len(angle_list)  # number of angles
    if nl * na != len(self.sorted_acf_key_list) or na == 1:
        raise ValueError("\nInsufficient number of angles for the different speeds")
    xlabel, ylabel = "Scanning angle [degree]", G_DELTA_X_LABEL
    acf = self.ppa_dict[f"{self.paa - 1}-{ACF_EXP}"]
    acf_model = self.ppa_dict[f"{self.paa - 1}-{ACF_MODEL}"]

    xticks = np.arange(min(angle_list), max(angle_list) + 1, angle_list[1] - angle_list[0])
    self.subplt_ppa.set_xticks(xticks)

    for dx_index, dx in enumerate(self.dxl):
        for lt_index, lt in enumerate(line_time_list):
            key_prefix = f"lt-{lt}-dx-{dx}"
            acf_values = [acf[f"{ANGLE}-{angle}-{key_prefix}"] for angle in angle_list]
            model_values = [acf_model[f"{ANGLE}-{angle}-{key_prefix}"] for angle in angle_list]

            color = self.colors[lt_index]
            marker = self.exp_marker[dx_index]
            label = f"{ACF_LABEL} - line time: {lt} [ms]" if dx_index == 0 else None

            self.subplt_ppa.plot(angle_list, acf_values, "-", color=color, alpha=0.3)
            self.subplt_ppa.scatter(angle_list, acf_values, label=label, color=color, marker=marker)

            if self.ultranest:
                band_paa = PredictionBand(angle_list)
                model_values = np.array(model_values)
                transposed_acf = np.transpose(model_values)
                qr = ["68.2% quantile range", "99% quantile range"]

                for acf_sample in transposed_acf:
                    band_paa.add(acf_sample)

                band_paa.line(color=color, label="Fit (median)" if dx_index == 0 else None)

                # Plot 68.2% quantile range as shaded area
                band_paa.shade(
                    q=0.341,
                    color="k",
                    alpha=0.4,
                    label=(qr[0] if (dx_index == len(self.dxl) - 1 and lt_index == len(line_time_list) - 1) else None),
                )

                # Plot 99% quantile range as shaded area
                band_paa.shade(
                    q=0.48,
                    color="gray",
                    alpha=0.4,
                    label=(qr[1] if (dx_index == len(self.dxl) - 1 and lt_index == len(line_time_list) - 1) else None),
                )
            else:
                self.subplt_ppa.plot(
                    angle_list, model_values, "--", lw=1.3, color=color, label="Fit" if dx_index == 0 else None
                )

        # Add Delta x annotation after looping through all line times for this dx
        annotation = f"{DELTA_X} = {dx} [{MICROMETER}]"
        x_loc = angle_list[0] - angle_list[-1] / 30
        y_loc = min(acf_values)
        self.subplt_ppa.text(x_loc, y_loc, annotation, fontsize=10, rotation="vertical")

    self.subplt_ppa.set_xlabel(xlabel, fontweight="bold", fontsize=12)
    self.subplt_ppa.set_ylabel(ylabel, fontweight="bold", fontsize=12)
    self.subplt_ppa.tick_params(axis="both", labelsize=10)
    self.subplt_ppa.legend(draggable=True, fontsize=10)
