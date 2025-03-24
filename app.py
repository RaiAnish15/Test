import streamlit as st
from PIL import Image

st.title("Meteorological Plot Viewer")

st.write(
    """
    **Instructions:**
    1. Upload your PNG files. Each file should be named in the format:  
       `State_District_Block_var.png`  
       e.g., `Haryana_Sonepat_Gohana_Tmax.png`
    2. Use the dropdowns below to select the State, then the District-Block, and finally the meteorological variable.
    3. The corresponding plot image will be displayed.
    """
)

# File uploader: allow multiple PNG files
uploaded_files = st.file_uploader("Upload your plot images", type=["png"], accept_multiple_files=True)

# Dictionary to store files in the format: { state: { "District-Block": { var: file } } }
file_dict = {}

if uploaded_files:
    for file in uploaded_files:
        filename = file.name  # e.g., "Haryana_Sonepat_Gohana_Tmax.png"
        # Remove extension and split by underscore
        parts = filename.split('.')[0].split('_')
        if len(parts) != 4:
            st.warning(f"Filename '{filename}' does not match the required format.")
            continue
        state, district, block, var = parts
        # Create a combined key for district and block
        district_block = f"{district}-{block}"
        # Organize files in nested dictionary structure
        file_dict.setdefault(state, {}).setdefault(district_block, {})[var] = file

    # --- Dropdown for State ---
    state_options = sorted(list(file_dict.keys()))
    state_selected = st.selectbox("Select State", ["select"] + state_options)

    if state_selected != "select":
        # --- Dropdown for District-Block (for the selected state) ---
        district_block_options = sorted(list(file_dict[state_selected].keys()))
        district_block_selected = st.selectbox("Select District-Block", ["select"] + district_block_options)

        if district_block_selected != "select":
            # --- Dropdown for meteorological variable (for the selected state and district-block) ---
            variable_options = sorted(list(file_dict[state_selected][district_block_selected].keys()))
            variable_selected = st.selectbox("Select Meteorological Variable", ["select"] + variable_options)

            if variable_selected != "select":
                # Retrieve and display the corresponding image
                file_obj = file_dict[state_selected][district_block_selected].get(variable_selected)
                if file_obj:
                    image = Image.open(file_obj)
                    st.image(image, caption=file_obj.name)
                else:
                    st.error("No image found for the selected options.")
