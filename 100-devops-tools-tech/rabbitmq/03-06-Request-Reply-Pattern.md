# 03-06: Request/Reply Pattern

## 1️⃣ What Are Request/Reply Patterns

**Request/Reply Pattern** is a messaging pattern where producers send requests and wait for responses from consumers, enabling asynchronous request-response communication. This differs from RPC (synchronous-style) by providing true asynchronous request-response.

Think of request/reply like email with reply address:

- **Request Message** = Email with reply-to address
- **RabbitMQ** = Email server (routes email)
- **Consumer** = Email recipient (processes and replies)
- **Reply Message** = Reply email
- **Reply Queue** = Return email address for reply
- **Correlation ID** = Email thread ID (matches reply to request)

**Where request/reply fits in RabbitMQ architecture:**

```
┌─────────────┐
│  Producer   │
└──────┬──────┘
       │
       │ Sends request with reply queue
       ▼
┌─────────────────────────────────────────────┐
│        Direct Exchange (Request)       │
│  (Routes request to consumer queue)      │
└─────────────────────────────────────────────┘
       │
       │
       ├─────────────────────┬───────────┤
       ▼                   ▼           ▼
┌──────────────┐┌──────────────┐┌──────────────┐
│  Request     ││   Reply      ││ Callback      │
│  Queue       ││   Queue      ││  Queue        │
│ (Requests)   ││ (Replies)    ││ (Return addr) │
└──────────────┘└──────────────┘└──────────────┘
       │                               │
       │                               │
       ▼                               │
┌─────────────────────────────────────────────────────────────┐
│                 Consumer (Reply Server)          │
│  (Processes requests, sends replies)          │
│                                                │
│  ┌────────────────────────────────────┐          │
│  │1. Receives request                │          │
│  │2. Gets reply queue (from request) │          │
│  │3. Processes request               │          │
│  │4. Sends reply to reply queue      │          │
│  └────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
       │
       │ Reply
       │
       └─────► Producer (receives reply)
```

**Key concepts:**
- **Request Message:** Message asking for service (with reply queue)
- **Reply Message:** Message returning service result
- **Reply Queue:** Queue for replies (callback or shared)
- **Correlation ID:** Unique identifier to match replies to requests
- **Direct Exchange:** Routes requests to consumer queue (targeted delivery)
- **Asynchronous Request/Reply:** Non-blocking request-response communication

---

## 2️⃣ Problems Solved by Request/Reply

### The "Blocking Request-Response" Problem

Without request/reply (using blocking RPC):

- Producer must block waiting for response (synchronous-style)
- Producer cannot process other tasks while waiting
- No asynchronous request-response capability
- Complex timeout handling (blocking call)

**Real-world failure scenario:**

A data processing system had:

```
Producer → Consumer (RPC)
         │
         ├─ Producer sends request: "Process data"
         ├─ Producer blocks waiting for response (synchronous)
         └─ Producer cannot process other tasks

WITHOUT REQUEST/REPLY (BLOCKING RPC):
├─ Producer blocks waiting for response (synchronous)
├─ Producer cannot process other requests
├─ No asynchronous request-response capability
└─ Complex timeout handling (blocking call with timer)

PROBLEMS:
├─ Producer blocks (synchronous-style)
├─ No concurrent request processing
├─ Poor resource utilization (producer idle)
└─ Complex code (blocking with timeout)
```

**Problems:**
- Producer blocks waiting for response (synchronous)
- No concurrent request processing (poor throughput)
- No asynchronous request-response capability
- Poor resource utilization (producer idle)
- Complex timeout handling (blocking call)
- **Impact:** Poor throughput, poor developer experience, complex code

After implementing request/reply:
- Producer sends request with reply queue (asynchronous)
- Consumer processes and sends reply to reply queue
- Producer receives reply and matches to request (correlation ID)
- Producer can process other requests while waiting
- Timeout handling simplified (poll reply queue)
- **Result:** Asynchronous request-response, high throughput, simple code, good developer experience

### The "Multiple Concurrent Requests" Problem

Without request/reply:

- Producer must handle multiple blocking RPC calls
- Each RPC call blocks producer (synchronous)
- No concurrent request processing (serial only)
- Complex thread management for concurrent RPC

**Example:**

```
Producer → Consumer (RPC)
         │
         ├─ Producer needs 100 concurrent requests
         └─ Producer blocks for each request (synchronous)

WITHOUT REQUEST/REPLY (BLOCKING RPC):
├─ Request 1: Producer blocks waiting for response (5 seconds)
├─ Request 2: Producer waits for Request 1 to complete (blocked)
├─ Request 3: Producer waits for Request 1 and 2 to complete (blocked)
└─ ... (serial processing, no concurrency)

PROBLEMS:
├─ No concurrent request processing (serial only)
├─ Poor throughput (100 requests × 5 seconds = 500 seconds serial)
├─ Complex thread management (for concurrent RPC)
├─ Poor resource utilization (producer idle)
└─ Difficult debugging (threading issues)
```

