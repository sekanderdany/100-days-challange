# 04-02: RabbitMQ Security

## 1️⃣ What Is RabbitMQ Security

**RabbitMQ Security** is the practice of protecting RabbitMQ brokers, queues, and messages from unauthorized access. This includes authentication (who can connect), authorization (what they can do), and encryption (data protection).

Think of RabbitMQ security like securing a company office building:

- **Authentication** = ID card check at entrance (who can enter)
- **Authorization** = Access card check at different rooms (where can they go)
- **Encryption** = Secure documents (data protection)
- **Network Security** = Firewalls and cameras (external protection)

**Where security fits in RabbitMQ architecture:**

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│  Producer   │        │  Consumer    │        │  Admin       │
└──────┬──────┘        └──────┬──────┘        └──────┬──────┘
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    RabbitMQ Server                                  │
│                    (Security Layer)                                 │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────────────────────┐   │
│   │              │              │              │               │   │   │
│   │    Login     │     Resource    │     Permission    │   │   │
│   │  (AuthN)     │   Control      │   (Authorize)    │   │   │
│   │              │              │               │               │   │   │
│   │   SASL/Plain   │   SSL/TLS      │   Configure      │   │   │
│   │              │              │               │               │   │   │
│   │              │              │               │               │   │   │
│   │              │              │               │               │   │   │
│   └──────────────┘  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │              │              │              │               │   │
│   │   Users       │   Virtual Hosts  │   Permissions    │   │   │
│   │              │              │              │               │   │   │
│   └──────────────┘  └───────────────┘  └───────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────────┘
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
┌──────────────┐┌──────────────┐┌──────────────┐
│  Secure     ││  Secure     ││  Secure     │
│  Connection  ││  Connection  ││  Connection  │
│  (SSL/TLS)   ││  (SSL/TLS)   ││  (SSL/TLS)   │
└──────────────┘└──────────────┘└──────────────┘
```

**Key concepts:**
- **Authentication:** Verify user identity (username/password, certificates)
- **Authorization:** Grant permissions (configure, write, read)
- **Encryption:** Protect data in transit (SSL/TLS)
- **Network Security:** Firewalls, IP whitelisting
- **Virtual Hosts:** Namespace isolation (separate applications)
- **User Permissions:** Configure, write, read access control

---

## 2️⃣ Problems Solved by Security

### The "Unauthorized Access" Problem

Without security:

- Anyone can connect to RabbitMQ
- Anyone can consume/publish messages
- No access control (read/write on any queue)
- Data leakage and unauthorized actions

**Real-world security breach scenario:**

A production system had:

```
Hacker → RabbitMQ (Unsecured)
          │
          ├─ Hacker connects to RabbitMQ (no authentication)
          └─ Hacker consumes all messages (data theft)

WITHOUT SECURITY:
├─ Anyone can connect (no authentication)
├─ Anyone can consume/publish (no authorization)
├─ No access control (read/write on any queue)
├─ Data leakage (hacker steals all messages)
└─ Unauthorized actions (hacker deletes queues)

PROBLEMS:
├─ No authentication (anyone can connect)
├─ No authorization (anyone can do anything)
├─ No encryption (data transmitted in plaintext)
├─ Data leakage (hacker steals all messages)
└─ Unauthorized actions (hacker deletes queues)
```

**Problems:**
- No authentication (anyone can connect)
- No authorization (anyone can do anything)
- No encryption (data transmitted in plaintext)
- Data leakage (hacker steals all messages)
- Unauthorized actions (hacker deletes queues)
- **Impact:** Data theft, unauthorized access, system compromise, compliance violations

After implementing security:
- Authentication required (username/password, certificates)
- Authorization enforced (permissions: configure, write, read)
- Encryption enabled (SSL/TLS for data protection)
- Network security (firewalls, IP whitelisting)
- Virtual hosts (namespace isolation)
- **Result:** Secure system, authorized access, data protection, compliance

### The "Data in Transit" Problem

Without security:

- Messages transmitted in plaintext
- Network sniffing attacks possible
- Data intercepted by attackers
- No data privacy or integrity

**Example:**

```
Producer → Network (Unencrypted) → Consumer
          │
          ├─ Messages transmitted in plaintext
          ├─ Network sniffer intercepts data
          └─ Data stolen (no protection)

