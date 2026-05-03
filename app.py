import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import json
import base64
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Global Airport Transit Explorer",
    page_icon="✈️",
    layout="wide"
)

# Permanently dark theme settings for charts
bg_color = "rgba(15, 15, 15, 1)"
text_color = "white"
grid_color = "#333333"
plotly_template = "plotly_dark"
html_text_color = "#CCCCCC"

# --- LOAD DATA ---
@st.cache_data(ttl=1)
def load_data():
    with open('airport_transit_data.json', 'r') as f:
        data = json.load(f)
    return pd.DataFrame(data)

@st.cache_data
def get_image_base64(filepath):
    if os.path.exists(filepath):
        with open(filepath, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

df = load_data()

# --- HEADER ---
st.title("🚆 Southeast Asia Airport-to-City Transit Explorer")
st.markdown("""
Welcome to the interactive infographic exploring major airport express connections.
Compare how quickly and efficiently you can get from the terminal to the city center!
""")
st.divider()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Filter & Sort Options")

# Sorting
sort_by = st.sidebar.selectbox("Sort data by:", ["Country", "Distance (km)", "Time (mins)", "Speed (km/h) - Estimated"])

# Search/Filter by Country (Defaulting to SE Asia)
sea_countries = ["Malaysia", "Singapore", "Thailand", "Indonesia"]
available_countries = df["country"].unique().tolist()
# Ensure default countries exist in the dataset
default_countries = [c for c in sea_countries if c in available_countries]

search_country = st.sidebar.multiselect("Filter by Country:", options=available_countries, default=default_countries)

st.sidebar.divider()
st.sidebar.markdown(f"""
**📅 Data Status**  
*As of:* May 3, 2026  
*Prices:* Local currency rates  
*Sources:* KLIA Ekspres, SMRT, ARL BKK, KAI Bandaraya official sites.
""")

# --- DATA PROCESSING ---
# Add estimated average speed
df["estimated_speed_kmh"] = (df["distance_km"] / (df["time_mins"] / 60)).round(1)

# Apply filters
filtered_df = df[df["country"].isin(search_country)].copy()

# Apply sorting
if sort_by == "Distance (km)":
    filtered_df = filtered_df.sort_values(by="distance_km", ascending=True)
elif sort_by == "Time (mins)":
    filtered_df = filtered_df.sort_values(by="time_mins", ascending=True)
elif sort_by == "Speed (km/h) - Estimated":
    filtered_df = filtered_df.sort_values(by="estimated_speed_kmh", ascending=False)
else:
    filtered_df = filtered_df.sort_values(by="country", ascending=True)

# --- VISUALIZATION: RADIAL TARGET MAP ---
st.subheader("🎯 Radial Map: Distance to City Center")
st.markdown("This bullseye standardizes geography. The exact center represents the **City Center (0 km)**. The dots represent **Airports**, plotted by their distance from the center. (Dot size represents travel time).")

if not filtered_df.empty:
    # Assign evenly spaced angles to spread dots around the circle
    df_radial = filtered_df.copy()
    df_radial['angle'] = np.linspace(0, 360, len(df_radial), endpoint=False)

    fig_radial = px.scatter_polar(
        df_radial,
        r='distance_km',
        theta='angle',
        text='city',
        size='time_mins', 
        color='country',
        hover_name='airport',
        hover_data={'angle': False, 'distance_km': True, 'time_mins': True, 'train_operator': True},
        template=plotly_template,
        color_discrete_sequence=px.colors.qualitative.Set1 # Vivid colors
    )
    
    # Enhance radial map styling to look like the reference bullseye
    fig_radial.update_traces(
        textposition='top center',
        textfont=dict(color=text_color, size=12),
        marker=dict(
            line=dict(color=text_color, width=1.5),
            opacity=0.9
        )
    )
    
    fig_radial.update_layout(
        polar=dict(
            bgcolor='#222222', # Solid dark center
            radialaxis=dict(
                visible=True, 
                title=dict(text="Distance (km)", font=dict(color=text_color)),
                gridcolor='#555555', # prominent rings
                linecolor='#555555',
                tickfont=dict(color='cyan', size=12),
                tickvals=[10, 20, 30, 40, 60],
                ticktext=["10km", "20km", "30km", "40km+", "+60km"],
                tickangle=45
            ),
            angularaxis=dict(visible=False) # Hide degrees for a cleaner look
        ),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        margin=dict(t=40, b=40, l=40, r=40),
        height=600,
        legend=dict(font=dict(color=text_color))
    )
    
    # Add 'City Center' right in the middle
    fig_radial.add_annotation(
        x=0.5, y=0.5,
        text="City<br>Center",
        showarrow=False,
        font=dict(color="white", size=14, weight="bold"),
        bgcolor="rgba(0,0,0,0.6)",
        bordercolor="white",
        borderwidth=1,
        borderpad=4
    )

    st.plotly_chart(fig_radial, use_container_width=True)
else:
    st.info("Please select at least one country.")

st.divider()

# --- VISUALIZATION: DUMBBELL CHART ---
st.subheader("📏 Dumbbell Chart: Direct Distance Comparison")
st.markdown("Quickly compare how far out the airports are. The blue dot is the **City Center**, the red dot is the **Airport**.")

def get_city_drawing(city_name):
    # Map city to local icon image
    if city_name == "Kuala Lumpur":
        img = get_image_base64("city_icon_image/kl_city_icon.jpeg")
        mime = "jpeg"
    elif city_name == "Singapore":
        img = get_image_base64("city_icon_image/sg_city_icon.avif")
        mime = "avif"
    elif city_name == "Bangkok":
        img = get_image_base64("city_icon_image/bkk_city_icon.png")
        mime = "png"
    elif city_name == "Jakarta":
        img = get_image_base64("city_icon_image/jakarta_city_icon.png")
        mime = "png"
    else:
        return None
    
    if img:
        return f"data:image/{mime};base64,{img}"
    return None

if not filtered_df.empty:
    fig_dumbbell = go.Figure()

    # Sort specifically for dumbbell flow (ascending distance looks best bottom-to-top)
    df_dumb = filtered_df.sort_values('distance_km', ascending=True)

    for i, row in df_dumb.iterrows():
        city = row['city']
        airport_code = row['airport'].split("(")[1].replace(")","")
        label = f"   {city} ({airport_code})" # Pad with spaces so image doesn't overlap text
        
        # Add the line and dots
        fig_dumbbell.add_trace(go.Scatter(
            x=[0, row['distance_km']],
            y=[label, label],
            mode='lines+markers',
            marker=dict(size=[12, 12], color=['#0068c9', '#ff4b4b']), # Blue for City, Red for Airport
            line=dict(color='#CCCCCC', width=3),
            name=row['city'],
            showlegend=False,
            hovertemplate=f"<b>{row['city']}</b><br>Distance: {row['distance_km']} km<br>Time: {row['time_mins']} mins<extra></extra>"
        ))
        
        # Add the custom drawn city icon to the left of the y-axis
        img_b64 = get_city_drawing(city)
        if img_b64:
            # Scale up KL and Singapore specifically as requested
            icon_size = 1.1 if city in ["Kuala Lumpur", "Singapore"] else 0.9
            
            fig_dumbbell.add_layout_image(
                dict(
                    source=img_b64,
                    xref="paper", yref="y",
                    x=-0.22, y=label, # Pin image firmly to the left side
                    sizex=0.20 * icon_size, sizey=icon_size,
                    xanchor="right", yanchor="middle"
                )
            )

    fig_dumbbell.update_layout(
        xaxis_title="Distance (km)",
        yaxis_title="",
        height=max(400, len(filtered_df) * 80), # Increased height per row for images
        margin=dict(l=250, r=20, t=20, b=20), # Increased left margin to fit custom drawings
        template="plotly_white", # Force LIGHT MODE
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="black", size=13),
        yaxis=dict(showgrid=False, zeroline=False)
    )
    # Add custom legend proxy
    fig_dumbbell.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(color='#0068c9', size=10), name='City Center'))
    fig_dumbbell.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(color='#ff4b4b', size=10), name='Airport'))
    fig_dumbbell.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="black")))

    st.plotly_chart(fig_dumbbell, use_container_width=True)

