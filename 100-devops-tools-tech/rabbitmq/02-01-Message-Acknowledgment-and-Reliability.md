# 02-01: Message Acknowledgment and Reliability

## 1️⃣ What Are Message Acknowledgments

**Message acknowledgments (acks)** are confirmations sent by consumers back to RabbitMQ to indicate successful (or unsuccessful) message processing. They provide reliability by ensuring messages aren't lost if consumers crash or fail.

Think of message acknowledgments like delivery receipts:

- **Message** = A package delivered by courier
- **Consumer** = The person receiving the package
- **Acknowledgment** = The recipient signing for the package
- **No Ack** = Package lost, courier doesn't know if delivered

**Where acknowledgments fit in RabbitMQ architecture:**

```
┌─────────────┐
│  Producer   │
└──────┬──────┘
       │
       │ Publishes message
       ▼
┌─────────────────────────────┐
│        Exchange           │
│     (Routes message)       │
└──────┬──────────────────────┘
       │
       ▼
┌──────────────────────┐
│      Queue          │
│  (Buffers message)  │
└──────┬───────────────┘
       │
       │ Delivers to consumer
       ▼
┌─────────────┐
│  Consumer   │
└──────┬──────┘
       │
       │ Process message
       │ Send ACK (success) or NACK (fail)
       ▼
┌─────────────────────────────┐
│        Exchange           │
│  (Removes from queue)     │
└──────────────────────────────┘
```

**Key concepts:**
- **Manual ACK:** Consumer explicitly acknowledges each message
- **Auto ACK:** RabbitMQ automatically acknowledges after delivery (not reliable)
- **Positive ACK:** Message successfully processed
- **Negative ACK (NACK): Message processing failed, may requeue
- **Reject:** Negative ACK with requeue=false (message discarded)
- **Multiple ACK:** Batch acknowledgments for multiple messages

---

## 2️⃣ Problems Solved by Message Acknowledgments

### The Lost Message Problem

Without acknowledgments (auto-ack mode):

- Consumer receives message
- Consumer crashes while processing
- Message is lost (marked as unacked but not redelivered)
- No guarantee message was processed

**Real-world failure scenario:**

An order processing system had:

```
Producer → Queue → Consumer (auto-ack)
                               │
                               │ Receive order
                               │ Crash during payment processing!
                               │ Message lost
```

**Problems:**
- 50 orders lost per day due to consumer crashes
- Customer orders disappeared from system
- No way to recover or retry lost orders
- Financial discrepancies and customer complaints
- **Impact:** $15K in lost revenue, 500 dissatisfied customers, customer trust damaged

After implementing manual acknowledgments:
- Consumer receives message and holds it
- Consumer crashes before ACK
- Message stays in queue (unacked)
- Another consumer redelivers message
- All orders eventually processed
- **Result:** 100% order reliability, zero lost orders

### The Consumer Crash Problem

Without acknowledgments:

- Consumer fails while processing message
- Message marked as "unacked" but not redelivered
- Queue grows with unprocessed messages
- System appears stuck

**Example:**

```
Queue State:
├─ 1000 messages ready
├─ 5 messages unacked (stuck)
└─ Consumer crashed

After consumer restart, 5 messages remain unprocessed
until timeout (not guaranteed)
```

**Problems:**
- Messages stuck in "unacked" state
- No visibility into processing failures
- Queue appears healthy but messages not processed
- Manual intervention required
- **Impact:** Customer-facing delays, system appears unresponsive, requires manual intervention

After implementing acknowledgments:
- Unacked messages automatically requeued
- New consumers pick up where crashed consumer left off
- No manual intervention needed
- System self-heals
- **Result:** Automatic recovery, zero intervention required

---

## 3️⃣ When You Should Use Message Acknowledgments

### Development vs Production

**Development:**
- Can use auto-ack for quick testing
- No need for reliability in throwaway code
- Simpler code for experimentation
- Don't use auto-ack in production code

**Production:**
- Absolutely required for reliability
- Essential for critical data (orders, payments)
- Critical for long-running processing tasks
- Required for fault-tolerant systems

### Auto-Ack vs Manual Ack

