import pandas as pd
import geopandas as gpd
import folium
import streamlit as st
from streamlit_folium import st_folium
from branca.element import Template, MacroElement

st.title(" NWS Heat Risk Map")
# --- Default base map ---
m = folium.Map(location=[40.7128, -74.0060], zoom_start=9, tiles="CartoDB positron")

# --- Add NWS HeatRisk WMS Layer ---
folium.raster_layers.WmsTileLayer(
    url="https://mapservices.weather.noaa.gov/experimental/services/NWS_HeatRisk/ImageServer/WMSServer?",
    layers="NWS_HeatRisk",
    fmt="image/png",
    transparent=True,
    attr="NOAA/NWS HeatRisk"
).add_to(m)

# --- Custom Legend ---
legend_html = """
{% macro html(this, kwargs) %}

<div style="
    position: fixed; 
    bottom: 30px; left: 30px; width: 200px; z-index:9999; 
    font-size:14px; background-color:white; 
    border:2px solid grey; border-radius:6px; 
    padding: 10px;
    ">
    <b>Heat Risk Categories</b><br>
    <i style="background: #d9f0d3; width: 15px; height: 15px; float: left; margin-right: 5px; opacity:0.7;"></i> Green (0) - Little/no risk<br>
    <i style="background: #ffff99; width: 15px; height: 15px; float: left; margin-right: 5px; opacity:0.7;"></i> Yellow (1) - Minor<br>
    <i style="background: #f46d43; width: 15px; height: 15px; float: left; margin-right: 5px; opacity:0.7;"></i> Orange (2) - Moderate<br>
    <i style="background: #d73027; width: 15px; height: 15px; float: left; margin-right: 5px; opacity:0.7;"></i> Red (3) - Major<br>
    <i style="background: #762a83; width: 15px; height: 15px; float: left; margin-right: 5px; opacity:0.7;"></i> Magenta (4) - Extreme
</div>

{% endmacro %}
"""

legend = MacroElement()
legend._template = Template(legend_html)
m.get_root().add_child(legend)

# --- Display map in Streamlit ---
st_folium(m, width=900, height=600)

#——————————————————————————————————————————————————————————————————————————————————————————————————————

st.title("NYC Heat Vulnerability Index Map")

# ---- Load Data ----
# Upload or hardcode file paths
hvi_csv = "data/hvi-nta-2020.csv"
nta_geojson = "data/Neighborhood Areas1.geojson"

hvi_df = pd.read_csv(hvi_csv)
nta_gdf = gpd.read_file(nta_geojson)

# Merge GeoJSON (nta2020) with CSV (NTACode)
merged = nta_gdf.merge(hvi_df, left_on="nta2020", right_on="NTACode", how="left")

# ---- Base Map ----
m = folium.Map(location=[40.7128, -74.0060], zoom_start=11, tiles="CartoDB positron")

# ---- Choropleth Layer ----
choropleth = folium.Choropleth(
    geo_data=merged,
    data=merged,
    columns=["nta2020", "HVI_RANK"],
    key_on="feature.properties.nta2020",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.3,
    legend_name="Heat Vulnerability Index (1-5)",
    highlight=True
).add_to(m)

# ---- Add Tooltips ----
folium.GeoJson(
    merged,
    style_function=lambda x: {"fillColor": "transparent", "color": "black", "weight": 0.3},
    tooltip=folium.GeoJsonTooltip(
        fields=["ntaname", "GEONAME", "HVI_RANK", "MEDIAN_INCOME", "PCT_HOUSEHOLDS_AC"],
        aliases=["NTA:", "Neighborhood:", "HVI Rank:", "Median Income:", "% Households w/ AC:"],
        localize=True,
        sticky=True
    )
).add_to(m)

# ---- Layer Control ----
folium.LayerControl().add_to(m)

# ---- Display in Streamlit ----
st_folium(m, width=1000, height=700)

