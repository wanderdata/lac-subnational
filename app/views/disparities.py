import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lib import BANDS, COLORS, INK2, base_layout, load_breaks, load_disparity, load_index, select_year, show

idx = load_index()
dis = load_disparity()
st.markdown("## Disparities by country")
st.caption("Regional GDP per capita relative to the national average (national = 100), current prices. "
           "Each country's latest year in DOSE unless another year is chosen.")
years = sorted(idx["year"].unique(), reverse=True)
mode = st.selectbox("Year", ["Latest available"] + years, index=0)
sel = select_year(idx, mode)
d = dis.merge(sel[["iso3", "year"]].drop_duplicates(), on=["iso3", "year"])

# ---- strip plot
st.markdown("#### Every region against its national average")
order = sel.groupby("country")["index"].max().sort_values().index.tolist()
fig = go.Figure()
for lo, hi, b in [(0, 75, "≤ 75"), (75, 90, "> 75 to 90"), (90, 110, "> 90 to 110"), (110, 1000, "> 110")]:
    fig.add_vrect(x0=max(lo, 25), x1=min(hi, 600), fillcolor=COLORS[b], opacity=0.12, line_width=0, layer="below")
for b in BANDS:
    s = sel[sel["band"] == b]
    fig.add_trace(go.Scatter(x=s["index"], y=s["country"], mode="markers", name=b,
                             marker=dict(color=COLORS[b], size=np.clip(np.sqrt(s["pop"]) / 120, 7, 26),
                                         line=dict(color="white", width=1)),
                             customdata=s[["region_name", "year", "pop"]].values,
                             hovertemplate="<b>%{customdata[0]}</b>, %{y} %{customdata[1]}<br>%{x:.0f} (national = 100)"
                                           "<br>Population %{customdata[2]:,.0f}<extra></extra>"))
fig.add_vline(x=100, line=dict(color=INK2, width=1.5, dash="dot"))
base_layout(fig, height=120 + 48 * len(order), xtitle="GDP per capita, national = 100 (log scale)")
fig.update_xaxes(type="log", tickvals=[30, 50, 75, 90, 100, 110, 150, 200, 300, 500], range=[np.log10(28), np.log10(520)])
fig.update_yaxes(categoryorder="array", categoryarray=order)
show(fig, key="strip")
st.caption("Each dot is a region; size reflects population. Shaded bands are the map classes. A log scale "
           "puts a region at half the national level the same distance from 100 as one at double.")

# ---- indicators
st.markdown("#### Summary indicators")
c1, c2 = st.columns(2)
with c1:
    x = d.sort_values("max_min_ratio")
    f = go.Figure(go.Bar(x=x["max_min_ratio"], y=x["country"], orientation="h", marker=dict(color="#4a78a8", cornerradius=4),
                         customdata=x[["richest", "poorest", "year"]].values, text=[f"{v:.1f}×" for v in x["max_min_ratio"]],
                         textposition="outside", cliponaxis=False,
                         hovertemplate="%{y} %{customdata[2]}: %{x:.1f}×<br>Richest: %{customdata[0]}<br>"
                                       "Poorest: %{customdata[1]}<extra></extra>"))
    base_layout(f, height=380, xtitle="richest ÷ poorest region (GDP per capita)", legend=False)
    st.markdown("**Richest ÷ poorest region**")
    show(f, key="ratio")
with c2:
    x = d.sort_values("pop_share_le75")
    f = go.Figure(go.Bar(x=x["pop_share_le75"], y=x["country"], orientation="h", marker=dict(color=COLORS["≤ 75"], cornerradius=4),
                         text=[f"{v:.0f}%" for v in x["pop_share_le75"]], textposition="outside", cliponaxis=False,
                         hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
    base_layout(f, height=380, xtitle="% of population in regions at or below 75", legend=False)
    st.markdown("**Share of people living in lagging regions (≤ 75)**")
    show(f, key="share")
st.caption("The richest-to-poorest ratio is driven by extremes, often a mining or oil region with few residents. "
           "The population share in regions at or below 75 shows how many people live in lagging regions.")

# ---- trend
st.markdown("#### How disparities have changed")
c = st.multiselect("Countries", sorted(dis["country"].unique()), default=sorted(dis["country"].unique()))
f = go.Figure()
pal = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#a1501b", "#52514e"]
for i, (cn, g) in enumerate(dis[dis["country"].isin(c)].groupby("country")):
    g = g.sort_values("year")
    f.add_trace(go.Scatter(x=g["year"], y=g["cv_weighted"], mode="lines+markers", name=cn,
                           line=dict(color=pal[sorted(dis["country"].unique()).index(cn) % len(pal)], width=2),
                           marker=dict(size=5), hovertemplate=f"{cn} %{{x}}: %{{y:.2f}}<extra></extra>"))
    f.add_annotation(x=g["year"].iloc[-1], y=g["cv_weighted"].iloc[-1], text=cn, showarrow=False, xanchor="left",
                     xshift=6, font=dict(size=11, color=INK2))
br = load_breaks().merge(dis[dis["country"].isin(c)][["iso3", "country", "year", "cv_weighted"]], on=["iso3", "year"])
if len(br):
    f.add_trace(go.Scatter(x=br["year"], y=br["cv_weighted"], mode="markers", name="Source break (DOSE)",
                           marker=dict(symbol="circle-open", size=14, color=INK2, line=dict(width=2)),
                           customdata=br[["country"]].values,
                           hovertemplate="%{customdata[0]} %{x}: change in the underlying data series<extra></extra>"))
base_layout(f, height=460, ytitle="population-weighted coefficient of variation")
f.update_yaxes(gridcolor="#e1e0d9")
show(f, key="trend")
st.caption("Population-weighted coefficient of variation of regional GDP per capita: 0 means every region "
           "equals the national average. Years differ by country, depending on what DOSE covers. Open circles mark "
           "years where DOSE switches to a different underlying series (a new base year or source); a jump there "
           "may partly reflect the switch. Many large moves also follow commodity prices at current prices, for "
           "example Tarija's gas (Bolivia 2015–16) and Antofagasta's copper (Chile).")

with st.expander("Indicator table"):
    st.dataframe(d.round(2), hide_index=True, width="stretch")
