# 02-05: Consumer Prefetch and Fair Dispatch

## 1️⃣ What Are Consumer Prefetch and Fair Dispatch

**Consumer Prefetch** (also called QoS - Quality of Service) is a limit on how many unacknowledged messages a consumer can receive at once. **Fair Dispatch** is the distribution of messages across consumers in a way that ensures no single consumer is overwhelmed.

Think of prefetch and fair dispatch like restaurant service:

- **Messages** = Dishes to be served
- **RabbitMQ** = The restaurant manager
- **Consumers** = Waiters/servers
- **Prefetch** = Maximum dishes a waiter can carry at once
- **Fair Dispatch** = Ensuring dishes distributed evenly across waiters

**Where prefetch and fair dispatch fit in RabbitMQ architecture:**

```
┌─────────────┐
│  Producer   │
└──────┬──────┘
       │
       │ Publishes messages
       ▼
┌─────────────────────────────────────────────┐
│           Queue                         │
│    (Buffer: 1000 messages)          │
│                                      │
│  ┌────────────────────────────────────┐ │
│  │ Consumer A (prefetch: 1)     │ │
│  │ Receives 1 message           │ │
│  │ Processes message              │ │
│  │ Only after ACK receives next   │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │ Consumer B (prefetch: 1)     │ │
│  │ Receives 1 message           │ │
│  │ Processes message              │ │
│  │ Only after ACK receives next   │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │ Consumer C (prefetch: 1)     │ │
│  │ Receives 1 message           │ │
│  │ Processes message              │ │
│  │ Only after ACK receives next   │ │
│  └────────────────────────────────────┘ │
│                                      │
│  FAIR DISPATCH: 333 each         │
│  (Messages distributed evenly)       │
└─────────────────────────────────────────────┘
```

**Key concepts:**
- **Prefetch Count:** Maximum unacknowledged messages a consumer can have
- **QoS (Quality of Service):** The prefetch setting per channel
- **Fair Dispatch:** Even distribution of messages across consumers
- **Slow Consumer Problem:** One slow consumer hogs all messages
- **Fast Consumer Problem:** One fast consumer receives all messages
- **Per-Channel Prefetch:** Set once per consumer channel

---

## 2️⃣ Problems Solved by Consumer Prefetch and Fair Dispatch

### The "Slow Consumer Hogging Messages" Problem

Without prefetch (default prefetch = unlimited):

- Fast consumer receives all messages
- Slow consumer gets nothing
- Slow consumer's messages pile up in queue
- System appears stuck when slow consumer exists

**Real-world failure scenario:**

A file processing system had:

```
Producer → Queue → 3 Consumers
                    │
                    ├─ Consumer A (fast): 5 files/second
                    ├─ Consumer B (slow): 0.1 files/second
                    └─ Consumer C (fast): 5 files/second

Producer publishes: 1000 files/second
```

**Problems:**
- Consumer A (fast) receives 1000 messages immediately
- Consumer B (slow) receives 0 messages (Consumer A is faster)
- Consumer C (fast) receives 0 messages (Consumer A is faster)
- Consumer A overwhelmed with 1000 messages
- Consumer B and C sit idle
- System appears unresponsive (slow consumer never gets work)
- **Impact:** Poor resource utilization, system appears broken, wasted resources

After implementing prefetch:
- Each consumer gets 10 messages at a time
- Consumer A processes 10, gets 10 more
- Consumer B processes 1, gets 10 more
- Consumer C processes 10, gets 10 more
- Even distribution across all consumers
- **Result:** Fair resource utilization, all consumers working efficiently

### The "Memory Overload" Problem

Without prefetch:

- Consumer receives thousands of messages
- Consumer runs out of memory
- Consumer crashes with Out Of Memory (OOM)
- Messages lost (unacked messages requeued)
- System destabilizes

**Example:**

```
Consumer (no prefetch limit):
├─ Receives 10,000 messages at once
├─ Loads all into memory
├─ Memory: 10,000 × 1MB = 10GB
├─ Consumer RAM: 8GB
└─ CRASH: Out Of Memory

Recovery:
├─ 10,000 messages unacked
├─ All requeued back to queue
├─ System appears stuck (10K messages requeued)
└─ Other consumers overwhelmed
```

