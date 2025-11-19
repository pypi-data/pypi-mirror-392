import numpy as np
from iocbio.fcs.lib.base_model import AbstractModel
from iocbio.fcs.lib.const import MEAN


class AbstractModelAnalyticalPSF(AbstractModel):
    @staticmethod
    def config_parser(parser):
        # PSF (Point Spread Function) parameters
        parser.add_argument("--wx", type=float, default=0.3, help="PSF width along X-axis [micrometer]")
        parser.add_argument("--wy", type=float, default=0.3, help="PSF width along Y-axis [micrometer]")
        parser.add_argument("--wz", type=float, default=1.1, help="PSF width along Z-axis [micrometer]")

    def __init__(self, args):
        super().__init__(args)
        self.wx, self.wy, self.wz = args.wx, args.wy, args.wz
        self.focal_vol = (np.pi**1.5) * self.wx * self.wy * self.wz

    def result_process(self, results, std_results, verbose=True):
        parameter_result_dict = super().result_process(results, std_results, verbose)
        component_num = 1

        for k, v in parameter_result_dict.items():
            if "Concentration" in str(k):
                component = f"(component {component_num}) " if self.component_num > 1 else ""
                n_particle = v[MEAN]
                num_p = n_particle * (self.psf_scale**3) * self.focal_vol
                print(f"Number of particles {component}[in focal volume]: {num_p:.3f}")
                component_num += 1
        return parameter_result_dict
