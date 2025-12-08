import streamlit as st
import pandas as pd
from io import BytesIO

# ==============================================================================
# 1. CONFIGURATION SECTION
# ==============================================================================

# --- NAVIGATION CONSTANTS ---
# The six main services that will appear as the TOP-LEVEL HEADER TABS.
MAIN_SERVICES = [
    "Picklist",
    "Listing Maker",
    "Reconciliations",
    "Optimization",
    "GST Reporting",
    "Configuration"
]

# The six channels that will appear as SUB-TABS inside each main service.
CHANNELS = [
    "Amazon",
    "Flipkart",
    "Myntra",
    "Meesho",
    "Ajio",
    "Jio Mart"
]

# --- THEME COLORS ---
VIBRANT_BLUE_ACCENT = "#4e73df" # Used for general buttons/elements
LIGHT_GRAY_BG = "#f5f8fb"
DARK_TEXT_DEFAULT = "#000000"  # NEW: Black for default text (Requested)
RED_ACCENT = "#dc3545"         # Red for active/hover states
DARK_SLATE_BLUE = "#263d57"    # Used for sub-headers


# ==============================================================================
# 2. UI/UX STYLING (KI-ADMIN INSPIRED HEADER THEME - BLACK & RED)
# ==============================================================================

def inject_header_css():
    """
    Injects custom CSS to style the main tabs as a primary website header navigation 
    with Black default text and Red active/hover states.
    """
    st.markdown(
        f"""
        <style>
        /* Base Streamlit Overrides */
        #MainMenu, footer, header {{visibility: hidden;}}
        
        /* Hide the Streamlit Sidebar completely */
        [data-testid="stSidebar"] {{
            display: none;
        }}
        
        /* --- Global Colors & Text --- */
        :root, body, .stApp {{
            color: {DARK_TEXT_DEFAULT} !important; 
            background-color: {LIGHT_GRAY_BG}; 
        }}
        
        /* Main Container Styling for Padding */
        .block-container {{
            padding-top: 2rem;
            padding-left: 2rem; 
            padding-right: 2rem; 
            padding-bottom: 5rem;
        }}
        
        /* --- TOP-LEVEL SERVICE TABS (The "Header Menu") --- */
        /* Targets the st.tabs container for the main services */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:first-child div[data-testid="stTabs"] {{
            margin-bottom: 2rem;
            background-color: white; 
            border-radius: 0; 
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08); 
            padding-left: 0; 
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        /* Default Style for the main service tabs (Header tabs) */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:first-child button[data-baseweb="tab"] {{
            color: {DARK_TEXT_DEFAULT} !important; /* DEFAULT: Black Text */
            font-size: 1.1rem;
            font-weight: 600;
            padding: 15px 30px !important; 
            border-bottom: 3px solid transparent !important;
            transition: color 0.2s, border-bottom 0.2s;
        }}
        
        /* Hover Style for the main service tabs */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:first-child button[data-baseweb="tab"]:hover {{
            color: {RED_ACCENT} !important; /* HOVER: Red Text */
        }}
        
        /* Active Style for the main service tabs */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:first-child button[data-baseweb="tab"][aria-selected="true"] {{
            color: {RED_ACCENT} !important; /* ACTIVE: Red Text */
            border-bottom: 3px solid {RED_ACCENT} !important; /* ACTIVE: Red Bottom Line */
        }}


        /* --- SECOND-LEVEL CHANNEL TABS (Sub-Navigation) --- */
        /* Targets tabs *within* the main content of a service */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:nth-child(2) div[data-testid="stTabs"] {{
            margin-top: 0.5rem;
            margin-bottom: 1.5rem;
            background-color: #ffffff; 
            border: 1px solid #e3eaf3;
            border-radius: 6px;
            box-shadow: none; 
            padding-left: 1rem;
        }}
        
        /* Default Style for the channel tabs (sub-tabs) */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:nth-child(2) button[data-baseweb="tab"] {{
            font-size: 1rem;
            padding: 8px 15px !important;
            color: {DARK_TEXT_DEFAULT} !important; /* DEFAULT: Black Text */
            transition: color 0.2s, border-bottom 0.2s;
        }}

        /* Hover Style for sub-tabs */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:nth-child(2) button[data-baseweb="tab"]:hover {{
            color: {RED_ACCENT} !important; /* HOVER: Red Text */
        }}
        
        /* Active Style for the channel tabs (sub-tabs) */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:nth-child(2) button[data-baseweb="tab"][aria-selected="true"] {{
            color: {RED_ACCENT} !important; /* ACTIVE: Red Text */
            border-bottom: 3px solid {RED_ACCENT} !important; /* ACTIVE: Red Bottom Line */
        }}


        /* --- Headers and Content Blocks --- */
        h1 {{
            display: none; 
        }}
        h2 {{
            color: {VIBRANT_BLUE_ACCENT}; 
            font-weight: 700;
            margin-bottom: 1rem;
            border-bottom: 1px dashed #cccccc;
            padding-bottom: 5px;
        }}
        h3, h4 {{
            color: {DARK_SLATE_BLUE}; 
            font-weight: 600;
        }}

        /* Card/Block Styles */
        div[data-testid="stVerticalBlock"]:not(:first-child) > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {{
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
            color: white !important; 
            border-radius: 6px; 
            border: 1px solid {VIBRANT_BLUE_ACCENT};
            padding: 0.6rem 1.2rem;
            font-weight: bold;
            box-shadow: none; 
        }}
        .stButton>button:hover {{
            background-color: #3b506a; 
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
    
    with st.container():
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
# 4. NAVIGATION LOGIC: HEADER (SERVICES) + TABS (CHANNELS)
# ==============================================================================

def render_application_layout():
    """Renders the entire application using nested tabs."""
    
    # 1. Initialize state with a default value
    if 'main_service' not in st.session_state:
        st.session_state.main_service = MAIN_SERVICES[0]
        st.session_state.active_channel = CHANNELS[0]

    # --- TOP-LEVEL HEADER (SERVICES) ---
    
    service_tabs = st.tabs(MAIN_SERVICES)
    
    for i, service_name in enumerate(MAIN_SERVICES):
        with service_tabs[i]:
            # This is the content area for the currently selected service.
            
            # --- SECOND-LEVEL TABS (CHANNELS) ---
            st.subheader(f"Channels for {service_name}")
            channel_tabs = st.tabs(CHANNELS)
            
            # Render content inside the respective channel tab
            for j, channel_name in enumerate(CHANNELS):
                with channel_tabs[j]:
                    render_channel_content(service_name, channel_name)


# ==============================================================================
# 5. MAIN APP EXECUTION
# ==============================================================================

def main():
    st.set_page_config(page_title="Operations Dashboard", layout="wide")
    
    # 1. Inject CSS for the theme and header structure
    inject_header_css()

    # 2. Render the entire nested tab structure
    render_application_layout()

if __name__ == "__main__":
    main()
