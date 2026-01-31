# 02-04: Message TTL and Expiration

## 1️⃣ What Are Message TTL and Expiration

**Message TTL (Time-To-Live)** is a timeout that causes RabbitMQ to automatically expire (delete) messages after a specified period of time. **Expiration** is when a message reaches the end of its TTL and is removed from the queue.

Think of TTL like expiration dates on products:

- **Message** = A product on a shelf
- **TTL** = The expiration date (e.g., "expires in 7 days")
- **Expiration** = When the date is reached (product removed)
- **DLX** = Returns section for expired products
- **Consumer** = Customers who must buy before expiration

**Where TTL and Expiration fit in RabbitMQ architecture:**

```
┌─────────────┐
│  Producer   │
└──────┬──────┘
       │
       │ Publishes message WITH TTL
       ▼
┌─────────────────────────────────────────────┐
│           Queue                         │
│  (Buffer messages with expiration)      │
│                                      │
│  ┌──────────────┬──────────────┬─────────┐│
│  │ Message 1    │ Message 2    │ Message 3││
│  │ (5 min TTL)   │ (5 min TTL)   │ (5 min TTL)││
│  │ Time starts→│ Time starts→│ Time starts→││
│  │ 5 min later │ 5 min later │ 5 min later││
│  │ EXPIRED ✗  │ Still fresh  │ Still fresh ││
│  └──────────────┴──────────────┴─────────┘│
└─────────────────────────────────────────────┘
       │
       │ Expired messages routed to DLX (if configured)
       ▼
┌─────────────────────────────┐
│       Dead Letter Queue (DLQ)  │
│    (Stores expired messages)  │
└─────────────────────────────────────┘
```

**Key concepts:**
- **Message TTL:** Time (in milliseconds) until message expiration
- **Queue TTL:** Time until entire queue is deleted (if unused)
- **Expiration:** When message reaches end of TTL and is removed
- **DLX Routing:** Expired messages can be routed to DLX
- **Per-Message TTL:** Different messages can have different TTLs

---

## 2️⃣ Problems Solved by Message TTL and Expiration

### The "Stale Data" Problem

Without TTL:

- Messages accumulate in queue indefinitely
- Consumers process outdated information
- No automatic cleanup of old messages
- Queue grows without bound

**Real-world failure scenario:**

A notification system had:

```
Producer → Queue → Notification Consumer
                    │
                    ├─ Push notification "Order shipped!"
                    ├─ Push notification "Order delivered!"
                    └─ Push notification "Order completed!"

PROBLEM: If consumer is down for 24 hours:
├─ All notifications accumulate in queue
├─ When consumer restarts, it sends ALL notifications
├─ "Order shipped!" notification sent 24 hours late
├─ Customer frustrated by delayed notification
└─ User has already received package (useless notification)
```

**Problems:**
- Customers receive notifications 24+ hours late
- Irrelevant notifications sent (customer already received package)
- Queue grows with stale messages
- Consumer overwhelmed with backlog on restart
- **Impact:** Poor customer experience, wasted resources, notification fatigue

After implementing TTL:
- Notifications expire after 1 hour
- Stale notifications automatically removed
- Consumer doesn't send old messages
- Customers receive timely, relevant notifications
- Queue stays clean
- **Result:** Improved customer experience, reduced load

### The "Message Pollution" Problem

Without TTL on temporary data:

- Temporary status messages (session tokens, short-lived data) never expire
- Queue polluted with expired messages
- Consumers waste time processing expired messages
- No way to automatically clean up temporary messages

**Example:**

```
Producer → Queue → Consumer
         │
         ├─ Message: "Session token valid for 1 hour" (should expire)
         ├─ Message: "One-time password reset" (should expire)
         ├─ Message: "Discount code expires in 24 hours" (should expire)
         └─ Message: "Temporary access granted" (should expire)

PROBLEM: All messages stay in queue forever
Consumer processes "Session token valid for 1 hour" 5 hours later → Confusing!
Consumer processes "One-time password reset" 2 days later → Already used!
Consumer processes "Discount code" 1 week later → Already expired!
```

