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


add_logo(r"C:\Users\mstfr\PycharmProjects\Final\dataset\mihenk_logo.png")

new_title = '<p style="font-family:sans-serif; color: white; font-size: 50px; text-align: center; margin-top: 30px; margin-bottom: 20px">📊 Alışveriş</p>'
st.markdown(new_title, unsafe_allow_html=True)
st.markdown("<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)

df = pd.read_csv(r"C:\Users\mstfr\PycharmProjects\Final\dataset\superstore_dataset2011-2015.csv", encoding="ISO-8859-1")
df.rename(columns=lambda x: x.replace(' ', '_').replace('-', '_'), inplace=True)

df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df['Ship_Date'] = pd.to_datetime(df['Ship_Date'])


def grab_col_names(dataframe, cat_th=10, car_th=20):
    """

    Veri setindeki kategorik, numerik ve kategorik fakat kardinal değişkenlerin isimlerini verir.
    Not: Kategorik değişkenlerin içerisine numerik görünümlü kategorik değişkenler de dahildir.

    Parameters
    ------
        dataframe: dataframe
                Değişken isimleri alınmak istenilen dataframe
        cat_th: int, optional
                numerik fakat kategorik olan değişkenler için sınıf eşik değeri
        car_th: int, optinal
                kategorik fakat kardinal değişkenler için sınıf eşik değeri

    Returns
    ------
        cat_cols: list
                Kategorik değişken listesi
        num_cols: list
                Numerik değişken listesi
        cat_but_car: list
                Kategorik görünümlü kardinal değişken listesi

    Examples
    ------
        import seaborn as sns
        df = sns.load_dataset("iris")
        print(grab_col_names(df))


    Notes
    ------
        cat_cols + num_cols + cat_but_car = toplam değişken sayısı
        num_but_cat cat_cols'un içerisinde.
        Return olan 3 liste toplamı toplam değişken sayısına eşittir: cat_cols + num_cols + cat_but_car = değişken sayısı

    """

    # cat_cols, cat_but_car
    cat_cols = [col for col in dataframe.columns if dataframe[col].dtypes == "O"]
    num_but_cat = [col for col in dataframe.columns if dataframe[col].nunique() < cat_th and
                   dataframe[col].dtypes != "O"]
    cat_but_car = [col for col in dataframe.columns if dataframe[col].nunique() > car_th and
                   dataframe[col].dtypes == "O"]
    cat_cols = cat_cols + num_but_cat
    cat_cols = [col for col in cat_cols if col not in cat_but_car]

    # num_cols
    num_cols = [col for col in dataframe.columns if dataframe[col].dtypes not in ["O", "datetime64[ns]"]]
    num_cols = [col for col in num_cols if col not in num_but_cat]

    # print(f"Observations: {dataframe.shape[0]}")
    # print(f"Variables: {dataframe.shape[1]}")
    # print(f'cat_cols: {len(cat_cols)}')
    # print(f'num_cols: {len(num_cols)}')
    # print(f'cat_but_car: {len(cat_but_car)}')
    # print(f'num_but_cat: {len(num_but_cat)}')
    return cat_cols, num_cols, cat_but_car


cat_cols, num_cols, cat_but_car = grab_col_names(df)


def outlier_thresholds(dataframe, variable, low_quantile=0.01, up_quantile=0.99):
    quantile_one = dataframe[variable].quantile(low_quantile)
    quantile_three = dataframe[variable].quantile(up_quantile)
    interquantile_range = quantile_three - quantile_one
    up_limit = quantile_three + 1.5 * interquantile_range
    low_limit = quantile_one - 1.5 * interquantile_range
    return low_limit, up_limit


def check_outlier(dataframe, col_name):
    low_limit, up_limit = outlier_thresholds(dataframe, col_name)
    if dataframe[(dataframe[col_name] > up_limit) | (dataframe[col_name] < low_limit)].any(axis=None):
        return True
    else:
        return False


def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit


for col in num_cols:
    replace_with_thresholds(df, col)

df["Order_Date"].max()
today_date = dt.datetime(2015, 1, 2)


#######################################################################################################################
# RFM
#######################################################################################################################
rfm = df.groupby('Customer_ID').agg({'Order_Date': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Order_ID': lambda Invoice: Invoice.nunique(),
                                     'Sales': lambda TotalPrice: TotalPrice.sum()})

rfm.columns = ['recency', 'frequency', 'monetary']

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
# 0-100, 0-20, 20-40, 40-60, 60-80, 80-100
rfm["frequency_score"] = pd.qcut(rfm['frequency'], 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
#######################################################################################################################



cltv_df = df.groupby("Customer_ID").agg(
    {
        "Order_Date": [
            lambda x: (x.max() - x.min()).days,
            lambda x: (today_date - x.min()).days,
        ],
        "Order_ID": lambda x: x.nunique(),
        "Sales": lambda x: x.sum(),
    }
)

cltv_df.columns = cltv_df.columns.droplevel(0)

cltv_df.columns = ['recency', 'T', 'frequency', 'monetary']

cltv_df["monetary"] = cltv_df["monetary"] / cltv_df["frequency"]

cltv_df = cltv_df[(cltv_df['frequency'] > 1)]

cltv_df["recency"] = cltv_df["recency"] / 7

cltv_df["T"] = cltv_df["T"] / 7


bgf = BetaGeoFitter(penalizer_coef=0.001)

bgf.fit(cltv_df['frequency'],
        cltv_df['recency'],
        cltv_df['T'])

ggf = GammaGammaFitter(penalizer_coef=0.01)

ggf.fit(cltv_df['frequency'], cltv_df['monetary'])

cltv = ggf.customer_lifetime_value(bgf,
                                   cltv_df['frequency'],
                                   cltv_df['recency'],
                                   cltv_df['T'],
                                   cltv_df['monetary'],
                                   time=3,  # 3 aylık
                                   freq="W",  # T'nin frekans bilgisi.
                                   discount_rate=0.14)

cltv = cltv.reset_index()


cltv_final = cltv_df.merge(cltv, on="Customer_ID", how="left")
cltv_final1 = df.merge(cltv, on="Customer_ID", how="left")
cltv_final.sort_values(by="clv", ascending=False).head(10)

#######################################################################################################################



#######################################################################################################################
# best_customers = cltv_final.sort_values(by="clv", ascending=False).head(100)
# customers = list(best_customers["Customer_ID"])
# cust = dff[dff["Customer_ID"].isin(customers)]
# cltv_customers = dff[dff["Customer_ID"].isin(customers)].drop(["Customer_ID", "Sales"], axis=1)
#
# sales_customers = model.predict(cltv_customers)
# cust["sales_pred"] = sales_customers
#
# best_cus_for_sales = cust.groupby("Customer_ID")["sales_pred"].sum()
#######################################################################################################################
# import random
# rand_cust = random.sample(list(df["Customer_ID"].unique()), 300)
# df[df["Customer_ID"].isin(rand_cust)]
#######################################################################################################################

cus_df = df.groupby("Customer_ID").agg({"Customer_Name": lambda x: x.mode(),
                                        "Category": lambda x: x.mode()[0]
                                        })

cus_df["Segment"] = rfm['segment']

cus_final = cus_df.merge(cltv, on="Customer_ID", how="left")

n = 0

st.sidebar.header("Filtre Seçiniz: ")

customer = st.sidebar.text_input("Müşteri ID")
if not customer:
    df = df.copy()
else:
    df = df[df["Customer_ID"] == customer]

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

startDate = pd.to_datetime(df["Order_Date"]).min()
endDate = pd.to_datetime(df["Order_Date"]).max()

col1, col2 = st.columns((2))
with col1:
    date1 = pd.to_datetime(st.date_input("Başlangıç", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("Bitiş", endDate))

filtered_df = filtered_df[(filtered_df["Order_Date"] >= date1) & (filtered_df["Order_Date"] <= date2)].copy()

with st.expander("Filtrelenmiş Alışveriş Verisi:", expanded=True):
    if n == 0:
        st.write(filtered_df.iloc[:5, :].style.background_gradient(cmap="Blues"))
    else:
        st.write(filtered_df.iloc[:n, :].style.background_gradient(cmap="Blues"))


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
        st.write(category_df.style.background_gradient(cmap="PuBu"))
        csv = category_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Veriyi İndir",
            data=csv,
            file_name="Category.csv",
            mime="text/csv",
            help="Click here to download the data as a CSV file",
        )

with cl2:
    with st.expander("Bölge Verisi"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Veriyi İndir",
            data=csv,
            file_name="Region.csv",
            mime="text/csv",
            help="Click here to download the data as a CSV file",
        )

filtered_df["month_year"] = filtered_df["Order_Date"].dt.to_period("M")
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
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Veriyi İndir", data=csv, file_name="TimeSeries.csv", mime="text/csv"
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
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1["layout"].update(
    title="Satışlar ve Kârlar Arasındaki İlişkinin Dağılım Grafiği.",
    titlefont=dict(size=20),
    xaxis=dict(title="Sales", titlefont=dict(size=19)),
    yaxis=dict(title="Profit", titlefont=dict(size=19)),
)
st.plotly_chart(data1, use_container_width=True)
