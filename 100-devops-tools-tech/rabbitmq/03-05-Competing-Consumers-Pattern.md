# 03-05: Competing Consumers Pattern

## 1️⃣ What Are Competing Consumers

**Competing Consumers** is a messaging pattern where multiple consumers compete for messages from the same queue, enabling parallel processing and load balancing. RabbitMQ distributes messages among consumers using round-robin or fair dispatch.

Think of competing consumers like a restaurant with multiple servers:

- **Messages** = Restaurant orders
- **RabbitMQ** = Kitchen order queue (holds orders)
- **Consumers** = Servers (pick up orders to prepare)
- **Fair Dispatch** = Orders distributed evenly among servers
- **Prefetch** = Limits unacknowledged orders per server

**Where competing consumers fit in RabbitMQ architecture:**

```
┌─────────────┐
│  Producer   │
└──────┬──────┘
       │
       │ Publishes messages (orders)
       ▼
┌─────────────────────────────────────────────┐
│          Work Queue                     │
│  (Buffer: 1000 orders)                │
│  (Each order picked by available server)     │
│                                      │
│  ┌────────────────────────────────────┐    │
│  │ Order 1 (being processed by     │    │
│  │   Server A)                    │    │
│  ├────────────────────────────────────┤    │
│  │ Order 2 (waiting for server)      │    │
│  ├────────────────────────────────────┤    │
│  │ Order 3 (waiting for server)      │    │
│  ├────────────────────────────────────┤    │
│  │ Order N (waiting for server)      │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
       │
       ├──────────────────┬──────────────────┬──────────────────┐
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│  Server A    ││  Server B    ││  Server C    ││  Server D    │
│ (Consumer)   ││ (Consumer)   ││ (Consumer)   ││ (Consumer)   │
│  Picks up     ││  Picks up     ││  Picks up     ││  Picks up     │
│  one order     ││  one order     ││  one order     ││  one order     │
│  at a time     ││  at a time     ││  at a time     ││  at a time     │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘
```

**Key concepts:**
- **Work Queue:** Queue containing messages to be processed
- **Consumers/Servers:** Consumers that pick up and process messages
- **Competing Consumers:** Multiple consumers competing for same queue
- **Fair Dispatch:** Messages distributed evenly among available consumers
- **Load Balancing:** Messages distributed across multiple consumers
- **Prefetch:** Limits unacknowledged messages per consumer

---

## 2️⃣ Problems Solved by Competing Consumers

### The "Single Consumer Bottleneck" Problem

Without competing consumers:

- Single consumer processes all messages
- Consumer becomes overwhelmed with high volume
- System unresponsive (consumer stuck processing)
- No parallel processing capability

**Real-world failure scenario:**

A data processing system had:

```
Producer → Queue → 1 Consumer (Server)
                    │
                    └─ Single Server (fast, but serial)

Producer publishes: 1000 data processing tasks

Without Competing Consumers:
├─ Single consumer receives 1000 tasks
├─ Single consumer processes tasks serially
├─ Each task takes 5 seconds
└─ Total processing time: 5000 seconds (83 minutes)

PROBLEMS:
├─ Serial processing (no parallelism)
├─ Consumer overwhelmed (1000 tasks to process)
├─ System appears unresponsive (single consumer stuck)
├─ No load balancing (single bottleneck)
└─ Processing time: 83 minutes
```

**Problems:**
- Serial processing (no parallelism)
- Consumer bottleneck (single point of failure)
- System unresponsive (consumer stuck)
- No load balancing (single server)
- Long processing times (83 minutes for 1000 tasks)
- **Impact:** Poor throughput, poor user experience, system instability