st.divider()

# --- VISUALIZATION: TRANSFER FOCUS ---
st.subheader("🔀 Transfer Focus: Route Segments")
st.markdown("Understanding the pain points of transfers. Color-coded segments represent different transit lines. *(Prices as of May 2026)*")

def generate_logo_badge(line_name, color):
    # Map operator to local LOGO file
    logo_file = None
    if "KLIA" in line_name:
        logo_file = "train_operator_logo/kul_erl_logo.png"
    elif "East West Line" in line_name:
        logo_file = "train_operator_logo/sg_smrt.png"
    elif "Airport Rail Link" in line_name:
        logo_file = "train_operator_logo/bkk_airport_rail_link_logo.png"
    elif "BTS" in line_name:
        logo_file = "train_operator_logo/bts_logo.png"
    elif "KAI" in line_name:
        logo_file = "train_operator_logo/indo_kai_bandaraya_logo.png"
    
    if logo_file:
        b64_str = get_image_base64(logo_file)
        if b64_str:
            # Make the image visibly larger (height 35px) and remove the boxy border for clean logos
            return f"<div style='display: inline-block; padding: 2px; background: rgba(255,255,255,0.9); border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'><img src='data:image/png;base64,{b64_str}' height='35' style='display: block;'></div>"

    # Fallback to CSS styled badges if no image is available
    if "KLIA" in line_name: abbr, border_radius = "ERL", "4px"
    elif "East West Line" in line_name: abbr, border_radius = "SMRT", "12px"
    elif "Airport Rail Link" in line_name: abbr, border_radius = "ARL", "4px"
    elif "BTS" in line_name: abbr, border_radius = "BTS", "4px"
    elif "Tokyo Monorail" in line_name: abbr, border_radius = "TM", "12px"
    elif "JR" in line_name: abbr, border_radius = "JR", "0px"
    elif "Heathrow" in line_name: abbr, border_radius = "HEX", "4px"
    elif "Airport Express" in line_name and "PEK" not in line_name: abbr, border_radius = "MTR", "12px"
    elif "AREX" in line_name: abbr, border_radius = "AREX", "4px"
    elif "Sydney" in line_name or "T8" in line_name: abbr, border_radius = "T", "12px"
    elif "RER" in line_name: abbr, border_radius = "RATP", "12px"
    elif "AirTrain" in line_name: abbr, border_radius = "JFK", "4px"
    elif "LIRR" in line_name: abbr, border_radius = "LIRR", "4px"
    elif "KAI" in line_name: abbr, border_radius = "KAI", "4px"
    elif "Taoyuan" in line_name or "MRT" in line_name: abbr, border_radius = "TY", "12px"
    else: 
        abbr = "".join([w[0] for w in line_name.split()[:2]]).upper()
        border_radius = "4px"
    
    return f"<div style='background-color: {color}; color: white; border-radius: {border_radius}; padding: 4px 10px; font-family: Impact, sans-serif; font-size: 14px; display: inline-block; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3); text-shadow: 1px 1px 0px rgba(0,0,0,0.4); letter-spacing: 0.5px;'>{abbr}</div>"

