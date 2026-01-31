# 02-06: Message Durability and Persistence

## 1️⃣ What Are Message Durability and Persistence

**Message Durability** ensures messages survive RabbitMQ server restarts. **Persistence** is the mechanism that writes messages to disk for long-term storage. Together, they guarantee message safety even if RabbitMQ crashes or restarts.

Think of durability and persistence like file saving:

- **Message** = A document in memory
- **Durability** = Flag that says "save this to disk"
- **Persistence** = The process of writing to disk
- **Restart Survival** = Message survives RabbitMQ restart
- **Disk Write** = Message stored on physical disk

**Where durability and persistence fit in RabbitMQ architecture:**

```
┌─────────────┐
│  Producer   │
└──────┬──────┘
       │
       │ Publishes message WITH DURABLE FLAG
       ▼
┌─────────────────────────────────────────────┐
│           Exchange (In-Memory)         │
│  (Routes messages to queues)            │
└─────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│           Queue (Durable?)             │
│  (Buffers messages with durability)        │
│                                      │
│  ┌────────────────────────────────────┐ │
│  │ Message 1 (Durable: ✓)       │ │
│  │ Message 2 (Durable: ✗)        │ │
│  │ Message 3 (Durable: ✓)        │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│        RabbitMQ Memory                │
│     (Messages in RAM for fast access)  │
└─────────────────────────────────────────────┘
       │
       └───────────┬─────────────────────┐
                     │                     │
                     ▼                     ▼
       ┌─────────────────────┐   ┌─────────────────────┐
       │ Durable Messages   │   │  Queue Metadata    │
       │ (Written to disk)    │   │  (Queue config)    │
       └─────────────────────┘   └─────────────────────┘
                     │                     │
                     ▼                     ▼
       ┌─────────────────────────────────────┐
       │          Disk Storage             │
       │   (Messages survive restart)      │
       └─────────────────────────────────────┘
```

**Key concepts:**
- **Durable Queue:** Queue definition survives RabbitMQ restart
- **Durable Message:** Message is written to disk (survives restart)
- **Transient Message:** Message is kept only in memory (lost on restart)
- **Persistence Mechanism:** Writes messages to disk
- **Durability Flag:** Per-message setting (must be true for persistence)

---

## 2️⃣ Problems Solved by Message Durability and Persistence

### The "Data Loss on Restart" Problem

Without durability:

- Messages exist only in memory (RAM)
- RabbitMQ server restart or crash
- All messages in memory are lost
- No way to recover lost messages
- Critical data disappears

**Real-world failure scenario:**

A payment processing system had:

```
Producer → Queue → Payment Consumer
                    │
                    ├─ Payment 1: $100 (in memory)
                    ├─ Payment 2: $200 (in memory)
                    └─ Payment 3: $300 (in memory)

RabbitMQ Server:
├─ Messages in memory: 3 payments
└─ No messages written to disk (transient)

SERVER RESTART (crash or maintenance)
├─ Memory cleared
└─ All 3 payments lost forever!
```

**Problems:**
- 3 payments lost on server restart
- $600 in lost transactions
- Customer payments disappeared from system
- No way to recover or retry lost payments
- Financial discrepancies and customer complaints
- **Impact:** $600K in lost revenue per year, 30,000 disputed payments, customer trust damaged

After implementing durability:
- All messages written to disk
- Server restart - all messages restored
- No data loss
- Consumers resume processing after restart
- **Result:** Zero message loss, $0 data loss, complete reliability

### The "Queue Definition Loss" Problem

Without durable queues:

- Queue definition exists only in memory
- RabbitMQ server restart
- Queue definition lost
- No way to recover queue configuration
- Consumers can't connect to queue

**Example:**

```
RabbitMQ Server:
├─ Queue: payments (transient, in memory)
├─ Exchange: payment-exchange (transient)
└─ Messages: 1000 payments

SERVER RESTART
├─ Memory cleared
└─ Queue definition lost!

Recovery:
├─ Queue: payments (gone!)
├─ Exchange: payment-exchange (gone!)
└─ Messages: 1000 payments (still on disk, but no queue)

Consumer:
├─ Connects to RabbitMQ
├─ Queue "payments" doesn't exist
└─ ERROR: Queue not found
```

