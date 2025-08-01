#!/bin/bash

# SRE Assignment Demo Script
# This script demonstrates the complete log parsing and monitoring solution

echo "🚀 SRE Assignment Demo - E-commerce Platform Log Monitoring"
echo "==========================================================="
echo

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Start services
echo "🚀 Starting ELK Stack services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 45

# Check if services are healthy
echo "📊 Checking service status..."
if curl -s http://localhost:9200/_cluster/health > /dev/null; then
    echo "✅ Elasticsearch is ready"
else
    echo "⏳ Elasticsearch still starting, waiting more..."
    sleep 30
fi

if curl -s http://localhost:5601/api/status > /dev/null 2>&1; then
    echo "✅ Kibana is ready"
else
    echo "⏳ Kibana still starting (this is normal)"
fi

echo
echo "🔍 Step 1: Parsing Sample Logs"
echo "--------------------------------"
python3 log_parser.py sample.log

echo
echo "📥 Step 2: Ingesting Logs into Elasticsearch"
echo "---------------------------------------------"
python3 ingest_logs.py sample.log

echo
echo "📈 Step 3: Current Monitoring Dashboard"
echo "---------------------------------------"
python3 simple_alerting.py --once

echo
echo "🌐 Step 4: Access Points"
echo "------------------------"
echo "• Kibana Dashboard: http://localhost:5601"
echo "• Elasticsearch API: http://localhost:9200"
echo "• Index data: http://localhost:9200/ecommerce-logs-*/_search?pretty"

echo
echo "🔔 Step 5: Continuous Monitoring (Optional)"
echo "-------------------------------------------"
echo "To start continuous monitoring, run:"
echo "  python3 simple_alerting.py"
echo

echo "✅ Demo completed successfully!"
echo
echo "📋 Summary of what was demonstrated:"
echo "• Log parsing from custom format to structured JSON"
echo "• Direct ingestion into Elasticsearch"
echo "• Real-time monitoring with threshold-based alerting"
echo "• Key metrics: Error rates, response times, transaction volumes"
echo "• Scalable ELK stack infrastructure"