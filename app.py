import streamlit as st
import pandas as pd
from io import BytesIO

# --- Configuration ---
ACCOUNT_NAMES = [
    "Drench", "Drench India", "Sparsh", "Sparsh SC", "Shine Arc",
    "Ansh ent", "BnB Industries", "Shopforher", "AV Enterprises"
]
ALLOWED_FILE_TYPES = ['csv', 'xlsx']

# --- CRITICAL COLUMN NAMES (ADJUST AS NEEDED) ---
# **YOU MUST CONFIRM THESE:**
PICKLIST_SKU_COL = 'SKU ID'      # Column in the 9 Meesho Pick Lists that identifies the product
PICKLIST_QTY_COL = 'Quantity'    # Column in the 9 Meesho Pick Lists that holds the quantity

# Mapping file column names (as provided by user):
MAP_CHANNEL_SKU_COL = 'Channel SKU'
MAP_D_SKU_COL = 'D SKU'
MAP_ACCOUNT_COL = 'Account name'

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
        st.warning("Ensure the file is not corrupted and is a valid CSV/Excel format.")
        return None

# ==============================================================================
# 1. PICK LIST COMPILER TAB FUNCTION
# ==============================================================================

def render_picklist_tab():
    st.title("📦 Meesho Master Pick List Compiler")
    st.markdown("Automate compilation and map to your master D SKU across 9 accounts.")
    st.markdown("---")

    # --- UPLOAD SECTION ---
    st.subheader("1️⃣ Upload Files (9 Pick Lists + 1 Mapping File)")

    # 1. UPLOAD 9 PICK LISTS
    with st.expander("Upload 9 Individual Account Pick Lists", expanded=True):
        pick_list_files_map = {}
        all_pick_lists_uploaded = True
        col1, col2, col3 = st.columns(3)
        columns = [col1, col2, col3]

        for i, account_name in enumerate(ACCOUNT_NAMES):
            with columns[i % 3]:
                file = st.file_uploader(
                    f"**{i+1}. {account_name}** Pick List",
                    type=ALLOWED_FILE_TYPES,
                    key=f"file_uploader_picklist_{i}"
                )
                pick_list_files_map[account_name] = file
                if file is None:
                    all_pick_lists_uploaded = False

    # 2. UPLOAD 1 MAPPING FILE
    st.markdown("---")
    mapping_file = st.file_uploader(
        f"**10. Master SKU Mapping File** ({MAP_CHANNEL_SKU_COL} | {MAP_D_SKU_COL} | {MAP_ACCOUNT_COL})",
        type=ALLOWED_FILE_TYPES,
        key="file_uploader_mapping"
    )
    is_mapping_file_uploaded = (mapping_file is not None)

    st.markdown("---")

    # --- PROCESSING LOGIC (Rest of your pick list code) ---
    if all_pick_lists_uploaded and is_mapping_file_uploaded:
        st.subheader("2️⃣ Processing and Compilation")
        st.success("All 10 files uploaded! Compiling data and applying mapping...")
        
        dataframes = []
        
        # Read all 9 Pick Lists
        for account_name, file in pick_list_files_map.items():
            df = read_uploaded_file(file)
            if df is not None:
                df['Meesho_Account'] = account_name
                try:
                    df.rename(columns={PICKLIST_SKU_COL: MAP_CHANNEL_SKU_COL}, inplace=True)
                    dataframes.append(df)
                except KeyError:
                    st.error(f"Column '{PICKLIST_SKU_COL}' not found in the file for {account_name}. Please check the file header.")
                    return

        # Read Mapping File
        mapping_df = read_uploaded_file(mapping_file)
        
        if dataframes and mapping_df is not None:
            combined_picklist_df = pd.concat(dataframes, ignore_index=True)

            try:
                # Merge Pick List with Mapping Table
                merged_df = pd.merge(
                    combined_picklist_df,
                    mapping_df[[MAP_CHANNEL_SKU_COL, MAP_D_SKU_COL, MAP_ACCOUNT_COL]],
                    left_on=[MAP_CHANNEL_SKU_COL, 'Meesho_Account'],
                    right_on=[MAP_CHANNEL_SKU_COL, MAP_ACCOUNT_COL],
                    how='left'
                )
                
                # Handle unmapped SKUs
                unmapped_count = merged_df[MAP_D_SKU_COL].isna().sum()
                if unmapped_count > 0:
                    merged_df[MAP_D_SKU_COL] = merged_df[MAP_D_SKU_COL].fillna(merged_df[MAP_CHANNEL_SKU_COL])

                # Final Consolidation using the Master D SKU
                final_compiled_picklist = merged_df.groupby(MAP_D_SKU_COL)[PICKLIST_QTY_COL].sum().reset_index()
                final_compiled_picklist.rename(
                    columns={PICKLIST_QTY_COL: 'Total Pick Quantity (D SKU)'},
                    inplace=True
                )
                final_compiled_picklist = final_compiled_picklist.sort_values(by=MAP_D_SKU_COL)

                # Display and Download
                st.subheader("3️⃣ Final Master Pick List by D SKU")
                st.dataframe(final_compiled_picklist, use_container_width=True)

                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    final_compiled_picklist.to_excel(writer, index=False, sheet_name='Master_Picklist_D_SKU')
                
                st.download_button(
                    label="⬇️ Download Master Pick List (Excel)",
                    data=output.getvalue(),
                    file_name='compiled_meesho_picklist_master.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            
            except KeyError as e:
                st.error(f"❌ Critical Error in Processing: Column not found. Missing column: **{e}**.")
                st.info("Please verify the column names defined at the top of the `app.py` script.")

    else:
        st.warning("Please upload all 10 required files to generate the compiled list.")

# ==============================================================================
# 2. GST FILING TOOLS TAB FUNCTION
# ==============================================================================

def render_gst_tab():
    st.title("📊 GST Filing Tools")
    st.markdown("Tools to assist with GSTR-1 and GSTR-3B preparation.")
    st.markdown("---")

    # GSTR-1 Collapsible Section
    with st.expander("GSTR-1 Preparation (Sales Summary)", expanded=False):
        st.markdown(
            """
            Use this section to generate your monthly GSTR-1 summary, which details all **outward supplies (sales)**.
            """
        )
        st.warning("Future Feature: Upload Meesho Sales Report to generate HSN/GST summary.")
        
        # Upload tool placeholder for GSTR-1
        gstr1_file = st.file_uploader(
            "Upload Monthly Sales Register (CSV/Excel)",
            type=['csv', 'xlsx'],
            key="gstr1_uploader"
        )
        
        if gstr1_file:
            st.success(f"File '{gstr1_file.name}' uploaded for GSTR-1 analysis.")
            # Future code here: read file, aggregate by GST rates, generate downloadable JSON/CSV format.

    st.markdown("---")

    # GSTR-3B Collapsible Section
    with st.expander("GSTR-3B Reconciliation (Summary & ITC)", expanded=False):
        st.markdown(
            """
            Use this section for reconciling your Input Tax Credit (ITC) and summary tax liability.
            GSTR-3B is a summary return for the month.
            """
        )
        st.warning("Future Feature: Upload GSTR-2A/2B for ITC reconciliation against your Purchase Register.")

        # Upload tool placeholder for GSTR-3B
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
            st.success("Sales and Purchase files uploaded for GSTR-3B reconciliation.")
            # Future code here: Calculate net tax liability and suggest reconciliation points.

# ==============================================================================
# MAIN APP EXECUTION
# ==============================================================================

def main():
    st.set_page_config(page_title="Meesho Operations Dashboard", layout="wide")

    # Sidebar Navigation
    st.sidebar.title("App Navigation")
    selected_tab = st.sidebar.radio(
        "Go to:",
        ["📦 Pick List Compiler", "📊 GST Filing Tools"]
    )
    st.sidebar.markdown("---")
    st.sidebar.info("Developed for quick supplier operations.")

    # Render the selected tab
    if selected_tab == "📦 Pick List Compiler":
        render_picklist_tab()
    elif selected_tab == "📊 GST Filing Tools":
        render_gst_tab()

if __name__ == "__main__":
    main()
