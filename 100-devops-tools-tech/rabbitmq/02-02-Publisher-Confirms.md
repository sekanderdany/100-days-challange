# 02-02: Publisher Confirms

## 1️⃣ What Are Publisher Confirms

**Publisher confirms** are acknowledgments from RabbitMQ back to the producer to confirm that a message was successfully received by the broker and (optionally) routed to appropriate queue(s). They provide publisher-side reliability, ensuring messages don't disappear between producer and RabbitMQ.

Think of publisher confirms like certified mail receipts:

- **Message** = A package sent by sender
- **Publisher Confirm** = The courier's receipt that package reached post office
- **Consumer ACK** = The recipient's signature for package
- **Publisher Confirm** = Courier confirms package reached sorting center (before consumer)

**Where publisher confirms fit in RabbitMQ architecture:**

```
┌─────────────┐
│  Producer   │
└──────┬──────┘
       │
       │ Publishes message
       │ Waits for confirm
       ▼
┌─────────────────────────────────────────────┐
│     RabbitMQ (Broker)               │
│                                      │
│  1. Receives message               │
│  2. Routes to queue(s)             │
│  3. Sends confirm to producer ✓      │
└─────────────────────────────────────────────┘
       │
       │ Confirm received
       ▼
┌─────────────┐
│  Producer   │
└─────────────┘
```

**Key concepts:**
- **Confirm:** Positive acknowledgment from broker (message received)
- **Return:** Unroutable message returned to publisher (no matching queue)
- **Publish Mode:** Synchronous (wait for confirm) vs Asynchronous (callback)
- **Correlation ID:** Links confirm to original message
- **Publishing Errors:** Network failures, broker unreachable

---

## 2️⃣ Problems Solved by Publisher Confirms

### The "Silent Drop" Problem

Without publisher confirms:

- Producer publishes message
- No indication if message reached RabbitMQ
- Network failure or broker down = message lost
- Producer assumes success but message never arrived

**Real-world failure scenario:**

An order submission system had:

```
Producer → (Network Failure) → RabbitMQ
                              ✗ Message never reaches broker
                              But producer thinks success!
```

**Problems:**
- 5% of orders lost during network issues
- No way to detect lost orders
- Customers think they submitted successfully
- Database shows order submitted but never processed
- **Impact:** $50K in lost revenue, 200 disputed orders, customer trust damage

After implementing publisher confirms:
- Publisher waits for broker confirmation
- Network failure detected immediately
- Producer can retry or alert user
- No silent drops
- **Result:** 100% order reliability, zero lost orders

### The "Partial Success" Problem

Without publisher confirms on clustering:

- Publisher publishes to cluster
- Message reaches some nodes but not all
- No indication of partial delivery
- Queue inconsistency across cluster

**Example:**

```
Producer → Cluster
              ├─ Node A: Message received ✓
              ├─ Node B: Message received ✓
              └─ Node C: Network failure, message lost ✗
              No confirm from Node C
```

**Problems:**
- Queue inconsistency (some messages missing)
- Hard to detect which node failed
- No way to guarantee all-or-nothing delivery
- Manual intervention required to reconcile
- **Impact:** Queue desync, data inconsistency, manual reconciliation needed

After implementing publisher confirms with mandatory flag:
- Unroutable messages returned to publisher
- Partial failures detected immediately
- Producer can retry or handle failures
- Consistent state across cluster
- **Result:** Immediate detection, retry possible, consistent state

---

## 3️⃣ When You Should Use Publisher Confirms

### Development vs Production

**Development:**
- Don't need publisher confirms for quick testing
- Can publish without waiting (faster iteration)
- OK to lose messages in throwaway code
- Don't use in production code

**Production:**
- Absolutely required for critical data (orders, payments)
- Essential for high-value messages
- Critical for legal/compliance requirements
- Required when message loss is unacceptable

### Publisher Confirms vs Consumer ACKs

| Feature | Publisher Confirms | Consumer ACKs |
|---------|-------------------|---------------|
| **Direction** | RabbitMQ → Producer | Consumer → RabbitMQ |
| **Purpose** | Message received by broker | Message processed by consumer |
| **Use Case** | Critical data, network reliability | Task completion, processing reliability |
| **When** | Immediately after publish | After processing completes |

