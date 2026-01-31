# 04-05: Advanced Message Patterns

## 1️⃣ What Are Advanced Message Patterns

**Advanced Message Patterns** are sophisticated message routing and processing techniques that go beyond basic exchanges. These include Dead Letter Exchanges (DLX), Message TTL (Time-To-Live), Priority Queues, Lazy Queues, and more.

Think of advanced patterns like special handling for package delivery:

- **Dead Letter Exchange** = Return address for failed packages (undeliverable mail)
- **Message TTL** = Expiration date for packages (same-day delivery)
- **Priority Queue** = Express delivery (important packages first)
- **Lazy Queue** = Storage on demand (warehouse on demand)
- **Master/Slave** = Backup delivery (primary route, backup route)

**Where advanced patterns fit in RabbitMQ architecture:**

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│  Producer   │        │  Consumer    │        │  Admin       │        │  Analyzer    │
└──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
       │                    │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    RabbitMQ Server                                  │
│                    (Advanced Patterns)                              │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────────────────────┐   │
│   │              │              │              │               │   │   │
│   │    DLX        │     TTL        │     Priority     │   │   │
│   │ (Dead Letter)  │   (Expiry)    │   (Express)     │   │   │
│   │              │              │              │               │   │   │
│   │              │              │              │               │   │   │
│   └──────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────────────────────┐   │
│   │              │              │              │               │   │   │
│   │   Lazy        │     Master     │     Batch       │   │   │
│   │   (On Demand)  │     Slave      │   (Bulk)        │   │   │
│   │              │              │              │               │   │   │
│   └──────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────────┘
       │                    │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼                    ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│  Dead Letter  ││  Expired     ││  Priority     ││  Lazy        │
│  Queue       ││  Messages     ││  Queue       ││  Queue       │
│  (Failed)     ││  (Timed out)   ││  (Ordered)    ││  (Efficient)  │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘
```

**Key concepts:**
- **Dead Letter Exchange (DLX):** Routing for failed/undeliverable messages
- **Message TTL:** Message expiration time-to-live
- **Priority Queues:** High-priority messages processed first
- **Lazy Queues:** Messages loaded on demand (memory efficiency)
- **Master/Slave Pattern:** Primary/backup queue configuration

---

## 2️⃣ Problems Solved by Advanced Patterns

### The "Failed Messages" Problem

Without Dead Letter Exchange:

- Failed messages discarded
- No retry mechanism
- No visibility into failure reasons
- Data loss on message failure

**Real-world failure scenario:**

A production system had:

```
Producer → Exchange → Queue → Consumer (Processing Failed)
          │            │
          ├─ Producer publishes message (with routing key)
          ├─ Exchange routes message to queue (matching binding)
          ├─ Consumer processes message (fails)
          └─ Message lost (no retry, no visibility)

WITHOUT DEAD LETTER EXCHANGE:
├─ Failed messages discarded (no retry)
├─ No visibility into failure reasons (why failed)
├─ No retry mechanism (manual intervention required)
├─ No audit trail (no record of failed messages)
└─ **Impact:** Data loss, manual intervention, no reliability

PROBLEMS:
├─ Failed messages discarded (data loss)
├─ No visibility into failure reasons (why failed)
├─ No retry mechanism (manual intervention required)
├─ No audit trail (no record of failed messages)
└─ **Impact:** Data loss, poor reliability, manual intervention
```

**Problems:**
- Failed messages discarded (data loss)
- No visibility into failure reasons (why failed)
- No retry mechanism (manual intervention required)
- No audit trail (no record of failed messages)
- **Impact:** Data loss, poor reliability, manual intervention

After implementing Dead Letter Exchange:
- Failed messages routed to dead letter queue
- Failure reasons visible (audit trail)
- Retry mechanism possible (consume from dead letter queue)
- No data loss (all messages preserved)
- **Result:** High reliability, visibility into failures, automatic retry mechanism

### The "Expired Messages" Problem

Without Message TTL:

- Messages never expire
- Stale messages clog queues
- Consumers process stale data
- System inefficiency

**Example:**

```
Producer → Exchange → Queue (Stale Messages)
          │
          ├─ Producer publishes message (timestamp embedded)
          ├─ Message sits in queue (no expiration)
          ├─ Message becomes stale (outdated data)
          └─ Consumer processes stale message (inefficiency)

WITHOUT MESSAGE TTL:
├─ Messages never expire (no cleanup)
├─ Stale messages clog queues (memory waste)
├─ Consumers process stale data (inefficiency)
├─ No cleanup mechanism (manual intervention)
└─ **Impact:** System inefficiency, stale data processing, memory waste