**Problems:**
- Queue definition lost on restart
- Exchange binding lost
- Consumers can't connect to queue
- Messages on disk but inaccessible
- Need to recreate queues manually
- **Impact:** Service downtime, manual intervention, data inaccessibility

After implementing durable queues:
- Queue definition survives restart
- Exchange bindings preserved
- Queue automatically restored
- Messages accessible after restart
- **Result:** Zero downtime, automatic recovery, no manual intervention

---

## 3️⃣ When You Should Use Message Durability and Persistence

### Development vs Production

**Development:**
- Can use transient queues for quick testing
- No need for durability in throwaway code
- Simpler code for experimentation
- Don't use in production code

**Production:**
- Absolutely required for all critical queues
- Essential for all critical messages (orders, payments)
- Critical for data safety and compliance
- Required for high-availability deployments
- Necessary for legal or regulatory requirements

### Durability Strategy

| Message Type | Durability | Example |
|--------------|-------------|----------|
| **Critical data** | Always Durable | Orders, payments, financial |
| **User data** | Always Durable | Profiles, preferences |
| **Audit logs** | Always Durable | Security events, compliance |
| **Telemetry** | Optional (Transient) | Metrics, heartbeat |
| **Status updates** | Transient (if stale) | Real-time status |
| **Notifications** | Transient (if timely) | Alerts, notifications |

### Required vs Optional

**Required when:**
- Processing critical data (orders, payments, financial transactions)
- Regulatory or compliance requirements (audit trails, financial records)
- High-availability deployments (clustering, replication)
- Legal requirements (data preservation)
- At-least-once delivery required
- Data loss unacceptable

**Optional when:**
- Transient data (telemetry, metrics, status)
- Time-sensitive data that loses value quickly (notifications, alerts)
- Development and testing environments
- Fire-and-forget messages (logs, debugging)
- Data can be regenerated from source
- Performance-critical but low-value data

### Trade-offs

**Durability and Persistence:**
✅ Messages survive RabbitMQ restart  
✅ Data loss prevention  
✅ Compliance requirements met  
✅ Audit trail guaranteed  
✅ Automatic recovery after restart  
❌ Slower performance (disk I/O)  
❌ Higher disk usage  
❌ More complex configuration  
❌ Slightly higher latency  

**Non-Durable (Transient):**
✅ Faster performance (in-memory only)  
✅ Lower disk usage  
✅ Simpler configuration  
✅ Lower latency  
❌ Data loss on restart  
❌ No compliance guarantee  
❌ Manual intervention after restart  
❌ Data lost forever (not recoverable)  

---

## 4️⃣ How Message Durability and Persistence Work

### Durability Configuration Process

**Setting up durability:**

```
1. Producer Sets Durable Flag
   │
   ├─ Message marked as "durable"
   ├─ Queue declared as "durable"
   └─ Exchange declared as "durable"
   │
2. RabbitMQ Receives Message
   │
   ├─ Message stored in memory (for fast access)
   ├─ Durable flag checked
   └─ Persistence scheduled (if durable)
   │
3. RabbitMQ Persists Message (if durable)
   │
   ├─ Message written to disk
   ├─ File system flush (sync)
   └─ Confirmation sent to producer
   │
4. Server Restart (if durable)
   │
   ├─ RabbitMQ restarts (crash or maintenance)
   ├─ Memory cleared
   └─ Durable queues/messages restored from disk
   │
5. Consumer Reconnects
   │
   ├─ Durable queue exists (restored from disk)
   ├─ Messages exist in queue (restored from disk)
   └─ Consumer resumes processing
```

### Durability Types

**Durable Queue:**

```python
# Declare durable queue (survives restart)
channel.queue_declare(
    queue='orders',
    durable=True  # CRITICAL: Queue persists
)
```

**Durable Message:**

