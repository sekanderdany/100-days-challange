# 04-01: Clustering and High Availability

## 1️⃣ What Are RabbitMQ Clusters

**RabbitMQ Clusters** are groups of RabbitMQ nodes that act as a single logical broker. Clusters provide high availability, fault tolerance, and horizontal scalability by distributing load across multiple nodes.

Think of clustering like having multiple data centers:

- **Cluster** = Multiple data centers working together
- **Nodes** = Individual servers in each data center
- **High Availability** = If one data center fails, others take over
- **Load Balancing** = Requests distributed across data centers

**Where clustering fits in RabbitMQ architecture:**

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│  Producer A │        │  Producer B │        │  Producer C │        │  Producer D │
└──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
       │                    │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    RabbitMQ Cluster                                  │
│           (Multiple nodes, high availability)              │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────────────────┐   │
│   │              │              │              │              │   │   │
│   │    Node 1     │     Node 2     │     Node 3     │   │   │   │
│   │  (Primary)     │   (Standby)    │   (Standby)    │   │   │   │
│   │              │              │              │              │   │   │   │
│   └──────────────┘  └──────────────┘  └──────────────┘  │   │   │   │
│   │              │              │              │              │   │   │   │
│   Queues:       Queues:       Queues:       Queues:       Queues:   │   │   │
│   (Mirrored)    │   (Mirrored)   │   (Mirrored)   │   (Mirrored)   │   │   │
│   │              │              │              │              │   │   │   │
│   │              │              │              │              │   │   │   │
│   Consumers:     Consumers:     Consumers:     Consumers:     Consumers:   │   │   │
│   (Active)      │   (Active)      │   (Active)      │   (Active)      │   │   │
│   │              │              │              │              │   │   │   │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │   │   │
│                                                                      │
└────────────────────────────────────────────────────────────────────────────────┘   │   │   │
       │                    │                    │                    │   │   │   │
       ▼                    ▼                    ▼                    ▼                    ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│ Consumer A   ││ Consumer B   ││ Consumer C   ││ Consumer D   ││
│ (Node 1)    ││ (Node 2)    ││ (Node 1)    ││ (Node 3)    ││
└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘
```

**Key concepts:**
- **Cluster:** Group of RabbitMQ nodes acting as single logical broker
- **Node:** Individual RabbitMQ instance in cluster
- **Primary Node:** Active node handling client connections
- **Standby Node:** Passive node (can become primary if primary fails)
- **Mirrored Queue:** Queue replicated across multiple nodes (high availability)
- **High Availability:** No single point of failure (node failure = failover)
- **Load Balancing:** Requests distributed across nodes
- **Cluster Management:** Adding/removing nodes without downtime

---

## 2️⃣ Problems Solved by Clustering

### The "Single Point of Failure" Problem

Without clustering:

- Single RabbitMQ node handles all connections
- If node fails, entire system down
- No redundancy or failover
- System unavailable during maintenance

**Real-world failure scenario:**

A production system had:

```
Producer → Single RabbitMQ Node (Production)
         │
         ├─ Producer connects to single node
         └─ If node fails, system down

WITHOUT CLUSTERING:
├─ Single point of failure (single node)
├─ Node failure = system unavailable
├─ No redundancy or failover
├─ System downtime during node maintenance
└─ No horizontal scalability (single node limited)

PROBLEMS:
├─ Single point of failure (node crash = outage)
├─ No high availability (node failure = downtime)
├─ No load balancing (single node limit)
├─ No horizontal scalability (limited capacity)
└─ **Impact:** System unavailable, poor reliability, user experience issues
```

**Problems:**
- Single point of failure (node crash = outage)
- No high availability (node failure = downtime)
- No load balancing (single node limit)
- No horizontal scalability (limited capacity)
- **Impact:** System unavailable, poor reliability, user experience issues

After implementing clustering:
- Multiple RabbitMQ nodes provide high availability
- Node failure = automatic failover to other nodes
- Load balancing across nodes (horizontal scalability)
- System remains available during maintenance
- **Result:** High availability, fault tolerance, reliability, good user experience

### The "Limited Throughput" Problem

Without clustering:

- Single RabbitMQ node processes all messages
- Limited by single node CPU/memory
- No parallel processing capability
- System bottleneck under high load

**Example:**

```
Producer → Single RabbitMQ Node (Bottleneck)
         │
         ├─ Producer publishes 10,000 messages/second
         └─ Single node processes all (bottleneck)