### Required vs Optional

**Required when:**
- Processing critical data (orders, payments, financial transactions)
- Message loss unacceptable
- Network reliability concerns
- Clustering or distributed deployments
- Legal or compliance requirements
- At-least-once delivery needed to broker

**Optional when:**
- Fire-and-forget messages (notifications, logs)
- Non-critical data (telemetry, heartbeats)
- Idempotent operations (can safely reprocess)
- High throughput requirements (confirm latency overhead)
- Development and testing environments

### Trade-offs

**Publisher Confirms:**
✅ Guarantees message reaches broker  
✅ Detects network failures immediately  
✅ Enables retry logic for failed publishes  
✅ Consistent state in clusters  
✅ Audit trail for all messages  
❌ Adds latency (must wait for confirm)  
❌ More complex code  
❌ Higher CPU usage (confirms)  
❌ Slower throughput (synchronous or callback overhead)  

**No Publisher Confirms:**
✅ Faster (no wait for confirm)  
✅ Simpler code  
✅ Higher throughput  
✅ Lower CPU usage  
❌ No guarantee message reaches broker  
❌ Silent failures (producer unaware)  
❌ Network issues cause data loss  
❌ No retry capability without custom logic  

---

## 4️⃣ How Publisher Confirms Work

### Publisher Confirm Process Flow

**Basic confirm flow:**

```
1. Publisher Enables Confirms
   │
   ├─ Channel confirms enabled
   ├─ Ready for publishing
   └─ Can be sync or async mode
   │
2. Publisher Publishes Message
   │
   ├─ Sends message to RabbitMQ
   ├─ Correlation ID (optional) for tracking
   └─ Publish mode (sync/async)
   │
3. RabbitMQ Processes Message
   │
   ├─ Receives message from producer
   ├─ Routes to queue(s) based on bindings
   ├─ Writes to disk (if persistent)
   └─ Sends confirm back to producer
   │
4. Publisher Receives Confirm
   │
   ├─ Confirmation received
   ├─ Correlation ID matches (if used)
   ├─ Publisher marks message as confirmed
   └─ Can continue or retry
```

### Confirm Types

**Synchronous Confirms (wait for each confirm):**

```python
# Enable confirms
channel.confirm_delivery()

# Publish and wait
channel.basic_publish(exchange='', routing_key='queue', body='message')
if channel.wait_for_confirms(timeout=5):
    print("[✓] Message confirmed")
else:
    print("[✗] Confirm timeout")
```

**Asynchronous Confirms (callback-based):**

```python
# Enable confirms
channel.confirm_delivery()

# Set callback
def confirm_callback(method_frame, properties_frame, body):
    # Called for each confirm
    confirm_tag = method_frame.method.confirm_tag
    multiple = method_frame.method.multiple  # Batch confirm
    if multiple:
        print(f"[✓] Multiple messages confirmed: {confirm_tag}")
    else:
        print(f"[✓] Single message confirmed: {confirm_tag}")

channel.add_confirm_callback(confirm_callback)

# Publish without waiting
for i in range(10):
    channel.basic_publish(exchange='', routing_key='queue', body=f'message_{i}')
print("Published 10 messages, waiting for confirms...")
```

**Returns (unroutable messages):**

```python
# Set mandatory flag
channel.basic_publish(
    exchange='',
    routing_key='nonexistent',
    body='message',
    mandatory=True  # Return if unroutable
)

# Handle returned messages
def return_callback(method_frame, properties_frame, body):
    print(f"[✗] Message returned: {body.decode()}")
    # Message didn't route to any queue

channel.add_on_return_callback(return_callback)
```

### Unconfirmed Messages State

**Publisher state with unconfirmed messages:**

```
Publisher State:
├─ Total published: 1000
├─ Confirmed: 950
└─ Unconfirmed: 50 (waiting for broker confirm)

Unconfirmed Messages:
└─ Message IDs 1-50
   └─ In flight (sent but not yet confirmed)
```

**Unconfirmed messages:**
- Sent to RabbitMQ but not yet confirmed
- Still in flight (may be confirmed later)
- Max limit controlled by window size
- If timeout, considered failed