WITHOUT SECURITY (DATA IN TRANSIT):
├─ Messages transmitted in plaintext
├─ Network sniffer intercepts data
├─ Data stolen (no protection)
├─ No data privacy
├─ No data integrity
└─ **Impact:** Data theft, privacy violations, compliance issues
```

**Problems:**
- No encryption (data transmitted in plaintext)
- Network sniffing (data intercepted)
- No data privacy or integrity
- Compliance violations (GDPR, PCI-DSS)
- **Impact:** Data theft, privacy violations, compliance issues

After implementing security:
- SSL/TLS enabled (encrypted connections)
- Data encrypted in transit
- Network sniffing prevented (data protected)
- Data privacy and integrity maintained
- Compliance achieved (GDPR, PCI-DSS)
- **Result:** Data protected, privacy maintained, compliance achieved

---

## 3️⃣ When You Should Use Security

### Development vs Production

**Development:**
- Can use default guest account (quick tests)
- Don't need SSL/TLS for local development
- Use simple authentication (username/password)
- Don't use in production code

**Production:**
- Absolutely required (no default guest account)
- Essential for authentication (strong passwords, certificates)
- Essential for authorization (least privilege principle)
- Critical for encryption (SSL/TLS in transit)
- Required for compliance (GDPR, PCI-DSS)
- Necessary for network security (firewalls, IP whitelisting)
- Required for production systems (security policies)

### Security Scenarios

| Scenario | Security Strategy | Example |
|----------|----------------|----------|
| **Internal service** | Authentication + Authorization | Internal API, microservices |
| **External service** | Authentication + SSL/TLS | Public API, third-party access |
| **High compliance** | Strong Auth + SSL + Auditing | Finance, healthcare |
| **Cloud deployment** | IAM + SSL + VPC | AWS, GCP, Azure |

### Required vs Optional

**Required when:**
- Production systems (any production environment)
- Public-facing services (internet access)
- High compliance requirements (GDPR, PCI-DSS, HIPAA)
- External access (third-party clients)
- Cloud deployments (public cloud)
- Sensitive data (PII, financial transactions)

**Optional when:**
- Internal services (trusted network)
- Development and testing environments
- Local development (localhost only)
- Non-sensitive data (logs, telemetry)

### Trade-offs

**Security:**
✅ Authentication (verify user identity)  
✅ Authorization (access control)  
✅ Encryption (SSL/TLS)  
✅ Virtual hosts (namespace isolation)  
✅ Network security (firewalls)  
✅ Compliance (GDPR, PCI-DSS)  
✅ Audit logs (security monitoring)  
✅ Least privilege principle (minimal permissions)  
❌ More complex setup (authentication, certificates)  
❌ More management (users, permissions, policies)  
❌ Performance overhead (SSL/TLS encryption)  
❌ Troubleshooting difficulty (certificates, firewalls)  

**No Security:**
✅ Simpler setup (default guest account)  
✅ Easier to manage (no users, permissions)  
✅ Better performance (no encryption overhead)  
❌ No authentication (anyone can connect)  
❌ No authorization (anyone can do anything)  
❌ No encryption (data transmitted in plaintext)  
❌ Data leakage (anyone can access)  
❌ Unauthorized actions (hacker can delete queues)  
❌ Compliance violations (GDPR, PCI-DSS)  

---

## 4️⃣ How RabbitMQ Security Works

### Authentication Mechanisms

**Setting up authentication:**

```
1. Enable Authentication Plugin
   │
   ├─ Enable rabbitmq_auth_backend_ldap (LDAP)
   ├─ Enable rabbitmq_auth_backend_http (HTTP)
   ├─ Configure authentication method (SASL, PLAIN, EXTERNAL)
   └─ Restart RabbitMQ
   │
2. Configure Users
   │
   ├─ Create user with username/password
   ├─ Assign user to virtual host
   ├─ Set user permissions (configure, write, read)
   └─ Apply changes
   │
3. Client Authentication
   │
   ├─ Client connects with username/password
   ├─ Client authenticates (credentials verified)
   ├─ Connection established
   └─ Client can publish/consume (if authorized)
   │
4. Authentication Methods
   │
   ├─ PLAIN: Username/password (basic)
   ├─ SASL: Username/password (SASL)
   ├─ EXTERNAL: Certificate-based authentication
   └─ AMQP 0-9-1: OAuth 2.0 (modern)
```

### Authorization Mechanisms

**How authorization works:**

```
Virtual Hosts (Namespace Isolation):
├─ Virtual Host A: Application A
├─ Virtual Host B: Application B
├─ Virtual Host C: Application C
└─ Separates applications (isolation)

