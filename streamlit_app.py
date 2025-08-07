import streamlit as st
import pandas as pd
from visualization import plot_network, HEX_PALETTE

st.set_page_config(page_title="Warehouse Network Mapper", layout="wide")
st.title("Warehouse Network Mapper")

uploaded = st.file_uploader("Upload CSV (CustomerLat, CustomerLon, WarehouseLat, WarehouseLon)", type=["csv"])

st.sidebar.header("Controls")
custom_toggle = st.sidebar.toggle(
    "Pick custom colours per warehouse",
    value=True,
    help="Toggle off to show all warehouses and edges in a neutral grey.",
)

def load_csv(file) -> pd.DataFrame:
    """Load CSV that can optionally have a header row.

    Expected column order:
    A: customer latitude
    B: customer longitude
    C: warehouse latitude
    D: warehouse longitude
    """
    # Ensure buffer at start
    file.seek(0)
    try:
        raw = pd.read_csv(file, header=None)
    except pd.errors.EmptyDataError:
        st.error("Uploaded file appears to be empty.")
        return pd.DataFrame()

    if raw.shape[1] < 4:
        st.error("CSV must contain at least 4 columns (cust_lat, cust_lon, wh_lat, wh_lon).")
        return pd.DataFrame()

    # Keep only first four columns, coerce to numeric
    raw = raw.iloc[:, :4].apply(pd.to_numeric, errors="coerce")
    raw.columns = ["cust_lat", "cust_lon", "wh_lat", "wh_lon"]
    raw = raw.dropna()
    return raw

if uploaded:
    df = load_csv(uploaded)
    if df.empty:
        st.stop()

    # Identify unique warehouses by lat/lon pair
    wh_pairs = list(dict.fromkeys(zip(df.wh_lat, df.wh_lon)))  # preserve order
    wh_index = {pair: i for i, pair in enumerate(wh_pairs)}
    df["Warehouse"] = [wh_index[(r.wh_lat, r.wh_lon)] for r in df.itertuples()]

    centres = [[lon, lat] for lat, lon in wh_pairs]  # convert to lon/lat order

    # Colour pickers
    if custom_toggle:
        st.sidebar.subheader("🎨 Pick colours")
        wh_colours = []
        for w_idx, (lat, lon) in enumerate(wh_pairs):
            default_hex = HEX_PALETTE[w_idx % len(HEX_PALETTE)]
            picked = st.sidebar.color_picker(f"Warehouse {w_idx} ({lat:.2f}, {lon:.2f})", default_hex)
            wh_colours.append(picked)
    else:
        wh_colours = ["#888888"] * len(wh_pairs)

    plot_network(df, centres, colours=wh_colours)