---

## 5️⃣ Installation / Setup

**Publisher confirms are built-in AMQP feature.** No installation required - just enable per channel.

### Prerequisites

- RabbitMQ server running
- AMQP client library that supports publisher confirms
- Understanding of publish vs confirm

### Enabling Publisher Confirms

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Enable publisher confirms (CRITICAL for reliability)
channel.confirm_delivery()

print("[✓] Publisher confirms enabled on channel")
connection.close()
```

**Node.js (amqplib):**

```javascript
const amqp = require('amqplib/callback_api');

const connection = amqp.connect('amqp://localhost');
const channel = connection.createChannel();

// Enable publisher confirms
channel.confirmSelect();

console.log('[✓] Publisher confirms enabled');
```

**Java (RabbitMQ Java Client):**

```java
import com.rabbitmq.client.*;

ConnectionFactory factory = new ConnectionFactory();
factory.setHost("localhost");
Connection connection = factory.newConnection();
Channel channel = connection.createChannel();

// Enable publisher confirms
channel.confirmSelect();

System.out.println("[✓] Publisher confirms enabled");
```

### Synchronous vs Asynchronous Confirms

**Synchronous (wait_for_confirms):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Enable confirms
channel.confirm_delivery()

# Publish message (no routing key = default exchange)
channel.basic_publish(
    exchange='',
    routing_key='orders',
    body='order_data'
)

# Wait for confirmation (BLOCKING)
if channel.wait_for_confirms(timeout=5):
    print("[✓] Message confirmed successfully")
else:
    print("[✗] Confirm timeout or negative ack")
    # Retry logic here
```

**Asynchronous (add_confirm_callback):**

```python
import pika

# Track unconfirmed messages
unconfirmed = {}

def confirm_callback(method_frame, properties_frame, body):
    # Called for each confirmation
    confirm_tag = method_frame.method.confirm_tag
    multiple = method_frame.method.multiple
    ack = method_frame.method.ack  # True = ack, False = nack
    
    if multiple:
        # Batch confirm (multiple messages confirmed at once)
        for tag in range(confirm_tag, method_frame.method.confirm_tag + 1):
            if tag in unconfirmed:
                message = unconfirmed.pop(tag)
                print(f"[✓] Confirmed message {tag}: {message}")
    else:
        # Single confirm
        if confirm_tag in unconfirmed:
            message = unconfirmed.pop(confirm_tag)
            print(f"[✓] Confirmed message {confirm_tag}: {message}")
    
    if not ack:
        # Negative confirm (message rejected)
        print(f"[✗] Message {confirm_tag} rejected (nack)")

def nack_callback(method_frame, header_frame, body):
    # Called when message is rejected
    confirm_tag = method_frame.method.confirm_tag
    if confirm_tag in unconfirmed:
        message = unconfirmed.pop(confirm_tag)
        print(f"[✗] NACK for message {confirm_tag}: {message}")

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Enable confirms
channel.confirm_delivery()

# Add callbacks
channel.add_confirm_callback(confirm_callback)
channel.add_on_return_callback(nack_callback)

# Set publish confirms callback
channel.confirm_select()

# Publish messages (NON-BLOCKING)
for i in range(10):
    message = f"Order {i+1}"
    unconfirmed[i] = message
    
    # Publish (don't specify confirm_tag, auto-generated)
    channel.basic_publish(
        exchange='',
        routing_key='orders',
        body=message
    )
    print(f"[x] Published message {i+1}")

print(f"[x] Published 10 messages, {len(unconfirmed)} unconfirmed")
print("[x] Waiting for confirms...")

# Keep channel open for callbacks
try:
    while unconfirmed:
        # Wait for all confirms
        import time
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n[*] Interrupted")
finally:
    connection.close()
```

### Version Notes

- **RabbitMQ 3.12+:** All publisher confirm features fully supported
- **AMQP 0-9-1+:** Confirms protocol standard
- **Performance:** Async confirms faster than sync
- **Window size:** Controls number of unconfirmed messages
- **Mandatory flag:** Required for unroutable message detection

---

## 6️⃣ Where Publisher Confirms Should Be Applied (With Example)

### Producer with Confirms

