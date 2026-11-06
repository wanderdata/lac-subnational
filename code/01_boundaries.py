"""First-level administrative boundaries (ADM1) for the 33 LAC countries.

    python code/01_boundaries.py

Source: geoBoundaries gbOpen, simplified ADM1 (Runfola et al. 2020, CC BY 4.0),
downloaded from the project's GitHub release data. Writes
    data/raw/boundaries/<ISO3>.geojson            (as downloaded, not committed)
    data/processed/adm1_lac.geojson               (all countries, further simplified for web maps)
    data/processed/adm1_lac_index.csv             (iso3, shapeID, shapeName, shapeISO; for matching)
"""
import time
import urllib.request

import geopandas as gpd
import pandas as pd

from config import COUNTRIES, PROCESSED, RAW

URL = ("https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/main/releaseData/"
       "gbOpen/{c}/ADM1/geoBoundaries-{c}-ADM1_simplified.geojson")
TOLERANCE = 0.01  # degrees (~1 km); enough for a regional map


def fetch(c, dest):
    for attempt in range(3):
        try:
            urllib.request.urlretrieve(URL.format(c=c), dest)
            return True
        except Exception as e:
            print(f"  {c}: attempt {attempt+1} failed ({e})")
            time.sleep(5)
    return False


def main():
    bdir = RAW / "boundaries"
    bdir.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    parts = []
    for c in COUNTRIES:
        f = bdir / f"{c}.geojson"
        if not f.exists() and not fetch(c, f):
            print(f"[fail] {c}")
            continue
        g = gpd.read_file(f)
        g["iso3"] = c
        parts.append(g[["iso3", "shapeID", "shapeName", "shapeISO", "geometry"]])
        print(f"[ok  ] {c}: {len(g)} regions")
    gdf = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=parts[0].crs).to_crs(4326)
    gdf["geometry"] = gdf.geometry.simplify(TOLERANCE, preserve_topology=True).make_valid()
    gdf.to_file(PROCESSED / "adm1_lac.geojson", driver="GeoJSON", COORDINATE_PRECISION=4)
    gdf.drop(columns="geometry").to_csv(PROCESSED / "adm1_lac_index.csv", index=False)
    print(f"{len(gdf)} regions in {gdf['iso3'].nunique()} countries")


if __name__ == "__main__":
    main()
