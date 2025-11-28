import streamlit as st
import pandas as pd
from PIL import Image
import time
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="Ecartologist | E-commerce Solutions",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Management (for Task Tracker) ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# --- Helper Functions ---
def local_css(file_name):
    """Placeholder for custom CSS if needed"""
    pass

def simulate_processing():
    """Simulates a loading bar for operations"""
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)
    st.success("Analysis Complete!")
    return True

# --- Data Simulation Functions (To run the demo without real files) ---

def create_mock_sales_df():
    """Simulates sales data with 'Column F (SKU)', 'Units Sold', and 'Warehouse' as default headers."""
    prod_skus = [f'"SKU:PROD{i:03}"' for i in range(1, 11)] 
    slow_skus = [f'"SKU:SLOW{i:03}"' for i in range(1, 6)]
    
    data = {
        'Column F (SKU)': prod_skus * 2 + slow_skus, # Length 25
        'Units Sold': [500, 450, 300, 250, 200, 150, 100, 90, 80, 70, 60, 50, 40, 30, 10, 50, 40, 30, 20, 10, 5, 4, 3, 2, 1],
        'State': ['MH', 'KA', 'DL', 'TN', 'MH', 'KA', 'DL', 'TN', 'MH', 'KA', 'DL', 'TN', 'MH', 'KA', 'DL', 'MH', 'KA', 'DL', 'TN', 'MH', 'KA', 'DL', 'TN', 'MH', 'KA'],
        'Warehouse': ['BLR', 'BLR', 'DEL', 'MAA', 'BLR', 'BLR', 'DEL', 'MAA', 'BLR', 'BLR', 'DEL', 'MAA', 'BLR', 'BLR', 'DEL', 'MAA', 'BLR', 'DEL', 'MAA', 'BLR', 'DEL', 'MAA', 'BLR', 'DEL', 'MAA']
    }
    
    df = pd.DataFrame(data)
    df['Column E (FSN Ref)'] = 'FSN_Ref_Data' # Add an E column for context
    return df

def create_mock_inventory_df():
    """Simulates inventory data with 'Column F (SKU)' as the header."""
    prod_skus = [f'"SKU:PROD{i:03}"' for i in range(1, 11)] 
    slow_skus = [f'"SKU:SLOW{i:03}"' for i in range(1, 6)]
    
    data = {
        'Column F (SKU)': prod_skus + slow_skus,
        'Warehouse': ['BLR', 'DEL', 'MAA', 'BLR', 'DEL', 'MAA', 'BLR', 'DEL', 'MAA', 'BLR', 'BLR', 'DEL', 'MAA', 'BLR', 'DEL'],
        'Current Stock': [1000, 800, 500, 400, 300, 200, 150, 100, 50, 40, 30, 20, 10, 5, 2]
    }
    df = pd.DataFrame(data)
    df['Column G (Other Data)'] = 'Other_Inventory_Data' 
    return df

def clean_sku(sku_series):
    """Removes special characters ' " ' and text 'SKU:' from the SKU column."""
    if sku_series.dtype == 'object':
        # This regex handles both the outer quotes and the "SKU:" prefix
        return sku_series.astype(str).str.replace(r'"|SKU:', '', regex=True).str.strip()
    return sku_series # Return original if not string

# The calculate_fsn function now accepts the name of the demand column
def calculate_fsn(sales_df, demand_col_name):
    """Calculates FSN status based on 70/20/10 sales volume split (ABC analysis principle)."""
    
    # 1. Calculate total sales per SKU - NOW USES demand_col_name
    sku_sales = sales_df.groupby('SKU_Clean')[demand_col_name].sum().reset_index()
    sku_sales.rename(columns={demand_col_name: 'Units Sold'}, inplace=True)
    sku_sales = sku_sales.sort_values(by='Units Sold', ascending=False).reset_index(drop=True)
    
    # 2. Calculate cumulative percentage
    total_sales = sku_sales['Units Sold'].sum()
    if total_sales == 0:
         sku_sales['FSN Status'] = 'N (Non-Moving)'
         return sku_sales[['SKU_Clean', 'Units Sold', 'FSN Status']]
         
    sku_sales['Sales Percentage'] = (sku_sales['Units Sold'] / total_sales) * 100
    sku_sales['Cumulative Percentage'] = sku_sales['Sales Percentage'].cumsum()
    
    # 3. Apply FSN classification (70% Fast, 20% Slow, 10% Non)
    def assign_fsn(cumulative_perc):
        if cumulative_perc <= 70:
            return 'F (Fast Moving)'
        elif cumulative_perc <= 90: # 70% + 20% = 90%
            return 'S (Slow Moving)'
        else:
            return 'N (Non-Moving)'

    sku_sales['FSN Status'] = sku_sales['Cumulative Percentage'].apply(assign_fsn)
    
    return sku_sales[['SKU_Clean', 'Units Sold', 'FSN Status']]