**Scenario:** Order submission system that must guarantee every order reaches RabbitMQ

**Producer (confirmed_order_publisher.py):**

```python
import pika
import json
import time

class OrderPublisher:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        
        # CRITICAL: Enable publisher confirms
        self.channel.confirm_delivery()
        
        # Track unconfirmed messages
        self.unconfirmed = {}
        self.confirm_counter = 0
        
        # Add callbacks
        self.channel.add_confirm_callback(self.on_confirm)
        self.channel.add_on_return_callback(self.on_return)
        
    def on_confirm(self, method_frame, properties_frame, body):
        """Called when message confirmed"""
        confirm_tag = method_frame.method.confirm_tag
        multiple = method_frame.method.multiple
        ack = method_frame.method.ack
        
        if multiple:
            # Batch confirm
            for tag in range(confirm_tag, method_frame.method.confirm_tag + 1):
                if tag in self.unconfirmed:
                    order = self.unconfirmed.pop(tag)
                    print(f"[✓] Confirmed order {tag}: {order}")
                    self.confirm_counter += 1
        else:
            # Single confirm
            if confirm_tag in self.unconfirmed:
                order = self.unconfirmed.pop(confirm_tag)
                print(f"[✓] Confirmed order {confirm_tag}: {order}")
                self.confirm_counter += 1
        
        if not ack:
            print(f"[✗] NACK for order {confirm_tag}")
    
    def on_return(self, method_frame, properties_frame, body):
        """Called when message is unroutable"""
        reply_code = method_frame.method.reply_code
        confirm_tag = method_frame.method.confirm_tag
        
        if confirm_tag in self.unconfirmed:
            order = self.unconfirmed.pop(confirm_tag)
            print(f"[✗] RETURNED order {confirm_tag}: {order.decode()} (code: {reply_code})")
    
    def publish_order(self, order_data):
        """Publish order and track"""
        message = json.dumps(order_data)
        
        # Generate unique confirm_tag (or let RabbitMQ generate)
        # Store message for tracking
        confirm_tag = self.confirm_counter
        self.unconfirmed[confirm_tag] = order_data
        
        # Publish (don't specify confirm_tag for auto-generation)
        self.channel.basic_publish(
            exchange='',
            routing_key='orders',
            body=message,
            mandatory=True  # Required for unroutable detection
        )
        print(f"[x] Published order {order_data['order_id']} (confirm_tag={confirm_tag})")
        
        return confirm_tag
    
    def wait_for_confirms(self, timeout=5):
        """Wait for all pending confirms"""
        start = time.time()
        while self.unconfirmed and (time.time() - start) < timeout:
            # Wait for confirms (async callback will process)
            import time
            time.sleep(0.01)
        
        remaining = len(self.unconfirmed)
        if remaining > 0:
            print(f"[⚠]  Timeout! {remaining} messages unconfirmed")
        else:
            print(f"[✓] All {self.confirm_counter} orders confirmed")
        
        return len(self.unconfirmed) == 0
    
    def close(self):
        self.connection.close()

# Usage
publisher = OrderPublisher()

orders = []
for i in range(10):
    orders.append({
        "order_id": f"order_{i+1:03d}",
        "customer_id": 12345 + i,
        "amount": (i+1) * 99.99,
        "timestamp": time.time()
    })

# Publish all orders
for order in orders:
    publisher.publish_order(order)

# Wait for all confirms (wait up to 5 seconds)
publisher.wait_for_confirms(timeout=5)

publisher.close()
```

**Expected output:**

```
[x] Published order order_001 (confirm_tag=0)
[x] Published order order_002 (confirm_tag=1)
...
[x] Published order order_010 (confirm_tag=9)
[✓] Confirmed order 0: {'order_id': 'order_001', ...}
[✓] Confirmed order 1: {'order_id': 'order_002', ...}
...
[✓] All 10 orders confirmed
```

### Best Practices

**Publisher Implementation:**
✅ Always enable confirms for critical data  
✅ Use mandatory flag to detect unroutable messages  
✅ Track unconfirmed messages with correlation ID  
✅ Implement retry logic for failed publishes  
✅ Use async confirms for higher throughput  
✅ Set reasonable timeout for wait_for_confirms  
✅ Log confirmation failures  
✅ Handle returns (unroutable messages)  

