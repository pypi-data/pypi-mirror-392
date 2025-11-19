#!/usr/bin/env python3
import argparse
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

from iocbio.fcs.lib.psf import PSF


def app(args):
    psf = PSF(psf_name=args.psf_name, create_psf_args=args)
    psf_values = psf.psf_value

    # Plot PSF
    zmax = psf_values.shape[0] - 1
    z0 = zmax // 2  # start from middle slice
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    im = ax.imshow(psf_values[z0], cmap="viridis")
    ax.set_xlabel("X", fontweight="bold", fontsize=12)
    ax.set_ylabel("Y", fontweight="bold", fontsize=12)

    # Slider setup
    ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])
    slider = Slider(ax_slider, "Z", 0, zmax, valinit=z0, valstep=1)

    # Update function
    def update(val):
        idx = int(slider.val)
        im.set_data(psf_values[idx])
        ax.set_title(f"Image {idx}")
        fig.canvas.draw_idle()

    slider.on_changed(update)
    plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Create a 3D-Gaussian ellipsoid PSF as HDF5 file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # PSF file name
    parser.add_argument("--psf-name", default="psf", help="Name of HDF file")

    # Number of voxels along X, Y, and Z axes
    parser.add_argument(
        "-xyv",
        "--xy-voxels",
        type=int,
        default=30,
        help="Specifies the number of voxels along X-Y axes in the 3D-PSF shape (Z, Y, X)",
    )
    parser.add_argument(
        "-zv",
        "--z-voxels",
        type=int,
        default=40,
        help="Specifies the number of voxels along Z axis in the 3D-PSF shape (Z, X, Y)",
    )

    # PSF size
    parser.add_argument(
        "-xyspan",
        "--total-xy-size",
        type=float,
        default=1,
        help="PSF size along X-Y axes [micrometer]",
    )
    parser.add_argument(
        "-zspan",
        "--total-z-size",
        type=float,
        default=4,
        help="PSF size along Z axis [micrometer]",
    )

    # PSF waist parameters
    parser.add_argument("--wx", type=float, default=0.3, help="PSF width along X axis [micrometer]")
    parser.add_argument("--wy", type=float, default=0.3, help="PSF width along Y axis [micrometer]")
    parser.add_argument("--wz", type=float, default=1.1, help="PSF width along Z axis [micrometer]")

    args = parser.parse_args()
    app(args)


if __name__ == "__main__":
    main()
