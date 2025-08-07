import streamlit as st
import pandas as pd
from visualization import plot_network, HEX_PALETTE

st.set_page_config(page_title="Warehouse Network Map", layout="wide")

st.title("Warehouse Network Mapper")

uploaded = st.file_uploader("Upload CSV with customer & warehouse coordinates", type=["csv"])

st.sidebar.header("Controls")

color_toggle = st.sidebar.toggle(
    "Custom colours per warehouse",
    value=True,
    help="Toggle on to pick a colour for each warehouse; off for default grey.",
)

def load_csv(file) -> pd.DataFrame:
    """Load the CSV.

    We accept either:
      • No header  ➜ columns 0‑3 = cust_lat, cust_lon, wh_lat, wh_lon
      • Header row with names like Cust_Lat, Cust_Lon, Wh_Lat, Wh_Lon (case‑insensitive)
    """
    df_try = pd.read_csv(file)
    # Detect if first row looks numeric; if not, treat current header row as data
    if not pd.api.types.is_numeric_dtype(df_try.iloc[0, 0]):
        # header row existed; ensure correct column names
        df = df_try.rename(columns=lambda c: c.strip().lower())
        expected = ["cust_lat", "cust_lon", "wh_lat", "wh_lon"]
        if all(any(ec in col for col in df.columns) for ec in expected):
            # re‑select using substring matching
            rename_map = {}
            for col in df.columns:
                if "cust_lat" in col: rename_map[col] = "cust_lat"
                elif "cust_lon" in col: rename_map[col] = "cust_lon"
                elif "wh_lat" in col: rename_map[col] = "wh_lat"
                elif "wh_lon" in col: rename_map[col] = "wh_lon"
            df = df.rename(columns=rename_map)
        else:
            st.stop()
    else:
        df = pd.read_csv(file, header=None)
        df.columns = ["cust_lat", "cust_lon", "wh_lat", "wh_lon"]
    return df

if uploaded:
    raw = load_csv(uploaded)

    # Create stores DataFrame expected by visualisation
    stores = pd.DataFrame({
        "Latitude": raw["cust_lat"],
        "Longitude": raw["cust_lon"],
    })

    # Identify unique warehouses by lat+lon pair
    wh_pairs = raw[["wh_lat", "wh_lon"]].drop_duplicates().reset_index(drop=True)
    wh_pairs["index"] = wh_pairs.index
    # Map each row to warehouse index
    raw = raw.merge(wh_pairs, on=["wh_lat", "wh_lon"], how="left")
    stores["Warehouse"] = raw["index"]

    # Build centres list in order of index
    centres = wh_pairs[["wh_lon", "wh_lat"]].values.tolist()

    # Sidebar colour pickers
    if color_toggle:
        st.sidebar.subheader("🎨 Warehouse colours")
        wh_colours = []
        for idx, row in wh_pairs.iterrows():
            default_hex = HEX_PALETTE[idx % len(HEX_PALETTE)]
            picked = st.sidebar.color_picker(f"Warehouse {idx}", default_hex)
            wh_colours.append(picked)
    else:
        wh_colours = ["#888888"] * len(wh_pairs)

    plot_network(stores, centres, colours=wh_colours)

    st.success(f"Visualised {len(stores):,} customers served by {len(centres)} warehouses.")
