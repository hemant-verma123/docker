#!/usr/bin/env python3
"""
Script to test all services and update infra.xlsx with actual status
"""

import requests
import subprocess
import time
import pandas as pd
from datetime import datetime
import socket

def test_port(host, port, timeout=5):
    """Test if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_http_endpoint(url, timeout=5):
    """Test if an HTTP endpoint is accessible"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code < 500  # Consider 4xx as accessible but with client errors
    except:
        return False

def test_service(service_info):
    """Test a specific service"""
    service = service_info['service']
    port = service_info['port']
    browser_url = service_info['browser_url']
    
    print(f"Testing {service}...")
    
    # Test port if available
    port_working = False
    if port != 'N/A':
        try:
            port_num = int(port)
            port_working = test_port('localhost', port_num)
        except ValueError:
            port_working = False
    
    # Test browser URL if available
    browser_working = False
    if browser_url != 'N/A':
        browser_working = test_http_endpoint(browser_url)
    
    # Determine overall status
    if port_working or browser_working:
        status = "✅ Working"
        if port_working and browser_working:
            status += " (Port & Browser)"
        elif port_working:
            status += " (Port only)"
        elif browser_working:
            status += " (Browser only)"
    else:
        status = "❌ Not accessible"
    
    return status

def update_excel_with_status():
    """Update Excel file with actual service status"""
    
    # Read existing Excel file
    try:
        df = pd.read_excel('infra.xlsx')
    except FileNotFoundError:
        print("❌ infra.xlsx not found. Please run generate_infra_excel.py first.")
        return
    
    print("🔍 Testing all services...")
    print("=" * 50)
    
    # Test each service
    for index, row in df.iterrows():
        service_info = {
            'service': row['service'],
            'port': row['port'],
            'browser_url': row['browser_url']
        }
        
        status = test_service(service_info)
        df.at[index, 'status'] = status
        df.at[index, 'last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"  {status}")
    
    # Save updated Excel file
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
    
    print("=" * 50)
    print("✅ Excel file updated with service status!")
    
    # Print summary
    working_services = df[df['status'].str.contains('✅')].shape[0]
    total_services = df.shape[0]
    print(f"📊 Summary: {working_services}/{total_services} services working")

def start_services():
    """Start all services using docker-compose"""
    print("🚀 Starting all services...")
    try:
        result = subprocess.run(['docker-compose', 'up', '-d'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            print("✅ Services started successfully!")
            print("⏳ Waiting 30 seconds for services to initialize...")
            time.sleep(30)
        else:
            print("❌ Failed to start services:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error starting services: {e}")

def stop_services():
    """Stop all services using docker-compose"""
    print("🛑 Stopping all services...")
    try:
        result = subprocess.run(['docker-compose', 'down'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            print("✅ Services stopped successfully!")
        else:
            print("❌ Failed to stop services:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error stopping services: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "start":
            start_services()
        elif command == "stop":
            stop_services()
        elif command == "test":
            update_excel_with_status()
        elif command == "full":
            start_services()
            update_excel_with_status()
        else:
            print("Usage: python test_services.py [start|stop|test|full]")
    else:
        print("🔍 Testing services without starting them...")
        update_excel_with_status() 