WITHOUT CLUSTERING (THROUGHPUT LIMITS):
├─ Single node processes all messages
├─ Limited by CPU/memory of single node
├─ No parallel processing (serial only)
├─ System bottleneck under high load (10K messages/sec)
└─ **Impact:** System overwhelmed, poor throughput, slow processing
```

**Problems:**
- Limited throughput (single node limit)
- No parallel processing (serial only)
- System bottleneck under high load
- Slow processing (10K messages/sec limited)
- **Impact:** System overwhelmed, poor throughput, slow user experience

After implementing clustering:
- Multiple nodes process messages in parallel
- Load balancing across nodes (10K messages/sec ÷ 3 nodes = 3.3K/node)
- Horizontal scalability (add more nodes for more throughput)
- System handles high load efficiently
- **Result:** High throughput, parallel processing, efficient system

---

## 3️⃣ When You Should Use Clustering

### Development vs Production

**Development:**
- Can use single node for quick tests
- Don't need clustering for simple tests
- Use single node for low volume (few messages)
- Don't use in production code

**Production:**
- Absolutely required for high availability
- Essential for fault tolerance (node failure)
- Critical for high-throughput systems (millions of messages)
- Required for load balancing (horizontal scalability)
- Necessary for production systems (no downtime allowed)

### Clustering Scenarios

| Scenario | Clustering Strategy | Example |
|----------|----------------|----------|
| **High availability** | Mirrored queues | Financial transactions, order processing |
| **High throughput** | Cluster with multiple nodes | Data processing, ETL jobs |
| **Multi-region** | Cross-region cluster | Global messaging, multi-region |
| **Large scale** | Large cluster (10+ nodes) | High-traffic applications, gaming |

### Required vs Optional

**Required when:**
- High availability required (no downtime)
- Fault tolerance needed (node failure)
- High-throughput systems (millions of messages)
- Load balancing required (horizontal scalability)
- Production systems (99.9%+ uptime SLA)

**Optional when:**
- Single node is sufficient (low volume, development)
- Fire-and-forget messages (notifications, telemetry)
- Development and testing environments
- Low-volume systems (few messages)

### Trade-offs

**Clustering:**
✅ High availability (no single point of failure)  
✅ Fault tolerance (automatic failover)  
✅ Load balancing (horizontal scalability)  
✅ High throughput (parallel processing)  
✅ Maintenance without downtime (node rotation)  
✅ Production-ready (enterprise-grade)  
❌ More complex setup (multiple nodes)  
❌ Higher cost (multiple servers)  
❌ More monitoring (cluster health)  
❌ Requires cluster management (node sync)  
❌ Requires network configuration (node communication)  

**Single Node:**
✅ Simpler setup (one node)  
✅ Lower cost (one server)  
✅ Easier to manage (single node)  
❌ Single point of failure (node crash = outage)  
❌ No fault tolerance (no failover)  
❌ No load balancing (single node limit)  
❌ No high throughput (limited capacity)  
❌ Downtime during maintenance  

---

## 4️⃣ How RabbitMQ Clusters Work

### Clustering Configuration Process

**Setting up RabbitMQ cluster:**

```
1. Configure Erlang Cookie
   │
   ├─ All nodes in cluster must share same Erlang cookie
   ├─ Cookie: Shared secret for cluster communication
   └─ Location: /var/lib/rabbitmq/.erlang.cookie
   │
2. Start RabbitMQ Nodes
   │
   ├─ Node 1: Start with cluster name
   ├─ Node 2: Start with same cluster name
   ├─ Node 3: Start with same cluster name
   └─ Nodes discover each other (cluster formation)
   │
3. Node Discovery
   │
   ├─ Nodes discover each other via Erlang cookie
   ├─ Nodes form cluster (single logical broker)
   ├─ Primary nodes accept connections
   ├─ Standby nodes wait for failover
   └─ Cluster ready for client connections
   │
4. Client Connections
   │
   ├─ Clients connect to any node in cluster
   ├─ Connections load-balanced across nodes
   ├─ If primary node fails, clients reconnect to standby
   └─ High availability achieved
