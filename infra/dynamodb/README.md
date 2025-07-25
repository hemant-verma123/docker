# 🚀 DynamoDB Local Setup & Usage Guide

## 📋 Overview

This setup provides a local DynamoDB environment using:
- **DynamoDB Local**: AWS DynamoDB emulator running on port 8083
- **DynamoDB Admin**: Web-based management interface on port 8002

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **DynamoDB Local** | http://localhost:8083 | API endpoint for applications |
| **DynamoDB Admin** | http://localhost:8002 | Web interface for management |

## 🔧 Quick Start

### Start DynamoDB Services
```bash
cd infra
docker-compose up -d dynamodb-local dynamodb-admin
```

### Check Status
```bash
# Check if DynamoDB Local is running
aws dynamodb list-tables --endpoint-url http://localhost:8083 --profile local

# Check if DynamoDB Admin is accessible
curl http://localhost:8002
```

## 🖥️ AWS CLI Configuration

### Setup AWS Profile for Local DynamoDB
```bash
# Configure AWS CLI for local DynamoDB
aws configure set aws_access_key_id test --profile local
aws configure set aws_secret_access_key test --profile local
aws configure set region us-east-1 --profile local
```

### Basic AWS CLI Commands
```bash
# List all tables
aws dynamodb list-tables --endpoint-url http://localhost:8083 --profile local

# Create a table
aws dynamodb create-table \
    --table-name Users \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --endpoint-url http://localhost:8083 \
    --profile local

# Put an item
aws dynamodb put-item \
    --table-name Users \
    --item '{"id":{"S":"user1"},"name":{"S":"John Doe"},"email":{"S":"john@example.com"}}' \
    --endpoint-url http://localhost:8083 \
    --profile local

# Get an item
aws dynamodb get-item \
    --table-name Users \
    --key '{"id":{"S":"user1"}}' \
    --endpoint-url http://localhost:8083 \
    --profile local

# Query items
aws dynamodb query \
    --table-name Users \
    --key-condition-expression "id = :id" \
    --expression-attribute-values '{":id":{"S":"user1"}}' \
    --endpoint-url http://localhost:8083 \
    --profile local
```

## 💻 Programming Language Examples

### Python (boto3)

```python
import boto3
from botocore.config import Config

# Configure DynamoDB client for local endpoint
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:8083',
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    config=Config(
        retries={'max_attempts': 0},
        read_timeout=5,
        connect_timeout=5
    )
)

# Create a table
table = dynamodb.create_table(
    TableName='Users',
    KeySchema=[
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait for table to be created
table.meta.client.get_waiter('table_exists').wait(TableName='Users')

# Put an item
table.put_item(
    Item={
        'id': 'user1',
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 30
    }
)

# Get an item
response = table.get_item(Key={'id': 'user1'})
item = response['Item']
print(item)

# Query items
response = table.query(
    KeyConditionExpression=boto3.dynamodb.conditions.Key('id').eq('user1')
)
items = response['Items']
print(items)
```

### Node.js (AWS SDK v3)

```javascript
const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, PutCommand, GetCommand, QueryCommand } = require('@aws-sdk/lib-dynamodb');

// Configure DynamoDB client for local endpoint
const client = new DynamoDBClient({
    endpoint: 'http://localhost:8083',
    region: 'us-east-1',
    credentials: {
        accessKeyId: 'test',
        secretAccessKey: 'test'
    }
});

const docClient = DynamoDBDocumentClient.from(client);

// Put an item
async function putItem() {
    const command = new PutCommand({
        TableName: 'Users',
        Item: {
            id: 'user1',
            name: 'John Doe',
            email: 'john@example.com',
            age: 30
        }
    });
    
    try {
        await docClient.send(command);
        console.log('Item added successfully');
    } catch (error) {
        console.error('Error:', error);
    }
}

// Get an item
async function getItem() {
    const command = new GetCommand({
        TableName: 'Users',
        Key: { id: 'user1' }
    });
    
    try {
        const response = await docClient.send(command);
        console.log('Item:', response.Item);
    } catch (error) {
        console.error('Error:', error);
    }
}

// Query items
async function queryItems() {
    const command = new QueryCommand({
        TableName: 'Users',
        KeyConditionExpression: 'id = :id',
        ExpressionAttributeValues: {
            ':id': 'user1'
        }
    });
    
    try {
        const response = await docClient.send(command);
        console.log('Items:', response.Items);
    } catch (error) {
        console.error('Error:', error);
    }
}

// Run examples
putItem();
getItem();
queryItems();
```

### Java (AWS SDK v2)

```java
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.*;

import java.net.URI;

public class DynamoDBLocalExample {
    public static void main(String[] args) {
        // Configure DynamoDB client for local endpoint
        DynamoDbClient client = DynamoDbClient.builder()
            .endpointOverride(URI.create("http://localhost:8083"))
            .region(Region.US_EAST_1)
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create("test", "test")
            ))
            .build();

        try {
            // Put an item
            PutItemRequest putRequest = PutItemRequest.builder()
                .tableName("Users")
                .item(Map.of(
                    "id", AttributeValue.builder().s("user1").build(),
                    "name", AttributeValue.builder().s("John Doe").build(),
                    "email", AttributeValue.builder().s("john@example.com").build(),
                    "age", AttributeValue.builder().n("30").build()
                ))
                .build();
            
            client.putItem(putRequest);
            System.out.println("Item added successfully");

            // Get an item
            GetItemRequest getRequest = GetItemRequest.builder()
                .tableName("Users")
                .key(Map.of("id", AttributeValue.builder().s("user1").build()))
                .build();
            
            GetItemResponse response = client.getItem(getRequest);
            System.out.println("Item: " + response.item());

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        } finally {
            client.close();
        }
    }
}
```

