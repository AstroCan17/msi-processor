# `data/input/` — msi-processor inputs

The processor consumes the **Sentinel-2 MSI Synthetic Raw Data Generator**'s output as its L0 input:
the open-container L0 (`l0/S02MSIL0__…_OC.zarr`, PSFD-named) plus the cal-DB ADFs
(`caldb/{nuc,dark,radiometric,spectral}.zarr`).

Those products live in one central **data store** written by the generator's E2E driver
`scripts/run_pipeline.py` — its store argument (the generator tracks `data/output/` in git;
on the SDE a dedicated root such as `~/data-store`). Point the driver (or place inputs here) with
explicit paths; no fixed cross-repo layout is assumed. Large `.zarr` products are gitignored.
