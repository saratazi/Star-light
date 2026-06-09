import streamlit as st
import requests
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u

st.set_page_config(page_title="Space App", layout="wide")

st.title("🌌 Space Explorer")

# =========================
# 📸 NASA IMAGE
# =========================
st.header("🚀 NASA Image of the Day")

API_KEY = "DEMO_KEY"  

url = "https://api.nasa.gov/planetary/apod"
params = {"api_key": API_KEY}

res = requests.get(url, params=params)

if res.status_code == 200:
    data = res.json()

    st.subheader(data["title"])
    st.write(data["explanation"])

    if data["media_type"] == "image":
        st.image(data["url"])
    else:
        st.video(data["url"])
else:
    st.error("NASA API error")

# =========================
# 📍 SIMBAD LOCATION
# =========================
st.header("✨ Localisation (Stars / Galaxies)")

name = st.text_input("Enter object name", "Sirius")

def get_position(obj):
    simbad = Simbad()
    result = simbad.query_object(obj)

    if result is None:
        return None

    ra = result["RA"][0]
    dec = result["DEC"][0]

    coord = SkyCoord(ra, dec, unit=(u.hourangle, u.deg))

    return {
        "ra": ra,
        "dec": dec,
        "ra_deg": coord.ra.degree,
        "dec_deg": coord.dec.degree,
        "gal_l": coord.galactic.l.degree,
        "gal_b": coord.galactic.b.degree
    }

if st.button("Search"):
    obj = get_position(name)

    if obj:
        st.success("Object found ✅")

        st.write("### Coordinates")
        st.write("RA:", obj["ra"])
        st.write("DEC:", obj["dec"])

        st.write("### Degrees")
        st.write("RA:", obj["ra_deg"])
        st.write("DEC:", obj["dec_deg"])

        st.write("### Galactic")
        st.write("l:", obj["gal_l"])
        st.write("b:", obj["gal_b"])
    else:
        st.error("Object not found ❌")
