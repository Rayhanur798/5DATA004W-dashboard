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
