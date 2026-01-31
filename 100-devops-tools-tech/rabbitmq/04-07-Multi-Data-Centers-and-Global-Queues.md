# 04-07: Multi-Data Centers and Global Queues

## 1️⃣ What Are Multi-Data Centers and Global Queues

**Multi-Data Centers and Global Queues** is the practice of deploying RabbitMQ across multiple geographic locations for high availability, disaster recovery, and low latency. This includes federation (linking clusters), shovel (cross-cluster messaging), and global queues (cross-data center).

Think of multi-data centers like having offices in multiple cities:

- **Multi-Data Centers** = Multiple locations (New York, London, Tokyo)
- **Global Queues** = Cross-data center messaging (global availability)
- **Federation** = Linking clusters (cross-data center replication)
- **Shovel** = Cross-cluster messaging (data bridge)
- **High Availability** = Geographic redundancy (disaster recovery)
- **Low Latency** = Local consumers (nearby brokers)

**Where multi-data centers fit in RabbitMQ architecture:**

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│  Producer   │        │  Consumer    │        │  Admin       │        │  Disaster    │
│  (NY)        │        │  (London)     │        │  (Tokyo)      │        │  Recovery    │
└──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
       │                    │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    RabbitMQ Federation (Multi-Data Centers)                                  │
│                    (Global Availability, Disaster Recovery)                              │
│                                                                                   │
│   ┌────────────────────────────────────────────────────────────────────────────┐   │
│   │              │              │              │               │   │   │
│   │    Cluster 1   │     Cluster 2   │     Cluster 3   │   │   │   │
│   │   (New York)  │     (London)    │     (Tokyo)     │   │   │   │
│   │              │              │              │               │   │   │   │
│   │              │              │              │               │   │   │   │
│   │              │              │              │               │   │   │   │
│   └──────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                                                   │
│   ┌────────────────────────────────────────────────────────────────────────────┐   │
│   │              │              │              │               │   │   │
│   │   Federation   │     Shovel     │     Global      │   │   │   │
│   │   (Linking)    │     (Bridge)    │     (Queues)     │   │   │   │
│   │              │              │              │               │   │   │   │
│   │              │              │              │               │   │   │   │
│   └──────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
       │                    │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼                    ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│  Cluster 1   ││  Cluster 2   ││  Cluster 3   ││  Shovel       │
│  (New York)   ││  (London)    ││  (Tokyo)     ││  (Bridge)      │
│  (Local)      ││  (Local)      ││  (Local)      ││  (Cross-DC)   │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘
```

**Key concepts:**
- **Federation:** Linking clusters (cross-data center replication)
- **Shovel:** Cross-cluster messaging (data bridge)
- **Global Queues:** Cross-data center queues (global availability)
- **Disaster Recovery:** Geographic redundancy (data center failure)
- **Low Latency:** Local consumers (nearby brokers)
- **Cluster Plugins:** Federation plugin, Shovel plugin
- **High Availability:** Geographic redundancy (99.9%+ uptime)

---

## 2️⃣ Problems Solved by Multi-Data Centers

### The "Single Data Center" Problem

Without multi-data centers:

- Geographic latency (consumers far from producer)
- Single point of failure (data center outage)
- No disaster recovery (data center failure = data loss)
- No global availability (local only)

**Real-world failure scenario:**

A production system had:

```
Producer → RabbitMQ (Single Data Center)
          │
          ├─ Producer publishes messages (New York)
          ├─ Consumer consumes messages (London)
          ├─ Geographic latency (NY to London: 100ms)
          ├─ Data center fails (disaster)
          └─ System unavailable (data loss)

WITHOUT MULTI-DATA CENTERS:
├─ Geographic latency (NY to London: 100ms)
├─ Single point of failure (data center outage)
├─ No disaster recovery (data center failure = data loss)
├─ No global availability (local only)
└─ **Impact:** Geographic latency, single point of failure, no disaster recovery, system unavailable

PROBLEMS:
├─ Geographic latency (consumers far from producer)
├─ Single point of failure (data center outage)
├─ No disaster recovery (data center failure = data loss)
├─ No global availability (local only)
└─ **Impact:** Geographic latency, single point of failure, no disaster recovery, system unavailable, poor user experience

