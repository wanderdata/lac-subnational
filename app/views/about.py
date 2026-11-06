import streamlit as st

from lib import load_coverage

st.markdown("## About this page")
st.markdown(
    """
**What this is.** This repeats, for South America, the exercise behind the OECD map *"Across Europe, regions
within the same country are experiencing very different economic outcomes"*, published in **OECD Regions and
Cities at a Glance 2026**. The OECD map shows each region's GDP per capita at current prices relative to its
own country's average (national = 100), in four classes: ≤ 75, > 75 to 90, > 90 to 110, and > 110. Here the
same indicator, the same classes and a similar colour scheme are applied to the first-level regions of South
American countries. Nothing is added to the OECD method; only the data source and the geography change.

**Why South America only.** Regional GDP compiled from official sources is available for 9 of the 12 South
American countries, but for few countries in Central America and the Caribbean (only Mexico and Panama, to
2019). Venezuela, Guyana and Suriname have no regional accounts in the source and are shown as "no data".
"""
)

st.markdown("### Data and method")
st.markdown(
    """
- **Regions:** first-level administrative regions (states, departments, provinces, regions), the closest
  equivalent of the OECD's large (TL2) regions.
- **GDP per capita:** regional GDP per capita in local currency at current prices, from **DOSE V2.14**, a
  compilation of officially reported subnational economic output.
- **National = 100:** the national average is the population-weighted mean of the regions' GDP per capita
  (total regional GDP ÷ total population), so regions average exactly to 100 in each country and year.
- **Year:** the latest year available for each country (2014–2019), as in the OECD map. Other years can be selected.
- **Population gaps:** where DOSE reports GDP per capita without population, population is interpolated
  between reported years or, outside them, held at a constant share of the country's total. This affects four
  Brazilian states and Chile's Los Ríos. It changes only the weights of the national average, not the regions'
  GDP per capita.
"""
)

st.markdown("### Coverage and notes by country")
cov = load_coverage()
cols = [c for c in ["country", "regions", "years", "latest", "note"] if c in cov.columns]
st.dataframe(cov[cols].rename(columns={"regions": "regions with data", "latest": "latest year"}),
             hide_index=True, width="stretch")

st.markdown("### Caveats")
st.markdown(
    """
- **Different years.** Countries' latest years differ (Uruguay 2014; Brazil and Paraguay 2017; others 2019),
  and none are post-pandemic. National statistics offices now publish more recent regional accounts for most of
  these countries; updating them is the next step.
- **Mining and oil regions** (Orellana in Ecuador, Antofagasta in Chile, Moquegua in Peru, Tierra del Fuego and
  Santa Cruz in Argentina, Casanare in Colombia) have very high GDP per capita that largely accrues outside the
  region.
- **Merged units:** Bogotá D.C. is reported with Cundinamarca, so Colombia's capital region does not stand out
  as it would on its own. Lima covers Lima Metropolitana and Lima Provincias; Callao is missing.
- **Argentina:** provincial GDP is not part of the country's official national accounts; DOSE compiles
  provincial estimates.
"""
)

st.markdown("### Sources")
st.markdown(
    """
- OECD (2026), *OECD Regions and Cities at a Glance 2026*, OECD Publishing, Paris. Map: "Across Europe, regions
  within the same country are experiencing very different economic outcomes" (GDP per capita, current prices,
  national = 100).
- Wenz, L., Carr, R. D., Kögel, N., Kotz, M. and Kalkuhl, M. (2023), "DOSE – Global data set of reported
  sub-national economic output", *Scientific Data* 10, 425. Data: DOSE V2.14, Zenodo.
- Natural Earth, *Admin 1 – States, Provinces* (1:10m), public domain.

Code and data: GitHub repository `wanderdata/lac-subnational`.
"""
)

st.divider()
st.markdown("Prepared by **Paul Wander**, Division of Production, Productivity and Management, UN-ECLAC.")