After implementing competing consumers:
- 4 consumers receive 250 tasks each (load balancing)
- Consumers process tasks in parallel
- No single bottleneck (failure of one consumer doesn't stop all)
- Processing time: 1250 seconds (21 minutes) - 4x improvement
- **Result:** Parallel processing, high throughput, good user experience

### The "No Fault Tolerance" Problem

Without competing consumers:

- Single consumer processes all messages
- If consumer fails, all messages lost/stuck
- No resilience (single point of failure)
- System downtime (consumer crash = no processing)

**Example:**

```
Producer → Queue → 1 Consumer
                    │
                    └─ Consumer processes 100 tasks

CRASH: Consumer crashes at task 50

Without Competing Consumers:
├─ Task 51-100: Stuck (consumer crashed)
├─ Tasks: Not processed (consumer not available)
├─ System: No processing until consumer restarts
└─ Recovery: Manual intervention required

PROBLEMS:
├─ No fault tolerance (single point of failure)
├─ Messages stuck (consumer crash)
├─ System downtime (no processing until restart)
├─ Manual recovery required
└─ **Impact:** Downtime, manual intervention, data loss
```

**Problems:**
- No fault tolerance (single point of failure)
- Messages stuck on consumer failure
- System downtime (no processing)
- Manual recovery required
- **Impact:** Downtime, manual intervention, poor reliability

After implementing competing consumers:
- 4 consumers process 25 tasks each (load balancing)
- If consumer 1 fails, consumers 2-4 process remaining 75 tasks
- Fault tolerance (consumer failure = messages rerouted)
- No system downtime (other consumers take over)
- **Result:** High reliability, no downtime, automatic failover

---

## 3️⃣ When You Should Use Competing Consumers

### Development vs Production

**Development:**
- Can use single consumer for quick tests
- Don't need competing consumers for simple tasks
- Use single consumer for low volume (few tasks)
- Don't use in production code

**Production:**
- Absolutely required for parallel processing
- Essential for fault tolerance (single consumer failure)
- Critical for high-throughput systems (thousands of messages)
- Required for load balancing (multiple consumers)
- Necessary for long-running tasks (seconds to hours)

### Competing Consumers Scenarios

| Scenario | Competing Consumers Strategy | Example |
|----------|----------------------------|----------|
| **Data processing** | Multiple consumers, prefetch=1 | File processing, ETL, data transformation |
| **API call handling** | Multiple consumers, prefetch=10 | Third-party API calls, webhooks |
| **Image processing** | Multiple consumers, prefetch=1 | Video encoding, image resizing |
| **Database operations** | Multiple consumers, prefetch=5 | Bulk inserts, batch updates |
| **Email sending** | Multiple consumers, prefetch=50 | Bulk email, newsletter delivery |

### Required vs Optional

**Required when:**
- Parallel processing required (high throughput)
- Fault tolerance needed (single consumer failure)
- Long-running tasks (seconds to hours)
- High-volume systems (thousands of messages)
- CPU-intensive or memory-intensive processing
- Resilience required (consumer crash = messages rerouted)

**Optional when:**
- Single consumer is sufficient (low volume, fast tasks)
- Fire-and-forget messages (notifications, telemetry)
- Development and testing environments
- Low-volume systems (few messages)
- Very short tasks (microseconds) - single consumer is faster

### Trade-offs

**Competing Consumers:**
✅ Parallel processing (multiple consumers)  
✅ Fault tolerance (consumer failure = messages rerouted)  
✅ Load balancing (messages distributed across consumers)  
✅ High throughput (parallel processing)  
✅ Resilient (no single point of failure)  
✅ Fair dispatch (RabbitMQ distributes evenly)  
❌ More complex setup (multiple consumers)  
❌ More resource usage (multiple consumer instances)  
❌ Requires prefetch configuration  
❌ Requires consumer management  
❌ Requires message ordering guarantees (RabbitMQ doesn't guarantee order across consumers)  

**Single Consumer:**
✅ Simpler setup (one consumer)  
✅ Lower resource usage (single consumer instance)  
✅ Message order guaranteed (serial processing)  
❌ No parallelism (serial processing only)  
❌ Single point of failure (consumer crash = no processing)  
❌ Low throughput (no parallelism)  
❌ System unresponsive (consumer overwhelmed)  
❌ No load balancing (single bottleneck)  
❌ No fault tolerance (single consumer failure = downtime)  

---

## 4️⃣ How Competing Consumers Work

### Competing Consumers Configuration Process

**Setting up competing consumers:**

```
1. Producer Creates Work Queue
   │
   ├─ Declares work queue
   ├─ Sets durable=true (for task survival)
   └─ Ready to publish tasks
   │
2. Producers Publish Tasks to Work Queue
   │
   ├─ Task 1: "Process file 1"
   ├─ Task 2: "Process file 2"
   ├─ Task 3: "Process file 3"
   └─ Task N: "Process file N"
   │
3. Consumers Connect to Work Queue
   │
   ├─ Consumer 1 connects, sets prefetch=1
   ├─ Consumer 2 connects, sets prefetch=1
   ├─ Consumer 3 connects, sets prefetch=1
   └─ Consumer N connects, sets prefetch=1
   │
4. RabbitMQ Distributes Tasks
   │
   ├─ RabbitMQ distributes tasks evenly among consumers
   ├─ Consumer 1 receives Task 1 (prefetch=1)
   ├─ Consumer 2 receives Task 2 (prefetch=1)
   ├─ Consumer 3 receives Task 3 (prefetch=1)
   └─ Consumer N receives Task 4 (prefetch=1)
   │
5. Consumers Process Tasks
   │
   ├─ Consumer 1 processes Task 1
   │  ├─ Consumer 1 ACKs Task 1
   │  └─ Consumer 1 receives Task 5 (next available)
   ├─ Consumer 2 processes Task 2
   │  ├─ Consumer 2 ACKs Task 2
   │  └─ Consumer 2 receives Task 6 (next available)
   └─ ... (continues)
```

### Competing Consumers Distribution Mechanism

**Round-robin distribution with prefetch:**

```
Work Queue: tasks (1000 items)

Consumer Connection (Prefetch=1):
├─ Consumer 1 (fast): Receives 1 task, processes, ACKs, gets next
│                    │
│                    ├─ Processes 10 tasks/second
│                    ├─ Completes 1 task in 0.1 seconds
│                    ├─ ACKs task
│                    ├─ Receives next task (prefetch allows it)
│                    └─ Gets 250 tasks (fast consumer)
├─ Consumer 2 (slow): Receives 1 task, processes, ACKs, gets next
│                    │
│                    ├─ Processes 1 task/second
│                    ├─ Completes 1 task in 1 second
│                    ├─ ACKs task (after delay)
│                    ├─ Receives next task (prefetch allows it)
│                    └─ Gets 250 tasks (slow consumer)
└─ Consumers 3 and 4 (fast): Each get 250 tasks

LOAD BALANCING: 1000 tasks / 4 consumers = 250 tasks per consumer
PARALLEL PROCESSING: Consumers 1, 3, 4 finish in 25 seconds
FAULT TOLERANCE: If Consumer 2 fails, Consumers 1, 3, 4 process 750 tasks
```

### Prefetch Mechanism

**How prefetch limits unacknowledged tasks:**

```
Work Queue: tasks (ready for processing)
        ↓
        ↓
        ↓
Consumer (prefetch=1):
├─ Consumer 1 (fast): Task 1 (UNACKED) ← Only 1 task at a time
├─ Consumer 2 (slow): Task 2 (UNACKED) ← Only 1 task at a time
└─ Consumer 3 (fast): Task 3 (UNACKED) ← Only 1 task at a time

Consumer 1 processes Task 1:
├─ Completes processing
└─ ACKs Task 1

Consumer 1 Ready for Next Task:
├─ RabbitMQ sends Task 5 (prefetch allows it)
├─ Task 5 (UNACKED) ← Only 1 task at a time
└─ Max Unacked: 1 (prefetch limit reached)

PREFETCH LIMIT: Controls max unacknowledged tasks per consumer
MEMORY: Bounded (max unacked × task_size)
LOAD BALANCING: Fast consumers get more tasks over time
```

---

## 5️⃣ Installation / Setup

**Competing Consumers are built-in RabbitMQ features.** No installation required - just create work queue and multiple consumers.

### Prerequisites

- RabbitMQ server running
- AMQP client library that supports prefetch
- Understanding of competing consumers
- Understanding of prefetch and fair dispatch

### Creating Work Queue

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Create work queue
channel.queue_declare(
    queue='file_tasks',
    durable=True  # CRITICAL: Queue persists
)

print("[✓] Work queue declared")
connection.close()
```

**Using rabbitmqctl:**

```bash
# Create work queue
sudo rabbitmqctl add_queue file_tasks durable=true

# Delete work queue (cleanup)
sudo rabbitmqctl delete_queue name=file_tasks
```

### Configuring Competing Consumers

**Consumer (competing_consumer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    """Process task with ACK"""
    task = json.loads(body)
    
    # Simulate variable processing time (1-10 seconds)
    import time
    processing_time = 1 + (int(task['task_id'][-3:]) % 10)
    
    # Simulate file processing
    time.sleep(processing_time)
    
    print(f"[✓] Processed task {task['task_id']} (took {processing_time}s)")
    
    # CRITICAL: Acknowledge after processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Consume from work queue
channel.queue_declare(queue='file_tasks', durable=True)

# CRITICAL: Set prefetch (max unacknowledged tasks per consumer)
channel.basic_qos(prefetch_count=1)

# CRITICAL: Manual acknowledgment (required with prefetch)
channel.basic_consume(
    queue='file_tasks',
    on_message_callback=callback,
    auto_ack=False  # CRITICAL: Manual acknowledgment
)

print('[*] Competing consumer waiting (prefetch=1 - fair dispatch)')
channel.start_consuming()
```

**Multiple Competing Consumers (consumer1.py, consumer2.py, consumer3.py, consumer4.py):**

Create `consumer1.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    task = json.loads(body)
    
    import time
    time.sleep(0.1)  # Fast consumer
    
    print(f"[Consumer 1] Processed task {task['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Consumer 1] Waiting')
channel.start_consuming()
```

Create `consumer2.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    task = json.loads(body)
    
    import time
    time.sleep(2.0)  # Slow consumer
    
    print(f"[Consumer 2] Processed task {task['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Consumer 2] Waiting')
channel.start_consuming()
```

### Version Notes

- **RabbitMQ 3.12+:** All competing consumers features fully supported
- **AMQP 0-9-1+:** Prefetch protocol standard
- **Prefetch Count:** Maximum unacknowledged messages per consumer
- **Fair Dispatch:** Based on consumer speed and availability
- **Competing Consumers:** Multiple consumers competing for same queue
- **Load Balancing:** Messages distributed across multiple consumers

---

## 6️⃣ Where Competing Consumers Should Be Applied (With Example)

### Producer Publishing Tasks

**Scenario:** File processing system with multiple workers

**Producer (task_producer.py):**

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Create work queue
channel.queue_declare(
    queue='file_tasks',
    durable=True
)

# CRITICAL: Publish tasks to work queue
tasks = []
for i in range(1000):
    task = {
        "task_id": f"task_{i+1:04d}",
        "file_path": f"/files/file_{i+1}.pdf",
        "output_path": f"/output/file_{i+1}.txt",
        "status": "pending",
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='file_tasks',
        body=json.dumps(task)
    )
    tasks.append(task)
    print(f"[x] Published task: {task['task_id']}")

print(f"[✓] Published {len(tasks)} tasks to work queue")
connection.close()
```

**Competing Consumers**

**Consumer (consumer1.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    task = json.loads(body)
    
    # Simulate fast processing
    import time
    time.sleep(0.1)  # Fast consumer
    
    print(f"[Consumer 1] Processed task {task['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Consumer 1] Waiting')
channel.start_consuming()
```

**Consumer (consumer2.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    task = json.loads(body)
    
    # Simulate slow processing
    import time
    time.sleep(2.0)  # Slow consumer
    
    print(f"[Consumer 2] Processed task {task['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Consumer 2] Waiting')
channel.start_consuming()
```

**Consumer (consumer3.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    task = json.loads(body)
    
    # Simulate fast processing
    import time
    time.sleep(0.1)  # Fast consumer
    
    print(f"[Consumer 3] Processed task {task['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Consumer 3] Waiting')
channel.start_consuming()
```

**Consumer (consumer4.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    task = json.loads(body)
    
    # Simulate fast processing
    import time
    time.sleep(0.1)  # Fast consumer
    
    print(f"[Consumer 4] Processed task {task['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Consumer 4] Waiting')
channel.start_consuming()
```

**How to test competing consumers:**

```bash
# Terminal 1: Consumer 1 (fast)
python3 consumer1.py

# Terminal 2: Consumer 2 (slow)
python3 consumer2.py

# Terminal 3: Consumer 3 (fast)
python3 consumer3.py

# Terminal 4: Consumer 4 (fast)
python3 consumer4.py

# Terminal 5: Producer
python3 task_producer.py
```

**Expected output:**

```
# Producer
[x] Published task: task_0001
[x] Published task: task_0002
...
[x] Published task: task_1000
[✓] Published 1000 tasks to work queue

# Consumer 1 (fast)
[Consumer 1] Waiting
[x] Processed task task_0001
[x] Processed task task_0005
[x] Processed task task_0009
...
[Consumer 1] Processed 250 tasks

# Consumer 2 (slow)
[Consumer 2] Waiting
[x] Processed task task_0002
[x] Processed task task_0006
[x] Processed task task_0010
...
[Consumer 2] Processed 250 tasks

# Consumer 3 (fast)
[Consumer 3] Waiting
[x] Processed task task_0003
[x] Processed task task_0007
[x] Processed task task_0011
...
[Consumer 3] Processed 250 tasks

# Consumer 4 (fast)
[Consumer 4] Waiting
[x] Processed task task_0004
[x] Processed task task_0008
[x] Processed task task_0012
...
[Consumer 4] Processed 250 tasks
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Queues tab → See "file_tasks" queue
3. Go to Channels tab → See 4 consumers/workers
4. Monitor task distribution (RabbitMQ distributes evenly)
5. See load balancing (250 tasks per consumer)
6. See fault tolerance (if one consumer fails, others take over)

### Best Practices

**Competing Consumers Configuration:**
✅ Use multiple consumers for parallel processing  
✅ Use prefetch on consumers (memory bounding)  
✅ Set prefetch=1 for long-running tasks  
✅ Use higher prefetch for short tasks (5-10)  
✅ Monitor consumer count and health  
✅ Use manual_ack with prefetch (required)  

**Consumer Configuration:**
✅ Set prefetch based on task processing time  
✅ Use prefetch=1 for long tasks (seconds to hours)  
✅ Use prefetch=5-10 for short tasks (milliseconds to seconds)  
✅ Process task completely before ACKing  
✅ Reject on failure (requeue=false)  
✅ Use DLX for failed tasks  
✅ Handle consumer crash gracefully (RabbitMQ reroutes tasks)  

**Load Balancing:**
✅ Tasks distributed based on consumer speed  
✅ Fast consumers get more tasks over time  
✅ Slow consumers get fewer tasks (not overwhelmed)  
✅ Add more consumers to scale processing  
✅ Remove consumers dynamically to scale down  
✅ RabbitMQ handles load balancing automatically  

**Fault Tolerance:**
✅ Consumer crash = messages rerouted to other consumers  
✅ No single point of failure (multiple consumers)  
✅ System continues processing if one consumer fails  
✅ Manual intervention not required for failover  
✅ High resilience (automatic failover)  

### Common Mistakes

❌ Single consumer → No parallelism, bottleneck  
❌ Not using prefetch → Consumer overload  
❌ Setting prefetch too high → Consumer OOM crash  
❌ Forgetting to ACK → Tasks requeued (duplication)  
❌ Not monitoring consumer health → Failover not visible  
❌ Using same prefetch for all task types → Inefficient processing  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Single Consumer Bottleneck (The "Serial Processing" Problem)**

You're building a file processing system:

- Producer publishes file processing tasks
- Single consumer processes all tasks
- Tasks take 1-10 seconds (variable processing time)
- System has 16GB RAM (each task is 10MB)

Current implementation:
- Producer publishes 1000 tasks rapidly
- Single consumer processes tasks serially
- No parallel processing (single consumer)
- No load balancing (single bottleneck)

**Problems:**
- Single consumer processes 1000 tasks serially (no parallelism)
- Consumer overwhelmed (100GB RAM needed = 6x available)
- System appears unresponsive (single consumer stuck)
- Processing time: 5000 seconds (83 minutes)
- No load balancing (single bottleneck)
- **Impact:** Poor throughput, poor user experience, system instability, consumer crash

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

**Step 2: Create producer with single consumer**

Create `single_consumer_producer.py`:

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: Work queue for single consumer
channel.queue_declare(queue='file_tasks', durable=True)

# PROBLEM: Publish 1000 tasks (single consumer bottleneck)
tasks = []
for i in range(1000):
    task = {
        "task_id": f"task_{i+1:04d}",
        "file_path": f"/files/file_{i+1}.pdf",
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='file_tasks',
        body=json.dumps(task)
    )
    tasks.append(task)
    print(f"[x] Published task: {task['task_id']}")

print(f"[✓] Published {len(tasks)} tasks (PROBLEM: Single consumer - serial processing)")
connection.close()
```

**Step 3: Create single consumer**

Create `single_consumer_consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    task = json.loads(body)
    
    # PROBLEM: Process task (1-10 seconds)
    import time
    processing_time = 1 + (int(task['task_id'][-3:]) % 10)
    time.sleep(processing_time)
    
    print(f"[✓] Processed task {task['task_id']} (took {processing_time}s)")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)

# PROBLEM: No prefetch (consumer overload)
channel.basic_consume(queue='file_tasks', on_message_callback=callback)

print("[*] Single consumer (PROBLEM: Serial processing - no parallelism)")
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal: Single consumer
python3 single_consumer_consumer.py

# Terminal: Producer
python3 single_consumer_producer.py
```

**Expected observation:**
- Producer publishes 1000 tasks
- Single consumer receives all 1000 tasks
- Single consumer processes tasks serially
- Processing time: 5000 seconds (83 minutes)
- **Impact:** Poor throughput, poor user experience, system instability

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Queues tab → See "file_tasks" queue
- Go to Channels tab → See 1 consumer (single bottleneck)
- No load balancing (single consumer processes all tasks)

### ✅ Solution & Explanation

**Solution: Implement Competing Consumers**

**Create producer (same as before) (task_producer.py):**

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Create work queue
channel.queue_declare(
    queue='file_tasks',
    durable=True
)

# SOLUTION: Publish 1000 tasks (competing consumers will handle)
tasks = []
for i in range(1000):
    task = {
        "task_id": f"task_{i+1:04d}",
        "file_path": f"/files/file_{i+1}.pdf",
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='file_tasks',
        body=json.dumps(task)
    )
    tasks.append(task)
    print(f"[x] Published task: {task['task_id']}")

print(f"[✓] Published {len(tasks)} tasks (SOLUTION: With competing consumers)")
connection.close()
```

**Create competing consumers (consumer1.py, consumer2.py, consumer3.py, consumer4.py):**

Create `consumer1.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    task = json.loads(body)
    
    # SOLUTION: Simulate fast processing
    import time
    time.sleep(0.1)  # Fast consumer
    
    print(f"[Consumer 1] Processed task {task['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)  # SOLUTION: Prefetch for fair dispatch
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Consumer 1] Waiting (SOLUTION: Prefetch=1 - fair dispatch)')
channel.start_consuming()
```

Create `consumer2.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    task = json.loads(body)
    
    # SOLUTION: Simulate slow processing
    import time
    time.sleep(2.0)  # Slow consumer
    
    print(f"[Consumer 2] Processed task {task['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)  # SOLUTION: Prefetch for fair dispatch
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Consumer 2] Waiting (SOLUTION: Prefetch=1 - fair dispatch)')
channel.start_consuming()
```

Create `consumer3.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    task = json.loads(body)
    
    # SOLUTION: Simulate fast processing
    import time
    time.sleep(0.1)  # Fast consumer
    
    print(f"[Consumer 3] Processed task {task['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)  # SOLUTION: Prefetch for fair dispatch
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Consumer 3] Waiting (SOLUTION: Prefetch=1 - fair dispatch)')
channel.start_consuming()
```

Create `consumer4.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    task = json.loads(body)
    
    # SOLUTION: Simulate fast processing
    import time
    time.sleep(0.1)  # Fast consumer
    
    print(f"[Consumer 4] Processed task {task['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)  # SOLUTION: Prefetch for fair dispatch
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Consumer 4] Waiting (SOLUTION: Prefetch=1 - fair dispatch)')
channel.start_consuming()
```

**How to verify:**

```bash
# Clear RabbitMQ
docker stop rabbitmq && docker rm rabbitmq
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Terminal 1: Consumer 1 (fast)
python3 consumer1.py

# Terminal 2: Consumer 2 (slow)
python3 consumer2.py

# Terminal 3: Consumer 3 (fast)
python3 consumer3.py

# Terminal 4: Consumer 4 (fast)
python3 consumer4.py

# Terminal 5: Producer
python3 task_producer.py
```

**Expected output:**

```
# Producer
[x] Published task: task_0001
[x] Published task: task_0002
...
[x] Published task: task_1000
[✓] Published 1000 tasks (SOLUTION: With competing consumers)

# All 4 Consumers (simultaneously)
[Consumer 1] Waiting (SOLUTION: Prefetch=1 - fair dispatch)
[x] Processed task task_0001
[x] Processed task task_0005
[x] Processed task task_0009
...
[Consumer 1] Processed 250 tasks (fast consumer)

[Consumer 2] Waiting (SOLUTION: Prefetch=1 - fair dispatch)
[x] Processed task task_0002
[x] Processed task task_0006
[x] Processed task task_0010
...
[Consumer 2] Processed 250 tasks (slow consumer)

[Consumer 3] Waiting (SOLUTION: Prefetch=1 - fair dispatch)
[x] Processed task task_0003
[x] Processed task task_0007
[x] Processed task task_0011
...
[Consumer 3] Processed 250 tasks (fast consumer)

[Consumer 4] Waiting (SOLUTION: Prefetch=1 - fair dispatch)
[x] Processed task task_0004
[x] Processed task task_0008
[x] Processed task task_0012
...
[Consumer 4] Processed 250 tasks (fast consumer)
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Queues tab → See "file_tasks" queue
3. Go to Channels tab → See 4 consumers/workers
4. See load balancing (250 tasks per consumer = 1000/4)
5. See fair distribution (fast consumers get more tasks: 250 each)
6. See fault tolerance (if one consumer fails, others take over)

**Comparison:**

| Design | Consumers | Parallelism | Processing Time |
|--------|-----------|-------------|----------------|
| Single Consumer (old) | 1 | No | 5000s (83 min) |
| Competing Consumers (new) | 4 | Yes | 1250s (21 min) |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Always use multiple consumers for parallel processing  
- Use prefetch on consumers (memory bounding)  
- Use prefetch=1 for long-running tasks  
- Use higher prefetch for short tasks (5-10)  
- Process task completely before ACKing  
- Reject on failure (requeue=false)  
- Use DLX for failed tasks  
- Monitor consumer count and health  
- Add/remove consumers dynamically to scale  

**❌ Don't:**
- Single consumer → No parallelism, bottleneck  
- Not using prefetch → Consumer overload  
- Setting prefetch too high → Consumer OOM crash  
- Forgetting to ACK → Tasks requeued (duplication)  
- Not monitoring consumer health → Failover not visible  
- Not scaling consumers → Poor throughput, poor user experience  

### Competing Consumers Guidelines

```
Consumer Count:
├─ Start with 4 consumers
├─ Add consumers if queue depth > 100
└─ Remove consumers if queue depth < 10

Prefetch Settings:
├─ Long tasks (seconds to hours): prefetch=1
├─ Medium tasks (1-10 seconds): prefetch=1-5
├─ Short tasks (100-500ms): prefetch=10-20
└─ Very short tasks (1-100ms): prefetch=50-100

Load Balancing:
├─ Tasks distributed based on consumer speed
├─ Fast consumers get more tasks over time
├─ Slow consumers get fewer tasks (not overwhelmed)
└─ RabbitMQ handles load balancing automatically

Fault Tolerance:
├─ Consumer crash = messages rerouted to other consumers
├─ No single point of failure (multiple consumers)
├─ System continues processing if one consumer fails
└─ Manual intervention not required for failover
```

### Production Considerations

**Scaling Consumers Dynamically:**

```bash
# Add consumer dynamically
docker run -d --name worker5 \
  -e WORKER_ID=5 \
  -p 5672:5672:15672 \
  rabbitmq:3-management \
  your-org/task-worker:latest

# Remove consumer dynamically
docker stop worker5
```

**Monitoring Consumer Performance:**

```python
# Monitor consumer task completion
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Get queue info (depth)
method = channel.queue_declare(queue='file_tasks', passive=True)
queue_depth = method.method.message_count

print(f"Queue depth: {queue_depth}")
print(f"Load Balancing: {'BALANCED' if queue_depth < 100 else 'HIGH'}")

# Alert if queue depth too high
if queue_depth > 500:
    print("[ALERT] Queue depth too high - consider adding more consumers")
    # Send alert to monitoring system

connection.close()
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's competing consumers?**

A: Competing consumers is a pattern where multiple consumers compete for messages from the same queue. RabbitMQ distributes messages among consumers using round-robin or fair dispatch. Enables parallel processing and load balancing.

**Q2: How does prefetch ensure fair distribution?**

A: Prefetch limits number of unacknowledged messages each consumer can have at once (e.g., prefetch=1 means max 1 unacknowledged). As consumers complete tasks, they ACK and receive next available task. Fast consumers complete tasks faster, so they receive more tasks over time.

**Q3: What's the right number of consumers?**

A: Number of consumers depends on throughput requirements and task processing time:
- Long tasks (seconds to hours): 4-8 consumers
- Medium tasks (1-10 seconds): 8-16 consumers
- Short tasks (100-500ms): 20-50 consumers
- Formula: consumers = floor(throughput / avg_task_time) + buffer

**Q4: What's the performance impact of competing consumers?**

A: Competing consumers enable parallel processing (multiple consumers process tasks simultaneously). Improves throughput significantly (2-4x improvement). No single bottleneck (multiple consumers).

**Q5: How do you scale consumers?**

A: Add more consumers to work queue. RabbitMQ automatically distributes tasks among available consumers. More consumers = faster task processing (horizontal scaling). Remove consumers when queue depth is low to save resources.

### Production Pitfalls

**Pitfall 1: Single consumer bottleneck**
- Problem: No parallelism, single point of failure
- Detection: Poor throughput, slow processing
- Solution: Always use multiple competing consumers

**Pitfall 2: Not using prefetch**
- Problem: Consumer overload (unlimited tasks)
- Detection: OOM crash, service outage
- Solution: Always use prefetch based on task processing time

**Pitfall 3: Setting prefetch too high**
- Problem: Consumer OOM crash
- Detection: Service outages, unacked messages lost
- Solution: Calculate prefetch based on available RAM and task size

**Pitfall 4: Not monitoring consumer count**
- Problem: Poor throughput, no visibility
- Detection: Queue fills with tasks, system stalled
- Solution: Monitor consumer count, alert on high queue depth, scale consumers

**Pitfall 5: Not scaling consumers**
- Problem: Poor throughput, poor user experience
- Detection: Queue depth doesn't decrease, high queue depth
- Solution: Add more consumers to scale processing

### Advanced Competing Consumers Concepts

**Multiple Consumer Groups:**

```python
# Separate work queues for different task types
channel.queue_declare(queue='file_processing_tasks', durable=True)
channel.queue_declare(queue='image_processing_tasks', durable=True)

# Multiple consumers share same queue (load balancing)
channel.basic_consume(queue='file_processing_tasks', on_message_callback=callback1, auto_ack=False)
channel.basic_consume(queue='file_processing_tasks', on_message_callback=callback2, auto_ack=False)

# Single consumer for image processing (no need for multiple)
channel.basic_consume(queue='image_processing_tasks', on_message_callback=callback3, auto_ack=False)
```

**Consumer Priority:**

```python
# Priority work queue (RabbitMQ priority queues)
channel.queue_declare(
    queue='priority_tasks',
    durable=True,
    arguments={
        'x-max-priority': 10  # Priority levels 0-10
    }
)

# Tasks with priority
channel.basic_publish(
    exchange='',
    routing_key='priority_tasks',
    body=task_data,
    properties=pika.BasicProperties(
        priority=5  # Priority 0-10
    )
)
```

---

## 📚 Summary

Competing consumers provide parallel processing and load balancing by distributing messages among multiple consumers. By setting prefetch limits, consumers receive bounded number of tasks, enabling efficient processing of long-running tasks with fair distribution.

**Key takeaways:**
- Multiple consumers for parallel processing
- Prefetch limits unacknowledged tasks per consumer
- Use prefetch=1 for long-running tasks
- Use prefetch=5-10 for short tasks
- Fair distribution (fast consumers get more tasks)
- Load balancing (multiple consumers)
- Fault tolerance (consumer crash = messages rerouted)
- Consumer scaling (add/remove consumers dynamically)

**Next steps:**
- Practice with competing consumers in your applications
- Learn about Request/Reply pattern
- Learn about Architectural patterns (shovel, federation)
- Explore clustering and high availability
- Learn about message ordering and consistency patterns

---

**Module 03 - Message Patterns and Architectures**  
**Lesson 05 - Complete**