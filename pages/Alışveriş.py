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

st.title(" :bar_chart: Alışveriş Verisi:")
st.markdown("<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)

df = pd.read_csv(r"dataset/final_project_dataset.csv", encoding="ISO-8859-1")

cus_final = df.copy()

n = 0

st.sidebar.header("Filtre Seçiniz: ")

category = st.sidebar.multiselect("Kategori:", df["Category"].unique())
if not category:
    df2 = df.copy()
else:
    df2 = df[df["Category"].isin(category)]

# Create for State
sub_cat = st.sidebar.multiselect("Alt Kategori:", df2["Sub_Category"].unique())
if not sub_cat:
    df3 = df2.copy()
else:
    df3 = df2[df2["Sub_Category"].isin(sub_cat)]


if not category and not sub_cat:
    filtered_df = df
elif category and not sub_cat:
    filtered_df = df[df["Category"].isin(category)]
elif category and sub_cat:
    filtered_df = df3[df["Category"].isin(category) & df3["Sub_Category"].isin(sub_cat)]
elif not category and sub_cat:
    filtered_df = df[df["Sub_Category"].isin(sub_cat)]


n = int(st.sidebar.number_input("Gözlem Sayısı:", max_value=filtered_df.shape[0]))

with st.expander("Filtrelenmiş Alışveriş Verisi:"):
    if n == 0:
        st.write(filtered_df.iloc[:5, :])
    else:
        st.write(filtered_df.iloc[:n, :])


category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()
col1, col2 = st.columns((2))
with col1:
    st.subheader("Kategori Bazında Satışlar")
    fig = px.bar(
        category_df,
        x="Category",
        y="Sales",
        text=["${:,.2f}".format(x) for x in category_df["Sales"]],
        template="seaborn",
    )
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Bölge Bazında Satışlar")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category Verisi"):
        st.write(category_df)
        csv = category_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Data",
            data=csv,
            file_name="Category.csv",
            mime="text/csv",
            help="Click here to download the data as a CSV file",
        )

with cl2:
    with st.expander("Bölge Verisi"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region)
        csv = region.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Data",
            data=csv,
            file_name="Region.csv",
            mime="text/csv",
            help="Click here to download the data as a CSV file",
        )

filtered_df["month_year"] = filtered_df["Order_Date"].dt.to_period("M", errors='coerce')
st.subheader("Zamana Göre Satışların Dağılım Grafiği")

linechart = pd.DataFrame(
    filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()
).reset_index()
fig2 = px.line(
    linechart,
    x="month_year",
    y="Sales",
    labels={"sales": "Amount"},
    height=500,
    width=1000,
    template="gridon",
)
st.plotly_chart(fig2, use_container_width=True)

with st.expander("TimeSeries Verilerini Görüntüle:"):
    st.write(linechart.T)
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Data", data=csv, file_name="TimeSeries.csv", mime="text/csv"
    )

# Create a treem based on Region, category, sub-Category
st.subheader("Satışların hiyerarşik TreeMap görünümü")
fig3 = px.treemap(
    filtered_df,
    path=["Region", "Category", "Sub_Category"],
    values="Sales",
    hover_data=["Sales"],
    color="Sub_Category",
)
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment Bazında Satışlar")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Kategori Bazında Satışlar")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff

st.subheader(":point_right: Ay Bazında Alt Kategori Satış Özeti")
with st.expander("Özet_Tablo"):
    df_sample = df[0:5][
        ["Region", "State", "Country", "Category", "Sales", "Profit", "Quantity"]
    ]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Ay Bazında Alt Kategori Tablosu")
    filtered_df["month"] = filtered_df["Order_Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(
        data=filtered_df, values="Sales", index=["Sub_Category"], columns="month"
    )
    st.write(sub_category_Year)

# Create a scatter plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1["layout"].update(
    title="Satışlar ve Kârlar Arasındaki İlişkinin Dağılım Grafiği.",
    titlefont=dict(size=20),
    xaxis=dict(title="Sales", titlefont=dict(size=19)),
    yaxis=dict(title="Profit", titlefont=dict(size=19)),
)
st.plotly_chart(data1, use_container_width=True)
