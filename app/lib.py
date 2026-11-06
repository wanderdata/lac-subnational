"""Data loading and map helpers for the lac-subnational Streamlit app."""
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OUT = ROOT / "output"

# OECD Regions and Cities at a Glance classes and colours
BANDS = ["≤ 75", "> 75 to 90", "> 90 to 110", "> 110"]
COLORS = {"≤ 75": "#d9795d", "> 75 to 90": "#e9c25c", "> 90 to 110": "#6aa894", "> 110": "#4a78a8"}
NO_DATA = "#e6e5e0"
INK, INK2, MUTED, GRID = "#14213d", "#52514e", "#898781", "#e1e0d9"
SA_VIEW = dict(lon=(-104, -16), lat=(-56, 13.5))

# Labelled capital regions: label position in the ocean (lon, lat) and which side the text sits on
LABELS = {
    "COL.14_1": ("Bogotá D.C. and<br>Cundinamarca", -84.5, 5.0, "left"),
    "ECU.19_1": ("Pichincha (Quito)", -84.5, -1.5, "left"),
    "PER.16_1": ("Lima", -83.0, -12.5, "left"),
    "CHL.13_1": ("Santiago<br>Metropolitan", -78.5, -33.5, "left"),
    "ARG.5_1": ("Ciudad de<br>Buenos Aires", -53.0, -40.0, "right"),
    "URY.10_1": ("Montevideo", -50.5, -35.0, "right"),
    "BRA.25_1": ("São Paulo", -43.0, -27.5, "right"),
    "BRA.7_1": ("Distrito Federal<br>(Brasília)", -35.0, -12.0, "right"),
}


@st.cache_data
def load_index():
    return pd.read_csv(PROC / "regional_index.csv")


@st.cache_data
def load_disparity():
    return pd.read_csv(PROC / "disparity.csv")


@st.cache_data
def load_breaks():
    f = PROC / "source_breaks.csv"
    return pd.read_csv(f) if f.exists() else pd.DataFrame(columns=["iso3", "year"])


@st.cache_data
def load_coverage():
    return pd.read_csv(OUT / "coverage.csv")


@st.cache_resource
def load_units():
    g = gpd.read_file(PROC / "map_units.geojson")
    return g, json.loads(g.to_json())


@st.cache_resource
def load_context():
    """Neighbouring countries (LAC outside South America) as white background, and country outlines."""
    g = gpd.read_file(PROC / "adm1_lac.geojson")
    countries = g.dissolve("iso3").reset_index()[["iso3", "south_america", "geometry"]]
    return countries, json.loads(countries.to_json())


def select_year(idx, mode):
    """'Latest available' -> each country's latest year; an int -> that year only."""
    if mode == "Latest available":
        return idx[idx["year"] == idx.groupby("iso3")["year"].transform("max")]
    return idx[idx["year"] == mode]


