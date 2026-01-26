# 01-04: Virtual Hosts, Users and Permissions

## 1️⃣ What Are Virtual Hosts, Users and Permissions

**Virtual Hosts (vhosts)** are namespaces within RabbitMQ that group exchanges, queues, bindings, and permissions together. They provide isolation and multi-tenancy, allowing different applications or teams to share a RabbitMQ instance without interfering.

**Users** are authentication entities that connect to RabbitMQ. Each user has credentials (username/password) and permissions to access specific virtual hosts.

**Permissions** are access controls that determine what operations a user can perform on a virtual host (configure, write, read).

Think of RabbitMQ like a building:
- **Virtual Host** = A floor with its own rooms (isolated space)
- **User** = An employee with keycard (access credentials)
- **Permissions** = Which rooms and what they can do in each room

**Where they fit in RabbitMQ architecture:**

```
┌─────────────────────────────────────────────┐
│          RabbitMQ Instance            │
│                                          │
│  ┌───────────┐   ┌───────────┐   ┌────┴────┐  │
│  │  Vhost A  │   │  Vhost B  │   │ Vhost C │  │
│  │(app1)    │   │(app2)    │   │(admin) │  │
│  └─────┬─────┘   └─────┬─────┘   └─────┬───┘  │
│        │               │               │       │   │
│  ┌─────▼──────┐   ┌─────▼──────┐   ┌─────▼───┐  │
│  │Exchange 1 │   │Exchange 2 │   │Exchange 3│  │
│  │Queue 1    │   │Queue 2    │   │Queue 3   │  │
│  └──────────┘   └──────────┘   └──────────┘  │
│                                          │
│  Users and Permissions:                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │ User App1 │   │ User App2 │   │Admin    ││
│  │ Config RW│   │ Config R │   │Config RW││
│  │ Vhost A   │   │ Vhost B   │   │All vhosts││
│  └──────────┘   └──────────┘   └──────────┘│
└─────────────────────────────────────────────┘
```

**Key concepts:**
- **Virtual Host (/):** The default vhost, use only for development
- **Virtual Host (name):** Named vhosts for production isolation
- **User:** Authentication credentials to connect to RabbitMQ
- **Permission:** Access rules (configure, write, read) per vhost

---

## 2️⃣ Problems Solved by Virtual Hosts, Users and Permissions

### The Multi-Tenancy Problem

Without virtual hosts:

- All applications share same exchanges and queues
- Queue name collisions between applications
- No isolation - one app can't access another's resources
- Hard to separate development, staging, production

**Real-world failure scenario:**

A SaaS platform had:

```
RabbitMQ Instance
├─ App A queues: orders, payments
├─ App B queues: orders, inventory  ← Same names!
└─ App C queues: orders, shipments  ← Same names!
```

**Problems:**
- Queue name conflicts between apps
- App A accidentally processes App B's orders
- No isolation - can't separate resources
- Security issues - apps access each other's data
- **Impact:** Production incident, wrong orders processed, customer data leaked, $500K in damages

After implementing virtual hosts:
- Each app has its own vhost (app-a, app-b, app-c)
- Complete isolation - queues don't conflict
- Apps can't access each other's resources
- Separate dev/staging/prod environments
- **Result:** Complete isolation, no conflicts, secure separation

### The Security Problem

Without users and permissions:

- Everyone uses default guest/guest credentials
- No access control - anyone can do anything
- Can't revoke access for specific applications
- No audit trail of who did what
- Can't assign different permissions to different teams

**Example:**

```
Production RabbitMQ:
├─ All apps use guest/guest
├─ Dev team can delete production queues
├─ Marketing team can read payment data
└─ No way to restrict access
```

**Problems:**
- Anyone can configure, delete, or read queues
- No way to restrict access by team or application
- Security vulnerability - unauthorized access
- Can't revoke access when needed
- **Impact:** Security breach, data exposure, unauthorized deletions

After implementing users and permissions:
- Each application has its own user
- Users only have access to their vhost
- Granular permissions - configure, write, read
- Can revoke access by disabling user
- **Result:** Secure access control, audit trail, principle of least privilege

---

## 3️⃣ When You Should Use Virtual Hosts, Users and Permissions

### Development vs Production

**Development:**
- Can use default vhost (/) and guest user
- Quick setup, no security needed
- Good for learning and experimentation
- Don't use in production

**Production:**
- Absolutely required for security
- Essential for multi-tenancy and isolation
- Critical for access control and audit
- Must create proper vhosts and users

### Virtual Host Usage Scenarios

| Scenario | Vhost Strategy | Example |
|----------|-----------------|----------|
| **Single application** | One vhost for app | `myapp-production` |
| **Multiple environments** | Separate vhosts | `myapp-dev`, `myapp-staging`, `myapp-prod` |
| **Multi-tenant SaaS** | One vhost per tenant | `tenant1`, `tenant2`, `tenant3` |
| **Team isolation** | One vhost per team | `team-web`, `team-backend`, `team-data` |