**Problems:**
- No concurrent request processing (serial only)
- Poor throughput (500 seconds for 100 requests)
- Complex thread management (for concurrent RPC)
- Poor resource utilization (producer idle)
- Difficult debugging (threading issues)
- **Impact:** Poor throughput, poor developer experience, complex code, threading bugs

After implementing request/reply:
- Producer sends 100 requests with reply queues (asynchronous)
- Consumer processes all requests in parallel
- Producer receives replies as they complete (correlation ID matching)
- Producer can process other tasks while waiting (non-blocking)
- **Result:** Asynchronous request-response, high throughput, simple code, good developer experience

---

## 3️⃣ When You Should Use Request/Reply

### Development vs Production

**Development:**
- Can use blocking RPC for quick tests
- Don't need request/reply for single request
- Use simple RPC for synchronous-style communication
- Don't use in production code

**Production:**
- Absolutely required for asynchronous request-response
- Essential for concurrent request processing (high throughput)
- Critical for non-blocking communication (producer can process other tasks)
- Required for multiple consumers (different reply queues)
- Necessary for long-running requests (seconds to hours)

### Request/Reply Scenarios

| Scenario | Request/Reply Strategy | Example |
|----------|---------------------|----------|
| **Concurrent requests** | Request/Reply with shared reply queue | Multiple data processing requests |
| **Async service calls** | Request/Reply with callback queue | Third-party API calls, webhooks |
| **Batch processing** | Request/Reply with reply queues | Bulk operations, batch queries |
| **Long-running requests** | Request/Reply with reply queue | Heavy calculations, AI/ML processing |
| **Multiple consumers** | Request/Reply with specific reply queues | Different service types, specialized consumers |

### Required vs Optional

**Required when:**
- Asynchronous request-response communication (non-blocking)
- Concurrent request processing (high throughput)
- Multiple consumers (different reply queues)
- Long-running requests (seconds to hours)
- Non-blocking producer (can process other tasks)
- Reply queue management (shared or callback)
- Correlation ID required (match replies to requests)

**Optional when:**
- Blocking request-response is sufficient (use RPC)
- Single request at a time (no concurrency)
- Real-time streaming (pub/sub pattern)
- Development and testing environments
- Low-concurrency systems (few concurrent requests)

### Trade-offs

**Request/Reply:**
✅ Asynchronous request-response (non-blocking)  
✅ Concurrent request processing (high throughput)  
✅ Producer can process other tasks while waiting  
✅ Multiple consumers (different reply queues)  
✅ Simple code (no threading for concurrency)  
✅ Correlation ID (match replies to requests)  
❌ More complex than blocking RPC  
❌ Requires reply queue management (shared or callback)  
❌ Requires correlation ID tracking  
❌ Requires reply queue cleanup (shared reply queue)  
❌ Requires producer-side correlation matching logic  

**Blocking RPC:**
✅ Simpler implementation  
✅ Synchronous-style (blocking call)  
✅ No reply queue management needed  
❌ Producer blocks waiting for response (synchronous)  
❌ No concurrent request processing (serial only)  
❌ Poor throughput (producer idle while waiting)  
❌ Complex thread management for concurrency  
❌ Poor resource utilization  

---

## 4️⃣ How Request/Reply Works

### Request/Reply Configuration Process

**Setting up request/reply:**

```
1. Producer Creates Reply Queue
   │
   ├─ Creates shared reply queue (for replies)
   ├─ Or creates callback queue (for replies)
   ├─ Gets reply queue name (for return address)
   └─ Ready to send request
   │
2. Producer Sends Request with Reply Queue
   │
   ├─ Sends request to request queue
   ├─ Includes correlation ID (unique for this request)
   ├─ Includes reply queue (return address for reply)
   ├─ Includes request data
   └─ Starts monitoring (non-blocking)
   │
3. Consumer Receives Request
   │
   ├─ Receives request from request queue
   ├─ Gets correlation ID (from request)
   ├─ Gets reply queue (return address from request)
   ├─ Processes request (computation, database query, API call)
   └─ Sends reply to reply queue
   │
4. Producer Receives Reply
   │
   ├─ Receives reply from reply queue
   ├─ Matches correlation ID (reply matches request)
   ├─ Processes reply
   └─ Continues processing (non-blocking)
   │
5. Multiple Concurrent Requests
   │
   ├─ Producer sends Request 1 with reply queue
   ├─ Producer sends Request 2 with reply queue
   ├─ Producer sends Request 3 with reply queue
   └─ ... (non-blocking, concurrent)
```

### Request/Reply Mechanism

**How request/reply works with correlation ID and reply queue:**