```python
# Publish durable message
channel.basic_publish(
    exchange='',
    routing_key='orders',
    body=order_data,
    properties=pika.BasicProperties(
        delivery_mode=2  # CRITICAL: Message persists
    )
)
```

### Persistence Flow

**When messages persist:**

```
Producer → RabbitMQ (Persistence Flow)
                    │
                    ├─ 1. Publish message (durable=True)
                    │  2. Message stored in memory (fast access)
                    │  3. Message written to disk (persisted)
                    │  4. File system sync (durability guaranteed)
                    │  5. Confirm sent to producer
                    │
                    └─ Message survives server restart
```

**Restart Recovery Flow:**

```
Server Restart:
├─ 1. RabbitMQ stops (crash or maintenance)
├─ 2. Memory cleared (all messages lost from RAM)
├─ 3. RabbitMQ starts
├─ 4. Loads durable queues from disk
├─ 5. Loads durable messages from disk
├─ 6. Queues and messages restored
└─ 7. Consumers reconnect and resume processing
```

### Durability Levels

**In-Memory (Transient):**

```
Queue: messages (durable=False)
Messages: All (delivery_mode=1, transient)
Persistence: None (in-memory only)
Restart: All data lost
```

**Durable (Disk Persistence):**

```
Queue: messages (durable=True)
Messages: All (delivery_mode=2, durable)
Persistence: Disk (all messages written to disk)
Restart: All data restored
```

---

## 5️⃣ Installation / Setup

**Message Durability and Persistence are built-in RabbitMQ features.** No installation required - just set durable flags on queues and messages.

### Prerequisites

- RabbitMQ server running
- AMQP client library that supports durability
- Understanding of persistence vs performance

### Declaring Durable Queue

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Declare durable queue
channel.queue_declare(
    queue='orders',
    durable=True  # CRITICAL: Queue persists
)

print("[✓] Durable queue declared")
connection.close()
```

**Using rabbitmqctl:**

```bash
# Declare durable queue
sudo rabbitmqctl add_queue orders durable=true

# Delete queue (cleanup)
sudo rabbitmqctl delete_queue name=orders
```

### Publishing Durable Message

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='orders')

# CRITICAL: Publish durable message
channel.basic_publish(
    exchange='',
    routing_key='orders',
    body=order_data,
    properties=pika.BasicProperties(
        delivery_mode=2  # CRITICAL: Message persists (2=durable)
    )
)

print("[✓] Published durable message")
connection.close()
```

**Node.js (amqplib):**

```javascript
const amqp = require('amqplib/callback_api');

const connection = amqp.connect('amqp://localhost');
const channel = connection.createChannel();

channel.assertQueue('orders', { durable: true });

// CRITICAL: Publish durable message (persistent=true)
channel.sendToQueue('orders', Buffer.from(order_data), {
    persistent: true  // CRITICAL: Message persists
});

console.log('[✓] Published durable message');
```

**Java (RabbitMQ Java Client):**

```java
import com.rabbitmq.client.*;

ConnectionFactory factory = new ConnectionFactory();
factory.setHost("localhost");
Connection connection = factory.newConnection();
Channel channel = connection.createChannel();

// CRITICAL: Declare durable queue
channel.queueDeclare("orders", true, false, null, null);

// CRITICAL: Publish durable message
AMQP.BasicProperties.Builder props = new AMQP.BasicProperties.Builder()
    .deliveryMode(2);  // CRITICAL: Message persists (2=durable)

channel.basicPublish("", "orders", props.build(), order_data);

System.out.println("[✓] Published durable message");
```

### Version Notes

- **RabbitMQ 3.12+:** All durability features fully supported
- **AMQP 0-9-1+:** Durability protocol standard
- **Delivery Mode 1:** Transient (non-persistent)
- **Delivery Mode 2:** Persistent (durable)
- **Durable Queue Required:** Messages only persist if queue is durable

---

## 6️⃣ Where Message Durability and Persistence Should Be Applied (With Example)

### Durable Queue and Message

**Scenario:** Order processing system that must survive RabbitMQ restarts

