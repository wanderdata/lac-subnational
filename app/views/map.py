import streamlit as st

from lib import BANDS, load_coverage, load_index, lac_map, select_year, show

idx = load_index()
st.markdown("## Across South America, regions within the same country are experiencing very different economic outcomes")
st.markdown("#### GDP per capita, current prices · national = 100")

c1, c2, c3 = st.columns([1.2, 1.2, 1])
years = sorted(idx["year"].unique(), reverse=True)
mode = c1.selectbox("Year", ["Latest available"] + years, index=0,
                    help="'Latest available' uses each country's most recent year in DOSE (2014–2019), as the OECD "
                         "map uses the latest year per country.")
countries = sorted(idx["country"].unique())
zoom = c2.selectbox("Zoom to", ["South America"] + countries)
labels = c3.toggle("Label capital regions", value=True)

sel = select_year(idx, mode)
iso = None if zoom == "South America" else idx.loc[idx["country"] == zoom, "iso3"].iloc[0]
show(lac_map(sel, iso_zoom=iso, show_labels=labels, height=820 if iso is None else 680), key="map")

yrs = sel.groupby("country")["year"].first()
st.caption("Year shown: " + "; ".join(f"{c} {y}" for c, y in yrs.items()) +
           ". Grey: no data (Venezuela, Guyana and Suriname have no regional accounts in DOSE; also Callao, Ñuble "
           "and Presidente Hayes). Colombia's Bogotá D.C. is reported together with Cundinamarca, and Peru's Lima "
           "covers Lima Metropolitana and Lima Provincias. Source: DOSE V2.14 (Wenz et al. 2023); boundaries: "
           "Natural Earth. Same exercise as the OECD map in *Regions and Cities at a Glance 2026*; see *About*.")

with st.expander("Regions and values"):
    t = sel[["country", "region_name", "year", "index", "band", "pop_imputed"]].sort_values(["country", "index"],
                                                                                              ascending=[True, False])
    t = t.rename(columns={"region_name": "region", "index": "GDP per capita (national = 100)", "band": "class",
                          "pop_imputed": "population imputed"})
    st.dataframe(t.round(1), hide_index=True, width="stretch")
    st.download_button("Download CSV", t.to_csv(index=False).encode("utf-8"), "south_america_regional_gdp_pc.csv",
                       "text/csv")