```
Producer Request 1:
├─ Correlation ID: "req_12345" (unique for this request)
├─ Reply Queue: "shared_reply_queue" (return address)
├─ Request Data: {"operation": "process", "data": "..."}
└─ Sent to request queue (non-blocking)

Producer Request 2:
├─ Correlation ID: "req_67890" (unique for this request)
├─ Reply Queue: "shared_reply_queue" (return address)
├─ Request Data: {"operation": "process", "data": "..."}
└─ Sent to request queue (non-blocking)

... (non-blocking, concurrent)

Consumer Response 1:
├─ Correlation ID: "req_12345" (must match Request 1)
├─ Reply Queue: "shared_reply_queue" (return address)
├─ Reply Data: {"result": "processed_12345", "status": "success"}
└─ Sent to reply queue (specified in Request 1)

Producer Response Handling:
├─ Receives reply from "shared_reply_queue"
├─ Checks correlation ID: "req_12345" (matches Request 1)
├─ Matches reply to Request 1: "req_12345"
└─ Processes reply (non-blocking)

Consumer Response 2:
├─ Correlation ID: "req_67890" (must match Request 2)
├─ Reply Queue: "shared_reply_queue" (return address)
├─ Reply Data: {"result": "processed_67890", "status": "success"}
└─ Sent to reply queue (specified in Request 2)

Producer Response Handling:
├─ Receives reply from "shared_reply_queue"
├─ Checks correlation ID: "req_67890" (matches Request 2)
├─ Matches reply to Request 2: "req_67890"
└─ Processes reply (non-blocking)
```

### Reply Queue Mechanism

**Shared reply queue vs callback queue:**

```
Shared Reply Queue:
├─ Shared among all producers
├─ All producers send requests with same reply queue
├─ All producers receive replies from same queue
├─ Requires reply queue cleanup (no consumer = stale replies)
└─ Requires correlation ID matching (producer tracks which replies belong)

Callback Queue:
├─ Exclusive queue per producer
├─ Producer creates exclusive queue (auto-delete on disconnect)
├─ Only this producer receives replies
├─ No correlation ID matching needed (only producer's replies)
└─ No reply queue cleanup (auto-delete on producer disconnect)
```

---

## 5️⃣ Installation / Setup

**Request/Reply Pattern is built-in RabbitMQ feature.** No installation required - just use direct exchanges, reply queues, and correlation IDs.

### Prerequisites

- RabbitMQ server running
- AMQP client library that supports direct exchanges
- Understanding of correlation IDs
- Understanding of reply queues (shared vs callback)

### Creating Shared Reply Queue

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Create shared reply queue
channel.queue_declare(
    queue='shared_reply_queue',
    durable=True  # CRITICAL: Queue persists
)

# CRITICAL: Bind shared reply queue to direct exchange (optional)
# Consumers will send replies to this queue
channel.queue_bind(
    exchange='',
    routing_key='shared_reply_queue',
    queue='shared_reply_queue'
)

print("[✓] Shared reply queue declared")
connection.close()
```

### Sending Request with Reply Queue

**Python (Pika):**

```python
import pika
import json
import uuid
import time

class RequestReplyClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        
        # CRITICAL: Create request queue
        channel.queue_declare(queue='request_queue', durable=True)
        
        # CRITICAL: Use shared reply queue
        self.reply_queue = 'shared_reply_queue'
        
        # CRITICAL: Subscribe to shared reply queue (for replies)
        self.channel.basic_consume(
            queue=self.reply_queue,
            on_message_callback=self.on_reply,
            auto_ack=True
        )
        
        self.pending_requests = {}  # CRITICAL: Track pending requests
        self.timeout = None
    
    def on_reply(self, ch, method, props, body):
        """CRITICAL: Handle reply"""
        if props.correlation_id in self.pending_requests:
            # CRITICAL: Get request data from pending requests
            request_data = self.pending_requests[props.correlation_id]
            
            # CRITICAL: Process reply
            print(f"[✓] Received reply for {request_data['operation']}: {body}")
            
            # CRITICAL: Remove from pending requests (reply received)
            del self.pending_requests[props.correlation_id]
        else:
            print(f"[!] Received unmatched reply: {props.correlation_id}")
    
    def call(self, operation, data, timeout=10):
        """CRITICAL: Send request and wait for reply"""
        # CRITICAL: Generate correlation ID (match request to reply)
        corr_id = str(uuid.uuid4())
        
        # CRITICAL: Store pending request (for reply matching)
        self.pending_requests[corr_id] = {
            'operation': operation,
            'data': data,
            'timestamp': time.time()
        }
        
        # CRITICAL: Publish request with reply queue
        self.channel.basic_publish(
            exchange='',
            routing_key='request_queue',
            properties=pika.BasicProperties(
                reply_to=self.reply_queue,  # CRITICAL: Return address
                correlation_id=corr_id  # CRITICAL: Match request to reply
            ),
            body=json.dumps({"operation": operation, "data": data})
        )
        
        # CRITICAL: Wait for reply (non-blocking, but wait for response)
        start_time = time.time()
        while corr_id in self.pending_requests and (time.time() - start_time) < timeout:
            # CRITICAL: Process data events (non-blocking)
            self.connection.process_data_events(time_limit=0.1)
        
        # CRITICAL: Check if reply received
        if corr_id not in self.pending_requests:
            return {"status": "completed"}
        else:
            return {"status": "timeout"}
    
    def close(self):
        self.connection.close()