# --- Service Modules: Inventory Planning (Updated to use Selectbox for Units Sold Column) ---

def service_inventory_planning():
    st.subheader("📦 Inventory Planning")
    
    tab1, tab2 = st.tabs(["FBF (Flipkart) FSN Analysis", "FBA (Amazon)"])
    
    with tab1:
        st.markdown("### Fulfilled by Flipkart (FBF) Inventory & FSN Planner")
        st.info("Upload your inventory and sales data. You must select the correct SKU, Demand, and Warehouse columns after upload.")

        # File Uploads (Uses mock data if files are not uploaded)
        col_fbf1, col_fbf2 = st.columns(2)
        
        # Initialize with mock data if not set
        if 'fbf_inventory_data' not in st.session_state:
            st.session_state['fbf_inventory_data'] = create_mock_inventory_df()
        if 'fbf_sales_data' not in st.session_state:
            st.session_state['fbf_sales_data'] = create_mock_sales_df()

        # --- UPLOADER 1: INVENTORY ---
        with col_fbf1:
            inventory_file = st.file_uploader("1. Current Warehouse Inventory (CSV)", type=['csv'], key="fbf_inventory")
            if inventory_file:
                try:
                    st.session_state['fbf_inventory_data'] = pd.read_csv(inventory_file)
                except Exception as e:
                    st.error(f"Error reading inventory file: {e}")

            inv_cols = st.session_state['fbf_inventory_data'].columns.tolist()
            default_inv_index = inv_cols.index('Column F (SKU)') if 'Column F (SKU)' in inv_cols else 0
            
            inv_sku_col = st.selectbox(
                "Select SKU Column (Inventory)", 
                inv_cols, 
                index=default_inv_index,
                key="inv_sku_col_select"
            )

        # --- UPLOADER 2: SALES ---
        with col_fbf2:
            sales_file = st.file_uploader("2. Demand in last 30 days (Sales File - CSV)", type=['csv'], key="fbf_sales")
            if sales_file:
                try:
                    st.session_state['fbf_sales_data'] = pd.read_csv(sales_file)
                except Exception as e:
                    st.error(f"Error reading sales file: {e}")

            sales_cols = st.session_state['fbf_sales_data'].columns.tolist()
            default_sales_sku_index = sales_cols.index('Column F (SKU)') if 'Column F (SKU)' in sales_cols else 0
            
            sales_sku_col = st.selectbox(
                "Select SKU Column (Sales)", 
                sales_cols, 
                index=default_sales_sku_index,
                key="sales_sku_col_select"
            )
            
            # --- SELECTBOX FOR UNITS SOLD / DEMAND COLUMN ---
            default_demand_index = sales_cols.index('Units Sold') if 'Units Sold' in sales_cols else (sales_cols.index(sales_sku_col) + 1 if sales_sku_col in sales_cols and len(sales_cols) > sales_cols.index(sales_sku_col) + 1 else 0)

            demand_col = st.selectbox(
                "Select Units Sold / Demand Column (Sales)", 
                sales_cols, 
                index=default_demand_index,
                key="sales_demand_col_select"
            )

            # --- NEW SELECTBOX FOR WAREHOUSE / LOCATION COLUMN ---
            default_warehouse_index = sales_cols.index('Warehouse') if 'Warehouse' in sales_cols else (sales_cols.index(sales_sku_col) + 2 if sales_sku_col in sales_cols and len(sales_cols) > sales_cols.index(sales_sku_col) + 2 else 0)

            warehouse_col = st.selectbox(
                "Select Warehouse/Location Column (Sales)",
                sales_cols,
                index=default_warehouse_index,
                key="sales_warehouse_col_select"
            )


        if st.button("Generate FSN & Inventory Analysis", key="analyze_fbf"):
            
            # --- START FSN ANALYSIS ---
            if 'fbf_inventory_data' in st.session_state and 'fbf_sales_data' in st.session_state:
                
                # 1. CLEANING AND PREPARATION
                sales_df = st.session_state['fbf_sales_data'].copy()
                inventory_df = st.session_state['fbf_inventory_data'].copy()

                # Data Cleaning: Use the dynamically selected column for cleaning
                try:
                    # Clean SKUs
                    sales_df['SKU_Clean'] = clean_sku(sales_df[sales_sku_col])
                    inventory_df['SKU_Clean'] = clean_sku(inventory_df[inv_sku_col])
                    
                    # Convert Demand column to numeric and standardize name
                    sales_df[demand_col] = pd.to_numeric(sales_df[demand_col], errors='coerce').fillna(0)
                    sales_df.rename(columns={demand_col: 'Demand (30D)'}, inplace=True)
                    
                    # Standardize the Warehouse column name for consistent grouping
                    sales_df.rename(columns={warehouse_col: 'Warehouse'}, inplace=True)
                    
                except KeyError as e:
                    st.error(f"Critical Error: The selected column '{e.args[0]}' was not found in one of the dataframes. Please re-upload the file or ensure the correct column is selected.")
                    return # Stop execution if a core column is missing
                except Exception as e:
                    st.error(f"Error during data processing (e.g., converting Demand column to numbers): {e}")
                    return

                
                # 2. FSN CLASSIFICATION
                # Pass the original name of the column containing demand data
                fsn_status_df = calculate_fsn(sales_df, 'Demand (30D)')

                # Merge FSN status back into Sales and Inventory DFs
                sales_df = sales_df.merge(fsn_status_df[['SKU_Clean', 'FSN Status']], on='SKU_Clean', how='left')
                
                # Prepare Inventory DF for merging (needed to get 'Units Sold' (Demand) for non-movers)
                inv_sku_demand = fsn_status_df[['SKU_Clean', 'Units Sold', 'FSN Status']].rename(columns={'Units Sold': 'Total Demand (30D)'})
                inventory_df = inventory_df.merge(inv_sku_demand, on='SKU_Clean', how='left')
                
                # Fill missing FSN (for items in inventory but not sold in last 30 days)
                inventory_df['FSN Status'].fillna('N (Non-Moving)', inplace=True)
                inventory_df['Total Demand (30D)'].fillna(0, inplace=True)
                
                # --- REPORT GENERATION ---
                simulate_processing()
                st.markdown("---")
                st.success("FSN Classification and Inventory Mapping Complete. Displaying FSN Reports based on cleaned SKUs.")
                
                
                # Report 1: Best 10 FSN SKUs (Top 10 Fast Movers by Volume)
                st.subheader("1. Best 10 FSN SKUs (Fastest Movers by Sales Volume)")
                best_10_fsn = fsn_status_df[fsn_status_df['FSN Status'].str.startswith('F')].head(10).reset_index(drop=True)
                best_10_fsn.columns = ['SKU Name', 'Total Demand (30D)', 'FSN Status']
                st.dataframe(best_10_fsn, use_container_width=True)


                # Report 2: Least 10 FSN SKUs (Slowest Selling Non-Movers)
                st.subheader("2. Least 10 FSN SKUs (Non-Moving / Slowest Sellers)")
                # Show Non-Moving items, sorted by lowest sales volume
                worst_10_fsn = fsn_status_df.sort_values(by='Units Sold', ascending=True).head(10).reset_index(drop=True)
                worst_10_fsn.columns = ['SKU Name', 'Total Demand (30D)', 'FSN Status']
                st.dataframe(worst_10_fsn, use_container_width=True)


                # Report 3: FSN-wise demand in warehouses (Top 20 table)
                st.subheader("3. FSN-Wise Demand in Warehouses (Top 20 SKU/Warehouse Combinations)")
                
                # Calculate aggregated demand volume per SKU-Warehouse combination
                # 'Warehouse' is now guaranteed to be the column name due to renaming above
                warehouse_demand = sales_df.groupby(['SKU_Clean', 'Warehouse', 'FSN Status'])['Demand (30D)'].sum().reset_index()
                
                # Merge with inventory for stock visibility
                inventory_stock = inventory_df.groupby(['SKU_Clean', 'Warehouse'])['Current Stock'].sum().reset_index()
                
                demand_report = warehouse_demand.merge(inventory_stock, on=['SKU_Clean', 'Warehouse'], how='left')
                demand_report.rename(columns={'SKU_Clean': 'SKU Name', 'Demand (30D)': 'Demand (30D)', 'Current Stock': 'Available Stock'}, inplace=True)
                
                demand_report.sort_values(by='Demand (30D)', ascending=False, inplace=True)
                
                st.dataframe(demand_report.head(20), use_container_width=True)

            else:
                st.warning("Please upload both the Current Warehouse Inventory and Sales files to run the FSN analysis.")


    with tab2:
        st.markdown("### Fulfilled by Amazon (FBA)")
        st.info("Restock recommendations for Amazon Fulfillment Centers.")
        st.dataframe(pd.DataFrame({
            "ASIN": ["B00123XY", "B00987AB"],
            "FBA Stock": [150, 20],
            "Inbound": [0, 50],
            "Recommended Action": ["Hold", "Restock Urgent"]
        }), use_container_width=True)


