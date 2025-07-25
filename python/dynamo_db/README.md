# DynamoDB Local Client

A comprehensive Python client for connecting to local DynamoDB instances with support for LocalStack and standalone DynamoDB Local.

## Features

- ✅ Connect to LocalStack DynamoDB (port 4566)
- ✅ Connect to standalone DynamoDB Local (port 8083)
- ✅ Connect to AWS DynamoDB (with proper credentials)
- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Table management (create, delete, list)
- ✅ Data import/export with pandas DataFrames
- ✅ Comprehensive error handling and logging
- ✅ Pylint compliant code
- ✅ Type hints and documentation

## Prerequisites

1. **Docker Compose Setup**: Make sure your DynamoDB services are running:
   ```bash
   cd infra
   docker-compose up -d dynamodb-local dynamodb-admin
   ```

2. **Python Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### 1. Basic Usage

```python
from dynamodb_client import DynamoDBClient, DynamoDBConfig

# Configure connection
config = DynamoDBConfig(
    endpoint_url="http://localhost:8083",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

# Initialize client
client = DynamoDBClient(config)

# List tables
tables = client.list_tables()
print(f"Tables: {tables}")
```

### 2. Run the Example

```bash
python example.py
```

### 3. Run the Main Script

```bash
python dynamodb_client.py
```

## Configuration Options

The script supports multiple DynamoDB configurations:

### LocalStack DynamoDB
```python
config = DynamoDBConfig(
    endpoint_url="http://localhost:4566",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)
```

### DynamoDB Local
```python
config = DynamoDBConfig(
    endpoint_url="http://localhost:8083",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)
```

### AWS DynamoDB
```python
config = DynamoDBConfig(
    endpoint_url="https://dynamodb.us-east-1.amazonaws.com",
    region_name="us-east-1",
    aws_access_key_id="your_access_key",
    aws_secret_access_key="your_secret_key"
)
```

## API Reference

### Table Operations

#### Create Table
```python
key_schema = [
    {'AttributeName': 'id', 'KeyType': 'HASH'}
]
attribute_definitions = [
    {'AttributeName': 'id', 'AttributeType': 'S'}
]
client.create_table("my_table", key_schema, attribute_definitions)
```

#### List Tables
```python
tables = client.list_tables()
```

#### Delete Table
```python
client.delete_table("my_table")
```

### Data Operations

#### Insert Item
```python
item = {
    'id': {'S': 'user001'},
    'name': {'S': 'John Doe'},
    'age': {'N': '30'}
}
client.put_item("users", item)
```

#### Get Item
```python
key = {'id': {'S': 'user001'}}
item = client.get_item("users", key)
```

#### Update Item
```python
key = {'id': {'S': 'user001'}}
update_expression = "SET age = :age"
expression_values = {':age': {'N': '31'}}
client.update_item("users", key, update_expression, expression_values)
```

#### Delete Item
```python
key = {'id': {'S': 'user001'}}
client.delete_item("users", key)
```

#### Scan Table
```python
# Get all items
items = client.scan_table("users")

# With filter
items = client.scan_table(
    "users",
    filter_expression="age > :age",
    expression_attribute_values={':age': {'N': '25'}}
)
```

#### Query Items
```python
items = client.query_items(
    "users",
    key_condition_expression="id = :id",
    expression_attribute_values={':id': {'S': 'user001'}}
)
```

### Data Import/Export

#### Export to DataFrame
```python
df = client.export_to_dataframe("users")
print(df.head())
```

#### Import from DataFrame
```python
import pandas as pd

df = pd.DataFrame({
    'id': ['user001', 'user002'],
    'name': ['John', 'Jane'],
    'age': [30, 25]
})

client.import_from_dataframe("users", df)
```

## Error Handling

The client includes comprehensive error handling:

```python
try:
    client = DynamoDBClient(config)
    # Your operations here
except ConnectionError as e:
    print(f"Connection failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Logging

The client uses Python's logging module. Configure logging level:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Development

### Code Quality

The code is designed to pass pylint with high standards:

```bash
pylint dynamodb_client.py
```

### Testing

Run the example script to test functionality:

```bash
python example.py
```

## Troubleshooting

### Connection Issues

1. **Check if DynamoDB is running**:
   ```bash
   docker ps | grep dynamodb
   ```

2. **Verify port accessibility**:
   ```bash
   curl http://localhost:8083
   ```

3. **Check Docker Compose logs**:
   ```bash
   docker-compose logs dynamodb-local
   ```

### Common Errors

- **Connection refused**: DynamoDB service not running
- **Table not found**: Table doesn't exist or wrong name
- **Validation error**: Invalid item format or key schema

## Ports Used

- **DynamoDB Local**: 8083 (external) → 8000 (internal)
- **DynamoDB Admin UI**: 8002 (external) → 8001 (internal)
- **LocalStack**: 4566 (if using LocalStack)

## Contributing

1. Follow the existing code style
2. Add type hints to all functions
3. Include comprehensive docstrings
4. Ensure pylint compliance
5. Add tests for new features

## License

This project is part of the Docker infrastructure setup. 