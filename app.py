import streamlit as st
from PIL import Image
import os

# Set page configuration
st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Dashboard")

# Create a horizontal radio button at the top to act as tabs
section = st.radio("Select Section", options=["Meteorological Variable", "Market", "What If"], horizontal=True)

if section == "Meteorological Variable":
    # Meteorological Variable Section: Read PNG files and build a file dictionary.
    png_files = [f for f in os.listdir() if f.endswith('.png')]
    
    if not png_files:
        st.error("No PNG files found in the current directory.")
    else:
        # Build a nested dictionary: { state: { "District-Block": { var: filename } } }
        file_dict = {}
        for filename in png_files:
            # Expecting format: State_District_Block_var.png
            parts = filename.split('.')[0].split('_')
            if len(parts) != 4:
                st.warning(f"Filename '{filename}' does not match the required format.")
                continue
            state, district, block, var = parts
            district_block = f"{district}-{block}"
            file_dict.setdefault(state, {}).setdefault(district_block, {})[var] = filename

        # Sidebar dropdowns for Meteorological Variable options
        st.sidebar.header("Meteorological Variable Options")
        state_options = sorted(list(file_dict.keys()))
        state_selected = st.sidebar.selectbox("Select State", ["select"] + state_options)
        
        if state_selected != "select":
            district_block_options = sorted(list(file_dict[state_selected].keys()))
            district_block_selected = st.sidebar.selectbox("Select District-Block", ["select"] + district_block_options)
            if district_block_selected != "select":
                variable_options = sorted(list(file_dict[state_selected][district_block_selected].keys()))
                variable_selected = st.sidebar.selectbox("Select Meteorological Variable", ["select"] + variable_options)
                if variable_selected != "select":
                    selected_filename = file_dict[state_selected][district_block_selected].get(variable_selected)
                    if selected_filename:
                        image = Image.open(selected_filename)
                        st.image(image, use_container_width=True)
                    else:
                        st.error("No image found for the selected options.")

elif section == "Market":
    # Market Section: Example dropdowns for Market-specific options.
    st.sidebar.header("Market Options")
    market_option = st.sidebar.selectbox("Select Market Option", ["Option A", "Option B", "Option C"])
    
    st.write("## Market Section")
    st.write(f"You selected: **{market_option}**")
    st.write("Add your Market-related plots or data here.")

elif section == "What If":
    # What If Section: Example dropdowns for What If scenarios.
    st.sidebar.header("What If Options")
    what_if_option = st.sidebar.selectbox("Select What If Scenario", ["Scenario 1", "Scenario 2", "Scenario 3"])
    
    st.write("## What If Section")
    st.write(f"You selected: **{what_if_option}**")
    st.write("Add your What If scenario analysis or plots here.")
