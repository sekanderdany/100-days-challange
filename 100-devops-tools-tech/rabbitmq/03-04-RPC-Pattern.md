# 03-04: RPC (Remote Procedure Call) Pattern

## 1️⃣ What Are RPC (Remote Procedure Call) Patterns

**RPC Pattern** enables request-response style communication over RabbitMQ, allowing producers to send requests and wait for responses from consumers. This mimics traditional function calls but uses messaging for decoupling and reliability.

Think of RPC like making a phone call:

- **RPC Request** = Phone call placed
- **RabbitMQ** = Phone network (routes call)
- **Consumer** = Service provider (answers call)
- **RPC Response** = Phone call answer
- **Callback Queue** = Return phone number for response

**Where RPC fits in RabbitMQ architecture:**

```
┌─────────────┐
│  Producer   │
└──────┬──────┘
       │
       │ Sends RPC request (call) + Callback queue
       ▼
┌─────────────────────────────────────────────┐
│         Direct Exchange (RPC)        │
│  (Routes request to response queue)     │
└──────┬────────────────────────────────┬─┘
       │                               │
       ├─────────────────────┬───────────┤
       ▼                   ▼           ▼
┌──────────────┐┌──────────────┐┌──────────────┐
│  Request     ││ Response     ││  Callback     │
│  Queue       ││  Queue       ││  Queue        │
│ (Requests)   ││ (Responses)  ││ (Return addr) │
└──────────────┘└──────────────┘└──────────────┘
       │                               │
       │                               │
       ▼                               │
┌─────────────────────────────────────────────────────────────┐
│                 Consumer (RPC Server)          │
│  (Processes requests, sends responses)          │
│                                      │
│  ┌────────────────────────────────────┐         │
│  │ 1. Receives request          │         │
│  │ 2. Processes request          │         │
│  │ 3. Sends response to callback │         │
│  └────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
       │
       │ Response
       │
       └─────► Producer (receives response)
```

**Key concepts:**
- **RPC Request:** Message asking for service (like function call)
- **RPC Response:** Message returning service result
- **Callback Queue:** Temporary queue for responses (return address)
- **Correlation ID:** Unique identifier to match responses to requests
- **Direct Exchange:** Routes requests to response queue (targeted delivery)
- **Timeout Handling:** Request timeout if response not received

---

## 2️⃣ Problems Solved by RPC Patterns

### The "Synchronous-Style Communication" Problem

Without RPC:

- Need synchronous request-response (like REST API)
- RabbitMQ is inherently asynchronous
- No built-in mechanism for request-response
- Producer must implement complex callback mechanism

**Real-world failure scenario:**

A data processing system had:

```
Producer → RabbitMQ → Consumer
         │
         ├─ Producer sends request: "Process data"
         ├─ Producer must wait for response: "Processing result"
         └─ RabbitMQ: No built-in request-response

WITHOUT RPC:
├─ Producer sends request to queue
├─ Consumer processes request in background
├─ Producer has no way to get response
├─ Producer must poll for response (inefficient)
└─ No correlation between request and response

PROBLEMS:
├─ No built-in request-response mechanism
├─ Producer cannot wait for response synchronously
├─ Complex polling logic required
├─ No guarantee response matches request
└─ Timeout handling difficult
```

**Problems:**
- No synchronous-style communication
- Producer must implement callback mechanism
- No correlation between request and response
- No timeout handling built-in
- Complex code for request-response
- **Impact:** Complex code, difficult debugging, poor developer experience

After implementing RPC:
- Producer sends request with callback queue
- Consumer processes and sends response to callback queue
- Producer receives response and matches to request (correlation ID)
- Timeout handling built-in
- **Result:** Synchronous-style communication over async RabbitMQ, simple code, easy debugging

### The "Service Decoupling" Problem

Without RPC:

- Tight coupling between producer and consumer (direct HTTP calls)
- Producer must know about consumer (URL, port)
- No resilience (consumer downtime = producer errors)
- No load balancing (single consumer instance)

**Example:**

