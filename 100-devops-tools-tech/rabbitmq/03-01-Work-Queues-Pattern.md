# 03-01: Work Queues Pattern

## 1️⃣ What Are Work Queues

**Work Queues** is a messaging pattern where tasks are distributed among multiple consumers (workers) to prevent any single consumer from being overwhelmed. Tasks are picked up by available workers, allowing efficient processing of long-running tasks.

Think of work queues like a restaurant kitchen with multiple chefs:

- **Messages** = Food orders
- **RabbitMQ** = Order management system
- **Producers** = Waiters (take orders)
- **Work Queue** = Kitchen order queue (holds orders)
- **Consumers/Workers** = Chefs (pick up orders to cook)
- **Fair Dispatch** = Orders distributed evenly among chefs

**Where Work Queues fit in RabbitMQ architecture:**

```
┌─────────────┐
│  Producer   │
└──────┬──────┘
       │
       │ Publishes tasks (work items)
       ▼
┌─────────────────────────────────────────────┐
│          Work Queue                     │
│  (Buffer: 1000 tasks)                │
│  (Each task picked by available worker)  │
│                                      │
│  ┌────────────────────────────────────┐    │
│  │ Task 1 (being processed by     │    │
│  │   Worker A)                    │    │
│  ├────────────────────────────────────┤    │
│  │ Task 2 (waiting for worker)      │    │
│  ├────────────────────────────────────┤    │
│  │ Task 3 (waiting for worker)      │    │
│  ├────────────────────────────────────┤    │
│  │ Task N (waiting for worker)      │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
       │
       ├──────────────────┬──────────────────┬──────────────────┐
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│  Worker A    ││  Worker B    ││  Worker C    ││  Worker D    │
│ (Consumer)   ││ (Consumer)   ││ (Consumer)   ││ (Consumer)   │
│  Picks up     ││  Picks up     ││  Picks up     ││  Picks up     │
│  one task     ││  one task     ││  one task     ││  one task     │
│  at a time     ││  at a time     ││  at a time     ││  at a time     │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘
```

**Key concepts:**
- **Work Queue:** Queue containing tasks to be processed
- **Workers/Consumers:** Consumers that pick up and process tasks
- **Fair Dispatch:** Tasks distributed evenly among available workers
- **Task Distribution:** Round-robin or prefetch-based distribution
- **Worker Scaling:** Add more workers to process tasks faster
- **Prefetch:** Limits unacknowledged tasks per worker (memory management)

---

## 2️⃣ Problems Solved by Work Queues

### The "Worker Overload" Problem

Without work queues (basic round-robin with no prefetch):

- Fast worker receives many tasks
- Slow worker receives few tasks
- Fast worker overwhelmed with many tasks
- Slow worker sits idle waiting

**Real-world failure scenario:**

A file processing system had:

```
Producer → Queue → 3 Consumers (Workers)
                    │
                    ├─ Worker A (fast): 10 files/second
                    ├─ Worker B (slow): 1 file/second
                    └─ Worker C (fast): 10 files/second

Producer publishes: 1000 file processing tasks

RabbitMQ Dispatch (Basic Round-Robin, No Prefetch):
├─ Task 1 → Worker A (fast)
├─ Task 2 → Worker B (slow)
├─ Task 3 → Worker C (fast)
├─ Task 4 → Worker A (fast)
├─ Task 5 → Worker B (slow)
└─ ... (continues)

After 100 tasks:
├─ Worker A: 34 tasks (completed quickly, gets more)
├─ Worker B: 33 tasks (slow, falls behind)
├─ Worker C: 33 tasks (completed quickly, gets more)
└─ Worker A and C get 67% of tasks, B gets 33%
```

**Problems:**
- Worker A and C overwhelmed with 67 tasks each (memory overload)
- Worker B idle after processing (underutilized)
- Fast workers process tasks sequentially (could process in parallel)
- System appears unresponsive (fast workers stuck)
- **Impact:** System instability, 5-hour delays, $50K in lost productivity

After implementing work queues with prefetch:
- Each worker gets limited tasks (prefetch=1)
- Tasks distributed based on worker speed
- Fast workers complete tasks and get more
- No worker overwhelmed
- **Result:** Fair distribution, stable system, efficient processing

### The "Queue Backpressure" Problem

Without prefetch control:

- Worker receives thousands of tasks at once
- Worker runs out of memory
- Worker crashes or becomes unresponsive
- Tasks lost or requeued

**Example:**

