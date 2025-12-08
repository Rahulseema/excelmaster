import streamlit as st
import pandas as pd
from io import BytesIO

# ==============================================================================
# 1. CONFIGURATION SECTION
# ==============================================================================

# --- NAVIGATION CONSTANTS ---
# The six main services that will appear in the dark sidebar.
MAIN_SERVICES = [
    "Picklist",
    "Listing Maker",
    "Reconciliations",
    "Optimization",
    "GST Reporting",
    "Configuration"
]

# The six channels that will appear as tabs within each main service.
CHANNELS = [
    "Amazon",
    "Flipkart",
    "Myntra",
    "Meesho",
    "Ajio",
    "Jio Mart"
]

# --- THEME COLORS ---
DARK_SLATE_BLUE = "#263d57"
VIBRANT_BLUE_ACCENT = "#4e73df"
LIGHT_GRAY_BG = "#f5f8fb"
DARK_TEXT = "#212529"
LIGHT_TEXT = "#ffffff"


# ==============================================================================
# 2. UI/UX STYLING (KI-ADMIN INSPIRED DARK THEME)
# ==============================================================================

def inject_admin_panel_css():
    """
    Injects custom CSS to achieve a KI-Admin inspired look: 
    Dark sidebar, vibrant blue accent, and clean main content.
    """
    st.markdown(
        f"""
        <style>
        /* Base Streamlit Overrides */
        #MainMenu, footer, header {{visibility: hidden;}}

        /* --- Global Colors & Text --- */
        :root, body, .stApp {{
            color: {DARK_TEXT} !important; 
            background-color: {LIGHT_GRAY_BG}; 
        }}
        
        /* Sidebar Styling: Dark Background */
        [data-testid="stSidebar"] {{
            background-color: {DARK_SLATE_BLUE}; 
            border-right: none;
            box-shadow: 2px 0 10px rgba(0, 0, 0, 0.2);
            position: fixed; 
            height: 100vh; 
            padding-top: 0; 
        }}
        
        /* Sidebar Header/Title (The "Operations Hub" text) */
        [data-testid="stSidebar"] h1 {{
            color: {VIBRANT_BLUE_ACCENT}; /* Use accent color for the main title/logo */
            font-size: 1.5rem;
            padding: 1.5rem 1.5rem 0.5rem 1.5rem;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid #3c526d; /* Lighter line for separation */
        }}
        
        /* --- SIDEBAR MENU (Radio Buttons for Services) --- */
        [data-testid="stSidebar"] div[data-testid="stRadio"] label {{
            font-size: 1.1rem;
            font-weight: 600;
            padding: 0.8rem 1.5rem;
            margin-left: 0; 
            width: 100%;
            color: {LIGHT_TEXT} !important; /* White text on dark background */
            transition: background-color 0.2s;
            border-left: 4px solid transparent; /* Space for accent border */
        }}
        [data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
            background-color: #3b506a; /* Slight hover effect */
        }}
        /* Active Link Styling */
        [data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {{
            background-color: {VIBRANT_BLUE_ACCENT} !important; /* Accent blue background */
            color: {LIGHT_TEXT} !important; 
            font-weight: 700 !important;
            border-left: 4px solid {LIGHT_TEXT}; /* White line accent */
        }}

        /* Hide the radio circle/dot and empty label space */
        div[data-testid="stRadio"] label[data-baseweb="radio"] div:first-child {{
            display: none !important;
        }}
        div[data-testid="stSidebar"] div[data-testid="stForm"] > label {{
            height: 0;
            padding: 0;
            margin: 0;
            overflow: hidden;
            display: block;
        }}

        /* --- MAIN CONTENT TABS STYLING (Channels) --- */
        div[data-testid="stTabs"] {{
            margin-bottom: 1.5rem;
            background-color: white; 
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            padding-left: 1rem;
        }}
        button[data-baseweb="tab"] {{
            color: {DARK_TEXT} !important; 
            font-weight: 600;
            border-radius: 6px 6px 0 0 !important;
            padding: 10px 20px !important;
            background-color: transparent !important; 
            border-bottom: 3px solid transparent !important;
            transition: all 0.2s;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {VIBRANT_BLUE_ACCENT} !important; /* Accent blue for active tab text */
            background-color: #ffffff !important; 
            border-bottom: 3px solid {VIBRANT_BLUE_ACCENT} !important; 
        }}


        /* --- Main Content Headers & Blocks --- */
        .block-container {{
            padding-top: 2rem;
            padding-left: 2rem; 
            padding-right: 2rem; 
            padding-bottom: 5rem;
        }}

        h1 {{
            color: {VIBRANT_BLUE_ACCENT}; /* Accent blue for main title */
            font-weight: 700;
            margin-bottom: 1.5rem;
        }}
        h2, h3, h4 {{
            color: {DARK_SLATE_BLUE}; /* Dark slate blue for sub-headers */
            font-weight: 600;
        }}

        /* Card/Block Styles - Clean White Boxes with Shadow */
        div[data-testid="stVerticalBlock"], 
        div[data-testid="stHorizontalBlock"] {{
            padding: 1.5rem;
            border-radius: 6px; 
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); 
            border: 1px solid #e3eaf3; 
            background: white;
            margin-bottom: 1.5rem;
        }}

        /* Primary Button Style - Accent Blue */
        .stButton>button {{
            background-color: {VIBRANT_BLUE_ACCENT};
            color: {LIGHT_TEXT} !important; 
            border-radius: 6px; 
            border: 1px solid {VIBRANT_BLUE_ACCENT};
            padding: 0.6rem 1.2rem;
            font-weight: bold;
            box-shadow: none; 
        }}
        .stButton>button:hover {{
            background-color: #3b506a; /* Darker blue on hover */
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

# ==============================================================================
# 3. CONTENT RENDERING FUNCTIONS
# ==============================================================================

def render_channel_content(service_name, channel_name):
    """
    Renders placeholder content tailored for the specific service and channel.
    """
    
    st.markdown(f"## 🛠️ {service_name}: {channel_name} Module")
    
    # Placeholder content based on the service name
    if service_name == "Picklist":
        st.info(f"Generate consolidated picklists for all pending orders from **{channel_name}**.")
        col1, col2 = st.columns(2)
        with col1:
            st.date_input("Select Order Date Range", key=f"date_{service_name}_{channel_name}", value=(pd.to_datetime('today'), pd.to_datetime('today')))
        with col2:
            st.selectbox("Select Warehouse", ["Main", "Secondary"], key=f"select_{service_name}_{channel_name}")
        st.button(f"Generate {channel_name} Picklist", key=f"btn_{service_name}_{channel_name}", type="primary")
    
    elif service_name == "Listing Maker":
        st.info(f"Create, bulk update, or optimize product listings for **{channel_name}**.")
        st.file_uploader(f"Upload {channel_name} Draft Listing File (Excel/CSV)", type=['xlsx', 'csv'], key=f"up_{service_name}_{channel_name}")
        st.button(f"Validate and Upload to {channel_name}", key=f"btn_{service_name}_{channel_name}", type="primary")
    
    elif service_name == "Reconciliations":
        st.info(f"Match sales data with payment settlements for **{channel_name}** to identify discrepancies.")
        st.file_uploader(f"Upload {channel_name} Settlement Report", type=['xlsx', 'csv'], key=f"up_{service_name}_{channel_name}")
        st.button(f"Run {channel_name} Reconciliation", key=f"btn_{service_name}_{channel_name}", type="primary")

    elif service_name == "Optimization":
        st.info(f"Tools to optimize pricing, inventory allocation, or advertising spend on **{channel_name}**.")
        st.slider("Inventory Threshold (%)", 0, 100, 75, key=f"slider_{service_name}_{channel_name}")
        st.button(f"Apply {channel_name} Pricing Rules", key=f"btn_{service_name}_{channel_name}", type="primary")

    elif service_name == "GST Reporting":
        st.info(f"Generate tax summaries (e.g., GSTR-1 data) for the selected period from **{channel_name}** sales.")
        st.selectbox("Select GST Form", ["GSTR-1 Summary", "GSTR-3B Input"], key=f"select_{service_name}_{channel_name}")
        st.button(f"Export {channel_name} GST Data", key=f"btn_{service_name}_{channel_name}", type="primary")
        
    elif service_name == "Configuration":
        st.info(f"Manage API keys, credentials, and master data mappings specific to **{channel_name}**.")
        st.text_input(f"{channel_name} API Key", "****************", type="password", key=f"input_{service_name}_{channel_name}")
        st.button(f"Save {channel_name} Settings", key=f"btn_{service_name}_{channel_name}", type="primary")


# ==============================================================================
# 4. NAVIGATION LOGIC: SIDEBAR (SERVICES) + TABS (CHANNELS)
# ==============================================================================

def setup_sidebar_navigation():
    """Sets up the six main service options in the sidebar."""
    st.sidebar.markdown('<h1>Operations Hub</h1>', unsafe_allow_html=True)
    
    # Initialize state with a default value
    if 'main_service' not in st.session_state:
        st.session_state.main_service = MAIN_SERVICES[0]
    
    # Determine the current index for the radio button
    try:
        current_index = MAIN_SERVICES.index(st.session_state.main_service)
    except ValueError:
        current_index = 0
        st.session_state.main_service = MAIN_SERVICES[0]

    # Create the sidebar radio button. Label is set to "" to hide the title.
    selected_main_service = st.sidebar.radio(
        "",  
        MAIN_SERVICES, 
        key='main_service_radio',
        index=current_index 
    )
    
    st.session_state.main_service = selected_main_service


def render_channel_tabs():
    """Renders the six channel options as tabs based on the selected main service."""
    
    current_service = st.session_state.main_service
    
    # Use st.tabs to create the channel navigation using the global CHANNELS list
    tabs = st.tabs(CHANNELS)

    # Render content inside the respective tab container
    for i, channel_name in enumerate(CHANNELS):
        with tabs[i]:
            # Call the content renderer for the specific Service and Channel
            render_channel_content(current_service, channel_name)


# ==============================================================================
# 5. MAIN APP EXECUTION
# ==============================================================================

def main():
    st.set_page_config(page_title="Operations Dashboard", layout="wide")
    
    # 1. Inject CSS for the theme and visibility
    inject_admin_panel_css()

    # 2. Setup Sidebar Navigation
    setup_sidebar_navigation()

    # 3. Render the Channel Tabs and Content
    st.markdown(f"# {st.session_state.main_service}") # Main Title for the content area
    render_channel_tabs()

if __name__ == "__main__":
    main()
