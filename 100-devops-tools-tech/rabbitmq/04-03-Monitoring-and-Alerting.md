# 04-03: Monitoring and Alerting

## 1️⃣ What Is RabbitMQ Monitoring

**RabbitMQ Monitoring** is the practice of observing RabbitMQ brokers, queues, exchanges, and messages to ensure system health, detect issues early, and optimize performance. This includes collecting metrics, visualizing data, and alerting on problems.

Think of RabbitMQ monitoring like monitoring a company's operations:

- **Metrics** = Production statistics (messages per second, queue depth)
- **Monitoring** = Dashboard visibility (real-time status)
- **Alerting** = Notifications (email, Slack, PagerDuty on issues)
- **Logs** = Audit trail (events, errors, warnings)

**Where monitoring fits in RabbitMQ architecture:**

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│  Producer   │        │  Consumer    │        │  Admin       │        │  Alerting    │
└──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
       │                    │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    RabbitMQ Server                                  │
│                    (Monitoring Layer)                                │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────────────────────┐   │
│   │              │              │              │               │   │   │
│   │   Metrics     │     Alerts    │     Dashboard    │   │   │   │
│   │  (Prometheus) │     (PagerDuty) │     (Grafana)    │   │   │   │
│   │              │              │              │               │   │   │
│   │              │              │              │               │   │   │
│   └──────────────┘  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │              │              │              │               │   │   │
│   │   Logs        │     Audit      │     Events      │   │   │   │
│   │  (File Logs)  │     (Security)  │     (Errors)     │   │   │   │
│   │              │              │              │               │   │   │
│   └──────────────┘  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────────┘
       │                    │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼                    ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│ Prometheus   ││  Alerting    ││  Grafana     ││  Logs        │
│  (Metrics)   ││ (PagerDuty)   ││  (Dashboard)  ││  (File/Cloud) │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘
```

**Key concepts:**
- **Metrics:** Quantitative data (message rates, queue depth, CPU, memory)
- **Monitoring:** Visual representation (dashboards, graphs, charts)
- **Alerting:** Notifications on threshold breaches (queue depth, node down)
- **Logs:** Audit trail (events, errors, warnings, security events)
- **Prometheus:** Metrics collection (pull-based scraping)
- **Grafana:** Dashboard visualization (prometheus data source)
- **PagerDuty:** Alerting service (escalation, on-call rotation)

---

## 2️⃣ Problems Solved by Monitoring

### The "System Downtime" Problem

Without monitoring:

- RabbitMQ node goes down silently
- No visibility into system health
- Problems detected only after user reports
- No proactive issue resolution
- Long MTTR (Mean Time To Repair)

**Real-world failure scenario:**

A production system had:

```
RabbitMQ Node → System Down (Silent)
            │
            ├─ RabbitMQ node crashes
            ├─ No monitoring (no alerts)
            ├─ No visibility into system health
            └─ Users complain about outages

WITHOUT MONITORING:
├─ RabbitMQ node crashes (silent)
├─ No monitoring (no visibility)
├─ No alerts (no notifications)
├─ No proactive issue resolution
└─ Long MTTR (hours to detect and fix)

PROBLEMS:
├─ Silent failures (no alerts)
├─ No visibility into system health
├─ No proactive issue resolution
├─ Long MTTR (hours to detect and fix)
└─ **Impact:** System unavailable, lost revenue, poor user experience
```

**Problems:**
- Silent failures (no alerts)
- No visibility into system health
- No proactive issue resolution
- Long MTTR (hours to detect and fix)
- **Impact:** System unavailable, lost revenue, poor user experience

After implementing monitoring:
- Real-time visibility into RabbitMQ health
- Immediate alerts on node failures (email, Slack, PagerDuty)
- Proactive issue resolution (detect before users notice)
- Reduced MTTR (minutes to detect and fix)
- **Result:** System health visible, proactive alerts, reduced downtime, good user experience

### The "Performance Bottleneck" Problem

Without monitoring:

- RabbitMQ bottlenecked (slow processing)
- Queue depth increases (messages piling up)
- Consumers can't keep up (slow processing)
- No visibility into system performance
- Performance degradation not detected

**Example:**

```
Producer → RabbitMQ (Bottleneck)
         │
         ├─ Producer publishes 10,000 messages/second
         ├─ RabbitMQ can't keep up (bottleneck)
         ├─ Queue depth increases (10,000 messages piling up)
         └─ Consumers can't process fast enough (bottleneck)