### User Management Scenarios

| Scenario | User Strategy | Example |
|----------|--------------|----------|
| **Application user** | One user per app | `app1-producer`, `app1-consumer` |
| **Team user** | One user per team | `team-frontend`, `team-backend` |
| **Admin user** | Single admin for all | `rabbitmq-admin` |
| **Service user** | User for service discovery | `consul` |

### Permission Levels

| Permission | Configure (C) | Write (W) | Read (R) | Description |
|------------|--------------|-----------|----------|-------------|
| **None** | ❌ | ❌ | ❌ | No access |
| **Management** | ✅ | ✅ | ✅ | Full access to vhost (dangerous) |
| **Policies** | ✅ | ❌ | ❌ | Can manage policies only |
| **Monitoring** | ❌ | ✅ | ❌ | Can access management plugin only |
| **Administrator** | ✅ | ❌ | ❌ | Can manage users and vhosts only |
| **Standard** | ❌ | ✅ | ✅ | Can create/delete and consume/publish |
| **Impersonator** | ✅ | ✅ | ✅ | Act as another user (for troubleshooting) |

### Required vs Optional

**Required when:**
- Production deployments
- Multi-tenant applications
- Multiple environments (dev/staging/prod)
- Security and access control needed
- Multiple teams or applications sharing RabbitMQ

**Optional when:**
- Single developer machine
- Learning and experimentation
- Single application with no security requirements
- Temporary or throwaway RabbitMQ instances

### Trade-offs

**Virtual Hosts:**
✅ Complete isolation between apps  
✅ Separate environments  
✅ Multi-tenancy  
✅ No queue name conflicts  
❌ More complex setup  
❌ Need to manage multiple namespaces  

**Users and Permissions:**
✅ Security and access control  
✅ Audit trail  
✅ Granular permissions  
✅ Principle of least privilege  
❌ More administrative overhead  
❌ Need to manage credentials  
❌ Complex permission matrix  

---

## 4️⃣ How Virtual Hosts, Users and Permissions Work

### Virtual Host Architecture

**Virtual host isolation:**

```
RabbitMQ Instance:
│
├─ Vhost: / (default)
│  ├─ Exchange: amq.default
│  └─ Queue: (none)
│
├─ Vhost: app1-production
│  ├─ Exchange: orders
│  ├─ Exchange: payments
│  └─ Queue: results
│
└─ Vhost: app2-production
   ├─ Exchange: orders
   ├─ Exchange: inventory
   └─ Queue: events
```

**Virtual host characteristics:**
- Isolated namespace for exchanges, queues, bindings
- Users have separate permission set per vhost
- AMQP connection specifies vhost to connect
- Default vhost (/) is always available

### User Authentication

**Authentication process:**

```
1. Client Connects
   │
   ├─ Provides username
   ├─ Provides password
   └─ Specifies vhost
   │
2. RabbitMQ Authenticates
   │
   ├─ Validates credentials
   ├─ Checks user exists
   └─ Checks user has permissions for vhost
   │
3. Connection Established
   │
   ├─ Access restricted to vhost
   ├─ Permissions enforced
   └─ Audit log created
```

**Authentication mechanisms:**
- **Internal:** RabbitMQ stores username/password in database
- **LDAP/AD:** External authentication (requires plugin)
- **OAuth 2.0:** Token-based authentication (requires plugin)
- **AMQP SASL:** Username/password via SASL mechanism

### Permission Model

**Permission scopes per vhost:**

```
Virtual Host: app1-production

User: app1-producer

Permissions:
├─ Configure (create exchanges, queues, bindings)
│  └─ ❌ Cannot configure
│
├─ Write (publish messages)
│  └─ ✅ Can publish
│
└─ Read (consume messages)
   └─ ✅ Can consume
```

**Permission breakdown:**

| Operation | Configure | Write | Read |
|-----------|-----------|-------|------|
| **Declare exchange** | ✅ | ❌ | ❌ |
| **Declare queue** | ✅ | ❌ | ❌ |
| **Bind queue** | ✅ | ❌ | ❌ |
| **Publish message** | ❌ | ✅ | ❌ |
| **Consume message** | ❌ | ❌ | ✅ |
| **Get message** | ❌ | ❌ | ✅ |
| **Ack message** | ❌ | ❌ | ✅ |
| **Purge queue** | ❌ | ✅ | ❌ |
| **Delete exchange/queue** | ✅ | ❌ | ❌ |

### Virtual Host and User Workflow

**Typical setup for new application:**

