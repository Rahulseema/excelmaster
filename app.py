import streamlit as st
import pandas as pd
from io import BytesIO

# ==============================================================================
# 1. CONFIGURATION SECTION (CRITICAL: ADJUST COLUMN NAMES HERE!)
# ==============================================================================

# Your 10 Master Account Names (Must match account name used in Mapping File)
MASTER_ACCOUNT_NAMES = [
    "Drench", "Drench India", "Shine ArC", "Sparsh", "Sparsh SC",
    "BnB industries", "Shopforher", "Ansh Ent.", "AV Enterprises", "UV Enterprises"
]

# Selling Channels
MULTI_ACCOUNT_CHANNELS = ["Meesho", "Amazon", "Flipkart", "Myntra"] # 10 accounts each
SINGLE_ACCOUNT_CHANNELS = ["Nykaa", "JioMart", "Ajio", "Tatacliq"] # 1 account each (for now)

ALL_CHANNELS = MULTI_ACCOUNT_CHANNELS + SINGLE_ACCOUNT_CHANNELS

# Configuration for Pick List Column Names by Channel
# !!! WARNING: VERIFY THESE COLUMN NAMES AGAINST YOUR ACTUAL REPORTS !!!
CHANNEL_COLUMNS_MAP = {
    "Meesho": {'sku': 'SKU ID', 'qty': 'Quantity'},
    "Amazon": {'sku': 'sku', 'qty': 'quantity-purchased'}, 
    "Flipkart": {'sku': 'Seller SKU ID', 'qty': 'quantity-purchased'},
    "Myntra": {'sku': 'Seller SKU', 'qty': 'Quantity'},
    "Nykaa": {'sku': 'Seller Code', 'qty': 'Inventory Qty'}, 
    "JioMart": {'sku': 'Product SKU', 'qty': 'Order Qty'},
    "Ajio": {'sku': 'Seller SKU', 'qty': 'Unit Qty'},
    "Tatacliq": {'sku': 'Item Code', 'qty': 'Units'},
}

# Mapping file column names (as provided):
MAP_CHANNEL_SKU_COL = 'Channel SKU'
MAP_D_SKU_COL = 'D SKU'
MAP_ACCOUNT_COL = 'Account name'

ALLOWED_FILE_TYPES = ['csv', 'xlsx']

# --- Helper Functions ---

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

# ==============================================================================
# 2. PICK LIST COMPILER TAB FUNCTION
# ==============================================================================

