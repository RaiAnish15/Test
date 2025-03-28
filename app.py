import streamlit as st
from PIL import Image
import zipfile
import io
import os

st.set_page_config(page_title="Smart Agri: Basmati Intelligence Portal", layout="wide")
st.title("Smart Agri: Basmati Intelligence Portal")

# Top-level section selection
section = st.radio("Select Section", options=["Meteorological Variable", "Market", "What If"], horizontal=True)

# -----------------------------
# Helper function to build dict from ZIP file contents
# -----------------------------
def build_file_dict_from_zip(zip_bytes):
    """
    Reads PNG files from the ZIP and parses their filenames into a nested dict:
      { state: { "District-Block": { var_label: internal_zip_filename } } }
    
    Accepts filenames with at least 4 underscore-separated parts:
       State_District_Block_Var[(_sinceYYYY)].png
    For example:
       Punjab_Gurdaspur_Batala_Rain_since2000.png  → "Rain since 2000"
       Punjab_Tarn Taran_Tarn Taran_Rain_since1990.png → "Rain since 1990"
    """
    file_dict = {}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for name in z.namelist():
            if not name.endswith(".png"):
                continue
            # Get only the filename (ignore any folder structure in the ZIP)
            filename = name.split("/")[-1]
            parts = filename.split(".")[0].split("_")
            if len(parts) < 4:
                st.warning(f"Filename '{filename}' does not have enough parts. Skipping.")
                continue

            state = parts[0]
            district = parts[1]
            block = parts[2]
            var_parts = parts[3:]
            # If any part starts with "since", assume the last part is the cutoff info.
            if len(var_parts) >= 2 and var_parts[-1].startswith("since"):
                var_name = "_".join(var_parts[:-1])
                year_str = var_parts[-1].replace("since", "").strip()
                var_label = f"{var_name} since {year_str}"
            else:
                var_label = "_".join(var_parts)
            
            district_block = f"{district}-{block}"
            file_dict.setdefault(state, {}).setdefault(district_block, {})[var_label] = name
    return file_dict

# -----------------------------
# Meteorological Variable Section using ZIP upload or default file
# -----------------------------
if section == "Meteorological Variable":
    st.sidebar.header("Meteorological Variable Options")
    
    uploaded_zip = st.sidebar.file_uploader("Upload Meteorological Variables ZIP file", type="zip")
    
    # If no file is uploaded, try to load default ZIP file from the current directory.
    if uploaded_zip is None:
        default_zip = "Meteorological_Variables.zip"
        if os.path.exists(default_zip):
            with open(default_zip, "rb") as f:
                zip_bytes = f.read()
            st.sidebar.info(f"Using default ZIP file: {default_zip}")
        else:
            st.info("Please upload the Meteorological Variables ZIP file.")
            zip_bytes = None
    else:
        zip_bytes = uploaded_zip.read()
    
    if zip_bytes is not None:
        file_dict = build_file_dict_from_zip(zip_bytes)
        
        if not file_dict:
            st.error("No valid PNG files found in the ZIP file.")
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
                        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
                            if variable_selected == "All":
                                for var_label, internal_name in file_dict[state_selected][district_block_selected].items():
                                    try:
                                        with z.open(internal_name) as file:
                                            image = Image.open(file)
                                            st.image(image, caption=internal_name, use_container_width=True)
                                    except Exception as e:
                                        st.error(f"Error opening {internal_name}: {e}")
                            else:
                                internal_name = file_dict[state_selected][district_block_selected].get(variable_selected)
                                if internal_name:
                                    try:
                                        with z.open(internal_name) as file:
                                            image = Image.open(file)
                                            st.image(image, caption=internal_name, use_container_width=True)
                                    except Exception as e:
                                        st.error(f"Error opening {internal_name}: {e}")
                                else:
                                    st.error("No image found for the selected options.")

# -----------------------------
# Market and What If Sections (Placeholder)
# -----------------------------
elif section == "Market":
    st.sidebar.header("Market Options")
    market_option = st.sidebar.selectbox("Select Market Option", ["Option A", "Option B", "Option C"])
    st.write("## Market Section")
    st.write(f"You selected: **{market_option}**")
    st.write("Add your Market-related plots or data here.")

elif section == "What If":
    st.sidebar.header("What If Options")
    what_if_option = st.sidebar.selectbox("Select What If Scenario", ["Scenario 1", "Scenario 2", "Scenario 3"])
    st.write("## What If Section")
    st.write(f"You selected: **{what_if_option}**")
    st.write("Add your What If scenario analysis or plots here.")