**Problems:**
- Confusing user experience (expired tokens still accepted)
- Security issue (expired credentials still valid)
- Resources wasted on processing expired messages
- No way to clean up temporary data
- **Impact:** Security vulnerabilities, wasted processing, poor UX

After implementing TTL:
- Messages automatically expire after TTL
- Expired messages routed to DLQ (for analysis)
- Consumers only process fresh messages
- Queue stays clean
- Security improved (expired tokens invalid)
- **Result:** Enhanced security, better UX, reduced waste

---

## 3️⃣ When You Should Use Message TTL and Expiration

### Development vs Production

**Development:**
- Optional for testing message flow
- Useful for simulating time-based processing
- Don't need TTL for simple tests
- Use short TTLs for quick cleanup

**Production:**
- Absolutely required for temporary data
- Essential for time-sensitive messages (notifications, discounts)
- Critical for security (session tokens, passwords)
- Important for resource management (queue cleanup)
- Required for data freshness (real-time updates)

### TTL Usage Scenarios

| Scenario | TTL Strategy | Example |
|----------|---------------|---------|
| **Short-lived notifications** | 5-30 min TTL | Order shipped, delivered |
| **Session tokens** | 1 hour TTL | Authentication tokens |
| **Discount codes** | 24 hours TTL | Promotional codes |
| **Status updates** | 1 min TTL | Real-time updates |
| **Temporary access** | 5 min TTL | Grant access codes |

### Required vs Optional

**Required when:**
- Processing temporary data (session tokens, passwords, OTPs)
- Time-sensitive messages (notifications, discounts, real-time updates)
- Security requirements (credentials must expire)
- Resource management (automatic queue cleanup)
- Data freshness requirements (real-time information)

**Optional when:**
- Permanent data (configuration, user profiles)
- Long-lived messages (logs, archives)
- Fire-and-forget messages (telemetry, metrics)
- Idempotent operations (message can be reprocessed any time)
- Development and testing environments

### Trade-offs