PROBLEMS:
├─ Messages never expire (no cleanup)
├─ Stale messages clog queues (memory waste)
├─ Consumers process stale data (inefficiency)
├─ No cleanup mechanism (manual intervention)
└─ **Impact:** System inefficiency, stale data processing, memory waste
```

**Problems:**
- Messages never expire (no cleanup)
- Stale messages clog queues (memory waste)
- Consumers process stale data (inefficiency)
- No cleanup mechanism (manual intervention)
- **Impact:** System inefficiency, stale data processing, memory waste

After implementing Message TTL:
- Messages expire automatically (cleanup mechanism)
- Stale messages discarded (memory efficiency)
- Consumers process fresh data (efficiency)
- No manual intervention (automatic cleanup)
- **Result:** System efficiency, fresh data processing, automatic cleanup

---

## 3️⃣ When You Should Use Advanced Patterns

### Development vs Production

**Development:**
- Can use basic exchanges (direct, fanout, topic)
- Don't need advanced patterns (simple tests)
- Use basic message TTL (cleanup for tests)
- Don't use in production code

**Production:**
- Required for reliability (Dead Letter Exchange for failed messages)
- Required for efficiency (Message TTL for stale message cleanup)
- Required for priority (Priority Queues for important messages)
- Required for memory efficiency (Lazy Queues for large messages)
- Required for high availability (Master/Slave for queue failover)
- Required for production systems (99.9%+ uptime SLA)
- Required for compliance (audit trails, data retention)

### Advanced Pattern Scenarios

| Scenario | Advanced Pattern Strategy | Example |
|----------|---------------------------|----------|
| **Failed messages** | Dead Letter Exchange (DLX) | Error handling, retry mechanism |
| **Stale messages** | Message TTL (Expiry) | Time-sensitive data, news feeds |
| **Priority processing** | Priority Queue | Financial transactions, emergency alerts |
| **Large messages** | Lazy Queue | File processing, large payload |
| **High availability** | Master/Slave Pattern | Queue failover, redundancy |

### Required vs Optional

**Required when:**
- Production systems (any production environment)
- High reliability requirements (no message loss)
- High efficiency requirements (automatic cleanup)
- High availability requirements (queue failover)
- Memory efficiency requirements (large messages)
- Priority requirements (important messages first)
- Compliance requirements (audit trails, data retention)

**Optional when:**
- Development and testing environments
- Single node systems (simple patterns sufficient)
- Low-volume systems (few messages)
- Non-time-sensitive data (no expiration)

### Trade-offs

**Advanced Patterns:**
✅ Failed messages routing (Dead Letter Exchange)  
✅ Automatic message expiration (Message TTL)  
✅ Priority processing (Priority Queues)  
✅ Memory efficiency (Lazy Queues)  
✅ High availability (Master/Slave)  
✅ Audit trails (failure reasons visible)  
✅ Automatic cleanup (no manual intervention)  
✅ Production-ready (enterprise-grade)  
✅ Compliance (audit trails, data retention)  
❌ More complex setup (DLX, TTL, priorities)  
❌ More management (dead letter queues, expiration)  
❌ More monitoring (queue depths, expiration rates)  
❌ Performance overhead (priority processing)  

**Basic Patterns:**
✅ Simpler setup (direct, fanout, topic)  
✅ Easier to manage (basic exchanges)  
✅ Better performance (no advanced processing)  
❌ No failed messages routing (messages lost)  
❌ No automatic message expiration (stale messages)  
❌ No priority processing (FIFO only)  
❌ No memory efficiency (all messages in memory)  
❌ No high availability (single queue)  
❌ No audit trails (no failure reasons)  

---

## 4️⃣ How Advanced Patterns Work

### Dead Letter Exchange (DLX) Configuration Process

**Setting up Dead Letter Exchange:**

```
1. Create Dead Letter Exchange
   │
   ├─ Create exchange (type: fanout, direct, topic)
   ├─ Bind dead letter queue to dead letter exchange
   ├─ Create dead letter queue (stores failed messages)
   └─ Ready for failed message routing
   │
2. Configure Queue with Dead Letter Exchange
   │
   ├─ Set dead letter exchange (DLX) on queue
   ├─ Set dead letter routing key (DLRK) on queue
   ├─ Queue routes failed messages to dead letter exchange
   └─ Failed messages preserved (no data loss)
   │
3. Publish Message to Queue
   │
   ├─ Producer publishes message to queue
   ├─ Consumer processes message (fails or rejects)
   ├─ Message routed to dead letter exchange (if failed)
   └─ Dead letter queue receives failed message
   │
4. Consume from Dead Letter Queue
   │
   ├─ Consumer consumes failed messages
   ├─ Analyze failure reasons (audit trail)
   ├─ Retry message (re-publish to original queue)
   └─ Failed messages handled (no data loss)
   │
5. Dead Letter Exchange Flow:
   │
   ├─ Message published to queue
   ├─ Consumer fails (nack/reject)
   ├─ Message routed to dead letter exchange
   ├─ Dead letter queue receives failed message
   └─ Audit trail visible (failure reasons)