```
Producer → Consumer (HTTP)
         │
         ├─ Producer knows: http://consumer:8080/api/process
         ├─ Producer calls: POST /api/process
         └─ Consumer returns: {"result": "processed"}

WITHOUT RPC (HTTP):
├─ Producer knows about consumer URL (tight coupling)
├─ Producer implements HTTP client
├─ No load balancing (single consumer instance)
├─ Consumer downtime = Producer errors
└─ No message reliability (no queue buffering)

PROBLEMS:
├─ Tight coupling (producer knows consumer URL)
├─ Producer implements HTTP client (language-specific)
├─ No load balancing (single instance)
├─ Consumer downtime = Producer errors
└─ No message buffering (direct HTTP, no queue)
```

**Problems:**
- Tight coupling between producer and consumer
- Producer implements consumer-specific client (HTTP)
- No load balancing (single consumer instance)
- Consumer downtime = producer errors
- No message buffering (no queue)
- **Impact:** Poor reliability, tight coupling, no scalability, poor developer experience

After implementing RPC:
- Producer sends request to RabbitMQ queue (decoupled)
- Consumer reads from queue, processes, sends response (resilient)
- Multiple consumers for load balancing (horizontal scaling)
- Message buffering in queue (consumer can catch up)
- **Result:** Decoupled, resilient, scalable, reliable

---

## 3️⃣ When You Should Use RPC Patterns

### Development vs Production

**Development:**
- Can use direct HTTP calls for quick tests
- Don't need RPC for simple request-response
- Use REST API for synchronous communication
- Don't use in production code

**Production:**
- Absolutely required for decoupled request-response
- Essential for resilient service communication (queue buffering)
- Critical for load balancing (multiple consumers)
- Required for timeout handling and correlation
- Necessary for service-to-service communication (microservices)

### RPC Scenario

| Scenario | RPC Strategy | Example |
|----------|---------------|----------|
| **Service request-response** | RPC with callback queue | Data processing, image resizing, PDF generation |
| **Microservices communication** | RPC with callback queue | Service-to-service calls, internal APIs |
| **Computation offloading** | RPC with callback queue | Heavy calculations, AI/ML processing |
| **Query execution** | RPC with callback queue | Database queries, API calls |

### Required vs Optional