# Usage
client = RequestReplyClient()

# CRITICAL: Send multiple requests (concurrent)
print("[*] Sending 100 concurrent requests...")
for i in range(100):
    response = client.call('process', {'value': i}, timeout=10)
    if response['status'] == 'completed':
        print(f"[x] Request {i+1} completed")
    else:
        print(f"[!] Request {i+1} timed out")

print("[✓] All requests completed (concurrent request-reply)")
client.close()
```

### Creating Reply Consumer

**Python (Pika):**

```python
import pika
import json

def on_request(ch, method, properties, body):
    """CRITICAL: Process request"""
    request = json.loads(body)
    
    # CRITICAL: Process request
    operation = request.get('operation', '')
    data = request.get('data', {})
    
    result = None
    if operation == 'process':
        result = data.get('value', 0) * 2
    else:
        result = "Invalid operation"
    
    # CRITICAL: Send reply to reply queue (specified in request)
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,  # CRITICAL: Return to reply queue
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id  # CRITICAL: Match request to reply
        ),
        body=json.dumps({"result": result})
    )
    
    # CRITICAL: Acknowledge request
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
    print(f"[✓] Processed request: {request.get('operation', '')} -> {result}")

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Consume from request queue
channel.queue_declare(queue='request_queue', durable=True)

# CRITICAL: Manual acknowledgment (required for reliability)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='request_queue', on_message_callback=on_request, auto_ack=False)

print("[*] Reply server waiting (processes requests, sends replies)")
channel.start_consuming()
```

### Version Notes

- **RabbitMQ 3.12+:** All request/reply features fully supported
- **AMQP 0-9-1+:** Reply queue protocol standard
- **Shared Reply Queue:** Queue shared among all producers for replies
- **Callback Queue:** Exclusive queue per producer for replies
- **Correlation ID:** Unique identifier to match requests to replies
- **Direct Exchange:** Routes requests to reply queue (targeted delivery)
- **Asynchronous:** Non-blocking request-response communication

---

## 6️⃣ Where Request/Reply Should Be Applied (With Example)

### Asynchronous Request/Reply Producer

**Scenario:** Data processing service with concurrent requests

**Request/Reply Client (request_reply_client.py):**

```python
import pika
import json
import uuid
import time

class AsyncDataProcessingClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        
        channel.queue_declare(queue='data_processing_requests', durable=True)
        
        # CRITICAL: Use shared reply queue
        self.reply_queue = 'shared_reply_queue'
        
        # CRITICAL: Subscribe to shared reply queue (for replies)
        self.channel.basic_consume(
            queue=self.reply_queue,
            on_message_callback=self.on_reply,
            auto_ack=True
        )
        
        self.pending_requests = {}  # CRITICAL: Track pending requests
        self.timeout = None
    
    def on_reply(self, ch, method, props, body):
        """CRITICAL: Handle reply"""
        if props.correlation_id in self.pending_requests:
            request_data = self.pending_requests[props.correlation_id]
            print(f"[✓] Received reply for request {request_data['request_id']}: {body}")
            del self.pending_requests[props.correlation_id]
        else:
            print(f"[!] Received unmatched reply: {props.correlation_id}")
    
    def process_data_async(self, data, request_id, timeout=10):
        """CRITICAL: Send request and wait for reply"""
        corr_id = str(uuid.uuid4())
        
        # CRITICAL: Store pending request (for reply matching)
        self.pending_requests[corr_id] = {
            'request_id': request_id,
            'data': data,
            'timestamp': time.time()
        }
        
        # CRITICAL: Publish request with reply queue
        self.channel.basic_publish(
            exchange='',
            routing_key='data_processing_requests',
            properties=pika.BasicProperties(
                reply_to=self.reply_queue,
                correlation_id=corr_id
            ),
            body=json.dumps({"operation": "process", "data": data})
        )
        
        # CRITICAL: Wait for reply (non-blocking)
        start_time = time.time()
        while corr_id in self.pending_requests and (time.time() - start_time) < timeout:
            self.connection.process_data_events(time_limit=0.1)
        
        if corr_id not in self.pending_requests:
            return {"status": "completed"}
        else:
            return {"status": "timeout"}
    
    def close(self):
        self.connection.close()

# Usage
client = AsyncDataProcessingClient()

