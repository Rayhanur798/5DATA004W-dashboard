import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SDG7 Energy Dashboard", layout="wide")

st.title("SDG7: Affordable and Clean Energy Dashboard")
st.markdown("Exploring global progress on clean energy access from 2000 to 2024.")

df = pd.read_csv("data/Goal7.csv", encoding="latin1")
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
df = df.dropna(subset=["Value"])

# Fix aggregation issue — averages urban/rural rows into one per country per year
df = df.groupby(
    ["SeriesDescription", "GeoAreaCode", "GeoAreaName", "TimePeriod"],
    as_index=False
)["Value"].mean()


# SIDEBAR FILTERS
st.sidebar.title("Filters")

# Dictionary mapping long names to short labels
indicator_labels = {
    "Proportion of population with access to electricity, by urban/rural (%)": "Access to Electricity (%)",
    "Proportion of population with primary reliance on clean fuels and technology (%)": "Clean Fuels Access (%)",
    "Renewable energy share in the total final energy consumption (%)": "Renewable Energy Share (%)",
    "Energy intensity level of primary energy (megajoules per constant 2021 purchasing power parity GDP)": "Energy Intensity (MJ per GDP)",
    "International financial flows to developing countries in support of clean energy research and development and renewable energy production, including in hybrid systems (millions of constant 2023 United States dollars)": "Financial Flows to Clean Energy ($M)"
    
}

# Show short labels in the dropdown
selected_label = st.sidebar.selectbox("Select Indicator", list(indicator_labels.values()))

# Get the full name to filter the data with
selected_indicator = [k for k, v in indicator_labels.items() if v == selected_label][0]

# Slider to pick a year
min_year = int(df["TimePeriod"].min())
max_year = int(df["TimePeriod"].max())
selected_year = st.sidebar.slider("Select Year", min_year, max_year, max_year)

# Multiselect to pick countries for the line chart
country_options = sorted(df["GeoAreaName"].unique().tolist())
selected_countries = st.sidebar.multiselect(
    "Select Countries (for trend chart)",
    options=country_options,
    default=["China", "India", "Nigeria", "United States of America"]
)
# INDICATOR DESCRIPTION

# Description for each indicator
indicator_descriptions = {
    "Proportion of population with access to electricity, by urban/rural (%)": "Track the percentage of population with access to electricity across 284 countries from 2000 to 2024. Sub-Saharan Africa remains the most underserved region.",
    "Proportion of population with primary reliance on clean fuels and technology (%)": "Explore how many people rely on clean fuels for cooking and heating. Access to clean fuels is a key factor in reducing indoor air pollution.",
    "Renewable energy share in the total final energy consumption (%)": "See what proportion of energy consumption comes from renewable sources. Higher values indicate a cleaner energy mix.",
    "Energy intensity level of primary energy (megajoules per constant 2021 purchasing power parity GDP)": "Energy intensity measures how efficiently energy is used in an economy. Lower values mean more economic output per unit of energy.",
    "International financial flows to developing countries in support of clean energy research and development and renewable energy production, including in hybrid systems (millions of constant 2023 United States dollars)": "Track financial support flowing to developing countries for clean energy. Shows global commitment to sustainable energy transition."
   
}

# Show the description for the selected indicator
st.info(indicator_descriptions[selected_indicator])


# FILTER THE DATA:

# Filter by the chosen indicator
indicator_df = df[df["SeriesDescription"] == selected_indicator]

# Filter by the chosen year
year_df = indicator_df[indicator_df["TimePeriod"] == selected_year]

# KEY METRICS ROW
st.subheader(f"Key Stats for {selected_year}")

# Splits the page into 3 equal columns side by side
col1, col2, col3 = st.columns(3)

world_data = year_df[year_df["GeoAreaName"] == "World"]
if not world_data.empty:
    # Gets the first value, rounds it to 1 decimal place, displays as metric box in column 1
    global_value = round(world_data["Value"].values[0], 1)
    col1.metric("Global Average", global_value)
else:
    col1.metric("Global Average", "No data")

# Anything below 900 is a real country
countries_only = year_df[year_df["GeoAreaCode"] < 900]
if not countries_only.empty:
    highest = countries_only.loc[countries_only["Value"].idxmax()]
    col2.metric("Highest Country", highest["GeoAreaName"], round(highest["Value"], 1))

    lowest = countries_only.loc[countries_only["Value"].idxmin()]
    col3.metric("Lowest Country", lowest["GeoAreaName"], round(lowest["Value"], 1), delta_color="inverse")

