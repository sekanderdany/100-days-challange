# 03-07: Architectural Patterns

## 1️⃣ What Are Architectural Patterns

**Architectural Patterns** in RabbitMQ are advanced messaging patterns that solve complex enterprise problems like cross-node communication, high availability, large-scale fanout, and message routing between clusters. These patterns go beyond basic producer-consumer communication.

Think of architectural patterns like logistics networks:

- **Shovel** = Package forwarding between warehouses
- **Federation** = Global logistics network (cross-region)
- **Consistent Hashing** = Same package always goes to same warehouse
- **Cluster** = Multiple warehouses with shared inventory
- **Super Streams** = Large broadcast distribution (regional warehouses)
- **Exchange-to-Exchange Bindings** = Warehouse-to-warehouse forwarding

**Where architectural patterns fit in RabbitMQ architecture:**

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│  Producer A │        │  Producer B │        │  Producer C │        │  Producer D │
└──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
       │                    │                    │                    │
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                RabbitMQ Cluster                    │
│                (High Availability)                 │
│         ┌─────────────────────────────────────┐   │
│         │  Node 1        │         │   │
│         │  Shovel:       │         │   │
│         │  Node 2  ↔ Node 3│         │   │
│         │  Federation:    │         │   │
│         │  Node 4  ↔ Node 5│         │   │
│         │  Consistent     │         │   │
│         │  Hashing        │         │   │
│         │  Cluster:       │         │   │
│         │  Multi-node     │         │   │
│         └─────────────────────────────────────┘   │
│                                              │   │
│         ┌─────────────────────────────────────┐   │
│         │        Exchange Network        │   │
│         │  (Routing & Distribution)        │   │
│         │                                  │   │
│         │  ┌────────────────────────────┐   │
│         │  │ Direct Exchange          │   │
│         │  │ Fanout Exchange          │   │
│         │  │ Topic Exchange           │   │
│         │  │ Headers Exchange         │   │
│         │  └────────────────────────────┘   │
│         │  (E2E Routing)                │   │
│         │                                  │   │
│         │  ┌────────────────────────────┐   │
│         │  │   Super Streams         │   │
│         │  │  (Large Fanout)         │   │
│         │  │  (Partitioned)           │   │
│         │  └────────────────────────────┘   │
│         └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
       │
       ├──────────────────┬──────────────────┬──────────────────┬──────────────────┐
       ▼                  ▼                  ▼                  ▼                  ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│ Consumer A   ││ Consumer B   ││ Consumer C   ││ Consumer D   ││ Consumer E   │
│ (Node 1)    ││ (Node 2)    ││ (Node 3)    ││ (Node 4)    ││ (Node 5)    │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘
```

**Key concepts:**
- **Shovel:** Cross-node message movement (package forwarding)
- **Federation:** Cross-cluster message movement (global logistics)
- **Consistent Hashing:** Same message always goes to same queue (same warehouse)
- **Cluster:** High availability (multiple nodes, shared inventory)
- **Super Streams:** Large fanout performance (regional distribution)
- **Exchange-to-Exchange Bindings:** Warehouse-to-warehouse forwarding (exchange forwarding)
- **Alternate Exchange:** High availability (backup exchange for failover)

---

## 2️⃣ Problems Solved by Architectural Patterns

### The "Cross-Node Message Movement" Problem

Without architectural patterns:

- Producer and consumer on different nodes
- No built-in cross-node communication
- Manual message forwarding required
- Tight coupling between nodes

**Real-world failure scenario:**

A multi-region system had:

```
Producer → Node 1 (Region A)
          │
          ├─ Producer sends messages to Node 1
          └─ Need to forward to Node 2 (Region B)

WITHOUT ARCHITECTURAL PATTERNS:
├─ Producer must manually forward to Node 2
├─ Node 2 must manually pull from Node 1
├─ Tight coupling between Node 1 and Node 2
├─ No automatic cross-node forwarding
└─ Complex configuration (manual setup)