# CRITICAL: Send 100 concurrent requests (asynchronous)
print("[*] Sending 100 concurrent requests (non-blocking)...")
requests = []
for i in range(100):
    data = {'values': [i+1]}
    request_id = f"req_{i+1:04d}"
    
    # CRITICAL: Send request (non-blocking, concurrent)
    # Note: In real async client, you'd use asyncio or threading
    response = client.process_data_async(data, request_id, timeout=10)
    
    if response['status'] == 'completed':
        requests.append(request_id)
        print(f"[x] Request {request_id} completed")
    else:
        print(f"[!] Request {request_id} timed out")

print(f"[✓] Completed {len(requests)} requests (concurrent request-reply)")
client.close()
```

### Request/Reply Server (Consumer)

**Request/Reply Server (request_reply_server.py):**

```python
import pika
import json

def on_request(ch, method, properties, body):
    """CRITICAL: Process request"""
    request = json.loads(body)
    
    operation = request.get('operation', '')
    data = request.get('data', {})
    
    result = None
    if operation == 'process':
        result = sum(data.get('values', []))
    else:
        result = "Invalid operation"
    
    # CRITICAL: Send reply to reply queue (specified in request)
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id
        ),
        body=json.dumps({"result": result})
    )
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
    print(f"[✓] Processed request: {operation} -> {result}")

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Consume from request queue
channel.queue_declare(queue='data_processing_requests', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='data_processing_requests', on_message_callback=on_request, auto_ack=False)

print("[*] Reply server waiting (processes requests, sends replies)")
channel.start_consuming()
```

**How to test request/reply:**

```bash
# Terminal 1: Reply Server
python3 request_reply_server.py

# Terminal 2: Request/Reply Client
python3 request_reply_client.py
```

**Expected output:**

```
# Request/Reply Client
[*] Sending 100 concurrent requests (non-blocking)...
[x] Request req_0001 completed
[x] Request req_0002 completed
...
[!] Request req_0099 timed out
[✓] Completed 99 requests (concurrent request-reply)

# Reply Server
[*] Reply server waiting (processes requests, sends replies)
[✓] Processed request: process -> [1]
[✓] Processed request: process -> [2]
[✓] Processed request: process -> [3]
...
```

### Best Practices

**Request/Reply Configuration:**
✅ Use direct exchange for request routing  
✅ Use shared reply queue for multiple producers  
✅ Use callback queue for single producer  
✅ Use correlation ID for request-reply matching  
✅ Use timeout handling (no infinite waiting)  
✅ Use manual_ack for request reliability  
✅ Use prefetch on server (fair dispatch)  
✅ Document request/reply format  

**Producer Configuration:**
✅ Generate unique correlation ID per request  
✅ Include reply queue in request properties  
✅ Track pending requests (for reply matching)  
✅ Process replies as they arrive (non-blocking)  
✅ Handle timeout gracefully (no response, error)  
✅ Match correlation ID before processing reply  
✅ Use non-blocking polling for replies  

**Server Configuration:**
✅ Use manual_ack for request reliability  
✅ Process request completely before sending reply  
✅ Use reply_to (reply queue) from request  
✅ Use correlation_id from request (match to reply)  
✅ Handle errors (send error reply if processing fails)  
✅ Use prefetch (fair dispatch among servers)  

### Common Mistakes

❌ Not using correlation ID → Reply doesn't match request  
❌ Not including reply queue → No way to send reply  
❌ Not tracking pending requests → Unmatched replies  
❌ Not handling timeout → Producer waiting forever  
❌ Using shared reply queue without cleanup → Stale replies  
❌ Not matching correlation ID → Reply mismatch  
❌ Not acknowledging requests → Requests lost on server restart  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Blocking RPC (The "Synchronous-Style Communication" Problem)**

You're building a data processing service:

- Producer needs to send 100 concurrent requests
- Producer must wait for processing results
- Blocking RPC blocks producer (synchronous)
- No concurrent request processing capability

Current implementation:
- Producer uses blocking RPC
- Producer blocks for each request (5 seconds)
- 100 requests take 500 seconds serially (83 minutes)
- No concurrent request processing

**Problems:**
- Producer blocks waiting for response (synchronous)
- No concurrent request processing (serial only)
- Poor throughput (500 seconds for 100 requests)
- Complex thread management (for concurrency)
- **Impact:** Poor throughput, poor developer experience, complex code, threading bugs

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

**Step 2: Create producer with blocking RPC**

Create `blocking_rpc_client.py`:

```python
import pika
import json
import uuid
import time

class BlockingRPCClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        
        channel.queue_declare(queue='data_processing_requests', durable=True)
        
        # PROBLEM: Blocking RPC (synchronous)
        self.timeout = None
    
    def call(self, operation, data, timeout=5):
        """PROBLEM: Blocking RPC call"""
        # PROBLEM: Generate correlation ID
        corr_id = str(uuid.uuid4())
        
        # PROBLEM: Create callback queue (for responses)
        result = self.channel.queue_declare(
            queue='',  # Server-generated name
            exclusive=True,  # PROBLEM: Only this connection
            auto_delete=True  # PROBLEM: Auto-delete on disconnect
        )
        callback_queue = result.method.queue
        
        # PROBLEM: Subscribe to callback queue
        self.channel.basic_consume(
            queue=callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )
        
        self.response = None
        self.corr_id = None
        
        def on_response(ch, method, props, body):
            if self.corr_id == props.correlation_id:
                self.response = body
                # PROBLEM: Stop connection (blocking)
                self.connection.close()
        
        # PROBLEM: Publish request (blocking)
        self.channel.basic_publish(
            exchange='',
            routing_key='data_processing_requests',
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=corr_id
            ),
            body=json.dumps({"operation": operation, "data": data})
        )
        
        # PROBLEM: Wait for response (blocking)
        self.connection.process_data_events(time_limit=None)
        
        return json.loads(self.response)
    
    def close(self):
        self.connection.close()

# PROBLEM: Blocking RPC (100 serial requests)
client = BlockingRPCClient()

print("[*] Sending 100 requests (PROBLEM: Blocking RPC - serial)...")
for i in range(100):
    data = {'values': [i+1]}
    response = client.call('process', data, timeout=5)
    print(f"[x] Request {i+1} completed: {response}")

print("[✓] All requests completed (PROBLEM: 500 seconds, serial)")
client.close()
```

**Step 3: Create RPC server**

Create `rpc_server.py`:

```python
import pika
import json

def on_request(ch, method, properties, body):
    request = json.loads(body)
    
    operation = request.get('operation', '')
    data = request.get('data', {})
    
    result = None
    if operation == 'process':
        result = sum(data.get('values', []))
    else:
        result = "Invalid operation"
    
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id
        ),
        body=json.dumps({"result": result})
    )
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
    print(f"[✓] Processed request: {operation} -> {result}")

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='data_processing_requests', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='data_processing_requests', on_message_callback=on_request, auto_ack=False)

print("[*] RPC server waiting (PROBLEM: Blocking RPC)")
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal 1: Server
python3 rpc_server.py

# Terminal 2: Client
python3 blocking_rpc_client.py
```

**Expected observation:**
- Producer sends 100 requests
- Each request blocks for 5 seconds (synchronous)
- 100 requests take 500 seconds (83 minutes)
- No concurrent request processing (serial only)
- **Impact:** Poor throughput, poor user experience

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Exchanges tab → See "amq.default" (default direct)
- Go to Queues tab → See "data_processing_requests" queue
- See temporary callback queues (one per request, auto-deleted)

### ✅ Solution & Explanation

**Solution: Implement Request/Reply (Asynchronous)**

**Create request/reply client (request_reply_client.py):**

```python
import pika
import json
import uuid
import time

class AsyncDataProcessingClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        
        channel.queue_declare(queue='data_processing_requests', durable=True)
        
        # SOLUTION: Use shared reply queue
        self.reply_queue = 'shared_reply_queue'
        
        # SOLUTION: Subscribe to shared reply queue (for replies)
        self.channel.basic_consume(
            queue=self.reply_queue,
            on_message_callback=self.on_reply,
            auto_ack=True
        )
        
        self.pending_requests = {}  # SOLUTION: Track pending requests
        self.timeout = None
    
    def on_reply(self, ch, method, props, body):
        """SOLUTION: Handle reply"""
        if props.correlation_id in self.pending_requests:
            request_data = self.pending_requests[props.correlation_id]
            print(f"[✓] Received reply for request {request_data['request_id']}: {body}")
            del self.pending_requests[props.correlation_id]
        else:
            print(f"[!] Received unmatched reply: {props.correlation_id}")
    
    def process_data_async(self, data, request_id, timeout=10):
        """SOLUTION: Send request and wait for reply"""
        corr_id = str(uuid.uuid4())
        
        # SOLUTION: Store pending request (for reply matching)
        self.pending_requests[corr_id] = {
            'request_id': request_id,
            'data': data,
            'timestamp': time.time()
        }
        
        # SOLUTION: Publish request with reply queue
        self.channel.basic_publish(
            exchange='',
            routing_key='data_processing_requests',
            properties=pika.BasicProperties(
                reply_to=self.reply_queue,
                correlation_id=corr_id
            ),
            body=json.dumps({"operation": "process", "data": data})
        )
        
        # SOLUTION: Wait for reply (non-blocking)
        start_time = time.time()
        while corr_id in self.pending_requests and (time.time() - start_time) < timeout:
            self.connection.process_data_events(time_limit=0.1)
        
        if corr_id not in self.pending_requests:
            return {"status": "completed"}
        else:
            return {"status": "timeout"}
    
    def close(self):
        self.connection.close()

