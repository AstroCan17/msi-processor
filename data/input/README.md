# `data/input/` — msi-processor inputs

The processor consumes the **Sentinel-2 MSI Synthetic Raw Data Generator**'s output as its L0 input:
the open-container L0 (`l0/L0c_opencontainer.zarr`) plus the cal-DB ADFs
(`caldb/{nuc,dark,radiometric,spectral}.zarr`).

Those products live in one central **data store** written by the generator's E2E driver
`scripts/run_e2e_l0_to_l1b.py` — its `work_dir` argument (default: the generator repo's `data/output/`;
on the SDE a dedicated root such as `~/data-store`). Point the driver (or place inputs here) with
explicit paths; no fixed cross-repo layout is assumed. Large `.zarr` products are gitignored.
