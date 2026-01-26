# 01-01: Exchanges and Their Types

## 1️⃣ What Are Exchanges

**Exchanges** are message routing agents in RabbitMQ that receive messages from producers and route them to queues based on rules. They act as the central routing hub, determining where messages should go based on exchange type and routing keys.

Think of exchanges like a post office sorting center:

- **Exchange** = The sorting center that receives all mail
- **Routing Key** = The address/zip code on the envelope
- **Binding Key** = The destination routes from sorting center
- **Queue** = The final mailboxes for recipients

**Where exchanges fit in RabbitMQ architecture:**

```
┌─────────────┐
│  Producer   │
└──────┬──────┘
       │
       │ Publish (with routing key)
       ▼
┌─────────────────────────────────┐
│        Exchange             │
│  (Routes messages to queues) │
└──────┬──────────────────────┘
       │
       │ Routing Rules (Bindings)
       ├────────────────┬────────────────┬────────────────┐
       │                │                │                │
       ▼                ▼                ▼                ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Queue A │    │  Queue B │    │  Queue C │    │  Queue D │
│ (orders) │    │ (logs)   │    │ (alerts) │    │ (events) │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

**Exchange types:**
- **Direct:** Routes messages to queues with exact routing key match
- **Fanout:** Broadcasts messages to all bound queues (ignores routing key)
- **Topic:** Routes messages using wildcard pattern matching on routing keys
- **Headers:** Routes messages based on header name/value pairs (rarely used)

---

## 2️⃣ Problems Solved by Exchanges

### The Direct Coupling Problem

Without exchanges (point-to-point messaging):

- Producers must know all queue names
- Tight coupling between producer and consumer
- Hard to add new queues or consumers
- No flexibility in routing logic

**Real-world failure scenario:**

An e-commerce system had:

```
Order Service → Direct to Queue → Payment Service (queue: payment)
                          → Inventory Service (queue: inventory)
                          → Notification Service (queue: notification)
```

**Problems:**
- Order Service hardcoded 3 queue names
- Adding "Analytics Service" required code change
- If Payment Service changes queue name, Order Service breaks
- No way to selectively route messages
- **Impact:** 2-week development cycle for each new service, $50K in lost time

After implementing exchanges:
- Order Service publishes to single exchange
- Each service binds its own queue with appropriate routing key
- Adding new service = just add new queue and binding (no code change)
- Flexible routing logic centralized in RabbitMQ
- **Result:** New services added in hours, not weeks

### The Routing Complexity Problem

Without proper exchange types:

- Complex routing logic scattered across applications
- Hard to maintain and debug routing rules
- Performance issues with application-level filtering
- No central control over message flow

**Example:**

```
Producer → Application-Level Router → Queue A
        → Application-Level Router → Queue B
        → Application-Level Router → Queue C