User Permissions (Access Control):
├─ Configure: Create/declare exchanges, queues, bindings
├─ Write: Publish messages, acknowledge messages
└─ Read: Consume messages, browse queues

Permission Matrix:
├─ User on Virtual Host A
│  ├─ Can configure exchanges/queues
│  ├─ Can publish messages
│  └─ Can consume messages
├─ User on Virtual Host B
│  ├─ Cannot configure exchanges/queues
│  ├─ Cannot publish messages
│  └─ Can consume messages
└─ Different users on different virtual hosts (isolation)
```

### Encryption Mechanisms

**How SSL/TLS works:**

```
SSL/TLS Connection (Encrypted):
├─ Client connects to RabbitMQ
├─ RabbitMQ presents SSL certificate
├─ Client validates certificate (chain of trust)
├─ Client presents client certificate (mutual TLS)
├─ Certificate validation successful
├─ Encrypted connection established
└─ Messages encrypted in transit

SSL/TLS Components:
├─ Certificate Authority (CA) - Signs certificates
├─ Server Certificate - RabbitMQ identity
├─ Client Certificate - Client identity
└─ Private Key - Decryption key

Encryption:
├─ Messages encrypted in transit
├─ Network sniffing prevented
├─ Data privacy maintained
└─ Data integrity maintained
```

---

## 5️⃣ Installation / Setup

**RabbitMQ Security is built-in RabbitMQ feature.** No installation required - just enable authentication plugins, create users, set permissions, enable SSL/TLS.

### Prerequisites

- RabbitMQ server running
- RabbitMQ authentication plugin installed
- RabbitMQ management plugin enabled
- SSL/TLS certificates (for encrypted connections)
- Understanding of authentication methods (SASL, PLAIN, EXTERNAL)
- Understanding of authorization (configure, write, read)
- Understanding of virtual hosts (namespace isolation)

### Enabling Authentication Plugin

**Using rabbitmq-plugins:**

```bash
# Enable authentication plugin (LDAP, HTTP, etc.)
sudo rabbitmq-plugins enable rabbitmq_auth_backend_ldap
sudo rabbitmq-plugins enable rabbitmq_auth_backend_http

# Restart RabbitMQ
sudo systemctl restart rabbitmq-server

# Verify authentication plugin
sudo rabbitmq-plugins list | grep auth
```

**Using Docker:**

```bash
# Start RabbitMQ with authentication plugins
docker run -d --name rabbitmq-secure \
  -e RABBITMQ_PLUGINS="rabbitmq_auth_backend_ldap,rabbitmq_management,rabbitmq_auth_mechanism_scram" \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Enable plugins via rabbitmq.conf (recommended)
sudo rabbitmqctl add_plugin rabbitmq_auth_backend_ldap

# Restart RabbitMQ
sudo systemctl restart rabbitmq-server
```

### Version Notes

- **RabbitMQ 3.12+:** All security features fully supported
- **Authentication Plugins:** LDAP, HTTP, OAuth, SCRAM
- **Authorization:** Configure, write, read permissions
- **SSL/TLS:** Encrypted connections (mutual TLS)
- **Virtual Hosts:** Namespace isolation (separate applications)
- **Network Security:** IP whitelisting, firewall rules
- **Compliance:** GDPR, PCI-DSS, HIPAA

---

## 6️⃣ Where Security Should Be Applied (With Example)

### Authentication with SSL/TLS

**Scenario:** Financial transaction system with strong security

**SSL/TLS Configuration:**

```bash
# Generate CA (Certificate Authority)
openssl genrsa -out ca.key 2048
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt

# Generate server certificate
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -in server.csr -signkey server.key -CA ca.crt -CAcreateserial -days 3650 -out server.crt

# Generate client certificate
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr
openssl x509 -req -in client.csr -signkey client.key -CA ca.crt -CAcreateserial -days 3650 -out client.crt

# Create RabbitMQ SSL configuration
cat > /etc/rabbitmq/rabbitmq.conf << EOF
listeners.ssl.default = 5671
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = true
ssl_options.depth = 2
certs./etc/rabbitmq/ssl/ca.crt
certs./etc/rabbitmq/ssl/server.crt
keyfile./etc/rabbitmq/ssl/server.key
EOF

# Restart RabbitMQ
sudo systemctl restart rabbitmq-server
```

**Consumer with SSL/TLS:**

```python
import pika
import ssl