**Required when:**
- Synchronous-style request-response communication
- Decoupled producer-consumer (don't want producer to know consumer)
- Message reliability required (queue buffering)
- Load balancing required (multiple consumers)
- Timeout handling required (no infinite waiting)
- Correlation ID required (match responses to requests)

**Optional when:**
- Simple direct communication (use direct exchange)
- Fire-and-forget messages (no response needed)
- One-way communication (notifications, events)
- Real-time streaming (pub/sub pattern)
- Development and testing environments

### Trade-offs

**RPC Pattern:**
✅ Synchronous-style communication over async RabbitMQ  
✅ Decoupled producer-consumer (queue buffering)  
✅ Load balancing (multiple consumers)  
✅ Message reliability (queue buffering)  
✅ Timeout handling (no infinite waiting)  
✅ Correlation ID (match responses to requests)  
❌ More complex than direct HTTP calls  
❌ More latency (round-trip through queue)  
❌ Requires callback queue management  
❌ Requires correlation ID tracking  
❌ Timeout handling complexity  

**Direct HTTP (No RPC):**
✅ Simpler implementation  
✅ Lower latency (direct HTTP call)  
✅ Synchronous by default  
❌ Tight coupling (producer knows consumer URL)  
❌ No message buffering (direct HTTP, no queue)  
❌ No load balancing (single consumer instance)  
❌ No resilience (consumer downtime = errors)  

---

## 4️⃣ How RPC Patterns Work

### RPC Configuration Process

**Setting up RPC:**

```
1. Producer Creates Callback Queue
   │
   ├─ Creates temporary exclusive queue (for responses)
   ├─ Gets callback queue name (for return address)
   └─ Ready to send RPC request
   │
2. Producer Sends RPC Request
   │
   ├─ Sends request to request queue
   ├─ Includes correlation ID (unique for this request)
   ├─ Includes callback queue (return address for response)
   ├─ Includes request data
   └─ Starts timeout timer
   │
3. Consumer Receives RPC Request
   │
   ├─ Receives request from request queue
   ├─ Gets correlation ID (from request)
   ├─ Gets callback queue (return address)
   ├─ Processes request (computation, database query, API call)
   └─ Sends response to callback queue
   │
4. Producer Receives RPC Response
   │
   ├─ Receives response from callback queue
   ├─ Matches correlation ID (response matches request)
   ├─ Processes response
   └─ Cancels timeout timer (response received)
   │
5. Timeout Handler
   │
   └─ If no response within timeout, request fails (no match)
```

### RPC Mechanism

**How RPC works with correlation ID:**

```
Producer Request:
├─ Correlation ID: "req_12345" (unique for this request)
├─ Callback Queue: "callback_queue_abc" (return address)
├─ Request Data: {"operation": "process", "data": "..."}
└─ Sent to request queue

Consumer Response:
├─ Correlation ID: "req_12345" (must match request)
├─ Callback Queue: "callback_queue_abc" (return address)
├─ Response Data: {"result": "processed", "status": "success"}
└─ Sent to callback queue (specified in request)

Producer Response Handling:
├─ Receives response from callback_queue
├─ Checks correlation ID: "req_12345"
├─ Matches response to request: "req_12345"
└─ Processes response
```

### Timeout Mechanism

**How timeout works:**

```
Producer Sends Request:
├─ Correlation ID: "req_12345"
├─ Timeout: 5 seconds
└─ Starts timer

Timer:
├─ 0 seconds: Waiting for response...
├─ 1 second: Waiting for response...
├─ 2 seconds: Waiting for response...
├─ 3 seconds: Waiting for response...
├─ 4 seconds: Waiting for response...
├─ 5 seconds: TIMEOUT!
└─ Request failed (no response)

Response Received:
├─ 2 seconds: Response received!
├─ Correlation ID matches: "req_12345"
├─ Timer cancelled
└─ Response processed
```

---

## 5️⃣ Installation / Setup

**RPC Pattern is built-in RabbitMQ feature.** No installation required - just use direct exchanges and callback queues.

### Prerequisites

- RabbitMQ server running
- AMQP client library that supports direct exchanges
- Understanding of correlation IDs
- Understanding of callback queues

### Creating RPC Request Queue

**Python (Pika):**

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# CRITICAL: Create RPC request queue
channel.queue_declare(
    queue='rpc_requests',
    durable=True  # CRITICAL: Queue persists (survives restart)
)

print("[✓] RPC request queue declared")
connection.close()
```

### Sending RPC Request

**Python (Pika):**

```python
import pika
import json
import uuid

class RPCClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        
        # CRITICAL: Create RPC request queue
        channel.queue_declare(queue='rpc_requests', durable=True)
        
        # CRITICAL: Create callback queue (for responses)
        result = self.channel.queue_declare(
            queue='',  # Server-generated name
            exclusive=True,  # CRITICAL: Only this connection
            auto_delete=True  # CRITICAL: Auto-delete on disconnect
        )
        self.callback_queue = result.method.queue
        
        # CRITICAL: Subscribe to callback queue (for responses)
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )
        
        self.response = None
        self.corr_id = None
        self.timeout = None
    
    def on_response(self, ch, method, props, body):
        """CRITICAL: Handle RPC response"""
        if self.corr_id == props.correlation_id:
            self.response = body
            # CRITICAL: Cancel timeout when response received
            if self.timeout:
                self.timeout.cancel()
    
    def call(self, request_data, timeout=5):
        """CRITICAL: Send RPC request and wait for response"""
        # CRITICAL: Generate correlation ID (match request to response)
        self.corr_id = str(uuid.uuid4())
        
        # CRITICAL: Publish RPC request with callback queue
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_requests',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,  # CRITICAL: Return address
                correlation_id=self.corr_id  # CRITICAL: Match request to response
            ),
            body=json.dumps(request_data)
        )
        
        # CRITICAL: Set timeout timer
        self.timeout = self.connection.add_timeout(
            timeout, lambda: self.connection.call_later(0, self.on_timeout)
        )
        
        # CRITICAL: Wait for response (blocking)
        self.connection.process_data_events(time_limit=None)
        
        # CRITICAL: Return response
        return json.loads(self.response)
    
    def on_timeout(self):
        """CRITICAL: Handle timeout"""
        print("[!] RPC call timed out")
        self.response = None
    
    def close(self):
        self.connection.close()

# Usage
client = RPCClient()

# CRITICAL: Send RPC request
request = {
    "operation": "process",
    "data": {"value": 42}
}

print("[*] Sending RPC request...")
response = client.call(request, timeout=5)

print(f"[✓] RPC response: {response}")
client.close()
```

### Creating RPC Server (Consumer)

**Python (Pika):**

```python
import pika
import json