**Problems:**
- Consumer OOM crash
- Unacked messages requeued (processing duplication)
- System destabilizes
- Recovery takes time
- **Impact:** Service outage, data duplication, system instability

After implementing prefetch:
- Consumer receives only 100 messages at a time
- Consumer processes 100, gets 100 more
- Memory usage bounded (100 × 1MB = 100MB)
- Consumer stable, no OOM
- **Result:** Stable system, bounded memory, no crashes

---

## 3️⃣ When You Should Use Consumer Prefetch and Fair Dispatch

### Development vs Production

**Development:**
- Can use default prefetch (unlimited)
- Faster message processing (no limit)
- OK for simple tests with few messages
- Don't use in production code

**Production:**
- Absolutely required for all consumers
- Essential for preventing memory overload
- Critical for fair distribution
- Required for long-running tasks
- Necessary for resource management

### Prefetch Settings

| Consumer Type | Prefetch Count | Example |
|---------------|----------------|----------|
| **Short tasks (100ms)** | 50-100 | Image processing, simple routing |
| **Medium tasks (1s)** | 10-20 | API calls, database writes |
| **Long tasks (10s)** | 1-5 | File processing, video encoding |
| **Very long tasks (60s)** | 1 | Email sending, PDF generation |
| **Variable tasks** | 5-10 | Mixed workloads |

### Required vs Optional

**Required when:**
- Production consumers (always)
- Long-running processing tasks
- Multiple consumers sharing same queue
- Memory constraints
- High-throughput systems
- Fair distribution required

**Optional when:**
- Single consumer (no competition)
- Very short tasks (microseconds)
- Development and testing
- Fire-and-forget processing
- Unlimited memory available

### Trade-offs

**Consumer Prefetch:**
✅ Prevents memory overload  
✅ Enables fair distribution  
✅ Bounded resource usage  
✅ Predictable system behavior  
✅ Better resource utilization  
❌ Slower throughput (more network round-trips)  
❌ More complex configuration  
❌ Requires tuning for optimal performance  
❌ Lower prefetch may cause idle time (ACK delay)  

**No Prefetch (unlimited):**
✅ Faster throughput (less network round-trips)  
✅ Simpler configuration  
✅ Consumer never waits for messages  
❌ Memory overload risk  
❌ Unfair distribution  
❌ Resource hogging by fast consumers  
❌ Unbounded resource usage  
❌ System instability  

---

## 4️⃣ How Consumer Prefetch and Fair Dispatch Work

### Prefetch Configuration Process

**Setting up prefetch:**

```
1. Producer Publishes Messages
   │
   ├─ Messages accumulate in queue
   └─ Queue depth: 1000
   │
2. Consumers Start
   │
   ├─ Consumer A connects, sets prefetch=10
   ├─ Consumer B connects, sets prefetch=10
   └─ Consumer C connects, sets prefetch=10
   │
3. RabbitMQ Distributes Messages
   │
   ├─ Consumer A receives first 10 messages
   ├─ Consumer B receives next 10 messages
   ├─ Consumer C receives next 10 messages
   └─ Remaining messages wait in queue
   │
4. Consumer Processing
   │
   ├─ Consumer A processes 1 message, ACKs
   ├─ RabbitMQ sends 11th message to Consumer A
   ├─ Consumer B processes 1 message, ACKs
   └─ RabbitMQ sends 11th message to Consumer B
   │
5. Fair Dispatch
   │
   └─ Messages distributed evenly (333 each over time)
```

### Prefetch vs Fair Dispatch

**Without Prefetch:**

```
Queue: 1000 messages
Consumers: 3 (A=fast, B=fast, C=slow)

RabbitMQ Dispatch (no prefetch limit):
├─ Round-robin: A, B, C, A, B, C, ...
├─ After first round:
│  ├─ Consumer A: 334 messages (prefetch=unlimited)
│  ├─ Consumer B: 333 messages (prefetch=unlimited)
│  └─ Consumer C: 333 messages (prefetch=unlimited)
└─ After processing round:
   ├─ Consumer A (fast) gets more messages
   ├─ Consumer B (fast) gets more messages
   └─ Consumer C (slow) gets fewer messages

UNFAIR: Fast consumers get more work
```

**With Prefetch:**

