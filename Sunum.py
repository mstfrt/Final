import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path
import validators
st.set_page_config(page_title="MİHENK", page_icon=":bar_chart:", layout="wide")


def add_logo(logo_url: str, height: int = 120):
    """Add a logo (from logo_url) on the top of the navigation page of a multipage app.
    Taken from https://discuss.streamlit.io/t/put-logo-and-title-above-on-top-of-page-navigation-in-sidebar-of-multipage-app/28213/6

    The url can either be a url to the image, or a local path to the image.

    Args:
        logo_url (str): URL/local path of the logo
    """

    if validators.url(logo_url) is True:
        logo = f"url({logo_url})"
    else:
        logo = f"url(data:image/png;base64,{base64.b64encode(Path(logo_url).read_bytes()).decode()})"

    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: {logo};
                background-repeat: no-repeat;
                padding-top: {height - 40}px;
                background-position: 105px 20px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


add_logo(r"dataset/mihenk_logo.png")


new_title = '<p style="font-family:sans-serif; color: white; font-size: 50px; text-align: center; margin-top: 30px; margin-bottom: 20px">📺 Sunum</p>'
st.markdown(new_title, unsafe_allow_html=True)
st.markdown("<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)
components.iframe("https://docs.google.com/presentation/d/e/2PACX-1vRt2Md0DKNnEgKV7q_cjd_FeF7EI3ju_ATUzrc6Dm2oLmIDhceFU8B-diGOs6TBBveq3VuDdQ7-oaiZ/embed?start=false&loop=false&delayms=30000", width=1240, height=738)

new_title1 = '<p style="font-family:sans-serif; color: white; font-size: 30px; text-align: center; margin-top: 130px; margin-bottom: 20px">Hazırlayanlar:</p>'
st.sidebar.markdown(new_title1, unsafe_allow_html=True)
ertugrul = '<p style="font-family:sans-serif; color: #d2d9d8; font-size: 20px; margin-left: 61px">• Ertuğrul Pancar</p>'
st.sidebar.markdown(ertugrul, unsafe_allow_html=True)
hilal = '<p style="font-family:sans-serif; color: #d2d9d8; font-size: 20px; margin-left: 61px">• Hilal Çalışkan</p>'
st.sidebar.markdown(hilal, unsafe_allow_html=True)
kadir = '<p style="font-family:sans-serif; color: #d2d9d8; font-size: 20px; margin-left: 61px">• Kadir Akbalık</p>'
st.sidebar.markdown(kadir, unsafe_allow_html=True)
mesut = '<p style="font-family:sans-serif; color: #d2d9d8; font-size: 20px; margin-left: 61px">• Mesut Fırat</p>'
st.sidebar.markdown(mesut, unsafe_allow_html=True)