def lac_map(sel, iso_zoom=None, show_labels=True, height=780):
    units, uj = load_units()
    countries, cj = load_context()
    fig = go.Figure()
    # background: other countries in white
    bg = countries[~countries["south_america"]]
    fig.add_trace(go.Choropleth(geojson=cj, locations=bg["iso3"], featureidkey="properties.iso3",
                                z=[0] * len(bg), colorscale=[[0, "#ffffff"], [1, "#ffffff"]], showscale=False,
                                marker_line_color="#b8b7b0", marker_line_width=0.6, hoverinfo="skip"))
    # no-data units
    nd = units[~units["unit_id"].isin(sel["unit_id"])]
    fig.add_trace(go.Choropleth(geojson=uj, locations=nd["unit_id"], featureidkey="properties.unit_id",
                                z=[0] * len(nd), colorscale=[[0, NO_DATA], [1, NO_DATA]], showscale=False,
                                marker_line_color="#ffffff", marker_line_width=0.4, name="No data",
                                customdata=nd[["region", "country"]].values,
                                hovertemplate="<b>%{customdata[0]}</b>, %{customdata[1]}<br>No data<extra></extra>"))
    # one trace per class so the legend reads like the OECD key
    for b in reversed(BANDS):
        s = sel[sel["band"] == b]
        if s.empty:
            continue
        fig.add_trace(go.Choropleth(
            geojson=uj, locations=s["unit_id"], featureidkey="properties.unit_id", z=[1] * len(s),
            colorscale=[[0, COLORS[b]], [1, COLORS[b]]], showscale=False, showlegend=True, name=b,
            marker_line_color="#ffffff", marker_line_width=0.4,
            customdata=s[["region_name", "country", "index", "year", "band"]].values,
            hovertemplate="<b>%{customdata[0]}</b>, %{customdata[1]}<br>GDP per capita: %{customdata[2]:.0f} "
                          "(national = 100)<br>Class: %{customdata[4]} · %{customdata[3]}<extra></extra>"))
    fig.add_trace(go.Scattergeo(lon=[None], lat=[None], mode="markers", name="No data", showlegend=True,
                                marker=dict(symbol="square", size=12, color=NO_DATA, line=dict(color="#b8b7b0", width=1))))
    # national borders on top
    sa = countries[countries["south_america"]]
    fig.add_trace(go.Choropleth(geojson=cj, locations=sa["iso3"], featureidkey="properties.iso3", z=[0] * len(sa),
                                colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale=False,
                                marker_line_color="#1d1d1b", marker_line_width=1.1, hoverinfo="skip"))
    if show_labels and iso_zoom is None:
        cent = units.set_index("unit_id").geometry.representative_point()
        for uid, (txt, lx, ly, side) in LABELS.items():
            if uid not in cent.index or uid not in set(sel["unit_id"]):
                continue
            p = cent[uid]
            fig.add_trace(go.Scattergeo(lon=[lx, p.x], lat=[ly, p.y], mode="lines", line=dict(color="#1d1d1b", width=1),
                                        hoverinfo="skip", showlegend=False))
            fig.add_trace(go.Scattergeo(lon=[lx], lat=[ly], mode="text", text=[f"<b>{txt}</b>"],
                                        textposition=f"middle {side}", textfont=dict(size=12.5, color=INK),
                                        hoverinfo="skip", showlegend=False))
    if iso_zoom:
        b = units[units["iso3"] == iso_zoom].total_bounds
        pad = 1.0
        lon, lat = (b[0] - pad, b[2] + pad), (b[1] - pad, b[3] + pad)
    else:
        lon, lat = SA_VIEW["lon"], SA_VIEW["lat"]
    fig.update_geos(projection_type="mercator", lonaxis_range=list(lon), lataxis_range=list(lat),
                    showcountries=False, showcoastlines=False, showland=False, showocean=False,
                    showframe=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)",
                      legend=dict(title=dict(text="<b>GDP per capita, current prices</b><br>National = 100",
                                              font=dict(size=13, color=INK)),
                                  x=0.99, xanchor="right", y=0.99, yanchor="top", bgcolor="rgba(250,250,248,0.95)",
                                  bordercolor="#898781", borderwidth=1, font=dict(size=13, color=INK),
                                  traceorder="normal"),
                      font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif"))
    return fig


def base_layout(fig, height=420, xtitle=None, ytitle=None, legend=True):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="rgba(0,0,0,0)",
                      paper_bgcolor="rgba(0,0,0,0)", showlegend=legend,
                      font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", size=12, color=INK2),
                      legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, title=None))
    fig.update_xaxes(title=xtitle, gridcolor=GRID, zeroline=False, linecolor="#c3c2b7")
    fig.update_yaxes(title=ytitle, gridcolor="rgba(0,0,0,0)", zeroline=False)
    return fig


def show(fig, key=None):
    st.plotly_chart(fig, width="stretch", key=key,
                    config={"displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d"],
                            "toImageButtonOptions": {"format": "png", "scale": 2, "filename": "south_america_regional_gdp_pc"}})
