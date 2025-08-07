import pandas as pd
import pydeck as pdk
import streamlit as st

HEX_PALETTE = [
    "#4E79A7", "#F28E2B", "#59A14F", "#E15759",
    "#499894", "#B07AA1", "#FF9DA7", "#9C755F",
    "#BAB0AB", "#A0CBE8"
]

def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

def _build_deck(layers):
    view_state = pdk.ViewState(latitude=39.5, longitude=-98.35, zoom=3)
    return pdk.Deck(layers=layers, initial_view_state=view_state, map_style="mapbox://styles/mapbox/light-v10")

def plot_network(data: pd.DataFrame, centres, *, colours):
    """Plot customer points and edges with per-warehouse colours.

    Parameters
    ----------
    data : DataFrame with columns cust_lat, cust_lon, wh_lat, wh_lon, Warehouse
    centres : list[[lon, lat]]
    colours : list[str] hex colours per warehouse
    """
    st.subheader("Network Map")

    rgb_cols = [_hex_to_rgb(c) for c in colours]

    # Warehouse layer
    wh_df = pd.DataFrame(centres, columns=["Lon", "Lat"])
    wh_df[["r", "g", "b"]] = rgb_cols

    wh_layer = pdk.Layer(
        "ScatterplotLayer",
        wh_df,
        get_position="[Lon,Lat]",
        get_fill_color="[r,g,b]",
        get_radius=40000,
        opacity=0.9,
    )

    # Customer layer
    cust_layer = pdk.Layer(
        "ScatterplotLayer",
        data.rename(columns={"cust_lat": "Lat", "cust_lon": "Lon"}),
        get_position="[Lon,Lat]",
        get_fill_color="[0,128,255]",
        get_radius=12000,
        opacity=0.6,
    )

    # Edge lines
    edges = []
    for row in data.itertuples():
        idx = int(row.Warehouse)
        color = rgb_cols[idx] + [120]
        edges.append({
            "from": [row.cust_lon, row.cust_lat],
            "to": centres[idx],
            "color": color
        })

    edge_layer = pdk.Layer(
        "LineLayer",
        edges,
        get_source_position="from",
        get_target_position="to",
        get_color="color",
        get_width=2,
    )

    st.pydeck_chart(_build_deck([edge_layer, cust_layer, wh_layer]))