```
1. Create Virtual Host
   │
   ├─ Name: myapp-production
   ├─ Description: MyApp Production Environment
   └─ Tracing: Enabled
   │
2. Create Users
   │
   ├─ User: myapp-producer
   │  └─ Password: secure_password_1
   │
   └─ User: myapp-consumer
      └─ Password: secure_password_2
   │
3. Set Permissions
   │
   ├─ User: myapp-producer
   │  ├─ Vhost: myapp-production
   │  ├─ Configure: ❌
   │  ├─ Write: ✅
   │  └─ Read: ✅
   │
   └─ User: myapp-consumer
      ├─ Vhost: myapp-production
      ├─ Configure: ✅
      ├─ Write: ❌
      └─ Read: ✅
   │
4. Application Connects
   │
   ├─ Producer connects as myapp-producer
   │  ├─ Consumer connects as myapp-consumer
   └─ Both connect to vhost: myapp-production
```

---

## 5️⃣ Installation / Setup

**Virtual hosts, users, and permissions are built-in RabbitMQ features.** No installation required - just configure properly.

### Prerequisites

- RabbitMQ server running
- Management Plugin enabled (for UI management)
- Understanding of security requirements

### Creating Virtual Hosts

**Via Management UI:**

1. Open http://localhost:15672
2. Click "Admin" tab
3. Click "Virtual Hosts"
4. Click "Add a new virtual host"
5. Enter name (e.g., `myapp-production`)
6. Click "Add virtual host"

**Via rabbitmqctl:**

```bash
# Create vhost
sudo rabbitmqctl add_vhost myapp-production

# Delete vhost
sudo rabbitmqctl delete_vhost myapp-production

# List vhosts
sudo rabbitmqctl list_vhosts
```

**Via HTTP API:**

```bash
# Create vhost
curl -u guest:guest -X PUT http://localhost:15672/api/vhosts/myapp-production

# Delete vhost
curl -u guest:guest -X DELETE http://localhost:15672/api/vhosts/myapp-production

# List vhosts
curl -u guest:guest http://localhost:15672/api/vhosts
```

### Creating Users

**Via Management UI:**

1. Open http://localhost:15672
2. Click "Admin" tab
3. Click "Users"
4. Click "Add a user"
5. Enter username and password
6. Click "Add user"

**Via rabbitmqctl:**

```bash
# Create user
sudo rabbitmqctl add_user myapp-user strongpassword123

# Delete user
sudo rabbitmqctl delete_user myapp-user

# List users
sudo rabbitmqctl list_users

# Change user password
sudo rabbitmqctl change_password myapp-user newpassword456
```

**Via HTTP API:**

```bash
# Create user
curl -u guest:guest -X PUT \
  -H "content-type: application/json" \
  -d '{"username":"myapp-user","password":"strongpassword123","tags":"management"}' \
  http://localhost:15672/api/users/myapp-user

# Delete user
curl -u guest:guest -X DELETE http://localhost:15672/api/users/myapp-user

# List users
curl -u guest:guest http://localhost:15672/api/users
```

### Setting Permissions

**Via Management UI:**

1. Open http://localhost:15672
2. Click "Admin" tab → Click on user
3. Scroll to "Permissions"
4. Click "Set permission"
5. Select virtual host
6. Check Configure, Write, Read as needed
7. Click "Set permission"

**Via rabbitmqctl:**

```bash
# Set permissions (Configure, Write, Read)
sudo rabbitmqctl set_permissions -p ".*" -c ".*" -k ".*" myapp-user myapp-vhost

# Remove all permissions
sudo rabbitmqctl clear_permissions -p ".*" -c ".*" -k ".*" myapp-user myapp-vhost

# List user permissions
sudo rabbitmqctl list_user_permissions myapp-user
```

**Via HTTP API:**

```bash
# Set permission
curl -u guest:guest -X PUT \
  -H "content-type: application/json" \
  -d '{"configure":".*","write":".*","read":".*"}' \
  http://localhost:15672/api/permissions/myapp-vhost/myapp-user

# Delete permission
curl -u guest:guest -X DELETE \
  http://localhost:15672/api/permissions/myapp-vhost/myapp-user
```

### Permission Regular Expressions

**Permission scopes:**

| Scope | Pattern | Matches | Example |
|-------|--------|---------|---------|
| **Exchange** | configure | Regex pattern for exchange names | `orders` or `orders.*` |
| **Queue** | configure | Regex pattern for queue names | `results` or `results.*` |
| **Write** | write | Regex pattern for routing keys | `order.created` or `order.*` |
| **Read** | read | Regex pattern for routing keys | `#` (all) or `order.*` |

**Examples:**

