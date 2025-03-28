import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="Smart Agri: Basmati Intelligence Portal", layout="wide")
st.title("Smart Agri: Basmati Intelligence Portal")

# Top-level section selection
section = st.radio("Select Section", options=["Meteorological Variable", "Market", "What If"], horizontal=True)

# -----------------------------
# Helper function to build dict from PNG files in a specific folder
# -----------------------------
def build_file_dict_from_folder(folder):
    """
    Reads PNG files from the specified folder and parses their filenames into a nested dict:
      { state: { "District-Block": { var_label: file_path } } }
    
    Expected filename formats:
      State_District_Block_Var.png  
      State_District_Block_Var_sinceYYYY.png

    For example:
      Haryana_Sirsa_Sirsa_Temp_since2010.png → variable label: "Temperature since 2010"
    """
    file_dict = {}
    if not os.path.exists(folder):
        st.error(f"Folder '{folder}' not found.")
        return None
    
    png_files = [f for f in os.listdir(folder) if f.endswith(".png")]
    if not png_files:
        st.error(f"No PNG files found in the folder '{folder}'.")
        return None
    
    for filename in png_files:
        # Full path for image file
        file_path = os.path.join(folder, filename)
        parts = filename.split(".")[0].split("_")
        if len(parts) < 4:
            st.warning(f"Filename '{filename}' does not have enough parts. Skipping.")
            continue

        state = parts[0]
        district = parts[1]
        block = parts[2]
        var_parts = parts[3:]
        # Format variable label; if the last part starts with "since", format it.
        if len(var_parts) >= 2 and var_parts[-1].startswith("since"):
            var_name = "_".join(var_parts[:-1])
            year_str = var_parts[-1].replace("since", "").strip()
            var_label = f"{var_name} since {year_str}"
        else:
            var_label = "_".join(var_parts)
        
        # Replace "Temp" with "Temperature" if it appears at the start
        if var_label.startswith("Temp"):
            var_label = var_label.replace("Temp", "Temperature", 1)
        
        district_block = f"{district}-{block}"
        file_dict.setdefault(state, {}).setdefault(district_block, {})[var_label] = file_path

    return file_dict

# -----------------------------
# Meteorological Variable Section using local folder files
# -----------------------------
if section == "Meteorological Variable":
    # Set folder name (make sure it matches exactly)
    folder = "Meteorological Variables"
    st.sidebar.header("Meteorological Variable Options")
    file_dict = build_file_dict_from_folder(folder)
    
    if file_dict:
        # State dropdown
        state_options = sorted(list(file_dict.keys()))
        state_selected = st.sidebar.selectbox("Select State", ["select"] + state_options)
        
        if state_selected != "select":
            # District-Block dropdown
            district_block_options = sorted(list(file_dict[state_selected].keys()))
            district_block_selected = st.sidebar.selectbox("Select District-Block", ["select"] + district_block_options)
            
            if district_block_selected != "select":
                # Variable dropdown with an "All" option
                vars_list = sorted(list(file_dict[state_selected][district_block_selected].keys()))
                variable_options = ["select", "All"] + vars_list
                variable_selected = st.sidebar.selectbox("Select Meteorological Variable", variable_options)
                
                if variable_selected != "select":
                    if variable_selected == "All":
                        for var_label, file_path in file_dict[state_selected][district_block_selected].items():
                            try:
                                image = Image.open(file_path)
                                st.image(image, use_container_width=True)
                            except Exception as e:
                                st.error(f"Error opening {file_path}: {e}")
                    else:
                        file_path = file_dict[state_selected][district_block_selected].get(variable_selected)
                        if file_path:
                            try:
                                image = Image.open(file_path)
                                st.image(image, use_container_width=True)
                            except Exception as e:
                                st.error(f"Error opening {file_path}: {e}")
                        else:
                            st.error("No image found for the selected options.")

# -----------------------------
# Market Section (Placeholder)
# -----------------------------
elif section == "Market":
    st.sidebar.header("Market Options")
    market_option = st.sidebar.selectbox("Select Market Option", ["Option A", "Option B", "Option C"])
    st.write("## Market Section")
    st.write(f"You selected: **{market_option}**")
    st.write("Add your Market-related plots or data here.")

# -----------------------------
# What If Section (Placeholder)
# -----------------------------
elif section == "What If":
    st.sidebar.header("What If Options")
    what_if_option = st.sidebar.selectbox("Select What If Scenario", ["Scenario 1", "Scenario 2", "Scenario 3"])
    st.write("## What If Section")
    st.write(f"You selected: **{what_if_option}**")
    st.write("Add your What If scenario analysis or plots here.")