After implementing multi-data centers:
- Geographic redundancy (New York, London, Tokyo)
- Local consumers (low latency)
- Disaster recovery (data center failure = failover)
- Global availability (system available from anywhere)
- **Result:** Low latency, high availability, disaster recovery, good user experience

### The "Cross-Cluster Messaging" Problem

Without federation/shovel:

- Separate clusters (no connectivity)
- No cross-cluster messaging (data silos)
- No global availability (cluster only)
- No disaster recovery (cluster failure = data loss)

**Example:**

```
Producer → Cluster 1 (New York)
          │
          ├─ Producer publishes messages (Cluster 1)
          ├─ Cluster 2 (London) no connectivity
          ├─ Cluster 3 (Tokyo) no connectivity
          ├─ No cross-cluster messaging (data silos)
          └─ System unavailable (global)

WITHOUT FEDERATION/SHOVEL:
├─ Separate clusters (no connectivity)
├─ No cross-cluster messaging (data silos)
├─ No global availability (cluster only)
├─ No disaster recovery (cluster failure = data loss)
└─ **Impact:** Data silos, no global availability, no disaster recovery, system unavailable, poor user experience

PROBLEMS:
├─ Separate clusters (no connectivity)
├─ No cross-cluster messaging (data silos)
├─ No global availability (cluster only)
├─ No disaster recovery (cluster failure = data loss)
└─ **Impact:** Data silos, no global availability, no disaster recovery, system unavailable, poor user experience

After implementing federation/shovel:
- Cross-cluster messaging (data silos broken)
- Global queues (cross-data center)
- Global availability (system available from anywhere)
- Disaster recovery (cluster failure = failover)
- **Result:** No data silos, global availability, disaster recovery, good user experience

---

## 3️⃣ When You Should Use Multi-Data Centers

### Development vs Production

**Development:**
- Can use single data center (local development)
- Don't need multi-data centers (simple tests)
- Don't need federation (single cluster)
- Don't use in production code

**Production:**
- Absolutely required for global availability (system available from anywhere)
- Essential for disaster recovery (data center failure = failover)
- Critical for low latency (local consumers)
- Required for geographic redundancy (New York, London, Tokyo)
- Necessary for production systems (99.9%+ uptime SLA)
- Necessary for compliance (GDPR, PCI-DSS, HIPAA)

### Multi-Data Center Scenarios

| Scenario | Multi-Data Center Strategy | Example |
|----------|---------------------------|----------|
| **Global availability** | Federation + Global Queues | Global applications, SaaS |
| **Disaster recovery** | Multi-Data Center + Failover | Financial transactions, order processing |
| **Low latency** | Local Consumers (Nearby Brokers) | Real-time gaming, video streaming |
| **Cross-cluster** | Shovel (Bridge) | Data migration, ETL jobs |

### Required vs Optional

**Required when:**
- Production systems (any production environment)
- Global availability requirements (system available from anywhere)
- Disaster recovery requirements (data center failure = failover)
- Low-latency requirements (local consumers)
- Geographic redundancy requirements (New York, London, Tokyo)
- Compliance requirements (GDPR, PCI-DSS, HIPAA)

**Optional when:**
- Development and testing environments
- Single data center (local deployment)
- Non-critical systems (downtime acceptable)
- Local-only applications (no global access)

### Trade-offs

**Multi-Data Centers:**
✅ Global availability (system available from anywhere)  
✅ Disaster recovery (data center failure = failover)  
✅ Low latency (local consumers)  
✅ Geographic redundancy (New York, London, Tokyo)  
✅ Cross-cluster messaging (data silos broken)  
✅ High availability (99.9%+ uptime)  
✅ Production-ready (enterprise-grade)  
✅ Compliance (GDPR, PCI-DSS, HIPAA)  
❌ More complex setup (federation, shovel, global queues)  
❌ Higher cost (multiple data centers)  
❌ More management (federation, shovel, global queues)  
❌ Higher latency (cross-data center if no local consumer)  
❌ Higher network cost (inter-data center bandwidth)  

**Single Data Center:**
✅ Simpler setup (single cluster)  
✅ Lower cost (single data center)  
✅ Easier to manage (single cluster)  
✅ Lower network cost (no inter-data center bandwidth)  
❌ Geographic latency (consumers far from producer)  
❌ Single point of failure (data center outage)  
❌ No disaster recovery (data center failure = data loss)  
❌ No global availability (local only)  
❌ No cross-cluster messaging (data silos)  

---

## 4️⃣ How Multi-Data Centers Work

### Federation Configuration Process

**Setting up RabbitMQ federation:**

```
1. Enable Federation Plugin
   │
   ├─ Enable rabbitmq_federation plugin
   ├─ Configure federation (upstream cluster)
   ├─ Configure policy (federated queues)
   └─ Federation ready (cross-data center replication)
   │
