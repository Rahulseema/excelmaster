import streamlit as st
import pandas as pd
from io import BytesIO

# ==============================================================================
# 1. CONFIGURATION SECTION
# ==============================================================================

# --- NEW NAVIGATION CONSTANTS ---
# The six main services that will appear in the sidebar.
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

# ==============================================================================
# 2. UI/UX STYLING (High Contrast, Clean Theme)
# ==============================================================================

def inject_admin_panel_css():
    """Injects custom CSS for a fixed-sidebar theme with DARK TEXT for visibility."""
    st.markdown(
        """
        <style>
        /* Base Streamlit Overrides */
        #MainMenu, footer, header {visibility: hidden;}

        /* --- Global High Contrast Text --- */
        :root, body, .stApp {
            color: #212529 !important; /* Very Dark Gray for all text */
            background-color: #f5f8fb; /* Light background */
        }
        
        /* Sidebar Styling: Fixed, Full Height */
        [data-testid="stSidebar"] {
            background-color: #ffffff; 
            border-right: 1px solid #e3eaf3;
            box-shadow: 1px 0 5px rgba(0, 0, 0, 0.05);
            position: fixed; 
            height: 100vh; 
            padding-top: 0; 
        }
        
        /* Sidebar Header/Title */
        [data-testid="stSidebar"] h1 {
            color: #71a5cc; /* Pastel Blue for Logo/Title */
            font-size: 1.5rem;
            padding: 1.5rem 1.5rem 0.5rem 1.5rem;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid #f0f8ff; 
        }
        
        /* --- SIDEBAR MENU (Radio Buttons for Services) --- */
        [data-testid="stSidebar"] div[data-testid="stRadio"] label {
            font-size: 1.1rem;
            font-weight: 600;
            padding: 0.6rem 1.5rem;
            margin-left: 0; 
            width: 100%;
            color: #212529 !important; /* Dark text for sidebar links */
            transition: background-color 0.2s;
        }
        [data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
            background-color: #f0f8ff; 
        }
        /* Active Link Styling */
        [data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {
            background-color: #e6f1f8 !important; 
            color: #3f516d !important; 
            font-weight: 700 !important;
            border-left: 4px solid #71a5cc; 
        }

        /* Hide the radio circle/dot and empty label space */
        div[data-testid="stRadio"] label[data-baseweb="radio"] div:first-child {
            display: none !important;
        }
        div[data-testid="stSidebar"] div[data-testid="stForm"] > label {
            height: 0;
            padding: 0;
            margin: 0;
            overflow: hidden;
            display: block;
        }

        /* --- MAIN CONTENT TABS STYLING (Channels) --- */
        div[data-testid="stTabs"] {
            margin-bottom: 1.5rem;
            background-color: white; 
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            padding-left: 1rem;
        }
        button[data-baseweb="tab"] {
            color: #212529 !important; /* Dark text for inactive tabs */
            font-weight: 600;
            border-radius: 6px 6px 0 0 !important;
            padding: 10px 20px !important;
            background-color: transparent !important; 
            border-bottom: 3px solid transparent !important;
            transition: all 0.2s;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #3f516d !important; /* Dark blue for active tab */
            background-color: #ffffff !important; 
            border-bottom: 3px solid #71a5cc !important; 
        }


        /* --- Main Content Headers & Blocks --- */
        .block-container {
            padding-top: 2rem;
            padding-left: 2rem; 
            padding-right: 2rem; 
            padding-bottom: 5rem;
        }

        h1 {
            color: #212529; 
            font-weight: 700;
            margin-bottom: 1.5rem;
        }
        h2, h3, h4 {
            color: #3f516d; 
            font-weight: 600;
        }

        /* Card/Block Styles */
        div[data-testid="stVerticalBlock"], 
        div[data-testid="stHorizontalBlock"] {
            padding: 1.5rem;
            border-radius: 6px; 
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); 
            border: 1px solid #e3eaf3; 
            background: white;
            margin-bottom: 1.5rem;
        }

        /* Placeholder Button Style */
        .stButton>button {
            background-color: #a8d5ba;
            color: #212529 !important; 
            border-radius: 6px; 
            border: 1px solid #94c7a6;
            padding: 0.6rem 1.2rem;
            font-weight: bold;
            box-shadow: none; 
        }
        .stButton>button:hover {
            background-color: #94c7a6;
        }

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
    
    # Placeholder content based on the new service name
    if service_name == "Picklist":
        st.info(f"Generate consolidated picklists for all pending orders from **{channel_name}**.")
        st.date_input("Select Order Date Range", key=f"date_{service_name}_{channel_name}")
        st.button(f"Generate {channel_name} Picklist", key=f"btn_{service_name}_{channel_name}")
    
    elif service_name == "Listing Maker":
        st.info(f"Create, bulk update, or optimize product listings for **{channel_name}**.")
        st.file_uploader(f"Upload {channel_name} Draft Listing File (Excel/CSV)", type=['xlsx', 'csv'], key=f"up_{service_name}_{channel_name}")
    
    elif service_name == "Reconciliations":
        st.info(f"Match sales data with payment settlements for **{channel_name}** to identify discrepancies.")
        st.file_uploader(f"Upload {channel_name} Settlement Report", type=['xlsx', 'csv'], key=f"up_{service_name}_{channel_name}")
        st.button(f"Run {channel_name} Reconciliation", key=f"btn_{service_name}_{channel_name}")

    elif service_name == "Optimization":
        st.info(f"Tools to optimize pricing, inventory allocation, or advertising spend on **{channel_name}**.")
        st.slider("Inventory Threshold (%)", 0, 100, 75, key=f"slider_{service_name}_{channel_name}")
        st.button(f"Apply {channel_name} Pricing Rules", key=f"btn_{service_name}_{channel_name}")

    elif service_name == "GST Reporting":
        st.info(f"Generate tax summaries (e.g., GSTR-1 data) for the selected period from **{channel_name}** sales.")
        st.selectbox("Select GST Form", ["GSTR-1 Summary", "GSTR-3B Input"], key=f"select_{service_name}_{channel_name}")
        st.button(f"Export {channel_name} GST Data", key=f"btn_{service_name}_{channel_name}")
        
    elif service_name == "Configuration":
        st.info(f"Manage API keys, credentials, and master data mappings specific to **{channel_name}**.")
        st.text_input(f"{channel_name} API Key", "****************", type="password", key=f"input_{service_name}_{channel_name}")
        st.button(f"Save {channel_name} Settings", key=f"btn_{service_name}_{channel_name}")
    
    else:
        st.warning("No specific functionality defined yet.")

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
