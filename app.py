import streamlit as st
import pandas as pd
from io import BytesIO

# ==============================================================================
# 1. CONFIGURATION SECTION (CRITICAL: ADJUST COLUMN NAMES HERE!)
# ==============================================================================

# Your 9 Meesho Account Names (for clarity)
MEESHO_ACCOUNT_NAMES = [
    "Drench", "Drench India", "Sparsh", "Sparsh SC", "Shine Arc",
    "Ansh ent", "BnB Industries", "Shopforher", "AV Enterprises"
]

# Master list of all Channels
ALL_CHANNELS = ["Meesho", "Amazon", "Flipkart", "Myntra", "Nykaa"]

# Configuration for Pick List Column Names by Channel
# !!! WARNING: VERIFY THESE COLUMN NAMES AGAINST YOUR ACTUAL REPORTS !!!
CHANNEL_COLUMNS_MAP = {
    "Meesho": {'sku': 'SKU ID', 'qty': 'Quantity'}, # Common Meesho Names
    "Amazon": {'sku': 'sku', 'qty': 'quantity-purchased'}, # Common Amazon Names
    "Flipkart": {'sku': 'Seller SKU ID', 'qty': 'quantity-purchased'}, # Common Flipkart Names
    "Myntra": {'sku': 'Seller SKU', 'qty': 'Quantity'}, # ASSUMED: Needs Verification
    "Nykaa": {'sku': 'Seller SKU', 'qty': 'Quantity'}, # ASSUMED: Needs Verification
}

# Mapping file column names (as provided by user):
MAP_CHANNEL_SKU_COL = 'Channel SKU'
MAP_D_SKU_COL = 'D SKU'
MAP_ACCOUNT_COL = 'Account name'

ALLOWED_FILE_TYPES = ['csv', 'xlsx']

# --- Helper Function to Read File ---
def read_uploaded_file(uploaded_file):
    """Reads a file object into a Pandas DataFrame."""
    try:
        if uploaded_file.name.lower().endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.lower().endswith('.xlsx'):
            return pd.read_excel(uploaded_file, engine='openpyxl')
        return None
    except Exception as e:
        st.error(f"Error reading file **{uploaded_file.name}**: {type(e).__name__} - {e}")
        return None

# ==============================================================================
# 2. PICK LIST COMPILER TAB FUNCTION
# ==============================================================================

