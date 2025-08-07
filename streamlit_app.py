
import streamlit as st
import pandas as pd
from visualization import plot_network, HEX_PALETTE

st.set_page_config(page_title="Customer ➜ Warehouse Visualizer", layout="wide")
st.title("📍 Customer to Warehouse Connection Visualizer")

st.markdown(
    """Upload a CSV where:

    * **Column A** – Customer latitude  
    * **Column B** – Customer longitude  
    * **Column C** – Warehouse latitude  
    * **Column D** – Warehouse longitude  

The header row is optional – the app ignores it.

    The map style, cost model and all other existing features are **unchanged**.
    The only new capability is that *you* decide the colour assigned to every
    warehouse (and all its outgoing customer lines)."""
)

up_file = st.file_uploader("Choose a CSV file", type=["csv"])

@st.cache_data(show_spinner=False)
def load_df(file):
    df = pd.read_csv(file, header=None, names=["cust_lat", "cust_lon", "wh_lat", "wh_lon"])
    return df

def hex_to_rgb(hex_str: str):
    hex_str = hex_str.lstrip('#')
    return [int(hex_str[i:i+2], 16) for i in (0, 2, 4)]

if up_file is not None:
    df = load_df(up_file)

    # Build list of unique warehouses preserving order
    seen = {}
    centers = []
    for lon, lat in zip(df["wh_lon"], df["wh_lat"]):
        key = (round(lon, 6), round(lat, 6))
        if key not in seen:
            seen[key] = len(centers)
            centers.append([lon, lat])

    center_lookup = seen  # maps (lon,lat) -> warehouse index

    stores = pd.DataFrame({
        "Longitude": df["cust_lon"],
        "Latitude": df["cust_lat"],
        "Warehouse": [center_lookup[(round(lon, 6), round(lat, 6))]
                        for lon, lat in zip(df["wh_lon"], df["wh_lat"])]
    })

    st.sidebar.subheader("🎨 Warehouse colours")

    colour_list = []
    for idx, (lon, lat) in enumerate(centers):
        default_hex = HEX_PALETTE[idx % len(HEX_PALETTE)]
        hex_colour = st.sidebar.color_picker(f"Warehouse {idx+1} ({lat:.2f}, {lon:.2f})", default_hex)
        colour_list.append(hex_to_rgb(hex_colour))

    plot_network(stores, centers, colours=colour_list)

    st.success(f"Displayed {len(stores):,} customer points across {len(centers)} warehouse locations.")