```
Queue: 1000 messages
Consumers: 3 (A=fast, B=fast, C=slow)
Prefetch: 10 per consumer

RabbitMQ Dispatch (with prefetch):
├─ Round-robin: A, B, C, A, B, C, ...
├─ After first round:
│  ├─ Consumer A: 10 messages (prefetch=10)
│  ├─ Consumer B: 10 messages (prefetch=10)
│  └─ Consumer C: 10 messages (prefetch=10)
└─ After processing round (based on ACK speed):
   ├─ Each consumer gets 10 more messages
   └─ Over time: ~333 messages each (fair)

FAIR: Each consumer gets same amount of work
```

### Prefetch Mechanism

**How prefetch limits unacked messages:**

```
Queue: orders
Consumers: 2 (A, B)
Prefetch: 5

Message Flow:
┌─────────────┐
│  Producer   │
└──────┬──────┘
       │
       │ Publishes 20 orders
       ▼
┌─────────────────────────────┐
│      Queue            │
│  (Ready: 20 messages)  │
└──────┬──────────────────┘
       │
       ├───────────────┬───────────────┐
       │               │               │
       ▼               ▼               ▼
┌──────────────┐┌──────────────┐┌──────────────┐
│ Consumer A   ││ Consumer B   ││     Ready    │
│ (prefetch:5) ││ (prefetch:5) ││   (10 msgs)  │
└──────┬───────┘└──────┬───────┘└──────────────┘
       │               │
       ├─ 5 messages   ├─ 5 messages
       │   (unacked)   │   (unacked)
       │               │
┌──────────────┐┌──────────────┐
│ Unacked A: 5 ││ Unacked B: 5 │
│ Processing... ││ Processing... │
└──────────────┘└──────────────┘
```

**Prefetch states:**
- **Ready:** Messages waiting in queue
- **Unacked:** Sent to consumer but not yet acknowledged
- **Prefetch limit:** Maximum unacked messages per consumer
- **Fair dispatch:** Distributes based on prefetch availability

---

## 5️⃣ Installation / Setup

**Consumer Prefetch and Fair Dispatch are built-in RabbitMQ features.** No installation required - just set prefetch count on consumer channel.

### Prerequisites

- RabbitMQ server running
- AMQP client library that supports prefetch
- Understanding of consumer processing time

### Setting Prefetch Count

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare queue
channel.queue_declare(queue='orders')

# CRITICAL: Set prefetch (Quality of Service)
channel.basic_qos(prefetch_count=10)

print("[✓] Prefetch set to 10 (max 10 unacknowledged messages)")
connection.close()
```

**Node.js (amqplib):**

```javascript
const amqp = require('amqplib/callback_api');

const connection = amqp.connect('amqp://localhost');
const channel = connection.createChannel();

// CRITICAL: Set prefetch (prefetch = max unacknowledged messages)
channel.prefetch(10);

console.log('[✓] Prefetch set to 10');
```

**Java (RabbitMQ Java Client):**

```java
import com.rabbitmq.client.*;

ConnectionFactory factory = new ConnectionFactory();
factory.setHost("localhost");
Connection connection = factory.newConnection();
Channel channel = connection.createChannel();

// CRITICAL: Set prefetch (max unacknowledged messages per consumer)
int prefetchCount = 10;
channel.basicQos(prefetchCount);

System.out.println("[✓] Prefetch set to " + prefetchCount);
```

### Setting Prefetch Per Channel

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare queue
channel.queue_declare(queue='orders')

# CRITICAL: Set prefetch PER CHANNEL
# Different channels can have different prefetch counts
channel.basic_qos(prefetch_count=10)

print("[✓] Channel 1: Prefetch = 10")

# Create second channel with different prefetch
channel2 = connection.channel()
channel2.basic_qos(prefetch_count=5)  # Different prefetch

print("[✓] Channel 2: Prefetch = 5")
connection.close()
```

### Version Notes

- **RabbitMQ 3.12+:** All prefetch features fully supported
- **AMQP 0-9-1+:** Prefetch protocol standard
- **Default prefetch:** Unlimited (not safe for production)
- **Per-channel prefetch:** Each channel can have different prefetch
- **Prefetch count:** Maximum unacknowledged messages (not total received)

---

## 6️⃣ Where Consumer Prefetch and Fair Dispatch Should Be Applied (With Example)

### Producer with High Throughput

**Scenario:** Order system with high throughput (1000 orders/second)

**Producer (fast_producer.py):**

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='orders')

