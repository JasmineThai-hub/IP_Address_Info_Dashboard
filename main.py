import streamlit as st
import requests
import socket
import pydeck as pdk
import re
import whois

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


@st.cache_data
def get_ip_info(ip_address):
    try:
        response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        return response.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def is_domain(input_string):
    pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$"
    return re.match(pattern, input_string)

def get_whois_info(domain):
    try:
        whois_info = whois.whois(domain)
        return {
            "Domain Name": whois_info.domain_name,
            "Registrar": whois_info.registrar,
            "Creation Date": whois_info.creation_date,
            "Expiration Date": whois_info.expiration_date,
            "Last Updated": whois_info.updated_date
        }
    except Exception as e:
        st.error(f"Error fetching WHOIS information: {e}")
        return None


st.title("Jasmine's IP & Domain Lookup")

user_input = st.text_input("Enter an IP Address or Domain Name:", value='google.com')

if is_domain(user_input):
    ip_address = domain_to_ip(user_input)
    if ip_address:
        st.write(f"Resolved Domain {user_input} to IP Address: {ip_address}")
    else:
        st.error(f"Could not resolve domain: {user_input}")
        st.stop()
else:
    ip_address = user_input

if st.button("Fetch Details"):
    with st.spinner("Fetching details..."):
        details = get_ip_info(ip_address)
        whois_info = get_whois_info(user_input)

    if details:
        data = {
            "IP Address": details.get("ip", "N/A"),
            "City": details.get("city", "N/A"),
            "Region": details.get("region", "N/A"),
            "Country": details.get("country", "N/A"),
            "Organization": details.get("org", "N/A")
        }
        st.table(data)

        if whois_info:
            st.subheader("WHOIS Information")
            st.table(whois_info)

        location = details.get("loc", "N/A").split(',')
        if len(location) == 2:
            display_map(float(location[0]), float(location[1]))
