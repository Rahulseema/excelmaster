import streamlit as st
import pandas as pd
from io import BytesIO

# ==============================================================================
# 1. CONFIGURATION SECTION (UNCHANGED)
# ==============================================================================

# Your 10 Master Account Names 
MASTER_ACCOUNT_NAMES = [
    "Drench", "Drench India", "Shine ArC", "Sparsh", "Sparsh SC",
    "BnB industries", "Shopforher", "Ansh Ent.", "AV Enterprises", "UV Enterprises"
]
THE_ONLY_CHANNEL = "Listing Compiler"
MAP_CHANNEL_SKU_COL = 'Channel SKU'
MAP_CHANNEL_SIZE_COL = 'Channel Size'
MAP_CHANNEL_COLOR_COL = 'Channel Color'
MAP_OUR_SKU_COL = 'Our SKU'
MAP_ACCOUNT_COL = 'Account name'
PICKLIST_SKU_COL = 'SKU'
PICKLIST_SIZE_COL = 'Size'
PICKLIST_COLOR_COL = 'Color'
PICKLIST_QTY_COL = 'Qty'
CHANNEL_COLUMNS_MAP = {
    THE_ONLY_CHANNEL: {'sku': 'SKU', 'size': 'Size', 'color': 'Color', 'qty': 'Qty'}, 
}
ALLOWED_FILE_TYPES = ['csv', 'xlsx']

# --- NAVIGATION CONSTANTS ---
MAIN_SERVICES = {
    "Listing Compiler": [
        "Consolidation Tool", "Meesho", "Flipkart", "Amazon", 
        "Myntra", "Nykaa", "Ajio", "JioMart", "Tatacliq"
    ],
    "GSTR Filing": [
        "GSTR1: Meesho", "GSTR1: Flipkart", "GSTR1: Amazon", "GSTR3B"
    ]
}

# Mapping tab names back to specific render functions
GSTR1_CHANNEL_MAP = {
    "GSTR1: Meesho": "Meesho", 
    "GSTR1: Flipkart": "Flipkart", 
    "GSTR1: Amazon": "Amazon"
}

# ==============================================================================
# 2. UI/UX STYLING (PHOENIX-INSPIRED PASTEL CSS) - MODIFIED FOR TABS
# ==============================================================================

