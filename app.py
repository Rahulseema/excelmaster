# ==============================================================================
# 1. CONFIGURATION SECTION (UPDATED)
# ==============================================================================

# ... (MASTER_ACCOUNT_NAMES, MULTI_ACCOUNT_CHANNELS, SINGLE_ACCOUNT_CHANNELS remain the same) ...

# Mapping file column names (UPDATED TO REFLECT ATTRIBUTES):
MAP_CHANNEL_SKU_COL = 'Channel SKU'
MAP_CHANNEL_SIZE_COL = 'Channel Size'
MAP_CHANNEL_COLOR_COL = 'Channel Color'
MAP_OUR_SKU_COL = 'Our SKU'
MAP_ACCOUNT_COL = 'Account name'

# Pick List file column names (WHAT THE APP LOOKS FOR IN YOUR 44 UPLOADS):
PICKLIST_SKU_COL = 'SKU'
PICKLIST_SIZE_COL = 'Size'
PICKLIST_COLOR_COL = 'Color'
PICKLIST_QTY_COL = 'Qty'


# Configuration for Pick List Column Names by Channel (Must contain SKU, Size, Color, Qty headers)
# !!! WARNING: VERIFY THESE COLUMN NAMES AGAINST YOUR ACTUAL REPORTS !!!
# Example: Amazon's "item-sku" is the SKU, but "item-description" might contain the size/color. 
# You must adjust these to match your actual report headers!
CHANNEL_COLUMNS_MAP = {
    "Meesho": {'sku': PICKLIST_SKU_COL, 'size': PICKLIST_SIZE_COL, 'color': PICKLIST_COLOR_COL, 'qty': PICKLIST_QTY_COL},
    "Amazon": {'sku': 'item-sku', 'size': 'size-attribute', 'color': 'color-attribute', 'qty': 'quantity-purchased'}, 
    "Flipkart": {'sku': 'Seller SKU ID', 'size': 'Size', 'color': 'Color', 'qty': 'quantity-purchased'},
    "Myntra": {'sku': 'Seller SKU', 'size': 'Style Size', 'color': 'Color Name', 'qty': 'Quantity'},
    "Nykaa": {'sku': 'Seller Code', 'size': 'Size', 'color': 'Color', 'qty': 'Inventory Qty'}, 
    "JioMart": {'sku': 'Product SKU', 'size': 'Size', 'color': 'Color', 'qty': 'Order Qty'},
    "Ajio": {'sku': 'Seller SKU', 'size': 'Size', 'color': 'Color', 'qty': 'Unit Qty'},
    "Tatacliq": {'sku': 'Item Code', 'size': 'Size', 'color': 'Color', 'qty': 'Units'},
}

# Function to generate the sample mapping file
def get_sample_mapping_file():
    sample_data = {
        MAP_CHANNEL_SKU_COL: ['MSHO-D101', 'AMZN-D101', 'MSHO-D102', 'MSHO-D101'],
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

# ... (read_uploaded_file helper function remains the same) ...
