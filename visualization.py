
import os
from typing import List, Sequence
import streamlit as st
import pandas as pd
import pydeck as pdk

# ─────────── Map provider / token handling ────────────
_MAPBOX_TOKEN = os.getenv("MAPBOX_API_KEY")
if not _MAPBOX_TOKEN:
    try:
        _MAPBOX_TOKEN = st.secrets["MAPBOX_API_KEY"]  # type: ignore[attr-defined]
    except Exception:
        _MAPBOX_TOKEN = None
else:
    pdk.settings.mapbox_api_key = _MAPBOX_TOKEN

# Default colour palette (10‑colour Tableau)
_COL = [
    [31, 119, 180],
    [255, 127, 14],
    [44, 160, 44],
    [214, 39, 40],
    [148, 103, 189],
    [140, 86, 75],
    [227, 119, 194],
    [127, 127, 127],
    [188, 189, 34],
    [23, 190, 207],
]
HEX_PALETTE = ["#%02x%02x%02x" % tuple(c) for c in _COL]

def _c(i):  # Fallback colour
    return _COL[i % len(_COL)]

def _build_deck(layers):
    view_state = pdk.ViewState(latitude=39, longitude=-98, zoom=3.5)
    if _MAPBOX_TOKEN:
        return pdk.Deck(layers=layers, initial_view_state=view_state,
                        map_style="mapbox://styles/mapbox/light-v10")
    return pdk.Deck(layers=layers, initial_view_state=view_state, map_style="light")

def plot_network(stores: pd.DataFrame,
                 centers: Sequence[Sequence[float]],
                 *,
                 colours: List[List[int]] | None = None) -> None:
    """Render the outbound network on an interactive map.

    Parameters
    ----------
    stores : DataFrame
        Must include Longitude, Latitude and Warehouse columns.
    centers : list-like
        [[lon, lat], …] coordinates of warehouses.
    colours : list[list[int]], optional
        RGB colours (0‑255) for each warehouse. When *None*,
        falls back to the default palette.
    """
    st.subheader("Network Map")

    cen_df = pd.DataFrame(centers, columns=["Lon", "Lat"])

    if colours is None:
        colours = [_c(i) for i in range(len(cen_df))]
    if len(colours) < len(cen_df):
        # pad if user provided fewer colours
        colours += [_c(i) for i in range(len(colours), len(cen_df))]

    cen_df[["r", "g", "b"]] = colours

    # Warehouses layer
    wh_layer = pdk.Layer(
        "ScatterplotLayer",
        cen_df,
        get_position="[Lon,Lat]",
        get_fill_color="[r,g,b]",
        get_radius=35000,
        opacity=0.9,
    )

    # Edges Store→Warehouse
    edges = []
    for r in stores.itertuples():
        col = colours[int(r.Warehouse)] + [120]  # alpha
        wh_row = cen_df.iloc[int(r.Warehouse)]
        edges.append({
            "f": [r.Longitude, r.Latitude],
            "t": [wh_row.Lon, wh_row.Lat],
            "col": col,
        })

    line_layer = pdk.Layer(
        "LineLayer",
        edges,
        get_source_position="f",
        get_target_position="t",
        get_color="col",
        get_width=2,
    )

    # Customer dots layer
    store_layer = pdk.Layer(
        "ScatterplotLayer",
        stores,
        get_position="[Longitude,Latitude]",
        get_fill_color="[0,128,255]",
        get_radius=12000,
        opacity=0.6,
    )

    deck = _build_deck([line_layer, store_layer, wh_layer])
    st.pydeck_chart(deck)