| Mode | Reliability | Use When | Example |
|-------|--------------|-----------|---------|
| **Auto-Ack** | None | Development/Testing | Throwaway scripts |
| **Manual ACK** | High | Production, critical data | Order processing, payments |

### Required vs Optional

**Required when:**
- Processing critical data (orders, payments, notifications)
- Long-running tasks (image processing, file uploads)
- Fault tolerance required (consumer crashes acceptable)
- At-least-once guarantee needed
- Data loss unacceptable

**Optional when:**
- Pure pub/sub with fire-and-forget (notifications)
- Very short-lived messages (heartbeat/status)
- Idempotent operations (message can be reprocessed)
- Performance-critical, data-loss acceptable

### Trade-offs

**Manual Acknowledgments:**
✅ High reliability and message safety  
✅ At-least-once guarantee  
✅ Automatic recovery from failures  
✅ No lost messages  
❌ Slower performance (more network traffic)  
❌ More complex code  
❌ Requires careful error handling  

**Auto-Acknowledgments:**
✅ Simpler code  
✅ Faster performance  
✅ Less network overhead  
❌ No reliability guarantee  
❌ Messages lost on failure  
❌ No at-least-once guarantee  

---

## 4️⃣ How Message Acknowledgments Work

### Acknowledgment Process Flow

**Basic acknowledgment flow:**

```
1. Consumer Receives Message
   │
   ├─ Message delivered to consumer
   ├─ Message marked as "unacked" in RabbitMQ
   └─ Message removed from "ready" count
   │
2. Consumer Processes Message
   │
   ├─ Business logic executes (process payment, update DB)
   ├─ Processing may take time (100ms - 5 minutes)
   └─ Consumer might crash during processing
   │
3. Consumer Sends Acknowledgment
   │
   ├─ If success: ch.basic_ack(delivery_tag)
   ├─ If failure: ch.basic_nack(delivery_tag)
   └─ If reject: ch.basic_reject(delivery_tag)
   │
4. RabbitMQ Updates Queue
   │
   ├─ Positive ACK: Message removed from queue
   ├─ Negative ACK (requeue): Message redelivered to queue
   └─ Reject (no requeue): Message removed (DLX if configured)
```

### Acknowledgment Types

**Basic Ack (single message):**

```python
def callback(ch, method, properties, body):
    # Process message
    result = process_message(body)
    
    if result:
        # Success: Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        # Failure: Negative ACK (requeue)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

**Multiple Ack (batch):**

```python
def callback(ch, method, properties, body):
    # Process multiple messages
    process_messages(body)
    
    # Acknowledge all delivery tags
    for tag in method.delivery_tags:
        ch.basic_ack(delivery_tag=tag)
```

**Reject (discard message):**

```python
def callback(ch, method, properties, body):
    try:
        # Process message
        result = process_message(body)
    except InvalidDataError as e:
        # Reject message (don't requeue)
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
```

### Unacked Messages State

**Queue state with acknowledgments:**

```
Queue: orders

Messages State:
├─ Ready: 950 (waiting to be delivered)
├─ Unacked: 50 (being processed by consumers)
└─ Total: 1000

Ready messages = 950
Unacked messages = 50
Total = 1000 (950 + 50)
```

**Unacked messages:**
- Sent to consumer but not yet acknowledged
- Still in queue (not delivered to other consumers)
- Max limit controlled by prefetch_count
- If consumer crashes, messages become ready again

### Publisher Confirms vs Consumer Acknowledgments

**Key differences:**

| Feature | Consumer ACK | Publisher Confirm |
|----------|---------------|-------------------|
| **Direction** | Consumer → RabbitMQ | RabbitMQ → Producer |
| **Purpose** | Message processed safely | Message received by broker |
| **Use Case** | Consumer reliability | Producer reliability |
| **When** | After processing | After publish |
| **Mechanism** | basic_ack/basic_nack | Confirm.select/confirm_callback |

**When to use each:**

- **Consumer ACK:** Always use in production consumers
- **Publisher Confirm:** Use when you need guarantee message reached broker

---

## 5️⃣ Installation / Setup

**Message acknowledgments are built-in AMQP features.** No installation required - just configure consumers properly.

### Prerequisites

- RabbitMQ server running
- AMQP client library installed
- Understanding of consumer workflow

### Enabling Manual Acknowledgments

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare queue
channel.queue_declare(queue='orders')

# Manual acknowledgment (default is False)
channel.basic_consume(
    queue='orders',
    on_message_callback=callback,
    auto_ack=False  # FALSE = Manual acknowledgment
)

print(' [*] Consumer with manual ACK waiting for messages')
channel.start_consuming()
```

