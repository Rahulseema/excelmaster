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

# ==============================================================================
# 2. UI/UX STYLING (MATDASH ADMIN CSS)
# ==============================================================================

def inject_admin_panel_css():
    """Injects custom CSS to mimic the MatDash Admin Template look."""
    st.markdown(
        """
        <style>
        /* Base Streamlit Overrides */
        #MainMenu, footer, header {visibility: hidden;}

        /* --- MatDash Admin Styling --- */
        
        /* Base Colors & Text */
        :root, body, .stApp {
            color: #1f2937 !important; /* Dark Slate Gray for primary text */
            background-color: #f8f9fa; /* Light gray background */
            padding-top: 1.5rem;
        }
        
        /* General Text, Labels, Spans */
        p, label, .stMarkdown, div[data-testid="stText"], 
        div[data-testid*="stFileUploader"] label, span {
            color: #1f2937 !important;
            line-height: 1.6;
            font-size: 1rem;
        }
        
        /* Sidebar Styling */
        .st-emotion-cache-1g82m8b, .st-emotion-cache-1wmy991 { /* Sidebar container classes */
            background-color: #ffffff !important; /* White sidebar */
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06);
        }

        /* Custom Card Styles: Defined shadow, crisp look */
        div[data-testid="stVerticalBlock"],
        div[data-testid="stHorizontalBlock"] {
            padding: 1.5rem;
            border-radius: 6px; /* Sharper corners */
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.08); /* Stronger shadow */
            border: 1px solid #e5e7eb; /* Light border */
            background: white;
            margin-bottom: 2rem;
            transition: box-shadow 0.2s ease-in-out;
        }
        
        /* Header Styles: Deep Indigo Accent */
        h1 {
            color: #4f46e5; /* Deep Indigo for main title */
            font-weight: 800;
            margin-bottom: 0.5rem;
            margin-top: 0;
            padding-bottom: 0.5rem;
        }
        h2, h3, h4 {
            color: #1f2937; /* Dark text for sub-headers */
            font-weight: 700;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        
        /* Primary Button Style (Emerald Green for Action) */
        .stButton>button {
            background-color: #10b981; /* Emerald Green */
            color: white !important; 
            border-radius: 6px;
            border: none;
            padding: 0.6rem 1.2rem;
            font-weight: bold;
            letter-spacing: 0.5px;
            transition: background-color 0.2s;
        }
        .stButton>button:hover {
            background-color: #059669; /* Darker green on hover */
        }

        /* Metric styling: Clean and prominent */
        div[data-testid="stMetric"] {
            background-color: #f3f4f6; /* Very light gray */
            border-radius: 6px;
            padding: 1rem;
            border: 1px solid #d1d5db;
        }
        div[data-testid="stMetricValue"] {
            color: #4f46e5 !important; /* Indigo value */
            font-size: 2rem;
            font-weight: 800;
        }
        div[data-testid="stMetricLabel"] label {
            color: #1f2937 !important; 
            font-weight: 600;
            text-transform: uppercase;
        }

        /* Sidebar Navigation: Highlight Active Tab with Indigo */
        .st-emotion-cache-1cypcdb label {
            color: #1f2937 !important;
            font-weight: 600;
            padding: 8px 10px;
            border-radius: 4px;
        }
        .st-emotion-cache-1cypcdb [data-baseweb="radio"] > div {
             /* Target active radio label background for Indigo accent */
             background-color: transparent;
        }
        .st-emotion-cache-1cypcdb [aria-checked="true"] {
             background-color: #eef2ff !important; /* Very light indigo background for active tab */
             border-left: 4px solid #4f46e5; /* Indigo accent bar */
             border-radius: 0px 6px 6px 0px; 
             margin-left: -15px; /* Pull active tab out slightly */
             padding-left: 10px !important;
             color: #4f46e5 !important; /* Active tab text color */
        }
        .st-emotion-cache-1cypcdb [aria-checked="true"] label {
            color: #4f46e5 !important; /* Active tab text color */
        }


        /* Horizontal rule color */
        hr {
            border-top: 1px solid #e5e7eb; 
            margin: 1.5rem 0;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

def admin_header(title):
    """Renders the main page title with admin styling."""
    st.markdown(f'<h1>{title}</h1>', unsafe_allow_html=True)
    st.markdown('<hr style="border-top: 1px solid #e9ecef;">', unsafe_allow_html=True)


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
    """Handles the heavy lifting of reading, mapping, and summing the data."""
    if uploaded_pick_list_count == 0:
        st.error("No pick list files were uploaded. Please upload at least one pick list file to run consolidation.")
        return

    with st.spinner(f"Processing {uploaded_pick_list_count} files... Reading, cleaning, merging, and consolidating data."):
        
        # Read Mapping File
        mapping_df = read_uploaded_file(mapping_file_object, "Mapping File")
        if mapping_df is None: return

        processed_data = []
        
        # 1. Process and Clean all Account DataFrames
        for key, item in raw_file_objects.items():
            if item['file'] is None: continue 
            
            df = read_uploaded_file(item['file'], f"{item['account']}")
            if df is not None:
                config = CHANNEL_COLUMNS_MAP[THE_ONLY_CHANNEL]
                
                try:
                    # Rename columns to standard names for merging
                    df_clean = df.rename(columns={
                        config['sku']: MAP_CHANNEL_SKU_COL,
                        config['size']: MAP_CHANNEL_SIZE_COL,
                        config['color']: MAP_CHANNEL_COLOR_COL,
                        config['qty']: PICKLIST_QTY_COL
                    })
                    
                    # Keep all relevant columns for the merge key + Qty
                    df_clean = df_clean[[MAP_CHANNEL_SKU_COL, MAP_CHANNEL_SIZE_COL, MAP_CHANNEL_COLOR_COL, PICKLIST_QTY_COL]]
                    df_clean[MAP_ACCOUNT_COL] = item['account'] 
                    processed_data.append(df_clean)
                    
                except KeyError as e:
                    st.error(f"Column Mismatch in **{item['account']}**: Column {e} not found.")
                    st.warning(f"Configuration Check: SKU='{config['sku']}', Size='{config['size']}', Color='{config['color']}', Qty='{config['qty']}'")
                    return

        # 2. Combine and Map
        combined_picklist_df = pd.concat(processed_data, ignore_index=True)

        # 🔑 Merge on COMPOUND KEY (4 columns)
        merge_keys = [MAP_CHANNEL_SKU_COL, MAP_CHANNEL_SIZE_COL, MAP_CHANNEL_COLOR_COL, MAP_ACCOUNT_COL]
        merged_df = pd.merge(
            combined_picklist_df,
            mapping_df[[MAP_CHANNEL_SKU_COL, MAP_CHANNEL_SIZE_COL, MAP_CHANNEL_COLOR_COL, MAP_OUR_SKU_COL, MAP_ACCOUNT_COL]],
            on=merge_keys,
            how='left'
        )
        
        # Handle unmapped items (No 'Our SKU' found) by safely concatenating 'UNMAPPED-'
        merged_df[MAP_CHANNEL_SKU_COL] = merged_df[MAP_CHANNEL_SKU_COL].astype(str)

        unmapped_mask = merged_df[MAP_OUR_SKU_COL].isna()
        
        merged_df.loc[unmapped_mask, MAP_OUR_SKU_COL] = (
            'UNMAPPED-' + merged_df.loc[unmapped_mask, MAP_CHANNEL_SKU_COL]
        )
        # -----------------------------

        # 3. Final Consolidation and Output Formatting
        # Aggregate QTY by all identifying columns
        final_compiled_picklist = merged_df.groupby([
            MAP_CHANNEL_SKU_COL, 
            MAP_CHANNEL_SIZE_COL, 
            MAP_CHANNEL_COLOR_COL, 
            MAP_OUR_SKU_COL 
        ])[PICKLIST_QTY_COL].sum().reset_index()
        
        final_compiled_picklist.rename(
            columns={PICKLIST_QTY_COL: 'Total Pick Quantity'},
            inplace=True
        )
        
        # Final required column order:
        final_compiled_picklist = final_compiled_picklist[[
            MAP_CHANNEL_SKU_COL, 
            MAP_CHANNEL_SIZE_COL, 
            MAP_CHANNEL_COLOR_COL, 
            MAP_OUR_SKU_COL, 
            'Total Pick Quantity'
        ]]
        final_compiled_picklist = final_compiled_picklist.sort_values(by=MAP_OUR_SKU_COL)

        # 4. Display and Download
        st.subheader("✅ Final Master Pick List by Our SKU")
        
        st.dataframe(final_compiled_picklist, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            final_compiled_picklist.to_excel(writer, index=False, sheet_name='Master_Picklist_D_SKU')
        
        st.download_button(
            label="⬇️ Download Master Pick List (Excel)",
            data=output.getvalue(),
            file_name='compiled_master_picklist.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        st.balloons()


# ==============================================================================
# 4. PICK LIST COMPILER TAB FUNCTION (CONSOLIDATED & ADMIN-STYLE)
# ==============================================================================

def render_picklist_tab():
    
    admin_header("📦 Master Pick List Compiler")

    if 'raw_file_objects' not in st.session_state:
        st.session_state.raw_file_objects = {}
    if 'mapping_file_object' not in st.session_state:
        st.session_state.mapping_file_object = None

    # --- 1. SETUP & MAPPING FILE UPLOAD ---
    
    st.subheader("1. Master SKU Mapping File Setup (REQUIRED)")
    st.markdown("Map **Channel SKU, Size, and Color** to your **Our SKU** for consolidation.")
    
    col_map_upload, col_map_download = st.columns([2, 1])
    
    with col_map_upload:
        mapping_file = st.file_uploader(
            f"Upload Master Mapping File (CSV/Excel)",
            type=ALLOWED_FILE_TYPES,
            key="file_uploader_mapping"
        )
        st.session_state.mapping_file_object = mapping_file
    
    with col_map_download:
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True) # Vertical spacing
        st.download_button(
            label="⬇️ Download Sample Mapping Template",
            data=get_sample_mapping_file(),
            file_name='sample_sku_mapping_template.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            use_container_width=True
        )

    st.markdown("---")
    
    # --- 2. LISTING COMPILER UPLOADS ---

    st.subheader(f"2. {THE_ONLY_CHANNEL} Pick List Uploads (10 Accounts)")
    
    config = CHANNEL_COLUMNS_MAP[THE_ONLY_CHANNEL]
    st.info(f"All 10 accounts must use these column headers: **SKU**: `{config['sku']}`, **Size**: `{config['size']}`, **Color**: `{config['color']}`, **Qty**: `{config['qty']}`.")

    # Sample Download Option for Pick List
    st.download_button(
        label=f"⬇️ Download {THE_ONLY_CHANNEL} Sample Template (Excel)",
        data=get_sample_picklist_file(),
        file_name=f'sample_{THE_ONLY_CHANNEL.lower().replace(" ", "_")}_picklist.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    st.markdown("---")

    # Uploader section for the 10 accounts
    accounts_to_upload = MASTER_ACCOUNT_NAMES
    cols = st.columns(3) 

    for j, account_name in enumerate(accounts_to_upload):
        unique_key = f"{THE_ONLY_CHANNEL}_{account_name.replace(' ', '_')}"
        
        with cols[j % 3]: 
            uploaded_file = st.file_uploader(
                f"**{account_name}** Pick List",
                type=ALLOWED_FILE_TYPES,
                key=unique_key
            )
            
            st.session_state.raw_file_objects[unique_key] = {
                'file': uploaded_file,
                'channel': THE_ONLY_CHANNEL,
                'account': account_name
            }

    st.markdown("---")

    # --- 3. CONSOLIDATION & SUBMIT ---
    
    st.subheader("3. Consolidate and Generate Pick List")
    
    TOTAL_POTENTIAL_UPLOADS = len(MASTER_ACCOUNT_NAMES) 
    uploaded_pick_list_count = sum(1 for item in st.session_state.raw_file_objects.values() if item['file'] is not None)

    col_metric, col_submit = st.columns([1, 2])

    with col_metric:
        st.metric(label="Pick List Files Uploaded", value=uploaded_pick_list_count, delta=f"Total Slots: {TOTAL_POTENTIAL_UPLOADS}")

    with col_submit:
        st.markdown('<br>', unsafe_allow_html=True) # Vertical spacing
        
        if st.session_state.mapping_file_object is None:
            st.error("🔴 **Mapping File Required:** Please upload the Master SKU Mapping File (Section 1).")
        
        elif uploaded_pick_list_count >= 1:
            st.success("✅ All requirements met! Click Submit to generate.")
            
            if st.button("🚀 SUBMIT: Generate Master Pick List", type="secondary", use_container_width=True):
                process_consolidation(st.session_state.raw_file_objects, st.session_state.mapping_file_object, uploaded_pick_list_count)
        
        else:
            st.warning("🟡 **Pick List Required:** Please upload at least one pick list file (Section 2).")


# ==============================================================================
# 5. GST FILING TOOLS TAB FUNCTION (ADMIN-STYLE)
# ==============================================================================

def render_gst_tab():
    admin_header("📊 GST Filing Tools")
    st.markdown("Tools to assist with GSTR-1 and GSTR-3B preparation.")
    st.markdown("---")

    st.subheader("GSTR-1 Preparation (Sales Summary)")
    st.markdown("Generate your monthly GSTR-1 summary.")
    
    with st.container():
        st.warning("Future Feature: Upload Sales Reports to generate HSN/GST summary.")
        gstr1_file = st.file_uploader("Upload Monthly Sales Register (CSV/Excel)", type=['csv', 'xlsx'], key="gstr1_uploader")
        if gstr1_file: st.info(f"File '{gstr1_file.name}' uploaded for GSTR-1 analysis.")

    st.markdown("---")

    st.subheader("GSTR-3B Reconciliation (Summary & ITC)")
    st.markdown("Reconcile Input Tax Credit (ITC) and summary tax liability.")
    
    with st.container():
        st.warning("Future Feature: Upload GSTR-2A/2B for ITC reconciliation against your Purchase Register.")
        gstr3b_sales_file = st.file_uploader("Upload GSTR-1 Summary Data (for comparison)", type=['csv', 'xlsx'], key="gstr3b_sales_uploader")
        gstr3b_purchase_file = st.file_uploader("Upload Purchase/Expense Register (for ITC calculation)", type=['csv', 'xlsx'], key="gstr3b_purchase_uploader")
        if gstr3b_sales_file and gstr3b_purchase_file: st.info("Sales and Purchase files uploaded for GSTR-3B reconciliation.")

# ==============================================================================
# 6. MAIN APP EXECUTION
# ==============================================================================

def main():
    st.set_page_config(page_title="Operations Dashboard", layout="wide")
    
    # Inject CSS for Admin Panel Look
    inject_admin_panel_css()

    # Sidebar Navigation
    with st.sidebar:
        st.markdown('<div style="margin-top: 1rem; font-size: 1.5rem; color: #4f46e5; font-weight: 700;">OPERATIONS HUB</div>', unsafe_allow_html=True)
        st.markdown('<hr style="border-top: 1px solid #e5e7eb;">', unsafe_allow_html=True)
        selected_tab = st.radio(
            "Navigation:",
            ["📦 Pick List Compiler", "📊 GST Filing Tools"],
            format_func=lambda x: x.replace(" ", " • "),
            key="main_navigation"
        )
        st.markdown("---")
        st.info("Built for streamlined supplier operations.")

    # Render the selected tab
    if selected_tab == "📦 Pick List Compiler":
        render_picklist_tab()
    elif selected_tab == "📊 GST Filing Tools":
        render_gst_tab()

if __name__ == "__main__":
    main()