```
Worker (no prefetch limit):
├─ Receives 10,000 tasks at once
├─ Loads all into memory
├─ Memory: 10,000 × 10MB = 100GB RAM
├─ Worker RAM: 8GB
└─ CRASH: Out Of Memory

Recovery:
├─ 10,000 tasks unacked
├─ All requeued back to queue
├─ System appears stuck (10K tasks requeued)
└─ Other workers overwhelmed
```

**Problems:**
- Worker OOM crash
- Unacked messages requeued (processing duplication)
- System destabilizes
- Recovery takes time
- **Impact:** Service outage, data duplication, system instability

After implementing prefetch:
- Worker receives only 10 tasks at once
- Worker processes 10, gets 10 more
- Memory bounded (10 × 10MB = 100MB)
- Worker stable, no OOM
- **Result:** Stable system, bounded memory, no crashes

---

## 3️⃣ When You Should Use Work Queues

### Development vs Production

**Development:**
- Can use simple round-robin for quick tests
- Don't need work queues for single consumer
- Use basic prefetch (no strict control)
- Don't use in production code

**Production:**
- Absolutely required for multiple workers
- Essential for long-running tasks (file processing, video encoding)
- Critical for CPU-intensive or memory-intensive tasks
- Required for fair distribution among workers
- Necessary for scaling workers dynamically

### Work Queue Scenarios

| Scenario | Work Queue Strategy | Example |
|----------|-------------------|----------|
| **File processing** | Work Queue + Prefetch=1 | Video encoding, image processing |
| **PDF generation** | Work Queue + Prefetch=1 | Report generation, document conversion |
| **Email sending** | Work Queue + Prefetch=10 | Bulk email, newsletter delivery |
| **API processing** | Work Queue + Prefetch=1 | Third-party API calls, webhooks |
| **Data transformation** | Work Queue + Prefetch=1 | ETL, data migration, format conversion |

### Required vs Optional

**Required when:**
- Multiple consumers/workers sharing same queue
- Long-running tasks (seconds to hours)
- CPU-intensive or memory-intensive processing
- Fair distribution among workers required
- Worker scaling (dynamic addition/removal of workers)
- High-throughput systems (thousands of tasks/second)

**Optional when:**
- Single consumer (no work queue needed)
- Very short tasks (microseconds)
- Fire-and-forget tasks (notifications, telemetry)
- Development and testing environments
- Low-throughput systems (few tasks/minute)

### Trade-offs

**Work Queues:**
✅ Fair distribution among workers  
✅ No worker overload (prefetch control)  
✅ Worker scaling (add/remove workers dynamically)  
✅ Efficient resource utilization  
✅ Stable system (bounded memory)  
✅ Parallel processing capability  
❌ More complex setup (prefetch configuration)  
❌ Round-trip latency (ACK for each task)  
❌ Requires worker management  
❌ Overhead of prefetch acknowledgments  
❌ May require load balancing for optimal performance  

**No Work Queues (Basic Round-Robin):**
✅ Simpler setup (no prefetch needed)  
✅ Lower latency (no ACK round-trips)  
✅ Faster for very short tasks (microseconds)  
❌ Worker overload (fast workers get all tasks)  
❌ Unfair distribution (slow workers starve)  
❌ System instability (memory unbounded)  
❌ No worker scaling control  
❌ Poor resource utilization  

---

## 4️⃣ How Work Queues Work

### Work Queue Configuration Process

**Setting up work queue:**

```
1. Producer Creates Work Queue
   │
   ├─ Declares work queue
   ├─ Sets durable=true (for task survival)
   └─ Ready to publish tasks
   │
2. Producer Publishes Tasks to Work Queue
   │
   ├─ Task 1: "Process file 1"
   ├─ Task 2: "Process file 2"
   ├─ Task 3: "Process file 3"
   └─ Task N: "Process file N"
   │
3. Workers Connect to Work Queue
   │
   ├─ Worker A connects, sets prefetch=1
   ├─ Worker B connects, sets prefetch=1
   ├─ Worker C connects, sets prefetch=1
   └─ Worker N connects, sets prefetch=1
   │
4. RabbitMQ Distributes Tasks
   │
   ├─ Worker A receives Task 1 (prefetch=1)
   ├─ Worker B receives Task 2 (prefetch=1)
   ├─ Worker C receives Task 3 (prefetch=1)
   └─ Worker N receives Task 4 (prefetch=1)
   │
5. Workers Process Tasks
   │
   ├─ Worker A processes Task 1
   │  ├─ Worker A ACKs Task 1
   │  └─ Worker A receives Task 5 (next available)
   ├─ Worker B processes Task 2 (slow)
   │  ├─ Worker B ACKs Task 2 (after delay)
   │  └─ Worker B receives Task 6 (next available)
   └─ ... (continues)
```