**Publishing Strategy:**
✅ Batch publishes (reduce overhead)  
✅ Use persistent messages for critical data  
✅ Use separate channels for publishers  
✅ Monitor confirm rate and latency  
✅ Alert on high unconfirmed count  
✅ Implement circuit breaker for continuous failures  

### Common Mistakes

❌ Not enabling confirms → Messages lost silently  
❌ Forgetting mandatory flag → Unroutable messages lost  
❌ Using sync confirms for high throughput → Performance bottleneck  
❌ Not handling returns → Unroutable messages lost  
❌ Not tracking unconfirmed messages → Can't retry failures  
❌ Setting confirm timeout too short → False negatives  
❌ Not handling negative acknowledges (nack) → Retry wrong messages  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Silent Message Loss (The "I Thought It Succeeded" Problem)**

You're building an order submission system:

- Producer receives order from web API
- Producer publishes order to RabbitMQ
- RabbitMQ routes to order processing queue
- Order processing system consumes and processes orders

Current implementation doesn't use publisher confirms:
- Producer publishes immediately
- No way to know if message reached RabbitMQ
- Network issues or RabbitMQ downtime = order lost
- But producer tells API "Success" immediately

**Problems:**
- 3% of orders lost during network issues (estimated)
- Customers think they submitted successfully
- No way to detect or recover lost orders
- Queue shows orders missing (but no notification)
- **Impact:** $30K in lost revenue per year, 1,500 disputed orders, customer trust damage

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

**Step 2: Create unreliable producer (no confirms)**

Create `unreliable_producer.py`:

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: No publisher confirms
# Producer has no way to know if message reached RabbitMQ

channel.queue_declare(queue='orders')

# Simulate network issues
def simulate_publish(producer, order):
    try:
        producer.channel.basic_publish(
            exchange='',
            routing_key='orders',
            body=json.dumps(order)
        )
        return True
    except Exception as e:
        print(f"[!] Publish failed: {e}")
        return False

for i in range(20):
    order = {
        "order_id": f"order_{i+1:03d}",
        "customer_id": 12345,
        "amount": (i+1) * 49.99,
        "timestamp": time.time()
    }
    
    # PROBLEM: Simulate 10% network failure rate
    if random.random() < 0.1:  # 10% of orders
        print(f"[!] SIMULATED NETWORK FAILURE for order {order['order_id']}")
        # Producer doesn't know message lost!
    
    simulate_publish(connection, order)
    print(f"[x] Published order {order['order_id']} (PROBLEM: No confirm)")

print(f"[!] Published 20 orders (PROBLEM: Some may have been lost)")
print(f"[!] Producer has no way to know which messages reached RabbitMQ")

