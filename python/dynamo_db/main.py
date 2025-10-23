import streamlit as st
import boto3
from botocore.exceptions import ClientError
import pandas as pd
import json

# ------------------------------
# DynamoDB connection (local)
# ------------------------------
def get_dynamodb_resource():
    return boto3.resource(
        "dynamodb",
        region_name="us-east-1",
        aws_access_key_id="dummy",
        aws_secret_access_key="dummy",
        endpoint_url="http://localhost:8000"
    )

# ------------------------------
# Fetch table list
# ------------------------------
def list_tables(dynamodb):
    try:
        return [table.name for table in dynamodb.tables.all()]
    except ClientError as e:
        st.error(f"Error listing tables: {e}")
        return []

# ------------------------------
# Fetch table items with pagination
# ------------------------------
def fetch_table_items(table, limit=100, last_key=None):
    try:
        scan_kwargs = {'Limit': limit}
        if last_key:
            scan_kwargs['ExclusiveStartKey'] = last_key
        
        data = table.scan(**scan_kwargs)
        return data.get("Items", []), data.get("LastEvaluatedKey")
    except ClientError as e:
        st.error(f"Error scanning table: {e}")
        return [], None

# ------------------------------
# Get table description
# ------------------------------
def get_table_description(dynamodb, table_name):
    try:
        response = dynamodb.meta.client.describe_table(TableName=table_name)
        return response['Table']
    except ClientError as e:
        st.error(f"Error describing table: {e}")
        return None

# ------------------------------
# Create table
# ------------------------------
def create_table(dynamodb, table_name, partition_key, sort_key=None):
    try:
        key_schema = [
            {'AttributeName': partition_key, 'KeyType': 'HASH'}
        ]
        attribute_definitions = [
            {'AttributeName': partition_key, 'AttributeType': 'S'}
        ]
        
        if sort_key:
            key_schema.append({'AttributeName': sort_key, 'KeyType': 'RANGE'})
            attribute_definitions.append({'AttributeName': sort_key, 'AttributeType': 'S'})
        
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            BillingMode='PAY_PER_REQUEST'
        )
        return True
    except ClientError as e:
        st.error(f"Error creating table: {e}")
        return False

# ------------------------------
# Delete table
# ------------------------------
def delete_table(dynamodb, table_name):
    try:
        table = dynamodb.Table(table_name)
        table.delete()
        return True
    except ClientError as e:
        st.error(f"Error deleting table: {e}")
        return False

# ------------------------------
# Add item to table
# ------------------------------
def add_item(table, item):
    try:
        table.put_item(Item=item)
        return True
    except ClientError as e:
        st.error(f"Error adding item: {e}")
        return False

# ------------------------------
# Update item in table
# ------------------------------
def update_item(table, key, update_expression, expression_values):
    try:
        table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
        return True
    except ClientError as e:
        st.error(f"Error updating item: {e}")
        return False

# ------------------------------
# Delete item from table
# ------------------------------
def delete_item(table, key):
    try:
        st.info(f"Attempting to delete item with key: {key}")
        response = table.delete_item(Key=key)
        st.info(f"Delete response: {response}")
        return True
    except ClientError as e:
        st.error(f"Error deleting item: {e}")
        st.error(f"Key used: {key}")
        return False
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return False

# ------------------------------
# Update record in table
# ------------------------------
def update_record(table, original_record, edited_data, key_attrs):
    try:
        # Extract key values from original record
        key_values = {attr: original_record[attr] for attr in key_attrs}
        
        # Build update expression for non-key attributes
        update_expressions = []
        expression_values = {}
        
        for attr, value in edited_data.items():
            if attr not in key_attrs:  # Don't update key attributes
                update_expressions.append(f"#{attr} = :{attr}")
                expression_values[f":{attr}"] = value
                expression_values[f"#{attr}"] = attr
        
        if update_expressions:
            update_expression = "SET " + ", ".join(update_expressions)
            table.update_item(
                Key=key_values,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ExpressionAttributeNames={f"#{attr}": attr for attr in edited_data.keys() if attr not in key_attrs}
            )
        else:
            # If only key attributes, just put the item back
            table.put_item(Item=edited_data)
        
        return True
    except ClientError as e:
        st.error(f"Error updating record: {e}")
        return False

