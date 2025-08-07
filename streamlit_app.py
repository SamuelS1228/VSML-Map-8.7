
import streamlit as st
import pandas as pd
from visualization import plot_network

st.set_page_config(page_title="Customer ➜ Warehouse Visualizer", layout="wide")
st.title("📍 Customer to Warehouse Connection Visualizer")

st.markdown(
    """Upload a CSV where:

    * **Column A** – Customer latitude  
    * **Column B** – Customer longitude  
    * **Column C** – Warehouse latitude  
    * **Column D** – Warehouse longitude  

    Header row is optional – the app ignores it.

    The map style replicates the one from the full *Warehouse Network Optimizer* tool,
    with colored warehouses, connection lines, and an automatic basemap fallback.
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

    # Build centers list and store assignment
    centers = (
        df[["wh_lon", "wh_lat"]]
        .drop_duplicates()
        .reset_index(drop=True)
        .values.tolist()
    )
    center_lookup = {
        (round(lon, 6), round(lat, 6)): idx
        for idx, (lon, lat) in enumerate(centers)
    }

    stores = pd.DataFrame({
        "Longitude": df["cust_lon"],
        "Latitude": df["cust_lat"],
        "Warehouse": [
            center_lookup[(round(lon, 6), round(lat, 6))]
            for lon, lat in zip(df["wh_lon"], df["wh_lat"])
        ],
        # DistMi is optional for visualization; leave blank
    })

    # Render map using legacy visual style
    plot_network(stores, centers)

    st.success(f"Displayed {len(stores):,} customer points across {len(centers)} warehouse locations.")
