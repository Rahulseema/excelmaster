import streamlit as st
import pandas as pd

st.title("🛍️ Meesho Pick List Compiler")

uploaded_files = st.file_uploader(
    "Upload all 9 Meesho Pick List files (CSV or Excel)",
    type=['csv', 'xlsx'],
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"Loaded {len(uploaded_files)} files. Compiling now...")

    # 1. Read and Concatenate Files
    all_data = []
    for file in uploaded_files:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else: # Assuming .xlsx
            df = pd.read_excel(file)
        all_data.append(df)

    combined_df = pd.concat(all_data, ignore_index=True)

    # 2. Consolidate (Group and Sum) - IMPORTANT: Adjust column names!
    # Replace 'SKU' and 'Quantity' with the actual column names from your Meesho files.
    compiled_picklist = combined_df.groupby('SKU')['Quantity'].sum().reset_index()
    compiled_picklist.rename(columns={'Quantity': 'Total Pick Quantity'}, inplace=True)

    # 3. Display and Download
    st.subheader("✅ Compiled Pick List")
    st.dataframe(compiled_picklist)

    # Download button
    csv = compiled_picklist.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Final Pick List CSV",
        data=csv,
        file_name='compiled_meesho_picklist.csv',
        mime='text/csv'
    )