PROBLEMS:
├─ No automatic cross-node forwarding
├─ Manual message forwarding (complex)
├─ Tight coupling between nodes
├─ No resilience (node failure = no forwarding)
└─ Difficult to scale (add new region = manual configuration)
```

**Problems:**
- No automatic cross-node message forwarding
- Manual message forwarding (complex)
- Tight coupling between nodes
- No resilience (node failure = no forwarding)
- Difficult to scale (add new region = manual configuration)
- **Impact:** Manual intervention, complex configuration, poor scalability, poor resilience

After implementing shovel:
- Automatic cross-node message forwarding
- Loose coupling (shovel handles forwarding)
- Resilience (shovel handles node failure)
- Easy to scale (add new node = configure shovel)
- **Result:** Automatic cross-node forwarding, loose coupling, easy scalability, high resilience

### The "Cross-Cluster Communication" Problem

Without architectural patterns:

- Producers and consumers in different clusters
- No built-in cross-cluster communication
- Manual cluster-to-cluster forwarding required
- Global message routing difficult

**Example:**

```
Producer → Cluster A (US)
          │
          ├─ Producer sends messages to Cluster A
          └─ Need to forward to Cluster B (EU)

WITHOUT ARCHITECTURAL PATTERNS:
├─ No automatic cross-cluster forwarding
├─ Manual cluster-to-cluster forwarding required
├─ Tight coupling between clusters
├─ No global message routing
└─ Complex configuration (manual setup)

PROBLEMS:
├─ No automatic cross-cluster forwarding
├─ Manual cluster-to-cluster forwarding (complex)
├─ Tight coupling between clusters
├─ No global message routing
└─ Difficult to manage (multiple clusters)
```

**Problems:**
- No automatic cross-cluster forwarding
- Manual cluster-to-cluster forwarding (complex)
- Tight coupling between clusters
- No global message routing
- Difficult to manage (multiple clusters)
- **Impact:** Manual intervention, complex configuration, poor global routing, difficult management

After implementing federation:
- Automatic cross-cluster message forwarding
- Loose coupling (federation handles forwarding)
- Global message routing (federation routes between clusters)
- Easy to manage (federation handles multiple clusters)
- **Result:** Automatic cross-cluster forwarding, loose coupling, global routing, easy management

### The "Large Fanout Performance" Problem

Without architectural patterns:

- Producer broadcasts to millions of consumers
- Fanout exchange copies message to all queues
- CPU bottleneck on exchange (millions of copies)
- Message delivery delay

**Example:**

```
Producer → Fanout Exchange → 1,000,000 Queues → 1,000,000 Consumers
          │
          ├─ Producer broadcasts: "Global update"
          └─ Fanout exchange copies to all 1M queues

WITHOUT ARCHITECTURAL PATTERNS (FANOUT):
├─ Fanout exchange copies message to all 1M queues
├─ CPU bottleneck on exchange (millions of copies)
├─ Memory bottleneck on exchange (1M copies in memory)
├─ Message delivery delay (seconds to minutes)
└─ System appears unresponsive

