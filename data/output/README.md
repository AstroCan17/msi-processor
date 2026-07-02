# `data/output/` — msi-processor products

| Sub-folder | Content | Git |
|---|---|---|
| `l1b/` | L1B **TOA-reflectance** product (`.zarr`) from `l0_decode → radiometric → enhancement → toa` | **ignored** (large satellite-image product) |
| `quicklook/` | Small RGB PNG preview of the L1B reflectance | **committed** (README / site showcase) |

Produced end-to-end by the generator's `scripts/run_e2e_l0_to_l1b.py` (needs `eopf==2.8.1` +
`msi_processor`): it reads the generator L0 + cal-DB from its central data store (the driver's
`work_dir`, e.g. `~/data-store` on the SDE), runs the processing chain, and persists the real L1B
reflectance (`EOZarrStore` → `l1b/L1B_TOA.zarr`) + an RGB quicklook into that same store. The
committed copies here are the small showcase artifacts; the large `.zarr` products stay gitignored.
