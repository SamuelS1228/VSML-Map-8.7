
import streamlit as st
import pandas as pd
from visualization import plot_network, _c

st.set_page_config(page_title="Customer ➜ Warehouse Visualizer", layout="wide")
st.title("📍 Customer to Warehouse Connection Visualizer")

st.markdown(
    """Upload a CSV where:

    * **Column A** – Customer latitude  
    * **Column B** – Customer longitude  
    * **Column C** – Warehouse latitude  
    * **Column D** – Warehouse longitude  

    Header row is optional – the app ignores it.

    Use the sidebar to pick custom colours for each warehouse and its
    connecting lines. Colours default to the standard palette so the app
    works exactly as before even if you leave them unchanged.
    """)

up_file = st.file_uploader("Choose a CSV file", type=["csv"])

@st.cache_data(show_spinner=False)
def load_df(file):
    df = pd.read_csv(file, header=None)
    df = df.iloc[:, :4]
    df.columns = ["cust_lat", "cust_lon", "wh_lat", "wh_lon"]
    df = df.dropna()
    return df

if up_file is not None:
    df = load_df(up_file)

    if df.empty:
        st.error("The file is empty or formatted incorrectly.")
        st.stop()

    # Build centres list and store assignment
    centres = (
        df[["wh_lon", "wh_lat"]]
        .drop_duplicates()
        .reset_index(drop=True)
        .values.tolist()
    )
    centre_lookup = {
        (round(lon, 6), round(lat, 6)): idx
        for idx, (lon, lat) in enumerate(centres)
    }

    stores = pd.DataFrame({
        "Longitude": df["cust_lon"],
        "Latitude": df["cust_lat"],
        "Warehouse": [
            centre_lookup[(round(lon, 6), round(lat, 6))]
            for lon, lat in zip(df["wh_lon"], df["wh_lat"])
        ],
    })

    # ─────────────────────────────────────────────
    # Sidebar colour pickers
    # ─────────────────────────────────────────────
    st.sidebar.header("🎨 Warehouse colours")
    hex_colours = []
    for idx in range(len(centres)):
        default_hex = '#%02x%02x%02x' % tuple(_c(idx))
        picked = st.sidebar.color_picker(f"Warehouse {idx+1}", default_hex)
        hex_colours.append(picked)

    def hex_to_rgb_list(h):
        h = h.lstrip('#')
        return [int(h[i:i+2], 16) for i in (0, 2, 4)]

    colours_rgb = [hex_to_rgb_list(h) for h in hex_colours]

    # Render map with chosen colours
    plot_network(stores, centres, colours_rgb)

    st.success(f"Displayed {len(stores):,} customer points across {len(centres)} warehouse locations.")
