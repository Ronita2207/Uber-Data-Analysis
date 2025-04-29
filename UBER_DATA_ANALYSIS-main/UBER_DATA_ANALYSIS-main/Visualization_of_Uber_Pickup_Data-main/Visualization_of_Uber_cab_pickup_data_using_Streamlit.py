# Import libraries
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

# Setting page configuration as the first Streamlit command
st.set_page_config(
    page_title="Visualization of Uber cab pickup data using Streamlit",
    page_icon="./image/taxi_image.jpg",
    layout="wide",
    menu_items={
        'About': "# Visualization of Uber cab pickup data using Streamlit\n"
                 "The project focuses on answering questions such as which hour of the day is most "
                 "busy or which place has the least pickups or any possible information that could be "
                 "extracted from the pick-up and drop-off data."
    }
)

# Initializing variables
data = pd.DataFrame()

# Load data once
@st.cache_resource
def load_data():
    data = pd.read_csv(
        "Bhopal Dataset(csv).csv",
        nrows=30000,  # taking 90% of data approximately
        names=["date/time", "lat", "lon"],  # specify names directly since they don't change
        skiprows=1,  # don't read header since names specified directly
        usecols=[0, 1, 2],
        parse_dates=["date/time"],  # set as datetime instead of converting after the fact
    )
    return data

# Function for airport map and railway stations
def map(data, lat, lon, zoom):
    st.write(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/streets-v11",
            initial_view_state={
                "latitude": lat,
                "longitude": lon,
                "zoom": zoom,
                "pitch": 50
            },
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data=data,
                    get_position=["lon", "lat"],
                    radius=100,
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                ),
            ],
        )
    )

# Filter data for a specific hour, cache
@st.cache_data
def filterdata(df, hour_selected):
    return df[df["date/time"].dt.hour == hour_selected]

# Calculate midpoint for given set of data
@st.cache_data
def mpoint(lat, lon):
    return (np.average(lat), np.average(lon))

# Filter data by hour
@st.cache_data
def histdata(df, hr):
    filtered = data[(df["date/time"].dt.hour >= hr) & (df["date/time"].dt.hour < (hr + 1))]
    hist = np.histogram(filtered["date/time"].dt.minute, bins=60, range=(0, 60))[0]
    return pd.DataFrame({"minute": range(60), "pickups": hist})

def main():
    global data

    # Streamlit app layout
    data = load_data()

    # Laying out the top section of the app
    row1_1, row1_2 = st.columns((2, 3))

    with row1_1:
        st.title("Bhopal Uber Ridesharing Data")
        hour_selected = st.slider("Select hour of pickup", 0, 23)

    with row1_2:
        st.write(
            """
            ## Examining how Uber pickups vary over time in Bhopal City, at its airport and its railway stations.
            By sliding the slider on the left you can view different slices of time and explore different transportation trends.
            """
        )

    # Laying out the middle section of the app with the maps
    row2_1, row2_2, row2_3, row2_4 = st.columns((2, 1, 1, 1))

    # Setting the zoom locations for the airport and railway stations
    raja_bhoj = [23.290374, 77.333208]
    railway = [23.26776, 77.414001]
    kamlapati = [23.2231274171, 77.4397832066]
    zoom_level = 12
    midpoint = mpoint(data["lat"], data["lon"])

    with row2_1:
        st.write(f"""*All Bhopal City from {hour_selected}:00 and {(hour_selected + 1) % 24}:00*""")
        map(filterdata(data, hour_selected), midpoint[0], midpoint[1], 11)

    with row2_2:
        st.write("*Raja Bhoj International Airport*")
        map(filterdata(data, hour_selected), raja_bhoj[0], raja_bhoj[1], zoom_level)

    with row2_3:
        st.write("*Bhopal Junction Railway Station*")
        map(filterdata(data, hour_selected),  railway[0],  railway[1], zoom_level)

    with row2_4:
        st.write("*Kamlapati Railway Station*")
        map(filterdata(data, hour_selected),  kamlapati[0],  kamlapati[1], zoom_level)

    # Calculating data for the histogram
    chart_data = histdata(data, hour_selected)

    # Laying out the histogram section
    st.write(f"""*Breakdown of rides per minute between {hour_selected}:00 and {(hour_selected + 1) % 24}:00*""")

    st.altair_chart(
        alt.Chart(chart_data)
        .mark_area(
            interpolate="step-after",
        )
        .encode(
            x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
            y=alt.Y("pickups:Q"),
            tooltip=["minute", "pickups"],
        )
        .configure_mark(opacity=0.2, color="red"),
        use_container_width=True,
    )

main()