```

### Message TTL Configuration Process

**Setting up Message TTL:**

```
1. Configure Message TTL on Queue
   │
   ├─ Set message TTL (milliseconds) on queue
   ├─ Messages expire after TTL
   ├─ Expired messages discarded (automatic cleanup)
   └─ Stale messages removed (memory efficiency)
   │
2. Publish Message with TTL
   │
   ├─ Producer publishes message with TTL
   ├─ Message expires after TTL
   ├─ Expired message discarded (automatic cleanup)
   └─ Stale messages removed (memory efficiency)
   │
3. Message TTL Flow:
   │
   ├─ Message published to queue
   ├─ Timer starts (TTL countdown)
   ├─ Message expires after TTL
   ├─ Expired message discarded (automatic cleanup)
   └─ Stale messages removed (memory efficiency)
   │
4. Per-Message TTL:
   │
   ├─ Producer publishes message with per-message TTL
   ├─ Message expires after per-message TTL
   ├─ Expired message discarded (automatic cleanup)
   └─ Stale messages removed (memory efficiency)
```

### Priority Queue Configuration Process

**Setting up Priority Queues:**

```
1. Declare Queue with Priority
   │
   ├─ Set x-max-priority (max priority level)
   ├─ Messages with higher priority processed first
   ├─ Messages with same priority processed FIFO
   └─ Priority queue ready (express delivery)
   │
2. Publish Message with Priority
   │
   ├─ Producer publishes message with priority
   ├─ Message placed in queue at priority position
   ├─ High-priority messages at queue front (processed first)
   └─ Low-priority messages at queue back (processed later)
   │
3. Consume from Priority Queue
   │
   ├─ Consumer receives high-priority messages first
   ├─ Consumer receives low-priority messages later
   ├─ FIFO ordering within same priority level
   └─ Priority processing achieved (express delivery)
```

---

## 5️⃣ Installation / Setup

**Advanced Patterns are built-in RabbitMQ features.** No installation required - just configure queues with DLX, TTL, priorities, etc.

### Prerequisites

- RabbitMQ server running
- Understanding of advanced patterns (DLX, TTL, priorities)
- Understanding of message reliability (nack/reject, acknowledgments)
- Understanding of message efficiency (stale messages, priority processing)
- Access to RabbitMQ Management UI (port 15672)
- Understanding of queue configuration (arguments)

### Declaring Dead Letter Exchange

**Using rabbitmqctl:**

```bash
# Create dead letter exchange
sudo rabbitmqctl add_exchange dlx.direct direct

# Create dead letter queue
sudo rabbitmqctl add_queue dlx.queue

# Bind dead letter queue to dead letter exchange
sudo rabbitmqctl bind_queue dlx.queue dlx.direct ""

# Configure queue with dead letter exchange
sudo rabbitmqctl set_policy dlx "^.*$" \
  '{"dead-letter-exchange": "dlx.direct", "dead-letter-routing-key": ""}'

# Verify dead letter configuration
sudo rabbitmqctl list_queues | grep dlx
```

**Using Python (pika):**

```python
import pika

# Create dead letter exchange
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Create dead letter exchange
channel.exchange_declare(
    exchange='dlx.direct',
    exchange_type='direct',
    durable=True
)

# Create dead letter queue
channel.queue_declare(
    queue='dlx.queue',
    durable=True
)

# Bind dead letter queue to dead letter exchange
channel.queue_bind(
    queue='dlx.queue',
    exchange='dlx.direct',
    routing_key=''
)

# Create main queue with dead letter exchange
channel.queue_declare(
    queue='main.queue',
    durable=True,
    arguments={
        "x-dead-letter-exchange": "dlx.direct",
        "x-dead-letter-routing-key": ""
    }
)

print("[✓] Dead letter exchange configured")
connection.close()
```

### Declaring Message TTL

**Using Python (pika):**

```python
import pika
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Create queue with message TTL
channel.queue_declare(
    queue='ttl.queue',
    durable=True,
    arguments={
        "x-message-ttl": 60000  # CRITICAL: Message TTL (60 seconds)
    }
)

# Publish message with per-message TTL
channel.basic_publish(
    exchange='',
    routing_key='ttl.queue',
    body='Message with TTL',
    properties=pika.BasicProperties(
        expiration='30000'  # CRITICAL: Per-message TTL (30 seconds)
    )
)

