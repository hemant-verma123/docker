#!/usr/bin/env python3
"""
Script to generate infra.xlsx with all services from docker-compose.yml
"""

import yaml
import pandas as pd
from datetime import datetime

def parse_docker_compose():
    """Parse docker-compose.yml and extract service information"""
    
    services_data = [
        {
            "service": "localstack",
            "port": "4566",
            "browser_url": "http://localhost:4566",
            "terminal": "aws --endpoint-url=http://localhost:4566 s3 ls",
            "remark": "AWS services emulator - S3, DynamoDB, Lambda, etc."
        },
        {
            "service": "minio-ui",
            "port": "9006",
            "browser_url": "http://localhost:9006",
            "terminal": "N/A",
            "remark": "MinIO Console UI - S3-compatible object storage interface"
        },
        {
            "service": "minio",
            "port": "9000",
            "browser_url": "http://localhost:9000",
            "terminal": "mc alias set myminio http://localhost:9000 minio minio123",
            "remark": "MinIO Server - S3-compatible object storage"
        },
        {
            "service": "dynamodb-local",
            "port": "8083",
            "browser_url": "N/A",
            "terminal": "aws dynamodb list-tables --endpoint-url http://localhost:8083",
            "remark": "DynamoDB Local - AWS DynamoDB emulator"
        },
        {
            "service": "dynamodb-admin",
            "port": "8002",
            "browser_url": "http://localhost:8002",
            "terminal": "N/A",
            "remark": "DynamoDB Admin - Web-based DynamoDB management interface"
        },
        {
            "service": "mysql",
            "port": "3307",
            "browser_url": "N/A",
            "terminal": "mysql -h localhost -P 3307 -u root -p080589",
            "remark": "MySQL Database - For PHP applications"
        },
        {
            "service": "phpmyadmin",
            "port": "8004",
            "browser_url": "http://localhost:8004",
            "terminal": "N/A",
            "remark": "phpMyAdmin - MySQL database management interface"
        },
        {
            "service": "sonarqube",
            "port": "9005",
            "browser_url": "http://localhost:9005",
            "terminal": "N/A",
            "remark": "SonarQube - Code quality and security analysis"
        },
        {
            "service": "postgres",
            "port": "5432",
            "browser_url": "N/A",
            "terminal": "psql -h localhost -p 5432 -U postgres -d sonar",
            "remark": "PostgreSQL - Database for SonarQube"
        },
        {
            "service": "www",
            "port": "8003",
            "browser_url": "http://localhost:8003",
            "terminal": "curl http://localhost:8003",
            "remark": "PHP7 Application - Web application with Apache"
        },
        {
            "service": "prometheus",
            "port": "9090",
            "browser_url": "http://localhost:9090",
            "terminal": "curl http://localhost:9090/api/v1/status/targets",
            "remark": "Prometheus - Metrics collection and monitoring"
        },
        {
            "service": "alertmanager",
            "port": "9093",
            "browser_url": "http://localhost:9093",
            "terminal": "curl http://localhost:9093/api/v1/status",
            "remark": "AlertManager - Alert management for Prometheus"
        },
        {
            "service": "promlens",
            "port": "8080",
            "browser_url": "http://localhost:8080",
            "terminal": "N/A",
            "remark": "PromLens - PromQL query builder and visualizer"
        },
        {
            "service": "elasticsearch",
            "port": "9200",
            "browser_url": "http://localhost:9200",
            "terminal": "curl http://localhost:9200/_cluster/health",
            "remark": "Elasticsearch - Search and analytics engine"
        },
        {
            "service": "logstash",
            "port": "N/A",
            "browser_url": "N/A",
            "terminal": "docker logs logstash",
            "remark": "Logstash - Data processing pipeline (internal service)"
        },
        {
            "service": "kibana",
            "port": "5601",
            "browser_url": "http://localhost:5601",
            "terminal": "curl http://localhost:5601/api/status",
            "remark": "Kibana - Data visualization and management"
        }
    ]
    
    return services_data

def create_excel_file():
    """Create Excel file with service information"""
    
    # Get services data
    services = parse_docker_compose()
    
    # Create DataFrame
    df = pd.DataFrame(services)
    
    # Add status column (will be filled by user)
    df['status'] = 'To be checked'
    
    # Add timestamp
    df['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Reorder columns
    df = df[['service', 'port', 'browser_url', 'terminal', 'remark', 'status', 'last_updated']]
    
    # Create Excel writer
    with pd.ExcelWriter('infra.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Services', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Services']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Add header styling
        from openpyxl.styles import Font, PatternFill, Alignment
        
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
    
    print("✅ Excel file 'infra.xlsx' created successfully!")
    print(f"📊 Total services: {len(services)}")
    print("📋 Columns: service, port, browser_url, terminal, remark, status, last_updated")

if __name__ == "__main__":
    create_excel_file() 