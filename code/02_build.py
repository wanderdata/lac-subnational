"""Regional GDP per capita relative to the national average (national = 100), South America.

    python code/02_build.py

Replicates, for South America, the indicator mapped in OECD *Regions and Cities at
a Glance 2026* ("GDP per capita, current prices, national = 100") using DOSE V2.14.

Steps
  1. Extract DOSE for the South American countries it covers (2000 onwards).
  2. Fill missing regional population where DOSE reports GDP per capita without
     population (see impute_pop); flagged in `pop_imputed`.
  3. National GDP per capita = sum over regions of (GDP per capita × population)
     / sum of population, so regions average exactly to 100 in each country-year.
     Only country-years in which every DOSE region of that country has GDP per
     capita are kept (no partial countries).
  4. Index = regional / national × 100; OECD classes.
  5. Match DOSE regions to Natural Earth polygons (crosswalk below), dissolving
     polygons where DOSE reports a merged unit.

Outputs (data/processed/ and output/)
  regional_index.csv      iso3, unit_id, region, year, gdp_pc_lcu, pop, pop_imputed, national_gdp_pc, index, band
  map_units.geojson       one polygon per mapping unit (South America), incl. "no data" units
  disparity.csv           per country-year: max/min ratio, population-weighted CV, share of population ≤ 75
  coverage.csv            per country: regions, years, latest year, notes
  source_breaks.csv       country-years where DOSE flags a change in the underlying series
"""
import re
import unicodedata

import geopandas as gpd
import numpy as np
import pandas as pd

from config import BANDS, COUNTRIES, OUTPUT, PROCESSED, RAW, SOUTH_AMERICA

DOSE = RAW / "dose" / "DOSE_V2.14.csv"
START = 2000