PROBLEMS:
├─ CPU bottleneck (millions of copies)
├─ Memory bottleneck (1M copies in memory)
├─ Message delivery delay (seconds to minutes)
├─ System unresponsive
└─ Poor throughput (1M copies take minutes)
```

**Problems:**
- CPU bottleneck (millions of copies)
- Memory bottleneck (1M copies in memory)
- Message delivery delay (seconds to minutes)
- System unresponsive
- Poor throughput (1M copies take minutes)
- **Impact:** System unresponsive, poor user experience, high latency, poor throughput

After implementing super streams:
- Fanout exchange partitions messages (super stream nodes)
- Each super stream node handles subset of queues
- CPU distributed across super stream nodes (parallel processing)
- Memory distributed across super stream nodes (1M copies partitioned)
- Message delivery improved (milliseconds instead of minutes)
- **Result:** Improved throughput, lower latency, better resource utilization, good user experience

---

## 3️⃣ When You Should Use Architectural Patterns

### Development vs Production

**Development:**
- Can use single node for quick tests
- Don't need architectural patterns for simple tests
- Use basic producer-consumer for development
- Don't use in production code

**Production:**
- Absolutely required for cross-node communication (shovel)
- Essential for cross-cluster communication (federation)
- Critical for high availability (cluster)
- Required for large fanout (super streams)
- Necessary for consistent hashing (same message to same queue)
- Required for high-throughput systems (millions of messages)
- Necessary for cross-region communication (global routing)

### Architectural Pattern Scenarios

| Scenario | Architectural Pattern | Example |
|----------|---------------------|----------|
| **Cross-node forwarding** | Shovel | Region-to-region message forwarding |
| **Cross-cluster forwarding** | Federation | Global message routing, multi-cluster |
| **High availability** | Cluster | Node failure resilience |
| **Large fanout** | Super Streams | Broadcast to millions of consumers |
| **Consistent routing** | Consistent Hashing | Same message to same queue (same warehouse) |
| **Backup exchange** | Alternate Exchange | Exchange failover |
| **Exchange forwarding** | Exchange-to-Exchange Bindings | Exchange-to-exchange forwarding |

### Required vs Optional

**Required when:**
- Cross-node communication (shovel)
- Cross-cluster communication (federation)
- High availability (cluster)
- Large fanout (millions of consumers)
- Consistent routing (same message to same queue)
- Global message routing (multi-cluster)
- High-throughput systems (millions of messages)
- Cross-region communication

**Optional when:**
- Single node (no cross-node forwarding)
- Single cluster (no cross-cluster forwarding)
- Small fanout (thousands of consumers)
- Development and testing environments
- Low-throughput systems (few messages)

### Trade-offs

**Architectural Patterns:**
✅ Cross-node communication (shovel)  
✅ Cross-cluster communication (federation)  
✅ High availability (cluster)  
✅ Large fanout performance (super streams)  
✅ Consistent routing (consistent hashing)  
✅ Global message routing (federation)  
✅ Backup exchanges (alternate exchange)  
❌ More complex setup (shovel, federation configuration)  
❌ More resource usage (shovel, federation processes)  
❌ Higher latency (cross-node, cross-cluster forwarding)  
❌ Requires advanced RabbitMQ knowledge  
❌ Difficult debugging (architectural patterns)  

**No Architectural Patterns:**
✅ Simpler setup (single node, single cluster)  
✅ Lower latency (no cross-node, cross-cluster forwarding)  
✅ Easier to debug (basic producer-consumer)  
❌ No cross-node forwarding (manual forwarding required)  
❌ No cross-cluster forwarding (manual cluster-to-cluster required)  
❌ No high availability (single point of failure)  
❌ No large fanout performance (CPU/memory bottleneck)  
❌ No global message routing (no multi-cluster routing)  

---

## 4️⃣ How Architectural Patterns Work

### Shovel Configuration Process

**Setting up shovel:**

```
1. Source Connection (Source Node)
   │
   ├─ Connects to source RabbitMQ node
   ├─ Creates connection to source queue
   └─ Ready to shovel messages
   │
2. Destination Connection (Destination Node)
   │
   ├─ Connects to destination RabbitMQ node
   ├─ Creates connection to destination queue
   └─ Ready to receive messages
   │
3. Shovel Configuration
   │
   ├─ Configured with source queue (from Source Connection)
   ├─ Configured with destination exchange (to Destination Connection)
   ├─ Starts shoveling messages
   └─ Automatic cross-node forwarding
   │
4. Message Shoveling
   │
   ├─ Shovel reads message from source queue
   ├─ Shovel publishes message to destination exchange
   └─ Automatic forwarding (continuous)
   │
5. Error Handling
   │
   ├─ Source node down: Shovel pauses, retries
   ├─ Destination node down: Shovel pauses, retries
   └─ Both nodes down: Shovel stops
```

### Federation Configuration Process

**Setting up federation:**

```
1. Upstream Cluster (Producer Cluster)
   │
   ├─ RabbitMQ nodes (Cluster A)
   ├─ Exchanges and queues
   └─ Ready to publish messages
   │
2. Downstream Cluster (Consumer Cluster)
   │
   ├─ RabbitMQ nodes (Cluster B)
   ├─ Federation links (from Cluster A)
   ├─ Exchanges and queues (mirrored from Cluster A)
   └─ Ready to receive messages
   │
3. Federation Link Configuration
   │
   ├─ Configured with upstream exchange (from Cluster A)
   ├─ Configured with downstream exchange (to Cluster B)
   ├─ Starts federating messages
   └─ Automatic cross-cluster forwarding
   │
4. Message Federation
   │
   ├─ Federation link reads message from upstream exchange
   ├─ Federation link publishes message to downstream exchange
   └─ Automatic forwarding (continuous)
   │
5. Cluster Communication
   │
   ├─ Upstream cluster publishes messages
   ├─ Federation link forwards to downstream cluster
   └─ Downstream cluster processes messages
```

### Super Streams Configuration Process

**Setting up super streams:**

```
1. Fanout Exchange (Large Fanout)
   │
   ├─ Fanout exchange with millions of queues
   ├─ Consumer connections (millions)
   └─ Ready to broadcast messages
   │
