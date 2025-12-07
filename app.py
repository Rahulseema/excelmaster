import streamlit as st
import pandas as pd
from io import BytesIO

# --- Configuration ---
# List of your 9 Meesho accounts for clear labeling
ACCOUNT_NAMES = [
    "Meesho Account 1 (Main)",
    "Meesho Account 2 (Partner)",
    "Meesho Account 3",
    "Meesho Account 4",
    "Meesho Account 5",
    "Meesho Account 6",
    "Meesho Account 7",
    "Meesho Account 8",
    "Meesho Account 9 (Reserve)"
]
ALLOWED_FILE_TYPES = ['csv', 'xlsx']

# --- Helper Function to Read File ---
def read_uploaded_file(uploaded_file):
    """Reads a file object into a Pandas DataFrame."""
    try:
        if uploaded_file.name.endswith('.csv'):
            # Read CSV, assuming standard format
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            # Read Excel
            return pd.read_excel(uploaded_file)
        else:
            st.error(f"Unsupported file type for {uploaded_file.name}")
            return None
    except Exception as e:
        st.error(f"Error reading file {uploaded_file.name}: {e}")
        return None

# --- Main Streamlit App ---
st.title("🛍️ Meesho Pick List Compiler")
st.markdown("---")
st.subheader("Upload Pick List Files for All 9 Accounts")

uploaded_files_map = {}
all_files_uploaded = True

# Create 9 separate uploaders
with st.container():
    col1, col2, col3 = st.columns(3)
    
    # Loop through the 9 accounts and create an uploader in one of the three columns
    for i, account_name in enumerate(ACCOUNT_NAMES):
        col = [col1, col2, col3][i % 3] # Distribute uploaders into 3 columns
        
        with col:
            file = st.file_uploader(
                f"**{i+1}. {account_name}**",
                type=ALLOWED_FILE_TYPES,
                key=f"file_uploader_{i}" # Important for unique widget IDs
            )
            uploaded_files_map[account_name] = file
            
            # Check if file is missing for any account
            if file is None:
                all_files_uploaded = False

st.markdown("---")


# --- Processing Logic ---
if all_files_uploaded and len(uploaded_files_map) == len(ACCOUNT_NAMES):
    st.success("All 9 files uploaded! Processing data...")
    
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
        # ⚠️ IMPORTANT: **Verify these column names ('SKU' and 'Quantity')**
        # and adjust them to match the exact headers in your Meesho reports.
        try:
            compiled_picklist = combined_df.groupby('SKU')['Quantity'].sum().reset_index()
            compiled_picklist.rename(columns={'Quantity': 'Total Pick Quantity'}, inplace=True)

            # 3. Display Results
            st.subheader("📦 Final Compiled Pick List")
            st.dataframe(compiled_picklist)

            # 4. Download Button
            # Convert DataFrame to a downloadable format (BytesIO for Excel)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                compiled_picklist.to_excel(writer, index=False, sheet_name='Compiled_Picklist')
            
            st.download_button(
                label="⬇️ Download Final Pick List (Excel)",
                data=output.getvalue(),
                file_name='compiled_meesho_picklist.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        except KeyError as e:
            st.error(f"Error: Column not found. Please check your file headers. Missing column: {e}. ")
            st.dataframe(combined_df.head())
            st.write("---")
            st.write("Sample Columns from your files:")
            st.write(combined_df.columns.tolist())
            st.warning("You must change `'SKU'` and `'Quantity'` in the script to match the exact column names in your files.")


else:
    st.warning("Please upload all 9 Meesho Pick List files to generate the compiled list.")
