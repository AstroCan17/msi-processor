# `data/input/` — msi-processor inputs

The processor consumes the **Sentinel-2 MSI Synthetic Raw Data Generator**'s output as its L0 input.
The symlink **`raw_generator_output`** points to the generator's `data/output/` (the open-container L0 +
the cal-DB ADFs `nuc`/`dark`/`radiometric`/`spectral`):

    raw_generator_output -> ../../../../s2-msi-raw-generator/data/output

The relative target resolves when `s2-msi-raw-generator` and `ipf/msi-processor` are checked out side by
side under the same parent (the standard dev layout). On other layouts (e.g. the SDE), point the E2E
driver `scripts/run_e2e_l0_to_l1b.py` at explicit paths instead. Large `.zarr` products are gitignored.