2. Super Stream Nodes
   │
   ├─ Super stream nodes connect to fanout exchange
   ├─ Each super stream node handles subset of queues
   ├─ Partitions fanout exchange (load balancing)
   └─ Ready to process messages
   │
3. Super Stream Configuration
   │
   ├─ Configured with fanout exchange (to partition)
   ├─ Starts super streaming
   └─ Automatic fanout partitioning
   │
4. Message Streaming
   │
   ├─ Super stream node reads message from fanout exchange
   ├─ Super stream node publishes to subset of queues
   └─ Automatic partitioning (continuous)
   │
5. Consumer Connections
   │
   ├─ Consumers connect to specific super stream node
   ├─ Consumers receive messages from super stream node
   └─ Improved throughput (CPU distributed)
```

### Consistent Hashing Mechanism

**How consistent hashing works:**

```
Producer → Exchange → Consistent Hashing
                      │
                      ├─ Message published with routing key
                      ├─ Consistent hashing algorithm calculates hash
                      ├─ Hash determines target queue (same queue for same key)
                      └─ Same message always goes to same queue

Consistent Hashing:
├─ Message with routing key: "orders.user_123"
├─ Hash algorithm: hash("orders.user_123") → 12345
├─ Queue selection: 12345 % 10 queues = 5 (queue_5)
└─ Message always goes to queue_5 (same user_123 → same queue)

BENEFITS:
├─ Same message always goes to same queue (consistent routing)
├─ User-specific queues (same user → same queue)
├─ Message ordering maintained (same user → same queue)
└─ Load balancing (multiple queues for different users)
```

---

## 5️⃣ Installation / Setup

**Architectural Patterns are built-in RabbitMQ features.** No installation required - just use shovel, federation, super streams, cluster, and consistent hashing.

### Prerequisites

- RabbitMQ server running
- RabbitMQ shovel plugin installed
- RabbitMQ federation plugin installed
- RabbitMQ consistent hash exchange plugin installed
- Multiple RabbitMQ nodes (for cluster, federation)
- Understanding of cross-node, cross-cluster communication

### Creating Shovel

**Using rabbitmqadmin:**

```bash
# Create shovel (cross-node message forwarding)
sudo rabbitmqctl set_parameter shovel \
  my_shovel \
  '{"src-uri": "amqp://source-node", "src-queue": "source_queue", \
    "dest-uri": "amqp://dest-node", "dest-exchange": "dest_exchange"}'

# List shovels
sudo rabbitmqctl list_shovels

# Delete shovel
sudo rabbitmqctl clear_parameter shovel my_shovel
```

**Using RabbitMQ Management Plugin:**

```bash
# Enable shovel plugin
sudo rabbitmq-plugins enable rabbitmq_shovel

# Start RabbitMQ with shovel enabled
rabbitmq-server -plugins rabbitmq_shovel
```

### Creating Federation

**Using rabbitmqadmin:**

```bash
# Create federation link (cross-cluster forwarding)
sudo rabbitmqctl set_parameter federation-upstream \
  my_federation \
  '{"uri": "amqp://upstream-node", "expires": 3600000}'

# List federation links
sudo rabbitmqctl list_federation_links

# Delete federation link
sudo rabbitmqctl clear_parameter federation-upstream my_federation
```

**Using RabbitMQ Management Plugin:**

```bash
# Enable federation plugin
sudo rabbitmq-plugins enable rabbitmq_federation

# Start RabbitMQ with federation enabled
rabbitmq-server -plugins rabbitmq_federation
```

### Creating Consistent Hashing

**Using rabbitmqadmin:**

```bash
# Define consistent hash exchange
sudo rabbitmqctl set_parameter \
  exchange-name \
  {"type": "x-consistent-hash", "hash-header": "order_id"}

# List exchanges
sudo rabbitmqctl list_exchanges
```

**Using RabbitMQ Management Plugin:**

```bash
# Enable consistent hash exchange plugin
sudo rabbitmq-plugins enable rabbitmq_consistent_hash_exchange