```bash
# Full access to everything
sudo rabbitmqctl set_permissions -p ".*" -c ".*" -k ".*" user vhost

# Access only to orders exchange and queue
sudo rabbitmqctl set_permissions -p "orders" -c "orders" -k "orders" user vhost

# Access to all exchanges/queues, but only read
sudo rabbitmqctl set_permissions -p ".*" -c "" -k ".*" user vhost
```

### Version Notes

- **RabbitMQ 3.12+:** All auth/permission features fully supported
- **Default vhost:** `/` always available
- **Default user:** `guest` (localhost only, full access)
- **LDAP/AD:** Requires rabbitmq_auth_backend_ldap plugin
- **OAuth 2.0:** Requires rabbitmq_auth_backend_oauth2 plugin

---

## 6️⃣ Where Virtual Hosts, Users and Permissions Should Be Applied (With Example)

### Production Setup for Multi-Application Environment

**Scenario:** Two applications sharing one RabbitMQ instance

- **App A:** Order processing system
- **App B:** Inventory management system

**Step 1: Create virtual hosts**

```bash
# Create vhost for App A
sudo rabbitmqctl add_vhost app-a-production

# Create vhost for App B
sudo rabbitmqctl add_vhost app-b-production
```

**Step 2: Create users**

```bash
# Create users for App A
sudo rabbitmqctl add_user app-a-producer strong_password_a1
sudo rabbitmqctl add_user app-a-consumer strong_password_a2

# Create users for App B
sudo rabbitmqctl add_user app-b-producer strong_password_b1
sudo rabbitmqctl add_user app-b-consumer strong_password_b2

# Create admin user
sudo rabbitmqctl add_user admin secure_admin_password
sudo rabbitmqctl set_user_tags admin administrator
```

**Step 3: Set permissions**

```bash
# App A producer permissions (Write, Read)
sudo rabbitmqctl set_permissions -p ".*" -c "" -k ".*" app-a-producer app-a-production

# App A consumer permissions (Configure, Write, Read)
sudo rabbitmqctl set_permissions -p ".*" -c ".*" -k ".*" app-a-consumer app-a-production

# App B producer permissions (Write, Read)
sudo rabbitmqctl set_permissions -p ".*" -c "" -k ".*" app-b-producer app-b-production

# App B consumer permissions (Configure, Write, Read)
sudo rabbitmqctl set_permissions -p ".*" -c ".*" -k ".*" app-b-consumer app-b-production

# Admin permissions (Full access to all vhosts)
sudo rabbitmqctl set_permissions -p ".*" -c ".*" -k ".*" admin ".*"
```

**Step 4: Verify in Management UI**

Open http://localhost:15672:
- Click "Admin" → "Virtual Hosts" → See `app-a-production`, `app-b-production`
- Click "Admin" → "Users" → See all users
- Click on user → See permissions for each vhost

### Application Code with Users

**Producer connecting as specific user:**

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        'localhost',
        credentials=pika.PlainCredentials(
            username='app-a-producer',
            password='strong_password_a1'
        ),
        virtual_host='app-a-production'  # Connect to specific vhost
    )
)
channel = connection.channel()

# Create exchange and queue in vhost
channel.exchange_declare(exchange='orders', exchange_type='direct')
channel.queue_declare(queue='results')

order = {
    "order_id": 12345,
    "amount": 99.99,
    "timestamp": "2024-01-15T10:30:00Z"
}

channel.basic_publish(
    exchange='orders',
    routing_key='results',
    body=json.dumps(order)
)

print(f" [x] Sent order to vhost: app-a-production")
connection.close()
```

**Consumer connecting as specific user:**

```python
import pika
import json

def callback(ch, method, properties, body):
    order = json.loads(body)
    print(f" [x] Processed order {order['order_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        'localhost',
        credentials=pika.PlainCredentials(
            username='app-a-consumer',
            password='strong_password_a2'
        ),
        virtual_host='app-a-production'  # Connect to specific vhost
    )
)
channel = connection.channel()

channel.queue_declare(queue='results')
channel.basic_consume(queue='results', on_message_callback=callback)

print(f" [*] Consuming from vhost: app-a-production")
channel.start_consuming()
```

### Separating Environments

**Scenario:** One RabbitMQ instance for dev, staging, production

```bash
# Create vhosts for each environment
sudo rabbitmqctl add_vhost myapp-dev
sudo rabbitmqctl add_vhost myapp-staging
sudo rabbitmqctl add_vhost myapp-prod

# Create dev user (full access to dev vhost)
sudo rabbitmqctl add_user myapp-dev-dev dev_pass_123
sudo rabbitmqctl set_permissions -p ".*" -c ".*" -k ".*" myapp-dev-dev myapp-dev

# Create staging user (full access to staging vhost)
sudo rabbitmqctl add_user myapp-staging-dev staging_pass_456
sudo rabbitmqctl set_permissions -p ".*" -c ".*" -k ".*" myapp-staging-dev myapp-staging