**Node.js (amqplib):**

```javascript
const amqp = require('amqplib/callback_api');

const connection = amqp.connect('amqp://localhost');
const channel = connection.createChannel();

channel.assertQueue('orders', function(err, ok) {
    channel.consume('orders', { noAck: true }, function(msg) {
        // Process message
        processMessage(msg.content, function(err) {
            if (err) {
                // Reject message
                channel.nack(msg.deliveryTag, false);
            } else {
                // Acknowledge message
                channel.ack(msg.deliveryTag);
            }
        });
    });
});
```

**Java (RabbitMQ Java Client):**

```java
import com.rabbitmq.client.*;

ConnectionFactory factory = new ConnectionFactory();
factory.setHost("localhost");
Connection connection = factory.newConnection();
Channel channel = connection.createChannel();

channel.queueDeclare("orders", false, false, null, null);
// noAck = true means manual acknowledgment
Consumer consumer = new DefaultConsumer(channel, "orders", false, true, (tag, message) -> {
    // Process message
    boolean success = processMessage(message.getBody());
    if (success) {
        // Positive acknowledgment
        channel.basicAck(message.getEnvelope().getDeliveryTag(), false);
    } else {
        // Negative acknowledgment (requeue)
        channel.basicNack(message.getEnvelope().getDeliveryTag(), true, false);
    }
});
```

### Enabling Publisher Confirms

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Enable publisher confirms
channel.confirm_delivery()

# Publish message
channel.basic_publish(
    exchange='',
    routing_key='orders',
    body='order_data'
)

# Wait for confirmation
if channel.wait_for_confirms(timeout=5):
    print(" [✓] Message confirmed by RabbitMQ")
else:
    print(" [✗] Message confirmation timeout")

connection.close()
```

### Version Notes

- **RabbitMQ 3.12+:** All acknowledgment features fully supported
- **AMQP 0-9-1:** Acknowledgments protocol standard
- **Default behavior:** auto_ack=True (not reliable)
- **Publisher confirms:** Must be enabled per channel

---

## 6️⃣ Where Message Acknowledgments Should Be Applied (With Example)

### Reliable Consumer Implementation

**Scenario:** Payment processing system that must never lose payment messages

**Producer (send_payment.py):**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='payments')

# Send payments (no publisher confirm for now)
for i in range(10):
    payment = {
        "payment_id": f"pay_{i+1:03d}",
        "amount": (i+1) * 99.99,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='payments',
        body=json.dumps(payment)
    )
    print(f" [x] Sent payment: {payment['payment_id']}")

connection.close()
```

**Consumer (reliable_consumer.py):**

```python
import pika
import json

def process_payment(payment_data):
    """Simulate payment processing (may fail)"""
    payment = json.loads(payment_data)
    
    # Simulate 20% failure rate
    if int(payment['payment_id'].split('_')[1]) % 5 == 0:
        print(f" [✗] Payment FAILED: {payment['payment_id']}")
        raise Exception("Payment gateway timeout")
    
    # Simulate processing time
    import time
    time.sleep(0.5)  # 500ms processing time
    
    print(f" [✓] Payment processed: {payment['payment_id']} ${payment['amount']}")
    return True

def callback(ch, method, properties, body):
    try:
        # Process payment
        success = process_payment(body)
        
        # Success: Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        # Failure: Reject message (don't requeue)
        # In production, might want to requeue or send to DLX
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        print(f" [✗] Message rejected: {e}")

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='payments')

# Fair dispatch (process one message at a time)
channel.basic_qos(prefetch_count=1)

# Manual acknowledgment (CRITICAL for reliability)
channel.basic_consume(
    queue='payments',
    on_message_callback=callback,
    auto_ack=False  # FALSE = Manual acknowledgment
)

print(' [*] Reliable consumer waiting for payments (manual ACK)')
channel.start_consuming()
```