**Producer (durable_producer.py):**

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Declare durable queue (survives restart)
channel.queue_declare(
    queue='orders',
    durable=True  # CRITICAL: Queue persists
)

# CRITICAL: Send durable messages
orders = []
for i in range(10):
    order = {
        "order_id": f"order_{i+1:04d}",
        "customer_id": 12345 + i,
        "amount": (i+1) * 99.99,
        "timestamp": time.time()
    }
    
    # CRITICAL: Durable message (delivery_mode=2)
    channel.basic_publish(
        exchange='',
        routing_key='orders',
        body=json.dumps(order),
        properties=pika.BasicProperties(
            delivery_mode=2  # CRITICAL: Message persists
        )
    )
    orders.append(order)
    print(f"[x] Sent durable order: {order['order_id']}")

print(f"[✓] Sent {len(orders)} durable orders (queue survives restart)")
connection.close()
```

**Consumer (durable_consumer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    """Process durable order"""
    order = json.loads(body)
    
    # Process order
    print(f"[✓] Processing order: {order['order_id']} ${order['amount']:.2f}")
    
    # CRITICAL: Acknowledge after processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Consume from durable queue
channel.queue_declare(queue='orders', durable=True)
channel.basic_consume(queue='orders', on_message_callback=callback)

print('[*] Consumer waiting (durable queue)')
channel.start_consuming()
```

**How to test durability:**

```bash
# Terminal 1: Consumer
python3 durable_consumer.py

# Terminal 2: Producer
python3 durable_producer.py
```

**Expected output:**

```
# Producer
[x] Sent durable order: order_0001
[x] Sent durable order: order_0002
...
[x] Sent durable order: order_0010
[✓] Sent 10 durable orders (queue survives restart)

# Consumer
[*] Consumer waiting (durable queue)
[x] Received order: order_0001
[✓] Processing order: order_0001 $99.99
[x] Received order: order_0002
[✓] Processing order: order_0002 $199.98
...
```

**Test Restart Survival:**

```bash
# Send some orders
python3 durable_producer.py

# Restart RabbitMQ
docker restart rabbitmq

# Check if queue and messages survived
# Terminal: RabbitMQ Management UI
# - Go to http://localhost:15672
# - Queue "orders" exists (durable)
# - Messages still in queue (persisted)

# Start consumer again
python3 durable_consumer.py
# Consumer processes messages from before restart
```

### Best Practices

**Durability Configuration:**
✅ Use durable=True for critical queues  
✅ Use delivery_mode=2 for critical messages  
✅ Use durable queues for persistence  
✅ Use durable messages for data safety  
✅ Avoid mixing durable/transient in same queue  
✅ Document durability strategy  
✅ Monitor disk usage (persistence consumes disk)  

**Persistence Strategy:**
✅ Use durability for all production queues  
✅ Use durable messages for critical data  
✅ Use transient for telemetry (performance)  
✅ Use transient for notifications (if timely)  
✅ Use durability for audit and compliance  
✅ Use durable for legal and financial data  

**Performance Considerations:**
✅ Disk I/O is slower than memory access  
✅ Persistence adds latency to publish  
✅ Monitor disk usage and I/O performance  
✅ Use SSD for better persistence performance  
✅ Tune fsync settings for balance of safety/performance  
✅ Use separate disks for data and logs  

### Common Mistakes

❌ Forgetting durable flag on queue → Queue lost on restart  
❌ Forgetting delivery_mode=2 on message → Message lost on restart  
❌ Mixing durable/transient messages → Data inconsistency  
❌ Using durable queue but transient messages → Confusion  
❌ Not monitoring disk usage → Disk fills up  
❌ Not testing restart survival → Issues discovered too late  
❌ Assuming persistence = no performance impact → Latency issues  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Catastrophic Data Loss (The Server Restart)**

You're building an order submission system:

- Producer sends order messages
- Order processing system consumes and processes orders
- RabbitMQ server may be restarted (crash or maintenance)
- All orders must survive restart

Current implementation:
- Producer publishes without durability
- Queue is transient (in-memory only)
- No persistence mechanism
- Server restart = All orders lost