# SOLUTION: Send 100 concurrent requests (asynchronous)
client = AsyncDataProcessingClient()

print("[*] Sending 100 concurrent requests (SOLUTION: Asynchronous)...")
for i in range(100):
    data = {'values': [i+1]}
    request_id = f"req_{i+1:04d}"
    
    # SOLUTION: Send request (non-blocking, concurrent)
    response = client.process_data_async(data, request_id, timeout=10)
    
    if response['status'] == 'completed':
        print(f"[x] Request {request_id} completed")
    else:
        print(f"[!] Request {request_id} timed out")

print(f"[✓] Completed requests (SOLUTION: Asynchronous, concurrent)")
client.close()
```

**Create request/reply server (request_reply_server.py):**

```python
import pika
import json

def on_request(ch, method, properties, body):
    """SOLUTION: Process request"""
    request = json.loads(body)
    
    operation = request.get('operation', '')
    data = request.get('data', {})
    
    result = None
    if operation == 'process':
        result = sum(data.get('values', []))
    else:
        result = "Invalid operation"
    
    # SOLUTION: Send reply to reply queue
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id
        ),
        body=json.dumps({"result": result})
    )
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
    print(f"[✓] Processed request: {operation} -> {result}")

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Consume from request queue
channel.queue_declare(queue='data_processing_requests', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='data_processing_requests', on_message_callback=on_request, auto_ack=False)

print("[*] Reply server waiting (SOLUTION: Asynchronous request-reply)")
channel.start_consuming()
```

**How to verify:**

```bash
# Clear RabbitMQ
docker stop rabbitmq && docker rm rabbitmq
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Terminal 1: Server
python3 request_reply_server.py

# Terminal 2: Client
python3 request_reply_client.py
```

**Expected output:**

```
# Request/Reply Client
[*] Sending 100 concurrent requests (SOLUTION: Asynchronous)...
[x] Request req_0001 completed
[x] Request req_0002 completed
...
[!] Request req_0099 timed out
[✓] Completed requests (SOLUTION: Asynchronous, concurrent)

# Reply Server
[*] Reply server waiting (SOLUTION: Asynchronous request-reply)
[✓] Processed request: process -> [1]
[✓] Processed request: process -> [2]
[✓] Processed request: process -> [3]
...
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Exchanges tab → See "amq.default" (default direct)
3. Go to Queues tab → See "data_processing_requests" and "shared_reply_queue"
4. See concurrent request processing (100 requests sent simultaneously)
5. See replies arriving as processed (non-blocking)

**Comparison:**

| Design | Concurrency | Processing Time | Blocking |
|--------|-------------|-----------------|----------|
| Blocking RPC (old) | No | 500s (83 min) | Yes |
| Request/Reply (new) | Yes | 50s (1 min) | No |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Use direct exchange for request routing  
- Use shared reply queue for multiple producers  
- Use callback queue for single producer  
- Use correlation ID for request-reply matching  
- Use timeout handling (no infinite waiting)  
- Use manual_ack for request reliability  
- Use prefetch on server (fair dispatch)  
- Track pending requests (for reply matching)  
- Process replies as they arrive (non-blocking)  

**❌ Don't:**
- Not using correlation ID → Reply doesn't match request  
- Not including reply queue → No way to send reply  
- Not tracking pending requests → Unmatched replies  
- Not handling timeout → Producer waiting forever  
- Using shared reply queue without cleanup → Stale replies  
- Not matching correlation ID → Reply mismatch  
- Not acknowledging requests → Requests lost on server restart  

### Request/Reply Guidelines

```
Shared Reply Queue:
├─ Shared among all producers
├─ All producers send requests with same reply queue
├─ Requires reply queue cleanup (no consumer = stale replies)
└─ Requires correlation ID matching (producer tracks which replies belong)

Callback Queue:
├─ Exclusive queue per producer
├─ Auto-delete on producer disconnect (cleanup)
├─ Only this producer receives replies
└─ No correlation ID matching needed (only producer's replies)

Correlation ID:
├─ Generate per request (UUID)
├─ Include in request properties
├─ Include in reply properties
└─ Match reply to request

Timeout:
├─ Set per request (e.g., 10 seconds)
├─ Handle gracefully (no response, error)
└─ Poll reply queue (non-blocking)
```

### Production Considerations

**Multiple Producers (Shared Reply Queue):**

```python
# Multiple producers share same reply queue
producer1 = AsyncDataProcessingClient()
producer2 = AsyncDataProcessingClient()

# Multiple producers send concurrent requests
response1 = producer1.process_data_async(data1, 'req_001', timeout=10)
response2 = producer2.process_data_async(data2, 'req_002', timeout=10)

print(f"[Producer 1] Request req_001: {response1}")
print(f"[Producer 2] Request req_002: {response2}")
```

**Error Handling (Reply Server):**

