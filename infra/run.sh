#!/bin/bash

# Combined Infrastructure Stack Management Script

set -e

COMPOSE_FILE="docker-compose.yml"

echo "🚀 Combined Infrastructure Stack Management"
echo "=========================================="

case "$1" in
    "start"|"up")
        echo "Starting all services..."
        docker-compose -f $COMPOSE_FILE up -d
        echo "✅ All services started successfully!"
        echo ""
        echo "📋 Service Access Points:"
        echo "  • Qdrant: http://localhost:6333"
        echo "  • LocalStack: http://localhost:4566"
        echo "  • MinIO UI: http://localhost:9001"
        echo "  • DynamoDB Admin: http://localhost:8002"    
        echo "  • PHP App: http://localhost:8003"
        echo "  • phpMyAdmin: http://localhost:8004"
        echo "  • SonarQube: http://localhost:9000"
        echo "  • Prometheus: http://localhost:9090"
        echo "  • AlertManager: http://localhost:9093"
        echo "  • PromLens: http://localhost:8080"
        echo "  • Elasticsearch: http://localhost:9200"
        echo "  • Kibana: http://localhost:5601"
        echo "  • Redis: localhost:6379"       
        ;;
    
    "stop"|"down")
        echo "Stopping all services..."
        docker-compose -f $COMPOSE_FILE down
        echo "✅ All services stopped successfully!"
        ;;
    
    "restart")
        echo "Restarting all services..."
        docker-compose -f $COMPOSE_FILE down
        docker-compose -f $COMPOSE_FILE up -d
        echo "✅ All services restarted successfully!"
        ;;
    
    "status"|"ps")
        echo "Checking service status..."
        docker-compose -f $COMPOSE_FILE ps
        ;;
    
    "logs")
        if [ -z "$2" ]; then
            echo "Showing logs for all services..."
            docker-compose -f $COMPOSE_FILE logs -f
        else
            echo "Showing logs for service: $2"
            docker-compose -f $COMPOSE_FILE logs -f "$2"
        fi
        ;;
    
    "clean")
        echo "⚠️  WARNING: This will remove all containers, networks, and volumes!"
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Cleaning up all resources..."
            docker-compose -f $COMPOSE_FILE down -v --remove-orphans
            docker system prune -f
            echo "✅ Cleanup completed!"
        else
            echo "Cleanup cancelled."
        fi
        ;;
    
    "health")
        echo "Checking service health..."
        echo ""
        
        # Check if services are running
        if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
            echo "✅ Services are running"
        else
            echo "❌ No services are running"
            exit 1
        fi
        
        # Check specific endpoints
        echo ""
        echo "🔍 Checking service endpoints..."
        
        # LocalStack
        if curl -s http://localhost:4566 > /dev/null 2>&1; then
            echo "✅ LocalStack (http://localhost:4566)"
        else
            echo "❌ LocalStack (http://localhost:4566)"
        fi
        
        # SonarQube
        if curl -s http://localhost:9000 > /dev/null 2>&1; then
            echo "✅ SonarQube (http://localhost:9000)"
        else
            echo "❌ SonarQube (http://localhost:9000)"
        fi
        
        # Prometheus
        if curl -s http://localhost:9090 > /dev/null 2>&1; then
            echo "✅ Prometheus (http://localhost:9090)"
        else
            echo "❌ Prometheus (http://localhost:9090)"
        fi
        
        # Elasticsearch
        if curl -s http://localhost:9200 > /dev/null 2>&1; then
            echo "✅ Elasticsearch (http://localhost:9200)"
        else
            echo "❌ Elasticsearch (http://localhost:9200)"
        fi
        
        # Kibana
        if curl -s http://localhost:5601 > /dev/null 2>&1; then
            echo "✅ Kibana (http://localhost:5601)"
        else
            echo "❌ Kibana (http://localhost:5601)"
        fi
        
        # Redis
        if redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
            echo "✅ Redis (localhost:6379)"
        else
            echo "❌ Redis (localhost:6379)"
        fi
        ;;
    
    "help"|"--help"|"-h"|"")
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  start, up      Start all services"
        echo "  stop, down     Stop all services"
        echo "  restart        Restart all services"
        echo "  status, ps     Show service status"
        echo "  logs [SERVICE] Show logs (all or specific service)"
        echo "  health         Check service health"
        echo "  clean          Remove all containers, networks, and volumes"
        echo "  help           Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 logs prometheus"
        echo "  $0 health"
        ;;
    
    *)
        echo "❌ Unknown command: $1"
        echo "Run '$0 help' for usage information."
        exit 1
        ;;
esac 