**Message TTL:**
✅ Automatic message cleanup  
✅ Data freshness guaranteed  
✅ Security improved (credentials expire)  
✅ Resources saved (don't process stale messages)  
✅ Consumer not overwhelmed with backlog  
✅ Queue stays clean and bounded  
❌ Messages lost after expiration (must be DLQ tracked)  
❌ Complex error handling (expired messages)  
❌ Additional DLX infrastructure required  
❌ TTL calculation required (in milliseconds)  
❌ Different messages have different TTLs  

**No TTL:**
✅ Simpler architecture  
✅ Messages never expire  
✅ No DLX needed  
✅ Processing can happen anytime  
❌ Queue grows without bound  
❌ Stale data processed  
❌ Security issues (old credentials valid)  
❌ Resources wasted on stale messages  
❌ Poor user experience (late notifications)  

---

## 4️⃣ How Message TTL and Expiration Work

### TTL Configuration Process

**Setting up TTL:**

```
1. Producer Sets TTL on Message
   │
   ├─ Message published with TTL (milliseconds)
   ├─ TTL can be per-message or per-queue
   └─ RabbitMQ tracks message age
   │
2. RabbitMQ Tracks Message Age
   │
   ├─ Message received in queue
   ├─ Timer starts (based on TTL)
   └─ Message marked as "fresh"
   │
3. Message Age Reaches TTL
   │
   ├─ Timer expires
   ├─ Message marked as "expired"
   └─ Expiration event triggered
   │
4. Message Removal
   │
   ├─ Message removed from queue
   ├─ NOT delivered to any consumer
   └─ Optional: Routed to DLX
   │
5. Expiration Handling
   │
   ├─ If DLX configured: Route to DLQ
   ├─ If no DLX: Message permanently lost
   └─ DLQ Consumer can analyze expired messages
```

### TTL Types

**Per-Message TTL (via properties):**

```python
# Set TTL on individual message
channel.basic_publish(
    exchange='',
    routing_key='orders',
    body=order_data,
    properties=pika.BasicProperties(
        expiration='3600000'  # 1 hour (in milliseconds)
    )
)
```

**Per-Queue TTL (via arguments):**

```python
# Set TTL on entire queue
channel.queue_declare(
    queue='orders',
    arguments={
        'x-message-ttl': '3600000'  # 1 hour (in milliseconds)
    }
)
```

### Message Expiration Flow

**When messages expire:**

```
Queue: orders (Message TTL: 5 min)

Message Flow:
┌─────────────────────────────────────────────────┐
│ Producer                                  │
└──────┬──────────────────────────────────────┘
       │
       │ Publish 3 orders WITH TTL (5 min)
       ▼
┌─────────────────────────────────────────┐
│      Orders Queue                    │
│ (Messages expire after 5 min)   │
│                                      │
│  ┌──────────────┬──────────────┬───────┐│
│  │ Order 1     │ Order 2     │ Order 3││
│  │ (5 min TTL)  │ (5 min TTL)  │ (5 min TTL)││
│  │ Time starts→│ Time starts→│ Time starts→││
│  │ 5 min later │ 5 min later │ 5 min later││
│  │ EXPIRED ✗  │ Still fresh  │ Still fresh ││
│  └──────────────┴──────────────┴─────────┘│
└─────────────────────────────────────────┘
       │
       │ Expired messages routed to DLX (if configured)
       ▼
┌─────────────────────────────┐
│       Dead Letter Queue (DLQ)  │
│    (Stores expired messages)  │
└─────────────────────────────────────┘
```

### TTL Value Considerations

**TTL Unit:**

```
TTL in RABBITMQ = milliseconds
                    │
        ┌───────────┼───────────┐
        │           │           │
        ↓           ↓           ↓
        1 second  1 minute    1 hour
      = 1000 ms = 60000 ms = 3600000 ms

Common TTLs:
├─ 1 minute      = 60000 ms     (Session tokens)
├─ 5 minutes     = 300000 ms    (Notifications)
├─ 15 minutes    = 900000 ms    (Status updates)
├─ 1 hour        = 3600000 ms   (Discount codes)
├─ 24 hours      = 86400000 ms  (Daily data)
└─ 7 days        = 604800000 ms (Weekly reports)
```

---

## 5️⃣ Installation / Setup

**Message TTL and Expiration are built-in RabbitMQ features.** No installation required - just set TTL on messages or queues.

### Prerequisites

- RabbitMQ server running
- AMQP client library installed
- Understanding of time requirements (in milliseconds)

### Setting Per-Message TTL

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='notifications')

# Publish message with TTL
channel.basic_publish(
    exchange='',
    routing_key='notifications',
    body='Order shipped!',
    properties=pika.BasicProperties(
        expiration='300000'  # 5 minutes (in milliseconds)
    )
)

print('[✓] Published notification with 5 min TTL')
connection.close()
```

**Node.js (amqplib):**

```javascript
const amqp = require('amqplib/callback_api');

const connection = amqp.connect('amqp://localhost');
const channel = connection.createChannel();

channel.assertQueue('notifications');

// Publish with TTL (expiration in milliseconds)
channel.sendToQueue('notifications', Buffer.from('Order shipped!'), {
    expiration: '300000'  // 5 minutes
});

console.log('[✓] Published notification with 5 min TTL');
```

**Java (RabbitMQ Java Client):**

```java
import com.rabbitmq.client.*;
import java.util.concurrent.TimeUnit;

ConnectionFactory factory = new ConnectionFactory();
factory.setHost("localhost");
Connection connection = factory.newConnection();
Channel channel = connection.createChannel();

channel.queueDeclare("notifications", false, false, null, null);

// Publish with TTL (expiration in milliseconds)
AMQP.BasicProperties.Builder props = new AMQP.BasicProperties.Builder()
    .expiration("300000");  // 5 minutes

channel.basicPublish("", "notifications", props.build(), "Order shipped!");

