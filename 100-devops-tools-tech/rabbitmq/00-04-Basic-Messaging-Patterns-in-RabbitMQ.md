# 00-04: Basic Messaging Patterns in RabbitMQ

## 1️⃣ What Are Basic Messaging Patterns

**Messaging patterns** are proven architectural blueprints for how producers and consumers interact through RabbitMQ. They define the communication patterns for solving common distributed systems problems like work distribution, broadcasting, and routing.

Think of messaging patterns like postal delivery methods:

- **Work Queue Pattern** = Multiple mail carriers handling letters efficiently
- **Pub/Sub Pattern** = Sending newsletter to all subscribers
- **Routing Pattern** = Sorting mail by zip code to different regions
- **Topics Pattern** = Matching mail with subject lines to specific departments

**Where patterns fit in RabbitMQ architecture:**

```
┌─────────────────────────────────────────┐
│         Messaging Patterns Layer       │
│                                     │
│  ┌──────────────┐   ┌──────────┐  │
│  │   Producer   │   │ Consumer │  │
│  │  (Sender)    │   │ Receiver │  │
│  └──────┬───────┘   └─────┬────┘  │
│         │                 │       │       │
│         │        Pattern  │       │       │
│         │    Selection  │       │       │
│         ▼                 ▼       │       │
│  ┌──────────────────────────────┐  │   │
│  │   RabbitMQ (Exchanges)     │  │   │
│  └──────────────┬───────────────┘  │   │
│                 │                  │   │
│         ┌───────┼──────────────┐│   │
│         │       │              ││   │
│         ▼       ▼              ▼▼   │
│  ┌─────────┐┌─────────┐┌─────────┐│
│  │  Queue  ││  Queue  ││  Queue  ││
│  └─────────┘└─────────┘└─────────┘│
└─────────────────────────────────────────┘
```

**Key patterns covered:**
- **Work Queue:** Distribute tasks across multiple workers
- **Publish/Subscribe:** Broadcast messages to all consumers
- **Routing:** Direct messages based on routing keys
- **Topics:** Pattern-based routing for complex routing needs

---

## 2️⃣ Problems Solved by Messaging Patterns

### The Work Distribution Problem

Without patterns, systems suffer from:

- Single consumer overwhelmed with work
- Other consumers idle
- No load balancing
- Consumer failures cause message loss

**Real-world failure scenario:**

A data processing company had:

```
Producer → Single Queue → Single Consumer
```

- Consumer processed 100 messages/second
- Producer sent 500 messages/second during spikes
- Queue filled up to 50,000 messages
- Consumer took 500+ seconds to drain
- System became unresponsive during peaks
- **Impact:** Customer SLA violations, $200K in penalties

After implementing Work Queue pattern:
- Multiple consumers (5 workers)
- Each consumer processes 100 messages/second
- Total capacity: 500 messages/second
- Queue depth stays near zero
- **Result:** SLA met, $200K savings

### The Broadcast Problem

Without pub/sub pattern:

- Multiple services need same data
- Producers must send to each service individually
- Tight coupling between services
- Hard to add new consumers

**Example:**

```
Order Service → Payment Service (API call)
Order Service → Inventory Service (API call)
Order Service → Notification Service (API call)
Order Service → Analytics Service (API call)
```

**Problems:**
- Order Service knows about all consumers
- Adding new service requires modifying Order Service
- If one consumer is down, others don't receive data
- No decoupling

After implementing Pub/Sub pattern:
- Order Service publishes to exchange once
- All services subscribe to same queue
- Adding new service is easy (just subscribe)
- Services are decoupled

### The Routing Problem

Without routing patterns:

- All messages go to all consumers
- Consumers filter messages themselves
- Wasteful network traffic
- Hard to manage complex routing rules

**Example:**

```
Log Producer → Queue → All Consumers
                          ├─ Log Writer (needs all logs)
                          ├─ Error Alerter (only errors)
                          └─ Analytics Service (only success)
```

**Problems:**
- All consumers receive all messages
- Error Alerter filters out 90% of messages
- Analytics Service filters 99% of messages
- Wasted bandwidth and CPU

After implementing Routing pattern:
- Messages routed to specific queues
- Each consumer only receives relevant messages
- Efficient use of resources
- Centralized routing rules in RabbitMQ

---

## 3️⃣ When You Should Use Messaging Patterns

### Development vs Production