### Go (AWS SDK v2)

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/aws/aws-sdk-go-v2/aws"
    "github.com/aws/aws-sdk-go-v2/config"
    "github.com/aws/aws-sdk-go-v2/credentials"
    "github.com/aws/aws-sdk-go-v2/service/dynamodb"
    "github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
)

func main() {
    // Configure DynamoDB client for local endpoint
    customResolver := aws.EndpointResolverWithOptionsFunc(func(service, region string, options ...interface{}) (aws.Endpoint, error) {
        return aws.Endpoint{
            PartitionID:   "aws",
            URL:           "http://localhost:8083",
            SigningRegion: "us-east-1",
        }, nil
    })

    cfg, err := config.LoadDefaultConfig(context.TODO(),
        config.WithEndpointResolverWithOptions(customResolver),
        config.WithCredentialsProvider(credentials.StaticCredentialsProvider{
            Value: aws.Credentials{
                AccessKeyID: "test", SecretAccessKey: "test",
            },
        }),
        config.WithRegion("us-east-1"),
    )
    if err != nil {
        log.Fatal(err)
    }

    client := dynamodb.NewFromConfig(cfg)

    // Put an item
    _, err = client.PutItem(context.TODO(), &dynamodb.PutItemInput{
        TableName: aws.String("Users"),
        Item: map[string]types.AttributeValue{
            "id":    &types.AttributeValueMemberS{Value: "user1"},
            "name":  &types.AttributeValueMemberS{Value: "John Doe"},
            "email": &types.AttributeValueMemberS{Value: "john@example.com"},
            "age":   &types.AttributeValueMemberN{Value: "30"},
        },
    })
    if err != nil {
        log.Printf("Error putting item: %v", err)
        return
    }
    fmt.Println("Item added successfully")

    // Get an item
    result, err := client.GetItem(context.TODO(), &dynamodb.GetItemInput{
        TableName: aws.String("Users"),
        Key: map[string]types.AttributeValue{
            "id": &types.AttributeValueMemberS{Value: "user1"},
        },
    })
    if err != nil {
        log.Printf("Error getting item: %v", err)
        return
    }
    fmt.Printf("Item: %+v\n", result.Item)
}
```

## 🔧 Environment Variables

For applications, you can set these environment variables:

```bash
# For AWS CLI
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
export DYNAMODB_ENDPOINT=http://localhost:8083

# For applications
export DYNAMODB_LOCAL_ENDPOINT=http://localhost:8083
export DYNAMODB_LOCAL_REGION=us-east-1
```

## 🛠️ Web Interface Usage

### Access DynamoDB Admin
1. Open browser: http://localhost:8002
2. Features available:
   - Create/Delete tables
   - Browse and edit data
   - Run queries
   - Import/Export data
   - Dark/Light theme toggle

### Common Operations via Web Interface
1. **Create Table**: Click "Create table" button
2. **Add Items**: Navigate to table → "Add item"
3. **Query Data**: Use the query interface
4. **Delete Items**: Select items → Delete
5. **Export Data**: Use the export functionality

## 📊 Monitoring & Debugging

### Check Service Status
```bash
# Check if DynamoDB Local is running
docker ps | grep dynamodb

# Check logs
docker logs dynamodb-local

# Check DynamoDB Admin logs
docker logs dynamodb-admin
```

### Health Check
```bash
# Test DynamoDB Local API
curl -X POST http://localhost:8083 \
  -H "Content-Type: application/x-amz-json-1.0" \
  -d '{"TableNames":[]}'

# Test DynamoDB Admin
curl http://localhost:8002
```

## 🚨 Troubleshooting

### Common Issues

1. **Connection Refused**
   ```bash
   # Check if port is in use
   netstat -tlnp | grep 8083
   
   # Restart services
   docker-compose restart dynamodb-local dynamodb-admin
   ```

2. **Authentication Errors**
   ```bash
   # Ensure AWS credentials are set
   aws configure list --profile local
   ```

3. **Table Not Found**
   ```bash
   # List all tables
   aws dynamodb list-tables --endpoint-url http://localhost:8083 --profile local
   ```

### Reset DynamoDB Data
```bash
# Stop services
docker-compose stop dynamodb-local dynamodb-admin

# Remove volume data
docker volume rm infra_dynamodb_data

# Restart services
docker-compose up -d dynamodb-local dynamodb-admin
```

## 📝 Notes

- **Data Persistence**: Data is stored in Docker volume `infra_dynamodb_data`
- **Performance**: Local DynamoDB is slower than AWS DynamoDB
- **Limitations**: Some advanced features may not be available
- **Security**: No encryption at rest (local development only)
- **Scaling**: Single instance, no auto-scaling

## 🔗 Related Services

- **LocalStack**: Full AWS emulator (includes DynamoDB)
- **DynamoDB Admin**: Web interface for management
- **AWS CLI**: Command-line interface

## 📚 Additional Resources

- [DynamoDB Local Documentation](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)
- [DynamoDB Admin GitHub](https://github.com/aaronshaf/dynamodb-admin)
- [AWS DynamoDB Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/)