System.out.println("[✓] Published notification with 5 min TTL");
```

### Setting Per-Queue TTL

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare queue with TTL
channel.queue_declare(
    queue='notifications',
    arguments={
        'x-message-ttl': '60000'  # 1 minute (in milliseconds)
    }
)

print('[✓] Queue declared with 1 min TTL')
connection.close()
```

**Using rabbitmqctl:**

```bash
# Declare queue with TTL (using policy)
sudo rabbitmqctl set_policy TTL \
  "^notifications" \
  '{"message-ttl":60000}' \
  --apply-to queues

# Delete TTL policy
sudo rabbitmqctl delete_policy name=TTL
```

### Setting Per-Queue + DLX (Expired messages to DLQ)

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Create DLX and DLQ
channel.exchange_declare(exchange='notification-dlx', exchange_type='direct')
channel.queue_declare(queue='expired-notifications')
channel.queue_bind(exchange='notification-dlx', queue='expired-notifications', routing_key='expired')

# Declare main queue with TTL and DLX
channel.queue_declare(
    queue='notifications',
    arguments={
        'x-message-ttl': '60000',  # 1 minute TTL
        'x-dead-letter-exchange': 'notification-dlx',  # DLX
        'x-dead-letter-routing-key': 'expired'  # Routing key
    }
)

print('[✓] Queue with TTL and DLX configured')
connection.close()
```

### Version Notes

- **RabbitMQ 3.12+:** All TTL and expiration features fully supported
- **AMQP 0-9-1+:** TTL protocol standard
- **TTL Unit:** Milliseconds (not seconds!)
- **Per-Message vs Per-Queue:** Can set both (per-message takes priority)
- **DLX Integration:** Expired messages can be routed to DLX

---

## 6️⃣ Where Message TTL and Expiration Should Be Applied (With Example)

### Producer with Per-Message TTL

**Scenario:** Notification system that sends time-sensitive notifications

**Producer (ttl_producer.py):**

```python
import pika
import json
import time

class NotificationProducer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='notifications')
    
    def send_notification(self, message, ttl_seconds):
        """Send notification with TTL"""
        # Convert seconds to milliseconds
        ttl_ms = ttl_seconds * 1000
        
        # CRITICAL: Set TTL per message
        self.channel.basic_publish(
            exchange='',
            routing_key='notifications',
            body=message,
            properties=pika.BasicProperties(
                expiration=str(ttl_ms)  # TTL in milliseconds
            )
        )
        print(f"[x] Sent notification: {message[:30]}... (TTL: {ttl_seconds}s)")
    
    def close(self):
        self.connection.close()

# Usage
producer = NotificationProducer()

notifications = [
    ("Order shipped!", 300),      # 5 minutes
    ("Order delivered!", 300),    # 5 minutes
    ("Payment received!", 300),  # 5 minutes
    ("Order completed!", 300),    # 5 minutes
    ("Session expires in 10 min", 600),  # 10 minutes
    ("Password reset expires in 1 hour", 3600),  # 1 hour
]

for message, ttl in notifications:
    producer.send_notification(message, ttl)

producer.close()
```

**Expected output:**

```
[x] Sent notification: Order shipped!... (TTL: 300s)
[x] Sent notification: Order delivered!... (TTL: 300s)
[x] Sent notification: Payment received!... (TTL: 300s)
[x] Sent notification: Order completed!... (TTL: 300s)
[x] Sent notification: Session expires in 10 min... (TTL: 600s)
[x] Sent notification: Password reset expires in 1 hour... (TTL: 3600s)
```

### Consumer Handling of TTL (No DLX)

**Consumer (ttl_consumer.py):**

```python
import pika
import time

def callback(ch, method, properties, body):
    """Process notification (may be expired)"""
    message = body.decode()
    
    # Check if message has expiration
    if properties.expiration:
        ttl_ms = int(properties.expiration)
        age_ms = int(time.time() * 1000) - int(properties.timestamp * 1000)
        
        # Check if message is expired
        if age_ms > ttl_ms:
            print(f"[!] EXPIRED: {message} (age: {age_ms}ms > TTL: {ttl_ms}ms)")
            # Don't process expired message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
    
    # Process fresh message
    print(f"[✓] Processing: {message}")
    time.sleep(0.5)  # Simulate processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='notifications')