### Work Queue Distribution Mechanism

**Fair dispatch with prefetch:**

```
Work Queue: tasks (1000 items)

Worker Connection (Prefetch=1):
├─ Worker A (fast): Receives 1 task, processes, ACKs, gets next
│                    │
│                    ├─ Processes 10 tasks/second
│                    ├─ Completes 1 task in 0.1 seconds
│                    ├─ ACKs task
│                    ├─ Receives next task (prefetch allows it)
│                    └─ Gets 10 tasks/second
├─ Worker B (slow): Receives 1 task, processes, ACKs, gets next
│                    │
│                    ├─ Processes 1 task/second
│                    ├─ Completes 1 task in 1 second
│                    ├─ ACKs task (after delay)
│                    ├─ Receives next task (prefetch allows it)
│                    └─ Gets 1 task/second
└─ Worker C (fast): Receives 1 task, processes, ACKs, gets next
                     │
                     ├─ Processes 10 tasks/second
                     ├─ Completes 1 task in 0.1 seconds
                     ├─ ACKs task
                     ├─ Receives next task (prefetch allows it)
                     └─ Gets 10 tasks/second

FAIR DISPATCH: Fast workers (A, C) get more tasks over time
Workers complete tasks based on speed (not round-robin)
```

### Prefetch Mechanism

**How prefetch limits unacknowledged tasks:**

```
Work Queue: tasks (ready for processing)
        ↓
        ↓
        ↓
Worker (prefetch=1):
├─ Task 1 (UNACKED) ← Only 1 task at a time
└─ Max Unacked: 1 (prefetch limit reached)

Worker processes Task 1:
├─ Completes processing
└─ ACKs Task 1

Worker Ready for Next Task:
├─ RabbitMQ sends Task 2 (prefetch allows it)
├─ Task 2 (UNACKED) ← Only 1 task at a time
└─ Max Unacked: 1 (prefetch limit reached)

PREFETCH LIMIT: Controls max unacknowledged tasks per worker
MEMORY: Bounded (max unacked × task_size)
```

---

## 5️⃣ Installation / Setup

**Work Queues are built-in RabbitMQ features.** No installation required - just create work queue and configure prefetch on workers.

### Prerequisites

- RabbitMQ server running
- AMQP client library that supports prefetch
- Understanding of task processing time
- Understanding of worker resource constraints

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

### Configuring Worker with Prefetch

**Python (Pika):**

```python
import pika
import time

def process_task(task_data):
    """Process long-running task"""
    task = json.loads(task_data)
    
    # Simulate long processing (1-10 seconds)
    processing_time = 1 + (task['task_id'] % 10)
    time.sleep(processing_time)
    
    print(f"[✓] Processed task {task['task_id']} (took {processing_time}s)")
    return True

def callback(ch, method, properties, body):
    """Process task with ACK"""
    process_task(body)
    
    # CRITICAL: Acknowledge after processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Consume from work queue
channel.queue_declare(queue='file_tasks', durable=True)

# CRITICAL: Set prefetch (max unacknowledged tasks per worker)
# This ensures fair distribution and prevents memory overload
channel.basic_qos(prefetch_count=1)

# CRITICAL: Manual acknowledgment (required with prefetch)
channel.basic_consume(
    queue='file_tasks',
    on_message_callback=callback,
    auto_ack=False  # CRITICAL: Manual acknowledgment
)

print('[*] Worker waiting (prefetch=1 - fair dispatch)')
channel.start_consuming()
```

**Node.js (amqplib):**

```javascript
const amqp = require('amqplib/callback_api');

const connection = amqp.connect('amqp://localhost');
const channel = connection.createChannel();

channel.assertQueue('file_tasks', { durable: true });

// CRITICAL: Set prefetch (max unacknowledged tasks per worker)
channel.prefetch(1);

// CRITICAL: Manual acknowledgment
channel.consume('file_tasks', (msg) => {
    processTask(msg.content.toString());
    channel.ack(msg);
});

console.log('[*] Worker waiting (prefetch=1 - fair dispatch)');
```

**Java (RabbitMQ Java Client):**