# Create prod user (producer - write/read, consumer - configure/write/read)
sudo rabbitmqctl add_user myapp-prod-producer prod_pass_789
sudo rabbitmqctl set_permissions -p ".*" -c "" -k ".*" myapp-prod-producer myapp-prod

sudo rabbitmqctl add_user myapp-prod-consumer prod_pass_abc
sudo rabbitmqctl set_permissions -p ".*" -c ".*" -k ".*" myapp-prod-consumer myapp-prod
```

### Best Practices

**Virtual Host Design:**
✅ Use descriptive vhost names (include app/environment)  
✅ Separate dev/staging/prod vhosts  
✅ One vhost per application or tenant  
✅ Enable tracing on production vhosts  
✅ Document vhost purpose and usage  
✅ Use consistent naming convention  

**User Management:**
✅ Create one user per application or service  
✅ Use strong passwords  
✅ Disable default guest user in production  
✅ Use admin user only for management  
✅ Implement user lifecycle (create/disable/delete)  
✅ Document user purposes  

**Permissions:**
✅ Follow principle of least privilege  
✅ Use read-only for producers when possible  
✅ Use regex patterns to limit access scope  
✅ Regularly audit permissions  
✅ Separate configure vs write vs read  
✅ Document permission matrix  

### Common Mistakes

❌ Using default guest/guest in production → Security risk  
❌ Using same vhost for all apps → Queue name conflicts  
❌ Giving everyone configure access → Security risk  
❌ Not setting permissions → Users can't access anything  
❌ Using weak passwords → Security vulnerability  
❌ Forgetting to specify virtual_host → Connects to / instead of intended vhost  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Security Breach (The Unauthorized Access)**

You're running a production RabbitMQ instance for a payment processing system. You have:

- Payment producer (sends payment requests)
- Payment consumer (processes payments)
- Analytics service (reads payment data)

Current setup:
- Everyone uses default guest/guest credentials
- All in default vhost (/)
- No access control - anyone can do anything

**Problems:**
- Analytics service accidentally deleted payment queue
- Developer from different team modified exchange settings
- No way to revoke access for contractors
- No audit trail of who did what
- **Impact:** Queue deleted, 50 payments lost, $25K in financial discrepancies, production outage for 2 hours

### 🧪 Lab Tasks

**Step 1: Set up RabbitMQ**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

**Step 2: Create vulnerable setup (no security)**

Create `vulnerable_producer.py`:

```python
import pika
import json

# PROBLEM: Using guest/guest, default vhost
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.exchange_declare(exchange='payments', exchange_type='direct')
channel.queue_declare(queue='payment-queue')

# Send payment
payment = {
    "payment_id": "pay_123",
    "amount": 99.99,
    "account": "account_456"
}

channel.basic_publish(
    exchange='payments',
    routing_key='payment-queue',
    body=json.dumps(payment)
)

print(f" [x] Sent payment to default vhost")
connection.close()
```

**Step 3: Create vulnerable consumer (no security)**

Create `vulnerable_consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    payment = json.loads(body)
    print(f" [x] Processing payment: {payment['payment_id']}")
    
    # PROBLEM: Can delete queue!
    if method.delivery_tag == 10:
        print(f" [DANGER] Deleting queue!")
        channel.queue_delete(queue='payment-queue')
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

# PROBLEM: Using guest/guest, default vhost
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.exchange_declare(exchange='payments', exchange_type='direct')
channel.queue_declare(queue='payment-queue')
channel.basic_consume(queue='payment-queue', on_message_callback=callback)

print(f" [*] Consuming from default vhost (can delete queues!)")
channel.start_consuming()
```

**Step 4: Reproduce problem**

```bash
# Terminal 1: Vulnerable consumer
python3 vulnerable_consumer.py

# Terminal 2: Vulnerable producer (send multiple payments)
python3 vulnerable_consumer.py
```

**Expected observation:**
- Consumer processes payments
- After 10th message, consumer deletes queue
- Subsequent payments are lost (no queue)
- No security - anyone can do anything

**Step 5: View in Management UI**

Open http://localhost:15672:
- Click "Admin" → "Users" → See only guest user
- Click "Admin" → "Virtual Hosts" → See only default vhost
- Click on guest user → Full access to everything
- Observe no access control

### ✅ Solution & Explanation

**Solution: Implement Virtual Hosts, Users, and Permissions**

**Step 1: Create virtual host**

```bash
sudo rabbitmqctl add_vhost payment-production
```

**Step 2: Create users**

```bash
# Create payment producer user
sudo rabbitmqctl add_user payment-producer pay_prod_pass_123

# Create payment consumer user
sudo rabbitmqctl add_user payment-consumer pay_cons_pass_456

