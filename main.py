import streamlit as st
from PIL import Image


st.set_page_config(page_title="Binary busters", layout="wide")

#navigation
maps = st.Page(
    page="maps.py",
    title="Maps",
    icon="🏠"
)

predict = st.Page(
    page="predict.py",
    title="Predict",
    icon="🧠"
)


pg = st.navigation(
    {
        "Maps":[maps],
        "Prediction":[predict],
    }
)
pg.run()
