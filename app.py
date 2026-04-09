import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SDG7 Energy Dashboard", layout="wide")

st.title("SDG7: Affordable and Clean Energy Dashboard")
st.markdown("Exploring global progress on clean energy access from 2000 to 2024.")

df = pd.read_csv("data/Goal7.csv", encoding="latin1")
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
df = df.dropna(subset=["Value"])

st.write(df.head())

# Sidebar filters
st.sidebar.title("Filters")

indicator_options = df["SeriesDescription"].unique().tolist()
selected_indicator = st.sidebar.selectbox("Select Indicator", indicator_options)

min_year = int(df["TimePeriod"].min())
max_year = int(df["TimePeriod"].max())
selected_year = st.sidebar.slider("Select Year", min_year, max_year, max_year)

country_options = sorted(df["GeoAreaName"].unique().tolist())
selected_countries = st.sidebar.multiselect(
    "Select Countries (for trend chart)",
    options=country_options,
    default=["China", "India", "Nigeria", "United States of America"]
)
# Filterig the data based on sidebar selections
indicator_df = df[df["SeriesDescription"] == selected_indicator]
year_df = indicator_df[indicator_df["TimePeriod"] == selected_year]

#aggregation fix
df = df.groupby(
    ["SeriesDescription", "GeoAreaCode", "GeoAreaName", "TimePeriod"],
    as_index=False
)["Value"].mean()