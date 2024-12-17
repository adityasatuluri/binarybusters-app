import streamlit as st
import folium
from folium.plugins import MarkerCluster
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(r'D:\STUDY\PROJECTS\Freelance Projects\flood-prediction-app\test-13da9-firebase-adminsdk-astns-f7b4f3b9e4.json')
if not firebase_admin._apps:
    # Initialize Firebase app if not already initialized
    firebase_admin.initialize_app(cred)
else:
    # If already initialized, pass
    pass

# Initialize Firestore
db = firestore.client()

# Function to retrieve latitude and longitude from Firestore
def get_lat_lon_from_firestore():
    # Reference to the collection
    collection_ref = db.collection('flood_risk_data')
    
    # Get all documents from the collection
    docs = collection_ref.stream()
    
    # List to store latitude and longitude
    lat_lon_list = []
    
    # Loop through each document and extract latitude and longitude
    for doc in docs:
        doc_data = doc.to_dict()
        latitude = doc_data.get('Latitude')
        longitude = doc_data.get('Longitude')
        
        # Append to the list if both latitude and longitude are present
        if latitude and longitude:
            lat_lon_list.append([latitude, longitude])
    
    return lat_lon_list

# Streamlit app
st.title("Flood Risk Locations Map")
st.write("Map of all places where floods occurred and the precipitation was higher than 200 mm.")

# Retrieve latitude and longitude data from Firestore
lat_lon_data = get_lat_lon_from_firestore()

# Create a map centered around the average latitude and longitude
if lat_lon_data:
    map_center = [sum([lat for lat, lon in lat_lon_data]) / len(lat_lon_data), 
                  sum([lon for lat, lon in lat_lon_data]) / len(lat_lon_data)]
    my_map = folium.Map(location=map_center, zoom_start=5)

    # Add marker cluster to the map
    marker_cluster = MarkerCluster().add_to(my_map)

    # Add markers for each latitude and longitude
    for lat, lon in lat_lon_data:
        folium.Marker(
            location=[lat, lon],
            popup=f"Latitude: {lat}, Longitude: {lon}"
        ).add_to(marker_cluster)

    # Display the map in Streamlit using folium
    st.write("### Flood Risk Locations")
    st.components.v1.html(my_map._repr_html_(), height=600)
else:
    st.write("No data available to display on the map.")
