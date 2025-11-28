import streamlit as st
import pandas as pd
from PIL import Image
import time
from datetime import datetime

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
    # Placeholder for custom CSS if needed
    pass

def simulate_processing():
    """Simulates a loading bar for operations"""
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)
    st.success("Operation Complete!")

# --- Service Modules ---

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

def service_reconciliation():
    st.subheader("📊 Reconciliation Report")
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

def service_task_tracker():
    st.subheader("✅ Task Tracker")
    
    with st.form(key='task_form', clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_task = st.text_input("New Task")
        with col2:
            add_task = st.form_submit_button("Add Task")
            
        if add_task and new_task:
            st.session_state.tasks.append({"task": new_task, "status": "Pending", "date": datetime.now().strftime("%Y-%m-%d")})
            st.rerun()

    if st.session_state.tasks:
        for i, task in enumerate(st.session_state.tasks):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"{i+1}. {task['task']}")
            with col2:
                st.caption(task['date'])
            with col3:
                if st.button("Complete", key=f"del_{i}"):
                    st.session_state.tasks.pop(i)
                    st.rerun()
    else:
        st.info("No pending tasks. Good job!")

# --- Main Navigation Sidebar ---

def main():
    st.sidebar.title("🛒 Ecartologist")
    st.sidebar.caption("E-commerce Solution Admin")
    st.sidebar.divider()

    # Sidebar Navigation Logic
    # We use expanders to simulate collapsible categories
    
    # Selection holder
    selected_option = None
    
    # 1. E-COMMERCE SECTION
    with st.sidebar.expander("📦 E-commerce Solutions", expanded=True):
        st.markdown("**Listing Optimization**")
        opt_choice = st.radio("Select Tool:", 
                              ["Keyword Extractor", "Image Optimizer"], 
                              label_visibility="collapsed",
                              index=None,
                              key="nav_opt")
        
        if opt_choice:
            selected_option = opt_choice

        st.markdown("---")
        st.markdown("**Creation Tools**")
        if st.sidebar.button("Listing Maker", use_container_width=True):
             selected_option = "Listing Maker"

        st.markdown("---")
        st.markdown("**Reporting**")
        if st.sidebar.button("Reconciliation", use_container_width=True):
            selected_option = "Reconciliation"

        st.markdown("---")
        st.markdown("**GST Filing**")
        gst_choice = st.selectbox("Select Return Type:", 
                                  ["Select...", "GSTR-1", "GSTR-2A/2B", "GSTR-3B"], 
                                  key="nav_gst")
        if gst_choice != "Select...":
            selected_option = gst_choice

    # 2. TASK TRACKER SECTION
    with st.sidebar.expander("📝 Productivity", expanded=False):
        if st.button("Task Tracker", use_container_width=True):
            selected_option = "Task Tracker"

    # Default Page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

    # Update session state based on interactions
    if selected_option:
        st.session_state.current_page = selected_option

    # --- Router Logic (Displaying the selected page) ---
    
    page = st.session_state.current_page

    if page == "Dashboard":
        st.title("Welcome to Ecartologist Admin")
        st.write("Select a service from the sidebar to begin.")
        
        # Dashboard metrics example
        col1, col2, col3 = st.columns(3)
        col1.metric("Pending Orders", "124", "4%")
        col2.metric("Listings Optimized", "45", "-2%")
        col3.metric("Pending GST", "GSTR-3B", "Due in 2 days")

    elif page == "Keyword Extractor":
        service_keyword_extractor()
    
    elif page == "Image Optimizer":
        service_image_optimizer()
        
    elif page == "Listing Maker":
        service_listing_maker()
        
    elif page == "Reconciliation":
        service_reconciliation()
        
    elif page in ["GSTR-1", "GSTR-2A/2B", "GSTR-3B"]:
        service_gst_filing(page)
        
    elif page == "Task Tracker":
        service_task_tracker()

if __name__ == "__main__":
    main()
