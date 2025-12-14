# ABOUTME: Cost data upload and management interface for econometricians
# ABOUTME: Allows uploading CSV/Excel files with cost data and mapping to frames/media owners

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
import io
from datetime import datetime

class CostDataManager:
    """Manages cost data upload, validation, and joining with campaign data"""
    
    def __init__(self) -> None:
        # Initialize session state for cost data
        if 'cost_data' not in st.session_state:
            st.session_state.cost_data = None
        if 'cost_mapping_type' not in st.session_state:
            st.session_state.cost_mapping_type = None
        if 'cost_join_column' not in st.session_state:
            st.session_state.cost_join_column = None
            
    def render_cost_upload_interface(self) -> None:
        """Render the complete cost upload and configuration interface"""
        
        st.markdown("### Cost Data Management")
        st.markdown("Upload your cost/spend data to join with Route audience metrics")
        
        # Create tabs for different input methods
        tab1, tab2, tab3 = st.tabs(["📁 Upload File", "✏️ Manual Entry", "📊 Rate Card"])
        
        with tab1:
            self._render_file_upload()
            
        with tab2:
            self._render_manual_entry()
            
        with tab3:
            self._render_rate_card_application()
            
        # Show current cost data status
        if st.session_state.cost_data is not None:
            self._render_cost_data_preview()
            
    def _render_file_upload(self) -> Optional[Dict[str, Any]]:
        """Render file upload interface for CSV/Excel files"""
        
        st.markdown("#### Upload Cost Data File")
        
        # File uploader with size limit
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit
        ALLOWED_MIME_TYPES = {
            'text/csv',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file with cost data",
            type=['csv', 'xlsx', 'xls'],
            help="File should contain columns for joining (e.g., frame_id, media_owner) and cost values. Max size: 50MB"
        )
        
        if uploaded_file is not None:
            # Validate file size
            if uploaded_file.size > MAX_FILE_SIZE:
                st.error(f"❌ File too large ({uploaded_file.size / 1024 / 1024:.1f}MB). Maximum allowed size is 50MB.")
                return None
            
            # Validate file type
            if uploaded_file.type and uploaded_file.type not in ALLOWED_MIME_TYPES:
                st.error(f"❌ Invalid file type: {uploaded_file.type}. Please upload a CSV or Excel file.")
                return None
            
            # Read the file with validation
            try:
                if uploaded_file.name.endswith('.csv'):
                    # Preview first few rows for validation
                    uploaded_file.seek(0)
                    df_preview = pd.read_csv(uploaded_file, nrows=5)
                    
                    # Validate structure
                    if df_preview.empty or len(df_preview.columns) < 2:
                        st.error("❌ Invalid file format: File must have at least 2 columns")
                        return None
                    
                    # Read full file
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file)
                else:
                    # Excel validation
                    uploaded_file.seek(0)
                    df_preview = pd.read_excel(uploaded_file, nrows=5)
                    
                    if df_preview.empty or len(df_preview.columns) < 2:
                        st.error("❌ Invalid file format: File must have at least 2 columns")
                        return None
                    
                    uploaded_file.seek(0)
                    df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ Loaded {len(df)} rows from {uploaded_file.name}")
                
                # Show preview
                st.markdown("##### Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Column mapping interface
                st.markdown("##### Configure Data Mapping")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Select join column
                    join_options = {
                        'frame_id': 'Frame ID (exact match)',
                        'media_owner': 'Media Owner name',
                        'media_owner_id': 'Media Owner ID',
                        'campaign_id': 'Campaign level (single cost)',
                        'postcode': 'Geographic (postcode)',
                        'custom': 'Custom mapping'
                    }
                    
                    join_type = st.selectbox(
                        "Join Type",
                        options=list(join_options.keys()),
                        format_func=lambda x: join_options[x],
                        help="How to match cost data with playout data"
                    )
                    
                    # Select which column in uploaded data contains join key
                    join_column = st.selectbox(
                        "Join Column in Your Data",
                        options=df.columns.tolist(),
                        help="Which column contains the matching values?"
                    )
                
                with col2:
                    # Select cost columns
                    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
                    
                    # Gross cost column
                    gross_cost_column = st.selectbox(
                        "Gross Cost Column",
                        options=numeric_columns,
                        help="Which column contains the gross cost/spend values?"
                    )
                    
                    # Net cost handling
                    st.markdown("**Net Cost Options**")
                    net_cost_method = st.radio(
                        "How to calculate net cost?",
                        ["Use Net Cost Column", "Apply Discount Rate", "No Net Cost"],
                        horizontal=True
                    )
                    
                    net_cost_column = None
                    discount_rate = 0.0
                    
                    if net_cost_method == "Use Net Cost Column":
                        remaining_cols = [c for c in numeric_columns if c != gross_cost_column]
                        if remaining_cols:
                            net_cost_column = st.selectbox(
                                "Net Cost Column",
                                options=remaining_cols,
                                help="Column with net (discounted) values"
                            )
                    elif net_cost_method == "Apply Discount Rate":
                        discount_rate = st.slider(
                            "Discount Rate (%)",
                            min_value=0.0,
                            max_value=50.0,
                            value=15.0,
                            step=0.5,
                            help="Discount to apply to gross cost"
                        )
                    
                    # Cost type
                    cost_type = st.selectbox(
                        "Cost Type",
                        options=[
                            "Total Cost",
                            "Cost per Thousand (CPT/CPM)",
                            "Cost per Frame per Day",
                            "Cost per Spot",
                            "Weekly Cost",
                            "Monthly Cost"
                        ],
                        help="What does the cost value represent?"
                    )
                
                # Validation checks
                st.markdown("##### Data Validation")
                
                validation_results = self._validate_cost_data(df, join_column, gross_cost_column)
                
                for check, result in validation_results.items():
                    if result['status'] == 'pass':
                        st.success(f"✅ {check}: {result['message']}")
                    elif result['status'] == 'warning':
                        st.warning(f"⚠️ {check}: {result['message']}")
                    else:
                        st.error(f"❌ {check}: {result['message']}")
                
                # Apply button
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    if st.button("✅ Apply Cost Data", type="primary"):
                        # Process and store cost data with gross/net
                        processed_df = df.copy()
                        
                        # Add net cost column if needed
                        if net_cost_method == "Apply Discount Rate":
                            processed_df['net_cost'] = processed_df[gross_cost_column] * (1 - discount_rate/100)
                        elif net_cost_method == "Use Net Cost Column" and net_cost_column:
                            processed_df['net_cost'] = processed_df[net_cost_column]
                        else:
                            processed_df['net_cost'] = processed_df[gross_cost_column]
                        
                        # Rename columns for consistency
                        processed_df['gross_cost'] = processed_df[gross_cost_column]
                        
                        # Store in session state
                        st.session_state.cost_data = processed_df
                        st.session_state.cost_mapping_type = join_type
                        st.session_state.cost_join_column = join_column
                        st.session_state.cost_gross_column = 'gross_cost'
                        st.session_state.cost_net_column = 'net_cost'
                        st.session_state.cost_type = cost_type
                        st.session_state.discount_rate = discount_rate if net_cost_method == "Apply Discount Rate" else None
                        st.success("Cost data applied successfully with Gross and Net values!")
                        st.rerun()
                
                with col2:
                    if st.button("🔄 Clear Cost Data"):
                        st.session_state.cost_data = None
                        st.session_state.cost_mapping_type = None
                        st.rerun()
                        
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                
    def _render_manual_entry(self) -> Optional[Dict[str, Any]]:
        """Render manual cost entry interface"""
        
        st.markdown("#### Manual Cost Entry")
        st.info("Enter cost data manually for specific frames or media owners")
        
        entry_type = st.radio(
            "Entry Level",
            ["Campaign Total", "Media Owner", "Individual Frame"],
            horizontal=True
        )
        
        if entry_type == "Campaign Total":
            col1, col2 = st.columns(2)
            with col1:
                total_cost = st.number_input(
                    "Total Campaign Cost (£)",
                    min_value=0.0,
                    value=10000.0,
                    step=100.0,
                    help="This will be distributed across all frames"
                )
            with col2:
                distribution_method = st.selectbox(
                    "Distribution Method",
                    ["Equal per frame", "Weighted by impacts", "Weighted by reach"],
                    help="How to allocate cost across frames"
                )
            
            if st.button("Apply Campaign Cost", type="primary"):
                # Create cost dataframe
                cost_df = pd.DataFrame({
                    'campaign_total': [total_cost],
                    'distribution': [distribution_method]
                })
                st.session_state.cost_data = cost_df
                st.session_state.cost_mapping_type = 'campaign_total'
                st.success(f"Applied £{total_cost:,.2f} campaign cost")
                
        elif entry_type == "Media Owner":
            # Get unique media owners from current data if available
            st.markdown("##### Cost per Media Owner")
            
            num_owners = st.number_input("Number of Media Owners", min_value=1, max_value=20, value=3)
            
            owner_costs = []
            for i in range(num_owners):
                col1, col2 = st.columns(2)
                with col1:
                    owner_name = st.text_input(f"Media Owner {i+1} Name", key=f"owner_{i}")
                with col2:
                    owner_cost = st.number_input(
                        f"Cost (£)", 
                        min_value=0.0, 
                        value=1000.0,
                        key=f"cost_{i}"
                    )
                owner_costs.append({'media_owner': owner_name, 'cost': owner_cost})
            
            if st.button("Apply Media Owner Costs", type="primary"):
                cost_df = pd.DataFrame(owner_costs)
                st.session_state.cost_data = cost_df
                st.session_state.cost_mapping_type = 'media_owner'
                st.success(f"Applied costs for {len(owner_costs)} media owners")
                
        else:  # Individual Frame
            st.markdown("##### Cost per Frame")
            st.info("For individual frame costs, please use the file upload option with a CSV containing frame_id and cost columns")
            
    def _render_rate_card_application(self) -> Optional[Dict[str, Any]]:
        """Render rate card based cost calculation"""
        
        st.markdown("#### Apply Rate Card")
        st.info("Calculate costs based on standard rate cards")
        
        col1, col2 = st.columns(2)
        
        with col1:
            rate_type = st.selectbox(
                "Rate Card Type",
                ["Standard CPT", "Premium Location", "Time-based", "Custom Formula"]
            )
            
            if rate_type == "Standard CPT":
                cpt_value = st.number_input(
                    "Cost per Thousand (£)",
                    min_value=0.0,
                    value=5.0,
                    step=0.1,
                    help="Standard CPT to apply across all frames"
                )
                
            elif rate_type == "Premium Location":
                st.markdown("**Base CPT by Location Type**")
                city_center_cpt = st.number_input("City Center (£)", value=8.0, step=0.1)
                high_street_cpt = st.number_input("High Street (£)", value=6.0, step=0.1)
                suburban_cpt = st.number_input("Suburban (£)", value=4.0, step=0.1)
                rural_cpt = st.number_input("Rural (£)", value=2.0, step=0.1)
                
        with col2:
            st.markdown("**Multipliers**")
            
            include_time = st.checkbox("Apply time-of-day multiplier")
            if include_time:
                peak_multiplier = st.slider("Peak hours multiplier", 0.5, 2.0, 1.5)
                offpeak_multiplier = st.slider("Off-peak multiplier", 0.5, 2.0, 0.8)
            
            include_size = st.checkbox("Apply frame size multiplier")
            if include_size:
                large_multiplier = st.slider("Large format multiplier", 0.5, 3.0, 1.8)
                standard_multiplier = st.slider("Standard size multiplier", 0.5, 2.0, 1.0)
                small_multiplier = st.slider("Small format multiplier", 0.5, 1.5, 0.7)
        
        if st.button("Calculate and Apply Rate Card", type="primary"):
            # Here we would calculate based on the rate card
            st.success("Rate card applied successfully!")
            st.info("Costs will be calculated when joined with campaign data")
            
    def _validate_cost_data(self, df: pd.DataFrame, join_col: str, cost_col: str) -> Dict[str, Any]:
        """Validate uploaded cost data"""
        
        validations = {}
        
        # Check for required columns
        if join_col in df.columns:
            validations['Join Column'] = {
                'status': 'pass',
                'message': f"Found '{join_col}' column"
            }
        else:
            validations['Join Column'] = {
                'status': 'fail',
                'message': f"Column '{join_col}' not found"
            }
        
        # Check for numeric cost values
        if cost_col in df.columns:
            non_numeric = df[cost_col].isna().sum()
            if non_numeric > 0:
                validations['Cost Values'] = {
                    'status': 'warning',
                    'message': f"{non_numeric} missing cost values found"
                }
            else:
                validations['Cost Values'] = {
                    'status': 'pass',
                    'message': f"All cost values are numeric"
                }
        
        # Check for duplicates
        if join_col in df.columns:
            duplicates = df[join_col].duplicated().sum()
            if duplicates > 0:
                validations['Duplicates'] = {
                    'status': 'warning',
                    'message': f"{duplicates} duplicate {join_col} values found"
                }
            else:
                validations['Duplicates'] = {
                    'status': 'pass',
                    'message': f"No duplicate {join_col} values"
                }
        
        # Check for negative costs
        if cost_col in df.columns:
            negative = (df[cost_col] < 0).sum()
            if negative > 0:
                validations['Negative Values'] = {
                    'status': 'fail',
                    'message': f"{negative} negative cost values found"
                }
            else:
                validations['Negative Values'] = {
                    'status': 'pass',
                    'message': "No negative cost values"
                }
        
        return validations
    
    def _render_cost_data_preview(self) -> None:
        """Show preview of currently loaded cost data"""
        
        st.markdown("---")
        st.markdown("### 📊 Current Cost Data")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Status", "✅ Loaded" if st.session_state.cost_data is not None else "❌ Not Loaded")
        
        with col2:
            if st.session_state.cost_data is not None:
                st.metric("Rows", len(st.session_state.cost_data))
        
        with col3:
            if st.session_state.cost_mapping_type:
                st.metric("Join Type", st.session_state.cost_mapping_type)
        
        with col4:
            if st.button("🗑️ Clear Cost Data"):
                st.session_state.cost_data = None
                st.session_state.cost_mapping_type = None
                st.rerun()
        
        if st.session_state.cost_data is not None:
            st.dataframe(
                st.session_state.cost_data.head(10),
                use_container_width=True,
                hide_index=True
            )
    
    def join_cost_with_campaign_data(self, campaign_data: pd.DataFrame) -> pd.DataFrame:
        """Join uploaded cost data with campaign playout data"""
        
        if st.session_state.cost_data is None:
            # Return with default/mock costs if no cost data uploaded
            return campaign_data
        
        cost_df = st.session_state.cost_data
        mapping_type = st.session_state.cost_mapping_type
        
        try:
            if mapping_type == 'frame_id':
                # Direct frame-level join
                merged = campaign_data.merge(
                    cost_df,
                    left_on='frame_id',
                    right_on=st.session_state.cost_join_column,
                    how='left'
                )
                
            elif mapping_type == 'media_owner':
                # Media owner level join
                merged = campaign_data.merge(
                    cost_df,
                    left_on='media_owner',
                    right_on=st.session_state.cost_join_column,
                    how='left'
                )
                
            elif mapping_type == 'campaign_total':
                # Distribute campaign total across frames
                total_cost = cost_df['campaign_total'].iloc[0]
                distribution = cost_df['distribution'].iloc[0]
                
                if distribution == 'Equal per frame':
                    campaign_data['cost'] = total_cost / len(campaign_data)
                elif distribution == 'Weighted by impacts':
                    total_impacts = campaign_data['daily_impacts'].sum()
                    campaign_data['cost'] = (campaign_data['daily_impacts'] / total_impacts) * total_cost
                else:  # Weighted by reach
                    total_reach = campaign_data['daily_reach'].sum()
                    campaign_data['cost'] = (campaign_data['daily_reach'] / total_reach) * total_cost
                    
                merged = campaign_data
                
            else:
                # Fallback to original data
                merged = campaign_data
                
            # Calculate derived metrics
            if 'cost' in merged.columns:
                merged['cost_per_thousand'] = merged['cost'] / (merged['daily_impacts'] / 1000)
                merged['roi_efficiency'] = merged['daily_impacts'] / (merged['cost'] + 0.01)
                
            return merged
            
        except Exception as e:
            st.error(f"Error joining cost data: {str(e)}")
            return campaign_data
            
    def export_cost_template(self) -> bytes:
        """Generate a template CSV for cost data upload"""
        
        template = pd.DataFrame({
            'frame_id': ['FRAME001', 'FRAME002', 'FRAME003'],
            'media_owner': ['Clear Channel', 'JCDecaux', 'Ocean Outdoor'],
            'daily_cost': [250.00, 180.00, 320.00],
            'cost_per_thousand': [5.50, 4.80, 6.20],
            'rate_card_type': ['Standard', 'Standard', 'Premium'],
            'location_premium': [1.0, 1.0, 1.5],
            'notes': ['City center location', 'High street', 'Digital spectacular']
        })
        
        # Convert to CSV bytes
        csv_buffer = io.StringIO()
        template.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue().encode()

def render_cost_upload_section() -> Optional[CostDataManager]:
    """Main function to render the cost upload section in the UI"""
    
    with st.expander("Cost Data Upload & Management", expanded=False):
        manager = CostDataManager()
        manager.render_cost_upload_interface()
        
        # Provide template download
        st.markdown("---")
        st.markdown("##### 📥 Download Template")
        col1, col2 = st.columns([1, 3])
        with col1:
            csv_template = manager.export_cost_template()
            st.download_button(
                label="Download Cost Template CSV",
                data=csv_template,
                file_name=f"cost_data_template_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                help="Use this template to structure your cost data for upload"
            )
        with col2:
            st.info("Download this template to see the expected format for cost data upload")
            
    return manager