**How to test reliability:**

```bash
# Terminal 1: Start consumer
python3 reliable_consumer.py

# Terminal 2: Send payments
python3 send_payment.py
```

**Expected output:**

```
# Consumer
[*] Reliable consumer waiting for payments (manual ACK)
[x] Received payment: pay_001
[✓] Payment processed: pay_001 $99.99
[x] Received payment: pay_002
[✗] Payment FAILED: pay_005
[✗] Message rejected: Payment gateway timeout
[x] Received payment: pay_003
[✓] Payment processed: pay_003 $299.97
...

# All messages processed, failed payments rejected
# No messages lost
```

### Publisher Confirms Implementation

**Scenario:** Order submission system that must guarantee order messages reach RabbitMQ

**Producer (confirmed_producer.py):**

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Enable publisher confirms
channel.confirm_delivery()

channel.queue_declare(queue='orders')

# Send orders with confirmation
orders = []
for i in range(10):
    order = {
        "order_id": f"order_{i+1:03d}",
        "customer_id": 12345 + i,
        "amount": (i+1) * 49.99,
        "timestamp": time.time()
    }
    
    # Publish message
    channel.basic_publish(
        exchange='',
        routing_key='orders',
        body=json.dumps(order)
    )
    orders.append(order)
    print(f" [x] Published order: {order['order_id']}")

# Wait for all confirms
confirmed = channel.wait_for_confirms(timeout=5)
print(f" [✓] Confirmed {confirmed} / {len(orders)} orders")

connection.close()
```

**Expected output:**

```
[x] Published order: order_001
[x] Published order: order_002
...
[x] Published order: order_010
[✓] Confirmed 10 / 10 orders
```

### Multiple Acknowledgments

**Scenario:** High-throughput system that acknowledges messages in batches for performance

**Consumer (batch_consumer.py):**

```python
import pika

def callback(ch, method, properties, body):
    """Process message (quick operation)"""
    # Quick processing (e.g., insert into batch)
    print(f" [x] Processing message: {body.decode()}")
    
    # Acknowledge this message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
    # Every 10 messages, send multiple ack
    if method.delivery_tag % 10 == 0:
        # Get unacked messages
        for tag in range(method.delivery_tag, method.delivery_tag + 5):
            if tag > method.delivery_tag:
                ch.basic_ack(delivery_tag=tag)
        print(f" [✓] Batch acknowledged messages {method.delivery_tag}-{method.delivery_tag+4}")

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='high-throughput')

# Prefetch for batching
channel.basic_qos(prefetch_count=10)

# Manual acknowledgment
channel.basic_consume(
    queue='high-throughput',
    on_message_callback=callback,
    auto_ack=False
)