```

### Cluster Node Types

**Disc Node:**
- Stores queue metadata (definitions, bindings, exchanges)
- Lightweight node (can be diskless)
- Stores no messages (only metadata)
- Does not accept client connections (metadata only)
- Used for cluster management

**RAM Node:**
- Stores queue metadata and messages in memory
- Stores messages in RAM (fast access)
- Accepts client connections (fast message access)
- Can process messages quickly
- Messages lost if node restarts (not durable)

**Queue Master Node:**
- Stores messages for specific queue
- Designated queue master for each queue
- Processes messages for that queue
- If master fails, slave becomes master (failover)
- High availability for each queue

**Queue Slave Node:**
- Mirrors messages from queue master
- Replicates messages for redundancy
- Becomes master if original master fails
- Provides backup for queue messages

### Cluster Communication

**How nodes communicate:**

```
Erlang Cookie: Shared secret for cluster authentication

Node 1          Node 2          Node 3
│                 │                 │
│                 │                 │
├─ Cookie        ├─ Cookie          ├─ Cookie
│  "secret123"    │  "secret123"    │  "secret123"
│                 │                 │
└─ Cluster formed (same cookie)

Cluster Name: "my_cluster"

Node Discovery:
├─ Nodes discover each other (same cookie, same cluster name)
├─ Nodes exchange cluster information
├─ Nodes form cluster (single logical broker)
└─ Client connections load-balanced

Node Communication:
├─ Nodes communicate via inter-node protocol
├─ Nodes exchange cluster state (queues, bindings)
├─ Nodes replicate queue state (if mirrored queues)
└─ Nodes handle failover (primary fails, standby takes over)
```

---

## 5️⃣ Installation / Setup

**RabbitMQ Clustering is built-in RabbitMQ feature.** No installation required - just configure Erlang cookie and start multiple nodes.

### Prerequisites

- RabbitMQ server installed on all nodes
- Same RabbitMQ version across all nodes
- Network connectivity between nodes
- Erlang cookie configured (same on all nodes)
- Same cluster name across all nodes
- Understanding of cluster node types (disc, RAM, queue master/slave)

### Creating Cluster Nodes

**Using rabbitmqctl (command-line):**

```bash
# Step 1: Configure Erlang Cookie (same on all nodes)
# On Node 1
sudo rabbitmqctl set_cluster_name my_cluster
# On Node 2
sudo rabbitmqctl set_cluster_name my_cluster
# On Node 3
sudo rabbitmqctl set_cluster_name my_cluster

# Step 2: Start RabbitMQ nodes with clustering
# Start Node 1
sudo systemctl start rabbitmq-server

# Start Node 2
sudo systemctl start rabbitmq-server

# Start Node 3
sudo systemctl start rabbitmq-server

# Step 3: Verify cluster status
sudo rabbitmqctl cluster_status
```

**Using Docker:**

```bash
# Node 1
docker run -d --name rabbitmq-node1 \
  --hostname rabbitmq-node1 \
  --link rabbitmq-node1 \
  -e RABBITMQ_ERLANG_COOKIE=secret123 \
  -e RABBITMQ_NODENAME=rabbitmq-node1 \
  -e RABBITMQ_CLUSTER_NAME=my_cluster \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Node 2
docker run -d --name rabbitmq-node2 \
  --hostname rabbitmq-node2 \
  --link rabbitmq-node1 \
  -e RABBITMQ_ERLANG_COOKIE=secret123 \
  -e RABBITMQ_NODENAME=rabbitmq-node2 \
  -e RABBITMQ_CLUSTER_NAME=my_cluster \
  -p 5673:5673 \
  rabbitmq:3-management

# Node 3
docker run -d --name rabbitmq-node3 \
  --hostname rabbitmq-node3 \
  --link rabbitmq-node1 \
  -e RABBITMQ_ERLANG_COOKIE=secret123 \
  -e RABBITMQ_NODENAME=rabbitmq-node3 \
  -e RABBITMQ_CLUSTER_NAME=my_cluster \
  -p 5674:5674 \
  rabbitmq:3-management