2. Configure Upstream Cluster
   │
   ├─ Configure upstream cluster (remote RabbitMQ)
   ├─ Configure upstream address (host, port)
   ├─ Configure upstream credentials (username, password)
   └─ Federation linked (cross-data center)
   │
3. Configure Federation Policy
   │
   ├─ Configure federated queues (replicated to upstream)
   ├─ Configure policy (queue name matching)
   ├─ Federation applies (queues replicated)
   └─ Global queues achieved (cross-data center)
   │
4. Configure Shovel (Bridge)
   │
   ├─ Configure shovel (source queue → destination queue)
   ├─ Configure source (cluster 1)
   ├─ Configure destination (cluster 2)
   ├─ Shovel bridges data (cross-cluster)
   └─ Cross-cluster messaging achieved (data silos broken)
   │
5. Configure Local Consumers
   │
   ├─ Consumer connects to local cluster (low latency)
   ├─ Consumer receives messages (local broker)
   ├─ Local consumers (low latency)
   └─ Low latency achieved (nearby brokers)
   │
6. Federation Flow:
   │
   ├─ Producer publishes message to cluster 1
   ├─ Federation replicates message to cluster 2
   ├─ Federation replicates message to cluster 3
   ├─ Global queues achieved (cross-data center)
   ├─ Local consumers receive messages (low latency)
   └─ Global availability achieved (system available from anywhere)
```

### Federation Mechanisms

**How federation works:**

```
Cluster 1 (New York) → Federation → Cluster 2 (London)
                        │
                        ├─ Upstream configured (remote cluster)
                        ├─ Federation policy configured (federated queues)
                        ├─ Messages replicated across clusters
                        ├─ Global queues achieved (cross-data center)
                        └─ Local consumers receive messages (low latency)

Federation Plugin:
├─ Upstream: Remote cluster (Cluster 2)
├─ Federation Policy: Queue name matching
├─ Replication: Messages replicated across clusters
├─ Global Queues: Cross-data center queues
└─ High Availability: System available from anywhere
```

**How shovel works:**

```
Cluster 1 (New York) → Shovel → Cluster 2 (London)
                        │
                        ├─ Source configured (cluster 1 queue)
                        ├─ Destination configured (cluster 2 queue)
                        ├─ Shovel bridges data (cross-cluster)
                        ├─ Data silos broken (cross-cluster messaging)
                        └─ Shovel achieved (data bridge)

Shovel Plugin:
├─ Source: Cluster 1 queue
├─ Destination: Cluster 2 queue
├─ Bridge: Cross-cluster messaging
├─ Data Silos: Broken (cross-cluster messaging)
└─ Data Migration: Shovel for data bridge
```

---

## 5️⃣ Installation / Setup

**Multi-Data Centers are built-in RabbitMQ features.** No installation required - just enable federation plugin, configure shovel, and set up global queues.

### Prerequisites

- RabbitMQ servers running on multiple hosts (different data centers)
- Same RabbitMQ version across all clusters
- Network connectivity between data centers (inter-data center bandwidth)
- Understanding of federation (linking clusters)
- Understanding of shovel (cross-cluster messaging)
- Understanding of global queues (cross-data center)
- Understanding of local consumers (low latency)
- Access to RabbitMQ Management UI (port 15672)

### Enabling Federation Plugin

**Using rabbitmq-plugins:**

```bash
# Enable Federation Plugin
sudo rabbitmq-plugins enable rabbitmq_federation