print(' [*] Batch consumer waiting for messages')
channel.start_consuming()
```

### Best Practices

**Consumer Implementation:**
✅ Always use manual_ack in production  
✅ Set appropriate prefetch_count  
✅ Handle exceptions in callback  
✅ Use try-except for error handling  
✅ Acknowledge only after successful processing  
✅ Reject or NACK failed messages appropriately  
✅ Monitor unacked message count  

**Publisher Implementation:**
✅ Enable confirms for critical messages  
✅ Wait for confirmation (or async callback)  
✅ Handle confirmation failures (re-publish)  
✅ Set reasonable timeout for wait_for_confirms  
✅ Log confirmation failures  
✅ Use confirms for persistent messages  

**Prefetch Settings:**
✅ Use prefetch_count=1 for long-running tasks  
✅ Use higher prefetch_count for fast tasks (10-100)  
✅ Monitor unacked messages (should be low)  
✅ Adjust prefetch based on processing time  

### Common Mistakes

❌ Using auto_ack in production → Messages lost on crash  
❌ Not acknowledging after processing → Messages stuck in unacked  
❌ Acknowledging before processing → Data loss on crash  
❌ Forgetting exception handling → Consumer crashes  
❌ Not using prefetch_count → Consumer overwhelmed  
❌ Setting prefetch too high → Consumer memory issues  
❌ NACK with requeue=True on permanent failure → Infinite loop  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Silent Data Loss (The Unprocessed Messages)**

You're building a notification system that sends push notifications to mobile devices:

- Producer sends notification messages to queue
- Consumer calls external push service API (can be slow)
- System processes 1000 notifications per hour
- Push service has 5% failure rate

Current implementation uses auto-ack:
- Consumer receives message and calls push service
- If push service fails, consumer crashes
- Notification is lost but system appears healthy
- No way to recover failed notifications

**Problems:**
- 50 notifications lost per hour (5% of 1000)
- Customers never receive critical notifications
- No visibility into push failures
- Queue appears empty (messages delivered but not processed)
- **Impact:** Customer complaints, missed critical alerts, $25K in potential revenue

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

**Step 2: Create unreliable producer**

Create `notification_producer.py`:

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='notifications')

# PROBLEM: Producer has no way to know if processed
# Notifications may be lost
notifications = []
for i in range(100):
    notification = {
        "notification_id": f"notif_{i+1:03d}",
        "user_id": 12345,
        "message": f"Notification message {i+1}",
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='notifications',
        body=json.dumps(notification)
    )
    notifications.append(notification)
    print(f" [x] Sent notification: {notification['notification_id']}")

print(f" [✓] Sent {len(notifications)} notifications (no confirmation if processed)")
connection.close()
```

**Step 3: Create unreliable consumer (auto-ack)**

Create `unreliable_consumer.py`:

```python
import pika
import json
import random
import time

def send_push_notification(notification_data):
    """Simulate push service API call (may fail)"""
    notification = json.loads(notification_data)
    
    # Simulate 5% failure rate
    if random.random() < 0.05:
        print(f" [✗] PUSH SERVICE FAILED for: {notification['notification_id']}")
        raise Exception("Push service timeout")
    
    # Simulate slow API call (200ms)
    time.sleep(0.2)
    
    print(f" [✓] Push sent: {notification['notification_id']}")
    return True

def callback(ch, method, properties, body):
    """PROBLEM: Auto-ack模式下，consumer崩溃会导致消息丢失"""
    try:
        # Process notification
        success = send_push_notification(body)
        
        # PROBLEM: 如果这里崩溃，消息已经被auto-ack确认，无法重新入队
        # 消息永久丢失
        if random.random() < 0.1:  # 模拟10%崩溃率
            print(f" [CRASH] Consumer crashing after processing: {json.loads(body)['notification_id']}")
            raise Exception("Simulated consumer crash")
    
        # 如果执行到这里，说明没有崩溃，由于auto_ack，消息已经被确认
        # 但实际上可能推送失败，只是没崩溃
        
    except Exception as e:
        print(f" [✗] Error: {e}")
        # 由于auto_ack，无法控制是否重新入队
    
    # PROBLEM: auto_ack=True 模式，RabbitMQ在投递消息时就自动确认
    # 无论消费者是否成功处理
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.connection.channel()
    channel.queue_declare(queue='notifications')
    # PROBLEM: 设置 auto_ack=True（默认行为，不可靠）
    channel.basic_consume(
        queue='notifications',
        on_message_callback=callback,
        auto_ack=True  # TRUE = 自动确认（不可靠！）
    )
    
    print(' [*] Unreliable consumer (auto-ack=True) - 消息可能丢失')
    channel.start_consuming()

if __name__ == '__main__':
    unreliable_consumer()

connection.close()
```

**Step 4: Reproduce problem**

```bash
# Terminal 1: Unreliable consumer
python3 unreliable_consumer.py

# Terminal 2: Producer
python3 notification_producer.py
```

**Expected observation:**
- Producer sends 100 notifications
- Consumer receives and processes ~95 (95 success rate)
- ~5 notifications fail due to push service
- ~5 notifications lost due to consumer crashes
- Queue appears healthy but messages are actually lost
- No way to detect which notifications were lost

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Queues tab → Click on "notifications"
- See queue empty (all messages delivered)
- No visibility into processing failures
- Can't tell which notifications were successfully sent

### ✅ Solution & Explanation

**Solution: Implement Manual Acknowledgments**

