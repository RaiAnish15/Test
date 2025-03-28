import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="Smart Agri: Basmati Intelligence Portal", layout="wide")
st.title("Smart Agri: Basmati Intelligence Portal")

# Top-level section selection
section = st.radio("Select Section", options=["Meteorological Variable", "Market", "What If"], horizontal=True)

# -----------------------------
# Helper function to build dict from uploaded PNG files
# -----------------------------
def build_file_dict_from_files(uploaded_files):
    """
    Reads uploaded PNG files and parses their filenames into a nested dict:
      { state: { "District-Block": { var_label: file } } }
    
    Expects filenames with at least 4 underscore-separated parts:
       State_District_Block_Var[(_sinceYYYY)].png
    For example:
       Punjab_Gurdaspur_Batala_Rain_since2000.png  → "Rain since 2000"
       Punjab_Tarn Taran_Tarn Taran_Rain_since1990.png → "Rain since 1990"
    """
    file_dict = {}
    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        if not filename.endswith(".png"):
            st.warning(f"File '{filename}' is not a PNG. Skipping.")
            continue
        
        parts = filename.split(".")[0].split("_")
        if len(parts) < 4:
            st.warning(f"Filename '{filename}' does not have enough parts. Skipping.")
            continue
        
        state = parts[0]
        district = parts[1]
        block = parts[2]
        var_parts = parts[3:]
        
        # If the last part starts with "since", format accordingly.
        if len(var_parts) >= 2 and var_parts[-1].startswith("since"):
            var_name = "_".join(var_parts[:-1])
            year_str = var_parts[-1].replace("since", "").strip()
            var_label = f"{var_name} since {year_str}"
        else:
            var_label = "_".join(var_parts)
        
        district_block = f"{district}-{block}"
        file_dict.setdefault(state, {}).setdefault(district_block, {})[var_label] = uploaded_file
    return file_dict

# -----------------------------
# Meteorological Variable Section using direct PNG upload
# -----------------------------
if section == "Meteorological Variable":
    st.sidebar.header("Upload PNG files")
    uploaded_files = st.sidebar.file_uploader("Upload your Meteorological Variable PNG files", type="png", accept_multiple_files=True)
    
    if not uploaded_files:
        st.info("Please upload one or more PNG files.")
    else:
        file_dict = build_file_dict_from_files(uploaded_files)
        if not file_dict:
            st.error("No valid PNG files found based on the expected filename format.")
        else:
            # State dropdown
            state_options = sorted(list(file_dict.keys()))
            state_selected = st.sidebar.selectbox("Select State", ["select"] + state_options)
            
            if state_selected != "select":
                # District-Block dropdown
                district_block_options = sorted(list(file_dict[state_selected].keys()))
                district_block_selected = st.sidebar.selectbox("Select District-Block", ["select"] + district_block_options)
                
                if district_block_selected != "select":
                    # Variable dropdown, with an "All" option
                    vars_list = sorted(list(file_dict[state_selected][district_block_selected].keys()))
                    variable_options = ["select", "All"] + vars_list
                    variable_selected = st.sidebar.selectbox("Select Meteorological Variable", variable_options)
                    
                    if variable_selected != "select":
                        if variable_selected == "All":
                            # Display all images for that district-block
                            for var_label, file_obj in file_dict[state_selected][district_block_selected].items():
                                try:
                                    image = Image.open(file_obj)
                                    st.image(image, caption=file_obj.name, use_container_width=True)
                                except Exception as e:
                                    st.error(f"Error opening {file_obj.name}: {e}")
                        else:
                            file_obj = file_dict[state_selected][district_block_selected].get(variable_selected)
                            if file_obj:
                                try:
                                    image = Image.open(file_obj)
                                    st.image(image, caption=file_obj.name, use_container_width=True)
                                except Exception as e:
                                    st.error(f"Error opening {file_obj.name}: {e}")
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
