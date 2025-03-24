import streamlit as st
from PIL import Image
import os

# Configure page with wide layout and custom title.
st.set_page_config(page_title="Meteorological Dashboard", layout="wide")

# Custom CSS for a refreshed look.
st.markdown(
    """
    <style>
    .header {font-size: 2.5rem; text-align: center; padding: 20px; color: #2c3e50;}
    .stTabs [role="tab"] {font-size: 1.1rem; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# Main header
st.markdown('<div class="header">Meteorological Plot Dashboard</div>', unsafe_allow_html=True)

# Read all PNG files from the current directory.
png_files = [f for f in os.listdir() if f.endswith('.png')]

if not png_files:
    st.error("No PNG files found in the current directory.")
    st.stop()

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

# Sidebar: Cascading dropdowns for filtering.
st.sidebar.header("Filter Options")

state_options = sorted(list(file_dict.keys()))
state_selected = st.sidebar.selectbox("Select State", ["Select"] + state_options)

selected_filename = None  # will store the final filename

if state_selected != "Select":
    district_block_options = sorted(list(file_dict[state_selected].keys()))
    district_block_selected = st.sidebar.selectbox("Select District-Block", ["Select"] + district_block_options)
    
    if district_block_selected != "Select":
        variable_options = sorted(list(file_dict[state_selected][district_block_selected].keys()))
        variable_selected = st.sidebar.selectbox("Select Meteorological Variable", ["Select"] + variable_options)
        
        if variable_selected != "Select":
            selected_filename = file_dict[state_selected][district_block_selected].get(variable_selected)
else:
    # If state is not selected, set defaults for later use.
    district_block_selected = "Select"
    variable_selected = "Select"

# Create two tabs: one for showing selections and one for the plot.
tab1, tab2 = st.tabs(["Selection", "Plot"])

with tab1:
    st.markdown("### Your Selections")
    st.write(f"**State:** {state_selected if state_selected != 'Select' else 'Not selected'}")
    st.write(f"**District-Block:** {district_block_selected if district_block_selected != 'Select' else 'Not selected'}")
    st.write(f"**Meteorological Variable:** {variable_selected if variable_selected != 'Select' else 'Not selected'}")

with tab2:
    if selected_filename:
        try:
            image = Image.open(selected_filename)
            st.image(image, caption=selected_filename, use_column_width=True)
        except Exception as e:
            st.error(f"Error loading image: {e}")
    else:
        st.info("Please select all options from the sidebar to view the plot.")
