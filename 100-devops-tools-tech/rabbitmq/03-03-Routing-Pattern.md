# 03-03: Routing Pattern

## 1️⃣ What Are Routing Patterns

**Routing Patterns** use RabbitMQ's topic exchange to route messages based on patterns in routing keys. This enables flexible, hierarchical message delivery without tight coupling between producers and consumers.

Think of routing patterns like email filters:

- **Messages** = Emails with subject lines
- **Topic Exchange** = Email server filtering
- **Routing Keys** = Email subject patterns (e.g., "orders.*")
- **Consumers** = Email folders (orders, support, sales)
- **Wildcards** = Pattern matching (e.g., "*.shipped", "orders.*")

**Where routing fits in RabbitMQ architecture:**

```
┌─────────────┐
│  Producer   │
└──────┬──────┘
       │
       │ Publishes message with routing key
       ▼
┌─────────────────────────────────────────────┐
│       Topic Exchange                 │
│  (Routes based on patterns)           │
│                                     │
│  ┌────────────────────────────────────┐   │
│  │ Routing Key: "orders.shipped"   │   │
│  │ Routing Key: "support.ticket"    │   │
│  │ Routing Key: "sales.inquiry"    │   │
│  │ Routing Key: "orders.*"        │   │
│  └────────────────────────────────────┘   │
└──────┬────────────────────────────────┬─┘
       │                               │
       ├─────────────────────┬───────────┤
       ▼                   ▼           ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│Consumer:     ││Consumer:     ││Consumer:     ││Consumer:     │
│Orders Folder ││Support Folder ││Sales Folder   ││Debug Folder  │
│             ││             ││             ││             │
│ Receives:    ││ Receives:    ││ Receives:    ││ Receives:    │
│ orders.*    ││ support.*    ││ sales.*     ││ * (ALL)     │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘
```

**Key concepts:**
- **Topic Exchange:** Routes based on routing key patterns (wildcards)
- **Routing Key:** Dot-separated words (e.g., "orders.shipped")
- **Wildcards:** `*` (match any word), `#` (match exactly one word)
- **Routing Patterns:** Hierarchical organization of topics
- **Flexible Routing:** Many consumers, many patterns
- **Decoupling:** Producer doesn't know about consumers

---

## 2️⃣ Problems Solved by Routing Patterns

### The "Hard-Coded Destinations" Problem

Without routing (direct exchanges):

- Producer must know about all destinations
- Adding new destination requires producer code change
- No flexibility in message routing
- Tight coupling between producer and consumers

**Real-world failure scenario:**

An order system had:

```
Producer → System (4 systems)
         ├─ Order Processing System
         ├─ Support Ticket System
         ├─ Sales Dashboard
         └─ Analytics System

Producer publishes: "New order"
Need to route to appropriate system

WITHOUT ROUTING (Direct):
├─ Producer knows about all 4 systems (tight coupling)
├─ Producer must check which system needs which message
├─ Producer sends to each system directly
└─ No way to broadcast to all

PROBLEMS:
├─ Adding new system requires producer code change
├─ Producer has logic for routing (not RabbitMQ)
├─ 4 separate network calls
├─ No broadcast capability
└─ System complexity (producer does routing)
```