# Create analytics user (read-only)
sudo rabbitmqctl add_user analytics-user analytics_pass_789

# Create admin user
sudo rabbitmqctl add_user payment-admin admin_pass_abc
sudo rabbitmqctl set_user_tags payment-admin administrator
```

**Step 3: Set permissions**

```bash
# Producer permissions (Write only - no Configure)
sudo rabbitmqctl set_permissions -p ".*" -c "" -k ".*" payment-producer payment-production

# Consumer permissions (Configure, Write, Read)
sudo rabbitmqctl set_permissions -p ".*" -c ".*" -k ".*" payment-consumer payment-production

# Analytics user permissions (Read only)
sudo rabbitmqctl set_permissions -p ".*" -c "" -k ".*" analytics-user payment-production

# Admin permissions (Full access to this vhost)
sudo rabbitmqctl set_permissions -p ".*" -c ".*" -k ".*" payment-admin payment-production
```

**Step 4: Verify in Management UI**

Open http://localhost:15672:
- Click "Admin" → "Users" → See 4 new users
- Click on each user → See permissions for `payment-production`
- Observe: analytics-user has Read only (no Configure)

**Step 5: Create secured producer**

Create `secured_producer.py`:

```python
import pika
import json

# FIX: Use specific user and vhost
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        'localhost',
        credentials=pika.PlainCredentials(
            username='payment-producer',
            password='pay_prod_pass_123'
        ),
        virtual_host='payment-production'  # Connect to specific vhost
    )
)
channel = connection.channel()

channel.exchange_declare(exchange='payments', exchange_type='direct')
channel.queue_declare(queue='payment-queue')

# Send payment
payment = {
    "payment_id": "pay_123",
    "amount": 99.99,
    "account": "account_456"
}

channel.basic_publish(
    exchange='permissions',
    routing_key='payment-queue',
    body=json.dumps(payment)
)

print(f" [x] Sent payment to vhost: payment-production (secured)")
connection.close()
```

**Step 6: Create secured consumer**

Create `secured_consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    payment = json.loads(body)
    print(f" [x] Processing payment: {payment['payment_id']}")
    
    # FIX: Can't delete queue (no Configure permission)
    if method.delivery_tag == 10:
        try:
            # PROBLEM TRY: Try to delete queue
            channel.queue_delete(queue='payment-queue')
            print(f" [ERROR] Deletion succeeded - CONFIGURE permission should be denied!")
        except pika.exceptions.ChannelClosedByBroker as e:
            if "ACCESS_REFUSED" in str(e):
                print(f" [✓] Deletion denied (no Configure permission)")
            else:
                print(f" [ERROR] Unexpected error: {e}")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

# FIX: Use specific user and vhost
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        'localhost',
        credentials=pika.PlainCredentials(
            username='payment-consumer',
            password='pay_cons_pass_456'
        ),
        virtual_host='payment-production'  # Connect to specific vhost
    )
)
channel = connection.channel()

channel.exchange_declare(exchange='payments', exchange_type='direct')
channel.queue_declare(queue='payment-queue')
channel.basic_consume(queue='payment-queue', on_message_callback=callback)

print(f" [*] Consuming from vhost: payment-production (secured)")
channel.start_consuming()
```

**Step 7: Test with analytics user**

Create `analytics_consumer.py`:

```python
import pika
import json

def callback(ch, method, properties, body):
    payment = json.loads(body)
    print(f" [Analytics] Track metric: {payment['payment_id']} ${payment['amount']}")
    
    # Can only read (no Write)
    # Try to publish
    try:
        channel.basic_publish(
            exchange='payments',
            routing_key='payment-queue',
            body=json.dumps({"analytics": "data"})
        )
        print(f" [ERROR] Publish succeeded - WRITE permission should be denied!")
    except pika.exceptions.ChannelClosedByBroker as e:
        if "ACCESS_REFUSED" in str(e):
            print(f" [✓] Publish denied (no Write permission)")
        else:
            print(f" [ERROR] Unexpected error: {e}")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

# FIX: Use analytics user (Read only)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        'localhost',
        credentials=pika.PlainCredentials(
            username='analytics-user',
            password='analytics_pass_789'
        ),
        virtual_host='payment-production'  # Connect to specific vhost
    )
)
channel = connection.channel()

channel.exchange_declare(exchange='payments', exchange_type='direct')
channel.queue_declare(queue='payment-queue')
channel.basic_consume(queue='payment-queue', on_message_callback=callback)