**Development:**
- Use patterns to learn RabbitMQ concepts
- Great for prototyping different architectures
- Easy to test and iterate
- Helps understand producer/consumer relationships

**Production:**
- Essential for scalable architecture
- Required for efficient message routing
- Critical for decoupling services
- Necessary for load balancing

### Small vs Large Systems

**Small systems (1-5 services):**
- Work Queue pattern most common
- Simple routing sufficient
- Pub/Sub optional but useful

**Large systems (10+ services):**
- Multiple patterns required
- Complex routing needs (Topics)
- Pub/Sub essential for event broadcasting
- Work Queues for horizontal scaling

### Pattern Selection Guide

| Pattern | Use When | Example |
|---------|----------|----------|
| **Work Queue** | Distribute work across workers | Image processing, email sending, data processing |
| **Pub/Sub** | Broadcast to multiple consumers | Notifications, events, news feeds |
| **Routing** | Selective delivery based on category | Logging levels (error/info/debug), priority queues |
| **Topics** | Complex pattern-based routing | Multi-tenant routing, dynamic subscriptions |

### Trade-offs

**Work Queue Pattern:**
✅ Load balancing across workers  
✅ Automatic consumer failover  
✅ Horizontal scaling  
❌ No guarantee of processing order  
❌ Consumers compete for messages  

**Pub/Sub Pattern:**
✅ Broadcast to all consumers  
✅ Decoupled producer/consumer  
✅ Easy to add new consumers  
❌ All consumers receive all messages  
❌ Can cause duplicate processing  

**Routing Pattern:**
✅ Selective message delivery  
✅ Centralized routing rules  
✅ Efficient resource usage  
❌ Producer must know routing keys  
❌ Less flexible than Topics  

**Topics Pattern:**
✅ Flexible, pattern-based routing  
✅ Dynamic subscriptions  
✅ Complex routing logic  
❌ More complex to debug  
❌ Performance overhead with many bindings  

---

## 4️⃣ How Messaging Patterns Work

### Work Queue Pattern (Competing Consumers)

**Concept:**
- Multiple consumers compete for messages from same queue
- RabbitMQ round-robins messages to consumers
- Each message processed by one consumer only

**Architecture:**

```
Producer                    RabbitMQ                   Consumers
   │                            │                         │
   │ 1. Publish              ┌─────────────┐         │
   │──────────────────────────→│   Queue     │         │
   │  (work tasks)            │  "tasks"     │         │
   │                          └──────┬──────┘         │
   │                                 │                 │
   │                          ┌────────┼────────┐     │
   │                          │        │        │     │
   │                          ▼        ▼        ▼     │
   │                      ┌──────┐┌──────┐┌──────┐│
   │                      │Worker1││Worker2││Worker3││
   │                      └──────┘└──────┘└──────┘│
   │                                 │         │
   │                                 └─────────┘
   │
   └─→ 2. New task (round-robins)
```

**How it works:**

1. Producer publishes work tasks to single queue
2. Multiple consumers subscribe to same queue
3. RabbitMQ distributes messages evenly (round-robins)
4. Each consumer processes one message at a time
5. If consumer fails, RabbitMQ redelivers to another consumer

**Example use cases:**
- Image thumbnail generation
- Email sending
- Data processing
- Batch jobs

### Publish/Subscribe Pattern

**Concept:**
- Producer publishes message once
- Multiple consumers each receive a copy
- Consumers process messages independently

**Architecture:**

```
Producer                    RabbitMQ                   Consumers
   │                            │                         │
   │ 1. Publish              ┌─────────────┐         │
   │──────────────────────────→│   Exchange  │         │
   │  (broadcast)             │  (fanout)   │         │
   │                          └──────┬──────┘         │
   │                                 │                 │
   │                          ┌────────┼────────┐     │
   │                          │        │        │     │
   │                    ┌─────────▼┐  ┌───────▼───┐  │
   │                    │  Queue A  │  │  Queue B   │  │
   │                    │ (notif)   │  │ (notif)   │  │
   │                    └─────┬────┘  └───────┬───┘  │
   │                          │                │      │
   │                    ┌───────▼────┐┌──────▼────┐│
   │                    │Consumer A  ││Consumer B  ││
   │                    │(mobile)    ││(email)     ││
   │                    └────────────┘└────────────┘│
   │                                                │
   │         Both consumers get same message              │
   └───────────────────────────────────────────────────────┘
```