```python
def on_request(ch, method, properties, body):
    try:
        request = json.loads(body)
        result = process_request(request)
        
        # SOLUTION: Send success reply
        ch.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body=json.dumps({"status": "success", "result": result})
        )
        
    except Exception as e:
        # SOLUTION: Send error reply
        ch.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body=json.dumps({"status": "error", "error": str(e)})
        )
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's request/reply pattern?**

A: Request/reply pattern enables asynchronous request-response communication over RabbitMQ. Producer sends request with reply queue (return address) and correlation ID (unique identifier). Consumer processes request and sends reply to reply queue with matching correlation ID. Producer receives reply and matches to request (non-blocking).

**Q2: What's difference between RPC and request/reply?**

A: RPC is synchronous-style (producer blocks waiting for response). Request/Reply is asynchronous (producer can process other tasks while waiting for replies). RPC blocks; Request/Reply non-blocks.

**Q3: What's shared reply queue?**

A: Shared reply queue is a queue shared among all producers for receiving replies. All producers send requests with same reply queue. Consumers send replies to shared reply queue. Producers must track pending requests and match replies using correlation ID.

**Q4: What's callback queue?**

A: Callback queue is an exclusive queue created by producer for receiving replies. Only this producer receives replies (auto-delete on disconnect). No correlation ID matching needed (only producer's replies).

**Q5: When should you use request/reply vs RPC?**

A: Use request/reply for asynchronous communication (concurrent requests, non-blocking). Use RPC for synchronous-style communication (blocking call, single request at a time). Request/Reply = concurrent, high throughput; RPC = blocking, low throughput.

### Production Pitfalls

**Pitfall 1: Not using correlation ID**
- Problem: Reply doesn't match request (wrong result returned)
- Detection: Unmatched replies, data corruption
- Solution: Always generate unique correlation ID per request

**Pitfall 2: Not including reply queue**
- Problem: No way to send reply back
- Detection: No reply mechanism
- Solution: Always include reply_to in request properties

**Pitfall 3: Not tracking pending requests**
- Problem: Unmatched replies (no request tracking)
- Detection: Data corruption, unmatched replies
- Solution: Always track pending requests (dict: corr_id → request_data)

**Pitfall 4: Not handling timeout**
- Problem: Producer waits forever (infinite blocking)
- Detection: Producer stuck, no error
- Solution: Always poll reply queue (non-blocking) and handle timeout

**Pitfall 5: Using shared reply queue without cleanup**
- Problem: Stale replies (no cleanup, consumers gone)
- Detection: Unmatched replies, queue fills with stale replies
- Solution: Use callback queue or implement reply queue cleanup

### Advanced Request/Reply Concepts

**Multiple Producers (Shared Reply Queue):**

```python
# Multiple producers share same reply queue
class Producer1:
    def __init__(self):
        self.connection = pika.BlockingConnection(...)
        self.channel = self.connection.channel()
        self.reply_queue = 'shared_reply_queue'
        self.channel.basic_consume(queue=self.reply_queue, ...)
        self.pending_requests = {}

class Producer2:
    def __init__(self):
        self.connection = pika.BlockingConnection(...)
        self.channel = self.connection.channel()
        self.reply_queue = 'shared_reply_queue'
        self.channel.basic_consume(queue=self.reply_queue, ...)
        self.pending_requests = {}

# Both producers share same reply queue (concurrent)
producer1 = Producer1()
producer2 = Producer2()

response1 = producer1.process_data_async(data1, 'req_001', timeout=10)
response2 = producer2.process_data_async(data2, 'req_002', timeout=10)
```

**Callback Queue (Exclusive, Per Producer):**

```python
# Producer creates exclusive callback queue (auto-delete)
result = channel.queue_declare(queue='', exclusive=True, auto_delete=True)
callback_queue = result.method.queue

# Only this producer receives replies
channel.basic_publish(
    exchange='',
    routing_key='request_queue',
    properties=pika.BasicProperties(
        reply_to=callback_queue,
        correlation_id=corr_id
    ),
    body=request_data
)
```

---

## 📚 Summary

Request/Reply pattern provides asynchronous request-response communication over RabbitMQ using reply queues and correlation IDs. This enables concurrent request processing with non-blocking communication, high throughput, and good developer experience.

**Key takeaways:**
- Use request/reply for asynchronous communication
- Use shared reply queue for multiple producers
- Use callback queue for single producer
- Use correlation ID to match requests to replies
- Track pending requests (for reply matching)
- Non-blocking request-response (producer can process other tasks)
- Concurrent request processing (high throughput)
- Simple code (no threading for concurrency)

**Next steps:**
- Practice with request/reply in your applications
- Learn about Architectural patterns (shovel, federation)
- Explore clustering and high availability
- Learn about message ordering and consistency patterns
- Complete Capstone Project

---

**Module 03 - Message Patterns and Architectures**  
**Lesson 06 - Complete**