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

# Key metrics 
st.subheader(f"Key Stats for {selected_year}")

#Splits the page into 3 equal columns side by side
col1, col2, col3 = st.columns(3)

world_data = year_df[year_df["GeoAreaName"] == "World"]
if not world_data.empty:
    global_value = round(world_data["Value"].values[0], 1) #Gets the first value from that filtered data, rounds it to 1 decimal place, then displays it as a metric box in column 1.
    col1.metric("Global Average", global_value)
else:
    col1.metric("Global Average", "No data")


#anything below 900 is a real country
countries_only = year_df[year_df["GeoAreaCode"] < 900]
if not countries_only.empty:
    highest = countries_only.loc[countries_only["Value"].idxmax()]
    col2.metric("Highest Country", highest["GeoAreaName"], round(highest["Value"], 1))

    lowest = countries_only.loc[countries_only["Value"].idxmin()]
    col3.metric("Lowest Country", lowest["GeoAreaName"], round(lowest["Value"], 1), delta_color="inverse")

#Just draws a horizontal line to separate sections
st.divider()

# Split the page into 2 columns — map on the left, line chart on the right
col_map, col_line = st.columns(2)

with col_map:
    # Subheading for the map section
    st.subheader("World Map")
    
    # Filter out regional aggregates, only keep real countries (code under 900)
    map_df = year_df[year_df["GeoAreaCode"] < 900]
    
    # Create the choropleth map using plotly
    fig_map = px.choropleth(
        map_df,
        locations="GeoAreaName",       
        locationmode="country names",  
        color="Value",                 # colour countries based on their value
        hover_name="GeoAreaName",      # show country name when hovering
        color_continuous_scale="Blues", # blue colour scale — avoids red/green colour blindness issue
        title=f"{selected_year}"      
    )
    
    # Make the map background transparent so it matches the dashboard theme
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",              # transparent outer background
        geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False), # transparent map background
        margin=dict(t=30, b=0, l=0, r=0),          # reduce whitespace around the map
        coloraxis_showscale=False                   # hide the colour scale bar
    )
    
    # Display the map in the app
    st.plotly_chart(fig_map, use_container_width=True)
    