```java
import com.rabbitmq.client.*;

ConnectionFactory factory = new ConnectionFactory();
factory.setHost("localhost");
Connection connection = factory.newConnection();
Channel channel = connection.createChannel();

// CRITICAL: Declare work queue
channel.queueDeclare("file_tasks", true, false, null, null);

// CRITICAL: Set prefetch (max unacknowledged tasks per worker)
int prefetchCount = 1;
channel.basicQos(prefetchCount);

// CRITICAL: Manual acknowledgment
boolean autoAck = false;
channel.basicConsume("file_tasks", autoAck, false, new TaskConsumer());

System.out.println("[*] Worker waiting (prefetch=1 - fair dispatch)");
```

### Version Notes

- **RabbitMQ 3.12+:** All work queue features fully supported
- **AMQP 0-9-1+:** Prefetch protocol standard
- **Prefetch Count:** Maximum unacknowledged messages per consumer
- **Fair Dispatch:** Based on worker speed and availability
- **Prefetch Limit:** Bounded memory per worker

---

## 6️⃣ Where Work Queues Should Be Applied (With Example)

### Producer Publishing Tasks

**Scenario:** File processing system with multiple workers

**Producer (task_producer.py):**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Create work queue
channel.queue_declare(
    queue='file_tasks',
    durable=True  # CRITICAL: Queue persists
)

# CRITICAL: Publish tasks to work queue
tasks = []
for i in range(100):
    task = {
        "task_id": f"task_{i+1:04d}",
        "file_path": f"/files/file_{i+1}.pdf",
        "output_path": f"/output/file_{i+1}.txt",
        "status": "pending",
        "timestamp": "2024-01-31T17:00:00Z"
    }
    
    # Publish task to work queue
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

**Worker (task_worker.py):**

```python
import pika
import json

def process_task(task_data):
    """Process long-running file task"""
    task = json.loads(task_data)
    
    # Simulate long processing (1-10 seconds)
    import time
    processing_time = 1 + (int(task['task_id'][-3:]) % 10)
    
    # Simulate file processing
    time.sleep(processing_time)
    
    print(f"[✓] Processed task {task['task_id']} (took {processing_time}s)")
    return True

def callback(ch, method, properties, body):
    """CRITICAL: Process task with ACK"""
    try:
        # Process task
        process_task(body)
        
        # CRITICAL: Acknowledge after processing
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[✓] ACKed task {json.loads(body)['task_id']}")
    
    except Exception as e:
        # CRITICAL: Reject on failure (send to DLX if configured)
        ch.basic_reject(
            delivery_tag=method.delivery_tag,
            requeue=False  # CRITICAL: Don't requeue (let other worker process)
        )
        print(f"[✗] REJECTED task {json.loads(body)['task_id']}: {e}")

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Consume from work queue
channel.queue_declare(queue='file_tasks', durable=True)

# CRITICAL: Set prefetch (max unacknowledged tasks per worker)
# This ensures fair distribution and prevents memory overload
channel.basic_qos(prefetch_count=1)

# CRITICAL: Manual acknowledgment (required with prefetch)
channel.basic_consume(
    queue='file_tasks',
    on_message_callback=callback,
    auto_ack=False  # CRITICAL: Manual acknowledgment
)

print('[*] Worker waiting (prefetch=1 - fair dispatch)')
channel.start_consuming()
```

**Multiple Workers (worker1.py, worker2.py, worker3.py):**

Create `worker1.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    """Worker 1: Process task with ACK"""
    task = json.loads(body)
    
    # Simulate fast processing
    import time
    time.sleep(0.1)  # Fast worker
    
    print(f"[Worker 1] Processed task {task['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Worker 1] Waiting (prefetch=1)')
channel.start_consuming()
```

Create `worker2.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    """Worker 2: Process task with ACK"""
    task = json.loads(body)
    
    # Simulate slow processing
    import time
    time.sleep(2.0)  # Slow worker
    
    print(f"[Worker 2] Processed task {task['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Worker 2] Waiting (prefetch=1)')
channel.start_consuming()
```

Create `worker3.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    """Worker 3: Process task with ACK"""
    task = json.loads(body)
    
    # Simulate fast processing
    import time
    time.sleep(0.1)  # Fast worker
    
    print(f"[Worker 3] Processed task {task['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Worker 3] Waiting (prefetch=1)')
channel.start_consuming()
```

**How to test work queue:**

