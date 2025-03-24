import streamlit as st
from PIL import Image
import os

# Set wide layout and custom page title
st.set_page_config(page_title="Meteorological Dashboard", layout="wide")

# Optional: Custom CSS styling for the app (adjust colors and styles as desired)
st.markdown(
    """
    <style>
    /* Customize the sidebar background */
    .css-1d391kg {  /* This selector might change in future Streamlit versions */
        background-color: #f0f2f6;
    }
    /* Customize the main title */
    .main-title {
        font-size: 2.5rem;
        color: #333;
        font-weight: bold;
        text-align: center;
        padding-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True
)

# Main title in the main container
st.markdown('<div class="main-title">Meteorological Plot Dashboard</div>', unsafe_allow_html=True)
st.write("### Explore your meteorological plots by selecting options from the sidebar.")

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
            st.sidebar.warning(f"Filename '{filename}' does not match the required format.")
            continue
        state, district, block, var = parts
        district_block = f"{district}-{block}"
        file_dict.setdefault(state, {}).setdefault(district_block, {})[var] = filename

    # Sidebar dropdowns for selection
    st.sidebar.header("Select Options")
    
    # Dropdown for State
    state_options = sorted(list(file_dict.keys()))
    state_selected = st.sidebar.selectbox("Select State", ["select"] + state_options)

    selected_filename = None  # initialize
    
    if state_selected != "select":
        # Dropdown for District-Block for the selected State
        district_block_options = sorted(list(file_dict[state_selected].keys()))
        district_block_selected = st.sidebar.selectbox("Select District-Block", ["select"] + district_block_options)

        if district_block_selected != "select":
            # Dropdown for meteorological variable for the selected State and District-Block
            variable_options = sorted(list(file_dict[state_selected][district_block_selected].keys()))
            variable_selected = st.sidebar.selectbox("Select Meteorological Variable", ["select"] + variable_options)

            if variable_selected != "select":
                # Retrieve the corresponding image filename
                selected_filename = file_dict[state_selected][district_block_selected].get(variable_selected)

    # Display the selected image in the main area using columns for a neat layout
    col1, col2 = st.columns([1, 3])
    with col1:
        st.write("### Selections")
        st.write(f"**State:** {state_selected}" if state_selected != "select" else "State not selected")
        st.write(f"**District-Block:** {district_block_selected}" if state_selected != "select" and district_block_selected != "select" else "District-Block not selected")
        st.write(f"**Variable:** {variable_selected}" if variable_selected != "select" else "Variable not selected")
    with col2:
        if selected_filename:
            try:
                image = Image.open(selected_filename)
                st.image(image, caption=selected_filename, use_column_width=True)
            except Exception as e:
                st.error(f"Error opening image: {e}")
        else:
            st.info("Please make selections from the sidebar to display the plot.")
