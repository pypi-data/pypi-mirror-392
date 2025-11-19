import h5py
import numpy as np
from scipy import ndimage
from iocbio.fcs.lib.const import MICROMETER_TO_METER

from .engines.psfmult import psfmult

VOXEL_SIZE_X = "voxel size x"
VOXEL_SIZE_Y = "voxel size y"
VOXEL_SIZE_Z = "voxel size z"


def gaussian_psf_model(x, y, z, w_x, w_y, w_z, x0, y0, z0, amplitude):
    gaus_x = np.exp(-2 * ((x - x0) ** 2) / (w_x**2))
    gaus_y = np.exp(-2 * ((y - y0) ** 2) / (w_y**2))
    gaus_z = np.exp(-2 * ((z - z0) ** 2) / (w_z**2))
    return amplitude * gaus_x * gaus_y * gaus_z


class PSF:
    MODE_CREATE_PSF = 1
    MODE_FIT_PSF = 2
    MODE_REAL_PSF = 3

    def __init__(self, psf_name="PSF_filename", downsample_xy=None, downsample_z=None, create_psf_args=None):
        self.psf_name = psf_name
        self.dsxy = downsample_xy
        self.dsz = downsample_z
        self._psf_scale = 1.0

        # determine the mode
        if create_psf_args:
            self._mode = PSF.MODE_CREATE_PSF
        elif self.dsxy is not None or self.dsz is not None:
            self._mode = PSF.MODE_REAL_PSF
        else:
            self._mode = PSF.MODE_FIT_PSF

        if self._mode == PSF.MODE_CREATE_PSF:
            self.set_psf_properties(create_psf_args)
        else:
            self.load_psf_file()

        # Meshgrid generation
        self.generate_mesh()

        if self._mode == PSF.MODE_CREATE_PSF:
            # Generate 3D Gaussian ellipsoid PSF
            self.psf_value = gaussian_psf_model(
                x=self.x_mesh,
                y=self.y_mesh,
                z=self.z_mesh,
                w_x=self.wx,
                w_y=self.wy,
                w_z=self.wz,
                x0=0,
                y0=0,
                z0=0,
                amplitude=1,
            )

            # Save values in HDF5 file
            self.save_psf_file()
        else:
            # Flatten arrays for vectorized operations
            self.flat_array()

            if self._mode == PSF.MODE_REAL_PSF:
                # Filtering (PSF value < 0.01 Max)
                self.filter_func()

                # Normalization
                self.normalization()

                # Get all unique combinations
                self.uniq_combine()

        # Print PSF info
        print(f"Voxel volume:  {self.voxel_volume:.5f}")
        print(f"voxel_x:       {self.voxel_x:.4f}")
        print(f"voxel_y:       {self.voxel_y:.4f}")
        print(f"voxel_z:       {self.voxel_z:.4f}")
        print(f"PSF*PSF all combinations: {self.psf_value.size * self.psf_value.size}")
        if self._mode == PSF.MODE_REAL_PSF:
            print(f"PSF*PSF unique values: {self.psf_mult.shape[0]}")
            print(f"PSF*PSF in MB: {(self.psf_mult.nbytes / 1024 / 1024):.4f}")

    @property
    def psf_scale(self):
        return self._psf_scale

    @property
    def voxel_x(self):
        return self._voxel_x * self.psf_scale

    @property
    def voxel_y(self):
        return self._voxel_y * self.psf_scale

    @property
    def voxel_z(self):
        return self._voxel_z * self.psf_scale

    @property
    def voxel_volume(self):
        return self.voxel_x * self.voxel_y * self.voxel_z

    @psf_scale.setter
    def psf_scale(self, a):
        self._psf_scale = a

    def set_psf_properties(self, args):
        # PSF array shape (Z, Y, X)
        self.z_dim, self.y_dim, self.x_dim = args.z_voxels, args.xy_voxels, args.xy_voxels

        # Physical PSF size (in micrometers)
        self._psf_width = args.total_xy_size  # total X span
        self._psf_height = args.total_xy_size  # total Y span
        self._psf_depth = args.total_z_size  # total Z span

        # PSF waist parameters
        self._voxel_x = self.wx = args.wx
        self._voxel_y = self.wy = args.wy
        self._voxel_z = self.wz = args.wz

    def flat_array(self):
        self.psf_value_flat = self.psf_value.flatten()
        self.x_flat = self.x_mesh.flatten()
        self.y_flat = self.y_mesh.flatten()
        self.z_flat = self.z_mesh.flatten()

    def filter_func(self):
        max_value = np.max(self.psf_value)
        cutoff = 0.01 * max_value
        filter_index = self.psf_value_flat > cutoff
        self.x_flat = self.x_flat[filter_index]
        self.y_flat = self.y_flat[filter_index]
        self.z_flat = self.z_flat[filter_index]
        self.psf_value = self.psf_value_flat[filter_index]
        print(f"Number of PSF elements after filtering:                  {self.psf_value.size}\n")

    def generate_mesh(self):
        # Fit ACF data by models
        if self._mode == PSF.MODE_REAL_PSF:
            # Coordinate axes (started from zero)
            self.x_axis = np.array(range(self.x_dim), dtype=np.int32)
            self.y_axis = np.array(range(self.y_dim), dtype=np.int32)
            self.z_axis = np.array(range(self.z_dim), dtype=np.int32)
        else:
            # Physical PSF size (in micrometers)
            psf_width = (
                self._psf_width if self._mode == PSF.MODE_CREATE_PSF else self.x_dim * self.voxel_x
            )  # total X span
            psf_height = (
                self._psf_height if self._mode == PSF.MODE_CREATE_PSF else self.y_dim * self.voxel_y
            )  # total Y span
            psf_depth = (
                self._psf_depth if self._mode == PSF.MODE_CREATE_PSF else self.z_dim * self.voxel_z
            )  # total Z span

            # Coordinate axes (centered around zero)
            self.x_axis = np.linspace(-psf_width / 2, psf_width / 2, self.x_dim)
            self.y_axis = np.linspace(psf_height / 2, -psf_height / 2, self.y_dim)  # flip for image convention
            self.z_axis = np.linspace(psf_depth / 2, -psf_depth / 2, self.z_dim)  # flip for image convention

        self.z_mesh, self.y_mesh, self.x_mesh = self.meshgrid_func()

    def load_psf_file(self):
        self.psf = h5py.File(self.psf_name, "r+")
        dataset_name = self.psf.keys()
        if "image" in dataset_name:
            dataset_name = "image"
        elif "psf" in dataset_name:
            dataset_name = "psf"
        else:
            raise Exception("\nUnknown dataset name")

        psf_data = self.psf[dataset_name]
        self.psf_value = np.array(psf_data)
        self._voxel_x = psf_data.attrs[VOXEL_SIZE_X] / MICROMETER_TO_METER  # [micrometer]
        self._voxel_y = psf_data.attrs[VOXEL_SIZE_Y] / MICROMETER_TO_METER  # [micrometer]
        self._voxel_z = psf_data.attrs[VOXEL_SIZE_Z] / MICROMETER_TO_METER  # [micrometer]

        print(f"\nShape of original PSF:           {self.psf_value.shape}; Elements: {self.psf_value.size}")

        # Fit ACF data by models
        if self._mode == PSF.MODE_REAL_PSF:
            # Convolution (Down Sampling)
            if self.dsxy > 1 or self.dsz > 1:
                ones_box = np.ones((self.dsz, self.dsxy, self.dsxy))
                convolved_psf = ndimage.convolve(self.psf_value, ones_box)
                self.psf_value = convolved_psf[
                    self.dsz // 2 : -1 : self.dsz,
                    self.dsxy // 2 : -1 : self.dsxy,
                    self.dsxy // 2 : -1 : self.dsxy,
                ]
                print(f"Shape of PSF after downsampling: {self.psf_value.shape}; Elements: {self.psf_value.size}")

            # PSF size
            self._voxel_x = self._voxel_x * self.dsxy
            self._voxel_y = self._voxel_y * self.dsxy
            self._voxel_z = self._voxel_z * self.dsz

        # Fit PSF to Gaussian ellipsoid for extracting waist parameters (wx, wy, and wz)
        else:
            # Normalization
            self.normalization()

        # PSF array shape (Z, Y, X)
        self.z_dim, self.y_dim, self.x_dim = self.psf_value.shape

    def normalization(self):
        self.psf_value /= self.psf_value.sum() * self.voxel_volume

    def meshgrid_func(self):
        return np.meshgrid(self.z_axis, self.y_axis, self.x_axis, indexing="ij")

    def save_psf_file(self):
        with h5py.File(f"{self.psf_name}.h5", "w") as psf:
            dataset = psf.create_dataset("image", data=self.psf_value)
            x = self._psf_width / self.x_dim
            y = self._psf_height / self.y_dim
            z = self._psf_depth / self.z_dim
            dataset.attrs["element_size_um"] = np.array([z, y, x])
            dataset.attrs[VOXEL_SIZE_X] = x * MICROMETER_TO_METER  # [meter]
            dataset.attrs[VOXEL_SIZE_Y] = y * MICROMETER_TO_METER  # [meter]
            dataset.attrs[VOXEL_SIZE_Z] = z * MICROMETER_TO_METER  # [meter]

    def uniq_combine(self):
        psf = self.psf
        combination_key = f"psfpsf/{self.dsxy}-{self.dsz}"
        if combination_key in psf:  # check HDF5 if older combinations were cached
            group = psf[combination_key]
            self.psf_mult = group["psfpsf"][:]
            deltax = group["x"][:]
            deltay = group["y"][:]
            deltaz = group["z"][:]
        else:
            self.psf_mult, deltax, deltay, deltaz = psfmult(self.psf_value, self.x_flat, self.y_flat, self.z_flat)
            print(deltax.dtype)
            if self.psf_value.size > 5000:
                psf[combination_key + "/psfpsf"] = self.psf_mult
                psf[combination_key + "/x"] = deltax
                psf[combination_key + "/y"] = deltay
                psf[combination_key + "/z"] = deltaz

        # Split into unique delta-xyz along each axis
        self.deltax_unique, self.deltax_index = np.unique(deltax, return_inverse=True)
        self.deltay_unique, self.deltay_index = np.unique(deltay, return_inverse=True)
        self.deltaz_unique, self.deltaz_index = np.unique(deltaz, return_inverse=True)
        self.deltax_index = self.deltax_index.astype(np.int32)
        self.deltay_index = self.deltay_index.astype(np.int32)
        self.deltaz_index = self.deltaz_index.astype(np.int32)
