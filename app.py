import streamlit as st
import pandas as pd
from io import BytesIO

# ==============================================================================
# 1. CONFIGURATION SECTION (CRITICAL: ADJUST COLUMN NAMES HERE!)
# ==============================================================================

# Your 9 distinct Marketplace Channels
ALL_MARKETPLACE_CHANNELS = [
    "Meesho",
    "Amazon",
    "Flipkart",
    "Myntra",
    "Nykaa",
    "Channel 6 (Placeholder)",
    "Channel 7 (Placeholder)",
    "Channel 8 (Placeholder)",
    "Channel 9 (Placeholder)",
]

# Configuration for Pick List Column Names by Channel
# !!! WARNING: VERIFY THESE COLUMN NAMES AGAINST YOUR ACTUAL REPORTS !!!
# If a channel is not working, check the 'sku' and 'qty' values below.
CHANNEL_COLUMNS_MAP = {
    "Meesho": {'sku': 'SKU ID', 'qty': 'Quantity'},
    "Amazon": {'sku': 'sku', 'qty': 'quantity-purchased'}, 
    "Flipkart": {'sku': 'Seller SKU ID', 'qty': 'quantity-purchased'},
    "Myntra": {'sku': 'Seller SKU', 'qty': 'Quantity'},
    "Nykaa": {'sku': 'Seller Code', 'qty': 'Inventory Qty'}, 
    "Channel 6 (Placeholder)": {'sku': 'Item SKU', 'qty': 'Order Qty'},
    "Channel 7 (Placeholder)": {'sku': 'Item SKU', 'qty': 'Order Qty'},
    "Channel 8 (Placeholder)": {'sku': 'Item SKU', 'qty': 'Order Qty'},
    "Channel 9 (Placeholder)": {'sku': 'Item SKU', 'qty': 'Order Qty'},
}

# Mapping file column names (as provided by user):
MAP_CHANNEL_SKU_COL = 'Channel SKU'
MAP_D_SKU_COL = 'D SKU'
MAP_ACCOUNT_COL = 'Account name'

ALLOWED_FILE_TYPES = ['csv', 'xlsx']

# --- Helper Function to Read File ---
def read_uploaded_file(uploaded_file, channel_name):
    """Reads a file object into a Pandas DataFrame."""
    try:
        # Pass the file object directly to Pandas functions
        if uploaded_file.name.lower().endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.lower().endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            st.error(f"Unsupported file type for {channel_name}.")
            return None
        
        # Add metadata before returning
        df['Channel'] = channel_name
        return df
        
    except Exception as e:
        st.error(f"Error reading file for **{channel_name}**: {type(e).__name__} - {e}")
        return None

# ==============================================================================
# 2. PICK LIST COMPILER TAB FUNCTION
# ==============================================================================

def render_picklist_tab():
    st.title("📦 Multi-Channel Master Pick List Compiler")
    st.markdown("Upload reports for your 9 channels and consolidate into a single pick list using your **D SKU**.")
    st.markdown("---")

    # The first tab is for Consolidation/Mapping, the rest are for uploading.
    tab_titles = ["Consolidate & Map"] + ALL_MARKETPLACE_CHANNELS
    
    # st.tabs creates the horizontal tabs interface
    tabs = st.tabs(tab_titles)
    
    # Dictionary to store all uploaded DataFrames
    all_raw_dataframes = {}

    # --- UPLOADING TABS ---
    for i, channel_name in enumerate(ALL_MARKETPLACE_CHANNELS):
        with tabs[i + 1]: # Start from the second tab (index 1)
            st.subheader(f"Upload Pick List for **{channel_name}**")
            
            # Show the expected columns for clarity
            config = CHANNEL_COLUMNS_MAP.get(channel_name, {'sku': 'N/A', 'qty': 'N/A'})
            st.info(f"Expected SKU Column: `{config['sku']}` | Expected Quantity Column: `{config['qty']}`")
            
            uploaded_file = st.file_uploader(
                f"Upload {channel_name} Pick List (CSV/Excel)",
                type=ALLOWED_FILE_TYPES,
                key=f"file_uploader_{channel_name.replace(' ', '_')}"
            )

            if uploaded_file:
                df = read_uploaded_file(uploaded_file, channel_name)
                if df is not None:
                    all_raw_dataframes[channel_name] = df
                    st.success(f"File for {channel_name} uploaded successfully!")
                    
    # --- CONSOLIDATE & MAP TAB (The Main Processing Logic) ---
    with tabs[0]:
        st.subheader("1️⃣ Master SKU Mapping File")
        mapping_file = st.file_uploader(
            f"Upload Master Mapping File ({MAP_CHANNEL_SKU_COL} | {MAP_D_SKU_COL} | {MAP_ACCOUNT_COL})",
            type=ALLOWED_FILE_TYPES,
            key="file_uploader_mapping"
        )
        st.markdown("---")
        
        # Check if all files needed are present
        uploaded_channel_count = len(all_raw_dataframes)
        required_channel_count = len(ALL_MARKETPLACE_CHANNELS)

        if uploaded_channel_count == required_channel_count and mapping_file:
            st.success(f"All {required_channel_count} channel files and mapping file uploaded. Starting compilation...")
            
            # Read Mapping File
            mapping_df = read_uploaded_file(mapping_file, "Mapping File")
            if mapping_df is None:
                 st.error("Failed to read mapping file.")
                 return

            processed_data = []
            
            # 1. Process and Clean all Channel DataFrames
            for channel_name, df in all_raw_dataframes.items():
                config = CHANNEL_COLUMNS_MAP[channel_name]
                
                try:
                    # Rename columns to standard names for merging
                    df_clean = df.rename(columns={
                        config['sku']: MAP_CHANNEL_SKU_COL,
                        config['qty']: 'Total Pick Quantity' 
                    })
                    
                    # Keep only essential columns plus the Channel metadata
                    df_clean = df_clean[[MAP_CHANNEL_SKU_COL, 'Total Pick Quantity', 'Channel']]
                    processed_data.append(df_clean)
                    
                except KeyError as e:
                    st.error(f"Column Mismatch in **{channel_name}**: Column {e} not found.")
                    st.warning("Please correct the configuration in the `app.py` script and re-upload.")
                    return # Stop processing on error

            # 2. Combine and Map
            combined_picklist_df = pd.concat(processed_data, ignore_index=True)

            # NOTE: We assume the 'Account name' in the mapping file corresponds to the 'Channel name'
            # since we are uploading one aggregated pick list per channel.
            merged_df = pd.merge(
                combined_picklist_df,
                mapping_df[[MAP_CHANNEL_SKU_COL, MAP_D_SKU_COL, MAP_ACCOUNT_COL]],
                left_on=[MAP_CHANNEL_SKU_COL, 'Channel'],
                right_on=[MAP_CHANNEL_SKU_COL, MAP_ACCOUNT_COL],
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
            # Display status summary for pending uploads
            missing_files = [c for c in ALL_MARKETPLACE_CHANNELS if c not in all_raw_dataframes]
            if mapping_file is None:
                 st.warning("Mapping file is missing.")
            if missing_files:
                st.warning(f"Please upload pick lists for the following channels: **{', '.join(missing_files)}**")
                
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