def render_picklist_tab():
    st.title("📦 44-File Multi-Channel Master Pick List Compiler")
    st.markdown("Upload reports for **44 accounts/channels** and click **Submit** to consolidate.")
    st.markdown("---")

    # Session state for managing all uploaded file objects and mapping file
    if 'raw_file_objects' not in st.session_state:
        st.session_state.raw_file_objects = {}
    if 'mapping_file_object' not in st.session_state:
        st.session_state.mapping_file_object = None

    # --- SETUP & UPLOADING TABS ---
    
    # Tabs for each channel plus a setup tab
    tab_titles = ["1. Setup (Mapping File)"] + [f"2. Upload - {c}" for c in ALL_CHANNELS]
    tabs = st.tabs(tab_titles)
    
    # 1. SETUP TAB (MAPPING FILE)
    with tabs[0]:
        st.header("1. Master SKU Mapping File")
        st.markdown("This file tells the system how to map each Channel SKU from a specific Account to your Master D SKU.")
        mapping_file = st.file_uploader(
            f"Upload Master Mapping File ({MAP_CHANNEL_SKU_COL} | {MAP_D_SKU_COL} | {MAP_ACCOUNT_COL})",
            type=ALLOWED_FILE_TYPES,
            key="file_uploader_mapping"
        )
        st.session_state.mapping_file_object = mapping_file
        if mapping_file:
            st.success("Mapping file uploaded. Proceed to channel uploads.")
    
    # 2. UPLOADING TABS (The 8 Channels)
    for i, channel_name in enumerate(ALL_CHANNELS):
        with tabs[i + 1]: 
            st.header(f"Upload Pick Lists for **{channel_name}**")
            
            config = CHANNEL_COLUMNS_MAP.get(channel_name)
            st.info(f"Expected SKU Col: `{config['sku']}` | Expected Qty Col: `{config['qty']}`")

            # Determine which account names to use for this channel
            if channel_name in MULTI_ACCOUNT_CHANNELS:
                accounts_to_upload = MASTER_ACCOUNT_NAMES
                cols = st.columns(3)
            else:
                accounts_to_upload = [f"{channel_name} - Main"] 
                cols = [st.container()] 

            # Generate uploaders based on account list
            for j, account_name in enumerate(accounts_to_upload):
                unique_key = f"{channel_name}_{account_name.replace(' ', '_')}"
                
                with cols[j % len(cols)]:
                    uploaded_file = st.file_uploader(
                        f"**{account_name}** Pick List",
                        type=ALLOWED_FILE_TYPES,
                        key=unique_key
                    )
                    
                    # Store the file object in session state keyed by unique_key
                    st.session_state.raw_file_objects[unique_key] = {
                        'file': uploaded_file,
                        'channel': channel_name,
                        'account': account_name
                    }
    
    st.markdown("---")

    # --- SUBMIT BUTTON & PROCESSING LOGIC ---
    
    # Calculate required and uploaded file count
    total_multi_uploads = len(MULTI_ACCOUNT_CHANNELS) * len(MASTER_ACCOUNT_NAMES)
    total_single_uploads = len(SINGLE_ACCOUNT_CHANNELS)
    REQUIRED_FILE_COUNT = total_multi_uploads + total_single_uploads
    
    # Filter out None values to get the count of uploaded pick lists
    uploaded_pick_list_count = sum(1 for item in st.session_state.raw_file_objects.values() if item['file'] is not None)

    st.subheader("3. Consolidate Files and Generate Pick List")
    
    if st.session_state.mapping_file_object is None:
        st.error("Please upload the **Master SKU Mapping File** in the Setup tab (Step 1).")
        return
        
    st.metric(label="Pick List Files Uploaded", value=uploaded_pick_list_count, delta=f"Required: {REQUIRED_FILE_COUNT}")
    
    # Check if all files are ready
    if uploaded_pick_list_count == REQUIRED_FILE_COUNT:
        st.success("All files are ready! Click Submit to generate the master pick list.")
        
        # The submit button triggers the consolidation
        if st.button("🚀 **SUBMIT: Generate Master Pick List**", type="primary", use_container_width=True):
            process_consolidation(st.session_state.raw_file_objects, st.session_state.mapping_file_object)
    
    else:
        st.info("Upload status: Please complete the remaining file uploads in the channel tabs.")

# ==============================================================================
# 4. CONSOLIDATION FUNCTION (Moved outside render function)
# ==============================================================================