def on_request(ch, method, properties, body):
    """CRITICAL: Process RPC request"""
    request = json.loads(body)
    
    # CRITICAL: Process request
    operation = request.get('operation', '')
    data = request.get('data', {})
    
    result = None
    if operation == 'process':
        result = data.get('value', 0) * 2
    else:
        result = "Invalid operation"
    
    # CRITICAL: Send RPC response to callback queue
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,  # CRITICAL: Return to callback queue
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id  # CRITICAL: Match request to response
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

# CRITICAL: Consume from RPC request queue
channel.queue_declare(queue='rpc_requests', durable=True)

# CRITICAL: Manual acknowledgment (required for reliability)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_requests', on_message_callback=on_request, auto_ack=False)

print("[*] RPC server waiting (processes requests)")
channel.start_consuming()
```

### Version Notes

- **RabbitMQ 3.12+:** All RPC features fully supported
- **AMQP 0-9-1+:** Callback queue protocol standard
- **Callback Queue:** Temporary exclusive queue for responses
- **Correlation ID:** Unique identifier to match requests to responses
- **Timeout:** Producer timeout if no response received
- **Direct Exchange:** Routes requests to response queue (targeted delivery)

---

## 6️⃣ Where RPC Should Be Applied (With Example)

### RPC Client (Producer)

**Scenario:** Data processing service that processes heavy computations

**RPC Client (rpc_client.py):**

```python
import pika
import json
import uuid

class DataProcessingClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        
        channel.queue_declare(queue='data_processing_requests', durable=True)
        
        # CRITICAL: Create callback queue
        result = channel.queue_declare(
            queue='',
            exclusive=True,
            auto_delete=True
        )
        self.callback_queue = result.method.queue
        
        # CRITICAL: Subscribe to callback queue
        channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )
        
        self.response = None
        self.corr_id = None
        self.timeout = None
    
    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
            if self.timeout:
                self.timeout.cancel()
    
    def process_data(self, data, timeout=10):
        """CRITICAL: Send RPC request for data processing"""
        self.corr_id = str(uuid.uuid4())
        
        request = {
            "operation": "process",
            "data": data
        }
        
        self.channel.basic_publish(
            exchange='',
            routing_key='data_processing_requests',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=json.dumps(request)
        )
        
        self.timeout = self.connection.add_timeout(
            timeout, lambda: self.connection.call_later(0, self.on_timeout)
        )
        
        self.connection.process_data_events(time_limit=None)
        
        return json.loads(self.response)
    
    def on_timeout(self):
        print("[!] Data processing timed out")
        self.response = None
    
    def close(self):
        self.connection.close()

# Usage
client = DataProcessingClient()

# CRITICAL: Send RPC request
data = {
    "values": [1, 2, 3, 4, 5]
}

print("[*] Sending data processing request...")
response = client.process_data(data, timeout=10)

print(f"[✓] Data processing result: {response.get('result', [])}")
client.close()
```

### RPC Server (Consumer)

**RPC Server (rpc_server.py):**

```python
import pika
import json

def on_request(ch, method, properties, body):
    """CRITICAL: Process data processing request"""
    request = json.loads(body)
    
    operation = request.get('operation', '')
    data = request.get('data', [])
    
    result = None
    if operation == 'process':
        # CRITICAL: Process data (heavy computation)
        result = sum(data)
    else:
        result = "Invalid operation"
    
    # CRITICAL: Send RPC response
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id
        ),
        body=json.dumps({"result": result})
    )
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
    print(f"[✓] Processed data: {data} -> {result}")

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='data_processing_requests', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='data_processing_requests', on_message_callback=on_request, auto_ack=False)

print("[*] RPC server waiting (data processing)")
channel.start_consuming()
```

**How to test RPC:**

```bash
# Terminal 1: RPC Server
python3 rpc_server.py

# Terminal 2: RPC Client
python3 rpc_client.py
```

**Expected output:**

```
# RPC Client
[*] Sending data processing request...
[✓] Data processing result: 15