# CRITICAL: Load SSL/TLS certificates
context = ssl.create_default_context(cafile="/etc/rabbitmq/ssl/ca.crt")
context.load_cert_chain("/etc/rabbitmq/ssl/server.crt", "/etc/rabbitmq/ssl/server.key")

# CRITICAL: Connect with SSL/TLS
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5671,
        credentials=pika.PlainCredentials('guest', 'guest'),  # Can use username/password too
        ssl_options=pika.SSLOptions(
            ssl_version=ssl.PROTOCOL_TLSv1_2,
            cert_reqs=ssl.CERT_REQUIRED,
            ca_certs=ca_path,
        ),
    )
)
channel = connection.channel()

# CRITICAL: Declare queue
channel.queue_declare(queue='secure_transactions', durable=True)

# CRITICAL: Publish message (encrypted in transit)
channel.basic_publish(
    exchange='',
    routing_key='secure_transactions',
    body='{"transaction_id": "txn_001", "amount": 1000}
)

print("[✓] Published message with SSL/TLS (encrypted in transit)")
connection.close()
```

### Virtual Hosts and User Permissions

**Scenario:** Multi-tenant application with isolation

**Virtual Host Configuration:**

```python
import pika

# CRITICAL: Connect to virtual host (namespace isolation)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        virtual_host='tenant_a',  # CRITICAL: Virtual host isolation
        credentials=pika.PlainCredentials('user_tenant_a', 'password_tenant_a')
    )
)
channel = connection.channel()

# CRITICAL: Declare queue on virtual host
channel.queue_declare(queue='tenant_a_transactions', durable=True)

# CRITICAL: Publish message
channel.basic_publish(
    exchange='',
    routing_key='tenant_a_transactions',
    body='{"transaction_id": "txn_001", "tenant": "tenant_a"}
)

print("[✓] Published message to virtual host (namespace isolation)")
connection.close()
```

**User Permissions Configuration:**

```bash
# Add user with permissions
sudo rabbitmqctl add_user tenant_a_user secure_password

# Set user permissions (configure, write, read)
sudo rabbitmqctl set_permissions -p tenant_a ".*" ".*" ".*"

# Verify user permissions
sudo rabbitmqctl list_permissions | grep tenant_a_user
```

**Expected output:**

```
# SSL/TLS Connection
[*] Connected to RabbitMQ with SSL/TLS (encrypted in transit)
[✓] Published message with SSL/TLS (encrypted in transit)

# Virtual Host Isolation
[*] Connected to virtual host (tenant_a - namespace isolation)
[✓] Published message to virtual host (namespace isolation)

# User Permissions
user: tenant_a_user
virtual_host: tenant_a
configure: .*
write: .*
read: .*
```

**View in Management UI:**

1. Open http://localhost:15672
2. Go to Admin tab → Users
3. See users and permissions (tenants isolated by virtual host)
4. See SSL/TLS status (encrypted connections)
5. See virtual hosts (namespace isolation)

### Best Practices

**Authentication:**
✅ Use strong passwords (12+ characters, mixed case)  
✅ Use certificates for production (SSL/TLS)  
✅ Use LDAP for enterprise authentication (centralized)  
✅ Use OAuth 2.0 for modern applications  
✅ Disable default guest account in production  

**Authorization:**
✅ Use virtual hosts for namespace isolation (multi-tenant)  
✅ Use least privilege principle (minimal permissions)  
✅ Separate configure, write, read permissions  
✅ Regularly audit user permissions  
✅ Remove unused accounts regularly  

**Encryption:**
✅ Use SSL/TLS for all connections (encrypt in transit)  
✅ Use mutual TLS for certificate-based authentication  
✅ Use strong TLS configuration (TLS 1.2+)  
✅ Use proper certificates (signed by trusted CA)  
✅ Regularly rotate certificates (before expiration)  

**Network Security:**
✅ Use firewalls to restrict access (IP whitelisting)  
✅ Use VPN for internal RabbitMQ access (secure tunnel)  
✅ Use load balancer with SSL termination (AWS ALB)  
✅ Use private subnets for RabbitMQ (network isolation)  
✅ Restrict management port (15672) to internal network  

### Common Mistakes

❌ Not disabling default guest account → Anyone can connect  
❌ Not using SSL/TLS → Data transmitted in plaintext  
❌ Not using virtual hosts → No namespace isolation  
❌ Using same password for all users → Security risk  
❌ Granting excessive permissions → Privilege escalation  
❌ Not monitoring authentication → Unauthorized access not visible  
❌ Not rotating certificates → Expired certificates cause outages  
❌ Opening management port to public → Security risk  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Unauthorized Access (The "Open Door" Problem)**

You're building a production messaging system:

- System must be secured (authentication, authorization)
- Default guest account enabled (anyone can connect)
- No SSL/TLS (data transmitted in plaintext)
- No virtual hosts (no namespace isolation)
- Sensitive data exposed

Current implementation:
- Default guest account enabled (anyone can connect)
- No SSL/TLS (data transmitted in plaintext)
- No virtual hosts (no namespace isolation)
- Sensitive data exposed
- No access control (anyone can do anything)

**Problems:**
- Unauthorized access (anyone can connect)
- Data theft (anyone can consume messages)
- Unauthorized actions (anyone can delete queues)
- Compliance violations (GDPR, PCI-DSS)
- Data transmitted in plaintext (network sniffing)
- No namespace isolation (tenants can access each other)
- **Impact:** Data theft, unauthorized access, compliance violations, legal liability

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ with authentication**

```bash
# Start RabbitMQ (insecure - no auth)
docker run -d --name rabbitmq-insecure \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Verify: Guest account enabled
# curl http://localhost:15672/api/overview
# See: "auth_mechanism": "PLAIN" (default guest)
```

**Step 2: Create producer without security**

Create `insecure_producer.py`:

```python
import pika
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: No authentication (guest account)
# PROBLEM: No SSL/TLS (data transmitted in plaintext)
channel.queue_declare(queue='transactions', durable=True)