```

### Version Notes

- **RabbitMQ 3.12+:** All clustering features fully supported
- **AMQP 0-9-1+:** Cluster protocol standard
- **Erlang Cookie:** Shared secret for cluster authentication
- **Cluster Name:** Logical cluster identifier
- **Node Types:** Disc, RAM, Queue Master/Slave
- **High Availability:** Node failover (standby becomes primary)
- **Load Balancing:** Connections distributed across nodes
- **Mirrored Queues:** Queue replication across nodes

---

## 6️⃣ Where Clustering Should Be Applied (With Example)

### Cluster with Mirrored Queues

**Scenario:** Financial transaction system with high availability

**Cluster Configuration (rabbitmq_cluster.conf):**

```json
{
  "cluster_nodes": [
    {
      "name": "rabbitmq-node1",
      "cluster_name": "my_cluster",
      "cookie": "secret123",
      "type": "disc"
    },
    {
      "name": "rabbitmq-node2",
      "cluster_name": "my_cluster",
      "cookie": "secret123",
      "type": "ram"
    },
    {
      "name": "rabbitmq-node3",
      "cluster_name": "my_cluster",
      "cookie": "secret123",
      "type": "ram"
    }
  ],
  "policies": {
    "ha-mirrored-all": {
      "pattern": ".*",
      "definition": {
        "ha-mode": "all",
        "ha-sync-mode": "automatic"
      },
      "priority": 1,
      "apply-to": "queues"
    }
  }
}
```

**Applying Cluster Configuration:**

```bash
# Apply cluster policy (mirrored queues for high availability)
sudo rabbitmqctl set_policy ha-mirrored_all "^.*$" \
  '{"ha-mode":"all","ha-sync-mode":"automatic"}'

# Verify cluster status
sudo rabbitmqctl cluster_status
```

**Producer (cluster_client.py):**

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', port=5672)  # Connect to any node
)
channel = connection.channel()

# CRITICAL: Declare mirrored queue (for high availability)
channel.queue_declare(
    queue='transactions',
    durable=True,  # CRITICAL: Queue persists
    arguments={
        "x-ha-policy": "ha-mirrored-all"  # CRITICAL: Mirror across nodes
    }
)

# CRITICAL: Publish transactions (load balanced across nodes)
for i in range(1000):
    transaction = {
        "transaction_id": f"txn_{i+1:04d}",
        "amount": 100 + i,
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='transactions',
        body=json.dumps(transaction)
    )
    
    if i % 100 == 0:
        print(f"[x] Published {i} transactions")

print(f"[✓] Published 1000 transactions to cluster (mirrored queue)")
connection.close()
```

**Consumer (cluster_consumer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    transaction = json.loads(body)
    print(f"[✓] Processing transaction: {transaction['transaction_id']}")
    
    # CRITICAL: Acknowledge after processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', port=5672)  # Connect to any node
)
channel = connection.channel()

# CRITICAL: Consume from mirrored queue (high availability)
channel.queue_declare(queue='transactions', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='transactions', on_message_callback=callback, auto_ack=False)

print("[*] Cluster consumer waiting (mirrored queue - high availability)")
channel.start_consuming()
```

**How to test cluster:**

```bash
# Terminal: Start all nodes
# Node 1
docker start rabbitmq-node1

# Node 2
docker start rabbitmq-node2

# Node 3
docker start rabbitmq-node3

# Wait for cluster formation
sleep 10

# Terminal: Producer
python3 cluster_client.py

# Terminal: Consumers (multiple)
python3 cluster_consumer.py &
python3 cluster_consumer.py &
python3 cluster_consumer.py &
```

**Expected output:**

```
# Cluster Client
[x] Published 100 transactions
[x] Published 200 transactions
...
[x] Published 1000 transactions
[✓] Published 1000 transactions to cluster (mirrored queue)

# Cluster Consumers (running in parallel)
[*] Cluster consumer waiting (mirrored queue - high availability)
[✓] Processing transaction: txn_0001
[✓] Processing transaction: txn_0002
...
[✓] Processing transaction: txn_1000
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Admin tab → Cluster tab
3. See cluster nodes (3 nodes: rabbitmq-node1, rabbitmq-node2, rabbitmq-node3)
4. See mirrored queues (transactions queue mirrored across nodes)
5. See load balancing (connections distributed across nodes)
6. See high availability (if node fails, others take over)

### Best Practices

**Cluster Configuration:**
✅ Use same Erlang cookie across all nodes  
✅ Use same cluster name across all nodes  
✅ Use mirrored queues for high availability  
✅ Use auto-sync mode for queue mirroring  
✅ Monitor cluster health (node status, queue mirroring)  
✅ Use disc nodes for lightweight metadata storage  
✅ Use RAM nodes for fast message processing  
✅ Use queue master/slave for queue failover  