```

**Problems:**
- Application must know all destinations
- Routing logic duplicated in every producer
- Hard to change routing rules
- Network overhead (messages sent multiple times)
- Application complexity increases

After implementing exchanges:
- Routing logic centralized in RabbitMQ
- Producers don't need to know destinations
- Easy to change routing (update bindings)
- Single message published once
- Simplified application code

---

## 3️⃣ When You Should Use Exchanges

### Development vs Production

**Development:**
- Use exchanges to learn routing concepts
- Great for prototyping different architectures
- Easy to test with Management UI
- Helps understand message flow

**Production:**
- Absolutely required for scalable architecture
- Essential for decoupling services
- Critical for flexible routing
- Necessary for multi-consumer scenarios

### Exchange Type Selection

| Exchange Type | Use When | Example |
|--------------|----------|----------|
| **Direct** | Exact routing key match | Log levels (error/info/debug), priority queues |
| **Fanout** | Broadcast to all queues | Notifications, cache invalidation, events |
| **Topic** | Pattern-based routing | Multi-tenant, complex categorization, dynamic routing |
| **Headers** | Header-based routing (rare) | Complex routing based on message metadata |

### Required vs Optional

**Required when:**
- Multiple consumers need messages
- Different consumers need different messages
- Routing logic should be centralized
- Want to decouple producer from consumer
- Need flexible, dynamic routing

**Optional when:**
- Single producer, single consumer (point-to-point)
- Very simple use case with no routing needs
- Learning/experimenting (default exchange works)

### Trade-offs

**Direct Exchange:**
✅ Simple, exact match routing  
✅ Fast performance  
✅ Easy to understand and debug  
❌ Inflexible (no patterns)  
❌ Producer must know routing keys  

**Fanout Exchange:**
✅ Broadcast to all bound queues  
✅ Simple, no routing key needed  
✅ Decouples producer from all consumers  
❌ All consumers get all messages  
❌ Wasteful if consumers don't need all messages  

**Topic Exchange:**
✅ Flexible pattern-based routing  
✅ Dynamic subscriptions  
✅ Complex routing logic possible  
❌ More complex to debug  
❌ Performance overhead with many bindings  
❌ Requires careful naming convention  

**Headers Exchange:**
✅ Routes based on message headers  
✅ Very flexible routing  
❌ Complex to configure  
❌ Poor performance  
❌ Rarely used in practice  

---

## 4️⃣ How Exchanges Work

### Exchange Architecture

**Exchange processing flow:**

```
1. Producer Publishes Message
   │
   ├─ Exchange name
   ├─ Routing key
   ├─ Message body
   └─ Properties (headers)
   │
2. Exchange Receives Message
   │
   ├─ Get exchange type (direct/fanout/topic/headers)
   ├─ Get routing key (or headers)
   └─ Get message properties
   │
3. Exchange Routes to Queues
   │
   ├─ Check all bindings for this exchange
   ├─ Match routing key against binding keys
   ├─ Apply exchange-specific routing logic
   └─ Deliver to matching queues
   │
4. Queues Receive Messages
   │
   └─ Consumers receive from their queues
```

### Direct Exchange

**Routing logic:** Exact match between message routing key and queue binding key.

```
Exchange: logs (type: direct)

Bindings:
├─ Queue "error-logs"  ← binding_key="error"
├─ Queue "info-logs"    ← binding_key="info"
└─ Queue "debug-logs"   ← binding_key="debug"

Message Flow:
┌─────────┐
│Producer │─→ routing_key="error" ──→ Matches Queue "error-logs" ✓
└─────────┘
│Producer │─→ routing_key="info" ───→ Matches Queue "info-logs" ✓
└─────────┘
│Producer │─→ routing_key="warning" → NO MATCH (discarded) ✗
└─────────┘
```

**Characteristics:**
- Exact match required
- Multiple queues can have same binding key (all receive message)
- Fast, simple routing
- Most commonly used after default exchange

### Fanout Exchange

**Routing logic:** Ignores routing key, broadcasts to all bound queues.

```
Exchange: notifications (type: fanout)

Bindings:
├─ Queue "mobile-queue"   ← (any binding_key, ignored)
├─ Queue "email-queue"    ← (any binding_key, ignored)
└─ Queue "slack-queue"    ← (any binding_key, ignored)

Message Flow:
┌─────────┐
│Producer │─→ routing_key="anything" ──→ All 3 queues receive message
└─────────┘
```

**Characteristics:**
- Ignores routing key completely
- Broadcasts to ALL bound queues
- Each queue gets copy of message
- Simplest exchange type
- Perfect for pub/sub pattern

### Topic Exchange

**Routing logic:** Pattern matching using wildcards on routing keys.

**Wildcard rules:**
- `*` (star) matches exactly one word
- `#` (hash) matches zero or more words