def render_picklist_tab():
    st.title("📦 Multi-Channel Master Pick List Compiler")
    st.markdown("Combines pick lists from all your channels and maps them to your master D SKU.")
    st.markdown("---")

    uploaded_data = []

    # 1. UPLOAD MAPPING FILE
    st.subheader("1️⃣ Master SKU Mapping File")
    mapping_file = st.file_uploader(
        f"Upload Master Mapping File ({MAP_CHANNEL_SKU_COL} | {MAP_D_SKU_COL} | {MAP_ACCOUNT_COL})",
        type=ALLOWED_FILE_TYPES,
        key="file_uploader_mapping"
    )
    is_mapping_file_uploaded = (mapping_file is not None)
    st.markdown("---")


    # 2. UPLOAD MULTI-CHANNEL PICK LISTS
    st.subheader("2️⃣ Upload Channel Pick Lists")

    # Use a dynamic list for all uploads
    all_uploads = []
    
    # Add 9 Meesho Accounts
    for name in MEESHO_ACCOUNT_NAMES:
        all_uploads.append({"channel": "Meesho", "account": name})

    # Add other channels (assuming one account per other channel for now)
    for channel in ALL_CHANNELS:
        if channel != "Meesho":
            # Creates an entry like "Amazon - Main Account"
            all_uploads.append({"channel": channel, "account": f"{channel} - Main Account"})


    # Create uploaders dynamically
    cols = st.columns(3)
    uploaded_files_map = {}
    all_pick_lists_uploaded = True

    with st.expander("Upload All Pick List Reports (Total 13 Uploads)", expanded=True):
        for i, item in enumerate(all_uploads):
            channel = item["channel"]
            account_name = item["account"]
            
            with cols[i % 3]: # Distribute across 3 columns
                file = st.file_uploader(
                    f"**{i+1}. {account_name}** ({channel})",
                    type=ALLOWED_FILE_TYPES,
                    key=f"file_uploader_picklist_{i}"
                )
                uploaded_files_map[account_name] = {'file': file, 'channel': channel}
                if file is None:
                    all_pick_lists_uploaded = False

    st.markdown("---")

    # --- PROCESSING LOGIC ---
    if all_pick_lists_uploaded and is_mapping_file_uploaded:
        st.subheader("3️⃣ Processing and Compilation")
        st.success("All files uploaded! Compiling data and applying mapping...")
        
        # Read Mapping File FIRST
        mapping_df = read_uploaded_file(mapping_file)
        if mapping_df is None:
             st.error("Failed to read mapping file.")
             return

        # 1. Process all Pick Lists
        for account_name, upload_info in uploaded_files_map.items():
            file = upload_info['file']
            channel = upload_info['channel']
            
            df = read_uploaded_file(file)
            if df is not None:
                config = CHANNEL_COLUMNS_MAP[channel]
                
                try:
                    # Rename and select necessary columns, add metadata
                    df_clean = df.rename(columns={
                        config['sku']: MAP_CHANNEL_SKU_COL,
                        config['qty']: 'Total Pick Quantity' # Use a temporary standard name
                    })
                    
                    df_clean = df_clean[[MAP_CHANNEL_SKU_COL, 'Total Pick Quantity']]
                    df_clean['Channel'] = channel
                    df_clean['Account'] = account_name
                    uploaded_data.append(df_clean)
                    
                except KeyError as e:
                    st.error(f"Column Error in **{account_name}** ({channel}): Column {e} not found.")
                    st.warning(f"Please check the configuration for '{channel}' in the script or verify your report headers.")
                    return # Stop processing on first error

        # 2. Final Consolidation
        if uploaded_data:
            combined_picklist_df = pd.concat(uploaded_data, ignore_index=True)

            # --- Mapping Logic ---
            merged_df = pd.merge(
                combined_picklist_df,
                mapping_df[[MAP_CHANNEL_SKU_COL, MAP_D_SKU_COL, MAP_ACCOUNT_COL]],
                left_on=[MAP_CHANNEL_SKU_COL, 'Account'],
                right_on=[MAP_CHANNEL_SKU_COL, MAP_ACCOUNT_COL],
                how='left'
            )
            
            # Handle unmapped SKUs
            merged_df[MAP_D_SKU_COL] = merged_df[MAP_D_SKU_COL].fillna(merged_df[MAP_CHANNEL_SKU_COL])

            # Final Consolidation using the Master D SKU
            final_compiled_picklist = merged_df.groupby(MAP_D_SKU_COL)['Total Pick Quantity'].sum().reset_index()
            final_compiled_picklist.rename(
                columns={'Total Pick Quantity': 'Total Pick Quantity (D SKU)'},
                inplace=True
            )
            final_compiled_picklist = final_compiled_picklist.sort_values(by=MAP_D_SKU_COL)

            # 3. Display and Download
            st.subheader("4️⃣ Final Master Pick List by D SKU")
            st.dataframe(final_compiled_picklist, use_container_width=True)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_compiled_picklist.to_excel(writer, index=False, sheet_name='Master_Picklist_D_SKU')
            
            st.download_button(
                label="⬇️ Download Master Pick List (Excel)",
                data=output.getvalue(),
                file_name='compiled_multi_channel_picklist.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
    else:
        st.warning("Please upload all required files to generate the compiled list.")

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
        gstr1_file = st.file_uploader(
            "Upload Monthly Sales Register (CSV/Excel)",
            type=['csv', 'xlsx'],
            key="gstr1_uploader"
        )
        if gstr1_file:
            st.info(f"File '{gstr1_file.name}' uploaded for GSTR-1 analysis.")

    st.markdown("---")

    with st.expander("GSTR-3B Reconciliation (Summary & ITC)", expanded=False):
        st.markdown("Use this section for reconciling your Input Tax Credit (ITC) and summary tax liability.")
        st.warning("Future Feature: Upload GSTR-2A/2B for ITC reconciliation against your Purchase Register.")
        gstr3b_sales_file = st.file_uploader(
            "Upload GSTR-1 Summary Data (for comparison)",
            type=['csv', 'xlsx'],
            key="gstr3b_sales_uploader"
        )
        gstr3b_purchase_file = st.file_uploader(
            "Upload Purchase/Expense Register (for ITC calculation)",
            type=['csv', 'xlsx'],
            key="gstr3b_purchase_uploader"
        )
        if gstr3b_sales_file and gstr3b_purchase_file:
            st.info("Sales and Purchase files uploaded for GSTR-3B reconciliation.")

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
