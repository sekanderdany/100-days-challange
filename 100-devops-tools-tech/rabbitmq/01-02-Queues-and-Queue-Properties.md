# 01-02: Queues and Queue Properties

## 1️⃣ What Are Queues

**Queues** are message buffers in RabbitMQ that store messages until consumers are ready to process them. They act as mailboxes where messages wait for pickup, providing storage, isolation, and reliability in the messaging system.

Think of queues like mailboxes at a post office:

- **Queue** = The mailbox where letters wait
- **Message** = The letter placed in the mailbox
- **Consumer** = The person who comes to collect their mail
- **Queue Properties** = Special mailbox rules (priority, size limit, expiration)

**Where queues fit in RabbitMQ architecture:**

```
┌─────────────┐
│  Producer   │
└──────┬──────┘
       │
       │ Publish to exchange
       ▼
┌─────────────────────────┐
│     Exchange           │
│  (Routes messages)    │
└──────┬────────────────┘
       │ Routes to queues
       ├──────────┬───────────┬──────────┐
       ▼          ▼           ▼          ▼
┌──────────┐┌──────────┐┌──────────┐┌──────────┐
│  Queue 1 ││  Queue 2 ││  Queue 3 ││  Queue 4 │
│ (mailbox) ││ (mailbox) ││ (mailbox) ││ (mailbox) │
└─────┬────┘└─────┬────┘└─────┬────┘└─────┬────┘
      │            │            │            │
      │ Messages  │ Messages   │ Messages   │ Messages
      │ wait here │ wait here  │ wait here  │ wait here
      ▼            ▼            ▼            ▼
┌──────────┐┌──────────┐┌──────────┐┌──────────┐
│Consumer 1 ││Consumer 2 ││Consumer 3 ││Consumer 4 │
│ (picks up)││ (picks up)││ (picks up)││ (picks up)│
└──────────┘└──────────┘└──────────┘└──────────┘
```

**Key queue characteristics:**
- **Storage:** Messages wait in queue until consumed
- **FIFO:** First-In-First-Out ordering (by default)
- **Durable:** Can survive RabbitMQ restarts
- **Exclusive:** Only one connection can use queue
- **Auto-delete:** Queue deleted when last consumer disconnects
- **TTL:** Time-to-live for messages and queues

---

## 2️⃣ Problems Solved by Queues

### The Buffering Problem

Without queues (direct synchronous calls):

- Producer must wait for consumer to be ready
- Consumer must be online when producer sends
- No buffering during traffic spikes
- System fails under load

**Real-world failure scenario:**

An image processing service had:

```
Frontend → Direct API Call → Backend Processor
```

- Frontend uploads 100 images/second during peak
- Backend processes 50 images/second
- No buffering - requests timeout or are rejected
- Customers see 503 errors
- **Impact:** 20% of uploads fail during peak hours, $100K in lost revenue

After implementing queues:
- Frontend publishes to queue (non-blocking)
- Queue buffers 100+ images during peaks
- Backend processes at steady 50/second
- Queue drains during off-peak
- **Result:** 0% failures, $100K savings

### The Reliability Problem

Without durable queues:

- Messages lost if RabbitMQ restarts
- No persistence during broker downtime
- Critical data disappears

**Example:**

A payment processing system:
- Payment messages in non-durable queue
- RabbitMQ crashes due to memory issues
- 50 payment messages lost
- Customers double-charged or not charged
- **Impact:** $25K in financial discrepancies, customer trust lost

After implementing durable queues:
- Messages persist to disk
- RabbitMQ restart doesn't lose messages
- Consumers resume processing after restart
- **Result:** Zero message loss

### The Coupling Problem

Without queues as buffer:

- Producer and consumer tightly coupled
- Must be deployed together
- Hard to scale independently
- No isolation between services

**Example:**

```
Order Service → Direct Call → Payment Service
```

- Payment Service down → Order Service fails
- Can't deploy updates independently
- Scaling Payment Service requires scaling Order Service
- No isolation of failures

