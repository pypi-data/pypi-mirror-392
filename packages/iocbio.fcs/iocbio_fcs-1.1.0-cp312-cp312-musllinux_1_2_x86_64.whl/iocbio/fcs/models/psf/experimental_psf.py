from iocbio.fcs.lib.base_model import AbstractModel


class AbstractModelExperimentalPSF(AbstractModel):
    @staticmethod
    def config_parser(parser):
        # PSF (Point Spread Function) parameters
        parser.add_argument("-pf", "--psf-file", default="average-psf.h5", help="PSF file name")
        parser.add_argument(
            "-dxy",
            "--downsample-xy",
            type=int,
            default=1,
            help="Downsample factor for the X and Y axes of the PSF. "
            "This reduces the resolution of the PSF in the lateral (XY) plane. "
            "The PSF is first smoothed using a box-shaped convolution filter "
            "then downsampled by the given factor. "
            "This mimics how the PSF would appear in a system with lower lateral resolution. "
            "For example, using --downsample-xy 2 halves the PSF size in X and Y.",
        )
        parser.add_argument(
            "-dz",
            "--downsample-z",
            type=int,
            default=1,
            help="Downsample factor for the Z axis of the PSF. "
            "This reduces the resolution of the PSF along the axial (Z) direction. "
            "For example, using --downsample-z 2 halves the PSF size in Z.",
        )

    def __init__(self, args):
        super().__init__(args)