# PROBLEM: Publish sensitive data (data exposure)
for i in range(100):
    transaction = {
        "transaction_id": f"txn_{i+1:04d}",
        "amount": 10000 + i,
        "account": "confidential",
        "ssn": "123-45-6789"
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='transactions',
        body=json.dumps(transaction)
    )
    
    if i % 10 == 0:
        print(f"[x] Published {i} sensitive transactions")

print(f"[✗] Published 100 sensitive transactions (PROBLEM: No auth - data exposure)")
connection.close()
```

**Step 3: Create consumer without security**

Create `insecure_consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    transaction = json.loads(body)
    print(f"[!] Hacker stole transaction: {transaction['transaction_id']}")
    print(f"[!] Sensitive data: SSN={transaction['ssn']}, Amount={transaction['amount']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# PROBLEM: No authentication (guest account)
# PROBLEM: No authorization (anyone can consume)
channel.queue_declare(queue='transactions', durable=True)
channel.basic_consume(queue='transactions', on_message_callback=callback)

print("[!] Insecure consumer (PROBLEM: No auth - data exposure)")
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal: Insecure consumer
python3 insecure_consumer.py

# Terminal: Insecure producer
python3 insecure_producer.py
```

**Expected observation:**
- Producer publishes 100 sensitive transactions
- Anyone can consume messages (guest account)
- Data transmitted in plaintext (network sniffing)
- Data stolen (hacker sees SSN, amount)
- Unauthorized actions (hacker can delete queues)
- **Impact:** Data theft, unauthorized access, compliance violations

**Step 5: View in Management UI**

Open http://localhost:15672:
- Go to Admin tab → Users tab
- See default guest account enabled
- See no user authentication
- See no SSL/TLS configured
- See no virtual hosts (no namespace isolation)
- **Impact:** Open door for attackers

### ✅ Solution & Explanation

**Solution: Implement RabbitMQ Security (Authentication + SSL/TLS + Virtual Hosts)**

**Step 1: Enable SSL/TLS on RabbitMQ**

```bash
# Stop insecure RabbitMQ
docker stop rabbitmq-insecure
docker rm rabbitmq-insecure

# Generate CA (Certificate Authority)
openssl genrsa -out ca.key 2048
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt

# Generate server certificate
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -in server.csr -signkey server.key -CA ca.crt -CAcreateserial -days 3650 -out server.crt

# Start RabbitMQ with SSL/TLS
docker run -d --name rabbitmq-secure \
  -v $(pwd)/rabbitmq:/etc/rabbitmq:/var/lib/rabbitmq \
  -p 5671:5671 -p 15672:15672 \
  -e RABBITMQ_SERVER_ADDITIONAL_ERLANG_ARGS="-rabbit ssl_listeners [{default,5671}]" \
  -e RABBITMQ_SSL_CERTFILE="/etc/rabbitmq/ssl/server.crt" \
  -e RABBITMQ_SSL_KEYFILE="/etc/rabbitmq/ssl/server.key" \
  -e RABBITMQ_SSL_CAFILE="/etc/rabbitmq/ssl/ca.crt" \
  -e RABBITMQ_SSL_VERIFY=verify_peer \
  -e RABBITMQ_SSL_FAIL_IF_NO_PEER_CERT=true \
  rabbitmq:3-management
```

**Step 2: Create user with permissions**

```bash
# Add user (no more guest account)
docker exec rabbitmq-secure rabbitmqctl add_user secure_user secure_password

# Set permissions (least privilege)
docker exec rabbitmq-secure rabbitmqctl set_permissions -p secure_user ".*" ".*" ".*"

# Create virtual host (namespace isolation)
docker exec rabbitmq-secure rabbitmqctl add_vhost tenant_a

# Set permissions for virtual host
docker exec rabbitmq-secure rabbitmqctl set_permissions -p secure_user tenant_a ".*" ".*" ".*"

# Disable guest account (security best practice)
docker exec rabbitmq-secure rabbitmqctl delete_user guest
```

**Step 3: Create producer with SSL/TLS**

Create `secure_producer.py`:

```python
import pika
import ssl
import json
import time

# SOLUTION: Load SSL/TLS certificates
context = ssl.create_default_context(cafile="ca.crt")
context.load_cert_chain("server.crt", "server.key")

# SOLUTION: Connect with username/password + SSL/TLS
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5671,
        credentials=pika.PlainCredentials('secure_user', 'secure_password'),
        ssl_options=pika.SSLOptions(
            ssl_version=ssl.PROTOCOL_TLSv1_2,
            cert_reqs=ssl.CERT_REQUIRED,
            ca_certs="ca.crt",
        ),
        virtual_host='tenant_a',  # SOLUTION: Virtual host isolation
    )
)
channel = connection.channel()