connection.close()
```

**Step 3: Create consumer to verify**

Create `order_consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    order = json.loads(body)
    print(f"[✓] Consumer received order: {order['order_id']} ${order['amount']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='orders')
channel.basic_consume(queue='orders', on_message_callback=callback)

print("[*] Consumer waiting for orders...")
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal 1: Consumer
python3 order_consumer.py

# Terminal 2: Producer (simulate network issues)
python3 unreleliable_producer.py
```

**Expected observation:**
- Producer publishes 20 orders
- ~10% fail with simulated network issues (producer sees error)
- ~90% succeed (producer doesn't know if they reach RabbitMQ)
- Consumer may receive only 15-18 orders (network failures)
- No way to tell which orders were lost
- Producer returns "success" to API for all 20 orders
- **Impact:** 2-5 orders actually lost, producer unaware

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Queues tab → Click on "orders"
- See message rate (may not match publisher)
- Can't tell which messages were successfully sent
- No visibility into publisher failures

### ✅ Solution & Explanation

**Solution: Implement Publisher Confirms**

**Create reliable producer (reliable_producer.py):**

```python
import pika
import json
import time

class ReliableOrderPublisher:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        
        # SOLUTION: Enable publisher confirms
        self.channel.confirm_delivery()
        
        # Track unconfirmed messages
        self.unconfirmed = {}
        self.confirm_counter = 0
        self.success_count = 0
        self.failure_count = 0
        
        # SOLUTION: Add callbacks
        self.channel.add_confirm_callback(self.on_confirm)
        self.channel.add_on_return_callback(self.on_return)
    
    def on_confirm(self, method_frame, properties_frame, body):
        """SOLUTION: Called when message confirmed"""
        confirm_tag = method_frame.method.confirm_tag
        multiple = method_frame.method.multiple
        ack = method_frame.method.ack
        
        if multiple:
            # Batch confirm
            for tag in range(confirm_tag, method_frame.method.confirm_tag + 1):
                if tag in self.unconfirmed:
                    order = self.unconfirmed.pop(tag)
                    print(f"[✓] CONFIRMED order {tag}: {order['order_id']}")
                    self.success_count += 1
        else:
            # Single confirm
            if confirm_tag in self.unconfirmed:
                order = self.unconfirmed.pop(confirm_tag)
                print(f"[✓] CONFIRMED order {confirm_tag}: {order['order_id']}")
                self.success_count += 1
        
        if not ack:
            print(f"[✗] NACK for order {confirm_tag}")
            self.failure_count += 1
    
    def on_return(self, method_frame, properties_frame, body):
        """SOLUTION: Called when message is unroutable"""
        reply_code = method_frame.method.reply_code
        confirm_tag = method_frame.method.confirm_tag
        
        if confirm_tag in self.unconfirmed:
            order = self.unconfirmed.pop(confirm_tag)
            print(f"[✗] RETURNED order {confirm_tag}: {order['order_id']} (unroutable - code: {reply_code})")
            self.failure_count += 1
    
    def publish_order(self, order_data, mandatory=True):
        """SOLUTION: Publish order with confirms"""
        message = json.dumps(order_data)
        
        # SOLUTION: Generate unique confirm_tag
        confirm_tag = self.confirm_counter
        self.unconfirmed[confirm_tag] = order_data
        
        # SOLUTION: Publish with mandatory flag (required for returns)
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key='orders',
                body=message,
                mandatory=mandatory  # SOLUTION: Detect unroutable messages
            )
            print(f"[x] PUBLISHED order {order_data['order_id']} (confirm_tag={confirm_tag})")
            self.confirm_counter += 1
            return True
        except Exception as e:
            print(f"[!] Publish failed: {e}")
            if confirm_tag in self.unconfirmed:
                del self.unconfirmed[confirm_tag]
            return False
    
    def wait_for_all_confirms(self, timeout=10):
        """SOLUTION: Wait for all pending confirms"""
        print(f"[*] Waiting for all {len(self.unconfirmed)} confirms...")
        start = time.time()
        
        while self.unconfirmed and (time.time() - start) < timeout:
            # Wait for callbacks (async)
            import time
            time.sleep(0.01)
        
        remaining = len(self.unconfirmed)
        if remaining > 0:
            print(f"[⚠]  TIMEOUT! {remaining} messages unconfirmed after {timeout}s")
            print(f"[⚠]  Unconfirmed order tags: {list(self.unconfirmed.keys())}")
        else:
            print(f"[✓] ALL {self.success_count} orders CONFIRMED successfully")
            print(f"[✓] Success rate: {self.success_count}/{self.success_count + self.failure_count}")
        
        return len(self.unconfirmed) == 0
    
    def close(self):
        self.connection.close()

# SOLUTION: Use reliable producer
publisher = ReliableOrderPublisher()

# Publish orders
orders = []
for i in range(20):
    orders.append({
        "order_id": f"order_{i+1:03d}",
        "customer_id": 12345 + i,
        "amount": (i+1) * 49.99,
        "timestamp": time.time()
    })

print("[*] Publishing 20 orders with publisher confirms...")
for order in orders:
    publisher.publish_order(order, mandatory=True)

print(f"[*] Published 20 orders")
print(f"[*] {len(publisher.unconfirmed)} orders unconfirmed, waiting for broker confirms...")

# SOLUTION: Wait for all confirms (with timeout)
all_confirmed = publisher.wait_for_all_confirms(timeout=10)

print(f"[*] All confirms received, closing publisher")
publisher.close()
```

**How to verify:**

```bash
# Clear RabbitMQ
docker stop rabbitmq && docker rm rabbitmq
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Terminal 1: Consumer
python3 order_consumer.py