**Create reliable consumer (reliable_consumer.py):**

```python
import pika
import json
import random
import time

def send_push_notification(notification_data):
    """Simulate push service API call (may fail)"""
    notification = json.loads(notification_data)
    
    # Simulate 5% failure rate
    if random.random() < 0.05:
        print(f" [✗] PUSH SERVICE FAILED for: {notification['notification_id']}")
        raise Exception("Push service timeout")
    
    # Simulate slow API call (200ms)
    time.sleep(0.2)
    
    print(f" [✓] Push sent: {notification['notification_id']}")
    return True

def callback(ch, method, properties, body):
    """SOLUTION: 手动确认模式，确保消息不会丢失"""
    try:
        # Process notification
        success = send_push_notification(body)
        
        # SOLUTION: 只有成功推送后才确认消息
        # 如果这里崩溃，消息保持为unacked状态，可以重新入队
        if random.random() < 0.1:  # 模拟10%崩溃率
            print(f" [CRASH] Consumer crashing after processing: {json.loads(body)['notification_id']}")
            raise Exception("Simulated consumer crash")
        
        # SOLUTION: 成功处理，发送ACK
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f" [✓] ACK sent for: {json.loads(body)['notification_id']}")
    
    except Exception as e:
        # SOLUTION: 推送失败，拒绝消息（不重新入队，避免无限循环）
        # 在生产环境中，可能需要DLX或重试逻辑
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        print(f" [✗] REJECTED (will not requeue): {json.loads(body)['notification_id']}")
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.connection.channel()
    channel.queue_declare(queue='notifications')
    
    # SOLUTION: 设置 auto_ack=False（手动确认模式）
    # 并设置 prefetch_count=1（fair dispatch，一次处理一个消息）
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='notifications',
        on_message_callback=callback,
        auto_ack=False  # FALSE = 手动确认（可靠！）
    )
    
    print(' [*] Reliable consumer (auto_ack=False) - 消息不会丢失')
    channel.start_consuming()

if __name__ == '__main__':
    reliable_consumer()

# 注意：由于使用了连接对象的connection.connection.channel()，
# 在关闭连接前需要手动处理
# 但start_consuming()会阻塞主线程，所以这里简化了代码

```

**Create improved producer (with publisher confirms)**

Create `confirmed_producer.py`:

```python
import pika
import json
import time

def send_notifications_with_confirms():
    """SOLUTION: 使用publisher confirms确保消息到达RabbitMQ"""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()
    
    # SOLUTION: 启用publisher confirms
    channel.confirm_delivery()
    
    channel.queue_declare(queue='notifications')
    
    # Send notifications with confirmation
    notifications = []
    confirmed = 0
    
    for i in range(100):
        notification = {
            "notification_id": f"notif_{i+1:03d}",
            "user_id": 12345,
            "message": f"Notification message {i+1}",
            "timestamp": time.time()
        }
        
        # 发布消息
        channel.basic_publish(
            exchange='',
            routing_key='notifications',
            body=json.dumps(notification)
        )
        notifications.append(notification)
        print(f" [x] Published notification: {notification['notification_id']}")
    
    # SOLUTION: 等待所有消息确认
    print(f" [✓] Waiting for confirms...")
    confirmed = channel.wait_for_confirms(timeout=5)
    print(f" [✓] Confirmed {confirmed} / {len(notifications)} notifications")
    
    # SOLUTION: 检查是否所有消息都确认
    if confirmed == len(notifications):
        print(f" [✓] All {len(notifications)} notifications confirmed by RabbitMQ")
    else:
        print(f" [✗] Only {confirmed}/{len(notifications)} confirmed - {len(notifications)-confirmed} failed")
    
    connection.close()

if __name__ == '__main__':
    send_notifications_with_confirms()
```

**How to verify:**

```bash
# Clear RabbitMQ
docker stop rabbitmq && docker rm rabbitmq
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Terminal 1: 可靠的消费者
python3 reliable_consumer.py

# Terminal 2: 带确认的生产者
python3 confirmed_producer.py
```

**Expected output:**

