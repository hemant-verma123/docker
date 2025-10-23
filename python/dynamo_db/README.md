# 🗄️ DynamoDB Admin Panel

A comprehensive phpMyAdmin-style web interface for managing local DynamoDB instances, built with Streamlit.

## ✨ Features

### 📊 Dashboard
- Overview of all tables and records
- Database statistics and metrics
- Connection status monitoring
- Quick access to table information

### 🗂️ Table Management
- **View Tables**: Detailed table information including schema, status, and metadata
- **Create Tables**: Easy table creation with partition and sort keys
- **Delete Tables**: Safe table deletion with confirmation

### 📝 Record Management
- **Browse Records**: Paginated view of table records with customizable page sizes
- **Add Records**: JSON-based record creation with key validation
- **Edit Records**: In-place editing capabilities (framework ready)
- **Delete Records**: Record deletion with key-based selection

### 🔍 Query Interface
- **Scan Operations**: Full table scanning with result display
- **Get Item**: Retrieve specific items by key
- **Query Builder**: Visual query construction (extensible)

### ⚙️ Settings & Configuration
- Connection settings display
- Application preferences
- About information

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Local DynamoDB instance

### Installation

1. **Start DynamoDB Local:**
   ```bash
   docker-compose up -d
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**
   ```bash
   streamlit run main.py
   ```

4. **Access the Interface:**
   Open your browser to `http://localhost:8501`

## 🎨 Interface Overview

The application features a modern, phpMyAdmin-inspired interface with:

- **Sidebar Navigation**: Easy switching between different sections
- **Tabbed Interface**: Organized functionality within each section
- **Responsive Design**: Works on different screen sizes
- **Real-time Updates**: Automatic refresh capabilities
- **Error Handling**: Comprehensive error messages and validation

## 📋 Usage Examples

### Creating a Table
1. Navigate to "🗂️ Tables" → "➕ Create Table"
2. Enter table name (e.g., "users")
3. Set partition key (e.g., "user_id")
4. Optionally add sort key (e.g., "timestamp")
5. Click "Create Table"

### Adding Records
1. Go to "📝 Records" → "➕ Add Record"
2. Select your table
3. Fill in required key fields
4. Add additional fields as JSON: `{"name": "John", "email": "john@example.com"}`
5. Click "Add Record"

### Browsing Data
1. Navigate to "📝 Records" → "📋 Browse"
2. Select your table
3. Choose page size (10, 25, 50, or 100 records)
4. Use pagination controls to navigate through data

## 🔧 Configuration

### DynamoDB Connection
The application connects to DynamoDB Local at:
- **Endpoint**: `http://localhost:8000`
- **Region**: `us-east-1`
- **Credentials**: Dummy values for local development

### Customization
You can modify the connection settings in the `get_dynamodb_resource()` function in `main.py`.

## 🛠️ Technical Details

### Built With
- **Streamlit**: Web application framework
- **Boto3**: AWS SDK for Python
- **Pandas**: Data manipulation and display
- **Docker**: Containerized DynamoDB Local

### Architecture
- **Modular Design**: Separate functions for different operations
- **Error Handling**: Comprehensive exception handling
- **State Management**: Session state for pagination and user preferences
- **Responsive UI**: Mobile-friendly interface

## 📈 Performance Features

- **Pagination**: Efficient handling of large datasets
- **Lazy Loading**: Data loaded on demand
- **Connection Pooling**: Optimized DynamoDB connections
- **Caching**: Session-based caching for better performance

## 🔒 Security Notes

- This application is designed for **local development only**
- No authentication or authorization implemented
- Do not use in production environments without proper security measures

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.