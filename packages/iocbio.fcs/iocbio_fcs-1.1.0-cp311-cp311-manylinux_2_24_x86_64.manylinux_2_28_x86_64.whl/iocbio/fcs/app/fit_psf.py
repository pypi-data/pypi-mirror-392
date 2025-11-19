#!/usr/bin/env python3
import argparse
from scipy.optimize import least_squares

from iocbio.fcs.lib.psf import PSF, gaussian_psf_model


def fit_psf(args):
    psf = PSF(psf_name=args.psf_name)
    x_flat = psf.x_flat
    y_flat = psf.y_flat
    z_flat = psf.z_flat
    psf_value_flat = psf.psf_value_flat

    # Fitting
    def error_func(parameters, delta_x, delta_y, delta_z, psf_value):
        y = gaussian_psf_model(delta_x, delta_y, delta_z, *parameters)
        residual = psf_value - y
        return residual

    parameters = ["w_x", "w_y", "w_z", "x_0", "y_0", "z_0", "amplitude"]
    p0 = [0.3, 0.3, 0.3 * 4, 0, 0, 0, 1]
    lower_bounds = [0.0, 0.0, 0.0, -2.0, -2.0, -2.0, 0.0]
    upper_bounds = [5.0, 5.0, 5.0, 2.0, 2.0, 2.0, 100.0]
    residual = least_squares(
        error_func,
        p0,
        bounds=(lower_bounds, upper_bounds),
        args=(x_flat, y_flat, z_flat, psf_value_flat),
    )
    error = error_func(residual.x, x_flat, y_flat, z_flat, psf_value_flat)
    error
    print()
    for i, k in enumerate(parameters):
        print(f"{k}:  {residual.x[i]:.2f}")


def main():
    parser = argparse.ArgumentParser(
        description="Fit PSF file (HDF5) using least squares method",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("psf_name", help="PSF file name")
    args = parser.parse_args()
    fit_psf(args)


if __name__ == "__main__":
    main()