After implementing queues:
- Order Service publishes to queue (doesn't wait)
- Payment Service processes at own pace
- Can scale services independently
- Order Service unaffected by Payment Service downtime
- **Result:** Independent deployment and scaling

---

## 3️⃣ When You Should Use Queues

### Development vs Production

**Development:**
- Use queues to test message flow
- Great for debugging consumer logic
- Easy to monitor queue depth
- Helps understand buffering behavior

**Production:**
- Absolutely required for reliability
- Essential for handling traffic spikes
- Critical for message persistence
- Necessary for service decoupling

### Queue Usage Scenarios

| Scenario | Queue Type | Example |
|----------|------------|----------|
| **Work buffering** | Durable, multiple consumers | Image processing, email sending |
| **Temporary storage** | Non-durable, auto-delete | WebSocket message relay |
| **Priority processing** | With priority queue | Urgent orders first |
| **Delayed processing** | With message TTL | Retry queues, delayed tasks |
| **Exclusive access** | Exclusive queue | Single consumer per message |

### Required vs Optional

**Required when:**
- Handling asynchronous work
- Need message persistence
- Handling traffic spikes
- Decoupling services
- Implementing retry logic
- Processing tasks with variable duration

**Optional when:**
- Request-response pattern (synchronous)
- Very low latency requirements (< 1ms)
- Simple point-to-point without buffering

### Trade-offs

**Durable Queues:**
✅ Survives RabbitMQ restart  
✅ Messages persisted to disk  
✅ Critical for reliability  
❌ Slower performance (disk I/O)  
❌ More disk space required  

**Non-durable Queues:**
✅ Faster performance (in-memory)  
✅ Less disk usage  
❌ Lost on RabbitMQ restart  
❌ Not suitable for critical data  

**Exclusive Queues:**
✅ Only one consumer  
✅ No competition for messages  
❌ No failover if consumer fails  
❌ Not suitable for load balancing  

**Auto-delete Queues:**
✅ Clean up automatically  
✅ Good for temporary consumers  
❌ Lost if consumer disconnects unexpectedly  
❌ Not suitable for persistent workloads  

---

## 4️⃣ How Queues Work

### Queue Lifecycle

**Queue creation to deletion:**

```
1. Queue Declaration
   │
   ├─ Queue name (or auto-generated)
   ├─ Properties (durable, exclusive, auto_delete)
   └─ Arguments (TTL, max length, etc.)
   │
2. Queue Created
   │
   ├─ Ready to accept messages
   ├─ Consumers can subscribe
   └─ Exchanges can bind to queue
   │
3. Message Reception
   │
   ├─ Exchange routes messages to queue
   ├─ Messages stored in queue buffer
   └─ Queue depth increases
   │
4. Message Consumption
   │
   ├─ Consumer receives message
   ├─ Message removed from queue (after ACK)
   └─ Queue depth decreases
   │
5. Queue Deletion
   │
   ├─ Auto-delete: When last consumer disconnects
   ├─ Manual delete: Via Management UI or rabbitmqctl
   └─ Broker restart: Non-durable queues deleted
```

### Queue Message Ordering

**FIFO (First-In-First-Out):**

```
Queue State:
┌─────────────────────────────────┐
│ [Msg1] [Msg2] [Msg3] [Msg4] │
│  ↑                        ↑      │
│  First                    Last      │
└─────────────────────────────────┘

Consumer receives: Msg1 → Msg2 → Msg3 → Msg4
```

**With multiple consumers:**

```
Queue:
┌──────────────────────────────────┐
│ [Msg1] [Msg2] [Msg3] [Msg4] │
└──────────────────────────────────┘
     │          │
     ▼          ▼
Consumer 1   Consumer 2

Round-robin distribution:
- Msg1 → Consumer 1
- Msg2 → Consumer 2
- Msg3 → Consumer 1
- Msg4 → Consumer 2
```

**Note:** Order is preserved within queue, but not guaranteed across multiple consumers.

### Queue Properties in Detail

**Durable:**

```python
# Durable queue (survives restart)
channel.queue_declare(
    queue='durable-queue',
    durable=True  # Persisted to disk
)

# Non-durable queue (in-memory only)
channel.queue_declare(
    queue='temp-queue',
    durable=False  # Lost on restart
)
```

**Exclusive:**

```python
# Exclusive queue (only one connection)
channel.queue_declare(
    queue='exclusive-queue',
    exclusive=True  # Only this connection can use
)

# Non-exclusive queue (multiple connections)
channel.queue_declare(
    queue='shared-queue',
    exclusive=False  # Multiple connections allowed
)
```

**Auto-delete:**

```python
# Auto-delete queue (deleted when no consumers)
channel.queue_declare(
    queue='auto-delete-queue',
    auto_delete=True  # Deleted when last consumer disconnects
)

# Permanent queue (stays even without consumers)
channel.queue_declare(
    queue='permanent-queue',
    auto_delete=False  # Persists without consumers
)
```

### Queue Arguments

**Message TTL (Time-to-live):**

```python
# Queue-level TTL (all messages expire after 1 hour)
channel.queue_declare(
    queue='with-ttl',
    arguments={'x-message-ttl': 3600000}  # Milliseconds
)
```

**Queue TTL (auto-delete after inactivity):**

```python
# Queue deleted if unused for 10 minutes
channel.queue_declare(
    queue='lazy-queue',
    arguments={'x-expires': 600000}  # Milliseconds
)
```

**Maximum Queue Length:**

```python
# Limit queue to 10,000 messages
channel.queue_declare(
    queue='limited-queue',
    arguments={
        'x-max-length': 10000  # Drop oldest when full
    }
)

# Or limit by bytes
channel.queue_declare(
    queue='limited-queue',
    arguments={
        'x-max-length-bytes': 100000000  # 100MB
    }
)
```

**Overflow Behavior:**

```python
# Drop oldest when full
channel.queue_declare(
    queue='drop-oldest',
    arguments={
        'x-max-length': 10000,
        'x-overflow': 'drop-head'  # Discard oldest
    }
)

# Reject new messages when full
channel.queue_declare(
    queue='reject-new',
    arguments={
        'x-max-length': 10000,
        'x-overflow': 'reject-publish'  # Reject new
    }
)
```

**Dead Letter Exchange (for rejected/failed messages):**

```python
# Define DLX (dead letter exchange)
channel.exchange_declare(exchange='dlx', exchange_type='direct')

# Define DLQ (dead letter queue)
channel.queue_declare(queue='dlq')

# Bind DLX to DLQ
channel.queue_bind(exchange='dlx', queue='dlq', routing_key='dlq')

# Create queue with DLX argument
channel.queue_declare(
    queue='main-queue',
    arguments={
        'x-dead-letter-exchange': 'dlx',  # Failed messages go here
        'x-dead-letter-routing-key': 'dlq'
    }
)
```

**Lazy Queues (move messages to disk):**

```python
# Lazy queue (messages moved to disk until consumed)
channel.queue_declare(
    queue='lazy-queue',
    arguments={'x-queue-mode': 'lazy'}  # Requires plugin
)
```

---

## 5️⃣ Installation / Setup

**Queues are built-in RabbitMQ features.** No installation required - just declare queues properly.

### Prerequisites

- RabbitMQ server running
- AMQP client library installed
- Understanding of queue properties

### Declaring Queues

**Basic Queue:**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare basic queue
channel.queue_declare(queue='my-queue')

print(" [✓] Queue 'my-queue' created")
connection.close()
```

**Durable Queue:**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare durable queue
channel.queue_declare(
    queue='durable-queue',
    durable=True  # Survives restart
)

print(" [✓] Durable queue 'durable-queue' created")
connection.close()
```

**Queue with TTL:**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare queue with message TTL
channel.queue_declare(
    queue='ttl-queue',
    arguments={'x-message-ttl': 60000}  # 60 seconds
)

print(" [✓] Queue 'ttl-queue' created (messages expire in 60s)")
connection.close()
```

**Queue with Dead Letter Exchange:**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Create DLX and DLQ
channel.exchange_declare(exchange='my-dlx', exchange_type='direct')
channel.queue_declare(queue='my-dlq')
channel.queue_bind(exchange='my-dlx', queue='my-dlq', routing_key='my-dlq')

# Create main queue with DLX
channel.queue_declare(
    queue='main-queue',
    arguments={
        'x-dead-letter-exchange': 'my-dlx',
        'x-dead-letter-routing-key': 'my-dlq'
    }
)

print(" [✓] Queue 'main-queue' created with DLX")
connection.close()
```

### Using rabbitmqctl for Queues

```bash
# List all queues
sudo rabbitmqctl list_queues

# List queues with details
sudo rabbitmqctl list_queues name durable auto_delete messages

# Delete a queue
sudo rabbitmqctl delete_queue name=my-queue

# Purge a queue (remove all messages)
sudo rabbitmqctl purge_queue name=my-queue

# Get queue messages
sudo rabbitmqctl list_queues name messages_ready messages_unacked
```

### Version Notes

- **RabbitMQ 3.12+:** All queue features fully supported
- **Lazy queues:** Requires rabbitmq_lazy_queue plugin
- **Quorum queues:** Modern replacement for mirrored queues
- **Classic queues:** Default queue type
- **Stream queues:** New type for very high throughput

---

## 6️⃣ Where Queues Should Be Applied (With Example)

### Queue in Application Code

**Producer publishing to queue:**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare durable queue
channel.queue_declare(
    queue='orders',
    durable=True  # Survives restart
)

# Publish messages to queue
for i in range(10):
    order = {
        "order_id": i + 1,
        "amount": (i + 1) * 10.99,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    channel.basic_publish(
        exchange='',  # Default exchange
        routing_key='orders',  # Queue name
        body=json.dumps(order),
        properties=pika.BasicProperties(
            delivery_mode=2  # Persistent message
        )
    )
    print(f" [x] Sent order {i + 1}")

connection.close()
```

**Consumer consuming from queue:**

```python
import pika
import json

def callback(ch, method, properties, body):
    order = json.loads(body)
    print(f" [x] Processing order {order['order_id']}: ${order['amount']}")
    
    # Process order (simulate processing)
    # ... business logic ...
    
    # Acknowledge message
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare queue
channel.queue_declare(queue='orders', durable=True)

# Fair dispatch
channel.basic_qos(prefetch_count=1)

# Consume messages
channel.basic_consume(queue='orders', on_message_callback=callback)

print(' [*] Waiting for orders...')
channel.start_consuming()
```

### Priority Queue

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Create priority queue
channel.queue_declare(
    queue='priority-queue',
    arguments={
        'x-max-priority': 10  # Priority levels 0-10
    }
)

# Publish high priority message
channel.basic_publish(
    exchange='',
    routing_key='priority-queue',
    body='urgent message',
    properties=pika.BasicProperties(
        priority=10  # Highest priority
    )
)

# Publish normal priority message
channel.basic_publish(
    exchange='',
    routing_key='priority-queue',
    body='normal message',
    properties=pika.BasicProperties(
        priority=5  # Normal priority
    )
)

print(" [✓] Sent messages with different priorities")
connection.close()
```

### Temporary Queue (Auto-delete)

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare temporary queue (auto-delete)
result = channel.queue_declare(
    queue='',  # Empty string = auto-generated name
    exclusive=True,  # Only this connection
    auto_delete=True  # Delete when no consumers
)

temp_queue_name = result.method.queue

print(f" [✓] Temporary queue created: {temp_queue_name}")

# When consumer disconnects, queue is automatically deleted
connection.close()
```

### Using Dead Letter Exchange

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Create DLX and DLQ
channel.exchange_declare(exchange='order-dlx', exchange_type='direct')
channel.queue_declare(queue='failed-orders')
channel.queue_bind(exchange='order-dlx', queue='failed-orders', routing_key='failed-orders')

# Create main queue with DLX
channel.queue_declare(
    queue='orders',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'order-dlx',
        'x-dead-letter-routing-key': 'failed-orders'
    }
)

# Publish a message
channel.basic_publish(
    exchange='',
    routing_key='orders',
    body='{"order_id": 123}'
)

print(" [x] Published message (will expire in 5 seconds)")

# Message expires and goes to DLX/DLQ
time.sleep(6)

# Check DLQ
method_frame, _, body = channel.basic_get(queue='failed-orders')
if method_frame:
    print(f" [✓] Found failed message in DLQ: {body.decode()}")
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

connection.close()
```

### Best Practices

**Queue Design:**
✅ Use descriptive queue names  
✅ Make queues durable for critical data  
✅ Set appropriate TTLs  
✅ Monitor queue depth  
✅ Use DLX for failed messages  

**Queue Properties:**
✅ durable=True for production queues  
✅ auto_delete=False for persistent workloads  
✅ exclusive=False for multiple consumers  
✅ Set max length to prevent memory issues  

**Queue Arguments:**
✅ Use message TTL for temporary data  
✅ Use queue TTL for cleanup  
✅ Set max-length to prevent unbounded growth  
✅ Use DLX for failed/rejected messages  
✅ Consider lazy queues for large messages  

### Common Mistakes

❌ Not making queues durable → Messages lost on restart  
❌ Not setting queue limits → Memory exhaustion  
❌ Forgetting DLX → Failed messages disappear  
❌ Using exclusive for work queues → No load balancing  
❌ Not monitoring queue depth → Silent failures  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Queue Exhaustion (The Memory Crisis)**

You're building a data ingestion system:
- Producer receives webhooks from external services
- Messages published to queue for processing
- Consumer processes messages asynchronously

Current implementation:
- Single queue, no limits
- Producer floods queue with 1M messages/second
- Consumer processes 10K messages/second

**Problems:**
- Queue grows without bound
- RabbitMQ runs out of memory
- RabbitMQ crashes or stops accepting messages
- Complete system outage
- Data loss during crash

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

**Step 2: Create unbounded producer**

Create `unbounded_producer.py`:

```python
import pika
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: Queue without limits
channel.queue_declare(queue='unbounded-queue')

print(" [*] Starting producer (will flood queue)...")

try:
    message_counter = 0
    while True:
        # Rapid message production
        channel.basic_publish(
            exchange='',
            routing_key='unbounded-queue',
            body=f'Message {message_counter}'
        )
        message_counter += 1
        
        if message_counter % 10000 == 0:
            print(f" [x] Sent {message_counter} messages")
        
        # No delay - as fast as possible
except Exception as e:
    print(f" [ERROR] Producer failed: {e}")
finally:
    connection.close()
```

**Step 3: Create slow consumer**

Create `slow_consumer.py`:

```python
import pika

def callback(ch, method, properties, body):
    # Simulate slow processing
    print(f" [x] Processing: {body.decode()}")
    time.sleep(0.01)  # 10ms per message
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='unbounded-queue')

# Limit prefetch
channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue='unbounded-queue', on_message_callback=callback)

print(' [*] Slow consumer waiting (10ms per message)')
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal 1: Start slow consumer
python3 slow_consumer.py

# Terminal 2: Start producer
python3 unbounded_producer.py

# Terminal 3: Monitor with Management UI
# Open: http://localhost:15672
```

**Expected observation:**
- Producer sends messages rapidly
- Queue depth grows continuously
- Memory usage increases in RabbitMQ
- Eventually RabbitMQ crashes or stops accepting messages
- Complete system failure

**Step 5: Check queue state in Management UI**

Open http://localhost:15672:
- Go to Queues tab
- Watch "unbounded-queue" depth grow
- Monitor memory usage in Overview tab
- Observe RabbitMQ degradation

### ✅ Solution & Explanation

**Solution: Implement Queue Limits and Overflow Handling**

**Create bounded producer (bounded_producer.py):**

```python
import pika
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# FIX: Queue with max length
channel.queue_declare(
    queue='bounded-queue',
    durable=True,
    arguments={
        'x-max-length': 100000,  # Max 100K messages
        'x-overflow': 'drop-head'  # Drop oldest when full
    }
)

print(" [✓] Bounded queue created (max 100K messages)")

try:
    message_counter = 0
    while message_counter < 200000:  # Send 200K messages
        channel.basic_publish(
            exchange='',
            routing_key='bounded-queue',
            body=f'Message {message_counter}'
        )
        message_counter += 1
        
        if message_counter % 10000 == 0:
            print(f" [x] Sent {message_counter} messages")
        
        time.sleep(0.001)  # Small delay
except Exception as e:
    print(f" [ERROR] Producer failed: {e}")
finally:
    connection.close()
    print(f" [✓] Producer finished: {message_counter} messages sent")
```

**Create improved consumer (same as before):**

```python
import pika

def callback(ch, method, properties, body):
    print(f" [x] Processing: {body.decode()}")
    time.sleep(0.01)  # 10ms per message
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='bounded-queue')

channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue='bounded-queue', on_message_callback=callback)

print(' [*] Slow consumer waiting (10ms per message)')
channel.start_consuming()
```

**Create queue with DLX for rejected messages:**

Create `dlx_queue_setup.py`:

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Create DLX and DLQ
channel.exchange_declare(exchange='overflow-dlx', exchange_type='direct')
channel.queue_declare(queue='overflow-dlq', durable=True)
channel.queue_bind(exchange='overflow-dlx', queue='overflow-dlq', routing_key='overflow')

# Create bounded queue with DLX
channel.queue_declare(
    queue='bounded-with-dlx',
    durable=True,
    arguments={
        'x-max-length': 100000,
        'x-dead-letter-exchange': 'overflow-dlx',
        'x-dead-letter-routing-key': 'overflow'
    }
)

print(" [✓] Queue with DLX created")
connection.close()
```

**Script to check DLQ:**

Create `check_dlq.py`:

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Check DLQ
method_frame, _, body = channel.basic_get(queue='overflow-dlq')
if method_frame:
    print(f" [✓] Found overflowed message in DLQ")
    print(f"     Message: {body.decode()}")
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
else:
    print(f" [✓] DLQ is empty (no overflow)")

# Check queue depth
method = channel.queue_declare(queue='bounded-with-dlx', passive=True)
queue_size = method.method.message_count
print(f" [✓] Queue size: {queue_size} messages")

connection.close()
```

**How to verify:**

```bash
# Clear RabbitMQ
docker stop rabbitmq && docker rm rabbitmq
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Terminal 1: Set up DLX
python3 dlx_queue_setup.py

# Terminal 2: Start consumer
python3 slow_consumer.py

# Terminal 3: Start bounded producer
python3 bounded_producer.py

# Terminal 4: Check DLQ after producer finishes
python3 check_dlq.py
```

**Expected output:**

```
# Bounded producer
[x] Sent 10000 messages
[x] Sent 20000 messages
...
[x] Sent 200000 messages
[✓] Producer finished: 200000 messages sent

# Check DLQ
[✓] Found overflowed message in DLQ
     Message: Message 100001
[✓] Queue size: 100000 messages

# Explanation:
# - Producer sent 200K messages
# - Queue limited to 100K messages
# - Oldest 100K messages dropped (overflow to DLQ)
# - Newest 100K messages in queue
# - System remains stable!
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Queues tab
3. See "bounded-with-dlx" queue:
   - Size: ~100K messages (at limit)
   - Not growing unbounded
4. See "overflow-dlq" queue:
   - Contains dropped/overflowed messages
5. Monitor memory usage - stable!

**Comparison:**

| Design | Queue Behavior | System Stability | Message Loss |
|--------|----------------|------------------|---------------|
| Unbounded (old) | Grows indefinitely | Crashes | 100K+ lost |
| Bounded (new) | Capped at 100K | Stable | Controlled (100K oldest) |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Set queue limits (max-length, max-bytes)
- Use durable queues for critical data
- Implement DLX for failed messages
- Monitor queue depth continuously
- Set appropriate TTLs
- Use fair dispatch (prefetch_count)
- Scale consumers to match production rates
- Clean up temporary queues
- Test queue overflow handling

**❌ Don't:**
- Create unbounded queues
- Forget to make queues durable
- Ignore queue depth warnings
- Use auto_delete for persistent workloads
- Skip monitoring queue metrics
- Forget to set message TTL
- Use exclusive for work queues
- Ignore memory/disk usage
- Let queues grow without limit

### Queue Sizing Guidelines

**Queue depth monitoring:**

```python
# Check queue size
method = channel.queue_declare(queue='my-queue', passive=True)
queue_size = method.method.message_count

# Alert if too large
if queue_size > 10000:
    print(f" [ALERT] Queue too large: {queue_size}")
    # Scale up consumers or take action
```

**Recommended queue limits:**

```
Work Queue:      x-max-length: 10000
Event Stream:    x-max-length: 100000
Retry Queue:    x-max-length: 1000 (with TTL)
DLQ:            x-max-length: 50000 (longer retention)
```

### Production Considerations

**Quorum Queues (Modern approach):**

```python
# Quorum queue (recommended for production)
channel.queue_declare(
    queue='quorum-queue',
    durable=True,
    arguments={'x-queue-type': 'quorum'}
)

# Benefits:
# - High availability
# - Data replication
# - Better than mirrored queues
# - Consensus-based
```

**Stream Queues (Very high throughput):**

```python
# Stream queue (for massive throughput)
channel.queue_declare(
    queue='stream-queue',
    durable=True,
    arguments={'x-queue-type': 'stream'}
)

# Benefits:
# - Very high throughput
# - No message loss
# - Supports filtering and replay
```

**Lazy Queues (Large messages):**

```python
# Lazy queue (move to disk)
channel.queue_declare(
    queue='lazy-queue',
    arguments={'x-queue-mode': 'lazy'}
)

# Benefits:
# - Reduces memory usage
# - Moves messages to disk
# - Good for large messages or many queues
```

### Monitoring Queue Health

**Key metrics to monitor:**

```bash
# Queue depth
rabbitmqctl list_queues name messages messages_ready messages_unacked

# Message rates
rabbitmqctl list_queues name message_stats

# Disk usage
rabbitmqctl list_queues name messages_disk_reads writes
```

**Grafana dashboard queries:**

```
rabbitmq_queue_messages{queue="orders"}
rabbitmq_queue_messages_ready{queue="orders"}
rabbitmq_queue_messages_unacked{queue="orders"}
rate(rabbitmq_queue_messages_published_total{queue="orders"}[5m])
rate(rabbitmq_queue_messages_delivered_total{queue="orders"}[5m])
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's the difference between durable and persistent messages?**

A: Durable queue means the queue itself survives RabbitMQ restart. Persistent message (delivery_mode=2) means the message is saved to disk. Both needed for guaranteed message persistence. Durable queue + persistent message = survives restart.

**Q2: When should you use exclusive queues?**

A: Use exclusive queues when only one consumer should access the queue. Example: Temporary reply-to queue for RPC pattern. Not suitable for work queues (can't load balance).

**Q3: What happens when a queue reaches x-max-length?**

A: Depends on x-overflow setting. Default is 'drop-head' (oldest messages dropped). Can set 'reject-publish' (reject new messages) or 'drop-head' (drop oldest). Overflowed messages can go to DLX if configured.

**Q4: What's a dead letter exchange (DLX)?**

A: DLX is an exchange where rejected/failed/expired messages are routed. Messages go to DLX when they're rejected (basic_reject/nack with requeue=false), TTL expires, or queue overflows. Configure with x-dead-letter-exchange argument.

**Q5: How do lazy queues work?**

A: Lazy queues move messages to disk as soon as they're queued, instead of keeping in memory. Messages are loaded into memory only when consumer is about to receive them. Reduces memory usage but adds disk I/O overhead.

### Production Pitfalls

**Pitfall 1: Unbounded queues**
- Problem: Queue grows without limit, memory exhaustion
- Detection: RabbitMQ crashes, high memory usage
- Solution: Always set x-max-length or x-max-length-bytes

**Pitfall 2: Non-durable queues for critical data**
- Problem: Messages lost on RabbitMQ restart
- Detection: Data loss after restart
- Solution: Use durable=True for critical queues

**Pitfall 3: No DLX for failed messages**
- Problem: Failed/rejected messages disappear
- Detection: Messages disappear, no audit trail
- Solution: Configure x-dead-letter-exchange for all queues

**Pitfall 4: Ignoring queue depth**
- Problem: Queue grows silently, no visibility
- Detection: System failure before detection
- Solution: Monitor queue depth, set up alerts

### Advanced Queue Concepts

**Quorum Queues (Replacement for mirrored queues):**

```python
# Quorum queue with majority
channel.queue_declare(
    queue='quorum-queue',
    durable=True,
    arguments={
        'x-queue-type': 'quorum',
        'x-quorum-initial-group-size': 3  # 3 replicas
    }
)

# Advantages over mirrored queues:
# - No split-brain
# - Consistent state
# - Better performance
```

**Consistent Hash Exchange (Sticky routing):**

```python
# Consistent hash exchange (plugin required)
channel.exchange_declare(
    exchange='consistent-hash',
    exchange_type='x-consistent-hash'
)

# Same routing key always routes to same queue
# Good for stateful consumers or grouping
```

**TTL Per Message (Priority to Queue TTL):**

```python
# Message-level TTL overrides queue TTL
channel.basic_publish(
    exchange='',
    routing_key='queue',
    body='message',
    properties=pika.BasicProperties(
        expiration='30000'  # 30 seconds TTL for this message
    )
)
```

---

## 📚 Summary

Queues are the storage and buffering layer in RabbitMQ, holding messages until consumers are ready to process them. Understanding queue properties (durable, exclusive, auto-delete) and arguments (TTL, max-length, DLX) is essential for building reliable, scalable messaging systems.

**Key takeaways:**
- Queues buffer messages between producer and consumer
- Durable queues survive RabbitMQ restarts
- Set queue limits to prevent unbounded growth
- Use DLX to handle failed/rejected messages
- Monitor queue depth continuously in production
- Choose appropriate queue type (classic, quorum, stream)

**Next steps:**
- Practice creating queues with different properties
- Learn about bindings and routing keys
- Understand virtual hosts for isolation
- Explore queue monitoring and alerting
- Learn about quorum queues vs classic queues

---

**Module 01 - Core Concepts**  
**Lesson 02 - Complete**