# RPC Server
[*] RPC server waiting (data processing)
[✓] Processed data: [1, 2, 3, 4, 5] -> 15
```

### Best Practices

**RPC Configuration:**
✅ Use direct exchange for request routing  
✅ Use temporary callback queues (auto-delete)  
✅ Use correlation ID for request-response matching  
✅ Use timeout handling (no infinite waiting)  
✅ Use manual_ack for request reliability  
✅ Use prefetch on server (fair dispatch)  
✅ Document request/response format  

**Client Configuration:**
✅ Generate unique correlation ID per request  
✅ Use temporary callback queue (exclusive, auto-delete)  
✅ Set timeout (no infinite waiting)  
✅ Handle timeout gracefully (no response, error)  
✅ Match correlation ID (response matches request)  
✅ Process response only if correlation matches  

**Server Configuration:**
✅ Use manual_ack for request reliability  
✅ Process request completely before sending response  
✅ Use reply_to (callback queue) from request  
✅ Use correlation_id from request (match to response)  
✅ Handle errors (send error response if processing fails)  
✅ Use prefetch (fair dispatch among servers)  
✅ Process requests efficiently (heavy computation)  

### Common Mistakes

❌ Not using correlation ID → Response doesn't match request  
❌ Not using callback queue → No way to send response  
❌ Not using timeout → Infinite waiting (producer stuck)  
❌ Using durable callback queue → Queue persists (cleanup issue)  
❌ Not matching correlation ID → Response mismatch  
❌ Not handling timeout → Producer stuck forever  
❌ Not acknowledging requests → Requests lost on server restart  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**No Request-Response (The "Fire-and-Forget" Problem)**

You're building a data processing service:

- Producer needs to send data for processing
- Producer must wait for processing result
- RabbitMQ is inherently asynchronous
- No built-in request-response mechanism

Current implementation:
- Producer sends message to queue
- Consumer processes in background
- Producer has no way to get result
- No correlation between request and response

**Problems:**
- No synchronous-style communication
- Producer cannot wait for response
- No correlation between request and response
- No timeout handling
- Complex polling logic required
- **Impact:** Poor developer experience, complex code, difficult debugging

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

**Step 2: Create producer without RPC**

Create `no_rpc_producer.py`:

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: No request-response mechanism
channel.queue_declare(queue='data_processing')

# PROBLEM: Send request without callback (no way to get result)
data = {"values": [1, 2, 3, 4, 5]}

channel.basic_publish(
    exchange='',
    routing_key='data_processing',
    body=json.dumps(data)
)

print("[x] Sent data processing request (PROBLEM: No way to get result)")
connection.close()
```

**Step 3: Create consumer without RPC**

Create `no_rpc_server.py`:

```python
import pika
import json

def on_request(ch, method, properties, body):
    data = json.loads(body)
    
    # PROBLEM: No way to send result back
    result = sum(data.get('values', []))
    
    # PROBLEM: No callback queue, no correlation ID
    print(f"[✓] Processed data: {data.get('values', [])} -> {result}")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue='data_processing')
channel.basic_consume(queue='data_processing', on_message_callback=on_request)

print("[*] Server waiting (PROBLEM: No request-response)")
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal 1: Server
python3 no_rpc_server.py

# Terminal 2: Producer
python3 no_rpc_producer.py
```

**Expected observation:**
- Producer sends request
- Consumer processes in background
- Producer has no way to get result
- No correlation between request and result
- **Impact:** Poor developer experience, no request-response, complex code

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Queues tab → See "data_processing" queue
- No callback queue (no request-response)
- No correlation ID visible

### ✅ Solution & Explanation

**Solution: Implement RPC Pattern**

**Create RPC client (rpc_client.py):**

