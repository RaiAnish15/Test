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
# Helper function: build dict from ZIP bytes
# -----------------------------
def build_file_dict_from_zip(zip_bytes):
    """
    Reads PNG files from the ZIP and parses their filenames into a nested dict:
      { state: { "District-Block": { var_label: internal_zip_filename } } }
    """
    file_dict = {}
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            for name in z.namelist():
                if not name.endswith(".png"):
                    continue
                filename = name.split("/")[-1]
                parts = filename.split(".")[0].split("_")
                if len(parts) < 4:
                    st.warning(f"Filename '{filename}' does not have enough parts. Skipping.")
                    continue
                state = parts[0]
                district = parts[1]
                block = parts[2]
                var_parts = parts[3:]
                if len(var_parts) >= 2 and var_parts[-1].startswith("since"):
                    var_name = "_".join(var_parts[:-1])
                    year_str = var_parts[-1].replace("since", "").strip()
                    var_label = f"{var_name} since {year_str}"
                else:
                    var_label = "_".join(var_parts)
                district_block = f"{district}-{block}"
                file_dict.setdefault(state, {}).setdefault(district_block, {})[var_label] = name
    except zipfile.BadZipFile:
        st.error("The uploaded file is not a valid ZIP archive. Please check your file and try again.")
        return None
    return file_dict

# -----------------------------
# Helper function: build dict from PNG files list
# -----------------------------
def build_file_dict_from_png_files(png_files):
    """
    Reads a list of uploaded PNG files and parses their filenames into a nested dict:
      { state: { "District-Block": { var_label: uploaded_file } } }
    """
    file_dict = {}
    for uploaded_file in png_files:
        filename = uploaded_file.name
        parts = filename.split(".")[0].split("_")
        if len(parts) < 4:
            st.warning(f"Filename '{filename}' does not have enough parts. Skipping.")
            continue
        state = parts[0]
        district = parts[1]
        block = parts[2]
        var_parts = parts[3:]
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
# Meteorological Variable Section
# -----------------------------
if section == "Meteorological Variable":
    st.sidebar.header("Meteorological Variable Options")
    
    # First, try to load a ZIP file.
    uploaded_zip = st.sidebar.file_uploader("Upload Meteorological Variables ZIP file", type="zip")
    
    zip_bytes = None
    file_dict = None
    if uploaded_zip is not None:
        zip_bytes = uploaded_zip.read()
    else:
        # If no ZIP is uploaded, try default ZIP file from current directory.
        default_zip = "Meteorological_Variables.zip"
        if os.path.exists(default_zip):
            with open(default_zip, "rb") as f:
                zip_bytes = f.read()
            st.sidebar.info(f"Using default ZIP file: {default_zip}")
    
    # If we have ZIP bytes, use that.
    if zip_bytes is not None:
        file_dict = build_file_dict_from_zip(zip_bytes)
        source = "zip"
    else:
        # If no ZIP file, allow user to upload PNG files directly.
        st.sidebar.info("No ZIP file provided. Please upload PNG files directly.")
        uploaded_png_files = st.sidebar.file_uploader("Upload PNG files", type="png", accept_multiple_files=True)
        if uploaded_png_files:
            file_dict = build_file_dict_from_png_files(uploaded_png_files)
            source = "png"
        else:
            st.info("Please upload either a ZIP file or PNG files.")
    
    # If we have a file dictionary, proceed with dropdowns.
    if file_dict:
        # State dropdown
        state_options = sorted(list(file_dict.keys()))
        state_selected = st.sidebar.selectbox("Select State", ["select"] + state_options)
        
        if state_selected != "select":
            district_block_options = sorted(list(file_dict[state_selected].keys()))
            district_block_selected = st.sidebar.selectbox("Select District-Block", ["select"] + district_block_options)
            
            if district_block_selected != "select":
                vars_list = sorted(list(file_dict[state_selected][district_block_selected].keys()))
                variable_options = ["select", "All"] + vars_list
                variable_selected = st.sidebar.selectbox("Select Meteorological Variable", variable_options)
                
                if variable_selected != "select":
                    if source == "zip":
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
                    elif source == "png":
                        if variable_selected == "All":
                            for var_label, uploaded_file in file_dict[state_selected][district_block_selected].items():
                                try:
                                    image = Image.open(uploaded_file)
                                    st.image(image, caption=uploaded_file.name, use_container_width=True)
                                except Exception as e:
                                    st.error(f"Error opening {uploaded_file.name}: {e}")
                        else:
                            uploaded_file = file_dict[state_selected][district_block_selected].get(variable_selected)
                            if uploaded_file:
                                try:
                                    image = Image.open(uploaded_file)
                                    st.image(image, caption=uploaded_file.name, use_container_width=True)
                                except Exception as e:
                                    st.error(f"Error opening {uploaded_file.name}: {e}")
                            else:
                                st.error("No image found for the selected options.")
    else:
        st.error("No valid files were provided.")

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