# Terminal 2: Reliable producer
python3 reliable_producer.py
```

**Expected output:**

```
# Producer
[*] Publishing 20 orders with publisher confirms...
[x] PUBLISHED order order_001 (confirm_tag=0)
[x] PUBLISHED order order_002 (confirm_tag=1)
...
[x] PUBLISHED order order_020 (confirm_tag=19)
[*] 20 orders unconfirmed, waiting for broker confirms...
[*] Waiting for all 20 confirms...
[✓] CONFIRMED order 0: order_001
[✓] CONFIRMED order 1: order_002
...
[✓] CONFIRMED order 19: order_020
[✓] ALL 20 orders CONFIRMED successfully
[✓] Success rate: 20/20 (100%)

# Consumer
[✓] Consumer received order: order_001 $49.99
[✓] Consumer received order: order_002 $99.98
...
[✓] Consumer received order: order_020 $999.80
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Queues tab → Click on "orders"
3. See all 20 messages delivered
4. Go to Channels tab → See confirm rate
5. View confirms in real-time

**Comparison:**

| Design | Reliability | Detectability | Message Loss | Implementation |
|--------|-------------|---------------|--------------|----------------|
| No Confirms | None | Impossible | ~3% | Simple |
| With Confirms | High | Immediate | 0% (with retry) | More complex |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Always use publisher confirms for critical data  
- Use mandatory flag to detect unroutable messages  
- Track unconfirmed messages with correlation ID  
- Implement retry logic with exponential backoff  
- Use async confirms for higher throughput  
- Set appropriate timeout for wait_for_confirms  
- Monitor confirm rate and latency  
- Log confirmation failures and returns  
- Use separate channels for publishers  

**❌ Don't:**
- Forget to enable confirms → Messages lost silently  
- Not using mandatory flag → Unroutable messages lost  
- Using sync confirms for high throughput → Performance bottleneck  
- Not handling returns → Unroutable messages lost  
- Not tracking unconfirmed messages → Can't retry failures  
- Setting confirm timeout too short → False negatives  
- Ignoring negative acknowledges (nack) → Retry wrong messages  
- Publishing faster than broker can confirm → Channel stall  

### Confirm Patterns

**Individual Confirms (one message):**

```python
# Confirm each message individually
for i in range(100):
    channel.basic_publish(exchange='', routing_key='queue', body=f'message_{i}')
    # Wait for confirm before next
    channel.wait_for_confirms(timeout=5)
```

**Batch Confirms (multiple messages):**

```python
# Publish all, then confirm batch
for i in range(100):
    channel.basic_publish(exchange='', routing_key='queue', body=f'message_{i}')

# Wait for all confirms (batch)
channel.wait_for_confirms(timeout=30)
```

**Async Confirms (callback-based):**

```python
# Publish without waiting, let callbacks handle confirms
for i in range(100):
    channel.basic_publish(exchange='', routing_key='queue', body=f'message_{i}')

# Keep channel open for async callbacks
time.sleep(5)  # Let async callbacks process
```

### Production Considerations

**Confirm Window Size:**

```python
# Controls how many messages can be unconfirmed
# Larger window = higher throughput but more memory usage
# Smaller window = lower throughput but better resource usage

channel.basic_qos(prefetch_count=1)
# Confirms are separate from consumer prefetch
```

**Retry Logic:**

```python
def publish_with_retry(channel, exchange, routing_key, body, max_retries=3):
    """Publish with retry logic"""
    for attempt in range(max_retries):
        try:
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body,
                mandatory=True
            )
            if channel.wait_for_confirms(timeout=5):
                return True  # Success
        except Exception as e:
            print(f"[!] Publish attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return False  # All retries failed
```

**Monitoring Confirms:**