WITHOUT MONITORING (PERFORMANCE BOTTLENECK):
├─ No visibility into queue depth (10,000 messages)
├─ No visibility into message rates (10,000 messages/sec)
├─ No visibility into consumer lag (bottleneck)
├─ No alerts on performance degradation
└─ No proactive issue resolution

PROBLEMS:
├─ Queue depth increases (10,000 messages piling up)
├─ No visibility into message rates (10,000 messages/sec)
├─ No visibility into consumer lag (bottleneck)
├─ No alerts on performance degradation
├─ No proactive issue resolution
└─ **Impact:** System overwhelmed, poor throughput, slow user experience
```

**Problems:**
- Queue depth increases (messages piling up)
- No visibility into message rates (bottleneck)
- No visibility into consumer lag (slow processing)
- No alerts on performance degradation
- No proactive issue resolution
- **Impact:** System overwhelmed, poor throughput, slow user experience

After implementing monitoring:
- Real-time visibility into queue depth (10,000 messages)
- Real-time visibility into message rates (10,000 messages/sec)
- Real-time visibility into consumer lag (bottleneck detected)
- Immediate alerts on performance degradation (queue depth > threshold)
- Proactive issue resolution (add consumers, scale RabbitMQ)
- **Result:** System performance visible, proactive alerts, proactive scaling, good user experience

---

## 3️⃣ When You Should Use Monitoring

### Development vs Production

**Development:**
- Can use RabbitMQ Management Plugin (basic monitoring)
- Don't need external monitoring (Prometheus, Grafana)
- Don't need alerting (no production incidents)
- Use simple monitoring for development

**Production:**
- Absolutely required for high availability (no silent failures)
- Essential for performance optimization (real-time metrics)
- Critical for alerting (immediate notifications on issues)
- Required for audit compliance (GDPR, PCI-DSS)
- Necessary for multi-node clusters (cluster health monitoring)
- Required for production systems (99.9%+ uptime SLA)

### Monitoring Scenarios

| Scenario | Monitoring Strategy | Example |
|----------|----------------|----------|
| **High availability** | Node health + Alerting | Financial transactions, order processing |
| **High throughput** | Queue depth + Message rates | Data processing, ETL jobs |
| **Multi-region** | Cluster monitoring + Alerting | Global messaging, multi-region |
| **Compliance** | Audit logs + Security events | Finance, healthcare |

### Required vs Optional

**Required when:**
- Production systems (any production environment)
- High availability requirements (99.9%+ uptime SLA)
- High-throughput systems (millions of messages)
- Multi-node clusters (cluster health monitoring)
- Compliance requirements (GDPR, PCI-DSS, HIPAA)
- External access (third-party clients, public API)

**Optional when:**
- Development and testing environments
- Single node systems (simple monitoring sufficient)
- Low-volume systems (few messages)
- Internal services (trusted network)

### Trade-offs

**Monitoring:**
✅ Real-time visibility into system health  
✅ Proactive alerting (immediate notifications on issues)  
✅ Performance optimization (real-time metrics)  
✅ Audit compliance (logs, security events)  
✅ Reduced MTTR (minutes instead of hours)  
✅ Production-ready (enterprise-grade)  
✅ Historical data (performance trends over time)  
❌ More complex setup (Prometheus, Grafana, PagerDuty)  
❌ Higher cost (monitoring infrastructure, alerting service)  
❌ Alert fatigue (too many notifications)  
❌ False positives (thresholds too aggressive)  
❌ Monitoring overhead (CPU, memory for monitoring)  

**No Monitoring:**
✅ Simpler setup (RabbitMQ Management Plugin)  
✅ Lower cost (no monitoring infrastructure)  
✅ Easier to manage (basic monitoring)  
❌ Silent failures (no alerts)  
❌ No visibility into system health  
❌ No proactive issue resolution  
❌ Long MTTR (hours to detect and fix)  
❌ No performance optimization (no real-time metrics)  
❌ No audit compliance (no logs, no security events)  

---

## 4️⃣ How RabbitMQ Monitoring Works

### Monitoring Architecture

**Setting up RabbitMQ monitoring:**

```
1. Enable RabbitMQ Management Plugin
   │
   ├─ Enables web UI (http://localhost:15672)
   ├─ Provides REST API for metrics
   ├─ Basic monitoring (queues, exchanges, connections)
   └─ Ready for metrics collection
   │
2. Enable Prometheus Plugin
   │
   ├─ Exports RabbitMQ metrics to Prometheus format
   ├─ Metrics: message rates, queue depth, CPU, memory
   ├─ HTTP endpoint: http://localhost:15692/metrics
   └─ Ready for Prometheus scraping
   │
3. Configure Prometheus (Metrics Collection)
   │
   ├─ Scrape RabbitMQ metrics (every 15 seconds)
   ├─ Store metrics in time-series database
   ├─ Query metrics for alerting
   └─ Ready for Grafana visualization
   │
4. Configure Grafana (Visualization)
   │
   ├─ Connect to Prometheus (data source)
   ├─ Create dashboards (queue depth, message rates)
   ├─ Create graphs (CPU, memory, disk)
   └─ Ready for real-time monitoring
   │
5. Configure Alerting (PagerDuty, Slack, Email)
   │
   ├─ Configure alert rules (queue depth > threshold)
   ├─ Configure alert rules (node down)
   ├─ Configure alert rules (consumer lag)
   └─ Configure alert routing (PagerDuty escalation)
   │
6. Configure Logs (Audit Trail)
   │
   ├─ Enable RabbitMQ logs (file logs)
   ├─ Configure log rotation (prevent disk full)
   ├─ Forward logs to centralized logging (ELK, CloudWatch)
   └─ Ready for audit compliance
   │
7. Configure Cluster Monitoring (Multi-Node)
   │
   ├─ Monitor node health (CPU, memory, disk)
   ├─ Monitor cluster status (nodes in cluster)
   ├─ Monitor queue mirroring status
   └─ Ready for cluster health visibility
   │
8. Client-Side Monitoring
   │
   ├─ Monitor client connections (producers, consumers)
   ├─ Monitor client message rates (publish/consume rates)
   ├─ Monitor client errors (connection refused, auth failed)
   └─ Ready for client-side visibility
```

### Monitoring Mechanisms

**How metrics collection works:**

```
RabbitMQ Server (Prometheus Plugin):
├─ Exports metrics to Prometheus format
├─ Metrics: message_rates, queue_depth, cpu, memory
├─ HTTP endpoint: http://localhost:15692/metrics
└─ Ready for Prometheus scraping

Prometheus (Metrics Collection):
├─ Scrapes RabbitMQ metrics (every 15 seconds)
├─ Stores metrics in time-series database
├─ Metrics available for querying and alerting
└─ Historical data (performance trends over time)

Grafana (Visualization):
├─ Connects to Prometheus (data source)
├─ Queries metrics (queue_depth, message_rates)
├─ Creates dashboards (queue depth graphs)
├─ Creates charts (CPU, memory, disk)
└─ Real-time monitoring visibility

Alerting (PagerDuty):
├─ Monitors Prometheus metrics (queue_depth thresholds)
├─ Monitors RabbitMQ metrics (node_down alerts)
├─ Triggers alerts (email, Slack, PagerDuty)
└─ Escalates (on-call rotation, manager notification)
```

---

## 5️⃣ Installation / Setup

**RabbitMQ Monitoring is built-in RabbitMQ feature.** No installation required - just enable Management Plugin and Prometheus Plugin.

### Prerequisites

- RabbitMQ server running
- RabbitMQ Management Plugin enabled
- RabbitMQ Prometheus Plugin enabled
- Prometheus installed and running
- Grafana installed and running
- Access to RabbitMQ Management UI (port 15672)
- Understanding of monitoring metrics (queue depth, message rates, CPU, memory)

### Enabling RabbitMQ Management Plugin

**Using rabbitmq-plugins:**

```bash
# Enable Management Plugin
sudo rabbitmq-plugins enable rabbitmq_management

# Restart RabbitMQ
sudo systemctl restart rabbitmq-server

# Verify Management Plugin
sudo rabbitmq-plugins list | grep management
```

**Using Docker:**

```bash
# Start RabbitMQ with Management Plugin
docker run -d --name rabbitmq-monitored \
  -e RABBITMQ_MANAGEMENT_PLUGIN=true \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

### Enabling RabbitMQ Prometheus Plugin

**Using rabbitmq-plugins:**

```bash
# Enable Prometheus Plugin
sudo rabbitmq-plugins enable rabbitmq_prometheus

# Restart RabbitMQ
sudo systemctl restart rabbitmq-server

# Verify Prometheus Plugin
sudo rabbitmq-plugins list | grep prometheus

# Verify Prometheus endpoint
curl http://localhost:15692/metrics
```

**Using Docker:**

```bash
# Start RabbitMQ with Prometheus Plugin
docker run -d --name rabbitmq-monitored \
  -e RABBITMQ_PROMETHEUS_PLUGIN=true \
  -p 5672:5672 -p 15672:15672 -p 15692:15692 \
  rabbitmq:3-management
```

### Installing Prometheus

```bash
# Install Prometheus (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install prometheus

# Create Prometheus configuration
cat > /etc/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['localhost:15692']
EOF

# Start Prometheus
sudo systemctl start prometheus

# Verify Prometheus
curl http://localhost:9090/targets
```

### Installing Grafana

```bash
# Install Grafana (Ubuntu/Debian)
sudo apt-get install grafana

# Start Grafana
sudo systemctl start grafana-server

# Access Grafana
# Open http://localhost:3000
# Username: admin
# Password: admin
```

### Version Notes

- **RabbitMQ 3.12+:** All monitoring features fully supported
- **Management Plugin:** Web UI, REST API for basic monitoring
- **Prometheus Plugin:** Metrics export to Prometheus format
- **Prometheus:** Metrics collection and storage
- **Grafana:** Dashboard visualization
- **Alerting:** PagerDuty, Slack, Email notifications
- **Logs:** File logs, centralized logging (ELK, CloudWatch)
- **Cluster Monitoring:** Multi-node cluster health visibility
- **Real-time Monitoring:** 15-second scrape interval for near-real-time

---

## 6️⃣ Where Monitoring Should Be Applied (With Example)

### Monitoring with Prometheus + Grafana

**Scenario:** High-throughput data processing system with performance monitoring

**Prometheus Configuration (prometheus.yml):**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'rabbitmq'
    scrape_interval: 15s
    metrics_path: /metrics
    static_configs:
      - targets: ['localhost:15692']
```

**Grafana Dashboard Configuration (rabbitmq_dashboard.json):**

```json
{
  "dashboard": {
    "title": "RabbitMQ Monitoring",
    "panels": [
      {
        "title": "Queue Depth",
        "targets": [
          {
            "expr": "rabbitmq_queue_messages{queue=\"data_processing\"}",
            "refId": "queue_depth"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Message Rates",
        "targets": [
          {
            "expr": "rate(rabbitmq_queue_messages{queue=\"data_processing\"}[1m])",
            "refId": "message_rates"
          }
        ],
        "type": "graph"
      },
      {
        "title": "CPU Usage",
        "targets": [
          {
            "expr": "rabbitmq_queue_memory{queue=\"data_processing\"}",
            "refId": "cpu_usage"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

**Applying Prometheus Configuration:**

```bash
# Apply Prometheus configuration
cat > /etc/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['localhost:15692']
EOF

# Restart Prometheus
sudo systemctl restart prometheus
```

**View in Grafana:**

1. Open http://localhost:3000
2. Go to Datasources → Add → Prometheus
3. Configure connection: http://localhost:9090
4. Go to Dashboards → Import → Import rabbitmq_dashboard.json
5. See real-time monitoring (queue depth, message rates, CPU)
6. Set up alerting (Grafana Alerting)

### Alerting Configuration

**Prometheus Alerting (alerting.yml):**

```yaml
groups:
  - name: rabbitmq_alerts
    rules:
      - alert: RabbitMQNodeDown
        expr: up{job="rabbitmq"} == 0
        for: 2m
        labels:
          severity: critical
          receiver: "pagerduty"
        annotations:
          summary: "RabbitMQ node down"
          description: "RabbitMQ node has been down for 2 minutes"
      
      - alert: RabbitMQQueueDepthHigh
        expr: rabbitmq_queue_messages{queue="data_processing"} > 100000
        for: 5m
        labels:
          severity: warning
          receiver: "slack"
        annotations:
          summary: "RabbitMQ queue depth high"
          description: "RabbitMQ queue data_processing depth is 100,000+ messages"
```

**Applying Alerting Configuration:**

```bash
# Apply alerting configuration
cat > /etc/prometheus/alerting.yml << EOF
groups:
  - name: rabbitmq_alerts
    rules:
      - alert: RabbitMQNodeDown
        expr: up{job="rabbitmq"} == 0
        for: 2m
        labels:
          severity: critical
          receiver: "pagerduty"
        annotations:
          summary: "RabbitMQ node down"
          description: "RabbitMQ node has been down for 2 minutes"
EOF

# Restart Alertmanager
sudo systemctl restart prometheus-alertmanager
```

### Best Practices

**Monitoring Configuration:**
✅ Use Prometheus for metrics collection  
✅ Use Grafana for dashboard visualization  
✅ Use 15-second scrape interval (near-real-time)  
✅ Monitor queue depth (messages piling up)  
✅ Monitor message rates (throughput)  
✅ Monitor CPU, memory, disk (system health)  
✅ Monitor node health (cluster status)  
✅ Set up alerting (immediate notifications on issues)  
✅ Store historical metrics (performance trends over time)  

**Alerting Configuration:**
✅ Set appropriate thresholds (queue depth > 100,000)  
✅ Set appropriate alert durations (node down > 2 minutes)  
✅ Use multiple alert channels (email, Slack, PagerDuty)  
✅ Configure escalation (on-call rotation, manager notification)  
✅ Use alert fatigue prevention (duplicate suppression, rate limiting)  
✅ Test alerting (send test alerts, verify notification)  

**Log Configuration:**
✅ Enable RabbitMQ file logs  
✅ Configure log rotation (prevent disk full)  
✅ Forward logs to centralized logging (ELK, CloudWatch)  
✅ Store logs in secure location (access control)  
✅ Retain logs for audit compliance (GDPR, PCI-DSS)  

### Common Mistakes

❌ Not monitoring queue depth → Messages piling up (bottleneck)  
❌ Not monitoring message rates → Throughput issues not visible  
❌ Not monitoring CPU, memory → System health not visible  
❌ Not setting up alerting → Silent failures (no notifications)  
❌ Alert thresholds too low → Alert fatigue (too many notifications)  
❌ Not storing historical metrics → No performance trends over time  
❌ Not configuring log rotation → Disk full, RabbitMQ crashes  
❌ Not forwarding logs centrally → No centralized audit trail  
❌ Monitoring too frequent → Performance overhead (CPU, memory)  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Silent Failures (The "Invisible Problems" Problem)**

You're building a production messaging system:

- RabbitMQ node crashes silently (no monitoring)
- No visibility into system health
- No alerts on node failures
- Users complain about outages only after the fact
- Long MTTR (Mean Time To Repair = 4 hours)

Current implementation:
- No monitoring (no visibility into system health)
- No alerting (no notifications on issues)
- No performance optimization (no real-time metrics)
- No audit compliance (no logs)

**Problems:**
- Silent failures (no alerts)
- No visibility into system health
- No proactive issue resolution
- Long MTTR (4 hours)
- **Impact:** System unavailable, lost revenue, poor user experience

### 🧪 Lab Tasks

**Step 1: Start RabbitMQ without monitoring**

```bash
# Start RabbitMQ (no monitoring)
docker run -d --name rabbitmq-unmonitored \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Verify Management Plugin enabled
# curl http://localhost:15672/api/overview
# See: "management": true
```

**Step 2: Create producer**

Create `unmonitored_producer.py`:

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: No monitoring (no visibility into system health)
channel.queue_declare(queue='data_processing', durable=True)

# PROBLEM: Publish messages (no monitoring of queue depth)
for i in range(1000):
    data = {
        "values": list(range(100)),
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='data_processing',
        body=json.dumps(data)
    )
    
    if i % 100 == 0:
        print(f"[x] Published {i} messages")

print(f"[!] Published 1000 messages (PROBLEM: No monitoring - queue depth not visible)")
connection.close()
```

**Step 3: Create consumer**

Create `unmonitored_consumer.py`:

```python
import pika
import json
import time

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"[✓] Processing data: {data}")
    # PROBLEM: No monitoring (no visibility into consumer lag)
    time.sleep(1)  # PROBLEM: Slow processing (simulates bottleneck)
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: No monitoring (no visibility into consumer lag)
channel.queue_declare(queue='data_processing', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='data_processing', on_message_callback=callback)

print("[!] Unmonitored consumer (PROBLEM: No monitoring - consumer lag not visible)")
channel.start_consuming()
```

**Step 4: Simulate node failure**

```bash
# Stop RabbitMQ (simulate node failure)
docker stop rabbitmq-unmonitored

# Verify: System unavailable
# Producer connection refused
# Consumer stops processing
# No alert (no monitoring)
```

**Expected observation:**
- Producer publishes 1000 messages
- Consumer processes slowly (bottleneck)
- Node fails (simulated)
- No monitoring (no visibility into system health)
- No alert (no notification)
- Long MTTR (4 hours to detect and fix)
- **Impact:** System unavailable, lost revenue, poor user experience

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Overview tab
- See RabbitMQ status (up)
- See message rates (visible)
- See queue depth (visible)
- See node status (up)
- See no alerting (no notifications configured)

### ✅ Solution & Explanation

**Solution: Implement RabbitMQ Monitoring (Prometheus + Grafana + Alerting)**

**Step 1: Enable Prometheus Plugin**

```bash
# Stop unmonitored RabbitMQ
docker stop rabbitmq-unmonitored
docker rm rabbitmq-unmonitored

# Start RabbitMQ with Prometheus Plugin
docker run -d --name rabbitmq-monitored \
  -e RABBITMQ_PROMETHEUS_PLUGIN=true \
  -p 5672:5672 -p 15672:15672 -p 15692:15692 \
  rabbitmq:3-management

# Verify Prometheus Plugin
# curl http://localhost:15692/metrics
```

**Step 2: Install and Start Prometheus**

```bash
# Install Prometheus
sudo apt-get install prometheus

# Create Prometheus configuration
cat > /etc/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['localhost:15692']
EOF

# Start Prometheus
sudo systemctl start prometheus

# Verify Prometheus
curl http://localhost:9090/targets
```

**Step 3: Install and Start Grafana**

```bash
# Install Grafana
sudo apt-get install grafana

# Start Grafana
sudo systemctl start grafana-server

# Access Grafana
# Open http://localhost:3000
# Username: admin
# Password: admin
```

**Step 4: Configure Grafana Datasource**

1. Open http://localhost:3000
2. Go to Configuration → Data Sources → Add → Prometheus
3. Configure connection: http://localhost:9090
4. Set name: RabbitMQ
5. Set scrape interval: 15s
6. Save and Test

**Step 5: Create Grafana Dashboard**

1. Go to Dashboards → New
2. Import dashboard: rabbitmq_dashboard.json
3. See real-time monitoring (queue depth, message rates, CPU)

**Step 6: Configure Alerting**

```bash
# Create alerting configuration
cat > /etc/prometheus/alerting.yml << EOF
groups:
  - name: rabbitmq_alerts
    rules:
      - alert: RabbitMQNodeDown
        expr: up{job="rabbitmq"} == 0
        for: 2m
        labels:
          severity: critical
          receiver: "email"
        annotations:
          summary: "RabbitMQ node down"
          description: "RabbitMQ node has been down for 2 minutes"
EOF

# Restart Alertmanager
sudo systemctl restart prometheus-alertmanager
```

**How to verify:**

```bash
# Terminal: Monitored producer
python3 monitored_producer.py

# Terminal: Monitored consumer
python3 monitored_consumer.py

# Terminal: Verify Prometheus
curl http://localhost:9090/metrics

# Terminal: Verify Grafana
# Open http://localhost:3000
# See real-time monitoring (queue depth, message rates, CPU)
```

**Expected output:**

```
# Monitored Producer
[x] Published 100 messages
[x] Published 200 messages
...
[x] Published 1000 messages
[!] Published 1000 messages (SOLUTION: Monitoring enabled)

# Monitored Consumer
[*] Monitored consumer (SOLUTION: Consumer lag monitored)
[✓] Processing data: {'values': [0, 1, ...]}
[!] Processing data: {'values': [0, 1, ...]}
...
```

**View in Grafana:**

1. Open http://localhost:3000
2. See RabbitMQ dashboard
3. See real-time monitoring (queue depth, message rates, CPU)
4. See performance trends over time

**Simulate node failure:**

```bash
# Stop RabbitMQ (simulate node failure)
docker stop rabbitmq-monitored

# Verify: Alert triggered
# Check email for alert: "RabbitMQ node down"
# Check Grafana dashboard (node status down)
# MTTR reduced (2 minutes instead of 4 hours)
```

**Comparison:**

| Design | Monitoring | Alerting | MTTR |
|--------|-----------|---------|------|
| No Monitoring (old) | None | No | 4 hours |
| Monitoring (new) | Prometheus + Grafana | Email/Slack | 2 minutes |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Use Prometheus for metrics collection  
- Use Grafana for dashboard visualization  
- Use 15-second scrape interval (near-real-time)  
- Monitor queue depth (messages piling up)  
- Monitor message rates (throughput)  
- Monitor CPU, memory, disk (system health)  
- Set up alerting (immediate notifications on issues)  
- Use multiple alert channels (email, Slack, PagerDuty)  
- Store historical metrics (performance trends over time)  
- Configure log rotation (prevent disk full)  
- Forward logs centrally (ELK, CloudWatch)  

**❌ Don't:**
- Not monitoring queue depth → Messages piling up (bottleneck)  
- Not monitoring message rates → Throughput issues not visible  
- Not monitoring CPU, memory → System health not visible  
- Not setting up alerting → Silent failures (no notifications)  
- Alert thresholds too low → Alert fatigue (too many notifications)  
- Not storing historical metrics → No performance trends over time  
- Not configuring log rotation → Disk full, RabbitMQ crashes  
- Not forwarding logs centrally → No centralized audit trail  
- Monitoring too frequently → Performance overhead (CPU, memory)  

### Monitoring Guidelines

```
Prometheus (Metrics Collection):
├─ Scrape RabbitMQ metrics (every 15 seconds)
├─ Store metrics in time-series database
├─ Query metrics for alerting
└─ Historical data (performance trends)

Grafana (Visualization):
├─ Connect to Prometheus (data source)
├─ Create dashboards (queue depth, message rates)
├─ Create graphs (CPU, memory, disk)
└─ Real-time monitoring visibility

Alerting:
├─ Monitor queue depth (messages piling up)
├─ Monitor node down (immediate notification)
├─ Use multiple alert channels (email, Slack, PagerDuty)
├─ Configure escalation (on-call rotation)
└─ Prevent alert fatigue (duplicate suppression)

Logs:
├─ Enable RabbitMQ file logs
├─ Configure log rotation
├─ Forward logs to centralized logging
└─ Retain logs for audit compliance

Cluster Monitoring:
├─ Monitor node health (CPU, memory, disk)
├─ Monitor cluster status (nodes in cluster)
└─ Monitor queue mirroring status
```

### Production Considerations

**Scaling Monitoring:**

```bash
# Add more Prometheus servers (high availability)
docker run -d --name prometheus-2 \
  -p 9090:9090 \
  -v $(pwd)/prometheus:/etc/prometheus:$(pwd)/prometheus \
  prom/prometheus \
  --config.file=/etc/prometheus/prometheus.yml

# Configure Prometheus high availability (HA)
cat > /etc/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'rabbitmq_1'
    static_configs:
      - targets: ['localhost:15692']
  - job_name: 'rabbitmq_2'
    static_configs:
      - targets: ['localhost:15693']
EOF
```

**Log Centralization:**

```bash
# Configure RabbitMQ to forward logs to ELK
cat > /etc/rabbitmq/rabbitmq.conf << EOF
log.console.level = info
log.console = true
log.file.level = info
log.file = true
log.file.path = /var/log/rabbitmq/rabbit.log
log.rotation.size = 104857600
log.rotation.count = 5
log.connection.level = info
log.channel.level = info

# Configure Filebeat to forward logs to ELK
cat > /etc/filebeat/filebeat.yml << EOF
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/rabbitmq/*.log
output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  indices: ["rabbitmq-logs"]
EOF
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's RabbitMQ monitoring?**

A: RabbitMQ monitoring is observing RabbitMQ brokers, queues, and messages to ensure system health, detect issues early, and optimize performance. Includes collecting metrics (Prometheus), visualizing data (Grafana), alerting (PagerDuty), and logging (file logs, centralized logging). Real-time visibility into system health.

**Q2: What's RabbitMQ Prometheus Plugin?**

A: RabbitMQ Prometheus Plugin exports RabbitMQ metrics in Prometheus format. Metrics include message rates, queue depth, CPU, memory, disk. Provides HTTP endpoint for Prometheus scraping. Enables metrics collection and alerting.

**Q3: What's RabbitMQ Management Plugin?**

A: RabbitMQ Management Plugin provides web UI and REST API for basic monitoring. Shows queues, exchanges, connections, consumers. Basic monitoring without external tools.

**Q4: What's Grafana?**

A: Grafana is open-source dashboard visualization tool. Connects to Prometheus (data source), creates dashboards and graphs. Real-time monitoring visibility.

**Q5: How do you set up RabbitMQ monitoring?**

A: Enable RabbitMQ Prometheus Plugin (exports metrics). Install Prometheus (scrapes metrics every 15 seconds). Install Grafana (connects to Prometheus, creates dashboards). Set up alerting (Prometheus Alertmanager or PagerDuty). Configure logs (RabbitMQ file logs, centralized logging).

### Production Pitfalls

**Pitfall 1: Not monitoring queue depth**
- Problem: Messages piling up (bottleneck)
- Detection: Queue depth increases (100,000+ messages)
- Solution: Always monitor queue depth (set alert threshold)

**Pitfall 2: Not monitoring message rates**
- Problem: Throughput issues not visible
- Detection: Message rates decrease (10,000 → 5,000 msg/sec)
- Solution: Always monitor message rates (set alert threshold)

**Pitfall 3: Not monitoring CPU, memory**
- Problem: System health not visible
- Detection: CPU increases (80% → 100%)
- Solution: Always monitor CPU, memory, disk (system health)

**Pitfall 4: Not setting up alerting**
- Problem: Silent failures (no notifications)
- Detection: Node down, no alert for 4 hours
- Solution: Always set up alerting (immediate notifications)

**Pitfall 5: Alert thresholds too low**
- Problem: Alert fatigue (too many notifications)
- Detection: Queue depth > 100,000 (too sensitive)
- Solution: Set appropriate thresholds (queue depth > 1,000,000 for critical)

### Advanced Monitoring Concepts

**Multi-Cluster Monitoring:**

```yaml
# Prometheus configuration for multiple clusters
scrape_configs:
  - job_name: 'rabbitmq_cluster_1'
    static_configs:
      - targets: ['cluster1-node1:15692', 'cluster1-node2:15692']
  - job_name: 'rabbitmq_cluster_2'
    static_configs:
      - targets: ['cluster2-node1:15692', 'cluster2-node2:15692']
```

**Custom Metrics (RabbitMQ Management API):**

```python
# Query RabbitMQ Management API for custom metrics
import requests

response = requests.get(
    "http://localhost:15672/api/queues",
    auth=('guest', 'guest')
)

queues = response.json()
for queue in queues:
    print(f"Queue: {queue['name']}, Messages: {queue.get('messages', 0)}")
```

**Log Aggregation (ELK, CloudWatch):**

```bash
# Configure Filebeat to forward logs to ELK
filebeat -e -c /etc/filebeat/filebeat.yml &
```

---

## 📚 Summary

RabbitMQ monitoring provides real-time visibility into system health, performance metrics, and alerting on issues. Prometheus collects metrics, Grafana visualizes data, alerting provides immediate notifications, logs provide audit trail.

**Key takeaways:**
- Use Prometheus for metrics collection (scrape every 15 seconds)
- Use Grafana for dashboard visualization (real-time monitoring)
- Monitor queue depth (messages piling up)
- Monitor message rates (throughput)
- Monitor CPU, memory, disk (system health)
- Set up alerting (immediate notifications on issues)
- Use multiple alert channels (email, Slack, PagerDuty)
- Configure log rotation (prevent disk full)
- Forward logs centrally (ELK, CloudWatch)
- Store historical metrics (performance trends over time)
- Reduced MTTR (minutes instead of hours)

**Next steps:**
- Practice with monitoring in your applications
- Learn about performance tuning (next lesson)
- Learn about advanced message patterns
- Complete all lessons in Module 04

---

**Module 04 - Advanced Concepts**  
**Lesson 03 - Complete**