# Restart RabbitMQ
sudo systemctl restart rabbitmq-server

# Verify Federation Plugin
sudo rabbitmq-plugins list | grep federation
```

**Using Docker:**

```bash
# Start RabbitMQ with Federation Plugin
docker run -d --name rabbitmq-federated \
  -e RABBITMQ_PLUGINS="rabbitmq_federation,rabbitmq_management" \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

### Configuring Shovel

**Using rabbitmq-plugins:**

```bash
# Enable Shovel Plugin
sudo rabbitmq-plugins enable rabbitmq_shovel

# Restart RabbitMQ
sudo systemctl restart rabbitmq-server

# Verify Shovel Plugin
sudo rabbitmq-plugins list | grep shovel
```

### Version Notes

- **RabbitMQ 3.12+:** All multi-data center features fully supported
- **Federation Plugin:** Cross-cluster replication (global queues)
- **Shovel Plugin:** Cross-cluster messaging (data bridge)
- **Global Queues:** Cross-data center queues (global availability)
- **Local Consumers:** Low latency (nearby brokers)
- **Disaster Recovery:** Data center failure = failover
- **High Availability:** Geographic redundancy (99.9%+ uptime)

---

## 6️⃣ Where Multi-Data Centers Should Be Applied (With Example)

### Federation for Global Queues

**Scenario:** Global application with geographic redundancy

**Federation Configuration (federation_upstream.py):**

```python
import pika
import json
import time

# CRITICAL: Configure upstream cluster (remote data center)
connection = pika.BlockingConnection(
    pika.ConnectionParameters('remote-cluster-host')  # CRITICAL: Remote cluster
)
channel = connection.channel()

# CRITICAL: Configure federation policy
channel.policy_declare(
    policy_name='federated-queues',
    pattern='^federated_',
    definition={
        "federation-upstream": "upstream-1"  # CRITICAL: Upstream cluster
    },
    priority=1,
    apply_to='queues'
)

print("[✓] Federation configured (CRITICAL: Global Queues - Cross-Data Center)")
connection.close()
```

**Producer (federation_producer.py):**

```python
import pika
import json
import time

# CRITICAL: Connect to local cluster (low latency)
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Declare federated queue (global queue)
channel.queue_declare(
    queue='federated_messages',
    durable=True
)

# CRITICAL: Publish messages (global queue replicated)
for i in range(100):
    message = {
        "message_id": f"msg_{i+1:04d}",
        "content": f"Global Message {i+1}",
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='federated_messages',
        body=json.dumps(message)
    )
    
    if i % 10 == 0:
        print(f"[x] Published {i} global messages")

print(f"[✓] Published 100 global messages (CRITICAL: Federated Queue - Cross-Data Center)")
connection.close()
```

**Consumer (federation_consumer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f"[✓] Processing global message: {message['message_id"]}")
    
    # CRITICAL: ACK message (low latency)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# CRITICAL: Connect to local cluster (low latency)
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Consume from federated queue (global queue)
channel.queue_declare(queue='federated_messages', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='federated_messages', on_message_callback=callback)

print("[*] Local consumer (CRITICAL: Federated Queue - Low Latency)")
channel.start_consuming()
```

### Shovel for Cross-Cluster Messaging

**Shovel Configuration (shovel_config.json):**

```json
{
  "shovels": [
    {
      "name": "cluster-1-to-cluster-2",
      "src-uri": "amqp://cluster-1-host",
      "src-queue": "messages",
      "dest-uri": "amqp://cluster-2-host",
      "dest-queue": "messages",
      "prefetch-count": 10
    }
  ]
}
```

**Applying Shovel Configuration:**

```bash
# Apply shovel configuration
cat > /etc/rabbitmq/shovel.json << EOF
{
  "shovels": [
    {
      "name": "cluster-1-to-cluster-2",
      "src-uri": "amqp://cluster-1-host",
      "src-queue": "messages",
      "dest-uri": "amqp://cluster-2-host",
      "dest-queue": "messages",
      "prefetch-count": 10
    }
  ]
}
EOF

