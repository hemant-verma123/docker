#!/usr/bin/env python3
"""
Simple script to check the status of all infrastructure services
"""

import subprocess
import requests
import socket
import time

def check_port(host, port, timeout=3):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_http(url, timeout=3):
    """Check if an HTTP endpoint is accessible"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code < 500
    except:
        return False

def main():
    """Check all services and display status"""
    
    services = [
        {"name": "LocalStack", "port": 4566, "url": "http://localhost:4566"},
        {"name": "MinIO Server", "port": 9000, "url": "http://localhost:9000"},
        {"name": "MinIO Console", "port": 9006, "url": "http://localhost:9006"},
        {"name": "DynamoDB Local", "port": 8083, "url": None},
        {"name": "DynamoDB Admin", "port": 8002, "url": "http://localhost:8002"},
        {"name": "MySQL", "port": 3307, "url": None},
        {"name": "phpMyAdmin", "port": 8004, "url": "http://localhost:8004"},
        {"name": "SonarQube", "port": 9005, "url": "http://localhost:9005"},
        {"name": "PostgreSQL", "port": 5432, "url": None},
        {"name": "PHP App", "port": 8003, "url": "http://localhost:8003"},
        {"name": "Prometheus", "port": 9090, "url": "http://localhost:9090"},
        {"name": "AlertManager", "port": 9093, "url": "http://localhost:9093"},
        {"name": "PromLens", "port": 8080, "url": "http://localhost:8080"},
        {"name": "Elasticsearch", "port": 9200, "url": "http://localhost:9200"},
        {"name": "Kibana", "port": 5601, "url": "http://localhost:5601"},
    ]
    
    print("🔍 Checking Infrastructure Services Status")
    print("=" * 50)
    
    working = 0
    total = len(services)
    
    for service in services:
        name = service["name"]
        port = service["port"]
        url = service["url"]
        
        # Check port
        port_ok = check_port("localhost", port)
        
        # Check URL if available
        url_ok = False
        if url:
            url_ok = check_http(url)
        
        # Determine status
        if port_ok or url_ok:
            status = "✅ Working"
            working += 1
            if port_ok and url_ok:
                status += " (Port & Browser)"
            elif port_ok:
                status += " (Port only)"
            elif url_ok:
                status += " (Browser only)"
        else:
            status = "❌ Not accessible"
        
        print(f"{name:<20} {status}")
    
    print("=" * 50)
    print(f"📊 Summary: {working}/{total} services working")
    
    if working == total:
        print("🎉 All services are running!")
    elif working > total * 0.8:
        print("✅ Most services are running")
    else:
        print("⚠️  Some services are not accessible")

if __name__ == "__main__":
    main() 