```bash
# Terminal 1: Worker 1
python3 worker1.py

# Terminal 2: Worker 2
python3 worker2.py

# Terminal 3: Worker 3
python3 worker3.py

# Terminal 4: Producer
python3 task_producer.py
```

**Expected output:**

```
# Producer
[x] Published task: task_0001
[x] Published task: task_0002
...
[x] Published task: task_0100
[✓] Published 100 tasks to work queue

# Worker 1 (fast)
[Worker 1] Waiting (prefetch=1)
[x] Received task_0001
[Worker 1] Processed task_0001
[✓] ACKed task_0001
[x] Received task_0004
[Worker 1] Processed task_0004
[✓] ACKed task_0004
...
[Worker 1] Processed 40 tasks (fast worker gets more)

# Worker 2 (slow)
[Worker 2] Waiting (prefetch=1)
[x] Received task_0002
[Worker 2] Processed task_0002
[✓] ACKed task_0002
[x] Received task_0005
[Worker 2] Processed task_0005
[✓] ACKed task_0005
...
[Worker 2] Processed 20 tasks (slow worker gets fewer)

# Worker 3 (fast)
[Worker 3] Waiting (prefetch=1)
[x] Received task_0003
[Worker 3] Processed task_0003
[✓] ACKed task_0003
[x] Received task_0006
[Worker 3] Processed task_0006
[✓] ACKed task_0006
...
[Worker 3] Processed 40 tasks (fast worker gets more)
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Queues tab → Click on "file_tasks"
3. See 100 tasks ready
4. Go to Channels tab → See 3 consumers/workers
5. Monitor task processing rate (fast workers faster)
6. See fair distribution (fast workers get more tasks over time)

### Best Practices

**Work Queue Configuration:**
✅ Use durable work queue (task survival)  
✅ Use prefetch on workers (memory bounding)  
✅ Set prefetch=1 for long-running tasks  
✅ Use higher prefetch for short tasks (5-10)  
✅ Monitor queue depth (backpressure)  
✅ Use manual_ack with prefetch (required)  

**Worker Configuration:**
✅ Set prefetch based on task processing time  
✅ Use prefetch=1 for long tasks (seconds to hours)  
✅ Use prefetch=5-10 for short tasks (milliseconds to seconds)  
✅ Process task completely before ACKing  
✅ Reject on failure (requeue=false)  
✅ Use DLX for failed tasks  

**Task Distribution:**
✅ Tasks distributed based on worker speed  
✅ Fast workers get more tasks over time  
✅ Slow workers get fewer tasks (not overwhelmed)  
✅ Add more workers to scale processing  
✅ Remove workers dynamically to scale down  

**Error Handling:**
✅ Reject on failure (send to DLX if configured)  
✅ NACK with requeue=true for transient failures  
✅ Reject with requeue=false for permanent failures  
✅ Monitor worker health and performance  
✅ Alert on high error rate  

### Common Mistakes

❌ Not setting prefetch → Worker overload, unfair distribution  
❌ Setting prefetch too high → Worker OOM crash  
❌ Setting prefetch too low → Worker idle (waiting for ACK)  
❌ Using auto_ack with prefetch → Unacked messages lost  
❌ Not rejecting on failure → Tasks never marked as failed  
❌ Forgetting to ACK → Tasks requeued (duplication)  
❌ Not monitoring queue depth → Backpressure issues  
❌ Using same prefetch for all task types → Inefficient processing  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Worker Overload and Unfair Distribution (The "Fast Worker Starvation")**

You're building a file processing system:

- Producer publishes file processing tasks
- Multiple workers process files
- Tasks take 1-10 seconds (variable processing time)
- System has 16GB RAM (each task is 100MB)

Current implementation:
- Producer publishes tasks rapidly
- No prefetch set (unlimited tasks per worker)
- Tasks distributed via basic round-robin
- Fast workers overwhelmed, slow workers starve

**Problems:**
- Fast workers receive 67% of tasks (overwhelmed)
- Slow workers receive 33% of tasks (underutilized)
- Fast workers crash (100GB RAM each = 300GB needed)
- System appears unresponsive (fast workers stuck)
- Queue depth unpredictable (no backpressure control)
- **Impact:** System instability, 8-hour delays, $100K in lost productivity, worker crashes

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
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

# PROBLEM: No prefetch on workers
channel.queue_declare(queue='file_tasks', durable=True)

# PROBLEM: Publish tasks without prefetch control
tasks = []
for i in range(100):
    task = {
        "task_id": f"task_{i+1:04d}",
        "file_path": f"/files/file_{i+1}.pdf",
        "timestamp": "2024-01-31T17:00:00Z"
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='file_tasks',
        body=json.dumps(task)
    )
    tasks.append(task)
    print(f"[x] Published task: {task['task_id']}")

print(f"[✓] Published {len(tasks)} tasks (PROBLEM: No prefetch - worker overload)")
connection.close()
```