channel.basic_consume(queue='notifications', on_message_callback=callback)

print('[*] Consumer waiting (will skip expired messages)')
channel.start_consuming()
```

### Best Practices

**TTL Configuration:**
✅ Use milliseconds for TTL (not seconds)  
✅ Set appropriate TTL based on message type  
✅ Use consistent TTL values (e.g., notifications=5 min)  
✅ Document TTL strategy  
✅ Monitor expired message rate  

**TTL Strategy:**
✅ Use shorter TTLs for time-sensitive data  
✅ Use longer TTLs for less critical data  
✅ Use per-message TTL when different messages need different TTLs  
✅ Use per-queue TTL when all messages have same TTL  
✅ Set DLX to capture expired messages for analysis  

**Expired Message Handling:**
✅ Check message expiration in consumer  
✅ Skip processing of expired messages  
✅ Use DLX to capture and analyze expired messages  
✅ Log expiration events for monitoring  
✅ Alert on high expiration rate  

### Common Mistakes

❌ Using seconds instead of milliseconds → TTL wrong (1000x too long)  
❌ Forgetting to set TTL → Messages never expire  
❌ Setting TTL too long → Stale data processed  
❌ Setting TTL too short → Valid messages expire before processing  
❌ Not checking expiration in consumer → Wasted processing  
❌ Not using DLX → Expired messages lost forever  
❌ Using same TTL for different message types → Inefficient cleanup  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Stale Notifications (The Delayed Alerts)**

You're building a notification system for order processing:

- Producer sends various notifications
- Consumer processes and pushes notifications
- Notifications should be timely (within minutes)
- Old notifications should expire

Current implementation:
- Producer publishes notifications immediately
- No TTL set on messages
- Notifications accumulate in queue
- If consumer is down, all notifications become stale

**Problems:**
- Notifications delivered 24+ hours late when consumer restarts
- Irrelevant notifications (customer already received package)
- Queue grows with stale notifications
- Consumer overwhelmed with backlog on restart
- Customer frustration with delayed notifications
- **Impact:** Poor customer experience, wasted resources, notification fatigue

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

**Step 2: Create producer without TTL**

Create `no_ttl_producer.py`:

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: No TTL on notifications
channel.queue_declare(queue='notifications')

notifications = [
    "Order shipped!",
    "Order delivered!",
    "Payment received!",
    "Order completed!",
]

for notification in notifications:
    channel.basic_publish(
        exchange='',
        routing_key='notifications',
        body=notification
    )
    print(f"[x] Sent notification: {notification}")

print(f"[✓] Sent {len(notifications)} notifications (PROBLEM: No TTL - stale)")
connection.close()
```

**Step 3: Create consumer without expiration check**

Create `no_ttl_consumer.py`:

```python
import pika
import time

def callback(ch, method, properties, body):
    """Process notification (no expiration check)"""
    message = body.decode()
    
    # PROBLEM: No expiration check
    # Process all messages regardless of age
    print(f"[✓] Processing: {message}")
    time.sleep(2)  # Simulate slow processing
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='notifications')
channel.basic_consume(queue='notifications', on_message_callback=callback)

print('[*] Consumer waiting (no expiration check)')
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal 1: Start consumer
python3 no_ttl_consumer.py

# Terminal 2: Wait 30 seconds (simulate consumer delay)

# Terminal 3: Producer
python3 no_ttl_producer.py

# Terminal 4: Stop consumer (Ctrl+C)
# Terminal 5: Start consumer again (will receive stale messages)
python3 no_ttl_consumer.py
```

