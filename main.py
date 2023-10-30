import streamlit as st
import requests
import socket
import pydeck as pdk

def domain_to_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None

def display_map(latitude, longitude):
    view_state = pdk.ViewState(
        latitude=latitude,
        longitude=longitude,
        zoom=10,
        pitch=40.5,
        bearing=-27.36
    )

    # Define the map layer
    layer = pdk.Layer(
        "HexagonLayer",
        data=[{"latitude": latitude, "longitude": longitude}],
        get_position="[longitude,latitude]",
        radius=500,
        elevation_scale=4,
        elevation_range=[0, 1000],
        pickable=True,
        extruded=True,
    )

    # Render the map
    map_ = pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=view_state,
        layers=[layer],
    )
    st.pydeck_chart(map_)


def get_ip_info(ip_address):
    try:
        response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        return response.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return None

st.title("Jasmine's IP & Domain Lookup")

user_input = st.text_input("Enter an IP Address or Domain Name:", value='google.com')

# Domain to IP conversion if applicable
if "." in user_input:
    if not any(c.isdigit() for c in user_input):
        ip_address = domain_to_ip(user_input)
        if ip_address:
            st.write(f"Resolved Domain {user_input} to IP Address: {ip_address}")
        else:
            st.error(f"Could not resolve domain: {user_input}")
            st.stop()
    else:
        ip_address = user_input
else:
    ip_address = user_input

if st.button("Fetch Details"):
    details = get_ip_info(ip_address)
    if details:
        st.write("IP Address:", details.get("ip", "N/A"))
        st.write("City:", details.get("city", "N/A"))
        st.write("Region:", details.get("region", "N/A"))
        st.write("Country:", details.get("country", "N/A"))
        st.write("Organization:", details.get("org", "N/A"))
        location = details.get("loc", "N/A").split(',')
        if len(location) == 2:
            display_map(float(location[0]), float(location[1]))