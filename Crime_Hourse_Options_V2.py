import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import pgeocode

import pandas as pd

Datafile = "incidents_part1_2.feather"
df = pd.read_feather(Datafile)

@st.cache_data
def read_data(df, num_examples=1000):
    df = df.dropna(subset=['lat', 'lng', 'text_general_code', 'dispatch_time'])

    data = []
    for index, row in df.iterrows():
        data.append({
            'name': row['text_general_code'],
            'latitude': row['lat'],
            'longitude': row['lng'],
            'crime_type': row['text_general_code'],
            'dispatch_time': row['dispatch_time']
        })

    return data

def get_time_of_day(timestamp):
    hour = int(timestamp.split(":")[0])
    if 6 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 18:
        return 'Afternoon'
    else:
        return 'Evening'

data = read_data(df)

st.sidebar.header("Please provide your location to get the nearest service")
st.sidebar.header("User Input")

option = st.sidebar.radio("Select Option", ["User Location", "Manual Input"])
crime_types = df['text_general_code'].unique()
crime_type = st.sidebar.selectbox("Choose Crime Type", crime_types)
time_of_day_options = ['Morning', 'Afternoon', 'Evening']
time_of_day = st.sidebar.selectbox("Choose Time of Day", time_of_day_options)
filtered_data = [loc for loc in data if loc['crime_type'] == crime_type and get_time_of_day(loc['dispatch_time']) == time_of_day]

# Initialize the radius variable
circle_radius = 80

if option == "User Location":
    try:
        loc = get_geolocation()
        latitude_user = loc['coords']['latitude']
        longitude_user = loc['coords']['longitude']
        st.sidebar.write(f"Your coordinates are {latitude_user}, {longitude_user}")

        # Slider for adjusting the circle radius
        # Change font using markdown
        st.markdown(f"<span style='font-family: Arial; font-size: 18px;'>Adjust Circle Radius (meters)</span>", unsafe_allow_html=True)
        circle_radius = st.slider("", min_value=10, max_value=200, value=circle_radius)

        map = folium.Map(location=[latitude_user, longitude_user], zoom_start=12)
        folium.Marker(
            location=[latitude_user, longitude_user],
            popup='Your Location',
            icon=folium.Icon(color='red')
        ).add_to(map)

        folium.CircleMarker(
            location=[latitude_user, longitude_user],
            radius=circle_radius,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.2
        ).add_to(map)

        marker_cluster = MarkerCluster().add_to(map)

        for loc in filtered_data:
            location = loc['latitude'], loc['longitude']
            crime_type = loc['crime_type']
            time_of_day = get_time_of_day(loc['dispatch_time'])
            popup = f"{crime_type} ({time_of_day})"
            folium.Marker(location, popup=popup).add_to(marker_cluster)

        st.header(f"{crime_type} Incidents in Philly ({time_of_day})")
        folium_static(map, width=700, height=800)

    except Exception as e:
        st.sidebar.error(f"Error retrieving location: {e}")

else:
    # Slider for adjusting the circle radius in the manual input option
    zip_code = st.sidebar.text_input("Enter ZIP Code", "")
    # Slider for adjusting the circle radius
    circle_radius = st.sidebar.slider("Adjust Circle Radius (meters)", min_value=10, max_value=200, value=circle_radius)
    
    submit_button = st.sidebar.button("Submit")

    if submit_button:
        # Use pgeocode for geocoding
        nomi = pgeocode.Nominatim('us')
        location_info = nomi.query_postal_code(zip_code)

        if not location_info.empty and not location_info[['latitude', 'longitude', 'place_name']].isna().any().any():
            latitude_user = location_info['latitude'].item()
            longitude_user = location_info['longitude'].item()
            city_name = location_info['place_name']

            st.sidebar.write(f"Coordinates for {zip_code} ({city_name}): {latitude_user}, {longitude_user}")

            map = folium.Map(location=[latitude_user, longitude_user], zoom_start=12)
            folium.CircleMarker(
                location=[latitude_user, longitude_user],
                radius=circle_radius,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.2
            ).add_to(map)

            marker_cluster = MarkerCluster().add_to(map)

            for loc in filtered_data:
                location = loc['latitude'], loc['longitude']
                crime_type = loc['crime_type']
                time_of_day = get_time_of_day(loc['dispatch_time'])
                popup = f"{crime_type} ({time_of_day})"
                folium.Marker(location, popup=popup).add_to(marker_cluster)

            st.header(f"{crime_type} Incidents in {city_name} ({time_of_day})")
            folium_static(map, width=700, height=800)

        else:
            st.sidebar.error(f"Error: Unable to retrieve valid location information for ZIP code {zip_code}")