# Restart RabbitMQ
sudo systemctl restart rabbitmq-server
```

### Best Practices

**Federation:**
✅ Use federation for global availability (system available from anywhere)  
✅ Use federation for disaster recovery (data center failure = failover)  
✅ Configure upstream clusters (remote data centers)  
✅ Configure federation policies (queue name matching)  
✅ Use local consumers (low latency)  
✅ Monitor federation status (replication visible)  
✅ Use load balancing (multiple data centers)  

**Shovel:**
✅ Use shovel for cross-cluster messaging (data silos broken)  
✅ Use shovel for data migration (cross-cluster bridge)  
✅ Configure source/destination (cluster 1 → cluster 2)  
✅ Configure shovel prefetch (batch size)  
✅ Monitor shovel status (data bridge visible)  

**Global Queues:**
✅ Use global queues for cross-data center (global availability)  
✅ Configure federated queues (replicated to upstream)  
✅ Use local consumers (low latency)  
✅ Monitor global queue status (replication visible)  

**Local Consumers:**
✅ Use local consumers for low latency (nearby brokers)  
✅ Use consumer prefetch (fair dispatch)  
✅ Use consumer acknowledgment (message reliability)  

### Common Mistakes

❌ Not using federation → No global availability (data silos)  
❌ Not using shovel → No cross-cluster messaging (data silos)  
❌ Not using local consumers → High latency (cross-data center)  
❌ Not monitoring federation → Replication not visible (no status)  
❌ Not monitoring shovel → Data bridge not visible (no status)  
❌ Configuring upstream incorrectly → Federation not working (no replication)  
❌ Not using load balancing → Single data center bottleneck (no geographic redundancy)  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Single Data Center (The "Geographic Latency" Problem)**

You're building a production messaging system:

- System must be globally available (accessible from New York, London, Tokyo)
- Single data center (New York)
- Consumers in London (geographic latency: 100ms)
- Consumers in Tokyo (geographic latency: 200ms)
- No disaster recovery (data center failure = data loss)
- No global availability (system available from New York only)

Current implementation:
- Single data center (New York)
- No federation (no cross-data center replication)
- No shovel (no cross-cluster messaging)
- No global queues (no cross-data center availability)
- No local consumers (high latency for London/Tokyo)

**Problems:**
- Geographic latency (London/Tokyo consumers high latency)
- Single point of failure (data center outage)
- No disaster recovery (data center failure = data loss)
- No global availability (system available from New York only)
- **Impact:** Geographic latency, single point of failure, no disaster recovery, no global availability, poor user experience

### 🧪 Lab Tasks

**Step 1: Start RabbitMQ without federation**

```bash
# Start RabbitMQ (single data center)
docker run -d --name rabbitmq-single \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Verify: Single data center (no federation)
# curl http://localhost:15672/api/overview
# See: "federation": false
```

**Step 2: Create producer without federation**

Create `single_dc_producer.py`:

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: No federation (single data center)
channel.queue_declare(queue='messages', durable=True)

# PROBLEM: Publish messages (no cross-data center replication)
for i in range(100):
    message = {
        "message_id": f"msg_{i+1:04d}",
        "content": f"Message {i+1}",
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='messages',
        body=json.dumps(message)
    )
    
    if i % 10 == 0:
        print(f"[x] Published {i} messages")

print(f"[!] Published 100 messages (PROBLEM: Single Data Center - No Federation)")
connection.close()
```

**Step 3: Create consumer without local preference**

Create `single_dc_consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f"[!] Processing message: {message['message_id"]}")
    # PROBLEM: High latency (cross-data center)
    time.sleep(1)  # PROBLEM: Simulate geographic latency (London/Tokyo)
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: No local preference (high latency for London/Tokyo)
channel.queue_declare(queue='messages', durable=True)

# PROBLEM: Consume without local preference (high latency)
channel.basic_consume(queue='messages', on_message_callback=callback)

print("[!] Single data center consumer (PROBLEM: High Latency - No Local Preference)")
channel.start_consuming()
```

