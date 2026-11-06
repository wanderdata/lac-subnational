"""South America regional disparities (Streamlit).

Run locally:   streamlit run app/app.py
Streamlit Community Cloud: main file path = app/app.py
"""
import streamlit as st

st.set_page_config(page_title="Regional Disparities in South America", page_icon="🗺️", layout="wide")
st.navigation([
    st.Page("views/map.py", title="Map", default=True),
    st.Page("views/disparities.py", title="Disparities by country", url_path="disparities"),
    st.Page("views/about.py", title="About, data and method", url_path="about"),
]).run()