# Send 1000 orders rapidly
start = time.time()
for i in range(1000):
    order = {
        "order_id": f"order_{i+1:04d}",
        "amount": (i+1) * 10.00,
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='orders',
        body=json.dumps(order)
    )
    
    # Progress indicator
    if (i+1) % 100 == 0:
        print(f"[x] Sent {i+1} orders...")

elapsed = time.time() - start
print(f"[✓] Sent 1000 orders in {elapsed:.2f} seconds")
connection.close()
```

**Expected output:**

```
[x] Sent 100 orders...
[x] Sent 200 orders...
...
[x] Sent 1000 orders in 1.23 seconds
```

### Consumer with Prefetch (Fair Distribution)

**Consumer (fair_consumer.py):**

```python
import pika
import json

def process_order(order_data):
    """Process order (simulates variable processing time)"""
    order = json.loads(order_data)
    
    # Simulate variable processing time (100ms - 2s)
    import time
    processing_time = 0.1 + (order['order_id'][-1] * 0.05)
    
    # Process order
    time.sleep(processing_time)
    
    print(f"[✓] Processed order {order['order_id']} ${order['amount']:.2f} (took {processing_time:.2f}s)")
    return True

def callback(ch, method, properties, body):
    """Process order with ACK"""
    process_order(body)
    
    # CRITICAL: Acknowledge after processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='orders')

# CRITICAL: Set prefetch (fair dispatch)
# Each consumer gets at most 10 messages at once
channel.basic_qos(prefetch_count=10)

# CRITICAL: Manual acknowledgment (required with prefetch)
channel.basic_consume(
    queue='orders',
    on_message_callback=callback,
    auto_ack=False  # FALSE = Manual acknowledgment
)

print('[*] Consumer with prefetch=10 (fair dispatch)')
channel.start_consuming()
```

**Multiple Consumers (Fair Distribution)**

**Consumer 1 (consumer1.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    import time
    time.sleep(0.5)  # Simulate processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='orders')
channel.basic_qos(prefetch_count=10)
channel.basic_consume(queue='orders', on_message_callback=callback, auto_ack=False)

print('[*] Consumer 1 (prefetch=10)')
channel.start_consuming()
```

