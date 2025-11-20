from pathlib import Path

import numpy
from ewokscore import Task
from silx.io.url import DataUrl
from tomoscan.esrf.scan.nxtomoscan import NXtomoScan


class ReduceDarkFlat(
    Task,
    input_names=["nx_path"],
    optional_input_names=[
        "dark_reduction_method",
        "flat_reduction_method",
        "overwrite",
        "output_dtype",
        "return_info",
    ],
    output_names=[
        "reduced_darks_path",
        "reduced_flats_path",
    ],
):
    def run(self):
        """
        Reduce the dark and flat frames of the input NX file.
        """

        nx_path = Path(self.inputs.nx_path).resolve()
        d_reduction_method = self.get_input_value("dark_reduction_method", "mean")
        f_reduction_method = self.get_input_value("flat_reduction_method", "median")
        overwrite = self.get_input_value("overwrite", True)
        output_dtype = self.get_input_value("output_dtype", numpy.float32)
        return_info = self.get_input_value("return_info", False)

        scan = NXtomoScan(str(nx_path), entry="entry0000")

        reduced_dark = scan.compute_reduced_darks(
            reduced_method=d_reduction_method,
            overwrite=overwrite,
            output_dtype=output_dtype,
            return_info=return_info,
        )
        reduced_flat = scan.compute_reduced_flats(
            reduced_method=f_reduction_method,
            overwrite=overwrite,
            output_dtype=output_dtype,
            return_info=return_info,
        )

        references_dir = nx_path.parent.parent / "references"
        references_dir.mkdir(parents=True, exist_ok=True)

        base_name = nx_path.stem

        dark_file = references_dir / f"{base_name}_darks.hdf5"
        flat_file = references_dir / f"{base_name}_flats.hdf5"

        dark_urls = (
            DataUrl(
                file_path=str(dark_file),
                data_path="{entry}/darks/{index}",
                scheme=NXtomoScan.SCHEME,
            ),
        )
        dark_metadata_urls = (
            DataUrl(
                file_path=str(dark_file),
                data_path="{entry}/darks/",
                scheme=NXtomoScan.SCHEME,
            ),
        )
        flat_urls = (
            DataUrl(
                file_path=str(flat_file),
                data_path="{entry}/flats/{index}",
                scheme=NXtomoScan.SCHEME,
            ),
        )
        flat_metadata_urls = (
            DataUrl(
                file_path=str(flat_file),
                data_path="{entry}/flats/",
                scheme=NXtomoScan.SCHEME,
            ),
        )

        scan.save_reduced_darks(
            reduced_dark,
            overwrite=overwrite,
            output_urls=dark_urls,
            metadata_output_urls=dark_metadata_urls,
        )
        scan.save_reduced_flats(
            reduced_flat,
            overwrite=overwrite,
            output_urls=flat_urls,
            metadata_output_urls=flat_metadata_urls,
        )

        self.outputs.reduced_darks_path = str(dark_file)
        self.outputs.reduced_flats_path = str(flat_file)
