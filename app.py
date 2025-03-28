import streamlit as st
from PIL import Image
import zipfile
import io

st.set_page_config(page_title="Smart Agri: Basmati Intelligence Portal", layout="wide")
st.title("Smart Agri: Basmati Intelligence Portal")

# Top-level section selection (only Meteorological Variable is implemented here)
section = st.radio("Select Section", options=["Meteorological Variable", "Market", "What If"], horizontal=True)

# -----------------------------
# Helper function to build dict from ZIP file contents
# -----------------------------
def build_file_dict_from_zip(zip_bytes):
    """
    Reads PNG files from the ZIP (with filenames in the format):
      State_District_Block_Var.png
      or
      State_District_Block_Var_sinceYYYY.png

    Returns a nested dict:
      { state: { "District-Block": { var_label: internal_zip_filename } } }
    """
    file_dict = {}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for name in z.namelist():
            if not name.endswith(".png"):
                continue
            # Use only the file name (ignore folder structure in ZIP, if any)
            filename = name.split("/")[-1]
            parts = filename.split(".")[0].split("_")
            if len(parts) < 4:
                st.warning(f"Filename '{filename}' does not match the required format. Skipping.")
                continue
            state = parts[0]
            district = parts[1]
            block = parts[2]
            var_parts = parts[3:]
            if len(var_parts) == 1:
                var_label = var_parts[0]
            elif len(var_parts) == 2:
                var = var_parts[0]
                since_part = var_parts[1]
                if since_part.startswith("since"):
                    year_str = since_part.replace("since", "").strip()
                    var_label = f"{var} since {year_str}"
                else:
                    var_label = "_".join(var_parts)
            else:
                var_label = "_".join(var_parts)
            district_block = f"{district}-{block}"
            file_dict.setdefault(state, {}).setdefault(district_block, {})[var_label] = name
    return file_dict

# -----------------------------
# Meteorological Variable Section using ZIP upload
# -----------------------------
if section == "Meteorological Variable":
    st.sidebar.header("Upload Meteorological Variables ZIP file")
    uploaded_zip = st.sidebar.file_uploader("Upload ZIP", type="zip")
    
    if uploaded_zip is not None:
        zip_bytes = uploaded_zip.read()
        file_dict = build_file_dict_from_zip(zip_bytes)
        
        if not file_dict:
            st.error("No valid PNG files found in the ZIP file.")
        else:
            st.sidebar.header("Meteorological Variable Options")
            
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
    else:
        st.info("Please upload the Meteorological Variables ZIP file.")

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
