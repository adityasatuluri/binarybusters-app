import streamlit as st
import pandas as pd
import joblib
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(r'test-13da9-firebase-adminsdk-astns-f7b4f3b9e4.json')
if not firebase_admin._apps:
    # Initialize Firebase app if not already initialized
    firebase_admin.initialize_app(cred)
else:
    # If already initialized, pass
    pass

# Initialize Firestore
db = firestore.client()

# Load the model and scaler
model = joblib.load(r'best_flood_model.pkl')
scaler = joblib.load(r'scaler.pkl')

# Streamlit app
st.title("Flood Risk Prediction Application")
st.write("Enter the environmental and weather parameters to predict flood risk.")

# User input fields for weather and environmental data
rainfall = st.number_input("Rainfall (mm)", min_value=0, value=150)
temperature = st.number_input("Temperature (°C)", min_value=-10, value=30)
humidity = st.number_input("Humidity (%)", min_value=0, max_value=100, value=70)
river_discharge = st.number_input("River Discharge (m³/s)", min_value=0, value=20000)
water_level = st.number_input("Water Level (m)", min_value=0.0, value=5.0)
elevation = st.number_input("Elevation (m)", min_value=0, value=200)
population_density = st.number_input("Population Density", min_value=0, value=5000)
infrastructure = st.selectbox("Infrastructure (1: Yes, 0: No)", [0, 1])
historical_floods = st.selectbox("Historical Floods (1: Yes, 0: No)", [0, 1])

# Land Cover and Soil Type (One-Hot Encoded)
st.subheader("Land Cover")
land_cover_options = ['Agricultural', 'Desert', 'Forest', 'Urban', 'Water Body']
land_cover = st.radio("Select Land Cover Type", land_cover_options)

st.subheader("Soil Type")
soil_type_options = ['Clay', 'Loam', 'Peat', 'Sandy', 'Silt']
soil_type = st.radio("Select Soil Type", soil_type_options)

# Add Latitude and Longitude input fields
st.subheader("Location (Latitude and Longitude)")
latitude = st.number_input("Latitude (e.g., 18.86166)", min_value=-90.0, max_value=90.0, value=18.86166)
longitude = st.number_input("Longitude (e.g., 78.835584)", min_value=-180.0, max_value=180.0, value=78.835584)

# Optionally, show the map
st.map(pd.DataFrame({'lat': [latitude], 'lon': [longitude]}))

# Prepare the input DataFrame
data = {
    'Rainfall (mm)': [rainfall],
    'Temperature (°C)': [temperature],
    'Humidity (%)': [humidity],
    'River Discharge (m³/s)': [river_discharge],
    'Water Level (m)': [water_level],
    'Elevation (m)': [elevation],
    'Population Density': [population_density],
    'Infrastructure': [infrastructure],
    'Historical Floods': [historical_floods],
    'Land Cover_Agricultural': [1 if land_cover == 'Agricultural' else 0],
    'Land Cover_Desert': [1 if land_cover == 'Desert' else 0],
    'Land Cover_Forest': [1 if land_cover == 'Forest' else 0],
    'Land Cover_Urban': [1 if land_cover == 'Urban' else 0],
    'Land Cover_Water Body': [1 if land_cover == 'Water Body' else 0],
    'Soil Type_Clay': [1 if soil_type == 'Clay' else 0],
    'Soil Type_Loam': [1 if soil_type == 'Loam' else 0],
    'Soil Type_Peat': [1 if soil_type == 'Peat' else 0],
    'Soil Type_Sandy': [1 if soil_type == 'Sandy' else 0],
    'Soil Type_Silt': [1 if soil_type == 'Silt' else 0],
}

new_data = pd.DataFrame(data)

# Scale the input data
new_data_scaled = scaler.transform(new_data)

# Predict flood risk
pred = 0

if st.button("Predict Flood Risk"):
    prediction = model.predict(new_data_scaled)
    pred = prediction[0]
    
    if prediction[0] == 1:
        st.error("⚠️ Flood Risk: HIGH")
    else:
        st.success("✅ Flood Risk: LOW")

    # Convert numpy.int64 to int before adding to Firestore
    data2 = {
        'Latitude': float(latitude),
        'Longitude': float(longitude),
        'Rainfall (mm)': float(rainfall),
        'Temperature (°C)': float(temperature),
        'Humidity (%)': float(humidity),
        'River Discharge (m³/s)': float(river_discharge),
        'Water Level (m)': float(water_level),
        'Elevation (m)': float(elevation),
        'Land Cover_Agricultural': int(1 if land_cover == 'Agricultural' else 0),
        'Land Cover_Desert': int(1 if land_cover == 'Desert' else 0),
        'Land Cover_Forest': int(1 if land_cover == 'Forest' else 0),
        'Land Cover_Urban': int(1 if land_cover == 'Urban' else 0),
        'Land Cover_Water Body': int(1 if land_cover == 'Water Body' else 0),
        'Soil Type_Clay': int(1 if soil_type == 'Clay' else 0),
        'Soil Type_Loam': int(1 if soil_type == 'Loam' else 0),
        'Soil Type_Peat': int(1 if soil_type == 'Peat' else 0),
        'Soil Type_Sandy': int(1 if soil_type == 'Sandy' else 0),
        'Soil Type_Silt': int(1 if soil_type == 'Silt' else 0),
        'Population Density': int(population_density),
        'Infrastructure': int(infrastructure),
        'Historical Floods': int(historical_floods),
        'Flood Occurred': int(pred),
    }

    # Insert the data into Firestore
    collection_ref = db.collection('flood_risk_data')
    collection_ref.add(data2)
    st.write("Data added to Firestore successfully!")