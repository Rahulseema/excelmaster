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
# Based on common Meesho report names:
PICKLIST_SKU_COL = 'SKU ID'      # Column in the 9 Meesho Pick Lists that identifies the product
PICKLIST_QTY_COL = 'Quantity'    # Column in the 9 Meesho Pick Lists that holds the quantity

# Mapping file column names (as provided by user):
MAP_CHANNEL_SKU_COL = 'Channel SKU' # Meesho's SKU in the mapping file
MAP_D_SKU_COL = 'D SKU'             # Your Master SKU in the mapping file
MAP_ACCOUNT_COL = 'Account name'    # Account name in the mapping file

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

# --- Main Streamlit App ---
st.set_page_config(page_title="Meesho Master Pick List Compiler", layout="wide")
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
    f"**10. Master SKU Mapping File** (Channels SKU | D SKU | Account Name)",
    type=ALLOWED_FILE_TYPES,
    key="file_uploader_mapping"
)
is_mapping_file_uploaded = (mapping_file is not None)

st.markdown("---")

# --- PROCESSING LOGIC ---
if all_pick_lists_uploaded and is_mapping_file_uploaded:
    st.subheader("2️⃣ Processing and Compilation")
    st.success("All 10 files uploaded! Compiling data and applying mapping...")
    
    dataframes = []
    
    # 1. Read all 9 Pick Lists
    for account_name, file in pick_list_files_map.items():
        df = read_uploaded_file(file)
        if df is not None:
            # Add an 'Account' column to link with the mapping file
            df['Meesho_Account'] = account_name
            # Rename the SKU column for merging clarity
            df.rename(columns={PICKLIST_SKU_COL: MAP_CHANNEL_SKU_COL}, inplace=True)
            dataframes.append(df)

    # 2. Read Mapping File
    mapping_df = read_uploaded_file(mapping_file)
    
    if dataframes and mapping_df is not None:
        # 3. Combine 9 Pick Lists
        combined_picklist_df = pd.concat(dataframes, ignore_index=True)

        # 4. Merge Pick List with Mapping Table
        # Merge on both Channel SKU and Account Name to ensure the right map is used
        try:
            merged_df = pd.merge(
                combined_picklist_df,
                mapping_df[[MAP_CHANNEL_SKU_COL, MAP_D_SKU_COL, MAP_ACCOUNT_COL]],
                left_on=[MAP_CHANNEL_SKU_COL, 'Meesho_Account'],
                right_on=[MAP_CHANNEL_SKU_COL, MAP_ACCOUNT_COL],
                how='left'
            )
            
            # 5. Handle unmapped SKUs (Optional but recommended)
            unmapped_count = merged_df[MAP_D_SKU_COL].isna().sum()
            if unmapped_count > 0:
                st.warning(f"⚠️ **{unmapped_count}** items found without a **{MAP_D_SKU_COL}**. These will be grouped by their **{MAP_CHANNEL_SKU_COL}**.")
                # For unmapped items, use the Channel SKU as the D SKU for grouping
                merged_df[MAP_D_SKU_COL] = merged_df[MAP_D_SKU_COL].fillna(merged_df[MAP_CHANNEL_SKU_COL])

            # 6. Final Consolidation using the Master D SKU
            final_compiled_picklist = merged_df.groupby(MAP_D_SKU_COL)[PICKLIST_QTY_COL].sum().reset_index()
            final_compiled_picklist.rename(
                columns={PICKLIST_QTY_COL: 'Total Pick Quantity (D SKU)'},
                inplace=True
            )
            final_compiled_picklist = final_compiled_picklist.sort_values(by=MAP_D_SKU_COL)

            # 7. Display and Download
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
            st.error(f"❌ Critical Error: Column not found. Missing column: **{e}**.")
            st.info("Please verify the column names defined at the top of the `app.py` script match your files.")
            st.write("**Sample Columns Found in Combined Pick Lists:**", combined_picklist_df.columns.tolist())
            st.write("**Sample Columns Found in Mapping File:**", mapping_df.columns.tolist())

    else:
        st.error("Could not process all files. Please check the error messages above.")

else:
    st.warning("Please upload all 10 required files to generate the compiled list.")