# Start RabbitMQ with consistent hash exchange enabled
rabbitmq-server -plugins rabbitmq_consistent_hash_exchange
```

### Version Notes

- **RabbitMQ 3.12+:** All architectural pattern features fully supported
- **Shovel Plugin:** Cross-node message forwarding
- **Federation Plugin:** Cross-cluster message forwarding
- **Super Streams Plugin:** Large fanout performance
- **Consistent Hashing:** Same message to same queue
- **Cluster Plugin:** High availability (multiple nodes)
- **Alternate Exchange:** Exchange failover

---

## 6️⃣ Where Architectural Patterns Should Be Applied (With Example)

### Shovel Example

**Scenario:** Region-to-region message forwarding

**Shovel Configuration (shovel_config.json):**

```json
{
  "shovels": [
    {
      "name": "region_to_region_shovel",
      "src-uri": "amqp://region-a-node",
      "src-queue": "orders_region_a",
      "dest-uri": "amqp://region-b-node",
      "dest-exchange": "orders_region_b"
    }
  ]
}
```

**Applying Shovel:**

```bash
# Apply shovel configuration
sudo rabbitmqctl import_config shovel shovel_config.json

# Verify shovel
sudo rabbitmqctl list_shovels
```

**Expected Result:**
- Shovel forwards messages from `orders_region_a` (Region A) to `orders_region_b` (Region B)
- Automatic cross-node forwarding
- Loose coupling (shovel handles forwarding)
- Resilience (shovel handles node failure)

### Federation Example

**Scenario:** Global message routing (multi-cluster)

**Federation Upstream Configuration (federation_config.json):**

```json
{
  "federation-upstreams": [
    {
      "name": "us_cluster_federation",
      "uri": "amqp://us-cluster-node",
      "expires": 3600000
    },
    {
      "name": "eu_cluster_federation",
      "uri": "amqp://eu-cluster-node",
      "expires": 3600000
    }
  ]
}
```

**Applying Federation:**

```bash
# Apply federation configuration
sudo rabbitmqctl import_config federation federation_config.json

# Verify federation links
sudo rabbitmqctl list_federation_links
```

**Expected Result:**
- Federation forwards messages from US cluster to EU cluster
- Automatic cross-cluster forwarding
- Global message routing
- Loose coupling (federation handles forwarding)

### Super Streams Example

**Scenario:** Broadcast to millions of consumers

**Super Streams Definition (policy_super_streams.json):**

```json
{
  "vhosts": {
    "/": {
      "super-streams": [
        {
          "name": "broadcast_super_stream",
          "queues": ["broadcast_1", "broadcast_2", "...", "broadcast_1000000"],
          "routing-keys": ["broadcast"]
        }
      ]
    }
  }
}
```

**Applying Super Streams Policy:**

```bash
# Apply super streams policy
sudo rabbitmqctl set_policy super_streams "^broadcast_.*$" \
  '{"max-length": "10", "max-age": "86400"}' \
  --vhost "/"

# Verify super streams
sudo rabbitmqctl list_policies | grep super_streams
```

**Expected Result:**
- Super streams partitions fanout exchange (10 queues per node)
- CPU distributed across super stream nodes (parallel processing)
- Memory distributed across super stream nodes (1M copies partitioned)
- Improved throughput (milliseconds instead of minutes)
- Lower latency (better user experience)

### Consistent Hashing Example

**Scenario:** Same message always goes to same queue

**Consistent Hashing Exchange Definition (policy_consistent_hash.json):**

```json
{
  "vhosts": {
    "/": {
      "exchanges": {
        "orders_consistent_hash": {
          "type": "x-consistent-hash",
          "arguments": {
            "hash-header": "order_id"
          }
        }
      }
    }
  }
}
```

**Applying Consistent Hashing Policy:**

```bash
# Apply consistent hash exchange policy
sudo rabbitmqctl set_policy consistent_hash \
  '{"pattern": "^orders_", "definition": {"type": "x-consistent-hash", "arguments": {"hash-header": "order_id"}}}' \
  --apply-to exchanges