**Node Configuration:**
✅ Configure disc node for cluster metadata (lightweight)  
✅ Configure RAM node for fast message processing  
✅ Configure queue master/slave for queue failover  
✅ Configure same Erlang cookie on all nodes  
✅ Configure same cluster name on all nodes  
✅ Monitor node health (CPU, memory, disk)  

**Mirrored Queues:**
✅ Use mirrored queues for critical queues (high availability)  
✅ Use auto-sync mode for queue mirroring  
✅ Use same queue name across all nodes  
✅ Configure durable queues (data persistence)  
✅ Monitor queue mirroring status (sync mode)  

**Client Configuration:**
✅ Connect to any node in cluster (load balancing)  
✅ Use durable queues (data persistence)  
✅ Handle connection failover (reconnect to other nodes)  
✅ Monitor connection status (node health)  
✅ Use publisher confirms (message reliability)  

### Common Mistakes

❌ Different Erlang cookies → Nodes can't form cluster  
❌ Different cluster names → Nodes can't form cluster  
❌ Not using mirrored queues → No high availability  
❌ Not using auto-sync mode → Manual sync required  
❌ Not monitoring cluster health → Failover not visible  
❌ Not configuring durable queues → Data loss on node failure  
❌ Connecting to specific node → No load balancing  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Single Point of Failure (The "System Outage" Problem)**

You're building a production messaging system:

- System must be highly available (99.9%+ uptime SLA)
- Single RabbitMQ node handles all connections
- Node failure = system outage (no failover)
- No redundancy or load balancing

Current implementation:
- Single RabbitMQ node in production
- No clustering (single point of failure)
- No mirrored queues (no redundancy)
- No failover (node crash = outage)

**Problems:**
- Single point of failure (node crash = outage)
- No high availability (node failure = downtime)
- No load balancing (single node limit)
- System outage during maintenance
- **Impact:** System unavailable, lost revenue, poor user experience

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ cluster (3 nodes)**

```bash
# Stop any existing RabbitMQ containers
docker stop $(docker ps -a | grep rabbitmq | awk '{print $1}')
docker rm $(docker ps -a | grep rabbitmq | awk '{print $1}')

# Start RabbitMQ cluster (3 nodes)
docker run -d --name rabbitmq-node1 \
  --hostname rabbitmq-node1 \
  --link rabbitmq-node1 \
  -e RABBITMQ_ERLANG_COOKIE=secret123 \
  -e RABBITMQ_NODENAME=rabbitmq-node1 \
  -e RABBITMQ_CLUSTER_NAME=my_cluster \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

docker run -d --name rabbitmq-node2 \
  --hostname rabbitmq-node2 \
  --link rabbitmq-node1 \
  -e RABBITMQ_ERLANG_COOKIE=secret123 \
  -e RABBITMQ_NODENAME=rabbitmq-node2 \
  -e RABBITMQ_CLUSTER_NAME=my_cluster \
  -p 5673:5673 \
  rabbitmq:3-management

docker run -d --name rabbitmq-node3 \
  --hostname rabbitmq-node3 \
  --link rabbitmq-node1 \
  -e RABBITMQ_ERLANG_COOKIE=secret123 \
  -e RABBITMQ_NODENAME=rabbitmq-node3 \
  -e RABBITMQ_CLUSTER_NAME=my_cluster \
  -p 5674:5674 \
  rabbitmq:3-management
```

**Step 2: Create producer without clustering**

Create `single_node_producer.py`:

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: Single node, no clustering
channel.queue_declare(queue='transactions', durable=True)

# PROBLEM: Publish 1000 messages (single node bottleneck)
for i in range(1000):
    transaction = {
        "transaction_id": f"txn_{i+1:04d}",
        "amount": 100 + i,
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='transactions',
        body=json.dumps(transaction)
    )
    
    if i % 100 == 0:
        print(f"[x] Published {i} messages")

