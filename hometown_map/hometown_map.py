# filename: generate_map.py

import os
import requests
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import urllib.parse

# ----------------------------
# Configuration
# ----------------------------
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")  # Make sure to set your token in terminal
MAPBOX_STYLE = "valdez-aili/cmm3r3a2q00dw01s1b90q89g0"  # Change if needed
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(BASE_DIR, "hometown_locations.csv")
df = pd.read_csv(INPUT_CSV)  # Load CSV to check if it exists before proceeding
CACHE_FILE = os.path.join(BASE_DIR, "geocode_cache.csv")  # Stores geocoding results to save API calls

# ----------------------------
# Helper functions
# ----------------------------
def geocode_address(address):
    """Return latitude, longitude for an address using Mapbox."""
    encoded = urllib.parse.quote(address)
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded}.json"
    params = {"access_token": MAPBOX_TOKEN, "limit": 1}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["features"]:
            lon, lat = data["features"][0]["center"]
            return lat, lon
    except Exception as e:
        print(f"Error geocoding '{address}': {e}")
    return None, None

# ----------------------------
# Load data
# ----------------------------
if not os.path.exists(INPUT_CSV):
    print(f"Error: {INPUT_CSV} not found in current folder.")
    exit()

df = pd.read_csv("hometown_locations.csv")
df.columns = df.columns.str.strip()  # remove extra spaces
df["latitude"] = None
df["longitude"] = None

# ----------------------------
# Load or create geocode cache
# ----------------------------
if os.path.exists(CACHE_FILE):
    cache_df = pd.read_csv(CACHE_FILE)
else:
    cache_df = pd.DataFrame(columns=["Address", "latitude", "longitude"])

# ----------------------------
# Geocode addresses
# ----------------------------
for idx in df.index:
    addr = df.loc[idx, "Address"]
    # Check cache first
    cached = cache_df[cache_df["Address"] == addr]
    if not cached.empty:
        df.loc[idx, "latitude"] = cached.iloc[0]["latitude"]
        df.loc[idx, "longitude"] = cached.iloc[0]["longitude"]
        continue

    lat, lon = geocode_address(addr)
    df.loc[idx, "latitude"] = lat
    df.loc[idx, "longitude"] = lon
    # Save to cache
cache_df = cache_df.append({"Address": addr, "latitude": lat, "longitude": lon}, ignore_index=True)
# Save cache
cache_df.to_csv(CACHE_FILE, index=False)

# ----------------------------
# Drop rows without coordinates
# ----------------------------
df = df.dropna(subset=["latitude", "longitude"])
if df.empty:
    print("No valid coordinates found. Exiting.")
    exit()

# ----------------------------
# Create Folium map
# ----------------------------
center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()

tile_url = f"https://api.mapbox.com/styles/v1/{MAPBOX_STYLE}/tiles/256/{{z}}/{{x}}/{{y}}?access_token={MAPBOX_TOKEN}"

import folium

# Example map centered at some location
m = folium.Map(location=[33.150, -96.900], zoom_start=12)
# Add marker cluster
marker_cluster = MarkerCluster().add_to(m)
for _, row in df.iterrows():
    popup_html = f"""
<b>{row['Name']}</b><br>
{row['Address']}<br>
<img src="https://example.com/photo1.jpg" width="200">
"""
    print(row['Name'], row['image_url'])
    folium.Marker(
    location=[row["latitude"], row["longitude"]],
    popup=folium.Popup(popup_html, max_width=300)
).add_to(marker_cluster)
    
import os
import base64
import pandas as pd
import folium
from folium.plugins import MarkerCluster

# ----------------------------
# Load CSV
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(BASE_DIR, "hometown_locations.csv")
df = pd.read_csv(INPUT_CSV)
df.columns = df.columns.str.strip()  # remove extra spaces

# ----------------------------
# Example: latitude and longitude already in CSV
# ----------------------------
# If you need to geocode, include your geocode logic here

# ----------------------------
# Helper: convert local image to base64
# ----------------------------
def img_to_base64(path):
    """Return base64 string for local image; if not found, return empty string."""
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(path)[1][1:].lower()  # png, jpg, etc
    return f"data:image/{ext};base64,{encoded}"

# ----------------------------
# Create Folium map
# ----------------------------
center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()
m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

marker_cluster = MarkerCluster().add_to(m)

for _, row in df.iterrows():
    # Determine image source
    if pd.isna(row["image_url"]):
        img_src = ""
    elif row["image_url"].startswith("http"):
        img_src = row["image_url"]  # web URL
    else:
        # local file → convert to base64
        img_path = os.path.join(BASE_DIR, row["image_url"])
        img_src = img_to_base64(img_path)
    
    popup_html = f"""
    <b>{row['Name']}</b><br>
    {row['Address']}<br>
    <img src="{img_src}" width="200">
    """
    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(marker_cluster)

# ----------------------------
# Save map
# ----------------------------
output_file = os.path.join(BASE_DIR, "interactive_map.html")
m.save(output_file)
print(f"Map saved at {output_file}")

# ----------------------------
# Save map
# ----------------------------
# ----------------------------
# Save map
# ----------------------------
# ----------------------------
# Save map as HTML
# ----------------------------
import os

# Save in the same folder as the script
output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interactive_map.html")
m.save(output_file)

print(f"Map saved successfully at: {output_file}")