print("[✓] Message TTL configured")
connection.close()
```

### Version Notes

- **RabbitMQ 3.12+:** All advanced pattern features fully supported
- **Dead Letter Exchange (DLX):** Failed message routing
- **Message TTL:** Message expiration time-to-live
- **Priority Queues:** High-priority messages processed first
- **Lazy Queues:** Messages loaded on demand (memory efficiency)
- **Master/Slave Pattern:** Primary/backup queue configuration
- **Per-Message TTL:** Individual message expiration

---

## 6️⃣ Where Advanced Patterns Should Be Applied (With Example)

### Dead Letter Exchange (DLX) for Failed Messages

**Scenario:** Financial transaction system with error handling

**DLX Configuration (dlx_producer.py):**

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Create dead letter exchange
channel.exchange_declare(
    exchange='dlx.direct',
    exchange_type='direct',
    durable=True
)

# CRITICAL: Create dead letter queue
channel.queue_declare(
    queue='dlx.queue',
    durable=True
)

# CRITICAL: Bind dead letter queue to dead letter exchange
channel.queue_bind(
    queue='dlx.queue',
    exchange='dlx.direct',
    routing_key=''
)

# CRITICAL: Create main queue with dead letter exchange
channel.queue_declare(
    queue='transactions',
    durable=True,
    arguments={
        "x-dead-letter-exchange": "dlx.direct",
        "x-dead-letter-routing-key": ""
    }
)

# CRITICAL: Publish transactions (DLX configured for failed messages)
for i in range(100):
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
    
    if i % 10 == 0:
        print(f"[x] Published {i} transactions")

print(f"[✓] Published 100 transactions (CRITICAL: DLX configured - failed messages routed)")
connection.close()
```

