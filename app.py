import streamlit as st
from PIL import Image
import os

# Set page configuration
st.set_page_config(page_title="SmartRice: Basmati Intelligence Portal", layout="wide")
st.title("Smart Agri: Basmati Intelligence Portal")

# Create a horizontal radio button at the top to act as tabs
section = st.radio("Select Section", options=["Meteorological Variable", "Market", "What If"], horizontal=True)

# -----------------------------
# Helper function to build dict
# -----------------------------
def build_file_dict(folder):
    """
    Reads all PNG files in 'folder' and parses their filenames into a nested dict:
       { state: { "District-Block": { var_label: filename } } }
    
    - Expects filenames in these possible formats:
        1) State_District_Block_Var.png
        2) State_District_Block_Var_sinceYYYY.png
    - For example: Haryana_Jind_Safidon_Rain_since1990.png
      => state=Haryana, district=Jind, block=Safidon, var='Rain', since='since1990'
      => var_label='Rain since 1990'
    """
    png_files = [f for f in os.listdir(folder) if f.endswith(".png")]
    if not png_files:
        return None  # No files found
    
    file_dict = {}
    for filename in png_files:
        filepath = os.path.join(folder, filename)
        # Remove extension, split by underscore
        parts = filename.split(".")[0].split("_")  # e.g. ["Haryana","Jind","Safidon","Rain","since1990"]
        
        if len(parts) < 4:
            # Not enough parts to parse properly
            st.warning(f"Filename '{filename}' does not match the required format (State_District_Block_Var...). Skipping.")
            continue
        
        state = parts[0]
        district = parts[1]
        block = parts[2]
        
        # The rest of the parts represent the variable portion, e.g. ["Rain"] or ["Rain","since1990"]
        var_parts = parts[3:]
        
        # We might have Var or Var_sinceYear
        # If there's a "sinceXXXX" part, combine it into a user-friendly label
        if len(var_parts) == 1:
            # Just a single var, e.g. "Rain"
            var_label = var_parts[0]
        elif len(var_parts) == 2:
            # e.g. ["Rain","since1990"]
            var = var_parts[0]
            since_part = var_parts[1]  # e.g. "since1990"
            if since_part.startswith("since"):
                # Turn "since1990" into "since 1990"
                year_str = since_part.replace("since", "").strip()  # "1990"
                var_label = f"{var} since {year_str}"  # "Rain since 1990"
            else:
                var_label = "_".join(var_parts)  # fallback
        else:
            # More complicated file name? We'll just join them with underscores
            var_label = "_".join(var_parts)
        
        district_block = f"{district}-{block}"
        file_dict.setdefault(state, {}).setdefault(district_block, {})[var_label] = filepath
    
    return file_dict

# -----------------------------
# Meteorological Variable
# -----------------------------
if section == "Meteorological Variable":
    folder = "Meteorological Variable"  # Path to your meteorological PNG files
    file_dict = build_file_dict(folder)
    
    if not file_dict:
        st.error(f"No PNG files found in the folder: '{folder}'.")
    else:
        st.sidebar.header("Meteorological Variable Options")
        
        # 1) State dropdown
        state_options = sorted(list(file_dict.keys()))
        state_selected = st.sidebar.selectbox("Select State", ["select"] + state_options)
        
        if state_selected != "select":
            # 2) District-Block dropdown
            district_block_options = sorted(list(file_dict[state_selected].keys()))
            district_block_selected = st.sidebar.selectbox("Select District-Block", ["select"] + district_block_options)
            
            if district_block_selected != "select":
                # 3) Meteorological Variable dropdown
                vars_list = sorted(list(file_dict[state_selected][district_block_selected].keys()))
                
                # Add "All" option if you want to show all at once
                variable_options = ["select", "All"] + vars_list
                variable_selected = st.sidebar.selectbox("Select Meteorological Variable", variable_options)
                
                if variable_selected != "select":
                    # Show all or one
                    if variable_selected == "All":
                        # Display all relevant images
                        for var_label, filepath in file_dict[state_selected][district_block_selected].items():
                            try:
                                image = Image.open(filepath)
                                st.image(image, caption=os.path.basename(filepath), use_container_width=True)
                            except Exception as e:
                                st.error(f"Error opening {filepath}: {e}")
                    else:
                        # Display only the selected image
                        selected_filepath = file_dict[state_selected][district_block_selected].get(variable_selected)
                        if selected_filepath:
                            try:
                                image = Image.open(selected_filepath)
                                st.image(image, caption=os.path.basename(selected_filepath), use_container_width=True)
                            except Exception as e:
                                st.error(f"Error opening {selected_filepath}: {e}")
                        else:
                            st.error("No image found for the selected options.")

# -----------------------------
# Market
# -----------------------------
elif section == "Market":
    folder = "Market"  # Path to your market PNG files
    png_files = [f for f in os.listdir(folder) if f.endswith('.png')] if os.path.exists(folder) else []
    
    st.sidebar.header("Market Options")
    market_option = st.sidebar.selectbox("Select Market Option", ["Option A", "Option B", "Option C"])
    
    st.write("## Market Section")
    st.write(f"You selected: **{market_option}**")
    
    if not png_files:
        st.info(f"No PNG files found in '{folder}' folder.")
    else:
        st.write(f"Found {len(png_files)} PNG file(s) in '{folder}':")
        for file in png_files:
            filepath = os.path.join(folder, file)
            try:
                image = Image.open(filepath)
                st.image(image, caption=file, use_container_width=True)
            except Exception as e:
                st.error(f"Error opening {filepath}: {e}")

# -----------------------------
# What If
# -----------------------------
elif section == "What If":
    folder = "What If"  # Path to your what-if PNG files
    png_files = [f for f in os.listdir(folder) if f.endswith('.png')] if os.path.exists(folder) else []
    
    st.sidebar.header("What If Options")
    what_if_option = st.sidebar.selectbox("Select What If Scenario", ["Scenario 1", "Scenario 2", "Scenario 3"])
    
    st.write("## What If Section")
    st.write(f"You selected: **{what_if_option}**")
    
    if not png_files:
        st.info(f"No PNG files found in '{folder}' folder.")
    else:
        st.write(f"Found {len(png_files)} PNG file(s) in '{folder}':")
        for file in png_files:
            filepath = os.path.join(folder, file)
            try:
                image = Image.open(filepath)
                st.image(image, caption=file, use_container_width=True)
            except Exception as e:
                st.error(f"Error opening {filepath}: {e}")
