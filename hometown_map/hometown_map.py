import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster

# ----------------------------
# Configuration
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(BASE_DIR, "hometown_locations.csv")
CACHE_FILE = os.path.join(BASE_DIR, "geocode_cache.csv")

# ----------------------------
# Load CSV and geocode cache
# ----------------------------
df = pd.read_csv(INPUT_CSV)
df.columns = df.columns.str.strip()  # remove extra spaces

# Load cached coordinates
cache_df = pd.read_csv(CACHE_FILE)
cache_df.columns = cache_df.columns.str.strip()

# Merge data with cached coordinates
df = df.merge(cache_df, on="Address", how="left")

# Drop rows without coordinates
df = df.dropna(subset=["latitude", "longitude"])

if df.empty:
    print("No valid coordinates found. Exiting.")
    exit()

# ----------------------------
# Create Folium map
# ----------------------------
center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

marker_cluster = MarkerCluster().add_to(m)

# ----------------------------
# Add markers with popups including images
# ----------------------------
for _, row in df.iterrows():
    # Get image URL
    img_src = ""
    if not pd.isna(row.get("Image_URL")):
        img_src = row["Image_URL"]
        if isinstance(img_src, str) and img_src.startswith("http://"):
            img_src = "https://" + img_src[len("http://"):]
    
    # Create popup HTML with image
    popup_html = f"""
    <div style="width: 250px; font-family: Arial, sans-serif;">
        <h4 style="margin: 5px 0;">{row['Name']}</h4>
        <p style="margin: 5px 0; font-size: 12px;">{row['Address']}</p>
        <p style="margin: 5px 0; font-size: 11px; color: #666;">{row.get('Type', '')}</p>
    """
    
    # Add image if available
    if img_src:
        popup_html += f"""
        <img src="{img_src}" 
             style="width: 220px; height: 140px; object-fit: cover; border-radius: 5px; margin-top: 8px;">
        """
    
    if not pd.isna(row.get("Description")):
        popup_html += f"""
        <p style="margin: 8px 0; font-size: 11px;">{row['Description']}</p>
        """
    
    popup_html += "</div>"
    
    popup = folium.Popup(folium.Html(popup_html, script=True), max_width=320)

    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=popup
    ).add_to(marker_cluster)

# ----------------------------
# Save map
# ----------------------------
output_file = os.path.join(BASE_DIR, "interactive_map.html")
m.save(output_file)
print(f"Map saved at {output_file}")