**Expected observation:**
- Producer sends 4 notifications
- Consumer stops after processing 2 notifications
- 2 notifications left in queue (stale)
- After 30 seconds, notifications are stale
- Consumer restarts and sends all 4 notifications
- 2 notifications are stale (order already completed hours ago)

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Queues tab → Click on "notifications"
- See 4 messages (2 stale, 2 might be stale)
- Can't tell which notifications are stale
- No way to clean up stale notifications

### ✅ Solution & Explanation

**Solution: Implement TTL for Notifications**

**Create producer with TTL (ttl_producer.py):**

```python
import pika
import json

class NotificationProducer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='notifications')
    
    def send_notification(self, message, ttl_seconds):
        """SOLUTION: Send notification with TTL"""
        # SOLUTION: Convert seconds to milliseconds
        ttl_ms = ttl_seconds * 1000
        
        # SOLUTION: Set TTL per message
        self.channel.basic_publish(
            exchange='',
            routing_key='notifications',
            body=message,
            properties=pika.BasicProperties(
                expiration=str(ttl_ms)  # SOLUTION: TTL in milliseconds
            )
        )
        print(f"[x] Sent notification: {message[:30]}... (TTL: {ttl_seconds}s)")
    
    def close(self):
        self.connection.close()

# SOLUTION: Send notifications with different TTLs
producer = NotificationProducer()

notifications = [
    ("Order shipped!", 300),      # 5 minutes
    ("Order delivered!", 300),    # 5 minutes
    ("Payment received!", 300),  # 5 minutes
    ("Order completed!", 300),    # 5 minutes
]

for message, ttl in notifications:
    producer.send_notification(message, ttl)

producer.close()
```

**Create consumer with DLX (ttl_consumer.py):**

```python
import pika

# SOLUTION: Setup DLX to capture expired notifications
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Create DLX exchange
channel.exchange_declare(exchange='notification-dlx', exchange_type='direct')

# SOLUTION: Create DLQ for expired notifications
channel.queue_declare(
    queue='expired-notifications',
    arguments={
        'x-message-ttl': 86400000  # 24 hours (DLQ cleanup)
    }
)

# SOLUTION: Bind DLQ to DLX
channel.queue_bind(
    exchange='notification-dlx',
    queue='expired-notifications',
    routing_key='expired'
)

# SOLUTION: Declare main queue with TTL and DLX
channel.queue_declare(
    queue='notifications',
    arguments={
        'x-message-ttl': '60000',  # SOLUTION: 1 minute TTL
        'x-dead-letter-exchange': 'notification-dlx',  # SOLUTION: DLX
        'x-dead-letter-routing-key': 'expired'  # SOLUTION: Routing key
    }
)

def callback(ch, method, properties, body):
    """SOLUTION: Process notification"""
    message = body.decode()
    print(f"[✓] Processing: {message}")
    time.sleep(2)  # Simulate processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='notifications', on_message_callback=callback)

def expired_callback(ch, method, properties, body):
    """SOLUTION: Handle expired notification"""
    message = body.decode()
    print(f"[!] EXPIRED: {message}")
    
    # SOLUTION: Log expired notification for analysis
    with open('expired_notifications.log', 'a') as f:
        f.write(f"{message}\n")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"[✓] Logged expired notification")

# SOLUTION: Main consumer
print('[*] Consumer waiting (notifications expire after 1 min)')
channel.start_consuming()

# SOLUTION: DLQ consumer (monitor expired notifications)
connection2 = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel2 = connection2.channel()

channel2.basic_consume(
    queue='expired-notifications',
    on_message_callback=expired_callback
)

print('[*] DLQ Consumer (monitoring expired notifications)')
channel2.start_consuming()
```

**How to verify:**

```bash
# Clear RabbitMQ
docker stop rabbitmq && docker rm rabbitmq
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Terminal 1: Main Consumer
python3 ttl_consumer.py

# Terminal 2: DLQ Consumer
python3 -c "import pika; conn = pika.BlockingConnection(pika.ConnectionParameters('localhost')); chan = conn.channel(); chan.basic_consume(queue='expired-notifications', on_message_callback=lambda ch, m, p, b: print('[DLQ]', expired=True) and not ch._consumers and chan.start_consuming())"

# Terminal 3: Producer
python3 ttl_producer.py

# Terminal 4: Wait 2 minutes (notifications expire)
# Terminal 5: Send new notifications (fresh ones)
```