if not filtered_df.empty:
    for i, row in filtered_df.iterrows():
        # Display the route header with pricing info if available
        price_str = f" • {row['currency']} {row['local_price']:g} (~${row['usd_price']:.2f} USD)" if 'usd_price' in row and pd.notna(row['usd_price']) else ""
        st.markdown(f"**{row['city']} ({row['airport']} ➡ {row['city_center']}){price_str}**")
        
        segments = row.get("segments", [])
        if segments:
            # Build custom HTML for the transit line with increased margin to accommodate larger logos
            html = f"<div style='display: flex; align-items: flex-start; margin-bottom: 5px; margin-top: 30px; font-family: sans-serif; width: 100%; color: {html_text_color};'>"
            
            for idx, seg in enumerate(segments):
                # Start Node
                html += f"<div style='display: flex; flex-direction: column; align-items: center; position: relative; z-index: 2;'><div style='width: 16px; height: 16px; border-radius: 50%; background-color: {seg['color']}; border: 3px solid {bg_color};'></div><div style='font-size: 11px; margin-top: 8px; white-space: nowrap;'>{seg['start']}</div></div>"
                
                # Determine if we should show the logo on this segment
                show_logo = False
                if idx == 0:
                    show_logo = True
                elif segments[idx-1]['line'] != seg['line']:
                    show_logo = True
                
                logo_html = generate_logo_badge(seg['line'], seg['color']) if show_logo else ""
                
                # Line with conditionally centered logo floating above it
                html += f"<div style='flex-grow: 1; height: 6px; background-color: {seg['color']}; margin-top: 5px; margin-left: -5px; margin-right: -5px; z-index: 1; position: relative;'><div style='position: absolute; top: -45px; left: 50%; transform: translateX(-50%);'>{logo_html}</div></div>"
                
                # End Node (only on the last segment)
                if idx == len(segments) - 1:
                    html += f"<div style='display: flex; flex-direction: column; align-items: center; position: relative; z-index: 2;'><div style='width: 16px; height: 16px; border-radius: 50%; background-color: {seg['color']}; border: 3px solid {bg_color};'></div><div style='font-size: 11px; margin-top: 8px; white-space: nowrap;'>{seg['end']}</div></div>"
            
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
            
            # Show legend for operators (Unique only)
            legend_html = "<div style='display: flex; gap: 15px; margin-bottom: 40px; margin-top: 15px; font-size: 12px; align-items: center;'>"
            seen_lines = set()
            for seg in segments:
                if seg['line'] not in seen_lines:
                    seen_lines.add(seg['line'])
                    legend_logo = generate_logo_badge(seg['line'], seg['color'])
                    legend_html += f"<div style='display: flex; align-items: center; gap: 5px;'>{legend_logo} <span style='color: {html_text_color};'>{seg['line']}</span></div>"
            legend_html += "</div>"
            st.markdown(legend_html, unsafe_allow_html=True)
        else:
            st.info("No transfer data available for this route.")

st.divider()

# --- VISUALIZATION: DETAILED GRID ---

st.subheader("📋 Detailed Transit Information")

# Format dataframe for display
display_cols = ["country", "city", "airport", "city_center", "train_operator", "distance_km", "time_mins", "estimated_speed_kmh"]

# Add pricing columns to the display grid if they exist
if "local_price" in filtered_df.columns:
    display_cols.extend(["currency", "local_price", "usd_price"])

display_df = filtered_df[display_cols].copy()

# Rename columns
new_col_names = ["Country", "City", "Airport", "City Center", "Train Operator", "Distance (km)", "Time (mins)", "Avg Speed (km/h)"]
if "local_price" in display_df.columns:
    new_col_names.extend(["Currency", "Local Price", "USD Price ($)"])
    
display_df.columns = new_col_names

st.dataframe(
    display_df, 
    use_container_width=True, 
    hide_index=True
)
