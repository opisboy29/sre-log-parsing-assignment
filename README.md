# SRE Assignment - E-commerce Platform Log Monitoring

## 🚀 Quick Start - One Command Setup!

```bash
./run_demo.sh
```

**That's it!** This script will automatically:
- ✅ Start Elasticsearch & Kibana with Docker
- ✅ Parse sample logs (260 log entries)
- ✅ Ingest data into Elasticsearch
- ✅ Run monitoring with real-time alerting
- ✅ Show all access points

## 📊 What Will Be Displayed

### 1. Log Parsing Results
```
Total Transactions: 260
Total Errors: 95
Error Rate: 36.54%
Average Response Time: 387.94ms
```

### 2. Real-time Alerts
```
🚨 WARNING: High Error Rate (36.54% > 25%)
🚨 WARNING: High Response Time (P95: 1970ms > 1000ms)
```

### 3. Access Points
- **Kibana Dashboard**: http://localhost:5601
- **Elasticsearch API**: http://localhost:9200

## 📁 Project Structure

```
sre-sawitpro/
├── run_demo.sh           # 🎯 MAIN SCRIPT - Run this!
├── log_parser.py         # Parser for custom log format
├── ingest_logs.py        # Elasticsearch ingestion
├── simple_alerting.py    # Real-time monitoring & alerts
├── sample.log            # Sample log data (260 entries)
├── docker-compose.yml    # ELK Stack (Elasticsearch + Kibana)
└── requirements.txt      # Python dependencies
```

## 🔧 Requirements

- Docker & Docker Compose
- Python 3.7+
- Ports 9200 & 5601 available

## 🎯 Assignment Requirements ✅

- ✅ **Log Parsing**: Custom format → JSON structure
- ✅ **Metrics Extraction**: Error rates, response times, volumes  
- ✅ **ELK Integration**: Elasticsearch + Kibana running
- ✅ **Real-time Monitoring**: Threshold-based alerting
- ✅ **Production Ready**: Docker Compose, health checks

---

**Just run `./run_demo.sh` and everything works! 🎉**