# Verify consistent hash exchange
sudo rabbitmqctl list_exchanges | grep orders_consistent_hash
```

**Expected Result:**
- Messages with same `order_id` always go to same queue
- Consistent routing (same user → same queue)
- Message ordering maintained (same user → same queue)
- Load balancing (multiple queues for different users)

### Best Practices

**Shovel Configuration:**
✅ Use shovel for cross-node message forwarding  
✅ Configure shovel with source and destination  
✅ Monitor shovel performance (throughput, errors)  
✅ Handle shovel errors gracefully (retries)  
✅ Use secure connections (SSL/TLS)  

**Federation Configuration:**
✅ Use federation for cross-cluster communication  
✅ Configure federation with upstream and downstream  
✅ Monitor federation performance (throughput, errors)  
✅ Handle federation errors gracefully (retries)  
✅ Use secure connections (SSL/TLS)  
✅ Set federation expiration (stale links cleanup)  

**Super Streams Configuration:**
✅ Use super streams for large fanout (millions of consumers)  
✅ Configure super streams with partitions (load balancing)  
✅ Monitor super stream performance (throughput, latency)  
✅ Use appropriate super stream nodes (CPU, memory)  
✅ Use TTL for super stream queues (cleanup)  

**Consistent Hashing Configuration:**
✅ Use consistent hashing for same message to same queue  
✅ Use hash header for consistent routing  
✅ Configure consistent hash exchange with proper arguments  
✅ Monitor consistent hash performance (load balancing)  
✅ Use multiple queues for different users (load balancing)  

### Common Mistakes

❌ Not using shovel → Manual cross-node forwarding required  
❌ Not using federation → Manual cluster-to-cluster forwarding required  
❌ Not using super streams → CPU/memory bottleneck for large fanout  
❌ Not using consistent hashing → Messages to different queues (inconsistent)  
❌ Not monitoring architectural patterns → Performance issues not visible  
❌ Not handling errors gracefully → Message forwarding failures  
❌ Using insecure connections → Security vulnerabilities  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Large Fanout Performance (The "CPU/Memory Bottleneck" Problem)**

You're building a global notification system:

- Producer broadcasts to 1,000,000 consumers worldwide
- Fanout exchange copies message to all 1M queues
- CPU bottleneck on exchange (millions of copies)
- Memory bottleneck on exchange (1M copies in memory)
- Message delivery delay (minutes to hours)

Current implementation:
- Producer broadcasts to fanout exchange
- Fanout exchange copies to all 1M queues
- No partitioning (single node handles all 1M copies)
- CPU/Memory bottleneck (millions of copies in memory)

**Problems:**
- CPU bottleneck (millions of copies)
- Memory bottleneck (1M copies in memory)
- Message delivery delay (hours for 1M messages)
- System appears unresponsive
- **Impact:** System unresponsive, poor user experience, high latency, poor throughput

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ (3 nodes)**

```bash
# Node 1
docker run -d --name rabbitmq-node1 \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Node 2
docker run -d --name rabbitmq-node2 \
  -p 5673:5673 -p 15673:15673 \
  rabbitmq:3-management

# Node 3
docker run -d --name rabbitmq-node3 \
  -p 5674:5674 -p 15674:15674 \
  rabbitmq:3-management
```

**Step 2: Create producer with fanout exchange (no super streams)**

Create `large_fanout_producer.py`:

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: Fanout exchange (no super streams)
channel.exchange_declare(
    exchange='broadcast_exchange',
    exchange_type='fanout'
)

# PROBLEM: Publish 1M messages (fanout bottleneck)
for i in range(1000000):
    message = {
        "notification_id": f"notification_{i+1:07d}",
        "message": "Global update",
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='broadcast_exchange',
        routing_key='',
        body=json.dumps(message)
    )
    
    if i % 100000 == 0:
        print(f"[x] Published {i} messages")

print("[x] Published 1,000,000 messages (PROBLEM: Large fanout - CPU/Memory bottleneck)")
connection.close()
```

**Step 3: Create 1,000,000 consumers**

Create `consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    notification = json.loads(body)
    print(f"[✓] Received {notification['notification_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: Fanout exchange (no super streams)
channel.exchange_declare(exchange='broadcast_exchange', exchange_type='fanout')

# PROBLEM: Create queue (auto-delete)
queue_name = channel.queue_declare(queue='', exclusive=True, auto_delete=True)
queue_name = queue_name.method.queue

# PROBLEM: Bind to fanout exchange
channel.queue_bind(exchange='broadcast_exchange', queue=queue_name)

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
print(f"[*] Consumer waiting (PROBLEM: Large fanout - 1M queues)")
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Create 1,000,000 consumer containers
for i in {1..1000}; do
  docker run -d --name consumer$i \
    rabbitmq:3-management \
    python3 consumer.py

# Terminal: Producer
python3 large_fanout_producer.py
```

