import streamlit as st
from PIL import Image
import os

st.title("Dashboard")

# Read all PNG files from the current directory
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

    # Sidebar dropdowns for selection
    st.sidebar.header("Select Options")
    
    # Dropdown for State
    state_options = sorted(list(file_dict.keys()))
    state_selected = st.sidebar.selectbox("Select State", ["select"] + state_options)

    if state_selected != "select":
        # Dropdown for District-Block for the selected State
        district_block_options = sorted(list(file_dict[state_selected].keys()))
        district_block_selected = st.sidebar.selectbox("Select District-Block", ["select"] + district_block_options)

        if district_block_selected != "select":
            # Dropdown for meteorological variable for the selected State and District-Block
            variable_options = sorted(list(file_dict[state_selected][district_block_selected].keys()))
            variable_selected = st.sidebar.selectbox("Select Meteorological Variable", ["select"] + variable_options)

            if variable_selected != "select":
                # Retrieve and display the corresponding image
                selected_filename = file_dict[state_selected][district_block_selected].get(variable_selected)
                if selected_filename:
                    image = Image.open(selected_filename)
                    st.image(image, caption=selected_filename)
                else:
                    st.error("No image found for the selected options.")
