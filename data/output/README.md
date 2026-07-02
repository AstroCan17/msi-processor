# `data/output/` — msi-processor products

| Sub-folder | Content | Git |
|---|---|---|
| `l1b/` | L1B **TOA-reflectance** product (`.zarr`) from `l0_decode → radiometric → enhancement → toa` | **ignored** (large satellite-image product) |
| `quicklook/` | Small RGB PNG preview of the L1B reflectance | **committed** (README / site showcase) |

Produced end-to-end by the generator's `scripts/run_e2e_l0_to_l1b.py` (needs `eopf==2.8.1` +
`msi_processor`): it reads the generator L0 + cal-DB from `data/input/raw_generator_output/`, runs the
processing chain, and writes the real L1B reflectance here. The large `.zarr` is gitignored; the small
quicklook PNG is committed.
