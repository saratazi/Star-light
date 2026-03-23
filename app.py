import streamlit as st
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.visualization import simple_norm
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats
import pandas as pd
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="AstroStar Pro | Sky Explorer",
    page_icon="🔭",
    layout="wide"
)

# Custom Styling for a Star Walk atmosphere
st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e0e0e0; }
    .stTextInput>div>div>input { background-color: #1e2130; color: white; border: 1px solid #3e445e; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e445e; }
    .stCheckbox { color: #00ffff; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar Navigation
st.sidebar.title("🔭 AstroStar Pro")
st.sidebar.markdown("---")
app_mode = st.sidebar.radio("Select Mode", ["Sky Explorer (Star Walk)", "FITS Analysis"])

# 3. Mode 1: Sky Explorer (The Star Walk Imitation)
if app_mode == "Sky Explorer (Star Walk)":
    st.title("🌌 Interactive Sky Map")
    st.subheader("Explore constellations and deep space objects in real-time")
    
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
        # Building the Star Walk logic into Aladin Lite v3
        aladin_html = f"""
        <div id="aladin-lite-div" style="width:100%;height:650px;border-radius:15px;border: 2px solid #3e445e; box-shadow: 0 0 20px rgba(0,255,255,0.1);"></div>
        <script type="text/javascript" src="https://code.jquery.com/jquery-1.12.1.min.js" charset="utf-8"></script>
        <script type="text/javascript" src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js" charset="utf-8"></script>
        <script type="text/javascript">
            let aladin;
            A.init.then(() => {{
                aladin = A.aladin('#aladin-lite-div', {{
                    survey: "{survey}", 
                    fov: {fov}, 
                    target: "{target}",
                    showReticle: false,
                    showConstellations: {str(show_const).lower()},
                    showLayersControl: false,
                    showGotoControl: false,
                    showFullscreenControl: true
                }});
            }});
        </script>
        """
        components.html(aladin_html, height=670)
        st.info("💡 Use your mouse to drag the sky. Scroll to zoom, just like Star Walk!")

# 4. Mode 2: FITS Analysis (Professional Tool)
else:
    st.title("🔬 FITS Analysis Pro")
    st.sidebar.markdown("### Detection Settings")
    fwhm_val = st.sidebar.slider("Star Blur (FWHM)", 1.0, 10.0, 3.0, help="Adjust for star focus sharpness")
    threshold_val = st.sidebar.slider("Sensitivity", 1.0, 20.0, 3.0, help="Lower values find dimmer stars")
    
    uploaded_file = st.file_uploader("Upload a FITS file (NASA scientific data)", type=["fits", "fit"])

    if uploaded_file is not None:
        try:
            with fits.open(uploaded_file) as hdul:
                data = hdul[0].data
            
            # Scientific math to identify stars against background noise
            mean, median, std = sigma_clipped_stats(data, sigma=3.0)
            daofind = DAOStarFinder(fwhm=fwhm_val, threshold=threshold_val * std)
            sources = daofind(data - median)

            col_img, col_data = st.columns([2, 1])
            with col_img:
                st.markdown("### 🔭 Detection Preview")
                fig, ax = plt.subplots(figsize=(10, 8))
                fig.patch.set_facecolor('#05070a')
                norm = simple_norm(data, 'log', percent=99.0)
                ax.imshow(data, cmap='magma', origin='lower', norm=norm)
                
                if sources:
                    ax.scatter(sources['xcentroid'], sources['ycentroid'], 
                               s=35, edgecolor='#00ffff', facecolor='none', lw=1.2)
                ax.axis('off')
                st.pyplot(fig)
            
            with col_data:
                if sources:
                    st.metric("Stars Found", len(sources))
                    st.write("### Data Table")
                    st.dataframe(sources.to_pandas()[['id', 'xcentroid', 'ycentroid', 'peak']].head(100), use_container_width=True)
                    
                    # CSV Export
                    csv = sources.to_pandas().to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Catalog", csv, "stars.csv", "text/csv")
                else:
                    st.warning("No stars detected. Try increasing Sensitivity.")
        except Exception as e:
            st.error(f"Error analyzing FITS: {e}")
    else:
        st.info("👋 Upload a .fits file to start detection.")
        st.image("https://images.nasa.gov/images/stsci-h-p2016a-m-2000x1333.jpg", use_container_width=True)

st.write("---")
st.caption("AstroStar Pro | Powered by Aladin Lite, Astropy, and Photutils")