# --- Service Modules (Non-Inventory, truncated for brevity) ---

def service_listing_maker():
    st.subheader("📝 Listing Maker")
    st.markdown("Create A+ Content templates for Amazon/Flipkart.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        title = st.text_input("Product Title")
        price = st.number_input("Selling Price", min_value=0.0)
        bullets = st.text_area("Bullet Points (One per line)")
    
    with col2:
        st.markdown("### Preview")
        st.markdown(f"**{title if title else 'Product Title'}**")
        st.markdown(f"Price: ₹{price}")
        if bullets:
            for line in bullets.split('\n'):
                st.markdown(f"- {line}")
        else:
            st.markdown("- Feature 1\n- Feature 2")

def service_keyword_extractor():
    st.subheader("🔍 Keyword Extractor")
    st.info("Extract high-volume keywords from your product descriptions.")
    
    text_input = st.text_area("Paste Product Description or Competitor Listing text:", height=200)
    
    if st.button("Extract Keywords"):
        if text_input:
            simulate_processing()
            # Simple frequency analysis logic for demo
            words = text_input.lower().split()
            # Remove simple punctuation (basic approach)
            clean_words = [w.strip(".,!?:;") for w in words if len(w) > 3]
            df = pd.DataFrame(clean_words, columns=['Keyword'])
            result = df['Keyword'].value_counts().reset_index()
            result.columns = ['Keyword', 'Frequency']
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(result, use_container_width=True)
            with col2:
                st.bar_chart(result.set_index('Keyword').head(10))
        else:
            st.warning("Please enter some text to analyze.")

def service_image_optimizer():
    st.subheader("🖼️ Image Optimizer")
    st.info("Compress and resize images for faster page loads.")
    
    uploaded_file = st.file_uploader("Upload Product Image", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption='Original Image', use_container_width=True)
            st.write(f"Original Size: {image.size}")
            
        with col2:
            st.write("Optimization Settings:")
            quality = st.slider("Quality Compression", 10, 100, 85)
            resize_factor = st.slider("Resize Percentage", 10, 100, 100)
            
            if st.button("Optimize"):
                simulate_processing()
                st.image(image, caption='Optimized Preview (Simulated)', use_container_width=True)
                st.success(f"Image optimized to {quality}% quality.")
                st.download_button("Download Optimized Image", data=uploaded_file, file_name="optimized_image.jpg")

def service_listing_optimizer():
    st.subheader("🚀 Listing Optimizer")
    st.info("Analyze and improve your current product listings.")
    st.text_input("Enter Product URL (Amazon/Flipkart)")
    st.write("OR")
    st.text_area("Paste Listing Content for Audit")
    if st.button("Analyze Listing"):
        simulate_processing()
        st.success("Analysis Complete")
        st.write("**Score: 7/10**")
        st.warning("Suggestion: Title length is too short. Add more keywords.")

# --- Service Modules: Pricing Tool ---

def service_rate_card():
    st.subheader("💳 Rate Card")
    st.info("View marketplace rate cards and commission structures.")
    
    platform = st.selectbox("Select Platform", ["Amazon", "Flipkart", "Meesho"])
    category = st.selectbox("Select Category", ["Electronics", "Fashion", "Home & Kitchen", "Beauty"])
    
    if st.button("Fetch Rates"):
        st.table(pd.DataFrame({
            "Fee Type": ["Commission", "Fixed Fee", "Collection Fee", "Shipping (Local)"],
            "Percentage/Amount": ["12%", "₹15", "2%", "₹45"]
        }))

def service_pricing_update():
    st.subheader("💲 Pricing Update")
    st.info("Bulk update pricing across platforms.")
    
    st.file_uploader("Upload Pricing CSV Template")
    if st.button("Process Price Updates"):
        simulate_processing()
        st.success("Prices updated successfully on 45 SKUs.")

# --- Service Modules: Reporting ---

def service_payment_reconciliation():
    st.subheader("📊 Payment Reconciliation")
    st.write("Upload your Marketplace Settlement Report vs ERP Report.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.file_uploader("Upload Marketplace CSV", key="mkt")
    with col2:
        st.file_uploader("Upload ERP/Ledger CSV", key="erp")
        
    if st.button("Run Reconciliation"):
        simulate_processing()
        st.warning("Demo Mode: Showing dummy discrepancy data.")
        
        # Dummy Data
        data = {
            'OrderID': ['101-A', '102-B', '103-C'],
            'Marketplace_Amt': [500, 1200, 800],
            'ERP_Amt': [500, 1200, 850],
            'Status': ['Matched', 'Matched', 'Mismatch (-50)']
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

def service_advertisement_analysis():
    st.subheader("📢 Advertisement Analysis")
    st.info("Analyze ACOS, ROAS, and ad spend efficiency.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Ad Spend", "₹50,000", "+12%")
    col2.metric("Sales from Ads", "₹2,25,000", "+8%")
    col3.metric("ROAS", "4.5", "-0.2")
    
    st.bar_chart({"Campaign A": 40, "Campaign B": 25, "Campaign C": 35})

def service_pnl():
    st.subheader("📉 Profit & Loss (P&L)")
    st.info("Monthly P&L statement generation.")
    
    st.date_input("Select Date Range", value=(datetime(2023, 1, 1), datetime(2023, 1, 31)))
    if st.button("Generate P&L"):
        st.table(pd.DataFrame({
            "Item": ["Total Sales", "COGS", "Marketplace Fees", "Marketing", "Net Profit"],
            "Amount": ["₹10,00,000", "₹4,00,000", "₹3,00,000", "₹1,00,000", "₹2,00,000"]
        }))

def service_return_analysis():
    st.subheader("↩️ Return Analysis")
    st.info("Analyze return reasons and rates.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Return Rate by Category**")
        st.bar_chart({"Electronics": 5, "Fashion": 15, "Home": 8})
    with col2:
        st.write("**Top Return Reasons**")
        st.write("1. Size Issue (40%)")
        st.write("2. Defective Product (25%)")
        st.write("3. Better Price Available (15%)")


# --- Service Modules: GST Filing ---

def service_gst_filing(gst_type):
    st.subheader(f"🏛️ GST Filing: {gst_type}")
    
    period = st.date_input("Select Filing Period", datetime.now())
    st.write(f"Preparing {gst_type} for: {period.strftime('%B %Y')}")
    
    uploaded_file = st.file_uploader(f"Upload Sales/Purchase Data for {gst_type}", type=['csv', 'xlsx'])
    
    if uploaded_file:
        st.success("File Uploaded Successfully")
        if st.button(f"Generate {gst_type} JSON"):
            simulate_processing()
            st.json({
                "gstin": "29ABCDE1234F1Z5",
                "fp": "102023",
                "gt": 500000,
                "cur_gt": 500000,
                "type": gst_type
            })
            st.success("JSON Generated ready for Portal Upload.")

# --- Service Modules: Insights ---

def service_business_health():
    st.subheader("❤️ Business Health")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Account Health Score", "85/100", "+5")
        st.progress(85)
    with col2:
        st.error("2 Policy Violations Detected")
        st.success("0 IP Complaints")
        st.info("98% VTR (Valid Tracking Rate)")

def service_earning_summary():
    st.subheader("💰 Earning Summary")
    st.line_chart({"Jan": 50000, "Feb": 65000, "Mar": 55000, "Apr": 72000})
    st.write("Projected Earnings for May: ₹80,000")

# --- Service Modules: Productivity ---

def service_task_tracker():
    st.subheader("✅ Task Tracker Dashboard")
    
    # --- 1. Cleanup Logic (Remove tasks completed > 7 days ago) ---
    if st.session_state.tasks:
        now = datetime.now()
        cleaned_tasks = []
        for task in st.session_state.tasks:
            keep = True
            # Check if task is completed and how long ago
            if task.get("Status") == "Completed" and task.get("Completed At"):
                try:
                    completion_time = task["Completed At"]
                    # Calculate difference
                    if (now - completion_time).days > 7:
                        keep = False
                except:
                    pass # Keep if date parsing fails
            
            if keep:
                cleaned_tasks.append(task)
        st.session_state.tasks = cleaned_tasks

    # --- 2. Dashboard Metrics ---
    if st.session_state.tasks:
        df_metrics = pd.DataFrame(st.session_state.tasks)
        if "Status" in df_metrics.columns:
            status_counts = df_metrics['Status'].value_counts()
            
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Total Tasks", len(df_metrics))
            m2.metric("Assigned", status_counts.get("Assigned", 0))
            m3.metric("WIP", status_counts.get("WIP", 0))
            m4.metric("Road Block", status_counts.get("Road Block", 0))
            m5.metric("Completed", status_counts.get("Completed", 0))
            st.divider()
    else:
        st.info("No tasks in the tracker. Add one below to get started.")

    # --- 3. Add New Task Form ---
    with st.expander("➕ Add New Task", expanded=False):
        with st.form(key='add_task_form', clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                task_name = st.text_input("Task Name")
                project = st.text_input("Project")
            with col2:
                channel = st.text_input("Channel")
                given_by = st.text_input("Task Given By")
                assigned_to = st.text_input("Assigned To")
            with col3:
                followup_by = st.text_input("Followup By")
                lead_time = st.text_input("Lead Time (e.g. 2 Days)")
                remarks = st.text_area("Remarks")
            
            submit_button = st.form_submit_button(label='Add Task')
            
            if submit_button and task_name:
                new_task = {
                    "Priority": priority,
                    "Task Name": task_name,
                    "Project": project,
                    "Channel": channel,
                    "Task Given By": given_by,
                    "Assigned To": assigned_to,
                    "Followup By": followup_by,
                    "Lead Time": lead_time,
                    "Status": "Assigned",
                    "Remarks": remarks,
                    "Created At": datetime.now(),
                    "Completed At": None
                }
                st.session_state.tasks.append(new_task)
                st.rerun()

    # --- 4. Task Table (Editable) ---
    if st.session_state.tasks:
        st.subheader("📋 Task List")
        
        # Prepare DataFrame
        df = pd.DataFrame(st.session_state.tasks)
        
        # Add Serial Number
        df.insert(0, 'Srl No.', range(1, 1 + len(df)))
        
        # Define Column Configuration
        column_config = {
            "Srl No.": st.column_config.NumberColumn(disabled=True, width="small"),
            "Priority": st.column_config.SelectboxColumn(
                "Priority",
                options=["High", "Medium", "Low"],
                width="small",
                required=True
            ),
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["Assigned", "Accepted", "WIP", "Road Block", "Completed"],
                width="medium",
                required=True
            ),
            "Task Name": st.column_config.TextColumn("Task Name", width="medium"),
            "Created At": None, # Hide system columns
            "Completed At": None
        }

        # Editable Dataframe
        edited_df = st.data_editor(
            df,
            column_config=column_config,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="task_editor"
        )

        # Sync changes back to Session State
        # We drop 'Srl No.' before saving back
        updated_data = edited_df.drop(columns=['Srl No.']).to_dict('records')
        
        # Update timestamp logic for completion
        state_updated = False
        for i, task in enumerate(updated_data):
            # Check if status changed to Completed
            if task['Status'] == 'Completed':
                if not task.get('Completed At'):
                    task['Completed At'] = datetime.now()
                    state_updated = True
            else:
                # Reset completion time if moved out of Completed
                if task.get('Completed At') is not None:
                    task['Completed At'] = None
                    state_updated = True
        
        # Only update session state if data actually changed to prevent infinite loops
        # Comparison excluding nan/timestamps nuances
        if updated_data != st.session_state.tasks:
            st.session_state.tasks = updated_data
            if state_updated:
                st.rerun()

# --- Main Navigation Sidebar ---

def main():
    st.sidebar.title("🛒 Ecartologist")
    st.sidebar.caption("E-commerce Solution Admin")
    st.sidebar.divider()

    # Sidebar Navigation Logic
    # We use expanders to simulate collapsible categories
    
    # Initialize session state for page if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

    # 1. CATALOGING
    with st.sidebar.expander("📂 Cataloging", expanded=True):
        if st.button("Listing Maker", use_container_width=True): st.session_state.current_page = "Listing Maker"
        if st.button("Keyword Extractor", use_container_width=True): st.session_state.current_page = "Keyword Extractor"
        if st.button("Image Optimizer", use_container_width=True): st.session_state.current_page = "Image Optimizer"
        if st.button("Listing Optimizer", use_container_width=True): st.session_state.current_page = "Listing Optimizer"

    # 2. PRICING TOOL
    with st.sidebar.expander("💲 Pricing Tool"):
        if st.button("Rate Card", use_container_width=True): st.session_state.current_page = "Rate Card"
        if st.button("Pricing Update", use_container_width=True): st.session_state.current_page = "Pricing Update"

    # 3. REPORTING
    with st.sidebar.expander("📊 Reporting"):
        if st.button("Payment Reconciliation", use_container_width=True): st.session_state.current_page = "Payment Reconciliation"
        if st.button("Advertisement Analysis", use_container_width=True): st.session_state.current_page = "Advertisement Analysis"
        if st.button("P&L", use_container_width=True): st.session_state.current_page = "P&L"
        if st.button("Return", use_container_width=True): st.session_state.current_page = "Return"
        if st.button("Inventory Planning", use_container_width=True): st.session_state.current_page = "Inventory Planning"

    # 4. GST FILING
    with st.sidebar.expander("🏛️ GST Filing"):
        if st.button("GSTR-1", use_container_width=True): st.session_state.current_page = "GSTR-1"
        if st.button("GSTR 2A/2B", use_container_width=True): st.session_state.current_page = "GSTR 2A/2B"
        if st.button("GSTR 3B", use_container_width=True): st.session_state.current_page = "GSTR 3B"

    # 5. INSIGHTS
    with st.sidebar.expander("📈 Insights"):
        if st.button("Business Health", use_container_width=True): st.session_state.current_page = "Business Health"
        if st.button("Earning Summary", use_container_width=True): st.session_state.current_page = "Earning Summary"
        
    # 6. PRODUCTIVITY (Task Tracker)
    with st.sidebar.expander("📝 Productivity"):
         if st.button("Task Tracker", use_container_width=True): st.session_state.current_page = "Task Tracker"


    # --- Router Logic (Displaying the selected page) ---
    
    page = st.session_state.current_page

    if page == "Dashboard":
        st.title("Welcome to Ecartologist Admin")
        st.write("Select a service from the sidebar to begin.")
        col1, col2, col3 = st.columns(3)
        col1.metric("Pending Orders", "124", "4%")
        col2.metric("Listings Optimized", "45", "-2%")
        col3.metric("Pending GST", "GSTR-3B", "Due in 2 days")

    # Cataloging
    elif page == "Listing Maker": service_listing_maker()
    elif page == "Keyword Extractor": service_keyword_extractor()
    elif page == "Image Optimizer": service_image_optimizer()
    elif page == "Listing Optimizer": service_listing_optimizer()
    
    # Pricing
    elif page == "Rate Card": service_rate_card()
    elif page == "Pricing Update": service_pricing_update()
    
    # Reporting
    elif page == "Payment Reconciliation": service_payment_reconciliation()
    elif page == "Advertisement Analysis": service_advertisement_analysis()
    elif page == "P&L": service_pnl()
    elif page == "Return": service_return_analysis()
    # Note: Inventory Planning contains the FBF/FBA tabs
    elif page == "Inventory Planning": 
        # The main function handles the tab switching internally
        service_inventory_planning() 
    
    # GST
    elif page in ["GSTR-1", "GSTR 2A/2B", "GSTR 3B"]: service_gst_filing(page)
    
    # Insights
    elif page == "Business Health": service_business_health()
    elif page == "Earning Summary": service_earning_summary()
    
    # Productivity
    elif page == "Task Tracker": service_task_tracker()

if __name__ == "__main__":
    main()