# Natural Earth polygons that DOSE reports as one unit: {iso3: {NE name: DOSE region}}
MERGE = {
    "COL": {"Bogota": "Cundinamarca"},          # DOSE Cundinamarca includes Bogotá D.C. (population ~10.9 m)
    "PER": {"Lima Province": "Lima"},           # DOSE Lima = Lima Metropolitana + Lima Provincias (Callao excluded)
}
# Name differences that normalisation does not resolve: {iso3: {DOSE region: NE name}}
ALIAS = {
    "BOL": {"Beni": "El Beni"},
    "CHL": {"Aisen Of General Carlos Ibanez Del Campo": "Aisén del General Carlos Ibáñez del Campo",
            "Araucania": "La Araucanía", "Bernardo O Higgins": "Libertador General Bernardo O'Higgins",
            "Bio Bio": "Bío-Bío", "Magallanes": "Magallanes y Antártica Chilena",
            "Rms Metropolitan Region": "Región Metropolitana de Santiago"},
    "PER": {"Moquequa": "Moquegua"},
}
# Polygons with no DOSE data although the country is covered (shown as "no data")
NOTES = {
    "ARG": "Provincial GDP is not part of Argentina's official national accounts; DOSE compiles provincial estimates.",
    "BRA": "Latest year 2017. Population for Mato Grosso do Sul, Rio de Janeiro, Rio Grande do Norte and Rio Grande do Sul imputed (only 2010 reported in DOSE).",
    "CHL": "Ñuble (created 2018) is not in DOSE; Biobío is the post-2018 region. Los Ríos population imputed after 2015.",
    "COL": "Bogotá D.C. is reported together with Cundinamarca.",
    "PER": "Lima = Lima Metropolitana + Lima Provincias. Callao is not in DOSE.",
    "PRY": "Latest complete year 2017; Presidente Hayes is not in DOSE.",
    "URY": "Latest year 2014.",
}
SA_NO_DATA = {"GUY": "Guyana", "SUR": "Suriname", "VEN": "Venezuela"}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z ]", " ", s)
    s = re.sub(r"\b(region|de|del|la|los|las|y|of|the|provincia|departamento)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def band(x):
    for lo, hi, lab in BANDS:
        if lo < x <= hi:
            return lab
    return None


def impute_pop(x):
    """x: one country's DOSE rows. Where a region lacks population in a year,
    interpolate linearly between its reported years; outside them, carry its
    nearest reported value forward/backward scaled by the growth of the
    country's other regions (i.e. constant population share)."""
    p = x.pivot_table(index="year", columns="region", values="pop")
    years = range(int(x["year"].min()), int(x["year"].max()) + 1)
    p = p.reindex(years)
    imputed = p.isna()
    filled = p.interpolate(limit_area="inside")
    for r in filled.columns:
        if filled[r].isna().any() and filled[r].notna().any():
            others = filled.drop(columns=r).sum(axis=1, min_count=1)
            known = filled[r].dropna()
            for y in filled.index[filled[r].isna()]:
                y0 = min(known.index, key=lambda k: abs(k - y))
                if pd.notna(others.get(y)) and pd.notna(others.get(y0)) and others[y0] > 0:
                    filled.loc[y, r] = known[y0] * others[y] / others[y0]
    out = filled.stack().rename("pop").reset_index()
    imp = imputed.stack().rename("pop_imputed").reset_index()
    return out.merge(imp, on=["year", "region"])


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(DOSE, low_memory=False)
    d = d[d["GID_0"].isin(SOUTH_AMERICA)]
    covered = sorted(d["GID_0"].unique())

    # ---- 1–4: index
    rows = []
    for c in covered:
        x = d[d["GID_0"] == c]
        pop = impute_pop(x)
        x = x[x["year"] >= START][["region", "GID_1", "year", "grp_pc_lcu"]].merge(pop, on=["year", "region"], how="left")
        n_regions = x.groupby("year")["region"].nunique()
        full_n = n_regions.max()
        for y, g in x.groupby("year"):
            g = g.dropna(subset=["grp_pc_lcu", "pop"])
            # keep only years covering the country's full DOSE region set at that time
            if len(g) < n_regions.loc[y] or len(g) < full_n - 1:
                continue
            nat = (g["grp_pc_lcu"] * g["pop"]).sum() / g["pop"].sum()
            g = g.assign(iso3=c, national_gdp_pc=nat, index=100 * g["grp_pc_lcu"] / nat, n_regions=len(g))
            rows.append(g)
    idx = pd.concat(rows, ignore_index=True)
    idx["band"] = idx["index"].map(band)
    idx["pop_imputed"] = idx["pop_imputed"].fillna(False).astype(bool)

    # ---- 5: crosswalk to Natural Earth
    ne = gpd.read_file(PROCESSED / "adm1_lac.geojson")
    ne = ne[ne["south_america"]].copy()
    ne["key"] = ne["name"].map(norm)
    cw = []
    for c in covered:
        regs = idx.loc[idx["iso3"] == c, ["region", "GID_1"]].drop_duplicates("region")
        sub = ne[ne["iso3"] == c]
        for r, gid in regs.itertuples(index=False):
            target = ALIAS.get(c, {}).get(r, r)
            hit = sub[sub["key"] == norm(target)]
            if hit.empty:
                raise ValueError(f"{c}: no Natural Earth match for DOSE region '{r}'")
            cw.append({"iso3": c, "region": r, "GID_1": gid, "ne_id": int(hit["ne_id"].iloc[0])})
        for ne_name, r in MERGE.get(c, {}).items():
            hit = sub[sub["name"] == ne_name]
            cw.append({"iso3": c, "region": r, "GID_1": regs.set_index("region").loc[r, "GID_1"],
                       "ne_id": int(hit["ne_id"].iloc[0])})
    cw = pd.DataFrame(cw)
    cw["unit_id"] = cw["GID_1"]
    cw.to_csv(PROCESSED / "crosswalk_dose_ne.csv", index=False)

    # map units: matched polygons dissolved by DOSE unit; unmatched polygons kept as "no data"
    m = ne.merge(cw[["ne_id", "unit_id", "region"]], on="ne_id", how="left")
    m["unit_id"] = m["unit_id"].fillna("NE." + m["ne_id"].astype(int).astype(str))
    m["region"] = m["region"].fillna(m["name"])
    names = m.groupby("unit_id")["name"].apply(lambda s: " + ".join(sorted(s)))
    units = m.dissolve(by="unit_id", aggfunc={"iso3": "first", "region": "first"}).reset_index()
    units["ne_names"] = units["unit_id"].map(names)
    units["country"] = units["iso3"].map(COUNTRIES)
    units["has_data"] = units["unit_id"].isin(idx["GID_1"])
    units[["unit_id", "iso3", "country", "region", "ne_names", "has_data", "geometry"]].to_file(
        PROCESSED / "map_units.geojson", driver="GeoJSON", COORDINATE_PRECISION=4)

    # display names: DOSE names tidied, with merged units spelled out
    disp = {"Cundinamarca": "Bogotá D.C. and Cundinamarca", "Lima": "Lima (Metropolitana and Provincias)"}
    nice = dict(zip(cw["region"], cw["region"]))
    ne_name_of = cw.drop_duplicates("region").merge(ne[["ne_id", "name"]], on="ne_id").set_index("region")["name"]
    idx["region_name"] = idx["region"].map(lambda r: disp.get(r, ne_name_of.get(r, r)))
    idx = idx.rename(columns={"GID_1": "unit_id"})
    idx["country"] = idx["iso3"].map(COUNTRIES)
    cols = ["iso3", "country", "unit_id", "region", "region_name", "year", "grp_pc_lcu", "pop", "pop_imputed",
            "national_gdp_pc", "index", "band", "n_regions"]
    idx[cols].sort_values(["iso3", "year", "unit_id"]).to_csv(PROCESSED / "regional_index.csv", index=False)

    # ---- disparity indicators
    dis = []
    for (c, y), g in idx.groupby(["iso3", "year"]):
        w = g["pop"] / g["pop"].sum()
        mean = (w * g["index"]).sum()
        dis.append({"iso3": c, "country": COUNTRIES[c], "year": y, "n_regions": len(g),
                    "max_min_ratio": g["index"].max() / g["index"].min(),
                    "richest": g.loc[g["index"].idxmax(), "region_name"],
                    "poorest": g.loc[g["index"].idxmin(), "region_name"],
                    "cv_weighted": np.sqrt((w * (g["index"] - mean) ** 2).sum()) / mean,
                    "pop_share_le75": 100 * w[g["index"] <= 75].sum(),
                    "pop_share_gt110": 100 * w[g["index"] > 110].sum()})
    dis = pd.DataFrame(dis)
    dis.to_csv(PROCESSED / "disparity.csv", index=False)

    # ---- source breaks flagged by DOSE (StructChange != 0): years where the underlying series changes
    br = d[(d["year"] >= START) & (d["StructChange"].fillna(0) != 0)].groupby(["GID_0", "year"]).size().reset_index()
    br = br.rename(columns={"GID_0": "iso3", 0: "regions_flagged"})
    br = br.merge(idx[["iso3", "year"]].drop_duplicates(), on=["iso3", "year"])
    br.to_csv(PROCESSED / "source_breaks.csv", index=False)

    # ---- coverage
    cov = []
    for c in SOUTH_AMERICA:
        g = idx[idx["iso3"] == c]
        if g.empty:
            cov.append({"iso3": c, "country": COUNTRIES[c], "regions": 0, "years": "—", "latest": None,
                        "note": "Not in DOSE (no official regional accounts compiled)."})
            continue
        last = int(g["year"].max())
        nmap = int((ne["iso3"] == c).sum())
        cov.append({"iso3": c, "country": COUNTRIES[c], "regions": int(g[g["year"] == last]["unit_id"].nunique()),
                    "map_polygons": nmap, "years": f"{int(g['year'].min())}–{last} ({g['year'].nunique()} years)",
                    "latest": last, "pop_imputed_latest": bool(g[g["year"] == last]["pop_imputed"].any()),
                    "note": NOTES.get(c, "")})
    cov = pd.DataFrame(cov)
    cov.to_csv(OUTPUT / "coverage.csv", index=False)
    print(cov.to_string())
    latest = idx.loc[idx.groupby("iso3")["year"].transform("max") == idx["year"]]
    print("\nCheck — population-weighted mean of index by country (must be 100):")
    print(latest.groupby("iso3").apply(lambda g: (g["index"] * g["pop"]).sum() / g["pop"].sum(), include_groups=False).round(6).to_dict())
    print("\nLatest-year bands:", latest["band"].value_counts().to_dict())


if __name__ == "__main__":
    main()