print(f"[✓] Published 1000 messages (PROBLEM: Single node - no failover)")
connection.close()
```

**Step 3: Create consumer without clustering**

Create `single_node_consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    transaction = json.loads(body)
    print(f"[✓] Processing transaction: {transaction['transaction_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: Single node, no failover
channel.queue_declare(queue='transactions', durable=True)
channel.basic_consume(queue='transactions', on_message_callback=callback)

print("[*] Single node consumer (PROBLEM: No failover)")
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal: Single node consumer
python3 single_node_consumer.py

# Terminal: Single node producer
python3 single_node_producer.py
```

**Expected observation:**
- Producer publishes 1000 messages to single node
- Single node processes all messages
- Single point of failure (if node crashes, system down)
- No failover (system outage)
- **Impact:** System unavailable, lost revenue, poor user experience

**Step 5: Simulate node failure**

```bash
# Stop single node (simulate node failure)
docker stop rabbitmq-node1

# Verify: System unavailable
# Producer can't connect
# Consumer stops processing
```

**Expected observation:**
- Producer connection refused (node down)
- Consumer stops processing (node down)
- System unavailable (single point of failure)
- **Impact:** System outage, no failover

### ✅ Solution & Explanation

**Solution: Implement RabbitMQ Cluster with Mirrored Queues**

**Create cluster producer (cluster_producer.py):**

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', port=5672)  # SOLUTION: Connect to any node
)
channel = connection.channel()

# SOLUTION: Declare mirrored queue (for high availability)
channel.queue_declare(
    queue='transactions',
    durable=True,  # SOLUTION: Queue persists
    arguments={
        "x-ha-policy": "ha-mirrored-all"  # SOLUTION: Mirror across nodes
    }
)

# SOLUTION: Publish 1000 messages (load balanced across cluster)
for i in range(1000):
    transaction = {
        "transaction_id": f"txn_{i+1:04d}",
        "amount": 100 + i,
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='transactions',
        body=json.dumps(transaction)
    )
    
    if i % 100 == 0:
        print(f"[x] Published {i} messages")

print(f"[✓] Published 1000 messages to cluster (SOLUTION: Mirrored queue - high availability)")
connection.close()
```

**Create cluster consumer (cluster_consumer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    transaction = json.loads(body)
    print(f"[✓] Processing transaction: {transaction['transaction_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', port=5672)  # SOLUTION: Connect to any node
)
channel = connection.channel()

# SOLUTION: Consume from mirrored queue (high availability)
channel.queue_declare(queue='transactions', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='transactions', on_message_callback=callback)

print("[*] Cluster consumer (SOLUTION: Mirrored queue - high availability)")
channel.start_consuming()
```

**How to verify:**

```bash
# Clear RabbitMQ
docker stop $(docker ps -a | grep rabbitmq | awk '{print $1}')
docker rm $(docker ps -a | grep rabbitmq | awk '{print $1}')

# Start RabbitMQ cluster (3 nodes)
docker run -d --name rabbitmq-node1 \
  --hostname rabbitmq-node1 \
  --link rabbitmq-node1 \
  -e RABBITMQ_ERLANG_COOKIE=secret123 \
  -e RABBITMQ_NODENAME=rabbitmq-node1 \
  -e RABBITMQ_CLUSTER_NAME=my_cluster \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

docker run -d --name rabbitmq-node2 \
  --hostname rabbitmq-node2 \
  --link rabbitmq-node1 \
  -e RABBITMQ_ERLANG_COOKIE=secret123 \
  -e RABBITMQ_NODENAME=rabbitmq-node2 \
  -e RABBITMQ_CLUSTER_NAME=my_cluster \
  -p 5673:5673 \
  rabbitmq:3-management

docker run -d --name rabbitmq-node3 \
  --hostname rabbitmq-node3 \
  --link rabbitmq-node1 \
  -e RABBITMQ_ERLANG_COOKIE=secret123 \
  -e RABBITMQ_NODENAME=rabbitmq-node3 \
  -e RABBITMQ_CLUSTER_NAME=my_cluster \
  -p 5674:5674 \
  rabbitmq:3-management

# Wait for cluster formation
sleep 10

# Terminal: Multiple consumers (load balancing)
python3 cluster_consumer.py &
python3 cluster_consumer.py &
python3 cluster_consumer.py

# Terminal: Cluster producer
python3 cluster_producer.py
```

**Expected output:**

```
# Cluster Producer
[x] Published 100 messages
[x] Published 200 messages
...
[x] Published 1000 messages
[✓] Published 1000 messages to cluster (SOLUTION: Mirrored queue - high availability)

# Cluster Consumers (running in parallel)
[*] Cluster consumer 1 (SOLUTION: Mirrored queue - high availability)
[✓] Processing transaction: txn_0001
[✓] Processing transaction: txn_0002
...
[*] Cluster consumer 2 (SOLUTION: Mirrored queue - high availability)
[✓] Processing transaction: txn_0334
[✓] Processing transaction: txn_0335
...
[*] Cluster consumer 3 (SOLUTION: Mirrored queue - high availability)
[✓] Processing transaction: txn_0667
[✓] Processing transaction: txn_0668
...
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Admin tab → Cluster tab
3. See cluster nodes (3 nodes: rabbitmq-node1, rabbitmq-node2, rabbitmq-node3)
4. See mirrored queues (transactions queue mirrored across nodes)
5. See load balancing (connections distributed across nodes)
6. See high availability (if node fails, others take over)

**Simulate node failure:**

```bash
# Stop one node (simulate node failure)
docker stop rabbitmq-node2

# Verify: System still available (other nodes take over)
# Cluster still operational (2 nodes)
# Producer connects to remaining nodes (load balancing)
# Consumers on remaining nodes (failover)
```

**Comparison:**

| Design | High Availability | Load Balancing | Failover |
|--------|----------------|---------------|----------|
| Single Node (old) | No | No | No (outage) |
| Cluster (new) | Yes | Yes | Yes |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Use same Erlang cookie across all nodes  
- Use same cluster name across all nodes  
- Use mirrored queues for high availability  
- Use auto-sync mode for queue mirroring  
- Monitor cluster health (node status, queue mirroring)  
- Use disc nodes for lightweight metadata storage  
- Use RAM nodes for fast message processing  
- Configure durable queues (data persistence)  
- Handle connection failover (reconnect to other nodes)  
- Use publisher confirms (message reliability)  

**❌ Don't:**
- Different Erlang cookies → Nodes can't form cluster  
- Different cluster names → Nodes can't form cluster  
- Not using mirrored queues → No high availability  
- Not using auto-sync mode → Manual sync required  
- Not monitoring cluster health → Failover not visible  
- Not configuring durable queues → Data loss on node failure  
- Connecting to specific node → No load balancing  
- Mixing RabbitMQ versions → Cluster instability  

### Cluster Guidelines

```
Erlang Cookie:
├─ Same cookie on all nodes (cluster authentication)
└─ Secure cookie (permissions: 400)

Cluster Name:
├─ Same cluster name on all nodes
└─ Logical cluster identifier

Node Types:
├─ Disc node: Metadata storage (lightweight)
├─ RAM node: Fast message processing
└─ Queue master/slave: Queue failover

Mirrored Queues:
├─ Use for critical queues (high availability)
├─ Auto-sync mode (automatic mirroring)
└─ Durable queues (data persistence)

Cluster Health:
├─ Monitor node status (CPU, memory, disk)
├─ Monitor queue mirroring status (sync mode)
└─ Alert on node failure (cluster partition)

Failover:
├─ Node failure detection (automatic)
├─ Standby node becomes primary (automatic)
├─ Client reconnection (automatic)
└─ Minimal downtime (failover seconds)
```

### Production Considerations

**Cluster Scaling:**

```bash
# Add more nodes to cluster (horizontal scaling)
docker run -d --name rabbitmq-node4 \
  --hostname rabbitmq-node4 \
  --link rabbitmq-node1 \
  -e RABBITMQ_ERLANG_COOKIE=secret123 \
  -e RABBITMQ_NODENAME=rabbitmq-node4 \
  -e RABBITMQ_CLUSTER_NAME=my_cluster \
  -p 5675:5675 \
  rabbitmq:3-management

# Cluster now has 4 nodes (more throughput)
```

**Cluster Monitoring:**

```python
# Monitor cluster health
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', port=5672)
)
channel = connection.channel()

# Get cluster status
nodes = pika.adapters.utils.ConnectionParameters.hosts  # Get cluster nodes
for node in nodes:
    print(f"Node: {node}")

# Get queue status (mirrored)
method = channel.connection.channel('rabbitmqadmin').queue_declare(
    queue='transactions',
    passive=True
)

print(f"Cluster health: {len(nodes)} nodes operational")
connection.close()
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's RabbitMQ clustering?**

A: RabbitMQ clustering is grouping multiple RabbitMQ nodes that act as a single logical broker. Clusters provide high availability, fault tolerance, and horizontal scalability. Nodes share Erlang cookie and cluster name for cluster authentication.

**Q2: What's Erlang cookie?**

A: Erlang cookie is a shared secret file used for cluster authentication. All nodes in cluster must have same Erlang cookie (location: /var/lib/rabbitmq/.erlang.cookie). Nodes with different cookies can't form cluster.

**Q3: What's difference between disc, RAM, and queue master/slave nodes?**

A: Disc nodes store queue metadata (definitions, bindings, exchanges) - lightweight, no messages. RAM nodes store queue metadata and messages in memory - fast access, messages lost on restart. Queue master/slave nodes store messages for specific queue - queue master processes messages, queue slave mirrors messages for redundancy. Queue master fails, slave becomes master (failover).

**Q4: What's mirrored queue?**

A: Mirrored queue is queue replicated across multiple nodes. Messages published to mirrored queue are copied to all nodes in cluster. If one node fails, others have copy of messages (high availability). Provides data redundancy and failover.

**Q5: How does RabbitMQ handle node failure?**

A: If primary node fails, standby node becomes primary automatically. Client connections reconnect to new primary. Queues mirrored across other nodes provide data redundancy. Minimal downtime (failover seconds). High availability achieved automatically.

### Production Pitfalls

**Pitfall 1: Different Erlang cookies**
- Problem: Nodes can't form cluster
- Detection: Cluster status shows nodes disconnected
- Solution: Always use same Erlang cookie on all nodes

**Pitfall 2: Not using mirrored queues**
- Problem: No high availability (queue data on single node)
- Detection: Queue not mirrored across nodes
- Solution: Always use mirrored queues for critical queues

**Pitfall 3: Not monitoring cluster health**
- Problem: Failover not visible
- Detection: Node failure not detected
- Solution: Always monitor cluster health (node status, queue mirroring)

**Pitfall 4: Mixing RabbitMQ versions**
- Problem: Cluster instability
- Detection: Nodes can't communicate (protocol mismatch)
- Solution: Always use same RabbitMQ version across cluster

**Pitfall 5: Connecting to specific node**
- Problem: No load balancing
- Detection: Connections not distributed across nodes
- Solution: Connect to any node (let load balancer distribute)

### Advanced Cluster Concepts

**Multiple Clusters:**

```bash
# Cluster 1: Production cluster (US)
rabbitmq_cluster_1:
  ├─ rabbitmq-node1 (disc)
  ├─ rabbitmq-node2 (ram)
  └─ rabbitmq-node3 (ram)

# Cluster 2: Disaster recovery cluster (DR)
rabbitmq_cluster_2:
  ├─ rabbitmq-dr1 (disc)
  ├─ rabbitmq-dr2 (ram)
  └─ rabbitmq-dr3 (ram)

# Federation: Link clusters (cluster to cluster)
# Use federation plugin to link clusters
```

**Shovel for Cross-Cluster:**

```json
{
  "shovels": [
    {
      "name": "prod_to_dr_shovel",
      "src-uri": "amqp://prod-cluster-node1",
      "src-queue": "transactions",
      "dest-uri": "amqp://dr-cluster-node1",
      "dest-exchange": "transactions"
    }
  ]
}
```

---

## 📚 Summary

RabbitMQ clustering provides high availability, fault tolerance, and horizontal scalability by grouping multiple nodes into a single logical broker. Mirrored queues provide data redundancy and automatic failover.

**Key takeaways:**
- Use RabbitMQ clusters for high availability
- Use same Erlang cookie and cluster name across nodes
- Use mirrored queues for data redundancy
- Monitor cluster health (node status, queue mirroring)
- Handle node failure gracefully (automatic failover)
- Scale horizontally (add more nodes for throughput)
- Use disc nodes for metadata (lightweight)
- Use RAM nodes for fast processing
- Use queue master/slave for queue failover

**Next steps:**
- Practice with clustering in your applications
- Learn about RabbitMQ security (next lesson)
- Explore monitoring and alerting
- Learn about performance tuning
- Complete all lessons in Module 04

---

**Module 04 - Advanced Concepts**  
**Lesson 01 - Complete**