def inject_admin_panel_css():
    """Injects custom CSS for a Phoenix-inspired, fixed-sidebar pastel theme."""
    st.markdown(
        """
        <style>
        /* Base Streamlit Overrides */
        #MainMenu, footer, header {visibility: hidden;}

        /* --- Pastel Phoenix Styling --- */
        
        /* Base Colors & Text */
        :root, body, .stApp {
            color: #3f516d !important; /* Deep slate blue for high-contrast text */
            background-color: #f5f8fb; /* Light, slightly cool gray background for main content */
        }
        
        /* Sidebar Styling: Fixed, Full Height, and Clean */
        [data-testid="stSidebar"] {
            background-color: #ffffff; /* White sidebar background */
            border-right: 1px solid #e3eaf3;
            box-shadow: 1px 0 5px rgba(0, 0, 0, 0.05);
            position: fixed; /* Fixes the sidebar position */
            height: 100vh; /* Full viewport height */
            padding-top: 0; /* Remove top padding */
        }
        
        /* Sidebar Header/Title */
        [data-testid="stSidebar"] h1 {
            color: #71a5cc; /* Soft Pastel Blue */
            font-size: 1.5rem;
            padding: 1.5rem 1.5rem 0.5rem 1.5rem;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid #f0f8ff; /* Subtle separation */
        }
        
        /* --- SIDEBAR MENU (RADIO BUTTONS FOR MAIN SERVICE) --- */
        [data-testid="stSidebar"] div[data-testid="stRadio"] label {
            /* Style the main menu items */
            font-size: 1.1rem;
            font-weight: 600;
            padding: 0.6rem 1.5rem;
            margin-left: 0; /* Align to the left edge */
            width: 100%;
            color: #3f516d;
            transition: background-color 0.2s;
        }
        [data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
            background-color: #f0f8ff; /* Light blue on hover */
        }
        /* Active Link Text Styling */
        [data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {
            background-color: #e6f1f8 !important; 
            color: #3f516d !important; 
            font-weight: 700 !important;
            border-left: 4px solid #71a5cc; /* Thicker pastel blue bar */
        }

        /* Hide the radio circle/dot */
        div[data-testid="stRadio"] label[data-baseweb="radio"] div:first-child {
            display: none !important;
        }
        
        /* --- MAIN CONTENT TABS STYLING (For Channel Navigation) --- */
        div[data-testid="stTabs"] {
            margin-bottom: 1.5rem;
            background-color: white; /* Ensure tabs area is visible */
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            padding-left: 1rem;
        }
        button[data-baseweb="tab"] {
            color: #71a5cc !important; /* Inactive tab text color - soft blue */
            font-weight: 600;
            border-radius: 6px 6px 0 0 !important;
            padding: 10px 20px !important;
            background-color: transparent !important; 
            border-bottom: 3px solid transparent !important;
            transition: all 0.2s;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #3f516d !important; /* Dark text for active tab */
            background-color: #ffffff !important; 
            border-bottom: 3px solid #71a5cc !important; /* Soft blue bottom bar */
        }


        /* --- Main Content Styling (Clean, Card-Based) --- */
        .block-container {
            padding-top: 2rem;
            padding-left: 2rem; 
            padding-right: 2rem; 
            padding-bottom: 5rem;
        }

        /* Headers */
        h1 {
            color: #71a5cc; 
            font-weight: 700;
            margin-bottom: 1.5rem;
        }
        h2, h3, h4 {
            color: #5890b9; 
            font-weight: 600;
        }

        /* Custom Card Styles: Clean, Phoenix-style container */
        div[data-testid="stVerticalBlock"], 
        div[data-testid="stHorizontalBlock"] {
            padding: 1.5rem;
            border-radius: 6px; /* Sharper corners */
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); /* Lighter, cleaner shadow */
            border: 1px solid #e3eaf3; 
            background: white;
            margin-bottom: 1.5rem;
        }
        
        /* Primary Button Style (Soft Green) */
        .stButton>button {
            background-color: #a8d5ba;
            color: #3f516d !important;
            border-radius: 6px; /* Sharper button corners */
            border: 1px solid #94c7a6;
            padding: 0.6rem 1.2rem;
            font-weight: bold;
            box-shadow: none; /* Keep buttons clean */
        }
        .stButton>button:hover {
            background-color: #94c7a6;
        }
        
        /* File Uploader styling */
        div[data-testid*="stFileUploader"] {
            background-color: #fcfdff; 
            border: 1px dashed #c8d9e6;
            border-radius: 6px;
            padding: 10px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

# ==============================================================================
# 3. HELPER FUNCTIONS (DATA PROCESSING & SAMPLE DOWNLOADS - UNCHANGED)
# ==============================================================================

def read_uploaded_file(uploaded_file, name):
    """Reads a file object into a Pandas DataFrame."""
    try:
        if uploaded_file.name.lower().endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.lower().endswith('.xlsx'):
            return pd.read_excel(uploaded_file, engine='openpyxl')
        return None
    except Exception as e:
        st.error(f"Error reading file **{name}**: {type(e).__name__} - {e}")
        return None

def get_sample_mapping_file():
    """Generates a sample Excel file for the SKU mapping template."""
    sample_data = {
        MAP_CHANNEL_SKU_COL: ['COMP-D101', 'COMP-D101', 'COMP-D102', 'COMP-D101'],
        MAP_CHANNEL_SIZE_COL: ['M', 'L', 'S', 'L'],
        MAP_CHANNEL_COLOR_COL: ['Red', 'Blue', 'Green', 'Red'],
        MAP_OUR_SKU_COL: ['DRENCH-T101-M-R', 'DRENCH-T101-L-B', 'DRENCH-T102-S-G', 'DRENCH-T101-L-R'],
        MAP_ACCOUNT_COL: ['Drench', 'Drench', 'Sparsh', 'Drench']
    }
    sample_df = pd.DataFrame(sample_data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        sample_df.to_excel(writer, index=False, sheet_name='Sample_Mapping')
    return output.getvalue()

def get_sample_picklist_file():
    """Generates a sample picklist file for the Listing Compiler channel."""
    config = CHANNEL_COLUMNS_MAP[THE_ONLY_CHANNEL]
    
    sample_data = {
        config['sku']: ['SKU-1001', 'SKU-1002', 'SKU-1003'],
        config['size']: ['XS', 'M', 'L'],
        config['color']: ['Black', 'Navy', 'Grey'],
        config['qty']: [20, 15, 12]
    }
    sample_df = pd.DataFrame(sample_data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        sample_df.to_excel(writer, index=False, sheet_name='Sample_Picklist')
    return output.getvalue()


def process_consolidation(raw_file_objects, mapping_file_object, uploaded_pick_list_count):
    st.success("Consolidation process complete! (Placeholder)")
    st.dataframe(pd.DataFrame({'SKU': ['D-101'], 'Qty': [50]}))


# ==============================================================================
# 4. CONTENT RENDERING FUNCTIONS (UNCHANGED)
# ==============================================================================

def render_consolidation_tool():
    """Renders the main Pick List Compilation tool."""
    
    st.markdown("## 📦 Consolidation Tool")
    
    st.subheader("1. Master SKU Mapping File Setup (REQUIRED)")
    st.markdown("Map **Channel SKU, Size, and Color** to your **Our SKU** for consolidation.")
    
    # Placeholder for file uploader and download
    col_map_upload, col_map_download = st.columns([2, 1])
    
    with col_map_upload:
        mapping_file = st.file_uploader(
            f"Upload Master Mapping File (CSV/Excel)",
            type=ALLOWED_FILE_TYPES,
            key="file_uploader_mapping"
        )
        st.session_state.mapping_file_object = mapping_file
    
    with col_map_download:
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True) 
        st.download_button(
            label="⬇️ Download Sample Mapping Template",
            data=get_sample_mapping_file(),
            file_name='sample_sku_mapping_template.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            use_container_width=True
        )

    st.markdown("---")
    
    st.subheader(f"2. {THE_ONLY_CHANNEL} Pick List Uploads (10 Accounts)")
    st.info("Upload pick list files here to be consolidated using the mapping file above.")
    
    # Placeholder for the 10 account uploaders
    accounts_to_upload = MASTER_ACCOUNT_NAMES
    cols = st.columns(3) 

    for j, account_name in enumerate(accounts_to_upload):
        unique_key = f"{THE_ONLY_CHANNEL}_{account_name.replace(' ', '_')}"
        with cols[j % 3]: 
            st.file_uploader(f"**{account_name}** Pick List", type=ALLOWED_FILE_TYPES, key=unique_key)
            
    st.markdown("---")
    st.subheader("3. Consolidate and Generate Pick List")
    if st.button("🚀 Run Consolidation", type="secondary"):
        process_consolidation({}, st.session_state.mapping_file_object, 1)


def render_gstr1_channel_tool(channel_name):
    """Renders the specific GSTR1 channel upload tool (e.g., Meesho, Amazon)."""
    
    st.markdown(f"## 📈 GSTR1 Preparation: {channel_name}")
    st.markdown(f"Upload the necessary reports from **{channel_name}** to prepare the GSTR-1 data.")
    
    with st.container():
        if channel_name == "Meesho":
            st.markdown('### Required Reports (Meesho)')
            st.file_uploader("1. Forward Sheet (CSV/Excel)", type=['csv', 'xlsx'], key="meesho_forward_uploader")
            st.file_uploader("2. Return Sheet (CSV/Excel)", type=['csv', 'xlsx'], key="meesho_return_uploader")
        
        elif channel_name == "Flipkart":
            st.markdown('### Required Reports (Flipkart)')
            st.file_uploader("1. Sales Data (CSV/Excel)", type=['csv', 'xlsx'], key="flipkart_sales_uploader")
            
        elif channel_name == "Amazon":
            st.markdown('### Required Reports (Amazon)')
            st.file_uploader("1. B2C MTR (CSV/Excel)", type=['csv', 'xlsx'], key="amazon_b2c_uploader")
            st.file_uploader("2. B2B MTR (CSV/Excel)", type=['csv', 'xlsx'], key="amazon_b2b_uploader")

        st.markdown("---")
        st.button(f"Generate {channel_name} GSTR1 Summary", type="secondary")

def render_gstr3b_tool():
    """Renders the GSTR3B Reconciliation tool."""
    st.markdown("## 📊 GSTR-3B Reconciliation")
    st.markdown("Upload documents to reconcile Input Tax Credit (ITC) and summary tax liability.")

    with st.container():
        st.warning("Future Feature: Upload GSTR-2A/2B for ITC reconciliation against your Purchase Register.")
        st.file_uploader("Upload GSTR-1 Summary Data (for comparison)", type=['csv', 'xlsx'], key="gstr3b_sales_uploader")
        st.file_uploader("Upload Purchase/Expense Register (for ITC calculation)", type=['csv', 'xlsx'], key="gstr3b_purchase_uploader")
        st.markdown("---")
        st.button("Run GSTR3B Reconciliation", type="secondary")

def render_default_page(menu_item):
    """Renders a default welcome page for undeveloped sections."""
    st.markdown(f"## 🚧 {menu_item} Module")
    st.info(f"This is the landing page for **{menu_item}**. Functionality will be implemented soon.")


# ==============================================================================
# 5. NAVIGATION LOGIC: SIDEBAR (MAIN) + TABS (CHANNELS)
# ==============================================================================

def setup_sidebar_navigation():
    """Sets up the simplified two-item sidebar menu."""
    st.sidebar.markdown('<h1>Operations Hub</h1>', unsafe_allow_html=True)
    
    if 'main_service' not in st.session_state:
        st.session_state.main_service = "Listing Compiler"
    
    # Static list of main services for the sidebar
    main_options = list(MAIN_SERVICES.keys())
    
    selected_main_service = st.sidebar.radio(
        "Main Services", 
        main_options, 
        key='main_service_radio',
        index=main_options.index(st.session_state.main_service)
    )
    
    st.session_state.main_service = selected_main_service


def render_channel_tabs():
    """Renders the channel options as tabs based on the selected main service."""
    
    current_service = st.session_state.main_service
    channel_options = MAIN_SERVICES[current_service]
    
    if not channel_options:
        st.warning("No channels defined for this service.")
        return

    # Use st.tabs to create the channel navigation
    tabs = st.tabs(channel_options)

    # Render content inside the respective tab container
    for i, channel_name in enumerate(channel_options):
        with tabs[i]:
            st.title(f"{current_service} - {channel_name}")
            
            if current_service == "Listing Compiler":
                if channel_name == "Consolidation Tool":
                    render_consolidation_tool()
                else:
                    render_default_page(f"Listing Compiler: {channel_name}")
            
            elif current_service == "GSTR Filing":
                if channel_name == "GSTR3B":
                    render_gstr3b_tool()
                elif channel_name in GSTR1_CHANNEL_MAP:
                    render_gstr1_channel_tool(GSTR1_CHANNEL_MAP[channel_name])
                else:
                    render_default_page(f"GSTR Filing: {channel_name}")


# ==============================================================================
# 6. MAIN APP EXECUTION
# ==============================================================================

def main():
    st.set_page_config(page_title="Operations Dashboard", layout="wide")
    
    # 1. Inject CSS for the Phoenix-Inspired Look
    inject_admin_panel_css()

    # 2. Setup Sidebar Navigation
    setup_sidebar_navigation()

    # 3. Render the Channel Tabs and Content
    st.markdown(f"# {st.session_state.main_service}") # Main Title
    render_channel_tabs()

if __name__ == "__main__":
    # Ensure session state is initialized
    if 'raw_file_objects' not in st.session_state:
        st.session_state.raw_file_objects = {}
    if 'mapping_file_object' not in st.session_state:
        st.session_state.mapping_file_object = None

    main()
