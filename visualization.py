import pandas as pd
import pydeck as pdk
import streamlit as st

HEX_PALETTE = [
    "#4E79A7", "#A0CBE8", "#F28E2B", "#FFBE7D",
    "#59A14F", "#8CD17D", "#B6992D", "#F1CE63",
    "#499894", "#86BCB6", "#E15759", "#FF9D9A",
    "#79706E", "#BAB0AC", "#D37295", "#FABFD2",
    "#B07AA1", "#D4A6C8", "#9D7660", "#D7B5A6",
]

def _hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

def _build_deck(layers):
    view_state = pdk.ViewState(latitude=39.5, longitude=-98.35, zoom=3)
    return pdk.Deck(layers=layers, initial_view_state=view_state, map_style="mapbox://styles/mapbox/light-v10")

def plot_network(stores: pd.DataFrame, centres, *, colours):
    """Plot network with per-warehouse colours.

    Parameters
    ----------
    stores : pd.DataFrame
        Must contain Longitude, Latitude, and Warehouse columns.
    centres : list[list[float,float]]
        Warehouse lon/lat pairs in the same order as `colours`.
    colours : list[str]
        Hex colours per warehouse.
    """
    st.subheader("Network Map")

    # Convert hex to rgb+a
    wh_rgbs = [_hex_to_rgb(c) for c in colours]

    # Warehouse scatter layer
    wh_df = pd.DataFrame(centres, columns=["Lon", "Lat"])
    wh_df[["r", "g", "b"]] = wh_rgbs

    wh_layer = pdk.Layer(
        "ScatterplotLayer",
        wh_df,
        get_position="[Lon,Lat]",
        get_fill_color="[r, g, b]",
        get_radius=40000,
        opacity=0.9,
    )

    # Store layer
    store_layer = pdk.Layer(
        "ScatterplotLayer",
        stores,
        get_position="[Longitude,Latitude]",
        get_fill_color="[0, 128, 255]",
        get_radius=12000,
        opacity=0.6,
    )

    # Edge lines
    edges = []
    for row in stores.itertuples():
        wh_idx = int(row.Warehouse)
        edges.append({
            "from": [row.Longitude, row.Latitude],
            "to": centres[wh_idx],
            "color": wh_rgbs[wh_idx] + [120]
        })

    line_layer = pdk.Layer(
        "LineLayer",
        edges,
        get_source_position="from",
        get_target_position="to",
        get_color="color",
        get_width=2,
    )

    deck = _build_deck([line_layer, store_layer, wh_layer])
    st.pydeck_chart(deck)
