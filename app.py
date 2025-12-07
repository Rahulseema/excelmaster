import streamlit as st
import pandas as pd
from io import BytesIO

# --- Configuration: YOUR 9 ACCOUNT NAMES ---
ACCOUNT_NAMES = [
    "Drench",
    "Drench India",
    "Sparsh",
    "Sparsh SC",
    "Shine Arc",
    "Ansh ent",
    "BnB Industries",
    "Shopforher",
    "AV Enterprises"
]

ALLOWED_FILE_TYPES = ['csv', 'xlsx']

# --- Helper Function to Read File ---
def read_uploaded_file(uploaded_file):
    """Reads a file object into a Pandas DataFrame."""
    try:
        # Use a more memory-efficient way to read data directly from the buffer
        if uploaded_file.name.lower().endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.lower().endswith('.xlsx'):
            # The 'openpyxl' engine is required for reading Excel files
            return pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            st.error(f"Unsupported file type for {uploaded_file.name}")
            return None
    except Exception as e:
        st.error(f"Error reading file **{uploaded_file.name}**: {type(e).__name__} - {e}")
        st.warning("Ensure the file is not password-protected and is a valid CSV/Excel format.")
        return None

# --- Main Streamlit App ---
st.set_page_config(page_title="Meesho Pick List Compiler", layout="wide")
st.title("📦 Meesho Pick List Compiler")
st.markdown("Automate your daily compilation for 9 accounts into a single master pick list.")

st.subheader("1️⃣ Upload Pick List Files")
st.info("Please upload the pick list report (CSV or Excel) for each of your 9 accounts.")

uploaded_files_map = {}
all_files_uploaded = True

# Create 9 separate uploaders in a 3-column layout
col1, col2, col3 = st.columns(3)
columns = [col1, col2, col3]

# Loop through the 9 accounts and create an uploader in one of the three columns
for i, account_name in enumerate(ACCOUNT_NAMES):
    with columns[i % 3]: # Distribute uploaders into 3 columns
        file = st.file_uploader(
            f"**{i+1}. {account_name}**",
            type=ALLOWED_FILE_TYPES,
            key=f"file_uploader_{i}" # Unique key for each widget
        )
        uploaded_files_map[account_name] = file
        
        # Check if file is missing for any account
        if file is None:
            all_files_uploaded = False

st.markdown("---")


# --- Processing Logic ---
if all_files_uploaded and len(uploaded_files_map) == len(ACCOUNT_NAMES):
    st.subheader("2️⃣ Processing and Compilation")
    st.success("All 9 files uploaded! Compiling data...")
    
    dataframes = []
    
    # Read each uploaded file into a DataFrame
    for account_name, file in uploaded_files_map.items():
        df = read_uploaded_file(file)
        if df is not None:
            # OPTIONAL: Add an 'Account' column for tracking/debugging
            df['Meesho_Account'] = account_name
            dataframes.append(df)

    if dataframes:
        # 1. Concatenate all DataFrames
        combined_df = pd.concat(dataframes, ignore_index=True)
        
        # 2. Consolidate (Group and Sum)
        
        # ⚠️ CRITICAL STEP: CONFIRM YOUR COLUMN NAMES HERE!
        # The most common column names for SKU and Quantity on Meesho are:
        SKU_COLUMN = 'SKU ID' 
        QUANTITY_COLUMN = 'Quantity' 
        # If the script fails, change these two variables based on your file's headers.
        
        try:
            # Group by SKU and sum the quantities
            compiled_picklist = combined_df.groupby(SKU_COLUMN)[QUANTITY_COLUMN].sum().reset_index()
            compiled_picklist.rename(columns={QUANTITY_COLUMN: 'Total Pick Quantity'}, inplace=True)
            compiled_picklist = compiled_picklist.sort_values(by=SKU_COLUMN)

            # 3. Display Results
            st.subheader("3️⃣ Final Compiled Pick List")
            st.dataframe(compiled_picklist, use_container_width=True)

            # 4. Download Button
            # Convert DataFrame to a downloadable Excel format
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                compiled_picklist.to_excel(writer, index=False, sheet_name='Master_Picklist')
            
            st.download_button(
                label="⬇️ Download Master Pick List (Excel)",
                data=output.getvalue(),
                file_name='compiled_meesho_picklist_master.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        except KeyError as e:
            st.error(f"❌ Error: Column not found.")
            st.warning(f"The script looked for column **{e}** but could not find it.")
            st.info("Please check the column names in your uploaded files.")
            st.write("---")
            st.write("**Sample Columns Found in Your Files:**")
            st.dataframe(pd.DataFrame(combined_df.columns.tolist(), columns=["Column Names"]))
            st.warning(f"You must manually correct `SKU_COLUMN` and `QUANTITY_COLUMN` in the `app.py` script to match one of the column names above (e.g., 'Seller SKU', 'Order Qty').")


else:
    st.warning("Please upload the pick list file for all 9 Meesho accounts to proceed with compilation.")