**Step 4: Simulate geographic latency**

```bash
# Terminal: Single data center consumer
python3 single_dc_consumer.py

# Terminal: Single data center producer
python3 single_dc_producer.py
```

**Expected observation:**
- Producer publishes 100 messages
- Consumer processes messages (high latency)
- No federation (no cross-data center replication)
- No global queues (no cross-data center availability)
- No local consumers (high latency for London/Tokyo)
- **Impact:** Geographic latency, single point of failure, no disaster recovery, no global availability, poor user experience

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Overview tab
- See RabbitMQ status (single data center)
- See no federation (no cross-data center replication)
- See no shovel (no cross-cluster messaging)
- See no global queues (no cross-data center availability)

### ✅ Solution & Explanation

**Solution: Implement RabbitMQ Multi-Data Centers (Federation + Shovel + Local Consumers)**

**Step 1: Enable federation plugin**

```bash
# Stop single data center RabbitMQ
docker stop rabbitmq-single
docker rm rabbitmq-single

# Start RabbitMQ with Federation Plugin (Cluster 1)
docker run -d --name rabbitmq-cluster-1 \
  -e RABBITMQ_PLUGINS="rabbitmq_federation,rabbitmq_management" \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Start RabbitMQ with Federation Plugin (Cluster 2)
docker run -d --name rabbitmq-cluster-2 \
  --link rabbitmq-cluster-1 \
  -e RABBITMQ_PLUGINS="rabbitmq_federation,rabbitmq_management" \
  -p 5673:5673 -p 15673:15673 \
  rabbitmq:3-management

# Start RabbitMQ with Federation Plugin (Cluster 3)
docker run -d --name rabbitmq-cluster-3 \
  --link rabbitmq-cluster-1 \
  -e RABBITMQ_PLUGINS="rabbitmq_federation,rabbitmq_management" \
  -p 5674:5674 -p 15674:15674 \
  rabbitmq:3-management
```

**Step 2: Configure federation policy**

```python
import pika

# SOLUTION: Configure upstream cluster (remote data center)
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Configure federation policy (global queues)
channel.policy_declare(
    policy_name='federated-queues',
    pattern='^global_',
    definition={
        "federation-upstream": "remote-cluster"
    },
    priority=1,
    apply_to='queues'
)

print("[✓] Federation configured (SOLUTION: Global Queues - Cross-Data Center)")
connection.close()
```

**Step 3: Create global producer**

Create `global_producer.py`:

```python
import pika
import json
import time

# SOLUTION: Connect to local cluster (low latency)
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Declare global queue (federated queue)
channel.queue_declare(
    queue='global_messages',
    durable=True
)

# SOLUTION: Publish messages (global queue replicated)
for i in range(100):
    message = {
        "message_id": f"msg_{i+1:04d}",
        "content": f"Global Message {i+1}",
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='global_messages',
        body=json.dumps(message)
    )
    
    if i % 10 == 0:
        print(f"[x] Published {i} global messages")

print(f"[✓] Published 100 global messages (SOLUTION: Federated Queue - Cross-Data Center)")
connection.close()
```

**Step 4: Create local consumer**

Create `local_consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f"[✓] Processing global message: {message['message_id"]}")
    
    # SOLUTION: ACK message (low latency)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# SOLUTION: Connect to local cluster (low latency)
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Consume from global queue (local consumer)
channel.queue_declare(queue='global_messages', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='global_messages', on_message_callback=callback)

print("[*] Local consumer (SOLUTION: Global Queue - Low Latency)")
channel.start_consuming()
```

**How to verify:**

```bash
# Terminal: Local consumer
python3 local_consumer.py

# Terminal: Global producer
python3 global_producer.py
```

**Expected output:**

