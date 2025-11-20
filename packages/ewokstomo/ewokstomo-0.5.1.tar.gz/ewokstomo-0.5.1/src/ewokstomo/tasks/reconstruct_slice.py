from ewokscore import Task
from pathlib import Path


class ReconstructSlice(
    Task,
    input_names=["nx_path", "config_dict", "slice_index"],
    output_names=[
        "reconstructed_slice_path",
        "slice_index",
    ],
):
    def run(self):
        """
        Task that reconstructs a single slice from full-field tomography data using Nabu:

        - Accepts a configuration dictionary for Nabu and a slice index.
        - Generates a Nabu configuration file with adjusted start and end z indices to reconstruct only one slice.
        - Runs Nabu to perform the reconstruction.
        - Saves the resulting slice to disk in a subfolder named "slices" located at the scan root (sibling of the `projections` directory).
        - Outputs both the path to the saved reconstructed slice and the in-memory numpy array of the slice.

        Inputs:

        - config_dict: A dictionary containing parameters used to override Nabu's default configuration.
                        Must include at least "dataset" -> "location", pointing to the input NX file.
                        (see https://www.silx.org/pub/nabu/doc/nabu_config_items.html)
        - slice_index: Index of the slice to reconstruct. Can be an integer or one of the strings:
                     "first", "middle", or "last".

        Outputs:

        - reconstructed_slice_path: The file path to the saved reconstructed slice.
        """
        from nabu.pipeline.fullfield.reconstruction import FullFieldReconstructor
        from nabu.pipeline.fullfield.processconfig import ProcessConfig

        overwritten_config_fields = self.get_input_value("config_dict")
        slice_index = self.get_input_value("slice_index", "middle")
        nx_path = Path(self.get_input_value("nx_path"))

        if not nx_path.exists():
            raise FileNotFoundError(f"NX file not found: {nx_path}")

        output_dir = nx_path.parent.parent / "slices"
        output_dir.mkdir(exist_ok=True)

        technique = _get_technique_from_nabu_config(overwritten_config_fields)

        # Prepare the configuration for nabu
        overwritten_config_fields["dataset"]["location"] = str(nx_path)
        overwritten_config_fields["reconstruction"]["start_z"] = slice_index
        overwritten_config_fields["reconstruction"]["end_z"] = slice_index
        overwritten_config_fields["output"]["location"] = str(output_dir)
        overwritten_config_fields["output"][
            "file_prefix"
        ] = f"{nx_path.stem}_{technique}_xy"

        proc = ProcessConfig(conf_dict=overwritten_config_fields)
        reconstructor = FullFieldReconstructor(proc)
        reconstructor.reconstruct()
        reconstructor.finalize_files_saving()
        self.outputs.reconstructed_slice_path = list(reconstructor.results.values())[0]
        self.outputs.slice_index = slice_index


def _get_technique_from_nabu_config(nabu_config: dict[str, dict[str, str]]) -> str:
    """Extract the technique from the Nabu configuration dictionary."""
    method = nabu_config.get("method")
    technique = "absorption"
    if isinstance(method, str):
        if method in ("Paganin", "CTF"):
            technique = "phase"
    return technique
