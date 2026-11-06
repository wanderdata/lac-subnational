# lac-subnational

Subnational economic disparities in Latin America and the Caribbean: GDP per capita of each first-level region (state, department, province) relative to its national average (national = 100). This follows the OECD *Regions and Cities at a Glance* map for Europe.

Paul Wander, Division of Production, Productivity and Management, UN-ECLAC.

**Status (2026-11-06):** boundaries in place; waiting for the regional GDP data (DOSE). Streamlit page to follow.

## Method

- **Unit:** first-level administrative regions (ADM1), the closest LAC equivalent of OECD TL2 regions.
- **Indicator:** regional GDP per capita at current prices ÷ national GDP per capita × 100. National GDP per capita = sum of regional GDP ÷ sum of regional population, so regions average exactly to 100 in each country.
- **Classes:** ≤ 75; > 75 to 90; > 90 to 110; > 110.
- **Countries:** the 33 LAC member states of ECLAC. Countries without official regional accounts are shown as "no data".

## Sources

| Data | Source | Licence |
|---|---|---|
| Regional GDP and population | DOSE V2.14, *Global data set of reported sub-national economic output* (Wenz et al. 2023, *Scientific Data*), compiled from official regional accounts | CC BY 4.0 |
| Boundaries | geoBoundaries gbOpen ADM1, simplified (Runfola et al. 2020) | CC BY 4.0 |

## Layout

| Path | Contents | Committed |
|---|---|---|
| `code/` | Pipeline scripts (`01_boundaries.py`, …) | yes |
| `data/raw/` | Downloads as received | no |
| `data/processed/` | `adm1_lac.geojson` (553 regions, 33 countries), matching index, panels | yes |
| `output/` | Generated tables and checks | yes |
| `app/` | Streamlit page | yes |