**How it works:**

1. Producer publishes to fanout exchange
2. Exchange broadcasts to all bound queues
3. Each queue has its own consumer
4. Each consumer receives every message
5. Consumers process independently

**Example use cases:**
- Push notifications (mobile + email)
- System events (logs + metrics + alerts)
- News feeds
- Cache invalidation

### Routing Pattern (Direct Exchange)

**Concept:**
- Producer publishes with routing key
- Exchange routes to queue with exact matching key
- Selective delivery based on routing key

**Architecture:**

```
Producer                    RabbitMQ                   Consumers
   │                            │                         │
   │ 1. Publish              ┌─────────────┐         │
   │──────────────────────────→│   Exchange  │         │
   │ (routing_key="error")     │  (direct)   │         │
   │                          └──────┬──────┘         │
   │                                 │                 │
   │              ┌────────────────┼────────────┐    │
   │              │                │            │    │
   │              │ key="error"    │key="info"  │    │
   │              ▼                ▼            ▼    │
   │       ┌──────────┐    ┌──────────┐┌──────────┐│
   │       │Queue     │    │Queue     ││Queue     ││
   │       │error-log │    │info-log  ││debug-log ││
   │       └─────┬────┘    └─────┬────┘└─────┬────┘│
   │             │                │            │      │
   │        ┌────▼────┐      ┌────▼────┐  ┌────▼────┐│
   │        │Consumer │      │Consumer │  │Consumer ││
   │        │(pager)  │      │(email)   │  │(db)     ││
   │        └─────────┘      └─────────┘  └─────────┘│
   │                                                    │
   └─→ Only error-log consumer receives error message    │
   │                                                    │
   └────────────────────────────────────────────────────────┘
```

**How it works:**

1. Producer publishes with routing key (e.g., "error", "info", "debug")
2. Direct exchange routes to queue with matching key
3. Only queues with exact matching key receive message
4. Multiple queues can have same key

**Example use cases:**
- Log routing by level (error/info/debug)
- Priority queues (high/normal/low)
- Regional routing (us-east/us-west/eu)

### Topics Pattern (Wildcard Routing)

**Concept:**
- Producer publishes with routing key (e.g., "usa.weather.sunny")
- Exchange routes using wildcard patterns
- * (star) matches one word, # (hash) matches zero or more words

**Architecture:**

```
Producer                    RabbitMQ                   Consumers
   │                            │                         │
   │ 1. Publish              ┌─────────────┐         │
   │──────────────────────────→│   Exchange  │         │
   │ (routing_key="usa.weather")│  (topic)    │         │
   │                          └──────┬──────┘         │
   │                                 │                 │
   │              ┌────────────────┼────────────┐    │
   │              │                │            │    │
   │              │usa.*          │*.weather   │#    │
   │              ▼                ▼            ▼    │
   │       ┌──────────┐    ┌──────────┐┌──────────┐│
   │       │Queue     │    │Queue     ││Queue     ││
   │       │usa-all   │    │all-weather││all-events││
   │       └─────┬────┘    └─────┬────┘└─────┬────┘│
   │             │                │            │      │
   │        ┌────▼────┐      ┌────▼────┐  ┌────▼────┐│
   │        │Consumer │      │Consumer │  │Consumer ││
   │        │(US only)│      │(weather) │  │(all)    ││
   │        └─────────┘      └─────────┘  └─────────┘│
   │                                                    │
   └─→ usa.* and *.weather both match "usa.weather"     │
   │                                                    │
   └────────────────────────────────────────────────────────┘
```

**How it works:**

1. Producer publishes with routing key (e.g., "usa.weather.sunny")
2. Topic exchange matches against binding keys with wildcards
3. `*` matches exactly one word (e.g., "usa.*" matches "usa.weather")
4. `#` matches zero or more words (e.g., "#" matches everything)
5. Multiple queues can match based on different patterns

**Example use cases:**
- Multi-tenant routing (tenant123.orders, tenant123.payments)
- Event streaming (user.created, user.updated, user.deleted)
- Geographic routing (us-east.orders, us-west.orders)
- Complex categorization

---

## 5️⃣ Installation / Setup

**Messaging patterns are built-in RabbitMQ features.** No installation required - just configure exchanges and queues properly.

### Prerequisites

- RabbitMQ server running
- Default exchanges available (amq.direct, amq.fanout, amq.topic)
- AMQP client library installed