def process_consolidation(raw_file_objects, mapping_file_object):
    """Handles the heavy lifting of reading, mapping, and summing the data."""
    with st.spinner("Processing 40+ files... Reading, cleaning, merging, and consolidating data."):
        
        # Read Mapping File
        mapping_df = read_uploaded_file(mapping_file_object, "Mapping File")
        if mapping_df is None: return

        processed_data = []
        
        # 1. Process and Clean all Channel DataFrames
        for key, item in raw_file_objects.items():
            if item['file'] is None: continue # Skip if somehow missed the check
            
            df = read_uploaded_file(item['file'], f"{item['channel']} - {item['account']}")
            if df is not None:
                config = CHANNEL_COLUMNS_MAP[item['channel']]
                
                try:
                    # Rename columns to standard names for merging
                    df_clean = df.rename(columns={
                        config['sku']: MAP_CHANNEL_SKU_COL,
                        config['qty']: 'Total Pick Quantity' 
                    })
                    
                    df_clean = df_clean[[MAP_CHANNEL_SKU_COL, 'Total Pick Quantity']]
                    df_clean['Channel'] = item['channel']
                    df_clean['Account name'] = item['account'] 
                    processed_data.append(df_clean)
                    
                except KeyError as e:
                    st.error(f"Column Mismatch in **{item['channel']} - {item['account']}**: Column {e} not found.")
                    st.warning(f"Verify configuration for {item['channel']}: SKU='{config['sku']}', Qty='{config['qty']}'")
                    return

        # 2. Combine and Map
        combined_picklist_df = pd.concat(processed_data, ignore_index=True)

        merged_df = pd.merge(
            combined_picklist_df,
            mapping_df[[MAP_CHANNEL_SKU_COL, MAP_D_SKU_COL, MAP_ACCOUNT_COL]],
            on=[MAP_CHANNEL_SKU_COL, MAP_ACCOUNT_COL],
            how='left'
        )
        
        # Final Consolidation using the Master D SKU
        merged_df[MAP_D_SKU_COL] = merged_df[MAP_D_SKU_COL].fillna(merged_df[MAP_CHANNEL_SKU_COL])

        final_compiled_picklist = merged_df.groupby(MAP_D_SKU_COL)['Total Pick Quantity'].sum().reset_index()
        final_compiled_picklist.rename(
            columns={'Total Pick Quantity': 'Total Pick Quantity (D SKU)'},
            inplace=True
        )
        final_compiled_picklist = final_compiled_picklist.sort_values(by=MAP_D_SKU_COL)
        
        # 3. Display and Download
        st.subheader("✅ Final Master Pick List by D SKU")
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
        st.balloons() # Success animation!


# ==============================================================================
# 5. GST FILING TOOLS TAB FUNCTION (UNCHANGED)
# ==============================================================================

def render_gst_tab():
    st.title("📊 GST Filing Tools")
    st.markdown("Tools to assist with GSTR-1 and GSTR-3B preparation.")
    st.markdown("---")

    with st.expander("GSTR-1 Preparation (Sales Summary)", expanded=False):
        st.markdown("Use this section to generate your monthly GSTR-1 summary, which details all **outward supplies (sales)**.")
        st.warning("Future Feature: Upload Sales Reports to generate HSN/GST summary.")
        gstr1_file = st.file_uploader("Upload Monthly Sales Register (CSV/Excel)", type=['csv', 'xlsx'], key="gstr1_uploader")
        if gstr1_file: st.info(f"File '{gstr1_file.name}' uploaded for GSTR-1 analysis.")

    st.markdown("---")

    with st.expander("GSTR-3B Reconciliation (Summary & ITC)", expanded=False):
        st.markdown("Use this section for reconciling your Input Tax Credit (ITC) and summary tax liability.")
        st.warning("Future Feature: Upload GSTR-2A/2B for ITC reconciliation against your Purchase Register.")
        gstr3b_sales_file = st.file_uploader("Upload GSTR-1 Summary Data (for comparison)", type=['csv', 'xlsx'], key="gstr3b_sales_uploader")
        gstr3b_purchase_file = st.file_uploader("Upload Purchase/Expense Register (for ITC calculation)", type=['csv', 'xlsx'], key="gstr3b_purchase_uploader")
        if gstr3b_sales_file and gstr3b_purchase_file: st.info("Sales and Purchase files uploaded for GSTR-3B reconciliation.")

# ==============================================================================
# MAIN APP EXECUTION
# ==============================================================================

def main():
    st.set_page_config(page_title="Multi-Channel Operations Dashboard", layout="wide")

    # Sidebar Navigation
    st.sidebar.title("App Navigation")
    selected_tab = st.sidebar.radio(
        "Go to:",
        ["📦 Pick List Compiler", "📊 GST Filing Tools"]
    )
    st.sidebar.markdown("---")
    st.sidebar.info("Developed for streamlined supplier operations.")

    # Render the selected tab
    if selected_tab == "📦 Pick List Compiler":
        render_picklist_tab()
    elif selected_tab == "📊 GST Filing Tools":
        render_gst_tab()

if __name__ == "__main__":
    main()
