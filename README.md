# SRE Assignment - E-commerce Platform Log Monitoring

## 🚀 Quick Start - Tinggal Satu Perintah!

```bash
./run_demo.sh
```

**That's it!** Script ini akan otomatis:
- ✅ Start Elasticsearch & Kibana dengan Docker
- ✅ Parse sample logs (52 log entries)
- ✅ Ingest data ke Elasticsearch
- ✅ Run monitoring dengan real-time alerting
- ✅ Show semua access points

## 📊 Apa yang Akan Ditampilkan

### 1. Log Parsing Results
```
Total Transactions: 52
Total Errors: 19
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

## 📁 File Structure (Yang Dipakai)

```
sre-sawitpro/
├── run_demo.sh           # 🎯 MAIN SCRIPT - Jalankan ini!
├── log_parser.py         # Parser untuk custom log format
├── ingest_logs.py        # Ingestion ke Elasticsearch
├── simple_alerting.py    # Real-time monitoring & alerts
├── sample.log            # Sample log data (52 entries)
├── docker-compose.yml    # ELK Stack (Elasticsearch + Kibana)
└── requirements.txt      # Python dependencies
```

## 🔧 Requirements

- Docker & Docker Compose
- Python 3.7+
- Port 9200 & 5601 available

## 🎯 Assignment Requirements ✅

- ✅ **Log Parsing**: Custom format → JSON structure
- ✅ **Metrics Extraction**: Error rates, response times, volumes  
- ✅ **ELK Integration**: Elasticsearch + Kibana running
- ✅ **Real-time Monitoring**: Threshold-based alerting
- ✅ **Production Ready**: Docker Compose, health checks

---

**Just run `./run_demo.sh` and everything works! 🎉**