**Expected output:**

```
# Producer
[x] Sent notification: Order shipped!... (TTL: 300s)
[x] Sent notification: Order delivered!... (TTL: 300s)
[x] Sent notification: Payment received!... (TTL: 300s)
[x] Sent notification: Order completed!... (TTL: 300s)

# Main Consumer
[*] Consumer waiting (notifications expire after 1 min)
[✓] Processing: Order shipped!
[✓] Processing: Order delivered!

# DLQ Consumer (after 2 minutes)
[!] EXPIRED: Order shipped!
[!] EXPIRED: Order delivered!
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Exchanges tab → See "notification-dlx"
3. Go to Queues tab → See "expired-notifications"
4. Monitor expired notifications in DLQ
5. See notifications expire in real-time (after 1 min)

**Comparison:**

| Design | Stale Notifications | Consumer Overload | Message Freshness |
|--------|-------------------|------------------|-----------------|
| No TTL | 24+ hours | Yes (on restart) | Poor |
| With TTL | 0 minutes | No | Excellent |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Always use milliseconds for TTL (not seconds)  
- Set appropriate TTL based on message type  
- Use shorter TTLs for time-sensitive data  
- Use longer TTLs for less critical data  
- Use per-message TTL when different messages need different TTLs  
- Set DLX to capture expired messages for analysis  
- Check message expiration in consumer  
- Monitor expired message rate  
- Log expiration events for monitoring  
- Use consistent TTL values  

**❌ Don't:**
- Use seconds instead of milliseconds → TTL wrong  
- Forget to set TTL → Messages never expire  
- Set TTL too long → Stale data processed  
- Set TTL too short → Valid messages expire before processing  
- Not checking expiration in consumer → Wasted processing  
- Not using DLX → Expired messages lost forever  
- Use same TTL for all messages → Inefficient cleanup  
- Leave expired messages in DLQ forever → Disk fills  

### TTL Strategy Guidelines

```
Time-Sensitive Data:
├─ Real-time updates: 1 minute TTL
├─ Notifications: 5-15 minutes TTL
└─ Session tokens: 1 hour TTL

Less Critical Data:
├─ Status updates: 15-30 minutes TTL
├─ Daily reports: 24 hours TTL
└─ Weekly reports: 7 days TTL

Archival/Log Data:
├─ Logs: 7-30 days TTL
└─ Archives: 90-365 days TTL
```

### Production Considerations

**Monitoring TTL:**

```python
# Monitor expired message rate
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Get DLQ info
method = channel.queue_declare(queue='expired-notifications', passive=True)
expired_count = method.method.message_count

print(f"Expired notifications: {expired_count}")

# Alert if too many expired messages
if expired_count > 100:
    print("[ALERT] High expiration rate - possible system issue!")
```

**TTL Tuning:**

```python
# Monitor and adjust TTL based on patterns
ttl_values = {
    'order_shipped': 300,    # 5 minutes
    'order_delivered': 300,  # 5 minutes
    'payment_received': 300, # 5 minutes
    'order_completed': 300,  # 5 minutes
    'session_token': 3600,   # 1 hour
    'password_reset': 86400, # 24 hours
    'discount_code': 86400    # 24 hours
}

def get_ttl(message_type):
    return ttl_values.get(message_type, 300)  # Default 5 minutes

# Use TTL based on message type
channel.basic_publish(
    exchange='',
    routing_key='notifications',
    body=message,
    properties=pika.BasicProperties(
        expiration=str(get_ttl(message_type))
    )
)
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's the difference between message TTL and queue TTL?**

A: Message TTL is a timeout for individual messages (different messages can have different TTLs). Queue TTL is a timeout for the entire queue (all messages have same TTL). Message TTL expires individual messages, queue TTL expires the entire queue if unused.

