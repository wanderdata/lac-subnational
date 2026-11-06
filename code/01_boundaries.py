"""First-level administrative boundaries (ADM1) for the 33 LAC countries.

    python code/01_boundaries.py

Source: Natural Earth 1:10m admin-1 states and provinces (public domain),
from the Natural Earth GitHub repository. Natural Earth is used rather than
geoBoundaries because its borders are consistent across countries and its
Argentina layer is complete (geoBoundaries' simplified file lacks Entre Ríos).

Writes
    data/raw/natural_earth/ne_10m_admin_1_states_provinces.geojson   (not committed)
    data/processed/adm1_lac.geojson     (33 countries, simplified for web maps)
    data/processed/adm1_lac_index.csv   (iso3, ne_id, name, iso_3166_2, south_america)
"""
import urllib.request

import geopandas as gpd

from config import COUNTRIES, PROCESSED, RAW, SOUTH_AMERICA

URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
       "ne_10m_admin_1_states_provinces.geojson")
TOLERANCE = 0.01  # degrees (~1 km)


def main():
    src = RAW / "natural_earth" / "ne_10m_admin_1_states_provinces.geojson"
    src.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        urllib.request.urlretrieve(URL, src)
    g = gpd.read_file(src)
    g = g[g["adm0_a3"].isin(COUNTRIES)].copy()
    g = g.rename(columns={"adm0_a3": "iso3"})
    g["name"] = g["name"].fillna("(unnamed)")
    g["south_america"] = g["iso3"].isin(SOUTH_AMERICA)
    g = g[["iso3", "ne_id", "name", "iso_3166_2", "south_america", "geometry"]].to_crs(4326)
    g["geometry"] = g.geometry.simplify(TOLERANCE, preserve_topology=True).make_valid()
    g.to_file(PROCESSED / "adm1_lac.geojson", driver="GeoJSON", COORDINATE_PRECISION=4)
    g.drop(columns="geometry").to_csv(PROCESSED / "adm1_lac_index.csv", index=False)
    print(f"{len(g)} regions in {g['iso3'].nunique()} countries "
          f"({g['south_america'].sum()} in South America)")


if __name__ == "__main__":
    main()
