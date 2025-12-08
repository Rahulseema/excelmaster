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
    st.markdown("Upload reports for **44 accounts/channels** and consolidate using your **D SKU**.")
    st.markdown("---")

    # Tabs for each channel plus a consolidation tab
    tab_titles = ["Consolidate & Map"] + ALL_CHANNELS
    tabs = st.tabs(tab_titles)
    
    # Session state to manage uploaded DataFrames across tabs
    if 'raw_dataframes' not in st.session_state:
        st.session_state.raw_dataframes = {}

    # --- UPLOADING TABS (The 8 Channels) ---
    for i, channel_name in enumerate(ALL_CHANNELS):
        with tabs[i + 1]: # Start from the second tab (index 1)
            st.header(f"Upload Pick Lists for **{channel_name}**")
            
            config = CHANNEL_COLUMNS_MAP.get(channel_name)
            st.info(f"Expected SKU Col: `{config['sku']}` | Expected Qty Col: `{config['qty']}`")

            # Determine which account names to use for this channel
            if channel_name in MULTI_ACCOUNT_CHANNELS:
                accounts_to_upload = MASTER_ACCOUNT_NAMES
                cols = st.columns(3) # Use columns for space efficiency
            else:
                # Use a single, generic account name for single-account channels
                accounts_to_upload = [f"{channel_name} - Main"] 
                cols = [st.container()] # Use a single container for full width

            # Generate uploaders based on account list
            for j, account_name in enumerate(accounts_to_upload):
                unique_key = f"{channel_name}_{account_name.replace(' ', '_')}"
                
                with cols[j % len(cols)]:
                    uploaded_file = st.file_uploader(
                        f"**{account_name}** Pick List",
                        type=ALLOWED_FILE_TYPES,
                        key=unique_key
                    )

                    if uploaded_file:
                        # Store the file object in session state keyed by (channel, account)
                        st.session_state.raw_dataframes[unique_key] = {
                            'file': uploaded_file,
                            'channel': channel_name,
                            'account': account_name
                        }
                        
    # --- CONSOLIDATE & MAP TAB (The Main Processing Logic) ---
    with tabs[0]:
        st.subheader("1️⃣ Master SKU Mapping File Upload")
        mapping_file = st.file_uploader(
            f"Upload Master Mapping File ({MAP_CHANNEL_SKU_COL} | {MAP_D_SKU_COL} | {MAP_ACCOUNT_COL})",
            type=ALLOWED_FILE_TYPES,
            key="file_uploader_mapping"
        )
        st.markdown("---")

        # Define expected total uploads
        total_multi_uploads = len(MULTI_ACCOUNT_CHANNELS) * len(MASTER_ACCOUNT_NAMES)
        total_single_uploads = len(SINGLE_ACCOUNT_CHANNELS)
        REQUIRED_FILE_COUNT = total_multi_uploads + total_single_uploads

        uploaded_count = len(st.session_state.raw_dataframes)
        
        st.subheader("2️⃣ Consolidation Status")
        st.metric(label="Files Uploaded (Pick Lists)", value=uploaded_count, delta=f"Required: {REQUIRED_FILE_COUNT}")
        
        if uploaded_count == REQUIRED_FILE_COUNT and mapping_file:
            st.success("All required pick lists and mapping file are uploaded. Starting compilation...")
            
            # Read Mapping File
            mapping_df = read_uploaded_file(mapping_file, "Mapping File")
            if mapping_df is None: return

            processed_data = []
            
            # 1. Process and Clean all Channel DataFrames
            for key, item in st.session_state.raw_dataframes.items():
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
                        df_clean['Account name'] = item['account'] # Use the exact mapping column header
                        processed_data.append(df_clean)
                        
                    except KeyError as e:
                        st.error(f"Column Mismatch in **{item['channel']} - {item['account']}**: Column {e} not found.")
                        st.warning(f"Verify configuration for {item['channel']}: SKU='{config['sku']}', Qty='{config['qty']}'")
                        return

            # 2. Combine and Map
            combined_picklist_df = pd.concat(processed_data, ignore_index=True)

            # Merge Pick List with Mapping Table (using Channel SKU and Account Name)
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

        else:
            st.info("Upload status: Please check all channel tabs to upload the remaining files.")


# ==============================================================================
# 3. GST FILING TOOLS TAB FUNCTION (UNCHANGED)
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