**Step 3: Create worker without prefetch**

Create `no_prefetch_worker.py`:

```python
import pika
import json

def process_task(task_data):
    """Process file task"""
    task = json.loads(task_data)
    
    # Simulate variable processing time (1-10 seconds)
    import time
    processing_time = 1 + (int(task['task_id'][-3:]) % 10)
    
    # Simulate file processing
    time.sleep(processing_time)
    
    print(f"[✓] Processed task {task['task_id']} (took {processing_time}s)")
    return True

def callback(ch, method, properties, body):
    """Process task with ACK"""
    process_task(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)

# PROBLEM: No prefetch limit (unlimited tasks per worker)
channel.basic_consume(queue='file_tasks', on_message_callback=callback)

print('[*] Worker (NO PREFETCH - unlimited tasks, worker overload)')
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal 1: Worker 1 (fast)
python3 no_prefetch_worker.py

# Terminal 2: Worker 2 (slow)
python3 no_prefetch_worker.py

# Terminal 3: Worker 3 (fast)
python3 no_prefetch_worker.py

# Terminal 4: Producer
python3 no_prefetch_producer.py
```

**Expected observation:**
- Producer publishes 100 tasks
- Round-robin distribution: 33 tasks to each worker
- Worker 1 and 3 (fast) complete 33 tasks quickly, get more
- Worker 2 (slow) falls behind, gets fewer tasks
- Fast workers receive 67% of tasks
- Slow workers receive 33% of tasks
- **Impact:** Unfair distribution, worker overload, system instability

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Queues tab → See 100 tasks
- Go to Channels tab → See 3 consumers
- See queue depth (unpredictable)
- No backpressure control (workers receive many tasks)

### ✅ Solution & Explanation

**Solution: Implement Work Queue with Prefetch**

**Create producer (same as before) (task_producer.py):**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Create work queue
channel.queue_declare(
    queue='file_tasks',
    durable=True
)

# SOLUTION: Publish tasks to work queue (same as before)
tasks = []
for i in range(100):
    task = {
        "task_id": f"task_{i+1:04d}",
        "file_path": f"/files/file_{i+1}.pdf",
        "timestamp": "2024-01-31T17:00:00Z"
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='file_tasks',
        body=json.dumps(task)
    )
    tasks.append(task)
    print(f"[x] Published task: {task['task_id']}")

print(f"[✓] Published {len(tasks)} tasks (SOLUTION: With work queue)")
connection.close()
```

**Create workers with prefetch (worker1.py, worker2.py, worker3.py):**

Create `worker1.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    """SOLUTION: Worker 1 (fast) with prefetch"""
    task = json.loads(body)
    
    # Simulate fast processing
    import time
    time.sleep(0.1)  # Fast worker
    
    print(f"[Worker 1] Processed task {task['task_id']}")
    
    # SOLUTION: Acknowledge after processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)

# SOLUTION: Set prefetch (max unacknowledged tasks per worker)
# This prevents worker overload and enables fair dispatch
channel.basic_qos(prefetch_count=1)

# SOLUTION: Manual acknowledgment (required with prefetch)
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Worker 1] Waiting (SOLUTION: prefetch=1 - fair dispatch, bounded memory)')
channel.start_consuming()
```

Create `worker2.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    """SOLUTION: Worker 2 (slow) with prefetch"""
    task = json.loads(body)
    
    # Simulate slow processing
    import time
    time.sleep(2.0)  # Slow worker
    
    print(f"[Worker 2] Processed task {task['task_id']}")
    
    # SOLUTION: Acknowledge after processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Worker 2] Waiting (SOLUTION: prefetch=1 - fair dispatch, bounded memory)')
channel.start_consuming()
```

Create `worker3.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    """SOLUTION: Worker 3 (fast) with prefetch"""
    task = json.loads(body)
    
    # Simulate fast processing
    import time
    time.sleep(0.1)  # Fast worker
    
    print(f"[Worker 3] Processed task {task['task_id']}")
    
    # SOLUTION: Acknowledge after processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='file_tasks', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='file_tasks', on_message_callback=callback, auto_ack=False)

