import streamlit as st
import pandas as pd
from visualization import plot_network, HEX_PALETTE

st.set_page_config(page_title="Warehouse Network Map", layout="wide")

st.title("Warehouse Network Mapper")

uploaded = st.file_uploader("Upload store CSV", type=["csv"])

# Sidebar controls
st.sidebar.header("Controls")

distinct_toggle = st.sidebar.toggle(
    "Use custom colours per warehouse",
    value=True,
    help="Toggle to apply the colour pickers below.",
)

def load_data(file) -> pd.DataFrame:
    return pd.read_csv(file)

if uploaded:
    df = load_data(uploaded)

    # Expect columns: Longitude, Latitude, Warehouse (int index)
    if not set(["Longitude", "Latitude", "Warehouse"]).issubset(df.columns):
        st.error("CSV must contain Longitude, Latitude, and Warehouse columns.")
        st.stop()

    warehouses = sorted(df["Warehouse"].unique())
    centres = []
    for wh in warehouses:
        subset = df[df["Warehouse"] == wh]
        # Use mean position as warehouse point if not separately supplied
        centres.append([subset["Longitude"].mean(), subset["Latitude"].mean()])

    # Sidebar colour pickers
    if distinct_toggle:
        st.sidebar.subheader("🎨 Warehouse colours")
        wh_colours = []
        for idx in warehouses:
            default_hex = HEX_PALETTE[idx % len(HEX_PALETTE)]
            picked = st.sidebar.color_picker(f"Warehouse {idx}", default_hex)
            wh_colours.append(picked)
    else:
        # one neutral grey
        wh_colours = ["#888888"] * len(warehouses)

    plot_network(df, centres, colours=wh_colours)