**Consumer with NACK (dlx_consumer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    transaction = json.loads(body)
    transaction_id = transaction["transaction_id"]
    amount = transaction["amount"]
    
    # CRITICAL: Simulate processing failure for odd transactions
    if amount % 2 == 1:
        print(f"[!] Transaction {transaction_id} failed (amount odd: {amount})")
        # CRITICAL: NACK message (routed to dead letter queue)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    else:
        print(f"[✓] Transaction {transaction_id} succeeded (amount even: {amount})")
        # CRITICAL: ACK message (processing successful)
        ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Consume from main queue (DLX configured)
channel.basic_consume(
    queue='transactions',
    on_message_callback=callback,
    auto_ack=False
)

print("[*] DLX consumer (CRITICAL: NACK messages routed to dead letter queue)")
channel.start_consuming()
```

**Dead Letter Consumer (dlx_analyzer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    transaction = json.loads(body)
    transaction_id = transaction.get("transaction_id", "unknown")
    
    # CRITICAL: Analyze failed message
    print(f"[!] Failed message: {transaction_id}")
    print(f"[!] Reason: {headers.get('x-death-reason', 'unknown')}")
    
    # CRITICAL: Retry message (re-publish to original queue)
    ch.basic_publish(
        exchange='',
        routing_key='transactions',
        body=body
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Consume from dead letter queue (analyze failed messages)
channel.basic_consume(
    queue='dlx.queue',
    on_message_callback=callback,
    auto_ack=False
)

print("[*] DLX analyzer (CRITICAL: Analyzing failed messages from dead letter queue)")
channel.start_consuming()
```

### Message TTL for Stale Messages

**TTL Producer (ttl_producer.py):**

```python
import pika
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Create queue with message TTL (60 seconds)
channel.queue_declare(
    queue='news_feed',
    durable=True,
    arguments={
        "x-message-ttl": 60000  # CRITICAL: Message TTL (60 seconds)
    }
)

# CRITICAL: Publish news articles (with per-message TTL)
for i in range(100):
    article = {
        "article_id": f"article_{i+1:04d}",
        "headline": f"News Article {i+1}",
        "timestamp": time.time()
    }
    
    # CRITICAL: Publish with per-message TTL (30 seconds)
    channel.basic_publish(
        exchange='',
        routing_key='news_feed',
        body=str(article),
        properties=pika.BasicProperties(
            expiration='30000'  # CRITICAL: Per-message TTL (30 seconds)
        )
    )
    
    if i % 10 == 0:
        print(f"[x] Published {i} articles")

print(f"[✓] Published 100 articles (CRITICAL: Message TTL configured - stale messages auto-expire)")
connection.close()
```

### Priority Queue for Emergency Alerts

**Priority Producer (priority_producer.py):**

```python
import pika
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Create priority queue (priority levels 0-9)
channel.queue_declare(
    queue='alerts',
    durable=True,
    arguments={
        "x-max-priority": 10  # CRITICAL: Max priority level (0-9)
    }
)

# CRITICAL: Publish alerts with priority
for i in range(100):
    if i % 10 == 0:
        # CRITICAL: Emergency alert (priority 9)
        alert = {
            "alert_id": f"alert_{i}",
            "severity": "emergency",
            "message": f"Emergency Alert {i}",
            "priority": 9
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='alerts',
            body=str(alert),
            properties=pika.BasicProperties(
                priority=9  # CRITICAL: Priority 9 (highest)
            )
        )
    else:
        # CRITICAL: Normal alert (priority 0)
        alert = {
            "alert_id": f"alert_{i}",
            "severity": "normal",
            "message": f"Normal Alert {i}",
            "priority": 0
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='alerts',
            body=str(alert),
            properties=pika.BasicProperties(
                priority=0  # CRITICAL: Priority 0 (lowest)
            )
        )
    
    if i % 10 == 0:
        print(f"[x] Published {i} alerts")

print(f"[✓] Published 100 alerts (CRITICAL: Priority queue configured - emergency alerts first)")
connection.close()
```

### Best Practices

**Dead Letter Exchange (DLX):**
✅ Use DLX for failed messages (no data loss)  
✅ Use DLX for rejected messages (visibility into failures)  
✅ Use DLX for expired messages (audit trail)  
✅ Consume from DLX queue (analyze failures, retry messages)  
✅ Monitor DLX queue depth (failure rate visible)  
✅ Use per-message TTL (message-level expiration)  

**Message TTL:**
✅ Use message TTL for stale message cleanup (automatic)  
✅ Use per-message TTL (message-level expiration)  
✅ Set appropriate TTL (based on message freshness)  
✅ Monitor TTL expiration rates (cleanup visible)  
✅ Use DLX with TTL (expired messages to DLX)  

**Priority Queues:**
✅ Use priority queues for important messages (express delivery)  
✅ Set appropriate max priority (enough levels for message importance)  
✅ Use same priority for same message type (FIFO within priority)  
✅ Monitor priority queue depth (backlog visible)  
✅ Use consumer prefetch with priority (fair dispatch within priority)  

**Lazy Queues:**
✅ Use lazy queues for large messages (memory efficiency)  
✅ Use lazy queues for file processing (on-demand loading)  
✅ Monitor lazy queue performance (loading latency)  

**Master/Slave Pattern:**
✅ Use master/slave for high availability (queue failover)  
✅ Configure slave to take over if master fails (automatic)  
✅ Monitor master/slave status (failover visible)  

### Common Mistakes

❌ Not using DLX → Failed messages lost (no retry)  
❌ Not using message TTL → Stale messages clog queues (memory waste)  
❌ Not using priorities → Important messages delayed (FIFO only)  
❌ Setting max priority too low → Not enough granularity  
❌ Setting TTL too short → Messages expire too quickly (data loss)  
❌ Setting TTL too long → Stale messages remain (memory waste)  
❌ Not monitoring DLX queue depth → Failure rate not visible  
❌ Not monitoring TTL expiration → Cleanup rate not visible  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Failed Messages Lost (The "Data Loss" Problem)**

You're building a production messaging system:

- System must be highly reliable (no message loss)
- Failed messages discarded (no retry mechanism)
- No visibility into failure reasons (audit trail missing)
- Manual intervention required (no automatic retry)
- Data loss on message failure

Current implementation:
- No Dead Letter Exchange (DLX)
- No message TTL (stale messages clog queues)
- No priority queues (FIFO only)
- Failed messages discarded (no retry)
- No visibility into failures

**Problems:**
- Failed messages lost (data loss)
- No visibility into failure reasons (audit trail missing)
- No retry mechanism (manual intervention)
- Stale messages clog queues (memory waste)
- No priority processing (important messages delayed)
- **Impact:** Data loss, poor reliability, manual intervention, inefficiency

### 🧪 Lab Tasks

**Step 1: Create producer without advanced patterns**

Create `basic_producer.py`:

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: No DLX (failed messages lost)
channel.queue_declare(queue='transactions', durable=True)

# PROBLEM: Publish messages (no DLX, no TTL, no priorities)
for i in range(100):
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
    
    if i % 10 == 0:
        print(f"[x] Published {i} transactions")

print(f"[!] Published 100 transactions (PROBLEM: No DLX - failed messages lost)")
connection.close()
```

**Step 2: Create consumer without NACK**

Create `basic_consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    transaction = json.loads(body)
    transaction_id = transaction["transaction_id"]
    amount = transaction["amount"]
    
    # PROBLEM: Consumer always succeeds (no failures)
    # PROBLEM: No NACK mechanism (failed messages not routed to DLX)
    print(f"[✓] Processing transaction: {transaction_id} (amount: {amount})")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: No NACK mechanism (failed messages not routed to DLX)
channel.basic_consume(queue='transactions', on_message_callback=callback)

print("[!] Basic consumer (PROBLEM: No NACK - failed messages not routed to DLX)")
channel.start_consuming()
```

**Step 3: Simulate failures**

```bash
# Terminal: Basic consumer
python3 basic_consumer.py

# Terminal: Basic producer
python3 basic_producer.py
```

**Expected observation:**
- Producer publishes 100 transactions
- Consumer processes all transactions (no failures)
- No DLX configured (failed messages lost)
- No TTL configured (stale messages clog queues)
- No priorities (FIFO only)
- **Impact:** Data loss if failures occur, no visibility into failures, inefficiency

**Step 4: View in Management UI**

Open http://localhost:15672:
- Go to Queues tab
- See transactions queue (no DLX configured)
- See no dead letter queue
- See no TTL (stale messages)

### ✅ Solution & Explanation

**Solution: Implement Advanced Patterns (DLX + TTL + Priorities)**

**Step 1: Create DLX producer**

Create `dlx_producer.py`:

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Create dead letter exchange
channel.exchange_declare(
    exchange='dlx.direct',
    exchange_type='direct',
    durable=True
)

# SOLUTION: Create dead letter queue
channel.queue_declare(
    queue='dlx.queue',
    durable=True
)

# SOLUTION: Bind dead letter queue to dead letter exchange
channel.queue_bind(
    queue='dlx.queue',
    exchange='dlx.direct',
    routing_key=''
)

# SOLUTION: Create main queue with DLX
channel.queue_declare(
    queue='transactions',
    durable=True,
    arguments={
        "x-dead-letter-exchange": "dlx.direct",
        "x-dead-letter-routing-key": ""
    }
)

# SOLUTION: Create priority queue with TTL
channel.queue_declare(
    queue='alerts',
    durable=True,
    arguments={
        "x-max-priority": 10,  # SOLUTION: Max priority (0-9)
        "x-message-ttl": 60000  # SOLUTION: Message TTL (60 seconds)
    }
)

# SOLUTION: Publish transactions (DLX configured)
for i in range(100):
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
    
    if i % 10 == 0:
        print(f"[x] Published {i} transactions")

# SOLUTION: Publish alerts with priority and TTL
for i in range(100):
    if i % 10 == 0:
        # SOLUTION: Emergency alert (priority 9)
        alert = {
            "alert_id": f"alert_{i}",
            "severity": "emergency",
            "message": f"Emergency Alert {i}",
            "priority": 9,
            "timestamp": time.time()
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='alerts',
            body=str(alert),
            properties=pika.BasicProperties(
                priority=9,  # SOLUTION: Priority 9 (highest)
                expiration='30000'  # SOLUTION: TTL (30 seconds)
            )
        )
    else:
        # SOLUTION: Normal alert (priority 0)
        alert = {
            "alert_id": f"alert_{i}",
            "severity": "normal",
            "message": f"Normal Alert {i}",
            "priority": 0,
            "timestamp": time.time()
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='alerts',
            body=str(alert),
            properties=pika.BasicProperties(
                priority=0,  # SOLUTION: Priority 0 (lowest)
                expiration='60000'  # SOLUTION: TTL (60 seconds)
            )
        )
    
    if i % 10 == 0:
        print(f"[x] Published {i} alerts")

print(f"[✓] Published 100 transactions + 100 alerts (SOLUTION: DLX + TTL + Priorities)")
connection.close()
```

**Step 2: Create consumer with NACK**

Create `dlx_consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    transaction = json.loads(body)
    transaction_id = transaction.get("transaction_id", "unknown")
    
    # SOLUTION: Simulate processing failure for odd transactions
    if transaction_id and int(transaction_id.split("_")[1]) % 2 == 1:
        print(f"[!] Transaction {transaction_id} failed (odd ID)")
        # SOLUTION: NACK message (routed to dead letter queue)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    else:
        print(f"[✓] Transaction {transaction_id} succeeded (even ID)")
        # SOLUTION: ACK message (processing successful)
        ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Consume from main queue (DLX configured)
channel.basic_consume(
    queue='transactions',
    on_message_callback=callback,
    auto_ack=False
)

print("[*] DLX consumer (SOLUTION: NACK messages routed to dead letter queue)")
channel.start_consuming()
```

**Step 3: Create DLX analyzer**

Create `dlx_analyzer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    transaction = json.loads(body)
    transaction_id = transaction.get("transaction_id", "unknown")
    
    # SOLUTION: Analyze failed message
    print(f"[!] Failed message: {transaction_id}")
    
    # SOLUTION: Retry message (re-publish to original queue)
    ch.basic_publish(
        exchange='',
        routing_key='transactions',
        body=body
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Consume from dead letter queue (analyze failed messages)
channel.basic_consume(
    queue='dlx.queue',
    on_message_callback=callback,
    auto_ack=False
)

print("[*] DLX analyzer (SOLUTION: Analyzing failed messages from dead letter queue)")
channel.start_consuming()
```

**How to verify:**

```bash
# Terminal: DLX consumer
python3 dlx_consumer.py

# Terminal: DLX producer
python3 dlx_producer.py

# Terminal: DLX analyzer (after failures)
python3 dlx_analyzer.py
```

**Expected output:**

```
# DLX Producer
[x] Published 10 transactions
[x] Published 20 transactions
...
[x] Published 100 transactions
[x] Published 10 alerts
[x] Published 20 alerts
...
[x] Published 100 alerts
[✓] Published 100 transactions + 100 alerts (SOLUTION: DLX + TTL + Priorities)

# DLX Consumer
[*] DLX consumer (SOLUTION: NACK messages routed to dead letter queue)
[!] Transaction txn_0002 failed (odd ID)
[!] Transaction txn_0004 failed (odd ID)
...
[!] Transaction txn_0100 failed (odd ID)
[✓] Transaction txn_0001 succeeded (even ID)
[✓] Transaction txn_0003 succeeded (even ID)

# DLX Analyzer
[*] DLX analyzer (SOLUTION: Analyzing failed messages from dead letter queue)
[!] Failed message: txn_0002
[!] Failed message: txn_0004
...
[!] Failed message: txn_0100
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Queues tab
3. See transactions queue (DLX configured)
4. See alerts queue (priorities + TTL configured)
5. See dlx.queue (dead letter queue with failed messages)
6. See DLX exchange (dead letter routing)

**Comparison:**

| Design | DLX | TTL | Priorities |
|--------|-----|-----|-----------|
| Basic (old) | No | No | No |
| Advanced (new) | Yes | Yes | Yes |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Use DLX for failed messages (no data loss)  
- Use DLX for rejected messages (visibility into failures)  
- Use DLX for expired messages (audit trail)  
- Consume from DLX queue (analyze failures, retry messages)  
- Use message TTL for stale message cleanup (automatic)  
- Use per-message TTL (message-level expiration)  
- Use priority queues for important messages (express delivery)  
- Set appropriate max priority (enough levels)  
- Monitor DLX queue depth (failure rate visible)  
- Monitor TTL expiration rates (cleanup visible)  
- Use lazy queues for large messages (memory efficiency)  

**❌ Don't:**
- Not using DLX → Failed messages lost (no retry)  
- Not using message TTL → Stale messages clog queues (memory waste)  
- Not using priorities → Important messages delayed (FIFO only)  
- Setting max priority too low → Not enough granularity  
- Setting TTL too short → Messages expire too quickly (data loss)  
- Setting TTL too long → Stale messages remain (memory waste)  
- Not monitoring DLX queue depth → Failure rate not visible  
- Not monitoring TTL expiration → Cleanup rate not visible  
- Setting too many priority levels → Performance overhead  

### Advanced Patterns Guidelines

```
Dead Letter Exchange (DLX):
├─ Use for failed messages (no data loss)
├─ Use for rejected messages (visibility into failures)
├─ Use for expired messages (audit trail)
└─ Consume from DLX queue (analyze failures, retry messages)

Message TTL:
├─ Use for stale message cleanup (automatic)
├─ Use per-message TTL (message-level expiration)
├─ Set appropriate TTL (based on message freshness)
└─ Monitor TTL expiration (cleanup visible)

Priority Queues:
├─ Use for important messages (express delivery)
├─ Set appropriate max priority (enough levels)
├─ Use same priority for same message type (FIFO)
└─ Monitor priority queue depth (backlog visible)

Lazy Queues:
├─ Use for large messages (memory efficiency)
├─ Use for file processing (on-demand loading)
└─ Monitor lazy queue performance (loading latency)

Master/Slave Pattern:
├─ Use for high availability (queue failover)
├─ Configure slave to take over (automatic)
└─ Monitor master/slave status (failover visible)
```

### Production Considerations

**DLX for Multiple Queues:**

```python
# Configure DLX for multiple queues
for queue in ['transactions', 'orders', 'notifications']:
    channel.queue_declare(
        queue=queue,
        durable=True,
        arguments={
            "x-dead-letter-exchange": "dlx.direct",
            "x-dead-letter-routing-key": ""
        }
    )
```

**DLX for Cross-Virtual Host:**

```bash
# Configure DLX for cross-virtual host routing
sudo rabbitmqctl set_policy cross_vhost_dlx "^.*$" \
  '{"dead-letter-exchange": "dlx.direct", "dead-letter-exchange-type": "direct"}'
```

**Priority Queues with Consumer Prefetch:**

```python
# Combine priority queues with consumer prefetch
channel.basic_qos(prefetch_count=10)  # Fair dispatch within priority
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's Dead Letter Exchange (DLX)?**

A: Dead Letter Exchange is RabbitMQ feature for routing failed/undeliverable messages to dead letter queue. Queue configured with dead letter exchange and routing key. If message fails (nack/reject), message routed to dead letter exchange. Dead letter queue receives failed messages. Consumers can analyze failures, retry messages. Provides visibility into failures, audit trail, no data loss.

**Q2: What's Message TTL?**

A: Message TTL (Time-To-Live) is message expiration feature. Queue configured with message TTL. Messages expire after TTL. Expired messages discarded (automatic cleanup). Per-message TTL overrides queue-level TTL. Provides automatic cleanup, memory efficiency, fresh data processing.

**Q3: What's Priority Queue?**

A: Priority Queue is RabbitMQ feature for high-priority message processing. Queue configured with x-max-priority. Messages have priority (0 = low, max-priority = high). High-priority messages processed first (express delivery). Same priority messages processed FIFO. Provides priority processing for important messages.

**Q4: What's Lazy Queue?**

A: Lazy Queue is RabbitMQ feature for memory efficiency. Messages stored on disk (not memory). Messages loaded on demand (when consumer reads). Reduces memory usage for large messages. Provides memory efficiency, better resource utilization.

**Q5: How do you configure Dead Letter Exchange?**

A: Create dead letter exchange (direct, fanout, topic). Create dead letter queue. Bind dead letter queue to dead letter exchange. Configure main queue with x-dead-letter-exchange and x-dead-letter-routing-key arguments. Consume from dead letter queue (analyze failures, retry messages). Monitor DLX queue depth (failure rate visible).

### Production Pitfalls

**Pitfall 1: Not using DLX**
- Problem: Failed messages lost (no retry)
- Detection: Data loss (messages missing)
- Solution: Always use DLX for production (no data loss)

**Pitfall 2: Not using Message TTL**
- Problem: Stale messages clog queues (memory waste)
- Detection: Queue depth increases (stale messages)
- Solution: Always use message TTL (automatic cleanup)

**Pitfall 3: Not using Priorities**
- Problem: Important messages delayed (FIFO only)
- Detection: Emergency alerts delayed (in queue back)
- Solution: Always use priorities for important messages (express delivery)

**Pitfall 4: Setting TTL too short**
- Problem: Messages expire too quickly (data loss)
- Detection: Messages missing (expired too quickly)
- Solution: Set appropriate TTL (based on message freshness)

**Pitfall 5: Setting max priority too low**
- Problem: Not enough granularity (few priority levels)
- Detection: Same priority for different message types
- Solution: Set appropriate max priority (enough levels for message importance)

### Advanced Pattern Concepts

**DLX with Multiple Queues:**

```python
# Configure DLX for multiple queues
dead_letter_exchanges = {
    "transactions": "dlx.transactions",
    "orders": "dlx.orders",
    "notifications": "dlx.notifications"
}

for queue, dlx in dead_letter_exchanges.items():
    channel.exchange_declare(
        exchange=dlx,
        exchange_type='direct',
        durable=True
    )
    channel.queue_declare(
        queue=f"dlx.{queue}",
        durable=True
    )
    channel.queue_bind(
        queue=f"dlx.{queue}",
        exchange=dlx,
        routing_key=''
    )
    channel.queue_declare(
        queue=queue,
        durable=True,
        arguments={
            "x-dead-letter-exchange": dlx,
            "x-dead-letter-routing-key": ""
        }
    )
```

**Per-Message TTL with DLX:**

```python
# Publish message with per-message TTL and DLX
channel.basic_publish(
    exchange='',
    routing_key='transactions',
    body='message',
    properties=pika.BasicProperties(
        expiration='30000',  # Per-message TTL (30 seconds)
        headers={
            "x-death": {}  # DLX headers
        }
    )
)
```

**Priority Queues with DLX:**

```python
# Priority queue with DLX
channel.queue_declare(
    queue='priority.transactions',
    durable=True,
    arguments={
        "x-max-priority": 10,
        "x-dead-letter-exchange": "dlx.direct",
        "x-dead-letter-routing-key": ""
    }
)

# Publish with priority and DLX
channel.basic_publish(
    exchange='',
    routing_key='priority.transactions',
    body='message',
    properties=pika.BasicProperties(
        priority=9,  # High priority
        expiration='60000'  # TTL
    )
)
```

---

## 📚 Summary

Advanced Message Patterns provide sophisticated message routing and processing techniques beyond basic exchanges. Dead Letter Exchange (DLX) routes failed/undeliverable messages, Message TTL expires stale messages automatically, Priority Queues process important messages first, Lazy Queues provide memory efficiency, and Master/Slave Pattern provides high availability.

**Key takeaways:**
- Use DLX for failed messages (no data loss)
- Use Message TTL for stale message cleanup (automatic)
- Use Priority Queues for important messages (express delivery)
- Use Lazy Queues for large messages (memory efficiency)
- Use Master/Slave for high availability (queue failover)
- Monitor DLX queue depth (failure rate visible)
- Monitor TTL expiration (cleanup rate visible)
- Monitor priority queue depth (backlog visible)
- Consume from DLX queue (analyze failures, retry messages)
- Use per-message TTL (message-level expiration)
- Set appropriate max priority (enough levels)
- Set appropriate TTL (based on message freshness)

**Next steps:**
- Practice with advanced patterns in your applications
- Learn about message ordering and consistency (next lesson)
- Learn about multi-data centers and global queues
- Complete all lessons in Module 04

---

**Module 04 - Advanced Concepts**  
**Lesson 05 - Complete**