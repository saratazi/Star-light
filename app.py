import streamlit as st
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.visualization import simple_norm
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats
import pandas as pd
import streamlit.components.v1 as components
import math
from streamlit_geolocation import streamlit_geolocation

# ---------------------------
# 1. Page Configuration
# ---------------------------
st.set_page_config(
    page_title="AstroStar Pro | Sky Explorer",
    page_icon="🔭",
    layout="wide"
)

# ---------------------------
# 2. Custom Styling
# ---------------------------
st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e0e0e0; }
    .stTextInput>div>div>input { background-color: #1e2130; color: white; border: 1px solid #3e445e; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e445e; }
    .stCheckbox { color: #00ffff; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------
# 3. Distance + Classification
# ---------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def classify_distance(distance):
    if distance < 50:
        return "NEAR"
    elif distance < 200:
        return "MEDIUM"
    else:
        return "FAR"

# ---------------------------
# 4. Sidebar Navigation
# ---------------------------
st.sidebar.title("🔭 AstroStar Pro")
st.sidebar.markdown("---")
app_mode = st.sidebar.radio("Select Mode", ["Sky Explorer (Star Walk)", "FITS Analysis"])

# ===========================
# MODE 1: SKY EXPLORER
# ===========================
if app_mode == "Sky Explorer (Star Walk)":
    st.title("🌌 Interactive Sky Map")
    st.subheader("Explore constellations and deep space objects in real-time")

    # ---------------------------
    # 📍 GEOLOCATION + AI
    # ---------------------------
    st.markdown("### 📍 Your Location & AI Classification")

    location = streamlit_geolocation()

    if location:
        user_lat = location["latitude"]
        user_lon = location["longitude"]

        # Reference location (Fes)
        ref_lat, ref_lon = 34.033, -5.000

        distance = haversine(user_lat, user_lon, ref_lat, ref_lon)
        classification = classify_distance(distance)

        col1, col2, col3 = st.columns(3)
        col1.metric("Latitude", f"{user_lat:.4f}")
        col2.metric("Longitude", f"{user_lon:.4f}")
        col3.metric("Distance to Fes (km)", f"{distance:.2f}")

        st.success(f"🤖 AI Classification: {classification}")
    else:
        st.warning("Please allow location access to enable AI features.")

    # ---------------------------
    # MAP + CONTROLS
    # ---------------------------
    col_map, col_ctrl = st.columns([3, 1])

    with col_ctrl:
        st.markdown("### 🛠️ View Controls")
        target = st.text_input("Find Object (e.g. Sirius, M42, Moon)", "Orion Nebula")
        show_const = st.checkbox("Show Constellations", True)
        show_labels = st.checkbox("Show Star Names", True)
        survey = st.selectbox("Map Theme", [
            "P/DSS2/color", 
            "P/2MASS/color", 
            "P/SDSS9/color",
            "P/Mellinger/color"
        ])
        fov = st.slider("Field of View (Zoom)", 0.1, 10.0, 2.0)

    with col_map:
        aladin_html = f"""
        <div id="aladin-lite-div" style="width:100%;height:650px;border-radius:15px;border: 2px solid #3e445e;"></div>
        <script type="text/javascript" src="https://code.jquery.com/jquery-1.12.1.min.js"></script>
        <script type="text/javascript" src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js"></script>
        <script>
            let aladin;
            A.init.then(() => {{
                aladin = A.aladin('#aladin-lite-div', {{
                    survey: "{survey}", 
                    fov: {fov}, 
                    target: "{target}",
                    showConstellations: {str(show_const).lower()},
                    showFullscreenControl: true
                }});
            }});
        </script>
        """
        components.html(aladin_html, height=670)
        st.info("💡 Drag to move, scroll to zoom.")

# ===========================
# MODE 2: FITS ANALYSIS
# ===========================
else:
    st.title("🔬 FITS Analysis Pro")

    st.sidebar.markdown("### Detection Settings")
    fwhm_val = st.sidebar.slider("Star Blur (FWHM)", 1.0, 10.0, 3.0)
    threshold_val = st.sidebar.slider("Sensitivity", 1.0, 20.0, 3.0)

    uploaded_file = st.file_uploader("Upload a FITS file", type=["fits", "fit"])

    if uploaded_file is not None:
        try:
            with fits.open(uploaded_file) as hdul:
                data = hdul[0].data

            mean, median, std = sigma_clipped_stats(data, sigma=3.0)
            daofind = DAOStarFinder(fwhm=fwhm_val, threshold=threshold_val * std)
            sources = daofind(data - median)

            col_img, col_data = st.columns([2, 1])

            with col_img:
                fig, ax = plt.subplots(figsize=(10, 8))
                fig.patch.set_facecolor('#05070a')
                norm = simple_norm(data, 'log', percent=99.0)
                ax.imshow(data, cmap='magma', origin='lower', norm=norm)

                if sources:
                    ax.scatter(
                        sources['xcentroid'],
                        sources['ycentroid'],
                        s=35,
                        edgecolor='#00ffff',
                        facecolor='none'
                    )

                ax.axis('off')
                st.pyplot(fig)

            with col_data:
                if sources:
                    st.metric("Stars Found", len(sources))
                    st.dataframe(
                        sources.to_pandas()[['id', 'xcentroid', 'ycentroid', 'peak']].head(100)
                    )

                    csv = sources.to_pandas().to_csv(index=False).encode('utf-8')
                    st.download_button("Download CSV", csv, "stars.csv")

                else:
                    st.warning("No stars detected. Increase sensitivity.")

        except Exception as e:
            st.error(f"Error: {e}")

    else:
        st.info("Upload a FITS file to start.")