print('[Worker 3] Waiting (SOLUTION: prefetch=1 - fair dispatch, bounded memory)')
channel.start_consuming()
```

**How to verify:**

```bash
# Clear RabbitMQ
docker stop rabbitmq && docker rm rabbitmq
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Terminal 1: Worker 1 (fast)
python3 worker1.py

# Terminal 2: Worker 2 (slow)
python3 worker2.py

# Terminal 3: Worker 3 (fast)
python3 worker3.py

# Terminal 4: Producer
python3 task_producer.py
```

**Expected output:**

```
# Producer
[x] Published task: task_0001
[x] Published task: task_0002
...
[x] Published task: task_0100
[✓] Published 100 tasks to work queue (SOLUTION: With work queue)

# Worker 1 (fast)
[Worker 1] Waiting (SOLUTION: prefetch=1 - fair dispatch, bounded memory)
[x] Received task_0001
[Worker 1] Processed task_0001
[✓] ACKed task_0001
[x] Received task_0002
[Worker 1] Processed task_0002
[✓] ACKed task_0002
...
[Worker 1] Processed 50 tasks (fast worker)

# Worker 2 (slow)
[Worker 2] Waiting (SOLUTION: prefetch=1 - fair dispatch, bounded memory)
[x] Received task_0003
[Worker 2] Processed task_0003
[✓] ACKed task_0003
[x] Received task_0006
[Worker 2] Processed task_0006
[✓] ACKed task_0006
...
[Worker 2] Processed 20 tasks (slow worker)

# Worker 3 (fast)
[Worker 3] Waiting (SOLUTION: prefetch=1 - fair dispatch, bounded memory)
[x] Received task_0004
[Worker 3] Processed task_0004
[✓] ACKed task_0004
[x] Received task_0007
[Worker 3] Processed task_0007
[✓] ACKed task_0007
...
[Worker 3] Processed 30 tasks (fast worker)
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Queues tab → Click on "file_tasks"
3. See 100 tasks ready
4. Go to Channels tab → See 3 consumers/workers
5. Monitor task processing rate
6. See fair distribution (fast workers get more tasks: 50 + 30 = 80 total)
7. See bounded memory (max 1 unacked per worker = 100MB per worker)

**Comparison:**

| Design | Worker 1 | Worker 2 | Worker 3 | Total |
|--------|---------|---------|---------|-------|
| No Prefetch (old) | 67 tasks | 33 tasks | 67 tasks | 167 tasks (no limit) |
| With Prefetch (new) | 50 tasks | 20 tasks | 30 tasks | 100 tasks (fair) |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Always use prefetch on workers (memory bounding)  
- Use prefetch=1 for long-running tasks  
- Use prefetch=5-10 for short tasks  
- Set prefetch based on task processing time  
- Use durable work queue (task survival)  
- Use manual_ack with prefetch (required)  
- Monitor queue depth (backpressure)  
- Scale workers by adding more consumers  
- Process task completely before ACKing  
- Reject on failure (requeue=false)  

**❌ Don't:**
- Not setting prefetch → Worker overload, unfair distribution  
- Setting prefetch too high → Worker OOM crash  
- Setting prefetch too low → Worker idle (waiting for ACK)  
- Using auto_ack with prefetch → Unacked messages lost  
- Not rejecting on failure → Tasks never marked as failed  
- Forgetting to ACK → Tasks requeued (duplication)  
- Not monitoring queue depth → Backpressure issues  
- Using same prefetch for all task types → Inefficient processing  

### Prefetch Guidelines

```
Task Processing Time: Prefetch Count:
├─ Long tasks (seconds to hours): prefetch=1
├─ Medium tasks (1-10 seconds): prefetch=1-5
├─ Short tasks (100-500ms): prefetch=10-20
└─ Very short tasks (1-100ms): prefetch=50-100

Memory Constraints:
├─ Task size: 10MB
├─ Available RAM per worker: 1GB
└─ Safe prefetch: floor(1GB / 10MB / 2) = 50

Worker Count:
├─ Start with 3 workers
├─ Add workers if queue depth > 100
└─ Remove workers if queue depth < 10
```

### Production Considerations

**Scaling Workers:**

```bash
# Add worker dynamically
docker run -d --name worker4 \
  -e TASK_WORKER_ID=4 \
  -p 5672:5672:15672 \
  rabbitmq:3-management \
  your-org/task-worker:latest

# Remove worker dynamically
docker stop worker4
```