```
# 可靠消费者
[*] Reliable consumer (auto_ack=False) - 消息不会丢失
[x] Received notification: notif_001
[✓] Push sent: notif_001
[x] Received notification: notif_002
[✗] PUSH SERVICE FAILED for: notif_005
[✓] ACK sent for: notif_002
[x] Received notification: notif_003
[CRASH] Consumer crashing after processing: notif_003
# 由于崩溃，消息未确认，RabbitMQ会重新入队
[x] Received notification: notif_003 (redelivered)
[✓] Push sent: notif_003
[✓] ACK sent for: notif_003
[x] Received notification: notif_004
[✓] Push sent: notif_004
[✓] ACK sent for: notif_004
[✗] REJECTED (will not requeue): notif_005
[x] Received notification: notif_005 (redelivered)
[✓] Push sent: notif_005
[✓] ACK sent for: notif_005
...

# 带确认的生产者
[x] Published notification: notif_001
[x] Published notification: notif_002
...
[x] Published notification: notif_010
[✓] Waiting for confirms...
[✓] Confirmed 95 / 100 notifications
[✗] Only 95/100 confirmed - 5 failed

# 所有消息最终都会被处理（重试后）
# 没有消息永久丢失
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Queues tab → Click on "notifications"
3. See queue empty (all messages delivered)
4. Click on "Get messages" → See all unprocessed messages (if any)
5. See messages getting ACKed in real-time

**View in Management UI:**

Open http://localhost:15672:
- Go to Queues tab → Click on "notifications"
- See queue state (Ready/Unacked)
- Monitor message processing in real-time
- See unacked messages when consumer is slow/crashing
- Verify messages are properly acknowledged

**Comparison:**

| Design | Reliability | Message Loss | Detectability |
|--------|-------------|--------------|---------------|
| Auto-Ack (old) | None | ~5-10% lost | Impossible |
| Manual ACK (new) | High | 0% lost | Visible in UI |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Always use manual_ack in production consumers  
- Set appropriate prefetch_count  
- Handle exceptions in callback  
- Acknowledge only after successful processing  
- Use publisher confirms for critical messages  
- Monitor unacked message count  
- Reject failed messages appropriately  
- Use DLX for failed messages  
- Test failure scenarios thoroughly  
- Log acknowledgment failures  

**❌ Don't:**
- Use auto_ack in production → Messages lost on crash  
- Acknowledge before processing → Data loss on failure  
- Forget to handle exceptions → Consumer crashes  
- Ignore unacked message count → Hidden issues  
- NACK with requeue=True on permanent failure → Infinite loop  
- Set prefetch too high → Consumer overwhelmed  
- Use publisher confirms for all messages (performance cost)  

### Prefetch Settings Guidelines

```
Long-running tasks (seconds to minutes):
prefetch_count = 1-5

Fast tasks (milliseconds):
prefetch_count = 10-100

Heavy processing (CPU/IO intensive):
prefetch_count = number_of_cpus * 2

High throughput (simple routing):
prefetch_count = 50-200
```

### Producer Confirm Best Practices

```
Critical messages (orders, payments, notifications):
✅ Use publisher confirms
✅ Wait for confirmation (or async callback)
✅ Handle confirmation failures (re-publish)
✅ Set reasonable timeout
✅ Log confirmation failures
✅ Retry on confirmation timeout

Non-critical messages (heartbeats, telemetry):
❌ Don't use publisher confirms (performance cost)
❌ Accept small message loss rate
```

### Production Considerations

**Monitoring Acknowledgments:**

```python
# Monitor unacked message count
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Get queue info
method = channel.queue_declare(queue='orders', passive=True)
queue_size = method.method.message_count
unacked = method.method.consumer_count

print(f"Queue: {queue_size} messages, {unacked} unacked")

# Alert if too many unacked messages
if unacked > 100:
    print("[ALERT] Too many unacked messages - consumers may be stuck!")
```

**Handling Consumer Crashes:**

```python
import pika
import signal
import sys

def signal_handler(signum, frame):
    print(f"\nInterrupt received ({signum}), stopping consumer...")
    sys.exit(0)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Register signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Manual acknowledgment
channel.basic_consume(queue='orders', on_message_callback=callback, auto_ack=False)