**Consumer 2 (consumer2.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    import time
    time.sleep(0.5)  # Simulate processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='orders')
channel.basic_qos(prefetch_count=10)
channel.basic_consume(queue='orders', on_message_callback=callback, auto_ack=False)

print('[*] Consumer 2 (prefetch=10)')
channel.start_consuming()
```

**Consumer 3 (consumer3.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    import time
    time.sleep(0.5)  # Simulate processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='orders')
channel.basic_qos(prefetch_count=10)
channel.basic_consume(queue='orders', on_message_callback=callback, auto_ack=False)

print('[*] Consumer 3 (prefetch=10)')
channel.start_consuming()
```

**How to test fair distribution:**

```bash
# Terminal 1: Consumer 1
python3 consumer1.py

# Terminal 2: Consumer 2
python3 consumer2.py

# Terminal 3: Consumer 3
python3 consumer3.py

# Terminal 4: Producer
python3 fast_producer.py
```

**Expected output:**

```
# Producer
[x] Sent 100 orders...
[x] Sent 200 orders...
[x] Sent 1000 orders in 1.23 seconds

# Consumer 1
[*] Consumer 1 (prefetch=10)
[x] Received order: order_0001 $10.00 (took 0.10s)
[x] Received order: order_0002 $20.00 (took 0.15s)
...
[✓] Processed order order_0010 $100.00 (took 0.50s)
[x] Received order: order_0011 $110.00 (took 0.15s)
...

# Consumer 2
[*] Consumer 2 (prefetch=10)
[x] Received order: order_0003 $30.00 (took 0.20s)
[x] Received order: order_0004 $40.00 (took 0.25s)
...
[✓] Processed order order_0012 $120.00 (took 0.55s)
[x] Received order: order_0013 $130.00 (took 0.20s)
...

# Consumer 3
[*] Consumer 3 (prefetch=10)
[x] Received order: order_0005 $50.00 (took 0.30s)
[x] Received order: order_0006 $60.00 (took 0.35s)
...
[✓] Processed order order_0014 $140.00 (took 0.45s)
[x] Received order: order_0015 $150.00 (took 0.25s)
...
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Queues tab → Click on "orders"
3. See message rate
4. Go to Channels tab → See 3 consumers
5. Monitor unacked message count (should be 30 = 3 consumers × 10 prefetch)
6. See fair distribution (each consumer ~333 messages over time)

### Best Practices

**Prefetch Configuration:**
✅ Always set prefetch for production consumers  
✅ Set prefetch based on processing time  
✅ Use lower prefetch for long-running tasks  
✅ Use higher prefetch for fast tasks  
✅ Monitor unacked message count  
✅ Adjust prefetch based on memory constraints  
✅ Test different prefetch values for optimal performance  

**Fair Dispatch:**
✅ Use same prefetch count across similar consumers  
✅ Use manual_ack with prefetch (required)  
✅ Monitor consumer processing rates  
✅ Ensure consumers have similar processing speeds  
✅ Use round-robin distribution (RabbitMQ default)  
✅ Avoid varying prefetch counts across similar consumers  

**Resource Management:**
✅ Estimate message size × prefetch count = memory usage  
✅ Ensure total prefetch fits in available RAM  
✅ Monitor consumer memory usage  
✅ Set prefetch to prevent OOM  
✅ Leave headroom for OS and other processes  
✅ Test with maximum expected message rate  

### Common Mistakes

❌ Not setting prefetch → Memory overload, unfair distribution  
❌ Setting prefetch too high → Consumer OOM crash  
❌ Setting prefetch too low → Consumer idle (waiting for messages)  
❌ Using auto_ack with prefetch → Unacked messages lost  
❌ Different prefetch for similar consumers → Unfair distribution  
❌ Forgetting to estimate memory usage → OOM risk  
❌ Not monitoring unacked messages → Hidden issues  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Resource Hogging (The Overwhelmed Consumer)**

You're building a file processing system:

- Producer sends 1000 file processing messages/second
- 3 consumers process files
- File processing takes 1-10 seconds (variable)
- System has 16GB RAM (each file is 1GB)

Current implementation:
- Producer publishes messages rapidly
- No prefetch set (unlimited)
- One fast consumer receives all messages
- Fast consumer runs out of memory (OOM crash)
- Slow consumers sit idle

**Problems:**
- Fast consumer OOM crash with 1000 messages (1GB RAM each = 1000GB needed)
- System destabilized (consumer crash)
- Unacked messages requeued (processing duplication)
- Slow consumers get no work (unfair)
- System appears broken (fast consumer crash loop)
- **Impact:** Service outage, data duplication, wasted resources, poor customer experience

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  --memory=8g \
  rabbitmq:3-management
```

**Step 2: Create producer without prefetch**

Create `no_prefetch_producer.py`:

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: No prefetch (unlimited)
channel.queue_declare(queue='files')

# Send 1000 files
for i in range(1000):
    file_data = {
        "file_id": f"file_{i+1:04d}",
        "size_bytes": 1024 * 1024,  # 1GB
        "timestamp": "2024-01-26T17:00:00Z"
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='files',
        body=json.dumps(file_data)
    )
    
    # Progress indicator
    if (i+1) % 200 == 0:
        print(f"[x] Sent {i+1} files...")

print(f"[✓] Sent 1000 files (PROBLEM: No prefetch - memory risk)")
connection.close()
```

**Step 3: Create consumer without prefetch**

Create `no_prefetch_consumer.py`:

```python
import pika
import json

def process_file(file_data):
    """Process file (simulates 1-10 seconds)"""
    file = json.loads(file_data)
    
    # Simulate variable processing time (1-10 seconds)
    import time
    processing_time = 1 + (int(file['file_id'][-3]) / 100)
    
    # Process file
    time.sleep(processing_time)
    
    print(f"[✓] Processed {file['file_id']} ({file['size_bytes']/1024/1024:.2f}GB) (took {processing_time}s)")
    return True

def callback(ch, method, properties, body):
    """Process file"""
    try:
        # Process file
        process_file(body)
        
        # PROBLEM: No prefetch (unlimited unacked)
        # Consumer gets ALL messages at once
        print(f"[!] Unacked: {ch.connection._channel_unacked_messages} messages")
        
        # Acknowledge after processing
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    except Exception as e:
        print(f"[!] ERROR: {e}")
        # PROBLEM: If no ACK, message requeued (duplication)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: No prefetch limit
# Consumer gets ALL messages at once (1000 messages = 1000GB RAM!)
channel.queue_declare(queue='files')

# PROBLEM: Auto-ack (not recommended, but for demo)
# Manual ack would be better
channel.basic_consume(queue='files', on_message_callback=callback)

print('[*] Consumer (NO PREFETCH - unlimited unacked)')
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal 1: Producer
python3 no_prefetch_producer.py

# Terminal 2: Consumer (watch for OOM)
python3 no_prefetch_consumer.py
```

**Expected observation:**
- Producer sends 1000 files
- Consumer receives all 1000 at once
- Consumer memory usage: 1000GB (1000 files × 1GB)
- Consumer RAM: 8GB (container limit)
- Consumer OOM crash (out of memory)
- Container killed
- **Impact:** Service outage, system destabilized, wasted resources

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Queues tab → See 1000 messages (unprocessed after crash)
- Go to Channels tab → See consumer crashed
- No visibility into memory usage before crash

### ✅ Solution & Explanation

**Solution: Implement Prefetch for Memory Bounding and Fair Dispatch**

**Create producer (same as before) (fast_producer.py):**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='files')

# SOLUTION: Producer unchanged (still sends rapidly)
for i in range(1000):
    file_data = {
        "file_id": f"file_{i+1:04d}",
        "size_bytes": 1024 * 1024,
        "timestamp": "2024-01-26T17:00:00Z"
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='files',
        body=json.dumps(file_data)
    )
    
    if (i+1) % 200 == 0:
        print(f"[x] Sent {i+1} files...")

print(f"[✓] Sent 1000 files (SOLUTION: Producer same)")
connection.close()
```

**Create consumers with prefetch (prefetch_consumer1.py, prefetch_consumer2.py, prefetch_consumer3.py):**

Create `prefetch_consumer1.py`:

```python
import pika
import json

def process_file(file_data):
    """SOLUTION: Process file (1-10 seconds)"""
    file = json.loads(file_data)
    
    import time
    processing_time = 1 + (int(file['file_id'][-3]) / 100
    
    time.sleep(processing_time)
    
    print(f"[✓] Processed {file['file_id']} ({file['size_bytes']/1024/1024:.2f}GB) (took {processing_time}s)")
    return True

def callback(ch, method, properties, body):
    """SOLUTION: Process file with ACK"""
    try:
        # Process file
        process_file(body)
        
        # SOLUTION: Acknowledge after processing
        # SOLUTION: Prefetch limits unacked to 5 (max 5GB RAM)
        print(f"[✓] Unacked messages: {ch.connection._channel_unacked_messages}")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    except Exception as e:
        print(f"[!] ERROR: {e}")

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='files')

# SOLUTION: Set prefetch = 5 (max 5 unacknowledged messages)
# Memory: 5 messages × 1GB = 5GB (within 8GB RAM)
channel.basic_qos(prefetch_count=5)

# SOLUTION: Manual acknowledgment (required with prefetch)
channel.basic_consume(
    queue='files',
    on_message_callback=callback,
    auto_ack=False  # SOLUTION: Manual acknowledgment
)

print('[*] Consumer 1 (prefetch=5 - memory bounded)')
channel.start_consuming()
```

Create `prefetch_consumer2.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    import time
    time.sleep(0.5)  # Simulate processing (fast)
    print(f"[✓] Processed {json.loads(body)['file_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='files')
channel.basic_qos(prefetch_count=5)
channel.basic_consume(queue='files', on_message_callback=callback, auto_ack=False)

print('[*] Consumer 2 (prefetch=5)')
channel.start_consuming()
```

Create `prefetch_consumer3.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    import time
    time.sleep(0.5)  # Simulate processing (fast)
    print(f"[✓] Processed {json.loads(body)['file_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='files')
channel.basic_qos(prefetch_count=5)
channel.basic_consume(queue='files', on_message_callback=callback, auto_ack=False)

print('[*] Consumer 3 (prefetch=5)')
channel.start_consuming()
```

**How to verify:**

```bash
# Clear RabbitMQ
docker stop rabbitmq && docker rm rabbitmq
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  --memory=8g \
  rabbitmq:3-management

# Terminal 1: Consumer 1
python3 prefetch_consumer1.py

# Terminal 2: Consumer 2
python3 prefetch_consumer2.py

# Terminal 3: Consumer 3
python3 prefetch_consumer3.py

# Terminal 4: Producer
python3 fast_producer.py
```

**Expected output:**

```
# Producer
[x] Sent 100 files...
[x] Sent 200 files...
[x] Sent 1000 files in 1.23 seconds

# Consumer 1
[*] Consumer 1 (prefetch=5 - memory bounded)
[x] Received file: file_0001 (1.00GB)
[✓] Processed file_0001 (1.00GB) (took 1s)
[x] Received file: file_0006 (1.00GB)
[✓] Processed file_0006 (1.00GB) (took 6s)
[x] Received file: file_0011 (1.00GB)
[✓] Unacked messages: 5
...
[✓] Processed file_0015 (1.00GB) (took 5s)
[x] Received file: file_0020 (1.00GB)
[✓] Unacked messages: 5

# Consumer 2
[*] Consumer 2 (prefetch=5)
[x] Received file: file_0002 (1.00GB)
[✓] Processed file_0002 (1.00GB) (took 1.5s)
...
[x] Received file: file_0012 (1.00GB)
[✓] Unacked messages: 5

# Consumer 3
[*] Consumer 3 (prefetch=5)
[x] Received file: file_0003 (1.00GB)
[✓] Processed file_0003 (1.00GB) (took 2s)
...
[x] Received file: file_0023 (1.00GB)
[✓] Unacked messages: 5
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Queues tab → See 1000 messages processing
3. Go to Channels tab → See 3 consumers
4. Monitor unacked message count (should be 15 = 3 consumers × 5 prefetch)
5. See fair distribution (each consumer ~333 files over time)
6. Monitor memory usage (should be ~5GB per consumer, well within 8GB RAM)

**Comparison:**

| Design | Memory Usage | Distribution | OOM Risk |
|--------|-------------|--------------|-----------|
| No Prefetch | 1000GB (unbounded) | Unfair (consumer gets all) | Yes (crash) |
| With Prefetch (5) | ~5GB per consumer | Fair (333 each) | No |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Always set prefetch for production consumers  
- Set prefetch based on processing time  
- Estimate memory usage (message_size × prefetch_count)  
- Use lower prefetch for long-running tasks  
- Use higher prefetch for fast tasks  
- Monitor unacked message count  
- Use same prefetch for similar consumers  
- Use manual_ack with prefetch (required)  
- Leave headroom for OS and other processes  

**❌ Don't:**
- Not setting prefetch → Memory overload, unfair distribution  
- Setting prefetch too high → Consumer OOM crash  
- Setting prefetch too low → Consumer idle time  
- Using auto_ack with prefetch → Unacked messages lost  
- Different prefetch for similar consumers → Unfair distribution  
- Not estimating memory usage → OOM risk  
- Ignoring unacked message count → Hidden issues  

### Prefetch Guidelines

```
Memory Calculation:
├─ Message Size (avg): 1MB
├─ Desired Unacked: 10
└─ Memory Needed: 10MB (10 × 1MB)

Processing Time:
├─ Fast tasks (100ms): Prefetch 50-100
├─ Medium tasks (1s): Prefetch 10-20
├─ Long tasks (10s): Prefetch 1-5
└─ Very long tasks (60s): Prefetch 1

System Constraints:
├─ Available RAM: 16GB
├─ Number of Consumers: 4
├─ Headroom (OS + other): 8GB
└─ Max Unacked per Consumer: (16GB - 8GB) / 4 / 1GB = 8
```

### Production Considerations

**Calculating Prefetch:**

```python
# Calculate prefetch based on memory constraints
def calculate_prefetch(message_size_mb, available_ram_gb, num_consumers, headroom_gb=4):
    """Calculate safe prefetch count"""
    # Available RAM per consumer
    ram_per_consumer = (available_ram_gb - headroom_gb) / num_consumers
    
    # Convert to MB
    ram_per_consumer_mb = ram_per_consumer * 1024
    
    # Calculate prefetch (leave headroom for buffers)
    prefetch = int(ram_per_consumer_mb / message_size_mb)
    
    # Reduce prefetch (safety margin)
    prefetch = int(prefetch * 0.8)  # 80% of max
    
    return max(1, prefetch)  # At least 1

# Example: 1MB messages, 16GB RAM, 4 consumers, 4GB headroom
prefetch = calculate_prefetch(message_size_mb=1, available_ram_gb=16, num_consumers=4)
print(f"Calculated prefetch: {prefetch}")
```

**Monitoring Unacked Messages:**

```python
# Monitor unacked message count
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Get channel info
method = channel.queue_declare(queue='orders', passive=True)
unacked = channel.connection._channel_unacked_messages

print(f"Unacked messages: {unacked}")

# Alert if too many unacked
if unacked > 50:
    print("[ALERT] Too many unacked messages - consumer may be stuck!")
    # Send alert to monitoring system

connection.close()
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's consumer prefetch?**

A: Consumer prefetch (QoS) is a limit on how many unacknowledged messages a consumer can receive at once. It prevents memory overload and enables fair distribution across consumers.

**Q2: What happens if you don't set prefetch?**

A: RabbitMQ defaults to unlimited prefetch (no limit). Consumer receives all messages at once, causing memory overload if many messages or large messages. Messages are distributed unfairly (fast consumers get all messages).

**Q3: How do you determine the right prefetch count?**

A: Calculate based on message size, available RAM, number of consumers, and processing time. Formula: (Available RAM - Headroom) / (Message Size × Number of Consumers). Leave safety margin (e.g., 80% of calculated value).

**Q4: What's the relationship between prefetch and fair dispatch?**

A: Prefetch limits unacked messages, enabling fair dispatch. Without prefetch, fast consumers get all messages and slow consumers starve. With prefetch, each consumer gets similar number of messages over time.

**Q5: Can prefetch cause performance issues?**

A: Yes, prefetch too low can cause consumer idle time (waiting for next message after ACK). Prefetch too high can cause memory overload. Need to tune based on processing time and memory constraints.

### Production Pitfalls

**Pitfall 1: Not setting prefetch**
- Problem: Memory overload, unfair distribution
- Detection: OOM crashes, system instability
- Solution: Always set prefetch for production consumers

**Pitfall 2: Setting prefetch too high**
- Problem: Consumer OOM crash
- Detection: Service outages, unacked messages lost
- Solution: Calculate prefetch based on available RAM and message size

**Pitfall 3: Setting prefetch too low**
- Problem: Consumer idle time (waiting for messages)
- Detection: Poor throughput, low resource utilization
- Solution: Increase prefetch (but stay within memory limits)

**Pitfall 4: Different prefetch for similar consumers**
- Problem: Unfair distribution (one consumer gets more messages)
- Detection: Uneven processing rates
- Solution: Use same prefetch for similar consumers

**Pitfall 5: Not monitoring unacked messages**
- Problem: Consumer stuck (not processing)
- Detection: Hidden issues, queue drain
- Solution: Monitor unacked count, alert if high

### Advanced Prefetch Concepts

**Global Prefetch:**

```python
# Set global prefetch for connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)

# All channels from this connection inherit prefetch
channel.basic_qos(prefetch_count=10)  # Global for this channel
```

**Prefetch with Multiple Queues:**

```python
# Different prefetch for different queues
channel.basic_qos(prefetch_count=1, global_qos=True)  # Queue A
channel2.basic_qos(prefetch_count=10, global_qos=True)  # Queue B
channel3.basic_qos(prefetch_count=50, global_qos=True)  # Queue C
```

**Prefetch with Cancel:**

```python
# Cancel prefetch (reset to unlimited)
channel.basic_qos(prefetch_count=0, global_qos=True)
```

---

## 📚 Summary

Consumer Prefetch and Fair Dispatch provide memory bounding and even message distribution across consumers. By setting appropriate prefetch counts and monitoring unacked messages, you prevent OOM crashes and ensure all consumers get fair work distribution.

**Key takeaways:**
- Prefetch limits unacknowledged messages per consumer
- Use prefetch to prevent memory overload
- Set prefetch based on processing time and memory
- Same prefetch for similar consumers (fair dispatch)
- Always use manual_ack with prefetch
- Monitor unacked message count
- Estimate memory usage (message_size × prefetch_count)
- Leave headroom for OS and other processes

**Next steps:**
- Practice with prefetch in your applications
- Learn about message durability and persistence
- Understand transactionality and atomic operations
- Explore clustering and high availability
- Learn about performance tuning

---

**Module 02 - Advanced RabbitMQ Features**  
**Lesson 05 - Complete**