print(f" [*] Analytics consuming from vhost: payment-production (read-only)")
channel.start_consuming()
```

**How to verify:**

```bash
# Clear RabbitMQ
docker stop rabbitmq && docker rm rabbitmq
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# Run setup commands from above
sudo rabbitmqctl add_vhost payment-production
sudo rabbitmqctl add_user payment-producer pay_prod_pass_123
sudo rabbitmqctl add_user payment-consumer pay_cons_pass_456
sudo rabbitmqctl add_user analytics-user analytics_pass_789
sudo rabbitmqctl set_user_tags admin administrator
sudo rabbitmqctl set_permissions -p ".*" -c "" -k ".*" payment-producer payment-production
sudo rabbitmqctl set_permissions -p ".*" -c ".*" -k ".*" payment-consumer payment-production
sudo rabbitmqctl set_permissions -p ".*" -c "" -k ".*" analytics-user payment-production
sudo rabbitmqctl set_permissions -p ".*" -c ".*" -k ".*" admin ".*"

# Terminal 1: Secured consumer
python3 secured_consumer.py

# Terminal 2: Secured producer (send 20 payments)
for i in {1..20}; do python3 secured_producer.py; done

# Terminal 3: Analytics consumer
python3 analytics_consumer.py
```

**Expected output:**

```
# Secured consumer
[x] Processing payment: pay_1
[x] Processing payment: pay_2
...
[x] Processing payment: pay_10
[✓] Deletion denied (no Configure permission)
[x] Processing payment: pay_11
...

# Analytics consumer
[Analytics] Track metric: pay_1 $99.99
[Analytics] Track metric: pay_2 $99.99
...
[Analytics] Track metric: pay_10 $99.99
[✓] Publish denied (no Write permission)
[Analytics] Track metric: pay_11 $99.99
...
```

**View in Management UI:**

1. Open http://localhost:15672
2. Click "Admin" → "Users"
3. See 4 users with proper permissions
4. Click on `analytics-user`:
   - `payment-production` vhost: Read only (no Write/Configure)
5. Click on `payment-consumer`:
   - `payment-production` vhost: Configure, Write, Read
6. Click "Admin" → "Virtual Hosts"
7. See `payment-production` with exchanges and queues

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**Virtual Hosts:**
✅ Use descriptive names (include app/environment)  
✅ Separate dev/staging/prod vhosts  
✅ One vhost per application or tenant  
✅ Enable tracing on production vhosts  
✅ Document vhost purpose and usage  
✅ Use consistent naming convention  

❌ Use default / vhost in production  
❌ Mix applications in same vhost  
❌ Use generic vhost names  
❌ Forget to delete unused vhosts  
❌ Disable tracing on production vhosts  

**Users:**
✅ Create one user per application or service  
✅ Use strong passwords  
✅ Disable default guest user in production  
✅ Use admin user only for management  
✅ Regularly rotate passwords  
✅ Disable or revoke unused users  
✅ Document user purposes  

❌ Use guest/guest in production  
❌ Share credentials across apps  
❌ Use weak passwords  
❌ Give everyone admin access  
❌ Forget to change default passwords  
❌ Leave unused accounts active  

**Permissions:**
✅ Follow principle of least privilege  
✅ Use read-only when possible  
✅ Use regex patterns to limit access  
✅ Regularly audit permissions  
✅ Separate configure vs write vs read  
✅ Document permission matrix  
✅ Test permissions thoroughly  

❌ Give everyone full access  
❌ Use wildcard patterns unnecessarily  
❌ Forget to set permissions  
❌ Ignore permission errors  
❌ Mix different permission levels in one user  
❌ Don't audit permission changes  

### Virtual Host Naming Convention

```
Format: {application-name}-{environment}

Examples:
myapp-production
myapp-staging
myapp-development
payment-processor-prod
analytics-service-dev
team-backend-staging
team-frontend-prod

Avoid:
❌ prod, staging (too generic)
❌ vhost1, vhost2 (no context)
❌ app1, app2 (no environment)
❌ test, live (not descriptive)
```

### User Management Guidelines

```bash
# Create user with tags
sudo rabbitmqctl add_user myapp-producer password123 \
  --tag "monitoring" --tag "policymaker"

# List users with tags
sudo rabbitmqctl list_users

# Change user password
sudo rabbitmqctl change_password myapp-producer newpassword456

# Disable user (revoke all permissions)
sudo rabbitmqctl clear_permissions -p ".*" -c ".*" -k ".*" myapp-producer

# Delete user
sudo rabbitmqctl delete_user myapp-producer
```

### Permission Matrix

```
Application: Payment Processor
Vhost: payment-prod

User              | Configure | Write | Read | Purpose
------------------|-----------|-------|------|---------
payment-producer   |     ✅     |  ✅  |   ✅  | Publish payments
payment-consumer   |     ✅     |  ✅  |   ✅  | Process payments
analytics-user     |     ❌     |  ❌  |   ✅  | Read metrics only
payment-admin      |     ✅     |  ✅  |   ✅  | Management
```

### Production Considerations

**Disabling Default Guest User:**

```conf
# /etc/rabbitmq/rabbitmq.conf