**Problems:**
- Tight coupling (producer knows about all systems)
- Adding new system requires producer code change
- Producer implements routing logic (not RabbitMQ's job)
- Multiple network calls (inefficient)
- No broadcast capability
- **Impact:** High coupling, difficult to add systems, inefficient, complex producer logic

After implementing routing:
- Producer sends to topic exchange with routing key
- RabbitMQ routes to bound queues (consumers)
- Adding new system: Just bind new queue with routing key
- No producer code change needed
- **Result:** Decoupled, easy to add systems, RabbitMQ handles routing

### The "Scattered Message Distribution" Problem

Without pattern-based routing:

- Messages sent to many consumers based on content type
- No way to categorize and route efficiently
- Consumers receive messages they shouldn't process

**Example:**

```
Producer → System (3 consumer types)
         ├─ Order Processing (should receive "orders.*")
         ├─ Shipping Updates (should receive "orders.shipped")
         └─ Analytics (should receive "orders.*")

Producer publishes: 3 messages
├─ "New order" → Should go to Order Processing and Analytics
├─ "Order shipped" → Should go to Shipping Updates and Analytics
├─ "Order delivered" → Should go to Order Processing and Analytics

WITHOUT ROUTING (Fanout):
├─ All consumers receive ALL 3 messages (no filtering)
├─ Order Processing receives "Order shipped" (incorrect)
└─ Analytics receives irrelevant messages

PROBLEMS:
├─ Consumers receive irrelevant messages
├─ No content-based filtering
├─ Consumers must filter in application code
├─ Inefficient processing (filtering out irrelevant messages)
└─ **Impact:** Inefficient processing, irrelevant messages, consumer complexity
```

After implementing routing:
- Producer sends with routing key (e.g., "orders.shipped")
- Consumers bind to topic with patterns (e.g., "orders.shipped")
- RabbitMQ routes based on patterns (filtering built-in)
- Consumers receive only relevant messages
- **Result:** Efficient processing, no irrelevant messages, RabbitMQ handles filtering

---

## 3️⃣ When You Should Use Routing Patterns

### Development vs Production

**Development:**
- Can use fanout for simple tests
- Don't need complex routing for basic tests
- Use direct routing for targeted delivery
- Don't use in production code

**Production:**
- Absolutely required for hierarchical message organization
- Essential for content-based filtering (email types, log levels)
- Critical for multi-system routing (same message to different consumers)
- Required for decoupled producer-consumer communication
- Necessary for complex message routing scenarios

### Routing Pattern Scenarios

| Scenario | Routing Strategy | Example |
|----------|-----------------|----------|
| **Email routing** | Topic exchange | orders.*, support.*, sales.* |
| **Log aggregation** | Topic exchange | error.*, warn.*, info.*, debug.* |
| **Event streaming** | Topic exchange | events.*, notifications.*, alerts.* |
| **Multi-system routing** | Topic exchange | systemA.*, systemB.*, systemC.* |
| **Content-based routing** | Topic exchange | video.*, image.*, audio.* |

### Required vs Optional

**Required when:**
- Hierarchical message organization (categories, subcategories)
- Content-based filtering (email types, log levels, event types)
- Multi-system routing (same message to different consumers)
- Decoupled producer-consumer communication (producer doesn't know consumers)
- Complex message routing patterns
- High message volume with different consumer types

**Optional when:**
- Simple broadcast (all consumers receive same message) - use fanout
- Point-to-point communication - use direct exchange
- Single consumer - direct routing is sufficient
- Development and testing environments
- Low volume systems (few messages)

### Trade-offs

**Routing Patterns:**
✅ Hierarchical message organization  
✅ Content-based filtering (RabbitMQ handles routing)  
✅ Multi-consumer routing (same message to different consumers)  
✅ Decoupled producer-consumer (no producer routing logic)  
✅ Flexible patterns (wildcards, hierarchy)  
✅ Easy to add new consumers (just bind with pattern)  
❌ More complex routing (patterns, wildcards)  
❌ Performance overhead (routing key matching)  
❌ More exchange setup (topic exchange configuration)  
❌ Difficult to debug (pattern matching issues)  
❌ Consumer must understand routing keys  

**No Routing (Direct/Fanout):**
✅ Simpler setup (no patterns)  
✅ Lower performance overhead (no routing)  
✅ Easier to debug (no pattern matching)  
❌ No content-based filtering (all or nothing)  
❌ Tight coupling (producer must know consumers)  
❌ Adding consumers requires producer change  
❌ Producer implements routing logic  

---

## 4️⃣ How Routing Patterns Work

### Routing Configuration Process

**Setting up routing:**

```
1. Producer Creates Topic Exchange
   │
   ├─ Declares topic exchange
   └─ Ready to publish with routing keys
   │
2. Consumers Create Queues and Bind to Topic Exchange
   │
   ├─ Consumer 1 creates queue, binds with pattern "orders.*"
   ├─ Consumer 2 creates queue, binds with pattern "support.*"
   └─ Consumer 3 creates queue, binds with pattern "orders.shipped"
   │
3. Producer Publishes Messages with Routing Keys
   │
   ├─ Message 1: routing key = "orders.new" (matched by Consumer 1)
   ├─ Message 2: routing key = "support.ticket" (matched by Consumer 2)
   ├─ Message 3: routing key = "orders.shipped" (matched by Consumer 1 and 3)
   └─ Message 4: routing key = "sales.inquiry" (matched by new Consumer)
   │
4. RabbitMQ Routes Messages Based on Patterns
   │
   ├─ Topic exchange matches routing keys to bound queue patterns
   ├─ Message 1: "orders.new" → "orders.*" → Queue 1 (Consumer 1)
   ├─ Message 2: "support.ticket" → "support.*" → Queue 2 (Consumer 2)
   ├─ Message 3: "orders.shipped" → "orders.*" → Queue 1 (Consumer 1) and "orders.shipped" → Queue 3 (Consumer 3)
   └─ Message 4: "sales.inquiry" → "sales.*" → No match (new Consumer needed)
   │
5. Consumers Process Messages
   │
   ├─ Consumer 1 processes messages for "orders.*" and "orders.shipped"
   ├─ Consumer 2 processes messages for "support.*"
   └─ Consumer 3 processes messages for "orders.shipped"
```

### Topic Exchange Routing Mechanism

**How wildcards work:**

```
Routing Keys:
├─ "orders.new"
├─ "orders.shipped"
├─ "support.ticket"
├─ "support.chat"
└─ "sales.inquiry"

Queue Patterns:
├─ Consumer 1: "orders.*" (matches "orders.new" and "orders.shipped")
├─ Consumer 2: "support.*" (matches "support.ticket" and "support.chat")
├─ Consumer 3: "orders.shipped" (matches "orders.shipped" only)
└─ Consumer 4: "sales.*" (matches "sales.inquiry")

WILDCARDS:
├─ * (star) = match any word (e.g., "orders.*" matches "orders.new", "orders.shipped")
├─ # (hash) = match exactly one word (e.g., "#.*" matches "#.only")
└─ Multiple levels: "a.b.c.*" (hierarchical)

ROUTING: Messages routed to consumers with matching queue patterns
```

### Hierarchical Routing Keys

**Organization of topics:**

```
Topic Hierarchy:
├─ orders
│  ├─ orders.new
│  ├─ orders.shipped
│  ├─ orders.cancelled
│  └─ orders.*
├─ support
│  ├─ support.ticket
│  ├─ support.chat
│  ├─ support.email
│  └─ support.*
├─ sales
│  ├─ sales.inquiry
│  ├─ sales.quote
│  ├─ sales.order
│  └─ sales.*
└─ analytics
   ├─ analytics.orders
   ├─ analytics.sales
   ├─ analytics.support
   └─ analytics.*
```

---

## 5️⃣ Installation / Setup

**Routing patterns are built-in RabbitMQ features.** No installation required - just use topic exchanges and routing keys.

### Prerequisites

- RabbitMQ server running
- AMQP client library that supports topic exchanges
- Understanding of routing key patterns
- Understanding of wildcards (*, #)

### Creating Topic Exchange

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Declare topic exchange
channel.exchange_declare(
    exchange='routing_exchange',
    exchange_type='topic'  # CRITICAL: Topic for routing patterns
)

print("[✓] Topic exchange declared")
connection.close()
```

**Using rabbitmqctl:**

```bash
# Declare topic exchange
sudo rabbitmqctl add_exchange routing_exchange topic

# Delete exchange (cleanup)
sudo rabbitmqctl delete_exchange name=routing_exchange
```

### Creating Queues with Pattern Binding

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Declare topic exchange
channel.exchange_declare(
    exchange='routing_exchange',
    exchange_type='topic'
)

# CRITICAL: Create queue and bind with pattern
queue_name = channel.queue_declare(
    queue='orders_queue',
    durable=True
)

# CRITICAL: Bind queue to topic exchange with pattern
channel.queue_bind(
    exchange='routing_exchange',
    queue='orders_queue',
    routing_key='orders.*'  # CRITICAL: Pattern matching
)

print(f"[✓] Queue {queue_name} bound to routing_exchange with pattern orders.*")
connection.close()
```

### Publishing with Routing Key

**Python (Pika):**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Declare topic exchange
channel.exchange_declare(
    exchange='routing_exchange',
    exchange_type='topic'
)

# CRITICAL: Publish with routing key
message = {
    "order_id": "12345",
    "status": "shipped",
    "customer": "John Doe"
}

# CRITICAL: Publish with routing key (pattern matching)
channel.basic_publish(
    exchange='routing_exchange',
    routing_key='orders.shipped',  # CRITICAL: Routing key for pattern matching
    body=json.dumps(message)
)

print(f"[x] Published message with routing key: orders.shipped")
connection.close()
```

### Version Notes

- **RabbitMQ 3.12+:** All routing features fully supported
- **AMQP 0-9-1+:** Topic exchange protocol standard
- **Routing Keys:** Dot-separated words (e.g., "orders.shipped")
- **Wildcards:** `*` (any word), `#` (exactly one word)
- **Routing:** Topic exchange matches routing keys to queue patterns
- **Performance:** Overhead from pattern matching (minimal for simple patterns)

---

## 6️⃣ Where Routing Patterns Should Be Applied (With Example)

### Producer with Routing Keys

**Scenario:** Order system with multiple consumers

**Producer (routing_producer.py):**

```python
import pika
import json
import time

class RoutingProducer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        
        # CRITICAL: Create topic exchange
        self.channel.exchange_declare(
            exchange='routing_exchange',
            exchange_type='topic'
        )
    
    def publish_order(self, order_id, status):
        """Publish order with routing key"""
        order = {
            "order_id": order_id,
            "status": status,
            "timestamp": time.time()
        }
        
        # CRITICAL: Publish with routing key (pattern matching)
        routing_key = f"orders.{status}"
        
        self.channel.basic_publish(
            exchange='routing_exchange',
            routing_key=routing_key,
            body=json.dumps(order)
        )
        print(f"[x] Published order {order_id} with routing key: {routing_key}")
    
    def publish_support(self, ticket_id, status):
        """Publish support ticket with routing key"""
        ticket = {
            "ticket_id": ticket_id,
            "status": status,
            "timestamp": time.time()
        }
        
        # CRITICAL: Publish with routing key (pattern matching)
        routing_key = f"support.{status}"
        
        self.channel.basic_publish(
            exchange='routing_exchange',
            routing_key=routing_key,
            body=json.dumps(ticket)
        )
        print(f"[x] Published ticket {ticket_id} with routing key: {routing_key}")
    
    def close(self):
        self.connection.close()

# Usage
producer = RoutingProducer()

# Publish orders
producer.publish_order("12345", "new")
producer.publish_order("12346", "shipped")
producer.publish_order("12347", "delivered")

# Publish support tickets
producer.publish_support("TCK-001", "open")
producer.publish_support("TCK-002", "closed")

print("[✓] Published messages with routing keys (routing pattern)")
producer.close()
```

**Consumers with Pattern Binding**

**Consumer (orders_consumer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    """Process order message"""
    order = json.loads(body)
    
    print(f"[✓] Processed order: {order['order_id']} - {order['status']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Declare topic exchange
channel.exchange_declare(exchange='routing_exchange', exchange_type='topic')

# CRITICAL: Create queue and bind with pattern "orders.*"
queue_name = channel.queue_declare(
    queue='orders_queue',
    durable=True
)

# CRITICAL: Bind queue to topic exchange with pattern
channel.queue_bind(
    exchange='routing_exchange',
    queue=queue_name,
    routing_key='orders.*'  # CRITICAL: Pattern: matches "orders.new", "orders.shipped"
)

# CRITICAL: Manual acknowledgment
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False
)

print("[*] Orders consumer waiting (pattern: orders.*)")
channel.start_consuming()
```

**Consumer (support_consumer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    """Process support ticket message"""
    ticket = json.loads(body)
    
    print(f"[✓] Processed ticket: {ticket['ticket_id']} - {ticket['status']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Declare topic exchange
channel.exchange_declare(exchange='routing_exchange', exchange_type='topic')

# CRITICAL: Create queue and bind with pattern "support.*"
queue_name = channel.queue_declare(
    queue='support_queue',
    durable=True
)

# CRITICAL: Bind queue to topic exchange with pattern
channel.queue_bind(
    exchange='routing_exchange',
    queue=queue_name,
    routing_key='support.*'  # CRITICAL: Pattern: matches "support.ticket", "support.chat"
)

# CRITICAL: Manual acknowledgment
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False
)

print("[*] Support consumer waiting (pattern: support.*)")
channel.start_consuming()
```

**Consumer (shipping_consumer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    """Process shipping notification"""
    order = json.loads(body)
    
    print(f"[✓] Shipping notification: {order['order_id']} - {order['status']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Declare topic exchange
channel.exchange_declare(exchange='routing_exchange', exchange_type='topic')

# CRITICAL: Create queue and bind with pattern "orders.shipped"
queue_name = channel.queue_declare(
    queue='shipping_queue',
    durable=True
)

# CRITICAL: Bind queue to topic exchange with pattern
channel.queue_bind(
    exchange='routing_exchange',
    queue=queue_name,
    routing_key='orders.shipped'  # CRITICAL: Exact match (no wildcard)
)

# CRITICAL: Manual acknowledgment
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False
)

print("[*] Shipping consumer waiting (pattern: orders.shipped)")
channel.start_consuming()
```

**How to test routing:**

```bash
# Terminal 1: Orders consumer
python3 orders_consumer.py

# Terminal 2: Support consumer
python3 support_consumer.py

# Terminal 3: Shipping consumer
python3 shipping_consumer.py

# Terminal 4: Producer
python3 routing_producer.py
```

**Expected output:**

```
# Producer
[x] Published order 12345 with routing key: orders.new
[x] Published order 12346 with routing key: orders.shipped
[x] Published order 12347 with routing key: orders.delivered
[x] Published ticket TCK-001 with routing key: support.open
[x] Published ticket TCK-002 with routing key: support.closed
[✓] Published messages with routing keys (routing pattern)

# Orders consumer (pattern: orders.*)
[*] Orders consumer waiting (pattern: orders.*)
[x] Received order: 12345 - new
[✓] Processed order: 12345 - new
[x] Received order: 12346 - shipped
[✓] Processed order: 12346 - shipped
[x] Received order: 12347 - delivered
[✓] Processed order: 12347 - delivered

# Support consumer (pattern: support.*)
[*] Support consumer waiting (pattern: support.*)
[x] Received ticket: TCK-001 - open
[✓] Processed ticket: TCK-001 - open
[x] Received ticket: TCK-002 - closed
[✓] Processed ticket: TCK-002 - closed

# Shipping consumer (pattern: orders.shipped)
[*] Shipping consumer waiting (pattern: orders.shipped)
[x] Received order: 12346 - shipped
[✓] Shipping notification: 12346 - shipped
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Exchanges tab → See "routing_exchange" (topic)
3. Go to Queues tab → See 3 queues (orders, support, shipping)
4. See bindings with patterns (orders.*, support.*, orders.shipped)
5. Monitor message routing (RabbitMQ matches patterns)

### Best Practices

**Routing Configuration:**
✅ Use topic exchange for pattern-based routing  
✅ Design routing keys hierarchically (categories.subcategories)  
✅ Use wildcards (*) for pattern matching  
✅ Use exact match (no wildcard) for specific routing  
✅ Keep patterns simple and performant  
✅ Document routing key conventions  
✅ Use durable queues (survival across restarts)  

**Producer Configuration:**
✅ Use routing keys for content-based routing  
✅ Follow routing key hierarchy (categories.subcategories)  
✅ Keep routing keys consistent and meaningful  
✅ Don't embed business logic in routing keys  
✅ Use separate routing keys for different message types  

**Consumer Configuration:**
✅ Bind queues with appropriate patterns  
✅ Use specific patterns (orders.*) for specific consumers  
✅ Use exact patterns (orders.shipped) for specific routing  
✅ Use wildcards (*) only when necessary  
✅ Use manual_ack for message reliability  
✅ Monitor consumer message rates  

### Common Mistakes

❌ Using fanout instead of topic exchange → No pattern-based routing  
❌ Not understanding wildcards → Routing confusion  
❌ Using too complex patterns → Performance degradation  
❌ Embedding business logic in routing keys → Tight coupling  
❌ Not documenting routing key conventions → Confusion  
❌ Using exact match when wildcard needed → No routing flexibility  
❌ Not monitoring consumer message rates → Routing issues not visible  
❌ Mixing routing patterns → Confusion, difficult debugging  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Hard-Coded Routing (The "Producer Knows All Consumers" Problem)**

You're building an order system:

- Producer sends order updates to multiple systems
- Producer must know about all systems (tight coupling)
- No way to route based on order status
- Adding new system requires producer code change

Current implementation:
- Producer knows about all systems
- Producer sends messages directly to each system
- No pattern-based routing
- Tight coupling between producer and consumers

**Problems:**
- Producer implements routing logic (not RabbitMQ's job)
- Adding new system requires producer code change
- No content-based filtering (all or nothing)
- Multiple network calls (inefficient)
- **Impact:** High coupling, difficult to add systems, inefficient, complex producer logic

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

**Step 2: Create producer without routing**

Create `no_routing_producer.py`:

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: Direct routing (no pattern matching)
channel.queue_declare(queue='orders_queue')
channel.queue_declare(queue='support_queue')
channel.queue_declare(queue='shipping_queue')

# PROBLEM: Producer sends to each queue directly
def send_order(queue, order):
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(order)
    )

orders = []
for i in range(10):
    order = {
        "order_id": f"order_{i+1:04d}",
        "status": "new",
        "timestamp": time.time()
    }
    
    # PROBLEM: Must know about all systems
    send_order('orders_queue', order)
    if i % 3 == 0:
        send_order('support_queue', {"ticket_id": f"TCK-{i+1:04d}"})
    else:
        send_order('shipping_queue', order)
    
    print(f"[x] Sent order {order['order_id']} to queue: {queue if i % 3 == 0 else 'shipping_queue'}")

print(f"[✓] Sent messages (PROBLEM: No routing - hard-coded destinations)")
connection.close()
```

**Step 3: Create consumers without routing**

Create `no_routing_consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f"[✓] Processed: {message}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: Direct queues (no pattern matching)
channel.queue_declare(queue='orders_queue')
channel.queue_declare(queue='support_queue')
channel.queue_declare(queue='shipping_queue')

# PROBLEM: Consume from specific queue
if sys.argv[1] == 'orders':
    queue_name = 'orders_queue'
elif sys.argv[1] == 'support':
    queue_name = 'support_queue'
else:
    queue_name = 'shipping_queue'

channel.basic_consume(queue=queue_name, on_message_callback=callback)

print(f"[*] Consumer for queue: {queue_name}")
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal 1: Orders consumer
python3 no_routing_consumer.py orders

# Terminal 2: Support consumer
python3 no_routing_consumer.py support

# Terminal 3: Shipping consumer
python3 no_routing_consumer.py shipping

# Terminal 4: Producer
python3 no_routing_producer.py
```

**Expected observation:**
- Producer sends messages to queues directly (no routing keys)
- Each consumer receives messages from its queue only
- No content-based filtering (orders consumer doesn't know about shipped orders)
- Producer must know about all systems (tight coupling)
- **Impact:** High coupling, inefficient, no content-based routing

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Exchanges tab → No topic exchange (direct)
- Go to Queues tab → See 3 queues (orders, support, shipping)
- No pattern-based routing visible

### ✅ Solution & Explanation

**Solution: Implement Routing Patterns (Topic Exchange)**

**Create routing producer (routing_producer.py):**

```python
import pika
import json
import time

class RoutingProducer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        
        # SOLUTION: Create topic exchange
        self.channel.exchange_declare(
            exchange='routing_exchange',
            exchange_type='topic'
        )
    
    def publish_order(self, order_id, status):
        """SOLUTION: Publish order with routing key"""
        order = {
            "order_id": order_id,
            "status": status,
            "timestamp": time.time()
        }
        
        # SOLUTION: Publish with routing key (pattern matching)
        routing_key = f"orders.{status}"
        
        self.channel.basic_publish(
            exchange='routing_exchange',
            routing_key=routing_key,
            body=json.dumps(order)
        )
        print(f"[x] Published order {order_id} with routing key: {routing_key}")
    
    def publish_support(self, ticket_id, status):
        """SOLUTION: Publish support ticket with routing key"""
        ticket = {
            "ticket_id": ticket_id,
            "status": status,
            "timestamp": time.time()
        }
        
        # SOLUTION: Publish with routing key (pattern matching)
        routing_key = f"support.{status}"
        
        self.channel.basic_publish(
            exchange='routing_exchange',
            routing_key=routing_key,
            body=json.dumps(ticket)
        )
        print(f"[x] Published ticket {ticket_id} with routing key: {routing_key}")
    
    def close(self):
        self.connection.close()

# SOLUTION: Routing pattern-based publishing
producer = RoutingProducer()

# Publish orders
producer.publish_order("12345", "new")
producer.publish_order("12346", "shipped")
producer.publish_order("12347", "delivered")

# Publish support tickets
producer.publish_support("TCK-001", "open")
producer.publish_support("TCK-002", "closed")

print("[✓] Published messages with routing keys (routing pattern)")
producer.close()
```

**Create consumers with pattern binding**

**Consumer (orders_consumer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    """SOLUTION: Process order message"""
    order = json.loads(body)
    
    print(f"[✓] Processed order: {order['order_id']} - {order['status']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Declare topic exchange
channel.exchange_declare(exchange='routing_exchange', exchange_type='topic')

# SOLUTION: Create queue and bind with pattern "orders.*"
queue_name = channel.queue_declare(
    queue='orders_queue',
    durable=True
)

# SOLUTION: Bind queue to topic exchange with pattern
channel.queue_bind(
    exchange='routing_exchange',
    queue=queue_name,
    routing_key='orders.*'  # SOLUTION: Pattern: matches "orders.new", "orders.shipped"
)

# SOLUTION: Manual acknowledgment
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False
)

print("[*] Orders consumer waiting (pattern: orders.*)")
channel.start_consuming()
```

**Consumer (support_consumer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    """SOLUTION: Process support ticket message"""
    ticket = json.loads(body)
    
    print(f"[✓] Processed ticket: {ticket['ticket_id']} - {ticket['status']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Declare topic exchange
channel.exchange_declare(exchange='routing_exchange', exchange_type='topic')

# SOLUTION: Create queue and bind with pattern "support.*"
queue_name = channel.queue_declare(
    queue='support_queue',
    durable=True
)

# SOLUTION: Bind queue to topic exchange with pattern
channel.queue_bind(
    exchange='routing_exchange',
    queue=queue_name,
    routing_key='support.*'  # SOLUTION: Pattern: matches "support.ticket", "support.chat"
)

# SOLUTION: Manual acknowledgment
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False
)

print("[*] Support consumer waiting (pattern: support.*)")
channel.start_consuming()
```

**Consumer (shipping_consumer.py):**

```python
import pika
import json

def callback(ch, method, properties, body):
    """SOLUTION: Process shipping notification"""
    order = json.loads(body)
    
    print(f"[✓] Shipping notification: {order['order_id']} - {order['status']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Declare topic exchange
channel.exchange_declare(exchange='routing_exchange', exchange_type='topic')

# SOLUTION: Create queue and bind with pattern "orders.shipped"
queue_name = channel.queue_declare(
    queue='shipping_queue',
    durable=True
)

# SOLUTION: Bind queue to topic exchange with pattern
channel.queue_bind(
    exchange='routing_exchange',
    queue=queue_name,
    routing_key='orders.shipped'  # SOLUTION: Exact match (no wildcard)
)

# SOLUTION: Manual acknowledgment
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False
)

print("[*] Shipping consumer waiting (pattern: orders.shipped)")
channel.start_consuming()
```

**How to verify:**

```bash
# Clear RabbitMQ
docker stop rabbitmq && docker rm rabbitmq
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Terminal 1: Orders consumer
python3 orders_consumer.py

# Terminal 2: Support consumer
python3 support_consumer.py

# Terminal 3: Shipping consumer
python3 shipping_consumer.py

# Terminal 4: Producer
python3 routing_producer.py
```

**Expected output:**

```
# Producer
[x] Published order 12345 with routing key: orders.new
[x] Published order 12346 with routing key: orders.shipped
[x] Published order 12347 with routing key: orders.delivered
[x] Published ticket TCK-001 with routing key: support.open
[x] Published ticket TCK-002 with routing key: support.closed
[✓] Published messages with routing keys (routing pattern)

# Orders consumer (pattern: orders.*)
[*] Orders consumer waiting (pattern: orders.*)
[x] Received order: 12345 - new
[✓] Processed order: 12345 - new
[x] Received order: 12346 - shipped
[✓] Processed order: 12346 - shipped
[x] Received order: 12347 - delivered
[✓] Processed order: 12347 - delivered

# Support consumer (pattern: support.*)
[*] Support consumer waiting (pattern: support.*)
[x] Received ticket: TCK-001 - open
[✓] Processed ticket: TCK-001 - open
[x] Received ticket: TCK-002 - closed
[✓] Processed ticket: TCK-002 - closed

# Shipping consumer (pattern: orders.shipped)
[*] Shipping consumer waiting (pattern: orders.shipped)
[x] Received order: 12346 - shipped
[✓] Shipping notification: 12346 - shipped
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Exchanges tab → See "routing_exchange" (topic)
3. Go to Queues tab → See 3 queues (orders, support, shipping)
4. See bindings with patterns (orders.*, support.*, orders.shipped)
5. Monitor message routing (RabbitMQ matches patterns to queues)

**Comparison:**

| Design | Content Routing | Producer Coupling | Adding Consumer |
|--------|-----------------|-----------------|-----------------|
| No Routing (old) | No | High (knows all) | Requires producer change |
| Routing (new) | Yes | Low (decoupled) | Just bind (no change) |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Use topic exchange for pattern-based routing  
- Design routing keys hierarchically (categories.subcategories)  
- Use wildcards (*) for pattern matching  
- Use exact match (no wildcard) for specific routing  
- Keep patterns simple and performant  
- Document routing key conventions  
- Use durable queues (survival across restarts)  

**❌ Don't:**
- Using fanout instead of topic exchange → No pattern-based routing  
- Not understanding wildcards → Routing confusion  
- Using too complex patterns → Performance degradation  
- Embedding business logic in routing keys → Tight coupling  
- Not documenting routing key conventions → Confusion  
- Using exact match when wildcard needed → No routing flexibility  
- Not monitoring consumer message rates → Routing issues not visible  
- Mixing routing patterns → Confusion, difficult debugging  

### Routing Guidelines

```
Routing Key Conventions:
├─ Use dot-separated words: category.subcategory.action
├─ Example: orders.new, orders.shipped, support.ticket
└─ Keep it consistent and meaningful

Wildcards:
├─ * (star): match any word (e.g., "orders.*")
├─ # (hash): match exactly one word (e.g., "#.*")
└─ Don't use multiple levels for simple routing

Pattern Complexity:
├─ Simple: "orders.*" (good performance)
├─ Complex: "orders.*.*.*" (poor performance)
└─ Balance flexibility vs performance

Consumer Management:
├─ Bind queues with specific patterns
├─ Use wildcards only when necessary
├─ Monitor consumer message rates
└─ Alert on unexpected routing patterns
```

### Production Considerations

**Monitoring Routing Patterns:**

```python
# Monitor topic exchange routing
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Get exchange info (requires RabbitMQ management plugin)
print("[MONITOR] Topic exchange: routing_exchange")
# See Management UI for bindings and message rates

connection.close()
```

**Routing Performance Tuning:**

```bash
# RabbitMQ configuration for routing performance
# /etc/rabbitmq/rabbitmq.conf

# Reduce routing cache size (default: 4)
routing_key_cache_size = 256

# Increase max connections for topic exchanges
channel_max = 2048
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's the difference between topic and fanout exchanges?**

A: Topic exchange routes messages based on routing key patterns (wildcard matching). Fanout exchange broadcasts messages to ALL bound queues (no filtering). Topic = pattern-based filtering (only matching patterns get messages); Fanout = all get messages.

**Q2: How do wildcards work in routing keys?**

A: `*` (star) matches zero or more words in routing key. `#` (hash) matches exactly one word. Multiple levels possible (e.g., "a.b.c.*"). Used for pattern matching in topic exchanges.

**Q3: What's the right routing key structure?**

A: Use dot-separated words (e.g., "orders.shipped", "support.ticket"). Hierarchical organization for categories, subcategories, and actions. Keep it consistent and meaningful across all messages.

**Q4: How do you add a new consumer to routing pattern?**

A: Create a new queue, bind it to the topic exchange with the desired routing key pattern (e.g., "orders.*"), and start consuming. No producer code change required (decoupled).

**Q5: What's the performance impact of complex routing patterns?**

A: Complex routing patterns (multiple levels like "a.b.c.*") can degrade performance due to pattern matching overhead. Keep patterns simple and specific (e.g., "orders.*") for better performance.

### Production Pitfalls

**Pitfall 1: Not using topic exchange for routing**
- Problem: No pattern-based routing, producer knows all destinations
- Detection: High coupling, difficult to add consumers
- Solution: Use topic exchange with routing keys and wildcards

**Pitfall 2: Not understanding wildcards**
- Problem: Routing confusion, unexpected message distribution
- Detection: Messages routed to wrong consumers
- Solution: Learn wildcard behavior (* matches any word, # matches exactly one)

**Pitfall 3: Using too complex patterns**
- Problem: Performance degradation, difficult debugging
- Detection: Slow message processing, high CPU
- Solution: Keep patterns simple and specific

**Pitfall 4: Embedding business logic in routing keys**
- Problem: Tight coupling, difficult to change routing
- Detection: Routing keys contain business logic, hard to modify
- Solution: Use hierarchical routing keys, not business logic

**Pitfall 5: Not monitoring consumer message rates**
- Problem: Routing issues not visible, unexpected message distribution
- Detection: Messages routed to wrong consumers, processing delays
- Solution: Monitor consumer message rates, alert on unexpected patterns

### Advanced Routing Concepts

**Multiple Topic Exchanges:**

```python
# Separate topic exchanges for different categories
channel.exchange_declare(
    exchange='orders_exchange',
    exchange_type='topic'
)
channel.exchange_declare(
    exchange='support_exchange',
    exchange_type='topic'
)
channel.exchange_declare(
    exchange='notifications_exchange',
    exchange_type='topic'
)
```

**Advanced Wildcard Patterns:**

```python
# Hierarchical routing keys
channel.queue_bind(
    exchange='orders_exchange',
    queue='orders_new_queue',
    routing_key='orders.new'
)
channel.queue_bind(
    exchange='orders_exchange',
    queue='orders_shipped_queue',
    routing_key='orders.shipped'
)
channel.queue_bind(
    exchange='support_exchange',
    queue='support_ticket_queue',
    routing_key='support.ticket'
)
channel.queue_bind(
    exchange='notifications_exchange',
    queue='notifications_all_queue',
    routing_key='#'  # All notifications
)
```

---

## 📚 Summary

Routing patterns use topic exchanges and routing keys to route messages based on patterns. This provides flexible, hierarchical message organization with content-based filtering and decoupled producer-consumer communication.

**Key takeaways:**
- Use topic exchange for pattern-based routing
- Use routing keys with dot-separated hierarchy
- Use wildcards (*) for pattern matching
- Keep patterns simple and performant
- Document routing key conventions
- Producer decoupled from consumers
- Easy to add new consumers (just bind with pattern)
- RabbitMQ handles routing (no producer routing logic)

**Next steps:**
- Practice with routing patterns in your applications
- Learn about RPC pattern (request-response)
- Learn about Competing Consumers pattern
- Learn about Request/Reply pattern
- Explore architectural patterns (shovel, federation)

---

**Module 03 - Message Patterns and Architectures**  
**Lesson 03 - Complete**