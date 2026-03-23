import streamlit as st
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.visualization import simple_norm
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats
import pandas as pd

st.set_page_config(page_title="AstroStar Finder", page_icon="🔭")
st.title("🌌 Stellar Source Finder")

uploaded_file = st.file_uploader("Choose a FITS file...", type=["fits", "fit"])

if uploaded_file is not None:
    with fits.open(uploaded_file) as hdul:
        data = hdul[0].data
    
    st.sidebar.header("Settings")
    threshold = st.sidebar.slider("Sensitivity", 1.0, 10.0, 3.0)
    
    mean, median, std = sigma_clipped_stats(data, sigma=3.0)
    daofind = DAOStarFinder(fwhm=3.0, threshold=threshold * std)
    sources = daofind(data - median)

    fig, ax = plt.subplots()
    norm = simple_norm(data, 'log', percent=99.0)
    ax.imshow(data, cmap='magma', origin='lower', norm=norm)
    
    if sources:
        st.metric("Stars Found", len(sources))
        ax.scatter(sources['xcentroid'], sources['ycentroid'], s=10, edgecolor='cyan', facecolor='none')
        st.dataframe(sources.to_pandas().head(50))
    
    st.pyplot(fig)
else:
    st.info("Upload a .fits file to see the magic!")