### Setting Up Patterns

**Work Queue (default exchange):**

```python
# Producer
channel.queue_declare(queue='tasks')
channel.basic_publish(
    exchange='',  # Default exchange
    routing_key='tasks',
    body='task data'
)

# Consumer (run multiple instances)
channel.queue_declare(queue='tasks')
channel.basic_consume(queue='tasks', ...)
```

**Pub/Sub (fanout exchange):**

```python
# Producer
channel.exchange_declare(exchange='notifications', exchange_type='fanout')
channel.basic_publish(
    exchange='notifications',
    routing_key='',  # Ignored for fanout
    body='notification data'
)

# Consumer
channel.exchange_declare(exchange='notifications', exchange_type='fanout')
result = channel.queue_declare(queue='', exclusive=True)  # Temporary queue
queue_name = result.method.queue
channel.queue_bind(exchange='notifications', queue=queue_name)
channel.basic_consume(queue=queue_name, ...)
```

**Routing (direct exchange):**

```python
# Producer
channel.exchange_declare(exchange='logs', exchange_type='direct')
channel.basic_publish(
    exchange='logs',
    routing_key='error',  # info, warning, debug
    body='error log data'
)

# Consumer (error logs)
channel.exchange_declare(exchange='logs', exchange_type='direct')
channel.queue_declare(queue='error-logs')
channel.queue_bind(exchange='logs', queue='error-logs', routing_key='error')
channel.basic_consume(queue='error-logs', ...)
```

**Topics (topic exchange):**

```python
# Producer
channel.exchange_declare(exchange='events', exchange_type='topic')
channel.basic_publish(
    exchange='events',
    routing_key='user.created',  # or user.updated, user.deleted
    body='user event data'
)

# Consumer (all user events)
channel.exchange_declare(exchange='events', exchange_type='topic')
channel.queue_declare(queue='user-events')
channel.queue_bind(exchange='events', queue='user-events', routing_key='user.*')
channel.basic_consume(queue='user-events', ...)
```

### Version Notes

- **RabbitMQ 3.12+:** All exchange types fully supported
- **Default exchanges:** amq.direct, amq.fanout, amq.topic always available
- **No additional setup required:** Built-in to RabbitMQ core

---

## 6️⃣ Where It Should Be Applied (With Example)

### Work Queue Pattern Example

**Scenario:** Image processing service

**Producer (upload.py):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='image-processing')

# Simulate image upload
for i in range(10):
    message = f'{{"image_id": {i+1}, "path": "/images/img{i+1}.jpg"}}'
    channel.basic_publish(
        exchange='',
        routing_key='image-processing',
        body=message
    )
    print(f" [x] Sent image {i+1} for processing")

connection.close()
```

**Consumer (worker.py) - Run 5 instances:**

```python
import pika
import json
import time

def callback(ch, method, properties, body):
    image = json.loads(body)
    
    # Simulate image processing (resize, thumbnail, etc.)
    print(f" [x] Processing image {image['image_id']}")
    time.sleep(2)  # Simulate processing
    
    print(f" [✓] Finished image {image['image_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='image-processing')

# Fair dispatch
channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue='image-processing', on_message_callback=callback)

print(' [*] Worker waiting for images to process')
channel.start_consuming()
```

**Run 5 workers:**

```bash
# Terminal 1
python3 worker.py

# Terminal 2
python3 worker.py

# ... repeat for 5 terminals

# Terminal 6: Upload images
python3 upload.py
```

**Expected result:**
- 5 workers process 10 images in ~4 seconds (2 images each)
- Work distributed evenly (round-robins)
- If worker fails, RabbitMQ redistributes to others

### Pub/Sub Pattern Example

**Scenario:** Send notifications to multiple services

**Producer (notification_publisher.py):**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.exchange_declare(exchange='notifications', exchange_type='fanout')

# Send notification
notification = {
    "type": "order_shipped",
    "order_id": 12345,
    "customer_id": 678,
    "message": "Your order has been shipped!"
}

channel.basic_publish(
    exchange='notifications',
    routing_key='',  # Ignored for fanout
    body=json.dumps(notification)
)

print(" [x] Sent notification to all subscribers")
connection.close()
```

**Consumer 1 (mobile_notifier.py):**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.exchange_declare(exchange='notifications', exchange_type='fanout')