# ------------------------------
# Streamlit UI
# ------------------------------
def main():
    st.set_page_config(
        page_title="DynamoDB Admin - phpMyAdmin Style", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for compact phpMyAdmin-like styling
    st.markdown("""
    <style>
    /* Reduce overall padding and margins */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Compact sidebar */
    .css-1d391kg {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
    
    /* Reduce spacing between elements */
    .stSelectbox > div > div {
        margin-bottom: 0.5rem;
    }
    
    .stButton > button {
        margin-bottom: 0.5rem;
    }
    
    /* Compact headers */
    h1, h2, h3 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Compact tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.25rem 0.5rem;
    }
    
    /* Compact dataframe */
    .stDataFrame {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Reduce column spacing */
    .stColumns > div {
        padding: 0.25rem;
    }
    
    /* Compact form elements */
    .stForm {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Compact expander */
    .streamlit-expanderHeader {
        padding: 0.25rem 0.5rem;
    }
    
    /* Remove excessive margins from info/warning boxes */
    .stAlert {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Compact radio buttons */
    .stRadio > div {
        gap: 0.25rem;
    }
    
    /* Compact sidebar content */
    .css-1lcbmhc .css-1d391kg {
        padding: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

   

    dynamodb = get_dynamodb_resource()

    # Compact sidebar navigation
    with st.sidebar:
        st.markdown("**🧭 Navigation**")
        page = st.radio(
            "Choose a section:",
            ["📊 Dashboard", "🗂️ Tables", "📝 Records", "🔍 Query", "⚙️ Settings"],
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("**📈 Connection**")
        try:
            # Test connection
            list_tables(dynamodb)
            st.success("✅ Connected")
        except Exception:
            st.error("❌ Failed")
    
    # Main content area
    if page == "📊 Dashboard":
        show_dashboard(dynamodb)
    elif page == "🗂️ Tables":
        show_tables_management(dynamodb)
    elif page == "📝 Records":
        show_records_management(dynamodb)
    elif page == "🔍 Query":
        show_query_interface(dynamodb)
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard(dynamodb):
    st.markdown("## 📊 Dashboard")
    
    tables = list_tables(dynamodb)

    # Compact metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tables", len(tables))
    with col2:
        total_items = sum(len(fetch_table_items(dynamodb.Table(name), limit=1)[0]) for name in tables)
        st.metric("Records", total_items)
    with col3:
        st.metric("Size", "Local")
    with col4:
        st.metric("Status", "Active")
    
    # Compact tables list
    st.markdown("**📋 Tables**")
    if tables:
        for table_name in tables:
            with st.expander(f"{table_name}", expanded=False):
                table_info = get_table_description(dynamodb, table_name)
                if table_info:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Status: {table_info['TableStatus']}")
                        st.write(f"Items: {table_info.get('ItemCount', 'N/A')}")
                    with col2:
                        st.write(f"Created: {table_info['CreationDateTime'].strftime('%m/%d %H:%M')}")
                        st.write(f"Mode: {table_info['BillingModeSummary']['BillingMode']}")
    else:
        st.info("No tables found. Create one in Tables section.")

def show_tables_management(dynamodb):
    st.markdown("## 🗂️ Tables Management")
    
    tab1, tab2, tab3 = st.tabs(["View", "Create", "Delete"])
    
    with tab1:
        tables = list_tables(dynamodb)
        if tables:
            selected_table = st.selectbox("Select table:", tables, label_visibility="collapsed")
            if selected_table:
                table_info = get_table_description(dynamodb, selected_table)
                if table_info:
                    st.markdown(f"**{selected_table}**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Status: {table_info['TableStatus']}")
                        st.write(f"Items: {table_info.get('ItemCount', 'N/A')}")
                        st.write(f"Size: {table_info.get('TableSizeBytes', 0)} bytes")
                    with col2:
                        st.write("**Keys:**")
                        for key in table_info['KeySchema']:
                            st.write(f"  {key['KeyType']}: {key['AttributeName']}")
                        st.write("**Attributes:**")
                        for attr in table_info['AttributeDefinitions']:
                            st.write(f"  {attr['AttributeName']}: {attr['AttributeType']}")
        else:
            st.info("No tables found.")
    
    with tab2:
        st.markdown("**Create Table**")
        with st.form("create_table_form"):
            col1, col2 = st.columns(2)
            with col1:
                table_name = st.text_input("Name", placeholder="my_table")
            with col2:
                partition_key = st.text_input("Partition Key", placeholder="id")
            sort_key = st.text_input("Sort Key (optional)", placeholder="timestamp")
            
            if st.form_submit_button("Create"):
                if table_name and partition_key:
                    if create_table(dynamodb, table_name, partition_key, sort_key if sort_key else None):
                        st.success(f"Created '{table_name}'!")
                        st.rerun()
                else:
                    st.error("Name and partition key required.")
    
    with tab3:
        st.markdown("**Delete Table**")
        tables = list_tables(dynamodb)
        if tables:
            table_to_delete = st.selectbox("Select table:", tables, label_visibility="collapsed")
            if st.button("Delete", type="secondary"):
                if delete_table(dynamodb, table_to_delete):
                    st.success(f"Deleted '{table_to_delete}'!")
                    st.rerun()
        else:
            st.info("No tables to delete.")

def show_records_management(dynamodb):
    st.markdown("## 📝 Records Management")
    
    tables = list_tables(dynamodb)
    if not tables:
        st.info("No tables found. Create a table first.")
        return
    
    selected_table = st.selectbox("Select table:", tables, label_visibility="collapsed")
    if not selected_table:
        return

    table = dynamodb.Table(selected_table)
    table_info = get_table_description(dynamodb, selected_table)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Browse", "Add", "Edit", "Delete"])
    
    with tab1:
        st.markdown(f"**{selected_table} Records**")
        
        # Compact controls
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            page_size = st.selectbox("Page size:", [10, 25, 50, 100], index=1, label_visibility="collapsed")
        with col2:
            if st.button("🔄", help="Refresh"):
                st.rerun()
        
        # Fetch and display records
        if 'last_key' not in st.session_state:
            st.session_state.last_key = None
        
        items, last_key = fetch_table_items(table, limit=page_size, last_key=st.session_state.last_key)

        if items:
            df = pd.DataFrame(items)
            
            # Add selection column for edit/delete
            if 'selected_record' not in st.session_state:
                st.session_state.selected_record = None
            
            # Display records with selection
            st.markdown("**Select a record to edit/delete:**")
            for idx, item in enumerate(items):
                col1, col2, col3 = st.columns([1, 8, 1])
                with col1:
                    if st.button("📝", key=f"edit_{idx}", help="Edit this record"):
                        st.session_state.selected_record = item
                        st.rerun()
                with col2:
                    # Display key information for identification
                    key_info = []
                    for key in table_info['KeySchema']:
                        key_info.append(f"{key['AttributeName']}: {item.get(key['AttributeName'], 'N/A')}")
                    st.write(" | ".join(key_info))
                with col3:
                    if st.button("🗑️", key=f"delete_{idx}", help="Delete this record"):
                        st.session_state.record_to_delete = item
                        st.session_state.selected_record = None  # Clear edit selection
                        st.rerun()
            
            # Show selected record details
            if st.session_state.selected_record:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("**Selected Record:**")
                    st.json(st.session_state.selected_record)
                with col2:
                    if st.button("❌ Clear Selection"):
                        st.session_state.selected_record = None
                        st.rerun()
            
            # Compact pagination
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.session_state.last_key and st.button("⬅️"):
                    st.session_state.last_key = None
                    st.rerun()
            with col3:
                if last_key and st.button("➡️"):
                    st.session_state.last_key = last_key
                    st.rerun()
        else:
            st.info("No records found.")
    
    with tab2:
        st.markdown("**Add Record**")
        if table_info:
            key_attrs = [key['AttributeName'] for key in table_info['KeySchema']]
            
            with st.form("add_record_form"):
                st.write("**Keys:**")
                record_data = {}
                for attr in key_attrs:
                    record_data[attr] = st.text_input(f"{attr}", key=f"add_{attr}")
                
                st.write("**Additional Fields:**")
                additional_fields = st.text_area("JSON:", placeholder='{"name": "John", "age": 30}', height=100)
                
                if st.form_submit_button("Add"):
                    try:
                        if additional_fields:
                            additional_data = json.loads(additional_fields)
                            record_data.update(additional_data)
                        
                        if add_item(table, record_data):
                            st.success("Record added!")
                            st.rerun()
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format.")
    
    with tab3:
        st.markdown("**Edit Record**")
        
        if st.session_state.selected_record:
            st.markdown("**Editing Record:**")
            st.json(st.session_state.selected_record)
            
            with st.form("edit_record_form"):
                st.write("**Edit Fields:**")
                
                # Get the key attributes for this record
                key_attrs = [key['AttributeName'] for key in table_info['KeySchema']]
                
                # Create editable fields for all attributes
                edited_data = {}
                for attr, value in st.session_state.selected_record.items():
                    if attr in key_attrs:
                        # Keys are read-only
                        st.text_input(f"{attr} (Key - Read Only)", value=str(value), disabled=True)
                        edited_data[attr] = value
                    else:
                        # Non-key attributes can be edited
                        if isinstance(value, (dict, list)):
                            # For complex types, use JSON input
                            json_str = st.text_area(f"{attr} (JSON)", value=json.dumps(value, indent=2), height=100)
                            try:
                                edited_data[attr] = json.loads(json_str)
                            except json.JSONDecodeError:
                                st.error(f"Invalid JSON for {attr}")
                                edited_data[attr] = value
                        else:
                            # For simple types, use text input
                            edited_data[attr] = st.text_input(f"{attr}", value=str(value))
                
                # Add new field option
                st.write("**Add New Field:**")
                new_field_name = st.text_input("Field Name", placeholder="new_field")
                new_field_value = st.text_input("Field Value", placeholder="value")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Save Changes"):
                        # Add new field if specified
                        if new_field_name and new_field_value:
                            try:
                                # Try to parse as JSON first
                                edited_data[new_field_name] = json.loads(new_field_value)
                            except json.JSONDecodeError:
                                # If not JSON, store as string
                                edited_data[new_field_name] = new_field_value
                        
                        # Update the record
                        if update_record(table, st.session_state.selected_record, edited_data, key_attrs):
                            st.success("Record updated successfully!")
                            st.session_state.selected_record = None
                            st.rerun()
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.selected_record = None
                        st.rerun()
        else:
            st.info("Select a record from Browse tab to edit.")
    
    with tab4:
        st.markdown("**Delete Record**")
        
        # Initialize session state if not exists
        if 'record_to_delete' not in st.session_state:
            st.session_state.record_to_delete = None
        
        # Handle delete confirmation
        if st.session_state.record_to_delete:
            record_to_delete = st.session_state.record_to_delete
            
            st.warning("⚠️ **Confirm Deletion**")
            st.markdown("**Record to delete:**")
            st.json(record_to_delete)
            
            # Show key information
            if table_info and 'KeySchema' in table_info:
                st.markdown("**Key Information:**")
                key_info = []
                for key in table_info['KeySchema']:
                    key_info.append(f"{key['KeyType']}: {key['AttributeName']} = {record_to_delete.get(key['AttributeName'], 'N/A')}")
                st.write(" | ".join(key_info))
            else:
                st.error("Table information not available")
                return
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Confirm Delete", type="primary"):
                    # Extract key values for deletion
                    key_values = {}
                    for key in table_info['KeySchema']:
                        attr_name = key['AttributeName']
                        if attr_name in record_to_delete:
                            key_values[attr_name] = record_to_delete[attr_name]
                        else:
                            st.error(f"Missing key attribute: {attr_name}")
                            return
                    
                    st.info(f"Deleting with key: {key_values}")
                    
                    if delete_item(table, key_values):
                        st.success("Record deleted successfully!")
                        st.session_state.record_to_delete = None
                        st.session_state.selected_record = None
                        st.rerun()
            
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state.record_to_delete = None
                    st.rerun()
        
        elif st.session_state.selected_record:
            st.info("Selected record for deletion:")
            st.json(st.session_state.selected_record)
            
            if st.button("🗑️ Delete Selected Record"):
                st.session_state.record_to_delete = st.session_state.selected_record
                st.rerun()
        else:
            st.info("Select a record from Browse tab to delete.")
            
            # Debug information
            st.markdown("**Debug Info:**")
            st.write(f"Selected table: {selected_table}")
            st.write(f"Table info available: {table_info is not None}")
            if table_info:
                st.write(f"Key schema: {table_info.get('KeySchema', 'N/A')}")
            st.write(f"Session state record_to_delete: {st.session_state.get('record_to_delete', 'None')}")
            st.write(f"Session state selected_record: {st.session_state.get('selected_record', 'None')}")

def show_query_interface(dynamodb):
    st.markdown("## 🔍 Query Interface")
    st.info("Simplified query interface. Use AWS CLI/SDK for complex queries.")
    
    tables = list_tables(dynamodb)
    if not tables:
        st.info("No tables found.")
        return
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_table = st.selectbox("Table:", tables, label_visibility="collapsed")
    with col2:
        query_type = st.selectbox("Type:", ["Scan", "Get Item"], label_visibility="collapsed")
    
    if query_type == "Scan":
        st.markdown("**Scan Table**")
        if st.button("Execute Scan"):
            table = dynamodb.Table(selected_table)
            items, _ = fetch_table_items(table, limit=50)
            if items:
                df = pd.DataFrame(items)
                st.dataframe(df, use_container_width=True, height=400)
            else:
                st.info("No items found.")
    
    elif query_type == "Get Item":
        st.markdown("**Get Item**")
        table_info = get_table_description(dynamodb, selected_table)
        if table_info:
            key_attrs = [key['AttributeName'] for key in table_info['KeySchema']]
            
            with st.form("get_item_form"):
                st.write("Key values:")
                key_values = {}
                for attr in key_attrs:
                    key_values[attr] = st.text_input(f"{attr}", key=f"get_{attr}")
                
                if st.form_submit_button("Get Item"):
                    try:
                        table = dynamodb.Table(selected_table)
                        response = table.get_item(Key=key_values)
                        if 'Item' in response:
                            st.json(response['Item'])
                        else:
                            st.info("Item not found.")
                    except ClientError as e:
                        st.error(f"Error: {e}")

def show_settings():
    st.markdown("## ⚙️ Settings")
    st.markdown("**Connection**")
    st.info("Connected to local DynamoDB at http://localhost:8000")
    
    st.markdown("**App Settings**")
    st.checkbox("Auto-refresh tables", value=True)
    st.selectbox("Default page size", [10, 25, 50, 100], index=1)
    
    st.markdown("**About**")
    st.write("DynamoDB Admin Panel v1.0")
    st.write("Built with Streamlit and boto3")

if __name__ == "__main__":
    main()