```python
import pika
import json
import uuid

class DataProcessingClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        
        channel.queue_declare(queue='data_processing_requests', durable=True)
        
        # SOLUTION: Create callback queue (for responses)
        result = channel.queue_declare(
            queue='',  # Server-generated name
            exclusive=True,  # SOLUTION: Only this connection
            auto_delete=True  # SOLUTION: Auto-delete on disconnect
        )
        self.callback_queue = result.method.queue
        
        # SOLUTION: Subscribe to callback queue
        channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )
        
        self.response = None
        self.corr_id = None
        self.timeout = None
    
    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
            if self.timeout:
                self.timeout.cancel()
    
    def process_data(self, data, timeout=10):
        """SOLUTION: Send RPC request for data processing"""
        self.corr_id = str(uuid.uuid4())
        
        request = {
            "operation": "process",
            "data": data
        }
        
        # SOLUTION: Send request with callback queue and correlation ID
        self.channel.basic_publish(
            exchange='',
            routing_key='data_processing_requests',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,  # SOLUTION: Return address
                correlation_id=self.corr_id  # SOLUTION: Match request to response
            ),
            body=json.dumps(request)
        )
        
        # SOLUTION: Set timeout timer
        self.timeout = self.connection.add_timeout(
            timeout, lambda: self.connection.call_later(0, self.on_timeout)
        )
        
        # SOLUTION: Wait for response (blocking)
        self.connection.process_data_events(time_limit=None)
        
        return json.loads(self.response)
    
    def on_timeout(self):
        print("[!] Data processing timed out")
        self.response = None
    
    def close(self):
        self.connection.close()

# SOLUTION: Send RPC request
client = DataProcessingClient()

data = {"values": [1, 2, 3, 4, 5]}

print("[*] Sending data processing request...")
response = client.process_data(data, timeout=10)

print(f"[✓] Data processing result: {response.get('result', [])}")
client.close()
```

**Create RPC server (rpc_server.py):**

```python
import pika
import json

def on_request(ch, method, properties, body):
    """SOLUTION: Process data processing request"""
    request = json.loads(body)
    
    operation = request.get('operation', '')
    data = request.get('data', [])
    
    result = None
    if operation == 'process':
        result = sum(data)
    else:
        result = "Invalid operation"
    
    # SOLUTION: Send RPC response to callback queue
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id  # SOLUTION: Match request to response
        ),
        body=json.dumps({"result": result})
    )
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
    print(f"[✓] Processed data: {data} -> {result}")

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# SOLUTION: Consume from RPC request queue
channel.queue_declare(queue='data_processing_requests', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='data_processing_requests', on_message_callback=on_request, auto_ack=False)

print("[*] RPC server waiting (SOLUTION: Request-response)")
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
python3 rpc_server.py

# Terminal 2: Client
python3 rpc_client.py
```

**Expected output:**

```
# RPC Client
[*] Sending data processing request...
[✓] Data processing result: 15

# RPC Server
[*] RPC server waiting (SOLUTION: Request-response)
[✓] Processed data: [1, 2, 3, 4, 5] -> 15
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Exchanges tab → See "amq.default" (default direct)
3. Go to Queues tab → See "data_processing_requests" queue
4. See temporary callback queue (auto-deleted on client disconnect)
5. See correlation ID in message properties

**Comparison:**

| Design | Request-Response | Coupling | Timeout |
|--------|-----------------|-----------|---------|
| No RPC (old) | No | High (direct) | None (infinite wait) |
| RPC (new) | Yes | Low (queue) | Yes (built-in) |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Use direct exchange for request routing  
- Use temporary callback queues (auto-delete, exclusive)  
- Use correlation ID for request-response matching  
- Use timeout handling (no infinite waiting)  
- Use manual_ack for request reliability  
- Use prefetch on server (fair dispatch)  
- Document request/response format  
- Handle errors gracefully (send error response)  

**❌ Don't:**
- Not using correlation ID → Response doesn't match request  
- Not using callback queue → No way to send response  
- Not using timeout → Infinite waiting (producer stuck)  
- Using durable callback queue → Queue persists (cleanup issue)  
- Not matching correlation ID → Response mismatch  
- Not acknowledging requests → Requests lost on server restart  
- Not handling timeout → Producer stuck forever  

### RPC Guidelines

```
Correlation ID:
├─ Generate per request (UUID)
├─ Include in request properties
├─ Include in response properties
└─ Match response to request

Callback Queue:
├─ Temporary (exclusive, auto-delete)
├─ Server-generated name
├─ Reply_to: Return address
└─ Auto-delete on client disconnect

Timeout:
├─ Set per request (e.g., 5 seconds)
├─ Handle gracefully (no response, error)
└─ Cancel timeout when response received

Server:
├─ Manual_ack for reliability
├─ Prefetch for fair dispatch
└─ Process completely before responding
```

### Production Considerations

**Multiple RPC Servers (Load Balancing):**

```python
# Multiple servers share same request queue
server1 = DataProcessingServer()
server2 = DataProcessingServer()