```
Exchange: events (type: topic)

Bindings:
├─ Queue "user-events"      ← binding_key="user.*"
├─ Queue "order-events"     ← binding_key="order.*"
└─ Queue "all-events"       ← binding_key="#"

Message Flow:
┌─────────┐
│Producer │─→ routing_key="user.created" ──→ Matches "user.*" ✓
└─────────┘                                    Matches "#" ✓
                                               (2 queues)

┌─────────┐
│Producer │─→ routing_key="order.paid" ───→ Matches "order.*" ✓
└─────────┘                                    Matches "#" ✓
                                               (2 queues)

┌─────────┐
│Producer │─→ routing_key="payment.failed" → Matches only "#" ✓
└─────────┘                                        (1 queue)
```

**Binding key examples:**

| Binding Key | Matches | Doesn't Match |
|------------|--------|---------------|
| `log.error` | `log.error` | `log.error.critical` |
| `log.*` | `log.error`, `log.info` | `log`, `log.error.critical` |
| `*.error` | `log.error`, `db.error` | `log.error.critical` |
| `#` | Everything | Nothing |
| `log.#` | `log`, `log.error`, `log.error.critical` | `error.log` |

**Characteristics:**
- Most flexible exchange type
- Requires naming convention for routing keys
- Can create complex routing patterns
- Slower than direct/fanout (pattern matching overhead)
- Most powerful for dynamic routing

### Headers Exchange

**Routing logic:** Routes based on message header name/value pairs.

```
Exchange: routed (type: headers)

Bindings:
├─ Queue "high-priority" ← headers: {"priority": "high"}
└─ Queue "urgent"        ← headers: {"urgency": "urgent", "x-match": "all"}

Message Flow:
┌─────────┐
│Producer │─→ headers: {"priority": "high"} ──→ Matches "high-priority" ✓
└─────────┘

┌─────────┐
│Producer │─→ headers: {"priority": "high", "urgency": "urgent"}
└─────────┘      → Matches "high-priority" ✓
                → Matches "urgent" ✓
                (2 queues)
```

**Characteristics:**
- Routes based on message headers, not routing key
- `x-match` header: "all" (all headers must match) or "any" (one match sufficient)
- Very flexible but complex
- Poor performance compared to other types
- Rarely used in production

### Exchange Attributes

**Common exchange properties:**

```python
# Creating exchange with properties
channel.exchange_declare(
    exchange='my-exchange',
    exchange_type='direct',
    durable=True,           # Survive broker restart
    auto_delete=False,       # Don't delete when no bindings
    internal=False,         # Not used for client publishing
    arguments={}            # Custom arguments
)
```

**Property explanations:**

