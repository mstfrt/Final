import pandas as pd
import warnings
import datetime as dt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
import plotly.express as px
import streamlit as st
import base64
from pathlib import Path
import validators

pd.set_option('display.float_format', lambda x: '%.10f' % x)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 500)
pd.set_option("display.max_rows", 100)
warnings.simplefilter(action="ignore")

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


st.title(" :bar_chart: Müşteri Verisi:")
st.markdown("<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)

df = pd.read_csv(r"dataset/final_customers.csv", encoding="ISO-8859-1")

cus_final = df.copy()


with st.sidebar.expander("Müşteri"):
    st.sidebar.header("Müşteri Filtresi Seçiniz: ")

    category = st.sidebar.multiselect("Kategori:", cus_final["Category"].unique())
    if not category:
        df12 = cus_final.copy()
    else:
        df12 = cus_final[cus_final["Category"].isin(category)]

    # Create for State
    segment = st.sidebar.multiselect("Segment:", df12["Segment"].unique())
    if not segment:
        df13 = df12.copy()
    else:
        df13 = df12[df12["Segment"].isin(segment)]


    if not category and not segment:
        filtered_df1 = cus_final
    elif category and not segment:
        filtered_df1 = cus_final[cus_final["Category"].isin(category)]
    elif category and segment:
        filtered_df1 = df13[cus_final["Category"].isin(category) & df13["Segment"].isin(segment)]
    elif not category and segment:
        filtered_df1 = cus_final[cus_final["Segment"].isin(segment)]


    n1 = int(st.sidebar.number_input("Müşteri Sayısı:", key=1, value=filtered_df1.shape[0]))

clm1, clm2 = st.columns([1, 1])

with clm1:
    st.subheader(" :bar_chart: Filtrelenmiş Müşteri Verisi:")
    with st.expander("Müşteri Verisi:"):
        if n1 == 0:
            st.write(filtered_df1.sort_values(by="clv", ascending=False).style.background_gradient(cmap="Blues"))
        else:
            st.write(filtered_df1.iloc[:n1, :].sort_values(by="clv", ascending=False).style.background_gradient(cmap="Blues"))
        clm3, clm4 = st.columns([1, 1])
        with clm3:
            csv = filtered_df1.to_csv(index=False).encode("utf-8")
            st.download_button(
            "Tüm Veriyi İndir", data=csv, file_name=f"Filtered_Data_{segment}_{category}.csv", mime="text/csv", key=2
            )
        with clm4:
            csv1 = filtered_df1["Customer_ID"].to_csv(index=False).encode("utf-8")
            st.download_button(
            "Müşteri ID İndir", data=csv1, file_name=f"Filtered_Customers_{segment}_{category}.csv", mime="text/csv", key=3
            )
with clm2:
        st.subheader("CLV Değerlerinin RFM Segmentlerine Göre Dağılımı")
        fig = px.pie(filtered_df1, values="clv", names="Segment", hole=0.5)
        fig.update_traces(text=filtered_df1["Segment"], textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

st.subheader("RFM Segmentlerine Göre Müşterilerin Hiyerarşik TreeMap Görünümü")
filtered_df1["Customers"] = 1
fig3 = px.treemap(
    filtered_df1,
    path=["Category", "Segment"],
    values="Customers",
    hover_data=["Customers"],
    color="Segment",
)
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)