# Disable guest user (CRITICAL for production)
loopback_users.guest = false
```

**Using LDAP/AD Authentication:**

```bash
# Enable LDAP plugin
sudo rabbitmq-plugins enable rabbitmq_auth_backend_ldap

# Configure LDAP in rabbitmq.conf
auth_backends.ldap1 = rabbit_auth_backend_ldap
auth_backends.ldap1.servers.1 = host=ldap.example.com
auth_backends.ldap1.servers.1.bind_dn = CN=rabbitmq,OU=Services,DC=example,DC=com
auth_backends.ldap1.servers.1.bind_dn_password = ${LDAP_PASSWORD}
auth_backends.ldap1.servers.1.user_search_pattern = (cn=$${username})
```

**Using OAuth 2.0 Authentication:**

```bash
# Enable OAuth2 plugin
sudo rabbitmqctl enable rabbitmq_auth_backend_oauth2

# Configure OAuth2 in rabbitmq.conf
auth_oauth2.scope_prefix = rabbitmq.
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: What's the difference between a virtual host and a user?**

A: Virtual host is a namespace that isolates exchanges, queues, and bindings. User is an authentication entity that connects to RabbitMQ. Users have permissions to access specific virtual hosts. Many users can connect to the same virtual host.

**Q2: Why shouldn't you use the default / virtual host in production?**

A: The default / vhost is shared by all applications, leading to queue name conflicts and no isolation. Always create named virtual hosts for production applications to ensure separation and avoid conflicts.

**Q3: What's the difference between Configure, Write, and Read permissions?**

A: Configure permission allows creating/deleting exchanges and queues. Write permission allows publishing messages. Read permission allows consuming messages. You can combine them (e.g., Write+Read allows publishing and consuming but not configuring).

**Q4: How do you revoke access for a specific application?**

A: Delete the user or clear all permissions for that user. For temporary revocation, you can clear permissions. For permanent revocation, delete the user. Changes apply immediately (no restart needed).

**Q5: What's the principle of least privilege?**

A: Grant users only the minimum permissions they need to do their job. For example, producers need Write and Read but not Configure. Analytics services need Read but not Write or Configure. This minimizes security risk.

### Production Pitfalls

**Pitfall 1: Using default guest/guest in production**
- Problem: Everyone has full access to everything
- Detection: Unauthorized access, data breaches
- Solution: Create specific users, disable guest

**Pitfall 2: Not separating environments**
- Problem: Development code accidentally affects production
- Detection: Production incidents from dev mistakes
- Solution: Separate vhosts for dev/staging/prod

**Pitfall 3: Over-permissioning**
- Problem: Users have more access than needed
- Detection: Accidental deletions or modifications
- Solution: Follow principle of least privilege

**Pitfall 4: Not auditing permissions**
- Problem: Unauthorized access goes unnoticed
- Detection: Security breaches found too late
- Solution: Regular permission audits and reviews

### Advanced Security Concepts

**User Tags for Management UI:**

```bash
# Create user with tags
sudo rabbitmqctl add_user app-monitor pass123 \
  --tag "monitoring" \
  --tag "policymaker"

# Tags affect UI display
# monitoring = Can see connection/queue/channels
# policymaker = Can create/manage policies
```

**Impersonator Permission (Troubleshooting):**

```bash
# Give user impersonator permission
sudo rabbitmqctl set_permissions -p ".*" -c ".*" -k ".*" troubleshooter vhost

# User can act as another user
# Useful for debugging issues without sharing credentials
```

**Quota Limits (Resource limiting):**

```bash
# Set max connections per user
sudo rabbitmqctl set_user_limits myapp-producer max-connections 10

# Set max channels per connection
sudo rabbitmqctl set_user_limits myapp-producer max-channels 100
```

---

## 📚 Summary

Virtual hosts, users, and permissions provide the security and isolation framework for RabbitMQ. Virtual hosts act as namespaces separating applications and environments. Users provide authentication credentials. Permissions grant granular access control (Configure, Write, Read) per virtual host.

**Key takeaways:**
- Virtual hosts isolate exchanges, queues, and bindings
- Use named vhosts instead of default / in production
- Create specific users for each application or service
- Disable default guest user in production
- Set appropriate permissions (Configure, Write, Read)
- Follow principle of least privilege
- Use strong passwords and regular rotation
- Separate dev/staging/prod into different vhosts

**Next steps:**
- Practice creating vhosts, users, and permissions
- Learn about advanced authentication (LDAP/OAuth)
- Understand connection and channel management
- Learn about message acknowledgment and reliability
- Explore clustering for high availability

---

**Module 01 - Core Concepts**  
**Lesson 04 - Complete**
**Module 01 - Core Concepts - COMPLETE** ✅