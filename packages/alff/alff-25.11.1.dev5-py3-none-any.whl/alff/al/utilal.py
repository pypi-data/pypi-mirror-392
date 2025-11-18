from pathlib import Path


class D3Param:
    """Different packages use different names for D3 parameters. This class to 'return' standard D3 parameter names for different packages."""

    def __init__(self, d3package: str = "7net"):
        self.d3package: str = d3package
        self.default_cutoff: float = 50.2022
        self.default_cn_cutoff: float = 21.1671
        params = self.get_params()  # set self.param_names and self.damping_map
        ### Store params
        self.param_names = params["params"]
        self.damping_map = params["damping_map"]
        return

    def get_params(self) -> dict:
        """Return D3 parameter names according to different packages."""
        if self.d3package == "lammps":
            params = self._d3_lammps()
        elif self.d3package == "7net":
            params = self._d3_7net()
        else:
            raise ValueError(f"Unsupported D3 package: {self.d3package}")
        return params

    def check_supported_damping(self, damping: str):
        """Check if the damping method is supported in the selected package."""
        params = self.get_params()
        if damping not in params["damping_map"].keys():
            raise ValueError(
                f"Damping method '{damping}' is not supported in package '{self.d3package}'. Supported methods: {list(params['damping_map'].keys())}"
            )
        return

    def _d3_lammps(self) -> dict:
        ### https://docs.lammps.org/pair_dispersion_d3.html
        ### use lammps' D3 in 7Net: https://github.com/MDIL-SNU/SevenNet/issues/246
        """Return D3 parameters using in LAMMPS's dispersion/d3"""
        return {
            "params": ["damping", "functional", "cutoff", "cn_cutoff"],
            "damping_map": {
                "zero": "original",
                "zerom": "zerom",
                "bj": "bj",
                "bjm": "bjm",
            },
        }

    def _d3_7net(self) -> dict:
        ### https://github.com/MDIL-SNU/SevenNet/tree/main/sevenn/pair_e3gnn
        """Return D3 parameters using in SevenNet's e3gnn"""
        return {
            "params": ["damping", "xc", "cutoff", "cnthr"],
            "damping_map": {
                "zero": "damp_zero",
                "bj": "damp_bj",
            },
        }

    @staticmethod
    def angstrom_to_bohr(value_in_angstrom: float) -> float:
        """Convert Angstrom to Bohr"""
        value = round(value_in_angstrom / 0.52917721, ndigits=2)
        return value

    @staticmethod
    def angstrom_to_bohr2(value_in_angstrom: float) -> float:
        """Convert Angstrom to Bohr^2. To used in 7net package."""
        value = round((value_in_angstrom / 0.52917721) ** 2, ndigits=2)
        return value


class MLP2Lammps:
    """Convert MLP model to be used in LAMMPS."""

    def __init__(self, mlp_model: str = "7net"):
        self.mlp_model: str = mlp_model
        self._check_supported_model()
        return

    def convert(
        self,
        checkpoint: str | Path,
        outfile: str | Path = "deployed.pt",
        **kwargs,
    ):
        """Convert MLP model to LAMMPS format.

        Args:
            checkpoint (str | Path): Path to checkpoint file of MLP model.
            outfile (str | Path): Path to output LAMMPS potential file.
            **kwargs: Additional arguments for specific conversion methods.
        """
        if self.mlp_model == "7net":
            MLP2Lammps.convert_7net(checkpoint, outfile, **kwargs)
        elif self.mlp_model == "7net_mliap":
            MLP2Lammps.convert_7net_mliap(checkpoint, outfile, **kwargs)
        return

    def _check_supported_model(self):
        """Return supported MLP models."""
        supported_models = ["7net", "7net_mliap"]
        if self.mlp_model not in supported_models:
            raise ValueError(
                f"MLP model: {self.mlp_model} is unsupported. Available models: {supported_models}"
            )
        return

    @staticmethod
    def convert_7net(
        checkpoint: str | Path,
        outfile: str | Path = "deploy_7net",
        parallel_type=False,
    ):
        ### https://github.com/MDIL-SNU/SevenNet/blob/main/sevenn/scripts/deploy.py
        """
        Args:
            checkpoint (str | Path): Path to checkpoint file of 7net model.
            outfile (str | Path): Path to output LAMMPS potential file.
            parallel_type (bool): Convert to potential for run in parallel simulations.

        Notes:
            Single mode: will generate file as "outfile.pt"
            Parallel mode: will generate files as "outfile/deployed_parallel_0.pt", "outfile/deployed_parallel_1.pt", ...
        """
        from sevenn.scripts.deploy import deploy, deploy_parallel

        if parallel_type:
            deploy_parallel(checkpoint, outfile)
        else:
            deploy(checkpoint, outfile)
        return

    @staticmethod
    def convert_7net_mliap(
        checkpoint: str | Path,
        outfile: str | Path = "deploy_7net_mliap.pt",
        modal: str = None,
        use_cueq: bool = False,
        use_flash: bool = False,
        cutoff: float = None,
    ):
        ### https://github.com/MDIL-SNU/SevenNet/blob/develop/omni/sevenn/integrations/lammps_mliap/create_lmp_mliap_file.py
        """
        Args:
            checkpoint (str | Path): Path to checkpoint file of 7net model.
            outfile (str | Path): Path to output LAMMPS potential file.
            modal (str): Channel of multi-task model.
            use_cueq (bool): Use cueq.
            use_flash (bool): Use flashTP.
            cutoff (float): Neighbor cutoff (Angstrom). Required if it cannot be inferred from the model.
        """
        try:
            import torch
            from sevenn.integrations.lammps_mliap.lmp_mliap_wrapper import (
                SevenNetLAMMPSMLIAPWrapper,
            )
        except Exception as e:
            raise ImportError(
                f"Error importing SevenNetLAMMPSMLIAPWrapper. \n{e} \nHints: Make sure installing 7Net package from its branch 'develop/omni', and install `lammps` from conda-forge channel."
            )

        mliap_module = SevenNetLAMMPSMLIAPWrapper(
            model_path=checkpoint,
            modal=modal,
            enable_cueq=use_cueq,
            enable_flash=use_flash,
            cutoff=cutoff,
        )
        torch.save(mliap_module, outfile)
        return