# Both servers consume from same queue (load balancing)
# Requests distributed between servers
```

**Error Handling:**

```python
def on_request(ch, method, properties, body):
    try:
        request = json.loads(body)
        result = process_request(request)
        
        # SOLUTION: Send success response
        ch.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body=json.dumps({"status": "success", "result": result})
        )
        
    except Exception as e:
        # SOLUTION: Send error response
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

**Q1: What's RPC pattern in RabbitMQ?**

A: RPC pattern enables request-response style communication over RabbitMQ. Producer sends request with callback queue (return address) and correlation ID (unique identifier). Consumer processes request and sends response to callback queue with matching correlation ID. Producer receives response and matches to request.

**Q2: What's correlation ID?**

A: Correlation ID is a unique identifier generated by producer for each RPC request. Included in request properties and response properties. Used to match responses to specific requests (ensures correct response for correct request).

**Q3: What's callback queue?**

A: Callback queue is a temporary exclusive queue created by producer for receiving RPC responses. Producers publish reply_to (callback queue) in request properties. Consumers send responses to callback queue (specified in request). Auto-deleted on producer disconnect (cleanup).

**Q4: How do you handle timeout in RPC?**

A: Set timeout timer when sending request. If response not received within timeout, request fails (no match). Use RabbitMQ connection timeout (add_timeout) or manual timeout tracking.

**Q5: When should you use RPC vs pub/sub?**

A: Use RPC for request-response communication (service calls, data processing). Use pub/sub for broadcast notifications (fire-and-forget, one-to-many). RPC is synchronous-style (wait for response); pub/sub is asynchronous (no waiting).

### Production Pitfalls

**Pitfall 1: Not using correlation ID**
- Problem: Response doesn't match request (wrong result returned)
- Detection: Unexpected responses, data corruption
- Solution: Always generate unique correlation ID per request

**Pitfall 2: Not using callback queue**
- Problem: No way to send response back
- Detection: No response mechanism
- Solution: Always create callback queue and use reply_to

**Pitfall 3: Not using timeout**
- Problem: Producer waits forever (infinite blocking)
- Detection: Producer stuck, no error
- Solution: Always set timeout and handle gracefully

**Pitfall 4: Using durable callback queue**
- Problem: Queue persists (cleanup issue)
- Detection: Queue proliferation, resource waste
- Solution: Always use temporary callback queue (exclusive, auto-delete)

**Pitfall 5: Not matching correlation ID**
- Problem: Response mismatch (wrong result returned)
- Detection: Data corruption, unexpected results
- Solution: Always match correlation ID before processing response

### Advanced RPC Concepts

**Multiple RPC Clients (Load Balancing):**

```python
# Multiple RPC clients send requests
client1 = DataProcessingClient()
client2 = DataProcessingClient()

# Requests distributed between servers (load balancing)
response1 = client1.process_data(data1, timeout=10)
response2 = client2.process_data(data2, timeout=10)

print(f"[Client 1] Result: {response1}")
print(f"[Client 2] Result: {response2}")
```

**Asynchronous RPC (Non-blocking):**

```python
# Non-blocking RPC (fire-and-forget requests)
async def process_data_async(data):
    corr_id = str(uuid.uuid4())
    
    # Send request (non-blocking)
    channel.basic_publish(
        exchange='',
        routing_key='data_processing_requests',
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=corr_id
        ),
        body=json.dumps({"operation": "process", "data": data})
    )
    
    # Store corr_id for future response lookup
    pending_requests[corr_id] = {"data": data, "timestamp": time.time()}
    
    print(f"[Async] Sent request: {corr_id}")
```

---

## 📚 Summary

RPC pattern enables synchronous-style request-response communication over RabbitMQ using callback queues and correlation IDs. This provides decoupled, resilient, and load-balanced service communication with timeout handling.

**Key takeaways:**
- Use RPC for request-response communication
- Use callback queue for responses (return address)
- Use correlation ID to match requests to responses
- Use timeout handling (no infinite waiting)
- Use temporary callback queues (auto-delete, exclusive)
- Decoupled producer-consumer (queue buffering)
- Load balancing (multiple consumers)
- Message reliability (manual_ack, prefetch)

**Next steps:**
- Practice with RPC in your applications
- Learn about Competing Consumers pattern
- Learn about Request/Reply pattern
- Explore architectural patterns (shovel, federation)

---

**Module 03 - Message Patterns and Architectures**  
**Lesson 04 - Complete**