import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from folium.plugins import MarkerCluster
from streamlit_js_eval import streamlit_js_eval, get_geolocation

import pandas as pd

Datafile = "https://raw.githubusercontent.com/HassanShafei/ShelterCrimeData/main/incidents_part1_2.feather"

df = pd.read_feather(Datafile)

@st.cache_data
def read_data(df, num_examples=2000):
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
# Sidebar for user input
st.sidebar.header("Please provide your location to get the nearest service")

st.sidebar.header("User Input")


# Select between user location and manual input
option = st.sidebar.radio("Select Option", ["User Location", "Manual Input"])

if option == "User Location":
    # Option 1: Get user's location
    try:
        loc = get_geolocation()
        latitude_user = loc['coords']['latitude']
        longitude_user = loc['coords']['longitude']
        st.sidebar.write(f"Your coordinates are {latitude_user}, {longitude_user}")

        # Draw a circle around the user's location
        circle_radius = 80  # in meters
        map = folium.Map(location=[latitude_user, longitude_user], zoom_start=12)
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
        st.sidebar.error(f"Error retrieving location: {e}")

else:
    # Option 2: Enter city and zip code
    city = st.sidebar.text_input("Enter City", "")
    zip_code = st.sidebar.text_input("Enter ZIP Code", "")

    submit_button = st.sidebar.button("Submit")

    if submit_button:
        try:
            geolocator = Nominatim(user_agent="my_geocoder")
            location = geolocator.geocode(f"{city}, {zip_code}")
            latitude_user, longitude_user = location.latitude, location.longitude
            st.sidebar.write(f"Coordinates for {city}, {zip_code}: {latitude_user}, {longitude_user}")

            # Draw a circle around the zip code area
            circle_radius = 5000  # in meters
            map = folium.Map(location=[latitude_user, longitude_user], zoom_start=12)
            folium.Circle(
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
            st.sidebar.error(f"Error retrieving location: {e}")