```
# Global Producer
[x] Published 10 global messages
[x] Published 20 global messages
...
[x] Published 100 global messages
[✓] Published 100 global messages (SOLUTION: Federated Queue - Cross-Data Center)

# Local Consumer
[*] Local consumer (SOLUTION: Global Queue - Low Latency)
[✓] Processing global message: msg_0001
[✓] Processing global message: msg_0002
...
[✓] Processing global message: msg_0100
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Overview tab
3. See RabbitMQ status (multi-data center)
4. See federation enabled (cross-data center replication)
5. See global queues (cross-data center availability)
6. See local consumers (low latency)

**Simulate data center failure:**

```bash
# Stop cluster 2 (simulate data center failure)
docker stop rabbitmq-cluster-2

# Verify: System still available (cluster 1, 3)
# Global queue still available (federated to cluster 3)
# Local consumers still processing (low latency)
```

**Comparison:**

| Design | Federation | Shovel | Global Queues | Local Consumers |
|--------|-----------|--------|--------------|---------------|
| Single Data Center (old) | No | No | No | No |
| Multi-Data Center (new) | Yes | Yes | Yes | Yes |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Use federation for global availability (system available from anywhere)  
- Use federation for disaster recovery (data center failure = failover)  
- Use shovel for cross-cluster messaging (data silos broken)  
- Use local consumers (low latency)  
- Configure upstream clusters (remote data centers)  
- Configure federation policies (queue name matching)  
- Monitor federation status (replication visible)  
- Monitor shovel status (data bridge visible)  
- Use load balancing (multiple data centers)  

**❌ Don't:**
- Not using federation → No global availability (data silos)  
- Not using shovel → No cross-cluster messaging (data silos)  
- Not using local consumers → High latency (cross-data center)  
- Not monitoring federation → Replication not visible (no status)  
- Not monitoring shovel → Data bridge not visible (no status)  
- Configuring upstream incorrectly → Federation not working (no replication)  
- Not using load balancing → Single data center bottleneck (no geographic redundancy)  

### Multi-Data Center Guidelines

```
Federation:
├─ Use for global availability (system available from anywhere)
├─ Use for disaster recovery (data center failure = failover)
├─ Configure upstream clusters (remote data centers)
├─ Configure federation policies (queue name matching)
└─ Monitor federation status (replication visible)

Shovel:
├─ Use for cross-cluster messaging (data silos broken)
├─ Use for data migration (cross-cluster bridge)
├─ Configure source/destination (cluster 1 → cluster 2)
└─ Monitor shovel status (data bridge visible)

Global Queues:
├─ Use for cross-data center (global availability)
├─ Configure federated queues (replicated to upstream)
└─ Monitor global queue status (replication visible)

Local Consumers:
├─ Use for low latency (nearby brokers)
├─ Use consumer prefetch (fair dispatch)
└─ Use consumer acknowledgment (message reliability)

Disaster Recovery:
├─ Use multi-data centers (geographic redundancy)
├─ Use federation for failover (data center failure)
└─ Monitor failover status (disaster recovery visible)
```

### Production Considerations

**Scaling Multi-Data Centers:**

```bash
# Add more data centers (geographic redundancy)
docker run -d --name rabbitmq-cluster-4 \
  --link rabbitmq-cluster-1 \
  -e RABBITMQ_PLUGINS="rabbitmq_federation,rabbitmq_management" \
  -p 5675:5675 -p 15675:15675 \
  rabbitmq:3-management
```

**Monitoring Federation Status:**

```python
# Monitor federation status (replication)
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Get federation status
method = channel.connection.channel('rabbitmqadmin').policy_declare(
    policy_name='federated-queues',
    pattern='^global_',
    definition={
        "federation-upstream": "remote-cluster"
    },
    priority=1,
    apply_to='queues'
)

print(f"Federation Status: {method}")
connection.close()
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's RabbitMQ federation?**

A: RabbitMQ federation is linking clusters for global availability. Federation plugin replicates queues across clusters. Producer publishes message to cluster 1, federation replicates message to cluster 2. Global queues achieved (cross-data center). System available from anywhere.

**Q2: What's RabbitMQ shovel?**

A: RabbitMQ shovel is cross-cluster messaging bridge. Shovel plugin moves messages from source queue (cluster 1) to destination queue (cluster 2). Cross-cluster messaging achieved (data silos broken). Used for data migration, cross-cluster messaging.

