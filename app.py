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
VIBRANT_BLUE_ACCENT = "#4e73df"
LIGHT_GRAY_BG = "#f5f8fb"
DARK_TEXT = "#212529"
DARK_SLATE_BLUE = "#263d57"


# ==============================================================================
# 2. UI/UX STYLING (KI-ADMIN INSPIRED HEADER THEME)
# ==============================================================================

def inject_header_css():
    """
    Injects custom CSS to remove the sidebar and style the main tabs 
    as a primary website header navigation.
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
            color: {DARK_TEXT} !important; 
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
            border-radius: 0; /* Remove rounded corners for full header effect */
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08); /* Stronger shadow for separation */
            padding-left: 0; 
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        /* Style for the main service tabs (Header tabs) */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:first-child button[data-baseweb="tab"] {{
            color: {DARK_TEXT} !important; 
            font-size: 1.1rem;
            font-weight: 600;
            padding: 15px 30px !important; /* Larger padding for header buttons */
            border-bottom: 3px solid transparent !important;
        }}
        /* Active style for the main service tabs */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:first-child button[data-baseweb="tab"][aria-selected="true"] {{
            color: {VIBRANT_BLUE_ACCENT} !important; 
            border-bottom: 3px solid {VIBRANT_BLUE_ACCENT} !important; 
        }}


        /* --- SECOND-LEVEL CHANNEL TABS (Sub-Navigation) --- */
        /* Targets tabs *within* the main content of a service */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:nth-child(2) div[data-testid="stTabs"] {{
            margin-top: 0.5rem;
            margin-bottom: 1.5rem;
            background-color: #ffffff; /* Use pure white for sub-nav background */
            border: 1px solid #e3eaf3;
            border-radius: 6px;
            box-shadow: none; /* Remove shadow to distinguish from header */
            padding-left: 1rem;
        }}
        
        /* Style for the channel tabs (sub-tabs) */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:nth-child(2) button[data-baseweb="tab"] {{
            font-size: 1rem;
            padding: 8px 15px !important;
            color: #555555 !important;
        }}
        /* Active style for the channel tabs (sub-tabs) */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:nth-child(2) button[data-baseweb="tab"][aria-selected="true"] {{
            color: {DARK_SLATE_BLUE} !important; /* Darker blue for sub-nav active text */
            border-bottom: 3px solid {DARK_SLATE_BLUE} !important; 
        }}


        /* --- Headers and Content Blocks --- */
        h1 {{
            display: none; /* Hide the h1 title previously used for the service name */
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
    
    # We use H2 here since H1 is now the main navigation
    st.markdown(f"## 🛠️ {service_name}: {channel_name} Module") 
    
    # Wrap the content in a main container block to apply card styling
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
    
    # st.tabs returns a list of containers. We save the tabs for content rendering later.
    service_tabs = st.tabs(MAIN_SERVICES)
    
    # Loop through the service tabs to check which one is active.
    # Note: Streamlit's st.tabs relies on the user selecting a tab to make its
    # container "active" (i.e., display its content). We manually track the click
    # to know which service is active.
    
    # We need a unique key for st.tabs if we want to programmatically control it, 
    # but since st.tabs auto-manages the layout, we'll focus on rendering nested content.
    
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
