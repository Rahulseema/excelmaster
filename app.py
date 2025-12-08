import streamlit as st
import pandas as pd
from io import BytesIO

# ==============================================================================
# 1. CONFIGURATION SECTION
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
        "GSTR1", "GSTR3B"
    ]
}
GSTR1_SUB_CHANNELS = ["Meesho", "Flipkart", "Amazon"]

# ==============================================================================
# 2. UI/UX STYLING (PASTEL ADMIN CSS - Sidebar Focused)
# ==============================================================================

def inject_admin_panel_css():
    """Injects custom CSS for a soft, low-contrast pastel theme, optimized for sidebar."""
    st.markdown(
        """
        <style>
        /* Base Streamlit Overrides */
        #MainMenu, footer, header {visibility: hidden;}

        /* --- Pastel Admin Styling --- */
        
        /* Base Colors & Text */
        :root, body, .stApp {
            color: #3f516d !important; /* Deep slate blue for high-contrast text */
            background-color: #fcfdff; /* Very soft white/cream background */
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff; /* White sidebar background */
            border-right: 1px solid #e3eaf3;
            box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
        }

        /* Sidebar Header/Title */
        [data-testid="stSidebar"] h1 {
            color: #71a5cc; /* Soft Pastel Blue */
            font-size: 1.5rem;
            padding: 1rem 1.5rem 0.5rem 1.5rem;
            margin-bottom: 0.5rem;
        }

        /* Expander/Menu Header Styling */
        div[data-testid="stExpander"] button {
            color: #3f516d !important; /* Dark text for menu headers */
            font-weight: 600;
            padding: 0.5rem 0rem 0.5rem 1.5rem; 
            border-radius: 4px;
        }
        div[data-testid="stExpander"] button:hover {
            background-color: #f0f8ff; /* Light blue on hover */
        }
        
        /* Adjust Expander Icon/Arrow */
        div[data-testid="stExpanderIcon"] {
            color: #71a5cc; /* Soft Blue Arrow/Icon */
        }
        
        /* Radio Button / Navigation Links (Mimicking the image style) */
        div[data-testid="stRadio"] label {
            padding: 0.3rem 0rem 0.3rem 2.5rem; /* Indentation for sub-links */
            margin-left: -1rem; /* Adjust horizontal position */
            width: 100%;
            border-radius: 4px;
            font-weight: 500;
            color: #5890b9; /* Slightly softer text for sub-links */
        }
        div[data-testid="stRadio"] label:hover {
            background-color: #f0f8ff; 
        }

        /* Highlight Active Radio Button */
        div[data-testid="stRadio"] label[data-baseweb="radio"] div:first-child {
            /* Hide the actual radio circle/dot */
            display: none !important;
        }
        
        /* Active Link Text Styling */
        div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {
            background-color: #e6f1f8 !important; /* Very light active background */
            color: #3f516d !important; /* Dark text for active link */
            font-weight: 600 !important;
            border-left: 3px solid #71a5cc; /* Pastel blue indicator bar */
        }


        /* --- Main Content Styling (Kept Pastel) --- */
        .block-container {
            padding-top: 2rem;
            padding-left: 2rem; 
        }

        h1 {
            color: #71a5cc; 
            font-weight: 700;
        }
        h2, h3, h4 {
            color: #5890b9; 
            font-weight: 600;
        }

        /* Custom Card Styles */
        div[data-testid="stVerticalBlock"], div[data-testid="stHorizontalBlock"] {
            padding: 1.5rem;
            border-radius: 10px; 
            box-shadow: 0 6px 15px -3px rgba(0, 0, 0, 0.08); 
            border: 1px solid #e3eaf3; 
            background: white;
            margin-bottom: 2rem;
        }
        
        /* Button Style (Soft Green) */
        .stButton>button {
            background-color: #a8d5ba;
            color: #3f516d !important;
            border-radius: 8px;
            border: 1px solid #94c7a6;
            padding: 0.6rem 1.2rem;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #94c7a6;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

# ==============================================================================
# 3. HELPER FUNCTIONS (DATA PROCESSING - Omitted for brevity, assumed unchanged)
# ==============================================================================

# (Keeping only necessary functions for demonstration of structure)
def get_sample_mapping_file():
    # ... (function body remains the same)
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


# ==============================================================================
# 4. CONTENT RENDERING FUNCTIONS
# ==============================================================================

def render_consolidation_tool():
    """Renders the main Pick List Compilation tool."""
    
    st.title("📦 Listing Compiler: Consolidation Tool")
    
    # ... (Content from previous render_picklist_tab, sections 1, 2, 3) ...
    
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
    st.button("🚀 Run Consolidation", type="secondary") # Placeholder action

def render_gstr1_channel_tool(channel_name):
    """Renders the specific GSTR1 channel upload tool (e.g., Meesho, Amazon)."""
    st.title(f"📊 GSTR1 Preparation: {channel_name}")
    st.markdown(f"Upload the necessary reports from **{channel_name}** to prepare the GSTR-1 data.")
    
    with st.container():
        if channel_name == "Meesho":
            st.markdown('### Required Reports')
            st.file_uploader("1. Forward Sheet (CSV/Excel)", type=['csv', 'xlsx'], key="meesho_forward_uploader")
            st.file_uploader("2. Return Sheet (CSV/Excel)", type=['csv', 'xlsx'], key="meesho_return_uploader")
        
        elif channel_name == "Flipkart":
            st.markdown('### Required Reports')
            st.file_uploader("1. Sales Data (CSV/Excel)", type=['csv', 'xlsx'], key="flipkart_sales_uploader")
            
        elif channel_name == "Amazon":
            st.markdown('### Required Reports')
            st.file_uploader("1. B2C MTR (CSV/Excel)", type=['csv', 'xlsx'], key="amazon_b2c_uploader")
            st.file_uploader("2. B2B MTR (CSV/Excel)", type=['csv', 'xlsx'], key="amazon_b2b_uploader")

        st.markdown("---")
        st.button(f"Generate {channel_name} GSTR1 Summary", type="secondary") # Placeholder action

def render_gstr3b_tool():
    """Renders the GSTR3B Reconciliation tool."""
    st.title("📊 GSTR-3B Reconciliation")
    st.markdown("Upload documents to reconcile Input Tax Credit (ITC) and summary tax liability.")

    with st.container():
        st.warning("Future Feature: Upload GSTR-2A/2B for ITC reconciliation against your Purchase Register.")
        st.file_uploader("Upload GSTR-1 Summary Data (for comparison)", type=['csv', 'xlsx'], key="gstr3b_sales_uploader")
        st.file_uploader("Upload Purchase/Expense Register (for ITC calculation)", type=['csv', 'xlsx'], key="gstr3b_purchase_uploader")
        st.markdown("---")
        st.button("Run GSTR3B Reconciliation", type="secondary") # Placeholder action

def render_default_page(menu_item):
    """Renders a default welcome page for undeveloped sections."""
    st.title(f"Welcome to the {menu_item} Module")
    st.info(f"This is the landing page for **{menu_item}**. Functionality will be implemented soon.")


# ==============================================================================
# 5. SIDEBAR NAVIGATION LOGIC
# ==============================================================================

def setup_sidebar_navigation():
    """
    Sets up the tiered sidebar menu structure and controls the page state.
    """
    st.sidebar.markdown('<h1>Operations Hub</h1>', unsafe_allow_html=True)
    
    # Initialize the current page selection in session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Consolidation Tool"

    # --- LISTING COMPILER Section ---
    with st.sidebar.expander("📦 Listing Compiler", expanded=True):
        
        compiler_options = [
            sub for sub in MAIN_SERVICES["Listing Compiler"] 
            if sub not in ["Meesho", "Flipkart", "Amazon", "Myntra", "Nykaa", "Ajio", "JioMart", "Tatacliq"]
        ]
        
        # Consolidation Tool is the first option
        st.session_state.current_page = st.radio(
            "Compiler Apps", 
            compiler_options, 
            key='listing_compiler_radio',
            index=compiler_options.index(st.session_state.current_page) if st.session_state.current_page in compiler_options else 0
        )
        
        # Sub-channels for Listing Compiler (displayed as simple text/placeholders for this tool)
        st.sidebar.markdown('**--- Sub-Channels ---**')
        for sub_channel in [
            "Meesho", "Flipkart", "Amazon", "Myntra", 
            "Nykaa", "Ajio", "JioMart", "Tatacliq"
        ]:
             # Mimic non-clickable menu items
            st.sidebar.markdown(f'<div style="padding-left: 2.5rem; color: #5890b9; font-size: 0.95rem;">{sub_channel}</div>', unsafe_allow_html=True)

    # --- GSTR FILING Section ---
    with st.sidebar.expander("📊 GSTR Filing", expanded=True):
        
        # GSTR1 Sub-menu (Nested Expander)
        with st.expander("GSTR1"):
            gstr1_options = GSTR1_SUB_CHANNELS
            
            # Check if current page is one of the GSTR1 options to set the initial index
            if st.session_state.current_page in gstr1_options:
                current_index = gstr1_options.index(st.session_state.current_page)
            else:
                current_index = 0

            # This is the actual GSTR1 channel selection radio
            selected_gstr1 = st.radio(
                "GSTR1 Channels", 
                gstr1_options, 
                key='gstr1_channels_radio',
                index=current_index
            )
            # Update current page only if a GSTR1 option is actively selected/clicked
            if selected_gstr1 != st.session_state.current_page:
                 st.session_state.current_page = selected_gstr1

        # GSTR3B Main Option
        gstr_options = ["GSTR3B"]
        if st.session_state.current_page == "GSTR3B":
             gstr3b_index = 0
        else:
             gstr3b_index = -1 # Ensures this radio only controls the state if clicked

        selected_gstr3b = st.radio(
            "Reconciliation",
            gstr_options,
            key='gstr3b_radio',
            index=gstr3b_index
        )
        # Update current page only if GSTR3B is actively selected/clicked
        if selected_gstr3b != st.session_state.current_page:
            st.session_state.current_page = selected_gstr3b

# ==============================================================================
# 6. MAIN APP EXECUTION
# ==============================================================================

def main():
    st.set_page_config(page_title="Operations Dashboard", layout="wide")
    
    # 1. Inject CSS for the Pastel Sidebar Look
    inject_admin_panel_css()

    # 2. Setup Sidebar Navigation
    setup_sidebar_navigation()

    # 3. Render the Main Content based on Selection
    
    current_page = st.session_state.current_page

    if current_page == "Consolidation Tool":
        render_consolidation_tool()
    
    elif current_page in GSTR1_SUB_CHANNELS:
        render_gstr1_channel_tool(current_page)
        
    elif current_page == "GSTR3B":
        render_gstr3b_tool()
    
    else:
        # Fallback for any other menu options (e.g., Myntra, Nykaa, etc.)
        render_default_page(current_page)

if __name__ == "__main__":
    # Ensure raw_file_objects is initialized (keeping for consistency)
    if 'raw_file_objects' not in st.session_state:
        st.session_state.raw_file_objects = {}
    if 'mapping_file_object' not in st.session_state:
        st.session_state.mapping_file_object = None

    main()