**Monitoring Worker Performance:**

```python
# Monitor worker task completion
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Get queue info (depth)
method = channel.queue_declare(queue='file_tasks', passive=True)
queue_depth = method.method.message_count

print(f"Queue depth: {queue_depth}")
print(f"Backpressure: {'NORMAL' if queue_depth < 100 else 'HIGH'}")

# Alert if queue depth too high
if queue_depth > 500:
    print("[ALERT] Queue depth too high - consider adding more workers")
    # Send alert to monitoring system

connection.close()
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's a work queue?**

A: A work queue is a messaging pattern for distributing tasks among multiple workers (consumers) to prevent any single worker from being overwhelmed. Tasks are picked up by available workers, enabling efficient processing of long-running tasks.

**Q2: How does prefetch ensure fair distribution?**

A: Prefetch limits the number of unacknowledged messages each worker can have at once (e.g., prefetch=1 means max 1 unacknowledged). As workers complete tasks, they ACK and receive next available task. Fast workers complete tasks faster, so they receive more tasks over time. Slow workers complete tasks slower, so they receive fewer tasks. This results in fair distribution based on worker speed.

**Q3: What's the right prefetch count?**

A: Prefetch count depends on task processing time and memory constraints:
- Long tasks (seconds to hours): prefetch=1
- Medium tasks (1-10 seconds): prefetch=1-5
- Short tasks (100-500ms): prefetch=10-20
- Formula: prefetch = floor(available_memory / task_size / 2) (safety margin)

**Q4: What happens if you don't set prefetch?**

A: Without prefetch, workers can receive unlimited unacknowledged messages. Fast workers may receive thousands of tasks and run out of memory (OOM crash). Workers receive tasks in round-robin (not based on speed), causing unfair distribution and system instability.

**Q5: How do you scale workers?**

A: Add more consumers/workers to the same work queue. RabbitMQ automatically distributes tasks among available workers based on their processing speed. More workers = faster task processing. Remove workers when queue depth is low to save resources.

### Production Pitfalls

**Pitfall 1: Not setting prefetch**
- Problem: Worker overload, unfair distribution
- Detection: OOM crashes, system instability
- Solution: Always set prefetch based on task processing time

**Pitfall 2: Setting prefetch too high**
- Problem: Worker OOM crash
- Detection: Service outages, unacked messages lost
- Solution: Calculate prefetch based on available RAM and task size

**Pitfall 3: Setting prefetch too low**
- Problem: Worker idle (waiting for ACK)
- Detection: Poor throughput, low resource utilization
- Solution: Increase prefetch to reduce idle time

**Pitfall 4: Not monitoring queue depth**
- Problem: Backpressure issues, no visibility
- Detection: Queue fills with tasks, system stalled
- Solution: Monitor queue depth, alert on high depth, scale workers

**Pitfall 5: Forgetting to ACK**
- Problem: Tasks requeued (duplication)
- Detection: Queue depth not decreasing, duplicate processing
- Solution: Always ACK after successful task processing

### Advanced Work Queue Concepts

**Multiple Work Queues:**

```python
# Separate work queues for different task types
channel.queue_declare(queue='file_processing_tasks', durable=True)
channel.queue_declare(queue='image_processing_tasks', durable=True)
channel.queue_declare(queue='email_sending_tasks', durable=True)

# Different prefetch per queue type
channel.basic_qos(prefetch_count=1, global_qos=True, arguments={'queue': 'file_processing_tasks'})
channel.basic_qos(prefetch_count=10, global_qos=True, arguments={'queue': 'email_sending_tasks'})
```

**Work Queue with Priority:**

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

Work Queues provide fair task distribution among multiple workers (consumers) while preventing worker overload. By setting prefetch limits, workers receive bounded number of tasks, enabling efficient processing of long-running tasks.

**Key takeaways:**
- Work queues distribute tasks among workers fairly
- Prefetch limits unacknowledged tasks per worker
- Set prefetch=1 for long-running tasks
- Set prefetch=5-10 for short tasks
- Use manual_ack with prefetch (required)
- Workers complete tasks based on speed (fast workers get more)
- Scale workers by adding more consumers
- Monitor queue depth for backpressure

**Next steps:**
- Practice with work queues in your applications
- Learn about Publish/Subscribe pattern
- Learn about Routing pattern
- Learn about RPC pattern
- Explore architectural patterns (shovel, federation)

---

**Module 03 - Message Patterns and Architectures**  
**Lesson 01 - Complete**