```python
# Confirm-specific metrics
total_published = 0
total_confirmed = 0
total_failed = 0

def on_confirm(method_frame, properties_frame, body):
    global total_confirmed
    total_confirmed += 1
    print(f"Confirm rate: {total_confirmed}/{total_published}")

def on_return(method_frame, properties_frame, body):
    global total_failed
    total_failed += 1
    print(f"Failure rate: {total_failed}/{total_published}")
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's the difference between publisher confirms and consumer ACKs?**

A: Publisher confirms are from RabbitMQ to producer indicating message reached the broker. Consumer ACKs are from consumer to RabbitMQ indicating message was processed. Publisher confirms ensure message delivery to broker, consumer ACKs ensure message processing.

**Q2: When should you use publisher confirms vs just publishing?**

A: Use publisher confirms when message delivery to broker must be guaranteed (critical data like orders, payments). Don't use confirms for fire-and-forget messages (logs, notifications) where some loss is acceptable and throughput is priority.

**Q3: What happens if a publish times out waiting for confirm?**

A: The wait_for_confirms call returns false and a TimeoutError is raised. The message's fate is unknown - it may have been confirmed after timeout or may have been lost. Should implement retry logic with timeout handling.

**Q4: What's the mandatory flag and when should you use it?**

A: The mandatory flag makes RabbitMQ return unroutable messages to the publisher (via on_return_callback) instead of silently dropping them. Use when you need to detect and handle messages that don't route to any queue.

**Q5: How do you handle high-volume publishing with confirms?**

A: Use asynchronous confirms (add_confirm_callback) instead of synchronous wait_for_confirms. Track unconfirmed messages in a buffer and process confirms via callbacks. Set appropriate confirm window size.

### Production Pitfalls

**Pitfall 1: Forgetting to enable confirms**
- Problem: Messages lost silently on network issues
- Detection: Discovered through data loss
- Solution: Always enable confirms for critical messages

**Pitfall 2: Not handling returns (mandatory flag)**
- Problem: Unroutable messages lost without detection
- Detection: No way to know messages didn't route
- Solution: Always set mandatory=True for critical messages, add on_return_callback

**Pitfall 3: Using synchronous confirms for high throughput**
- Problem: Performance bottleneck (must wait for each confirm)
- Detection: Low throughput, channel stalls
- Solution: Use async confirms (add_confirm_callback) for high volume

**Pitfall 4: Not implementing retry logic**
- Problem: Confirm failures result in permanent message loss
- Detection: Messages lost after one publish attempt
- Solution: Implement retry with exponential backoff

### Advanced Confirm Concepts

**Negative Acknowledgments (NACK):**

```python
# RabbitMQ can negative ack (nack) a publish
# This indicates message couldn't be processed by broker
# Different from consumer NACK which requeues message
```

**Confirms with Transactions (atomic):**

```python
# Confirms work within transactions
channel.tx_select()

# Multiple publishes (atomic - all or none)
channel.basic_publish(exchange='', routing_key='orders', body='order_1')
channel.basic_publish(exchange='', routing_key='orders', body='order_2')

# Commit transaction (confirms all at once)
channel.tx_commit()

# Wait for all confirms
channel.wait_for_confirms(timeout=5)
```

**Correlation ID Pattern:**

```python
# Link confirm to original message
import uuid

correlation_id = str(uuid.uuid4())

channel.basic_publish(
    exchange='',
    routing_key='orders',
    body=order_data,
    properties=pika.BasicProperties(
        correlation_id=correlation_id  # Track original message
    )
)

# In confirm callback, correlation_id helps match confirm to message
```

---

## 📚 Summary

Publisher confirms provide producer-side reliability by ensuring messages reach RabbitMQ broker. Combined with consumer ACKs and proper error handling, they guarantee end-to-end message reliability in RabbitMQ systems.

**Key takeaways:**
- Publisher confirms guarantee message reaches broker
- Use mandatory flag to detect unroutable messages
- Synchronous confirms (wait_for_confirms) simpler but slower
- Asynchronous confirms (callbacks) faster but more complex
- Track unconfirmed messages for retry logic
- Implement retry with exponential backoff
- Monitor confirm rate and latency
- Use confirms for critical data (orders, payments)

**Next steps:**
- Practice with publisher confirms (sync and async)
- Learn about Dead Letter Exchanges (DLX) for failed messages
- Understand message TTL and expiration
- Learn about message durability and persistence
- Explore transactionality and atomic operations

---

**Module 02 - Advanced RabbitMQ Features**  
**Lesson 02 - Complete**