- **durable**: Exchange survives RabbitMQ restart. Messages to durable exchanges don't persist (message durability depends on queue).
- **auto_delete**: Exchange deleted when last queue unbound. Useful for temporary exchanges.
- **internal**: Internal exchange (can't be published to by clients). Used for exchange-to-exchange bindings.
- **arguments**: Custom arguments for exchange behavior (e.g., alternate exchange for unroutable messages).

---

## 5️⃣ Installation / Setup

**Exchanges are built-in RabbitMQ features.** No installation required - just declare exchanges properly.

### Prerequisites

- RabbitMQ server running
- AMQP client library installed
- Basic understanding of routing concepts

### Creating Exchanges

**Direct Exchange:**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare direct exchange
channel.exchange_declare(
    exchange='logs',
    exchange_type='direct',
    durable=True
)

print(" [✓] Direct exchange 'logs' created")
connection.close()
```

**Fanout Exchange:**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare fanout exchange
channel.exchange_declare(
    exchange='notifications',
    exchange_type='fanout',
    durable=True
)

print(" [✓] Fanout exchange 'notifications' created")
connection.close()
```

**Topic Exchange:**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare topic exchange
channel.exchange_declare(
    exchange='events',
    exchange_type='topic',
    durable=True
)

print(" [✓] Topic exchange 'events' created")
connection.close()
```

**Headers Exchange:**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare headers exchange
channel.exchange_declare(
    exchange='routed',
    exchange_type='headers',
    durable=True
)

print(" [✓] Headers exchange 'routed' created")
connection.close()
```

### Default Exchange

**Default exchange** (`amq.default` or empty string `""`) is a special direct exchange pre-declared by RabbitMQ.

```python
# Publishing to default exchange (direct routing)
channel.basic_publish(
    exchange='',  # Default exchange
    routing_key='my-queue',  # Queue name = routing key
    body='message'
)
```

**Characteristics:**
- Pre-declared, always available
- Direct exchange type
- Routing key = queue name (direct routing to specific queue)
- Most common for simple use cases

### Version Notes

- **RabbitMQ 3.12+:** All exchange types fully supported and stable
- **Default exchanges:** `amq.direct`, `amq.fanout`, `amq.topic`, `amq.headers` always available
- **No additional setup required:** Exchanges built into RabbitMQ core

---

## 6️⃣ Where Exchanges Should Be Applied (With Example)

### Exchange in Application Code

**Producer using direct exchange:**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare direct exchange
channel.exchange_declare(exchange='logs', exchange_type='direct')

# Publish error log
error_log = {
    "level": "error",
    "message": "Database connection failed",
    "timestamp": "2024-01-15T10:30:00Z"
}

channel.basic_publish(
    exchange='logs',
    routing_key='error',  # Routing key
    body=json.dumps(error_log)
)

print(" [x] Sent error log to direct exchange")

# Publish info log
info_log = {
    "level": "info",
    "message": "User logged in",
    "timestamp": "2024-01-15T10:31:00Z"
}

channel.basic_publish(
    exchange='logs',
    routing_key='info',  # Different routing key
    body=json.dumps(info_log)
)

print(" [x] Sent info log to direct exchange")

connection.close()
```

**Producer using fanout exchange:**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare fanout exchange
channel.exchange_declare(exchange='notifications', exchange_type='fanout')

# Publish notification
notification = {
    "type": "order_shipped",
    "order_id": 12345,
    "message": "Your order has been shipped!"
}

channel.basic_publish(
    exchange='notifications',
    routing_key='',  # Ignored for fanout
    body=json.dumps(notification)
)

print(" [x] Sent notification to fanout exchange (broadcast)")

connection.close()
```

**Producer using topic exchange:**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare topic exchange
channel.exchange_declare(exchange='events', exchange_type='topic')

# Publish user event
user_event = {
    "event_type": "user.created",
    "user_id": 12345,
    "email": "user@example.com"
}

channel.basic_publish(
    exchange='events',
    routing_key='user.created',  # Topic routing key
    body=json.dumps(user_event)
)

print(" [x] Sent user event to topic exchange")

# Publish order event
order_event = {
    "event_type": "order.paid",
    "order_id": 67890,
    "amount": 99.99
}

channel.basic_publish(
    exchange='events',
    routing_key='order.paid',  # Different topic
    body=json.dumps(order_event)
)

print(" [x] Sent order event to topic exchange")

connection.close()
```

### Using rabbitmqctl for Exchanges

```bash
# List all exchanges
sudo rabbitmqctl list_exchanges

# List exchanges with details
sudo rabbitmqctl list_exchanges name type durable auto_delete

# Declare exchange (via management plugin)
sudo rabbitmqctl eval 'rabbit_exchange:declare(direct, <<"my-exchange">>, [], false).'

# Delete exchange
sudo rabbitmqctl delete_exchange name=my-exchange

# List bindings for exchange
sudo rabbitmqctl list_bindings source destination
```

### Exchange-to-Exchange Bindings

Advanced feature: Exchanges can bind to other exchanges for complex routing.

```python
# Create exchange A (direct)
channel.exchange_declare(exchange='exchange-a', exchange_type='direct')

# Create exchange B (topic)
channel.exchange_declare(exchange='exchange-b', exchange_type='topic')

# Bind exchange B to exchange A
channel.exchange_bind(
    source='exchange-a',
    destination='exchange-b',
    routing_key='events'
)

# Messages to exchange-a are now routed through exchange-b
channel.basic_publish(
    exchange='exchange-a',
    routing_key='events.user.created',
    body='message'
)
```

### Best Practices

**Exchange Design:**
✅ Use descriptive exchange names  
✅ Choose appropriate exchange type for use case  
✅ Make exchanges durable in production  
✅ Document routing key conventions  
✅ Use consistent naming (e.g., `logs`, `events`, `notifications`)  

**Routing Keys:**
✅ Use hierarchical routing keys (e.g., `user.created`, `order.paid`)  
✅ Keep routing keys simple and predictable  
✅ Document naming convention  
✅ Avoid overly complex patterns  
✅ Use dot-separated words for topics  

**Exchange Attributes:**
✅ Set durable=True for production exchanges  
✅ Use auto_delete for temporary exchanges only  
✅ Consider alternate exchange for unroutable messages  
✅ Monitor exchange message rates  

### Common Mistakes

❌ Wrong exchange type for use case → Routing failures  
❌ Typos in routing keys → Messages not delivered  
❌ Forgetting to bind queues → Messages discarded  
❌ Using fanout when direct needed → All consumers get everything  
❌ Overcomplicating topic patterns → Hard to debug  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Message Black Hole (The Lost Messages)**

You're building a notification system with:
- Order Service publishes order events
- Email Service needs all order events
- SMS Service needs only urgent orders (priority="high")
- Push Notification Service needs only shipped orders

Current implementation uses fanout exchange:
- Order Service → Fanout Exchange → All three queues
- All services receive all order events
- Services must filter messages themselves

**Problems:**
- SMS Service receives non-urgent messages (99% wasted)
- Push Service receives all order types (99% wasted)
- Wasted bandwidth and processing
- No centralized routing logic

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

**Step 2: Create problematic producer (fanout exchange)**

Create `order_producer.py`:

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: Using fanout exchange
channel.exchange_declare(exchange='order-events', exchange_type='fanout')

# Simulate different order events
orders = [
    {"type": "created", "priority": "normal", "order_id": 1},
    {"type": "paid", "priority": "normal", "order_id": 2},
    {"type": "shipped", "priority": "normal", "order_id": 3},
    {"type": "created", "priority": "high", "order_id": 4},
    {"type": "paid", "priority": "high", "order_id": 5},
    {"type": "shipped", "priority": "high", "order_id": 6},
]

for order in orders:
    channel.basic_publish(
        exchange='order-events',
        routing_key='',  # Ignored for fanout
        body=json.dumps(order)
    )
    print(f" [x] Sent order {order['order_id']}: {order['type']} (priority={order['priority']})")

print(" [✓] Sent 6 orders (all go to all services)")
connection.close()
```

**Step 3: Create SMS Service (needs urgent only)**

Create `sms_service.py`:

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.exchange_declare(exchange='order-events', exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='order-events', queue=queue_name)

def callback(ch, method, properties, body):
    order = json.loads(body)
    
    # PROBLEM: Receives ALL orders, must filter
    if order['priority'] == 'high':
        print(f" [SMS] Send SMS for urgent order {order['order_id']}")
    else:
        print(f" [SMS] WASTED: Non-urgent order {order['order_id']} (ignored)")

channel.basic_consume(queue=queue_name, on_message_callback=callback)

print(' [*] SMS Service waiting for orders (will filter)')
channel.start_consuming()
```

**Step 4: Create Push Service (needs shipped only)**

Create `push_service.py`:

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.exchange_declare(exchange='order-events', exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='order-events', queue=queue_name)

def callback(ch, method, properties, body):
    order = json.loads(body)
    
    # PROBLEM: Receives ALL orders, must filter
    if order['type'] == 'shipped':
        print(f" [Push] Send push notification: Order {order['order_id']} shipped")
    else:
        print(f" [Push] WASTED: Non-shipped order {order['order_id']} (ignored)")

channel.basic_consume(queue=queue_name, on_message_callback=callback)

print(' [*] Push Service waiting for orders (will filter)')
channel.start_consuming()
```

**Step 5: Reproduce problem**

```bash
# Terminal 1: SMS Service
python3 sms_service.py

# Terminal 2: Push Service
python3 push_service.py

# Terminal 3: Producer
python3 order_producer.py
```

**Expected observation:**
- SMS Service receives all 6 orders, only processes 2 (urgent)
- Push Service receives all 6 orders, only processes 2 (shipped)
- 66% of messages wasted (received but ignored)
- Services doing unnecessary filtering

**Step 6: View in Management UI**

Open http://localhost:15672:
- Go to Exchanges tab → Click on "order-events"
- See fanout exchange type
- See bindings (all queues bound to exchange)
- Observe message rates - high wasted traffic

### ✅ Solution & Explanation

**Solution: Use Topic Exchange with Routing Keys**

**Create improved producer (topic_exchange_producer.py):**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# FIX: Use topic exchange!
channel.exchange_declare(exchange='order-events', exchange_type='topic')

# Send orders with routing keys
orders = [
    {"type": "created", "priority": "normal", "order_id": 1},
    {"type": "paid", "priority": "normal", "order_id": 2},
    {"type": "shipped", "priority": "normal", "order_id": 3},
    {"type": "created", "priority": "high", "order_id": 4},
    {"type": "paid", "priority": "high", "order_id": 5},
    {"type": "shipped", "priority": "high", "order_id": 6},
]

for order in orders:
    # FIX: Routing key: order.type.order.priority
    routing_key = f"order.{order['type']}.{order['priority']}"
    
    channel.basic_publish(
        exchange='order-events',
        routing_key=routing_key,  # Topic routing key
        body=json.dumps(order)
    )
    print(f" [x] Sent order {order['order_id']}: {routing_key}")

print(" [✓] Sent 6 orders with topic routing keys")
connection.close()
```

**Create improved SMS Service (urgent orders only):**

Create `improved_sms_service.py`:

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Use topic exchange
channel.exchange_declare(exchange='order-events', exchange_type='topic')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# FIX: Bind to urgent orders only (all types, priority=high)
channel.queue_bind(exchange='order-events', queue=queue_name, routing_key='order.*.high')

def callback(ch, method, properties, body):
    order = json.loads(body)
    
    # FIX: No filtering needed - RabbitMQ routes correctly!
    print(f" [SMS] Send SMS for urgent order {order['order_id']}")

channel.basic_consume(queue=queue_name, on_message_callback=callback)

print(' [*] SMS Service waiting for urgent orders only')
channel.start_consuming()
```

**Create improved Push Service (shipped orders only):**

Create `improved_push_service.py`:

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Use topic exchange
channel.exchange_declare(exchange='order-events', exchange_type='topic')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# FIX: Bind to shipped orders only (all priorities)
channel.queue_bind(exchange='order-events', queue=queue_name, routing_key='order.shipped.*')

def callback(ch, method, properties, body):
    order = json.loads(body)
    
    # FIX: No filtering needed - RabbitMQ routes correctly!
    print(f" [Push] Send push: Order {order['order_id']} shipped")

channel.basic_consume(queue=queue_name, on_message_callback=callback)

print(' [*] Push Service waiting for shipped orders only')
channel.start_consuming()
```

**Create Email Service (all orders):**

Create `email_service.py`:

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Use topic exchange
channel.exchange_declare(exchange='order-events', exchange_type='topic')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# FIX: Bind to all orders (order.# matches everything)
channel.queue_bind(exchange='order-events', queue=queue_name, routing_key='order.#')

def callback(ch, method, properties, body):
    order = json.loads(body)
    print(f" [Email] Send email for order {order['order_id']}")

channel.basic_consume(queue=queue_name, on_message_callback=callback)

print(' [*] Email Service waiting for all orders')
channel.start_consuming()
```

**How to verify:**

```bash
# Clear RabbitMQ
docker stop rabbitmq && docker rm rabbitmq
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Terminal 1: SMS Service (urgent only)
python3 improved_sms_service.py

# Terminal 2: Push Service (shipped only)
python3 improved_push_service.py

# Terminal 3: Email Service (all orders)
python3 email_service.py

# Terminal 4: Producer
python3 topic_exchange_producer.py
```

**Expected output:**

```
# SMS Service (receives 2 urgent orders)
[SMS] Send SMS for urgent order 4
[SMS] Send SMS for urgent order 6

# Push Service (receives 2 shipped orders)
[Push] Send push: Order 3 shipped
[Push] Send push: Order 6 shipped

# Email Service (receives all 6 orders)
[Email] Send email for order 1
[Email] Send email for order 2
[Email] Send email for order 3
[Email] Send email for order 4
[Email] Send email for order 5
[Email] Send email for order 6
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Exchanges tab → Click on "order-events"
3. See topic exchange type
4. See bindings:
   - `order.*.high` → SMS Service
   - `order.shipped.*` → Push Service
   - `order.#` → Email Service
5. Efficient routing - no wasted messages!

**Comparison:**

| Design | Messages Received | Messages Wasted | Efficiency |
|--------|-------------------|------------------|-------------|
| Fanout (old) | 18 total (6 × 3 services) | 12 wasted | 33% |
| Topic (new) | 10 total (6 + 2 + 2) | 0 wasted | 100% |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Choose appropriate exchange type for use case
- Use descriptive exchange names
- Make exchanges durable in production
- Document routing key conventions
- Use topic exchange for flexible routing
- Monitor exchange message rates
- Test routing logic thoroughly
- Use consistent naming patterns

**❌ Don't:**
- Use wrong exchange type
- Forget to bind queues to exchanges
- Use headers exchange (unless absolutely necessary)
- Overcomplicate topic patterns
- Ignore unroutable messages
- Use fanout when direct/topic needed
- Forget to make exchanges durable
- Skip monitoring exchange metrics

### Exchange Selection Guide

```
Decision Tree:

1. Do all consumers need same message?
   YES → Fanout exchange
   NO  → Go to question 2

2. Is routing key exact match needed?
   YES → Direct exchange
   NO  → Go to question 3

3. Do you need pattern-based routing?
   YES → Topic exchange
   NO  → Direct exchange

4. Do you need header-based routing?
   YES → Headers exchange (rare)
   NO  → Topic exchange
```

### Production Considerations

**Exchange durability:**

```python
# Production: Always durable
channel.exchange_declare(
    exchange='logs',
    exchange_type='direct',
    durable=True  # Survives restart
)

# Development: Can be non-durable
channel.exchange_declare(
    exchange='test-logs',
    exchange_type='direct',
    durable=False
)
```

**Alternate exchanges for unroutable messages:**

```python
# Create alternate exchange (dead letter for unroutable)
channel.exchange_declare(exchange='unroutable', exchange_type='fanout')

# Create queue for unroutable messages
channel.queue_declare(queue='unroutable-queue')

# Bind alternate exchange to queue
channel.queue_bind(exchange='unroutable', queue='unroutable-queue')

# Declare main exchange with alternate exchange
channel.exchange_declare(
    exchange='main',
    exchange_type='direct',
    arguments={'alternate-exchange': 'unroutable'}
)

# Unroutable messages go to alternate exchange
```

**Monitoring exchange metrics:**

```bash
# Monitor message rates per exchange
rabbitmqctl list_bindings source messages_in_rate messages_out_rate

# Or use Management UI API
curl -u guest:guest http://localhost:15672/api/exchanges | \
  jq '.[] | {name: .name, message_stats: .message_stats}'
```

### Performance Considerations

**Exchange type performance (fastest to slowest):**

1. **Direct** - O(1) hash lookup (fastest)
2. **Fanout** - O(n) where n = number of queues (fast)
3. **Topic** - O(n) where n = number of bindings (slower)
4. **Headers** - O(n) where n = number of bindings (slowest)

**Optimizing topic exchanges:**

```python
# Avoid overly broad patterns
# BAD: # matches everything
channel.queue_bind(exchange='events', queue='queue', routing_key='#')

# GOOD: Specific patterns
channel.queue_bind(exchange='events', queue='queue', routing_key='user.*')

# Monitor binding count (too many = slow)
rabbitmqctl list_bindings source destination | wc -l
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's the difference between direct and topic exchanges?**

A: Direct exchange routes messages to queues with exact routing key match. Topic exchange routes using wildcard patterns (* and #) on routing keys. Direct is simpler and faster, topic is more flexible.

**Q2: When would you use a fanout exchange?**

A: Use fanout when you need to broadcast the same message to all consumers. Examples: notifications, cache invalidation, system events where every consumer needs every message.

**Q3: What happens if no queue matches the routing key?**

A: Message is discarded (unroutable). If mandatory flag is set, message is returned to publisher. Can use alternate exchange to catch unroutable messages.

**Q4: Can a queue bind to multiple exchanges?**

A: Yes, queue can have bindings to multiple exchanges with different routing keys. Queue receives messages matching any binding.

**Q5: What's the default exchange in RabbitMQ?**

A: The default exchange (empty string "") is a pre-declared direct exchange. Routing key = queue name. Used for simple point-to-point messaging.

### Production Pitfalls

**Pitfall 1: Wrong exchange type**
- Problem: Using fanout when topic needed
- Detection: All consumers receive all messages, wasted bandwidth
- Solution: Evaluate requirements, choose appropriate exchange type

**Pitfall 2: Typos in routing keys**
- Problem: Messages not routed to any queue
- Detection: Messages disappear, no consumers receive them
- Solution: Use constants for routing keys, test routing

**Pitfall 3: Forgetting to bind queues**
- Problem: Queue exists but not bound to exchange
- Detection: Messages published but not consumed
- Solution: Verify bindings in Management UI, automate binding creation

**Pitfall 4: Overusing # wildcard in topics**
- Problem: All consumers receive all messages
- Detection: High bandwidth, CPU usage, consumers overwhelmed
- Solution: Use specific patterns, avoid # unless necessary

### Advanced Exchange Concepts

**Exchange-to-exchange bindings:**

```python
# Chain exchanges for complex routing
channel.exchange_declare(exchange='ex1', exchange_type='direct')
channel.exchange_declare(exchange='ex2', exchange_type='topic')

# Bind ex2 to ex1
channel.exchange_bind(
    source='ex1',
    destination='ex2',
    routing_key='events'
)

# Messages to ex1 are routed through ex2
```

**Consistent hash exchange (plugin):**

```bash
# Enable consistent hash plugin
rabbitmq-plugins enable rabbitmq_consistent_hash_exchange

# Use for sticky routing (same routing key always to same queue)
```

**Lazy exchange (plugin):**

```bash
# Enable lazy exchange plugin
rabbitmq-plugins enable rabbitmq_lazy_exchange

# Queues are created lazily when first message arrives
# Saves resources when many queues
```

---

## 📚 Summary

Exchanges are the central routing component in RabbitMQ, determining where messages go based on exchange type and routing keys. Understanding exchange types (direct, fanout, topic, headers) is essential for building flexible, scalable messaging systems.

**Key takeaways:**
- Direct exchange: Exact routing key match (simple, fast)
- Fanout exchange: Broadcast to all queues (pub/sub pattern)
- Topic exchange: Pattern-based routing with wildcards (flexible, powerful)
- Headers exchange: Header-based routing (complex, rarely used)
- Choose exchange type based on requirements
- Document routing key conventions
- Monitor exchange metrics in production

**Next steps:**
- Practice with each exchange type
- Learn about queue properties and configuration
- Understand bindings in detail
- Explore virtual hosts for isolation
- Learn about users and permissions

---

**Module 01 - Core Concepts**  
**Lesson 01 - Complete**