# Just draws a horizontal line to separate sections
st.divider()


# MAP + LINE CHART (side by side)
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
        color="Value",                  # colour countries based on their value
        hover_name="GeoAreaName",       # show country name when hovering
        color_continuous_scale="Blues", # blue colour scale — avoids red/green colour blindness issue
        title=f"{selected_year}"
    )

    # Make the map background transparent so it matches the dashboard theme
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",                      # transparent outer background
        geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False), # transparent map background
        margin=dict(t=30, b=0, l=0, r=0),                  # reduce whitespace around the map
        coloraxis_showscale=False                           # hide the colour scale bar
    )

    # Display the map in the app
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption("Darker blue indicates higher values. Hover over a country to see its exact value.")
    st.caption("NOTE: Some countries may appear blank due to limited data availability in the UN SDG database.")

with col_line:
    # Subheading for the line chart section
    st.subheader("Trend Over Time")

    # Only show the chart if the user has selected at least one country
    if selected_countries:
        # Filter data to only include the countries the user selected
        trend_df = indicator_df[indicator_df["GeoAreaName"].isin(selected_countries)]

        # Create the line chart using plotly
        fig_line = px.line(
            trend_df,
            x="TimePeriod",       # year on the x axis
            y="Value",            # indicator value on the y axis
            color="GeoAreaName",  # different colour line for each country
            markers=True,         # show dots on each data point
            title="Trend by Country",
            labels={"TimePeriod": "Year", "Value": "Value", "GeoAreaName": "Country"}
        )

        # Clean up the layout
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", # transparent background
            margin=dict(t=40, b=0, l=0, r=0),
            yaxis_title=""               # remove y axis label to avoid overlap
        )

        # Display the chart
        st.plotly_chart(fig_line, use_container_width=True)
        st.caption("Select countries in the sidebar to compare how they have progressed over time.")

    else:
        # Show a message if no countries are selected
        st.info("Please select at least one country in the sidebar.")

st.divider()


# BOTTOM 10 + GLOBAL TREND(side by side)
col_bar, col_global = st.columns(2)

with col_bar:
    # Bottom 10 countries bar chart
    st.subheader(f"Bottom 10 Countries — {selected_year}")

    # Only use real countries, filter out regional groupings
    bar_df = year_df[year_df["GeoAreaCode"] < 900]

    bottom10 = bar_df.nsmallest(10, "Value")

    # Create the horizontal bar chart
    fig_bar = px.bar(
        bottom10,
        x="Value",          # value on the x axis
        y="GeoAreaName",    # country name on the y axis
        orientation="h",    # horizontal bars
        title=f"Bottom 10 Countries — {selected_year}",
        labels={"Value": "Value", "GeoAreaName": "Country"},
        color_discrete_sequence=["#1f77b4"]  # single solid blue colour
    )

    # Sort bars so lowest is at the bottom
    fig_bar.update_layout(
        yaxis={"categoryorder": "total ascending"},
        paper_bgcolor="rgba(0,0,0,0)", # transparent background
        margin=dict(t=40, b=0, l=0, r=0),
        showlegend=False
    )

    # Display the chart
    st.plotly_chart(fig_bar, use_container_width=True)
    st.caption("These are the countries that need the most attention for global sustainability goals.")

with col_global:
    # Global trend chart — shows world average over time for selected indicator
    st.subheader("Global Trend Over Time")

    # Filter to only the World row for the selected indicator
    global_trend = indicator_df[indicator_df["GeoAreaName"] == "World"]

    # Only show if world data exists for this indicator
    if not global_trend.empty:
        fig_global = px.line(
            global_trend,
            x="TimePeriod",    # year on x axis
            y="Value",         # value on y axis
            markers=True,      # show dots on each data point
            title=f"Global Average — {selected_label}",
            labels={"TimePeriod": "Year", "Value": "Value"}
        )

        # Clean up layout
        fig_global.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", # transparent background
            margin=dict(t=40, b=0, l=0, r=0),
            yaxis_title=""
        )

        # Display the chart
        st.plotly_chart(fig_global, use_container_width=True)
        st.caption("This chart shows the global average progress over time. An upward trend indicates worldwide improvement.")

    else:
        st.info("No global average data available for this indicator.")

st.divider()

# FOOTER
st.caption("Data source: UN SDG Global Database | Goal 7: Affordable and Clean Energy")