# SOLUTION: Declare queue on virtual host
channel.queue_declare(queue='secure_transactions', durable=True)

# SOLUTION: Publish sensitive data (encrypted in transit)
for i in range(100):
    transaction = {
        "transaction_id": f"txn_{i+1:04d}",
        "amount": 10000 + i,
        "account": "confidential",
        "ssn": "encrypted_protected"
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='secure_transactions',
        body=json.dumps(transaction)
    )
    
    if i % 10 == 0:
        print(f"[x] Published {i} secure transactions")

print(f"[✓] Published 100 secure transactions (SOLUTION: Auth + SSL/TLS - encrypted)")
connection.close()
```

**Step 4: Create consumer with SSL/TLS**

Create `secure_consumer.py`:

```python
import pika
import ssl
import json

# SOLUTION: Load SSL/TLS certificates
context = ssl.create_default_context(cafile="ca.crt")
context.load_cert_chain("server.crt", "server.key")

def callback(ch, method, properties, body):
    transaction = json.loads(body)
    print(f"[✓] Processing transaction: {transaction['transaction_id']}")
    print(f"[✓] Sensitive data: SSN={transaction['ssn']}, Amount={transaction['amount']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

# SOLUTION: Connect with username/password + SSL/TLS
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5671,
        credentials=pika.PlainCredentials('secure_user', 'secure_password'),
        ssl_options=pika.SSLOptions(
            ssl_version=ssl.PROTOCOL_TLSv1_2,
            cert_reqs=ssl.CERT_REQUIRED,
            ca_certs="ca.crt",
        ),
        virtual_host='tenant_a',  # SOLUTION: Virtual host isolation
    )
)
channel = connection.channel()

# SOLUTION: Consume from virtual host
channel.queue_declare(queue='secure_transactions', durable=True)
channel.basic_consume(queue='secure_transactions', on_message_callback=callback)

print("[*] Secure consumer (SOLUTION: Auth + SSL/TLS - encrypted)")
channel.start_consuming()
```

**How to verify:**

```bash
# Terminal: Secure producer
python3 secure_producer.py

# Terminal: Secure consumer
python3 secure_consumer.py
```

**Expected output:**

```
# Secure Producer
[x] Published 10 secure transactions
[x] Published 20 secure transactions
...
[x] Published 100 secure transactions
[✓] Published 100 secure transactions (SOLUTION: Auth + SSL/TLS - encrypted)

