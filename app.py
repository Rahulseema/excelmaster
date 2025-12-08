import streamlit as st
import pandas as pd
from io import BytesIO

# ==============================================================================
# 1. CONFIGURATION SECTION 
# ==============================================================================

# Your 10 Master Account Names (Must match account name used in Mapping File)
MASTER_ACCOUNT_NAMES = [
    "Drench", "Drench India", "Shine ArC", "Sparsh", "Sparsh SC",
    "BnB industries", "Shopforher", "Ansh Ent.", "AV Enterprises", "UV Enterprises"
]

# The single, consolidated channel
THE_ONLY_CHANNEL = "Listing Compiler"

# Mapping file column names:
MAP_CHANNEL_SKU_COL = 'Channel SKU'
MAP_CHANNEL_SIZE_COL = 'Channel Size'
MAP_CHANNEL_COLOR_COL = 'Channel Color'
MAP_OUR_SKU_COL = 'Our SKU'
MAP_ACCOUNT_COL = 'Account name'

# Pick List file column names (What the consolidation logic looks for):
PICKLIST_SKU_COL = 'SKU'
PICKLIST_SIZE_COL = 'Size'
PICKLIST_COLOR_COL = 'Color'
PICKLIST_QTY_COL = 'Qty'


# Configuration for Pick List Column Names for the Listing Compiler
# NOTE: All 10 accounts must use these exact column headers in their reports.
CHANNEL_COLUMNS_MAP = {
    THE_ONLY_CHANNEL: {'sku': 'SKU', 'size': 'Size', 'color': 'Color', 'qty': 'Qty'}, 
}

ALLOWED_FILE_TYPES = ['csv', 'xlsx']

# ==============================================================================
# 2. HELPER FUNCTIONS
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
# 3. PICK LIST COMPILER TAB FUNCTION
# ==============================================================================

def render_picklist_tab():
    st.title("📦 Master Pick List Compiler")
    st.markdown("Upload **Mapping File (Required)** and **at least one** Pick List file to consolidate.")
    st.markdown("---")

    # Session state for managing all uploaded file objects and mapping file
    if 'raw_file_objects' not in st.session_state:
        st.session_state.raw_file_objects = {}
    if 'mapping_file_object' not in st.session_state:
        st.session_state.mapping_file_object = None

    # --- SETUP & UPLOADING TABS ---
    
    tab_titles = ["1. Setup & Mapping", "2. Listing Compiler Upload"]
    tabs = st.tabs(tab_titles)
    
    # 1. SETUP TAB (MAPPING FILE)
    with tabs[0]:
        st.header("1. Master SKU Mapping File Setup (REQUIRED)")
        st.markdown("This file requires **Channel SKU, Size, and Color** to map to your **Our SKU**.")
        
        mapping_file = st.file_uploader(
            f"Upload Master Mapping File (CSV/Excel)",
            type=ALLOWED_FILE_TYPES,
            key="file_uploader_mapping"
        )
        st.session_state.mapping_file_object = mapping_file
        
        st.markdown("---")
        
        # Sample Download Option for Mapping File
        st.subheader("Download Sample Mapping Template")
        st.download_button(
            label="Download Sample Mapping File (Excel)",
            data=get_sample_mapping_file(),
            file_name='sample_sku_mapping_template.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        if mapping_file:
            st.success("Mapping file uploaded. Proceed to upload pick lists.")
    
    # 2. UPLOADING TAB (The Single Channel)
    with tabs[1]: 
        st.header(f"Upload Pick Lists for **{THE_ONLY_CHANNEL}**")
        
        config = CHANNEL_COLUMNS_MAP[THE_ONLY_CHANNEL]
        st.info(f"All 10 accounts must use these column headers: **SKU**: `{config['sku']}`, **Size**: `{config['size']}`, **Color**: `{config['color']}`, **Qty**: `{config['qty']}`.")

        # Sample Download Option for Pick List
        st.subheader("Download Sample Pick List Template")
        st.download_button(
            label=f"Download {THE_ONLY_CHANNEL} Sample Template (Excel)",
            data=get_sample_picklist_file(),
            file_name=f'sample_{THE_ONLY_CHANNEL.lower().replace(" ", "_")}_picklist.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        st.markdown("---")

        accounts_to_upload = MASTER_ACCOUNT_NAMES
        cols = st.columns(3) # Display 3 uploaders per row

        for j, account_name in enumerate(accounts_to_upload):
            unique_key = f"{THE_ONLY_CHANNEL}_{account_name.replace(' ', '_')}"
            
            with cols[j % 3]: # Use modulo 3 for cycling through the 3 columns
                uploaded_file = st.file_uploader(
                    f"**{account_name}** Pick List",
                    type=ALLOWED_FILE_TYPES,
                    key=unique_key
                )
                
                # Store the file object with account name
                st.session_state.raw_file_objects[unique_key] = {
                    'file': uploaded_file,
                    'channel': THE_ONLY_CHANNEL,
                    'account': account_name
                }
    
    st.markdown("---")

    # --- SUBMIT BUTTON & PROCESSING LOGIC TRIGGER ---
    
    TOTAL_POTENTIAL_UPLOADS = len(MASTER_ACCOUNT_NAMES) # 10 accounts total
    
    uploaded_pick_list_count = sum(1 for item in st.session_state.raw_file_objects.values() if item['file'] is not None)

    st.subheader("3. Consolidate Files and Generate Pick List")
    
    if st.session_state.mapping_file_object is None:
        st.error("🔴 **Mapping File Required:** Please upload the Master SKU Mapping File in the Setup tab (Step 1).")
        return
        
    st.metric(label="Pick List Files Uploaded", value=uploaded_pick_list_count, delta=f"Total Slots: {TOTAL_POTENTIAL_UPLOADS}")
    
    if uploaded_pick_list_count >= 1:
        st.success("All requirements met! Click Submit to generate the master pick list.")
        
        if st.button("🚀 **SUBMIT: Generate Master Pick List**", type="primary", use_container_width=True):
            process_consolidation(st.session_state.raw_file_objects, st.session_state.mapping_file_object, uploaded_pick_list_count)
    
    else:
        st.info("🟡 **Pick List Required:** Please upload at least one pick list file in the Listing Compiler Upload tab.")


# ==============================================================================
# 4. GST FILING TOOLS TAB FUNCTION (UNCHANGED)
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
# 5. MAIN APP EXECUTION
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