print(' [*] Consumer with graceful shutdown')
channel.start_consuming()
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's the difference between auto-ack and manual ack?**

A: Auto-ack means RabbitMQ automatically acknowledges message after delivery to consumer (no guarantee consumer processed it). Manual ack means consumer explicitly acknowledges message after processing (guarantees message processed before acknowledgment).

**Q2: What happens if a consumer crashes without sending ack?**

A: Message remains in queue as "unacked". Another consumer can redeliver and process it. If auto-ack was enabled, message would be lost permanently.

**Q3: What's prefetch_count and why is it important?**

A: Prefetch_count limits how many unacknowledged messages a consumer can receive at once. Prevents overwhelming slow consumers and ensures fair distribution across multiple consumers.

**Q4: What's the difference between basic_nack and basic_reject?**

A: basic_nack (requeue=True) redelivers message back to queue for retry. basic_reject (requeue=False) discards message (optionally to Dead Letter Exchange). Reject is for permanent failures, NACK for transient failures.

**Q5: What are publisher confirms and when should you use them?**

A: Publisher confirms are acknowledgments from RabbitMQ to producer confirming message receipt. Use when you need guarantee message reached broker (critical messages like orders, payments). Not needed for fire-and-forget messages.

### Production Pitfalls

**Pitfall 1: Using auto-ack in production**
- Problem: Messages lost when consumer crashes
- Detection: Silent data loss discovered too late
- Solution: Always use manual_ack in production

**Pitfall 2: Acknowledging before processing**
- Problem: Consumer crashes after ack but before processing completes
- Detection: Data loss, partial processing
- Solution: Ack only after successful processing completion

**Pitfall 3: Setting prefetch too high**
- Problem: Consumer overwhelmed with messages
- Detection: Consumer crashes, slow processing, high memory
- Solution: Set prefetch_count based on processing time

**Pitfall 4: NACK with requeue=True on permanent failure**
- Problem: Message fails, gets requeued, fails again (infinite loop)
- Detection: Consumer CPU 100%, queue full
- Solution: Reject or send to DLX instead of requeuing

### Advanced Acknowledgment Concepts

**Dead Letter Exchange for Failed Messages:**

```python
# Create DLX for failed messages
channel.exchange_declare(exchange='payment-dlx', exchange_type='direct')

channel.queue_declare(queue='failed-payments')

channel.queue_bind(exchange='payment-dlx', queue='failed-payments', routing_key='failed')

# Declare main queue with DLX argument
channel.queue_declare(
    queue='payments',
    arguments={
        'x-dead-letter-exchange': 'payment-dlx',
        'x-dead-letter-routing-key': 'failed'
    }
)

# Reject failed messages to DLX
def callback(ch, method, properties, body):
    try:
        process_payment(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except PermanentFailureError as e:
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        # Message goes to DLX
```

**Idempotent Processing:**

```python
# Process message with idempotency
def process_idempotent(message_id, message_data):
    """Ensure message only processed once even if delivered multiple times"""
    # Check if already processed
    if is_already_processed(message_id):
        print(f" [SKIP] Message {message_id} already processed")
        return
    
    # Process message
    result = process_message(message_data)
    mark_as_processed(message_id)
    
    return result
```

---

## 📚 Summary

Message acknowledgments provide reliability by ensuring messages aren't lost if consumers crash or fail. Manual acknowledgments (auto_ack=False) combined with appropriate error handling, prefetch settings, and Dead Letter Exchanges guarantee at-least-once delivery in RabbitMQ systems.

**Key takeaways:**
- Always use manual_ack in production consumers
- Set appropriate prefetch_count based on processing time
- Acknowledge only after successful processing
- Use basic_nack with requeue=True for transient failures
- Use basic_reject for permanent failures (or DLX)
- Publisher confirms guarantee message reaches broker
- Monitor unacked message count
- Handle exceptions gracefully in callbacks

**Next steps:**
- Practice with manual_ack in your applications
- Learn about publisher confirms in detail
- Understand Dead Letter Exchanges (next lesson)
- Explore message TTL and expiration
- Learn about transactionality and atomic operations

---

**Module 02 - Advanced RabbitMQ Features**  
**Lesson 01 - Complete**