**Q3: What's global queue?**

A: Global queue is RabbitMQ queue replicated across multiple data centers via federation. Producer publishes message to cluster 1, federation replicates message to cluster 2. Global queue available from anywhere (global availability). System available from New York, London, Tokyo.

**Q4: How do you achieve global availability?**

A: Use federation (linking clusters). Configure upstream clusters (remote data centers). Configure federation policies (queue name matching). Declare global queues (federated queues). Messages replicated across clusters. Global queues achieved (cross-data center). System available from anywhere.

**Q5: How do you achieve low latency?**

A: Use local consumers (nearby brokers). Consumer connects to local cluster (low latency). Consumer receives messages from local broker (not cross-data center). Low latency achieved (nearby brokers).

### Production Pitfalls

**Pitfall 1: Not using federation**
- Problem: No global availability (data silos)
- Detection: System not available from London/Tokyo
- Solution: Always use federation for global availability

**Pitfall 2: Not using local consumers**
- Problem: High latency (cross-data center)
- Detection: London/Tokyo consumers high latency (100ms, 200ms)
- Solution: Always use local consumers for low latency

**Pitfall 3: Not monitoring federation**
- Problem: Replication not visible (no status)
- Detection: Federation not working (no replication)
- Solution: Always monitor federation status (replication visible)

**Pitfall 4: Not using shovel**
- Problem: No cross-cluster messaging (data silos)
- Detection: Data silos (no cross-cluster messaging)
- Solution: Always use shovel for cross-cluster messaging

**Pitfall 5: Not using load balancing**
- Problem: Single data center bottleneck (no geographic redundancy)
- Detection: Single data center overloaded (no load balancing)
- Solution: Always use load balancing (multiple data centers)

### Advanced Multi-Data Center Concepts

**Federation with Multiple Upstreams:**

```python
# Configure federation with multiple upstreams
channel.policy_declare(
    policy_name='federated-queues',
    pattern='^global_',
    definition={
        "federation-upstream": "upstream-1,upstream-2,upstream-3"  # Multiple upstreams
    },
    priority=1,
    apply_to='queues'
)
```

**Shovel with Multiple Bridges:**

```json
{
  "shovels": [
    {
      "name": "cluster-1-to-cluster-2",
      "src-uri": "amqp://cluster-1-host",
      "src-queue": "messages",
      "dest-uri": "amqp://cluster-2-host",
      "dest-queue": "messages"
    },
    {
      "name": "cluster-1-to-cluster-3",
      "src-uri": "amqp://cluster-1-host",
      "src-queue": "messages",
      "dest-uri": "amqp://cluster-3-host",
      "dest-queue": "messages"
    }
  ]
}
```

**Local Consumers with Load Balancing:**

```python
# Load balancing across multiple data centers
connections = [
    pika.BlockingConnection(pika.ConnectionParameters('cluster-1-host')),
    pika.BlockingConnection(pika.ConnectionParameters('cluster-2-host')),
    pika.BlockingConnection(pika.ConnectionParameters('cluster-3-host'))
]

for connection in connections:
    channel = connection.channel()
    channel.queue_declare(queue='global_messages', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='global_messages', on_message_callback=callback)
    channel.start_consuming()
```

---

## 📚 Summary

RabbitMQ multi-data centers provide global availability, disaster recovery, and low latency. Federation links clusters for cross-data center replication, shovel provides cross-cluster messaging (data silos broken), and global queues provide cross-data center availability. Local consumers provide low latency (nearby brokers).

**Key takeaways:**
- Use federation for global availability (system available from anywhere)
- Use federation for disaster recovery (data center failure = failover)
- Use shovel for cross-cluster messaging (data silos broken)
- Use local consumers (low latency)
- Configure upstream clusters (remote data centers)
- Configure federation policies (queue name matching)
- Monitor federation status (replication visible)
- Monitor shovel status (data bridge visible)
- Use load balancing (multiple data centers)

**Next steps:**
- Practice with multi-data centers in your applications
- Complete all lessons in Module 04

---

**Module 04 - Advanced Concepts**  
**Lesson 07 - Complete**