# Create temporary queue (exclusive=True)
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Bind queue to exchange
channel.queue_bind(exchange='notifications', queue=queue_name)

def callback(ch, method, properties, body):
    notification = json.loads(body)
    print(f" [Mobile] Send push notification: {notification['message']}")

channel.basic_consume(queue=queue_name, on_message_callback=callback)

print(' [*] Mobile notifier waiting for notifications')
channel.start_consuming()
```

**Consumer 2 (email_notifier.py):**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.exchange_declare(exchange='notifications', exchange_type='fanout')

# Create temporary queue
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Bind queue to exchange
channel.queue_bind(exchange='notifications', queue=queue_name)

def callback(ch, method, properties, body):
    notification = json.loads(body)
    print(f" [Email] Send email: {notification['message']}")

channel.basic_consume(queue=queue_name, on_message_callback=callback)

print(' [*] Email notifier waiting for notifications')
channel.start_consuming()
```

**Expected result:**
- Both mobile and email consumers receive same notification
- Easy to add new consumer (analytics, SMS, etc.)
- Publisher doesn't know about consumers

### Routing Pattern Example

**Scenario:** Log routing by severity

**Producer (log_sender.py):**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='direct')

# Send different log levels
logs = [
    ("error", "Database connection failed"),
    ("info", "User logged in"),
    ("warning", "Memory usage high"),
    ("error", "Payment gateway timeout")
]

for level, message in logs:
    log_data = {
        "level": level,
        "message": message,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    channel.basic_publish(
        exchange='logs',
        routing_key=level,
        body=json.dumps(log_data)
    )
    print(f" [x] Sent {level.upper()} log")

connection.close()
```

**Consumer (error_logger.py):**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='direct')
channel.queue_declare(queue='error-logs')
channel.queue_bind(exchange='logs', queue='error-logs', routing_key='error')

def callback(ch, method, properties, body):
    log = json.loads(body)
    print(f" [ERROR] {log['message']} - Page on call!")

channel.basic_consume(queue='error-logs', on_message_callback=callback)

print(' [*] Error logger waiting for ERROR logs')
channel.start_consuming()
```

**Consumer (info_logger.py):**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='direct')
channel.queue_declare(queue='info-logs')
channel.queue_bind(exchange='logs', queue='info-logs', routing_key='info')

def callback(ch, method, properties, body):
    log = json.loads(body)
    print(f" [INFO] {log['message']}")

channel.basic_consume(queue='info-logs', on_message_callback=callback)

print(' [*] Info logger waiting for INFO logs')
channel.start_consuming()
```

**Expected result:**
- Error logger only receives error logs
- Info logger only receives info logs
- Warning logs not consumed (or create warning logger)
- Efficient routing - consumers don't filter

### Best Practices

**Work Queue:**
✅ Use prefetch_count for fair dispatch  
✅ Handle consumer failures gracefully  
✅ Scale horizontally by adding workers  
✅ Monitor queue depth  
✅ Use acknowledgment  

**Pub/Sub:**
✅ Use temporary queues for transient consumers  
✅ Consider message durability  
✅ Handle duplicate processing (idempotency)  
✅ Easy to add/remove consumers  

**Routing:**
✅ Use descriptive routing keys  
✅ Document routing key conventions  
✅ Consider message TTL  
✅ Monitor per-queue message rates  

**Topics:**
✅ Use consistent naming convention  
✅ Document wildcard patterns  
✅ Be careful with # wildcard (matches everything)  
✅ Test routing patterns thoroughly  

### Common Mistakes

❌ Work Queue: Not using prefetch_count → Workers get overwhelmed  
❌ Pub/Sub: Not handling duplicates → Double processing  
❌ Routing: Typo in routing key → Messages not delivered  
❌ Topics: Overusing # wildcard → All consumers receive everything  
❌ All patterns: Forgetting acknowledgment → Messages stuck in unacked  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Inefficient Routing (The Wrong Pattern)**

You're building a logging system with three services:

1. **Error Alerter** - Needs only ERROR logs to page on-call
2. **Log Writer** - Needs ALL logs (ERROR, WARNING, INFO, DEBUG) for archiving
3. **Analytics Service** - Needs only INFO and DEBUG for metrics

Current implementation uses direct exchange:
- Log Producer → Direct Exchange → 4 Queues (error, warning, info, debug)
- Each consumer subscribes to its respective queue

**Problems:**
- Log Writer needs to subscribe to 4 queues (error + warning + info + debug)
- Analytics Service subscribes to 2 queues (info + debug)
- Managing multiple subscriptions is complex
- Adding new log level requires modifying all consumers

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

**Step 2: Create producer with current (inefficient) design**

Create `log_sender.py`:

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Direct exchange (current design)
channel.exchange_declare(exchange='logs', exchange_type='direct')

# Declare 4 queues (one per log level)
channel.queue_declare(queue='error-logs')
channel.queue_bind(exchange='logs', queue='error-logs', routing_key='error')

channel.queue_declare(queue='warning-logs')
channel.queue_bind(exchange='logs', queue='warning-logs', routing_key='warning')

channel.queue_declare(queue='info-logs')
channel.queue_bind(exchange='logs', queue='info-logs', routing_key='info')

channel.queue_declare(queue='debug-logs')
channel.queue_bind(exchange='logs', queue='debug-logs', routing_key='debug')

# Send logs
levels = ['error', 'warning', 'info', 'debug']
for i in range(20):
    level = levels[i % 4]
    message = f'Log message {i+1}'
    
    log_data = {
        "level": level,
        "message": message,
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='logs',
        routing_key=level,
        body=json.dumps(log_data)
    )
    print(f" [x] Sent {level.upper()}: {message}")

connection.close()
```