**Q2: What unit does RabbitMQ use for TTL?**

A: RabbitMQ uses milliseconds for TTL. Many developers accidentally use seconds, which results in TTL 1000x too long (e.g., setting TTL to 300 results in 5 minutes, not 5 seconds).

**Q3: What happens to expired messages?**

A: Expired messages are removed from queue and NOT delivered to any consumer. If DLX is configured, expired messages are routed to Dead Letter Queue for analysis. If no DLX, messages are permanently lost.

**Q4: How do you handle expired messages in consumer?**

A: Consumers can check message expiration properties (properties.expiration) and skip processing if message has expired. Alternatively, use DLX to capture expired messages in a separate queue for analysis and logging.

**Q5: What's the best practice for TTL: per-message or per-queue?**

A: Per-message TTL gives more flexibility (different messages can have different TTLs). Per-queue TTL is simpler (all messages have same TTL) but less flexible. Use per-message TTL when different messages need different TTLs, per-queue TTL when all messages have same expiration time.

### Production Pitfalls

**Pitfall 1: Using seconds instead of milliseconds**
- Problem: TTL 1000x too long (300 instead of 5 seconds)
- Detection: Messages expire much later than expected
- Solution: Always use milliseconds for TTL

**Pitfall 2: Not setting TTL**
- Problem: Messages never expire, queue grows indefinitely
- Detection: Queue fills disk with ancient messages
- Solution: Always set TTL for time-sensitive data

**Pitfall 3: Setting TTL too short**
- Problem: Valid messages expire before processing
- Detection: Message lost, customer frustration
- Solution: Set TTL longer than max processing time

**Pitfall 4: Not using DLX**
- Problem: Expired messages lost forever
- Detection: No audit trail of expired messages
- Solution: Always configure DLX to capture expired messages

**Pitfall 5: Not checking expiration in consumer**
- Problem: Wasted processing on expired messages
- Detection: High CPU, poor performance
- Solution: Check message expiration before processing

### Advanced TTL Concepts

**Queue TTL (expires entire queue if unused):**

```python
# Queue expires if unused for 30 days
channel.queue_declare(
    queue='notifications',
    arguments={
        'x-expires': '2592000000'  # 30 days (in milliseconds)
    }
)
```

**Per-Message vs Per-Queue Priority:**

```python
# Per-message TTL takes priority over per-queue TTL
channel.queue_declare(
    queue='notifications',
    arguments={
        'x-message-ttl': '60000'  # Per-queue: 1 minute
    }
)

# Per-message: 5 minutes (takes priority)
channel.basic_publish(
    exchange='',
    routing_key='notifications',
    body=message,
    properties=pika.BasicProperties(
        expiration='300000'  # Per-message: 5 minutes
    )
)
```

**TTL with DLX and Alternate Exchange:**

```python
# Configure alternate exchange
channel.queue_declare(
    queue='notifications',
    arguments={
        'x-message-ttl': '60000',
        'x-dead-letter-exchange': 'alt-dlx'  # Alternate DLX
    }
)
```

---

## 📚 Summary

Message TTL and Expiration provide automatic message cleanup based on time, ensuring queue stays clean and consumers process only fresh, relevant data. Combined with DLX, they guarantee expired messages are captured for analysis while preventing stale data processing.

**Key takeaways:**
- TTL controls when messages expire (in milliseconds)
- Message expiration removes messages from queue
- Expired messages NOT delivered to consumers
- Use DLX to capture expired messages for analysis
- Use shorter TTLs for time-sensitive data
- Use longer TTLs for less critical data
- Check message expiration in consumer (skip if expired)
- Monitor expired message rate
- Always use milliseconds (not seconds) for TTL

**Next steps:**
- Practice with TTL in your applications
- Learn about Consumer Prefetch and Fair Dispatch
- Understand message durability and persistence
- Learn about transactionality and atomic operations

---

**Module 02 - Advanced RabbitMQ Features**  
**Lesson 04 - Complete**