# Secure Consumer
[*] Secure consumer (SOLUTION: Auth + SSL/TLS - encrypted)
[✓] Processing transaction: txn_0001
[✓] Sensitive data: SSN=encrypted_protected, Amount=10001
[✓] Processing transaction: txn_0002
[✓] Sensitive data: SSN=encrypted_protected, Amount=10002
...
```

**View in Management UI:**

1. Open https://localhost:15671 (SSL/TLS port)
2. Accept certificate warning (self-signed)
3. Go to Admin tab → Users tab
4. See user: secure_user (permissions configured)
5. See virtual host: tenant_a (namespace isolation)
6. See SSL/TLS enabled (encrypted connections)
7. See guest account disabled (no more open door)

**Comparison:**

| Design | Authentication | Authorization | SSL/TLS | Guest Account |
|--------|---------------|------------|-----------|--------------|
| Insecure (old) | No | No | No | Yes (open door) |
| Secure (new) | Yes | Yes | Yes | No (closed) |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Always disable default guest account in production  
- Use strong passwords (12+ characters, mixed case)  
- Use certificates for production (SSL/TLS)  
- Use mutual TLS for certificate-based authentication  
- Use virtual hosts for namespace isolation (multi-tenant)  
- Use least privilege principle (minimal permissions)  
- Separate configure, write, read permissions  
- Regularly audit user permissions  
- Remove unused accounts regularly  
- Use firewalls to restrict access (IP whitelisting)  
- Use VPN for internal RabbitMQ access  
- Regularly rotate certificates (before expiration)  

**❌ Don't:**
- Not disabling default guest account → Open door for attackers  
- Not using SSL/TLS → Data transmitted in plaintext  
- Not using virtual hosts → No namespace isolation  
- Using same password for all users → Security risk  
- Granting excessive permissions → Privilege escalation  
- Not monitoring authentication → Unauthorized access not visible  
- Not rotating certificates → Expired certificates cause outages  
- Opening management port to public → Security risk  
- Using weak passwords → Brute force attacks  

### RabbitMQ Security Guidelines

```
Authentication:
├─ Use strong passwords (12+ characters, mixed case)
├─ Use certificates for production (SSL/TLS)
├─ Use mutual TLS for certificate-based authentication
├─ Disable default guest account in production
└─ Regularly rotate passwords

Authorization:
├─ Use virtual hosts for namespace isolation (multi-tenant)
├─ Use least privilege principle (minimal permissions)
├─ Separate configure, write, read permissions
└─ Regularly audit user permissions

Encryption:
├─ Use SSL/TLS for all connections (encrypt in transit)
├─ Use strong TLS configuration (TLS 1.2+)
├─ Use proper certificates (signed by trusted CA)
└─ Regularly rotate certificates (before expiration)

Network Security:
├─ Use firewalls to restrict access (IP whitelisting)
├─ Use VPN for internal RabbitMQ access
├─ Use load balancer with SSL termination
└─ Restrict management port to internal network

Compliance:
├─ Enable audit logs (security monitoring)
├─ Regularly review user permissions
├─ Disable unused accounts regularly
└─ Follow GDPR, PCI-DSS, HIPAA requirements
```

### Production Considerations

**Authentication Methods:**

```python
# LDAP Authentication (enterprise)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='ldap.company.com',
        credentials=pika.PlainCredentials('user@company.com', 'password'),
    )
)

# OAuth 2.0 Authentication (modern)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='rabbitmq.company.com',
        credentials=pika.PlainCredentials('token', ''),
    )
)

# External Authentication (certificate-based)
context = ssl.create_default_context(cafile="ca.crt")
context.load_cert_chain("client.crt", "client.key")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='rabbitmq.company.com',
        credentials=pika.ExternalCredentials('client.crt', None),
        ssl_options=pika.SSLOptions(cert_reqs=ssl.CERT_REQUIRED, ca_certs="ca.crt"),
    )
)
```

**SSL/TLS Configuration:**

```bash
# Enable SSL/TLS in rabbitmq.conf
listeners.ssl.default = 5671
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = true
ssl_options.depth = 2
certs./etc/rabbitmq/ssl/ca.crt
certs./etc/rabbitmq/ssl/server.crt
keyfile./etc/rabbitmq/ssl/server.key
```

**Virtual Host Management:**

```bash
# Add virtual host
sudo rabbitmqctl add_vhost tenant_a

# Set permissions for virtual host
sudo rabbitmqctl set_permissions -p secure_user tenant_a ".*" ".*" ".*"