**Step 3: Create Log Writer (needs ALL logs)**

Create `log_writer.py`:

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='direct')

# PROBLEM: Must subscribe to 4 queues!
def create_consumer(queue_name):
    channel.queue_declare(queue=queue_name)
    channel.queue_bind(exchange='logs', queue=queue_name, routing_key=queue_name.split('-')[0])
    
    def callback(ch, method, properties, body):
        log = json.loads(body)
        print(f" [Log Writer] {log['level'].upper()}: {log['message']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

# Subscribe to all 4 queues
create_consumer('error-logs')
create_consumer('warning-logs')
create_consumer('info-logs')
create_consumer('debug-logs')

print(' [*] Log Writer consuming from 4 queues...')
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal 1: Run Log Writer
python3 log_writer.py

# Terminal 2: Send logs
python3 log_sender.py
```

**Observation:**
- Log Writer needs to manage 4 queues
- Channel has 4 consumers (one per queue)
- Complex to manage
- Adding new log level requires modifying Log Writer

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Exchanges tab → Click on "logs"
- See 4 bindings (error, warning, info, debug)
- Go to Channels tab → Log Writer has 4 channels
- Complex topology!

### ✅ Solution & Explanation

**Solution: Use Topic Exchange Pattern**

**Create improved producer (topic_log_sender.py):**

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# FIX: Use topic exchange!
channel.exchange_declare(exchange='logs', exchange_type='topic')

# Send logs with routing keys
levels = ['error', 'warning', 'info', 'debug']
for i in range(20):
    level = levels[i % 4]
    message = f'Log message {i+1}'
    
    log_data = {
        "level": level,
        "message": message,
        "timestamp": time.time()
    }
    
    # FIX: Use routing key with level
    channel.basic_publish(
        exchange='logs',
        routing_key=f'log.{level}',
        body=json.dumps(log_data)
    )
    print(f" [x] Sent {level.upper()}: {message}")

connection.close()
```

**Create improved Log Writer (needs ALL logs):**

Create `improved_log_writer.py`:

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# FIX: Use topic exchange
channel.exchange_declare(exchange='logs', exchange_type='topic')

# FIX: Temporary queue, single binding!
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# FIX: Single binding with wildcard (# matches everything)
channel.queue_bind(exchange='logs', queue=queue_name, routing_key='log.#')

def callback(ch, method, properties, body):
    log = json.loads(body)
    print(f" [Log Writer] {log['level'].upper()}: {log['message']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=queue_name, on_message_callback=callback)

print(' [*] Log Writer consuming ALL logs with single binding')
channel.start_consuming()
```

**Create improved Error Alerter (only ERROR logs):**

Create `error_alerter.py`:

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Use topic exchange
channel.exchange_declare(exchange='logs', exchange_type='topic')

# Temporary queue
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# FIX: Bind to log.error only!
channel.queue_bind(exchange='logs', queue=queue_name, routing_key='log.error')

def callback(ch, method, properties, body):
    log = json.loads(body)
    print(f" [ALERT] {log['level'].upper()}: {log['message']} - PAGE ON-CALL!")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=queue_name, on_message_callback=callback)

print(' [*] Error Alerter waiting for ERROR logs only')
channel.start_consuming()
```

**Create improved Analytics Service (INFO + DEBUG):**

Create `analytics.py`:

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Use topic exchange
channel.exchange_declare(exchange='logs', exchange_type='topic')

# Temporary queue
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# FIX: Two bindings for log.info and log.debug
channel.queue_bind(exchange='logs', queue=queue_name, routing_key='log.info')
channel.queue_bind(exchange='logs', queue=queue_name, routing_key='log.debug')

def callback(ch, method, properties, body):
    log = json.loads(body)
    print(f" [Analytics] {log['level'].upper()}: Processing metrics...")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=queue_name, on_message_callback=callback)

print(' [*] Analytics waiting for INFO and DEBUG logs')
channel.start_consuming()
```

**How to verify:**

```bash
# Clear RabbitMQ
docker stop rabbitmq && docker rm rabbitmq
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Terminal 1: Start Log Writer
python3 improved_log_writer.py

# Terminal 2: Start Error Alerter
python3 error_alerter.py

# Terminal 3: Start Analytics
python3 analytics.py

# Terminal 4: Send logs
python3 topic_log_sender.py
```

**Expected output:**

```
# Log Writer (receives ALL 20 logs)
[Log Writer] ERROR: Log message 1
[Log Writer] WARNING: Log message 2
[Log Writer] INFO: Log message 3
[Log Writer] DEBUG: Log message 4
...

# Error Alerter (receives only 5 ERROR logs)
[ALERT] ERROR: Log message 1 - PAGE ON-CALL!
[ALERT] ERROR: Log message 5 - PAGE ON-CALL!
...

# Analytics (receives 10 INFO + DEBUG logs)
[Analytics] INFO: Log message 3 - Processing metrics...
[Analytics] DEBUG: Log message 4 - Processing metrics...
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Exchanges tab → Click on "logs"
3. See bindings:
   - `log.error` → Error Alerter
   - `log.info` → Analytics Service
   - `log.debug` → Analytics Service
   - `log.#` → Log Writer (matches everything)
4. Much simpler topology!

**Comparison:**

| Design | Bindings | Complexity | Adding new consumer |
|--------|----------|------------|---------------------|
| Direct (old) | 4 queues × consumers | High | Modify all consumers |
| Topic (new) | 1 binding per consumer | Low | Add new binding only |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Choose right pattern for your use case
- Use Work Queue for task distribution
- Use Pub/Sub for broadcasting events
- Use Routing for category-based delivery
- Use Topics for complex, dynamic routing
- Test routing patterns thoroughly
- Document routing key conventions
- Monitor message rates per queue
- Use acknowledgment for reliability
- Consider message durability

**❌ Don't:**
- Use wrong pattern for use case
- Forget prefetch in Work Queue
- Ignore duplicate processing in Pub/Sub
- Use # wildcard in Topics unnecessarily
- Mix patterns without understanding
- Skip testing routing logic
- Forget to bind queues to exchanges
- Use auto_ack in production
- Ignore queue depth monitoring
- Overengineer simple use cases

### Pattern Selection Guide

```
Start with these questions:

1. Do multiple consumers need same message?
   YES → Pub/Sub or Topics
   NO  → Work Queue or Routing

2. Do consumers compete for messages (each message once)?
   YES → Work Queue
   NO  → Routing or Topics

3. Do you need selective delivery?
   YES → Routing or Topics
   NO  → Work Queue or Pub/Sub

4. Is routing key format flexible/variable?
   YES → Topics
   NO  → Routing
```

### Production Considerations

**Message ordering:**
- Work Queue: No guarantee with multiple consumers
- Pub/Sub: Each queue maintains order
- Routing/Topics: Order maintained per queue

**Scaling:**
- Work Queue: Add more consumers
- Pub/Sub: Add more queues/consumers
- Routing/Topics: Add more queues/consumers with bindings

**Failure handling:**
- All patterns: Use manual acknowledgment
- Work Queue: RabbitMQ redistributes to other consumers
- Pub/Sub: Message lost if consumer not running
- Routing/Topics: Message lost if no matching queue

### Performance Tips

**Work Queue optimization:**
```python
# Fair dispatch
channel.basic_qos(prefetch_count=1)

# Or for high throughput
channel.basic_qos(prefetch_count=10)
```

**Topics optimization:**
- Avoid overly broad wildcards (log.# matches everything)
- Use specific patterns (log.error instead of log.*)
- Monitor binding count (too many = slow)
- Consider multiple exchanges for different domains

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's the difference between Work Queue and Routing patterns?**

A: Work Queue has multiple consumers competing for messages from same queue (each message to one consumer). Routing has multiple queues, each consumer gets messages matching their routing key. Work Queue for load balancing, Routing for selective delivery.

**Q2: When should you use Topics instead of Routing?**

A: Use Topics when you need flexible, pattern-based routing. Use Routing when routing keys are fixed and exact match is sufficient. Topics use wildcards (* and #), Routing uses exact match.

**Q3: What happens if no queue matches the routing key?**

A: Message is discarded (unless using mandatory flag). RabbitMQ returns unroutable message to publisher if mandatory=true. Otherwise, message is dropped.

**Q4: Can a queue bind to multiple exchanges?**

A: Yes, queue can have multiple bindings to same or different exchanges. Each binding has its own routing key. Queue receives messages matching any binding.

**Q5: What's the difference between fanout and topic with # wildcard?**

A: Fanout broadcasts to all bound queues. Topic with # matches all routing keys but you can have other bindings too (e.g., log.error and log.#). Fanout is simpler, Topics are more flexible.

### Production Pitfalls

**Pitfall 1: Wrong pattern choice**
- Problem: Using Pub/Sub when Work Queue needed
- Detection: Consumers overwhelmed, poor load balancing
- Solution: Reevaluate requirements, choose appropriate pattern

**Pitfall 2: Overusing # wildcard in Topics**
- Problem: All consumers receive all messages
- Detection: High CPU/network usage, consumers overwhelmed
- Solution: Use specific patterns, avoid # unless necessary

**Pitfall 3: Not using prefetch in Work Queue**
- Problem: One consumer gets all messages, others idle
- Detection: Unbalanced load, one consumer overwhelmed
- Solution: Use channel.basic_qos(prefetch_count=1)

**Pitfall 4: Missing queue bindings**
- Problem: Messages not routed to any queue
- Detection: No consumers receiving messages, messages dropped
- Solution: Test bindings, use mandatory flag, verify in Management UI

### Advanced Pattern Combinations

**Work Queue + Pub/Sub:**

```python
# Multiple consumers, each gets copy
channel.exchange_declare(exchange='events', exchange_type='fanout')

# Each consumer creates its own queue
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='events', queue=queue_name)
channel.basic_consume(queue=queue_name, ...)

# Run multiple instances - each gets copy
```

**Routing + Work Queue:**

```python
# Route to specific queue, multiple consumers compete
channel.exchange_declare(exchange='tasks', exchange_type='direct')
channel.queue_declare(queue='high-priority')
channel.queue_bind(exchange='tasks', queue='high-priority', routing_key='high')

# Multiple consumers for high-priority tasks
channel.basic_consume(queue='high-priority', ...)
```

**Topics + TTL:**

```python
# Messages expire if not consumed
channel.exchange_declare(exchange='logs', exchange_type='topic')

result = channel.queue_declare(
    queue='',
    exclusive=True,
    arguments={'x-message-ttl': 60000}  # 60 seconds TTL
)
queue_name = result.method.queue

channel.queue_bind(exchange='logs', queue=queue_name, routing_key='log.error')
```

---

## 📚 Summary

Messaging patterns provide proven architectural blueprints for common RabbitMQ use cases. Understanding when to use Work Queue, Pub/Sub, Routing, or Topics is essential for building scalable, maintainable distributed systems.

**Key takeaways:**
- Work Queue: Distribute work across multiple workers
- Pub/Sub: Broadcast messages to all consumers
- Routing: Selective delivery based on exact routing key
- Topics: Flexible, pattern-based routing with wildcards
- Choose pattern based on requirements, not what's easiest
- Test routing logic thoroughly in development

**Next steps:**
- Practice each pattern with hands-on examples
- Combine patterns for complex use cases
- Learn about exchange types in detail
- Understand queue properties and TTL
- Explore advanced routing features

---

**Module 00 - Foundations of RabbitMQ**  
**Lesson 04 - Complete**
**Module 00 - Foundations of RabbitMQ - COMPLETE** ✅