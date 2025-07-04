import streamlit as st
import boto3
from botocore.exceptions import ClientError
import os

# -----------------------------------------------
# 🧠 GLOBAL STATE MANAGEMENT
# -----------------------------------------------

if "current_prefix" not in st.session_state:
    st.session_state.current_prefix = ""

if "selected_bucket" not in st.session_state:
    st.session_state.selected_bucket = None

# -----------------------------------------------
# 📡 Endpoint Config
# -----------------------------------------------

ENDPOINTS = {
    "LocalStack": {
        "endpoint_url": "http://localhost:4566",
        "aws_access_key_id": "test",
        "aws_secret_access_key": "test",
        "region_name": "us-east-1",
    },
    "MinIO": {
        "endpoint_url": "http://localhost:9000",
        "aws_access_key_id": "admin",
        "aws_secret_access_key": "admin123",
        "region_name": "us-east-1",
    },
    "AWS (default creds)": {
        "endpoint_url": None,
        "aws_access_key_id": None,
        "aws_secret_access_key": None,
        "region_name": "us-east-1",
    }
}

# -----------------------------------------------
# 🧰 Utility Functions
# -----------------------------------------------

def get_s3_client(config):
    return boto3.client(
        "s3",
        endpoint_url=config["endpoint_url"],
        aws_access_key_id=config["aws_access_key_id"],
        aws_secret_access_key=config["aws_secret_access_key"],
        region_name=config["region_name"],
    )

def list_buckets(s3):
    return [b["Name"] for b in s3.list_buckets()["Buckets"]]

def create_bucket(s3, name):
    try:
        s3.create_bucket(Bucket=name)
        st.success(f"Bucket '{name}' created")
    except ClientError as e:
        st.error(f"Error: {e}")

def delete_bucket(s3, name):
    try:
        s3.delete_bucket(Bucket=name)
        st.success(f"Bucket '{name}' deleted")
    except ClientError as e:
        st.error(f"Error: {e}")

def list_objects(s3, bucket, prefix):
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter="/")
        folders = response.get("CommonPrefixes", [])
        objects = response.get("Contents", [])
        return folders, objects
    except ClientError as e:
        st.error(f"Error: {e}")
        return [], []

def upload_files(s3, bucket, prefix, files):
    for f in files:
        key = os.path.join(prefix, f.name).replace("\\", "/")
        s3.upload_fileobj(f, bucket, key)
        st.success(f"Uploaded: {key}")

def delete_object(s3, bucket, key):
    try:
        s3.delete_object(Bucket=bucket, Key=key)
        st.success(f"Deleted: {key}")
    except ClientError as e:
        st.error(f"Error: {e}")

def generate_presigned_url(s3, bucket, key):
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=3600
        )
        return url
    except ClientError as e:
        st.error(f"Error: {e}")
        return None

# -----------------------------------------------
# 🖼️ Streamlit UI
# -----------------------------------------------

st.set_page_config(page_title="🗂️ S3 Explorer", layout="wide")
st.title("🗂️ S3 File Manager")

# Endpoint selector
endpoint_choice = st.sidebar.selectbox("🔌 Select Endpoint", list(ENDPOINTS.keys()))
config = ENDPOINTS[endpoint_choice]
s3 = get_s3_client(config)

# Bucket selection & management
st.sidebar.header("🪣 Buckets")

try:
    bucket_list = list_buckets(s3)
except Exception as e:
    st.error(f"Connection error: {e}")
    st.stop()

selected_bucket = st.sidebar.selectbox("Select Bucket", bucket_list)
st.session_state.selected_bucket = selected_bucket

# Create bucket
with st.sidebar.form("create_bucket_form"):
    new_bucket = st.text_input("New bucket name")
    submitted = st.form_submit_button("➕ Create Bucket")
    if submitted and new_bucket:
        create_bucket(s3, new_bucket)

# Delete bucket
if st.sidebar.button("❌ Delete Selected Bucket"):
    delete_bucket(s3, selected_bucket)

# -----------------------------------------------
# 📁 Folder Navigation
# -----------------------------------------------

prefix = st.session_state.current_prefix
st.subheader(f"📂 `{prefix or '/'} ` in `{selected_bucket}`")

if prefix:
    if st.button("🔙 Go Up"):
        st.session_state.current_prefix = "/".join(prefix.strip("/").split("/")[:-1]) + "/"

# Upload files
uploaded_files = st.file_uploader("📤 Upload Files", accept_multiple_files=True, type=None)
if uploaded_files:
    upload_files(s3, selected_bucket, prefix, uploaded_files)

# List folders & files
folders, objects = list_objects(s3, selected_bucket, prefix)

if folders:
    st.markdown("### 📁 Folders")
    for f in folders:
        folder_name = f["Prefix"].replace(prefix, "").strip("/")
        if st.button(f"📂 {folder_name}", key=f["Prefix"]):
            st.session_state.current_prefix = f["Prefix"]

if objects:
    st.markdown("### 📄 Files")
    for obj in objects:
        key = obj["Key"]
        if key.endswith("/"):
            continue  # skip folders
        file_name = key.replace(prefix, "")
        col1, col2, col3 = st.columns([5, 2, 1])
        col1.markdown(f"`{file_name}`")
        with col2:
            url = generate_presigned_url(s3, selected_bucket, key)
            if url:
                st.markdown(f"[⬇️ Download]({url})", unsafe_allow_html=True)
        with col3:
            if st.button("🗑️", key=f"del_{key}"):
                delete_object(s3, selected_bucket, key)

elif not folders:
    st.info("This folder is empty.")