**Expected observation:**
- Producer publishes 1M messages
- Fanout exchange copies to all 1M queues
- CPU bottleneck on exchange (millions of copies)
- Memory bottleneck on exchange (1M copies in memory)
- Message delivery delay (hours)
- System appears unresponsive
- **Impact:** System unresponsive, poor user experience, high latency

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Exchanges tab → See "broadcast_exchange" (fanout)
- Go to Queues tab → See 1M queues
- See CPU/Memory bottleneck (exchange overwhelmed)

### ✅ Solution & Explanation

**Solution: Implement Super Streams (Large Fanout Performance)**

**Create super streams policy (super_streams_policy.json):**

```json
{
  "policies": {
    "super-streams": {
      "pattern": "^broadcast_.*$",
      "vhost": "/",
      "apply-to": "exchanges",
      "definition": {
        "super-stream": true,
        "max-length": 10000,
        "max-age": 86400
      },
      "priority": 1
    }
  }
}
```

**Applying Super Streams Policy:**

```bash
# Apply super streams policy
sudo rabbitmqctl apply_policy super_streams_policy.json

# Enable super streams plugin
sudo rabbitmq-plugins enable rabbitmq_super_stream
sudo rabbitmqctl restart
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Admin tab → Policies
3. See "super-streams" policy applied
4. Go to Exchanges tab → See "broadcast_exchange" (super stream enabled)
5. See improved throughput (CPU distributed, memory partitioned)

**Comparison:**

| Design | CPU Usage | Memory Usage | Delivery Time |
|--------|-----------|-------------|---------------|
| No Super Streams (old) | 100% | 100% | Hours |
| Super Streams (new) | 33% (3 nodes) | 33% (3 nodes) | Minutes |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Use shovel for cross-node message forwarding  
- Use federation for cross-cluster communication  
- Use super streams for large fanout (millions of consumers)  
- Use consistent hashing for same message to same queue  
- Monitor architectural pattern performance (throughput, errors)  
- Handle errors gracefully (retries)  
- Use secure connections (SSL/TLS)  

**❌ Don't:**
- Not using shovel → Manual cross-node forwarding  
- Not using federation → Manual cluster-to-cluster forwarding  
- Not using super streams → CPU/memory bottleneck for large fanout  
- Not using consistent hashing → Messages to different queues (inconsistent)  
- Not monitoring architectural patterns → Performance issues not visible  
- Not handling errors gracefully → Message forwarding failures  
- Using insecure connections → Security vulnerabilities  

### Architectural Pattern Guidelines

```
Shovel:
├─ Use for cross-node message forwarding
├─ Configure with source and destination
├─ Monitor shovel performance
└─ Handle errors gracefully

Federation:
├─ Use for cross-cluster communication
├─ Configure with upstream and downstream
├─ Monitor federation performance
├─ Set expiration for stale links
└─ Handle errors gracefully

Super Streams:
├─ Use for large fanout (millions of consumers)
├─ Configure with partitions (load balancing)
├─ Monitor super stream performance
├─ Use appropriate super stream nodes
└─ Use TTL for super stream queues

Consistent Hashing:
├─ Use for same message to same queue
├─ Use hash header for consistent routing
├─ Configure consistent hash exchange
├─ Monitor load balancing performance
└─ Use multiple queues for different users
```

### Production Considerations

**Monitoring Architectural Patterns:**

```python
# Monitor shovel performance
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Get shovel stats (via rabbitmqadmin)
print("[MONITOR] Shovel: cross-node message forwarding")

# Monitor federation performance
print("[MONITOR] Federation: cross-cluster communication")

# Monitor super stream performance
print("[MONITOR] Super Streams: large fanout performance")

# Monitor consistent hash performance
print("[MONITOR] Consistent Hashing: same message to same queue")

connection.close()
```

**Scaling Architectural Patterns:**

```bash
# Add RabbitMQ node (cluster scaling)
docker run -d --name rabbitmq-node4 \
  -p 5675:5675 -p 15675:15675 \
  rabbitmq:3-management

# Remove RabbitMQ node
docker stop rabbitmq-node4
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's shovel?**

A: Shovel is a RabbitMQ plugin for cross-node message forwarding. It connects to source and destination RabbitMQ nodes, reads messages from source queue, and publishes to destination exchange. Automatic cross-node forwarding.

**Q2: What's federation?**

