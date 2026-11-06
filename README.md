# lac-subnational

Regional GDP per capita relative to the national average (national = 100) in **South America**. This repeats the exercise behind the OECD map *"Across Europe, regions within the same country are experiencing very different economic outcomes"* (OECD, *Regions and Cities at a Glance 2026*), using the same indicator, classes and colour scheme.

Paul Wander, Division of Production, Productivity and Management, UN-ECLAC.

**Status (2026-11-06):** first version on DOSE V2.14. 9 of 12 South American countries; latest years 2014–2019.

## Streamlit app

Deploy on share.streamlit.io: **Create app** → repository `wanderdata/lac-subnational`, branch `main`, main file `app/app.py`. Dependencies are in `app/requirements.txt`. To run locally: `streamlit run app/app.py`.

| Page | Contents |
|---|---|
| Map | OECD-style map, latest year by country (or a chosen year), zoom to a country, capital regions labelled, data table and CSV |
| Disparities by country | Every region against 100 (strip plot), richest ÷ poorest ratio, share of population in regions ≤ 75, trend in population-weighted CV with DOSE source breaks marked |
| About, data and method | What this replicates, method, coverage, caveats, sources |

## Method

- **Regions:** first-level administrative regions (ADM1), the closest equivalent of OECD TL2 regions.
- **Indicator:** regional GDP per capita at current prices (local currency) ÷ national GDP per capita × 100. The national figure is the sum of regional GDP divided by the sum of regional population, so regions average exactly to 100.
- **Classes:** ≤ 75; > 75 to 90; > 90 to 110; > 110.
- **Population gaps:** where DOSE gives GDP per capita without population, population is interpolated or, outside reported years, held at a constant share of the country's total (four Brazilian states; Chile's Los Ríos). This affects only the weights of the national average.
- **Coverage notes:** see `output/coverage.csv`.
  - Bogotá D.C. is reported together with Cundinamarca.
  - Lima = Lima Metropolitana + Lima Provincias, and Callao is missing.
  - Ñuble and Presidente Hayes are missing.
  - Argentina's provincial figures are compiled estimates, not official national accounts.
  - Venezuela, Guyana and Suriname have no data.

## Sources

| Data | Source | Licence |
|---|---|---|
| Regional GDP per capita and population | DOSE V2.14 (Wenz, Carr, Kögel, Kotz and Kalkuhl 2023, *Scientific Data* 10, 425), compiled from official regional accounts | CC BY 4.0 |
| Boundaries | Natural Earth 1:10m Admin 1 – States, Provinces | Public domain |
| Reference exercise | OECD (2026), *OECD Regions and Cities at a Glance 2026*, OECD Publishing, Paris | — |

## Pipeline

```
python code/01_boundaries.py   # Natural Earth ADM1 for the 33 LAC countries -> data/processed/adm1_lac.geojson
python code/02_build.py        # DOSE -> regional_index.csv, map_units.geojson, disparity.csv, source_breaks.csv, output/coverage.csv
```

`data/raw/` (DOSE CSV, Natural Earth file) is not committed. Download `DOSE_V2.14.csv` from Zenodo (record 20035157) into `data/raw/dose/`.

## Next steps

- Update to the latest official regional accounts (2022–23) from national statistics offices: IBGE, BCCh, DANE, BCE, INEI, INE Bolivia, BCP. These would also separate Bogotá and add Callao and Ñuble.
- Extend to Mexico, Central America and the Caribbean where official regional accounts exist.
