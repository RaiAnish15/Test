import streamlit as st
from PIL import Image
import os

# Set page configuration and title
st.set_page_config(page_title="Smart Agri: Basmati Intelligence Portal", layout="wide")
st.title("Smart Agri: Basmati Intelligence Portal")

# Top-level section selection (including "Quality")
section = st.radio("Select Section", options=["Meteorological Variable", "Market", "What If", "Quality"], horizontal=True)

# -----------------------------
# Helper: Load and resize image to fixed dimensions
# -----------------------------
def load_and_resize_image(file_path, size=(700, 300)):
    try:
        image = Image.open(file_path)
        image = image.resize(size)
        return image
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return None

# -----------------------------
# Helper: Build file dictionary from PNG files (for Meteorological Variable)
# -----------------------------
def build_file_dict_from_folder(folder):
    """
    Reads PNG files from the specified folder and parses their filenames into a nested dict:
      { state: { "District-Block": { var_label: file_path } } }
    
    Expected filename formats:
      State_District_Block_Var.png  
      State_District_Block_Var_sinceYYYY.png
    
    Example:
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
        file_path = os.path.join(folder, filename)
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
        
        if var_label.startswith("Temp"):
            var_label = var_label.replace("Temp", "Temperature", 1)
        
        district_block = f"{district}-{block}"
        file_dict.setdefault(state, {}).setdefault(district_block, {})[var_label] = file_path

    return file_dict

# -----------------------------
# Helper: Build quality dictionaries from image files (for Quality section)
# -----------------------------
def build_quality_dicts(folder):
    """
    Reads image files (JPG or PNG) from the specified folder and separates them into two dictionaries:
    
    base_dict: for images without a percentile (expected filename: State_District_Block_QualityParameter.png)
    perc_dict: for images with a percentile (expected filename: State_District_Block_QualityParameter_Percentile.png)
    
    Returns:
      (base_dict, perc_dict)
    
    Both dictionaries are structured as:
      base_dict[state][district_block][quality_param] = file_path
      perc_dict[state][district_block][quality_param][percentile] = file_path
    """
    base_dict = {}
    perc_dict = {}
    
    if not os.path.exists(folder):
        st.error(f"Folder '{folder}' not found.")
        return None, None
    
    quality_files = [f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".png"))]
    if not quality_files:
        st.error(f"No image files found in the folder '{folder}'.")
        return None, None
    
    for filename in quality_files:
        file_path = os.path.join(folder, filename)
        parts = filename.split(".")[0].split("_")
        if len(parts) < 4:
            st.warning(f"Filename '{filename}' does not have enough parts. Skipping.")
            continue
        
        state = parts[0]
        district = parts[1]
        block = parts[2]
        district_block = f"{district}-{block}"
        
        # Base image: exactly 4 parts (no percentile)
        if len(parts) == 4:
            quality_param = parts[3]
            base_dict.setdefault(state, {}).setdefault(district_block, {})[quality_param] = file_path
        # Percentile image: 5 or more parts
        elif len(parts) >= 5:
            quality_param = parts[3]
            percentile = parts[4]
            perc_dict.setdefault(state, {}).setdefault(district_block, {}).setdefault(quality_param, {})[percentile] = file_path
        else:
            st.warning(f"Filename '{filename}' is not in an expected format. Skipping.")
    
    return base_dict, perc_dict

# -----------------------------
# Meteorological Variable Section using local folder files
# -----------------------------
if section == "Meteorological Variable":
    st.sidebar.header("Meteorological Variable Options")
    folder = "Meteorological Variables Monthly"  # Folder containing PNG files for meteorological variables
    file_dict = build_file_dict_from_folder(folder)
    
    if file_dict:
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
                    if variable_selected == "All":
                        for var_label, file_path in file_dict[state_selected][district_block_selected].items():
                            img = load_and_resize_image(file_path)
                            if img:
                                st.image(img, use_container_width=True)
                    else:
                        file_path = file_dict[state_selected][district_block_selected].get(variable_selected)
                        if file_path:
                            img = load_and_resize_image(file_path)
                            if img:
                                st.image(img, use_container_width=True)
                        else:
                            st.error("No image found for the selected options.")

# -----------------------------
# Quality Section using local image files
# -----------------------------
elif section == "Quality":
    st.sidebar.header("Quality Options")
    quality_folder = "Quality"  # Folder containing quality images
    base_dict, perc_dict = build_quality_dicts(quality_folder)
    
    if base_dict is None:
        st.info("No quality images available.")
    else:
        state_options = sorted(base_dict.keys())
        state_selected = st.sidebar.selectbox("Select State", ["select"] + state_options)
        
        if state_selected != "select":
            district_block_options = sorted(base_dict[state_selected].keys())
            district_block_selected = st.sidebar.selectbox("Select District-Block", ["select"] + district_block_options)
            
            if district_block_selected != "select":
                # First dropdown: Quality Parameter (base image without percentile)
                quality_params = sorted(base_dict[state_selected][district_block_selected].keys())
                quality_param_selected = st.sidebar.selectbox("Select Quality Parameter", ["select", "All"] + quality_params)
                
                # Default: show base image unless a percentile is selected
                show_base = True
                if quality_param_selected != "select" and quality_param_selected != "All":
                    # Check if percentile images exist for the selected quality parameter
                    if perc_dict and state_selected in perc_dict and district_block_selected in perc_dict[state_selected] and quality_param_selected in perc_dict[state_selected][district_block_selected]:
                        pct_dict = perc_dict[state_selected][district_block_selected][quality_param_selected]
                        percentile_options = sorted(pct_dict.keys())
                        # Format options as "At 90th percentile"
                        formatted_options = ["select", "All"] + [f"At {opt} percentile" for opt in percentile_options]
                        percentile_selected = st.sidebar.selectbox("Select True vs Predicted", formatted_options)
                        
                        if percentile_selected != "select":
                            # If a specific percentile is chosen, hide base image
                            show_base = False
                            if percentile_selected == "All":
                                for opt, file_path in pct_dict.items():
                                    img = load_and_resize_image(file_path)
                                    if img:
                                        st.image(img, use_container_width=True)
                            else:
                                raw_pct = percentile_selected.replace("At ", "").replace(" percentile", "").strip()
                                file_path = pct_dict.get(raw_pct)
                                if file_path:
                                    img = load_and_resize_image(file_path)
                                    if img:
                                        st.image(img, use_container_width=True)
                                else:
                                    st.error("No image found for the selected percentile.")
                    else:
                        st.info("No percentile images available for the selected quality parameter.")
                
                # If no percentile selection is made, display the base image(s)
                if show_base:
                    if quality_param_selected == "All":
                        for param, file_path in base_dict[state_selected][district_block_selected].items():
                            img = load_and_resize_image(file_path)
                            if img:
                                st.image(img, use_container_width=True)
                    elif quality_param_selected != "select":
                        base_image_path = base_dict[state_selected][district_block_selected].get(quality_param_selected)
                        if base_image_path:
                            img = load_and_resize_image(base_image_path)
                            if img:
                                st.image(img, use_container_width=True)
                        else:
                            st.info("No base image available for the selected quality parameter.")

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
