import streamlit as st
import folium
from streamlit_folium import folium_static

from folium.plugins import MarkerCluster
from streamlit_js_eval import streamlit_js_eval, get_geolocation

import pandas as pd

Datafile = "incidents_part1_part2-2.csv"

df = pd.read_csv(Datafile)

@st.cache_data
def read_data(df, num_examples=1000):
    df = df.dropna(subset=['lat', 'lng'])
    df = df.sample(n=min(num_examples, len(df)))

    data = []
    for index, row in df.iterrows():
        data.append({
            'name': row['text_general_code'],
            'latitude': row['lat'],
            'longitude': row['lng']
        })

    return data

data = read_data(df)

# Button to initiate the process of getting the user's location
if st.checkbox("Get My Location"):
    try:
        loc = get_geolocation()
        latitude_user = loc['coords']['latitude']
        longitude_user = loc['coords']['longitude']
        st.write(f"Your coordinates are {latitude_user}, {longitude_user}")

        # Slider for adjusting the circle radius
        circle_radius = st.slider("Adjust Circle Radius (meters)", min_value=10, max_value=200, value=80)

        # Plot the map
        map = folium.Map(location=[latitude_user, longitude_user], zoom_start=12)
        folium.Marker(
            location=[latitude_user, longitude_user],
            popup='Your Location',
            icon=folium.Icon(color='red')
        ).add_to(map)

        # Draw a circle around the user's location
        folium.CircleMarker(
            location=[latitude_user, longitude_user],
            radius=circle_radius,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.2
        ).add_to(map)

        # Create a MarkerCluster layer to group your data points
        marker_cluster = MarkerCluster().add_to(map)

        # Add data points to the map
        for loc in data:
            location = loc['latitude'], loc['longitude']
            popup = loc['name']
            folium.Marker(location, popup=popup).add_to(marker_cluster)

        # Render the map
        st.header("Homeless Shelters and Crime in Philly")
        folium_static(map, width=700, height=800)

    except Exception as e:
        st.error(f"Error retrieving location: {e}")