**Problems:**
- 10 orders lost on server restart (in-memory only)
- Customer payments disappeared from system
- Queue definition lost (recreate needed)
- No way to recover lost orders
- **Impact:** $1K in lost revenue per month, 100 disputed orders, customer trust damage, manual intervention required

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

**Step 2: Create transient producer**

Create `transient_producer.py`:

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: Transient queue (in-memory only)
channel.queue_declare(
    queue='orders',
    durable=False  # PROBLEM: Queue lost on restart
)

# PROBLEM: Transient messages (in-memory only)
orders = []
for i in range(10):
    order = {
        "order_id": f"order_{i+1:04d}",
        "customer_id": 12345 + i,
        "amount": (i+1) * 99.99,
        "timestamp": time.time()
    }
    
    # PROBLEM: No delivery_mode (transient)
    channel.basic_publish(
        exchange='',
        routing_key='orders',
        body=json.dumps(order)
    )
    orders.append(order)
    print(f"[x] Sent order: {order['order_id']}")

print(f"[✓] Sent {len(orders)} orders (PROBLEM: Transient - lost on restart)")
connection.close()
```

**Step 3: Create transient consumer**

Create `transient_consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    """Process order"""
    order = json.loads(body)
    print(f"[✓] Processing order: {order['order_id']} ${order['amount']:.2f}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: Transient queue
channel.queue_declare(queue='orders', durable=False)
channel.basic_consume(queue='orders', on_message_callback=callback)

print('[*] Consumer waiting (transient queue)')
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal 1: Consumer
python3 transient_consumer.py

# Terminal 2: Producer
python3 transient_producer.py

# Terminal 3: Restart RabbitMQ (simulate crash/maintenance)
docker restart rabbitmq
```

**Expected observation:**
- Producer sends 10 orders
- Consumer processes 3 orders
- RabbitMQ restarts (7 orders remaining)
- Queue definition lost (transient)
- 7 remaining orders lost (in-memory only)
- Consumer can't reconnect (queue doesn't exist)
- **Impact:** All 10 orders lost, $1K revenue loss, customer payments missing, system requires manual queue recreation

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Queues tab → See "orders" queue gone (transient, lost on restart)
- See 0 messages (all lost)
- No way to recover lost orders

### ✅ Solution & Explanation

**Solution: Implement Durability for Orders**

**Create durable producer (durable_producer.py):**

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Declare durable queue (survives restart)
channel.queue_declare(
    queue='orders',
    durable=True  # SOLUTION: Queue persists
)

# SOLUTION: Send durable messages
orders = []
for i in range(10):
    order = {
        "order_id": f"order_{i+1:04d}",
        "customer_id": 12345 + i,
        "amount": (i+1) * 99.99,
        "timestamp": time.time()
    }
    
    # SOLUTION: Durable message (delivery_mode=2)
    channel.basic_publish(
        exchange='',
        routing_key='orders',
        body=json.dumps(order),
        properties=pika.BasicProperties(
            delivery_mode=2  # SOLUTION: Message persists
        )
    )
    orders.append(order)
    print(f"[x] Sent durable order: {order['order_id']}")

print(f"[✓] Sent {len(orders)} durable orders (queue survives restart)")
connection.close()
```

**Create durable consumer (durable_consumer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    """SOLUTION: Process durable order"""
    order = json.loads(body)
    print(f"[✓] Processing order: {order['order_id']} ${order['amount']:.2f}")
    
    # SOLUTION: Acknowledge after processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Consume from durable queue
channel.queue_declare(queue='orders', durable=True)
channel.basic_consume(queue='orders', on_message_callback=callback)

print('[*] Consumer waiting (durable queue)')
channel.start_consuming()
```

**How to verify durability:**

```bash
# Clear RabbitMQ
docker stop rabbitmq && docker rm rabbitmq
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Terminal 1: Consumer
python3 durable_consumer.py

# Terminal 2: Producer
python3 durable_producer.py

# Terminal 3: Restart RabbitMQ (simulate crash/maintenance)
docker restart rabbitmq

# Terminal 4: Start consumer again
python3 durable_consumer.py
```

**Expected output:**

```
# Producer (before restart)
[x] Sent durable order: order_0001
[x] Sent durable order: order_0002
...
[x] Sent durable order: order_0010
[✓] Sent 10 durable orders (queue survives restart)

# Consumer (before restart)
[*] Consumer waiting (durable queue)
[x] Received order: order_0001
[✓] Processing order: order_0001 $99.99
[x] Received order: order_0002
[✓] Processing order: order_0002 $199.98
...
[x] Received order: order_0003
[✓] Processing order: order_0003 $299.97

# RabbitMQ restart...
# Wait for container to restart...

# Consumer (after restart)
[*] Consumer waiting (durable queue)
[x] Received order: order_0004
[✓] Processing order: order_0004 $399.96
[x] Received order: order_0005
[✓] Processing order: order_0005 $499.95
...
[x] Received order: order_0010
[✓] Processing order: order_0010 $999.90

# All 10 orders processed after restart
# No data loss!
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Queues tab → See "orders" queue with Features: D
3. See message count after restart (still 10 messages)
4. See message persistence (on disk)
5. Queue survived restart automatically

**Comparison:**

| Design | Data Loss | Queue Survival | Message Recovery |
|--------|-----------|-----------------|-----------------|
| Transient (old) | 100% | None | None |
| Durable (new) | 0% | Complete | Complete |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Always use durable=True for critical queues  
- Always use delivery_mode=2 for critical messages  
- Use durable queues for persistence  
- Use durable messages for data safety  
- Avoid mixing durable/transient in same queue  
- Document durability strategy  
- Monitor disk usage and I/O performance  
- Test restart survival in development  
- Use durable for audit and compliance  

**❌ Don't:**
- Use transient queues for critical data → Data loss on restart  
- Use transient messages for critical data → Data loss on restart  
- Mix durable/transient messages → Data inconsistency  
- Use durable queue but transient messages → Confusion  
- Not monitoring disk usage → Disk fills up  
- Not testing restart survival → Issues discovered too late  
- Assume persistence = no performance impact → Latency issues  

### Durability Guidelines

```
Critical Data:
├─ Orders: Durable queue + Durable messages
├─ Payments: Durable queue + Durable messages
├─ Financial: Durable queue + Durable messages
└─ Audit logs: Durable queue + Durable messages

User Data:
├─ Profiles: Durable queue + Durable messages
├─ Preferences: Durable queue + Durable messages
└─ History: Durable queue + Durable messages

Transient Data:
├─ Telemetry: Transient queue + Transient messages (performance)
├─ Metrics: Transient queue + Transient messages (performance)
└─ Heartbeat: Transient queue + Transient messages (performance)
```

### Production Considerations

**Monitoring Disk Usage:**

```python
# Monitor RabbitMQ disk usage
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Get queue info (includes message count)
method = channel.queue_declare(queue='orders', passive=True)
queue_size = method.method.message_count

# Estimate disk usage (approximate: 1KB per message)
disk_usage_kb = queue_size * 1

print(f"Queue size: {queue_size} messages")
print(f"Estimated disk usage: {disk_usage_kb} KB ({disk_usage_kb/1024:.2f} MB)")

# Alert if disk usage too high
if disk_usage_mb > 1024:  # 1GB
    print("[ALERT] High disk usage - consider archiving or message TTL")
```

**Performance Tuning:**

```bash
# RabbitMQ configuration for persistence balance
# /etc/rabbitmq/rabbitmq.conf

# Write messages to disk synchronously (safer, slower)
disk_free_limit.relative = 1.0
disk_free_limit.absolute = 2GB

# Sync interval (balance of safety vs performance)
disk_free_limit.msync_interval = 10000  # 10 seconds

# Use journal for durability
queue_index_embed_msgs_below = 51200  # Optimize for speed
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's the difference between durable queue and durable message?**

A: Durable queue means the queue definition survives RabbitMQ restart. Durable message means the message content is written to disk and survives RabbitMQ restart. Both are required for complete data safety (durable queue required for durable messages to be stored).

**Q2: What happens if you publish a durable message to a transient queue?**

A: Message is stored in memory only (transient) because the queue is transient. The durable flag on the message is ignored because the queue itself is not durable. Message will be lost on RabbitMQ restart.

**Q3: What's the performance impact of durability?**

A: Durability adds disk I/O overhead, which is slower than memory access. This increases publish latency and reduces overall throughput. However, for critical data, this performance cost is acceptable for data safety. Use durable for critical data, transient for high-volume, low-value data (telemetry).

**Q4: Can you mix durable and transient messages in the same queue?**

A: Technically yes, but not recommended. Durable queue will store both durable and transient messages to disk, which is confusing and wastes disk space for transient messages. Better to use separate queues (one durable for critical data, one transient for telemetry).

**Q5: How do you test that durability works?**

A: Publish messages, restart RabbitMQ, and verify that:
1. Queue definition still exists (not recreated)
2. Messages are still in queue (same count)
3. Consumers can reconnect and process remaining messages
4. No data loss occurred

### Production Pitfalls

**Pitfall 1: Not setting durable=True**
- Problem: Queue definition lost on restart
- Detection: Queue doesn't exist after restart
- Solution: Always use durable=True for critical queues

**Pitfall 2: Not using delivery_mode=2**
- Problem: Messages lost on restart
- Detection: Data loss after restart
- Solution: Always use delivery_mode=2 for critical messages

**Pitfall 3: Mixing durable/transient**
- Problem: Confusing data persistence (transient messages stored to disk)
- Detection: Wasted disk space, confusing behavior
- Solution: Use separate queues for different durability needs

**Pitfall 4: Not monitoring disk usage**
- Problem: Disk fills up with persisted messages
- Detection: RabbitMQ crashes when disk full
- Solution: Monitor disk usage, implement message TTL for cleanup

**Pitfall 5: Assuming durability = no performance impact**
- Problem: Unexpected latency and throughput degradation
- Detection: System performance issues
- Solution: Monitor publish latency, tune fsync settings

### Advanced Durability Concepts

**Queue Durability vs Message Durability:**

```python
# Queue durable, message transient (message lost on restart)
channel.queue_declare(queue='orders', durable=True)
channel.basic_publish(exchange='', routing_key='orders', body=data)

# Queue transient, message durable (ignored, message lost on restart)
channel.queue_declare(queue='orders', durable=False)
channel.basic_publish(exchange='', routing_key='orders', body=data, properties=pika.BasicProperties(delivery_mode=2))
```

**Durability with Confirm and Ack:**

```python
# Complete reliability flow
channel.confirm_delivery()

channel.queue_declare(queue='orders', durable=True)

channel.basic_publish(
    exchange='',
    routing_key='orders',
    body=data,
    properties=pika.BasicProperties(
        delivery_mode=2  # Durable message
    )
)

channel.wait_for_confirms(timeout=5)

# Consumer (manual_ack)
channel.basic_consume(queue='orders', on_message_callback=callback, auto_ack=False)
```

---

## 📚 Summary

Message Durability and Persistence ensure data survival across RabbitMQ restarts by writing messages to disk. Combined with durable queues and messages, they guarantee zero data loss for critical systems, even in server crash or maintenance scenarios.

**Key takeaways:**
- Durable queue ensures queue definition survives restart
- Durable message (delivery_mode=2) ensures message content survives restart
- Persistence writes messages to disk for long-term storage
- Use durability for all critical data (orders, payments, financial)
- Use transient for high-volume, low-value data (telemetry, metrics)
- Monitor disk usage and I/O performance
- Test restart survival in development
- Document durability strategy

**Next steps:**
- Practice with durability in your applications
- Learn about transactionality and atomic operations
- Explore clustering and high availability
- Learn about quorum queues (modern approach)
- Understand federation and shovel for distributed messaging

---

**Module 02 - Advanced RabbitMQ Features**  
**Lesson 06 - Complete**