# Delete virtual host
sudo rabbitmqctl delete_vhost tenant_a
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's RabbitMQ authentication?**

A: RabbitMQ authentication verifies user identity before granting access. Supports multiple methods: PLAIN (username/password), SASL (username/password with SASL), EXTERNAL (certificate-based), OAuth 2.0 (modern), LDAP (enterprise). Authentication prevents unauthorized access to RabbitMQ.

**Q2: What's RabbitMQ authorization?**

A: RabbitMQ authorization controls what authenticated users can do. Uses permissions: configure (create/declare exchanges, queues, bindings), write (publish messages), read (consume messages). Permissions can be scoped to virtual hosts for namespace isolation.

**Q3: What's virtual host?**

A: Virtual host is namespace isolation mechanism. Separate virtual hosts for different applications/tenants. Users on one virtual host can't access resources on other virtual hosts. Provides multi-tenancy support.

**Q4: What's SSL/TLS in RabbitMQ?**

A: SSL/TLS encrypts data in transit between client and RabbitMQ. Uses certificates for authentication (mutual TLS). Prevents network sniffing attacks. Protects data privacy and integrity.

**Q5: How do you secure RabbitMQ in production?**

A: Disable default guest account. Create users with strong passwords. Use virtual hosts for namespace isolation. Use least privilege principle (minimal permissions). Enable SSL/TLS for encrypted connections. Use firewalls to restrict access (IP whitelisting). Regularly audit user permissions.

### Production Pitfalls

**Pitfall 1: Not disabling default guest account**
- Problem: Anyone can connect (open door)
- Detection: Unauthorized connections from unknown IPs
- Solution: Always disable guest account in production

**Pitfall 2: Not using SSL/TLS**
- Problem: Data transmitted in plaintext
- Detection: Network sniffing attacks
- Solution: Always use SSL/TLS for production

**Pitfall 3: Granting excessive permissions**
- Problem: Privilege escalation
- Detection: User can delete queues, exchanges
- Solution: Use least privilege principle (minimal permissions)

**Pitfall 4: Not using virtual hosts**
- Problem: No namespace isolation
- Detection: Tenants can access each other
- Solution: Always use virtual hosts for multi-tenant

**Pitfall 5: Not rotating certificates**
- Problem: Expired certificates cause outages
- Detection: Certificate expiration errors
- Solution: Regularly rotate certificates before expiration

### Advanced Security Concepts

**Mutual TLS (Certificate-Based Authentication):**

```python
# Client presents certificate (mutual TLS)
context = ssl.create_default_context(cafile="ca.crt")
context.load_cert_chain("client.crt", "client.key")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='rabbitmq.company.com',
        credentials=pika.ExternalCredentials('client.crt', None),
        ssl_options=pika.SSLOptions(cert_reqs=ssl.CERT_REQUIRED, ca_certs="ca.crt"),
    )
)
```

**Multi-Tenant Architecture:**

```bash
# Virtual hosts for tenants
sudo rabbitmqctl add_vhost tenant_a  # Tenant A
sudo rabbitmqctl add_vhost tenant_b  # Tenant B
sudo rabbitmqctl add_vhost tenant_c  # Tenant C

# User per tenant
sudo rabbitmqctl add_user tenant_a_user password_a
sudo rabbitmqctl add_user tenant_b_user password_b
sudo rabbitmqctl add_user tenant_c_user password_c

# Permissions per tenant (isolation)
sudo rabbitmqctl set_permissions -p tenant_a_user tenant_a ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p tenant_b_user tenant_b ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p tenant_c_user tenant_c ".*" ".*" ".*"
```

---

## 📚 Summary

RabbitMQ security provides authentication, authorization, and encryption to protect RabbitMQ brokers. SSL/TLS encrypts data in transit, virtual hosts provide namespace isolation, and user permissions enforce access control.

**Key takeaways:**
- Always disable default guest account in production
- Use strong passwords and certificates
- Use virtual hosts for namespace isolation (multi-tenant)
- Use least privilege principle (minimal permissions)
- Enable SSL/TLS for encrypted connections
- Use firewalls to restrict access
- Regularly audit user permissions
- Regularly rotate certificates
- Compliance achieved (GDPR, PCI-DSS, HIPAA)

**Next steps:**
- Practice with security in your applications
- Learn about monitoring and alerting (next lesson)
- Learn about performance tuning
- Complete all lessons in Module 04

---

**Module 04 - Advanced Concepts**  
**Lesson 02 - Complete**