A: Federation is a RabbitMQ plugin for cross-cluster communication. It connects to upstream and downstream RabbitMQ clusters, and links exchanges between clusters. Messages published to upstream cluster are automatically forwarded to downstream cluster.

**Q3: What's super streams?**

A: Super Streams is a RabbitMQ plugin for large fanout performance. It partitions fanout exchange across multiple super stream nodes, distributing CPU and memory load. Each super stream node handles subset of queues, improving throughput and reducing latency.

**Q4: What's consistent hashing?**

A: Consistent hashing is a RabbitMQ exchange type that ensures same message always goes to same queue. It uses hash header to calculate target queue (hash function). Messages with same hash header always go to same queue (consistent routing).

**Q5: When should you use architectural patterns?**

A: Use shovel for cross-node message forwarding. Use federation for cross-cluster communication. Use super streams for large fanout (millions of consumers). Use consistent hashing for same message to same queue. Use cluster for high availability. Use architectural patterns for complex enterprise scenarios.

### Production Pitfalls

**Pitfall 1: Not using shovel**
- Problem: Manual cross-node forwarding required
- Detection: Manual intervention, complex configuration
- Solution: Always use shovel for cross-node forwarding

**Pitfall 2: Not using federation**
- Problem: No automatic cross-cluster forwarding
- Detection: Manual cluster-to-cluster forwarding required
- Solution: Always use federation for cross-cluster communication

**Pitfall 3: Not using super streams**
- Problem: CPU/memory bottleneck for large fanout
- Detection: System unresponsive, high latency
- Solution: Always use super streams for large fanout

**Pitfall 4: Not using consistent hashing**
- Problem: Messages to different queues (inconsistent)
- Detection: Data inconsistency, wrong queue processing
- Solution: Always use consistent hashing for same message to same queue

**Pitfall 5: Not monitoring architectural patterns**
- Problem: Performance issues not visible
- Detection: Poor throughput, high latency, system unresponsive
- Solution: Always monitor architectural patterns (throughput, errors)

### Advanced Architectural Concepts

**Multiple Shovels (Different Node Pairs):**

```json
{
  "shovels": [
    {
      "name": "region_to_region_shovel",
      "src-uri": "amqp://region-a-node",
      "src-queue": "orders_region_a",
      "dest-uri": "amqp://region-b-node",
      "dest-exchange": "orders_region_b"
    },
    {
      "name": "cluster_to_cluster_shovel",
      "src-uri": "amqp://cluster-1-node",
      "src-queue": "global_orders_cluster_1",
      "dest-uri": "amqp://cluster-2-node",
      "dest-exchange": "global_orders_cluster_2"
    }
  ]
}
```

**Multi-Region Federation (Global Routing):**

```json
{
  "federation-upstreams": [
    {
      "name": "us_cluster_federation",
      "uri": "amqp://us-cluster-node"
    },
    {
      "name": "eu_cluster_federation",
      "uri": "amqp://eu-cluster-node"
    },
    {
      "name": "apac_cluster_federation",
      "uri": "amqp://apac-cluster-node"
    }
  ]
}
```

**Super Streams with Partitions:**

```json
{
  "policies": {
    "super-streams": {
      "pattern": "^broadcast_.*$",
      "vhost": "/",
      "apply-to": "exchanges",
      "definition": {
        "super-stream": true,
        "max-length": 100000
      }
    }
  }
}
```

---

## 📚 Summary

Architectural patterns in RabbitMQ provide advanced messaging solutions for cross-node, cross-cluster, large fanout, and high availability. Shovel, federation, super streams, and consistent hashing enable enterprise-grade messaging architectures.

**Key takeaways:**
- Use shovel for cross-node message forwarding
- Use federation for cross-cluster communication
- Use super streams for large fanout (millions of consumers)
- Use consistent hashing for same message to same queue
- Use cluster for high availability (multiple nodes)
- Use exchange-to-exchange bindings for exchange forwarding
- Use alternate exchange for exchange failover
- Monitor architectural patterns (throughput, errors)
- Handle errors gracefully (retries, failover)
- Use secure connections (SSL/TLS)

**Next steps:**
- Practice with architectural patterns in your applications
- Complete Capstone Project
- Explore clustering and high availability
- Learn about message ordering and consistency patterns
- Continue to Module 04 (Advanced Concepts)

---

**Module 03 - Message Patterns and Architectures**  
**Lesson 07 - Complete**
**Module 03 - Complete** ✅