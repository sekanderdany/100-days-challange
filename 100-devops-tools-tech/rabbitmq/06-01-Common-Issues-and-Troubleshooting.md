# 06-01: Common Issues and Troubleshooting

## 🔧 What Is Troubleshooting

**Troubleshooting** is the systematic process of identifying, diagnosing, and resolving RabbitMQ issues. This includes connection failures, message loss, queue issues, and system errors.

Think of troubleshooting like being a detective:

- **Problem Identification** = Gathering clues (symptoms, errors)
- **Root Cause Analysis** = Solving the mystery (finding the cause)
- **Resolution** = Closing the case (fixing the issue)
- **Prevention** = Preventing future crimes (lessons learned)

**Where troubleshooting fits in RabbitMQ architecture:**

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│  Producer   │        │  Consumer    │        │  Troubleshooting│        │  Logs        │        │  Metrics      │
└──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
       │                    │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼                    ▼                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                    RabbitMQ Troubleshooting                                                │
│                    (Problem Identification, Root Cause Analysis, Resolution)                  │
│                                                                                   │
│   ┌────────────────────────────────────────────────────────────────────────┐   │
│   │              │              │              │               │   │   │   │
│   │    Connection   │     Message     │     Queue       │   │   │   │
│   │    Issues       │     Loss        │     Issues       │   │   │   │
│   │    (Network)      │     (Reliability) │     (Config)      │   │   │   │
│   │              │              │              │               │   │   │   │
│   │              │              │              │               │   │   │   │
│   └──────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                                                   │
└────────────────────────────────────────────────────────────────────────────────────────────┘
       │                    │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼                    ▼                    ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│  Connection   ││  Message     ││  Queue       ││  Resolved     ││  Prevented    │
│  Issues       ││  Loss        ││  Issues       ││  (Fixed)      ││  (Learned)     │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘
   (Diagnosed)     (Recovered)     (Fixed)       (Production)     (Future-proof)
```

**Key concepts:**
- **Problem Identification:** Gathering symptoms (error messages, user reports)
- **Root Cause Analysis:** Finding the underlying cause (not just symptoms)
- **Resolution:** Fixing the issue (configuration changes, code fixes)
- **Prevention:** Learning from issues (documentation, runbooks)
- **Logs:** System logs, error logs, audit trails (evidence)
- **Metrics:** Performance metrics, health checks (data)
- **Diagnostics Tools:** rabbitmqctl, Management UI, diagnostics tools

---

## 2️⃣ Problems Solved by Troubleshooting

### The "Connection Failure" Problem

**Connection Refused:**

```
Symptoms:
- Producer can't connect (connection refused)
- Consumer can't connect (connection refused)
- RabbitMQ Management UI inaccessible

Diagnosis:
- RabbitMQ not running (process stopped)
- Firewall blocking connection (port 5672)
- Wrong hostname/port configuration

Resolution:
- Start RabbitMQ service
- Configure firewall (open port 5672)
- Verify hostname/port (connection string)
```

### The "Message Loss" Problem

**Missing Messages:**

```
Symptoms:
- Messages published but not consumed
- Queue depth increasing (backlog)
- Consumers not receiving messages

Diagnosis:
- No consumer connected (consumer not running)
- Wrong routing key (messages not routed to queue)
- Wrong exchange type (messages dropped)

Resolution:
- Start consumer (ensure consumer running)
- Verify routing key (match producer)
- Verify exchange type (match queue binding)
```

### The "Queue Issues" Problem

**Queue Blocked:**

```
Symptoms:
- Queue depth increasing (backlog)
- Consumers not receiving messages
- RabbitMQ slow (high CPU/memory)

Diagnosis:
- Queue blocked (consumer not ACKing)
- Consumer prefetch too low (single message processing)
- Consumer too slow (can't keep up with producer)

Resolution:
- Fix consumer ACK (ensure proper acknowledgment)
- Increase prefetch count (batch processing)
- Scale consumers (more consumers)
```

---

## 3️⃣ Common Issues and Solutions

### Issue 1: RabbitMQ Not Starting

**Symptoms:**
- RabbitMQ service won't start
- Process exits immediately
- Error logs (Erlang port already in use)

**Diagnosis:**
```bash
# Check RabbitMQ status
sudo systemctl status rabbitmq-server

# Check RabbitMQ logs
sudo journalctl -u rabbitmq-server -n 100
```

**Common Causes:**
- Port already in use (Erlang port 25672)
- Permission denied (no file access)
- Configuration error (invalid rabbitmq.conf)

**Resolution:**
```bash
# SOLUTION: Stop existing RabbitMQ
sudo systemctl stop rabbitmq-server

# SOLUTION: Check ports (netstat, lsof)
sudo netstat -tulpn | grep 25672

# SOLUTION: Fix permissions
sudo chown -R rabbitmq:rabbitmq /var/lib/rabbitmq

# SOLUTION: Fix configuration
sudo rabbitmqctl status
sudo rabbitmq-plugins list

echo "[✓] RabbitMQ not starting issue resolved"
```

### Issue 2: Consumer Can't Connect

**Symptoms:**
- Consumer connection refused
- Authentication failed (wrong credentials)
- Permission denied (no access to vhost)

**Diagnosis:**
```bash
# Check RabbitMQ users
sudo rabbitmqctl list_users

# Check RabbitMQ vhost permissions
sudo rabbitmqctl list_permissions -p /production
```

**Common Causes:**
- Wrong username/password (authentication failed)
- User not created (permission denied)
- User no access to vhost (permission denied)

**Resolution:**
```bash
# SOLUTION: Create user
sudo rabbitmqctl add_user app_user appPassword456!

# SOLUTION: Grant vhost permissions
sudo rabbitmqctl set_permissions -p /production app_user ".*" ".*" ".*"

# SOLUTION: Verify permissions
sudo rabbitmqctl list_permissions -p /production

echo "[✓] Consumer can't connect issue resolved"
```

### Issue 3: Messages Not Being Delivered

**Symptoms:**
- Messages published but not consumed
- Queue depth increasing (backlog)
- Consumers not receiving messages

**Diagnosis:**
```bash
# Check queue depth
sudo rabbitmqctl list_queues name messages consumers

# Check bindings
sudo rabbitmqctl list_bindings
```

**Common Causes:**
- Wrong exchange type (messages dropped)
- Wrong routing key (messages not routed)
- No queue bound (messages nowhere to go)
- No consumer connected (messages queued)

**Resolution:**
```bash
# SOLUTION: Verify exchange type
sudo rabbitmqctl list_exchanges name type

# SOLUTION: Verify routing key
sudo rabbitmqctl list_bindings source destination routing_key

# SOLUTION: Verify queue binding
sudo rabbitmqctl list_bindings

# SOLUTION: Check consumer connections
sudo rabbitmqctl list_connections

echo "[✓] Messages not being delivered issue resolved"
```

### Issue 4: High Queue Depth

**Symptoms:**
- Queue depth increasing rapidly (backlog)
- Consumers can't keep up (bottleneck)
- RabbitMQ slow (high CPU/memory)

**Diagnosis:**
```bash
# Check queue depth
sudo rabbitmqctl list_queues name messages

# Check consumer count
sudo rabbitmqctl list_connections name state

# Check CPU/memory usage
top -p $(pgrep -f rabbitmq)
```

**Common Causes:**
- Consumer too slow (can't keep up)
- Consumer prefetch too low (single message processing)
- Producer rate too high (consumer overwhelmed)

**Resolution:**
```bash
# SOLUTION: Increase prefetch count
# Consumer: channel.basic_qos(prefetch_count=50)

# SOLUTION: Scale consumers (more consumers)
# Deploy more consumer instances

# SOLUTION: Check consumer performance
# Monitor consumer processing time

echo "[✓] High queue depth issue resolved"
```

### Issue 5: RabbitMQ Memory Exhaustion

**Symptoms:**
- RabbitMQ crash (out of memory)
- System instability (performance degradation)
- Data loss (messages lost)

**Diagnosis:**
```bash
# Check RabbitMQ memory usage
sudo rabbitmqctl status | grep memory

# Check system memory
free -h

# Check RabbitMQ logs
sudo journalctl -u rabbitmq-server -n 100 | grep memory
```

**Common Causes:**
- vm_memory_high_watermark too high (no disk flush)
- Too many messages in RAM (no persistence)
- Large messages in RAM (memory exhaustion)

**Resolution:**
```bash
# SOLUTION: Configure memory watermark
cat > /etc/rabbitmq/rabbitmq.conf << EOF
# SOLUTION: Memory Management
vm_memory_high_watermark = 4GB
disk_free_limit.absolute = 5GB
EOF

sudo systemctl restart rabbitmq-server

# SOLUTION: Enable persistent queues
# Producer: channel.queue_declare(queue='messages', durable=True)

echo "[✓] RabbitMQ memory exhaustion issue resolved"
```

### Issue 6: RabbitMQ Disk Full

**Symptoms:**
- RabbitMQ crash (disk full)
- Messages rejected (no disk space)
- Data loss (messages lost)

**Diagnosis:**
```bash
# Check disk space
df -h /var/lib/rabbitmq

# Check RabbitMQ disk usage
sudo rabbitmqctl status | grep disk

# Check RabbitMQ logs
sudo journalctl -u rabbitmq-server -n 100 | grep disk
```

**Common Causes:**
- Disk full (no space for messages)
- disk_free_limit too low (aggressive threshold)
- Too many retained messages (no cleanup)

**Resolution:**
```bash
# SOLUTION: Clean up disk space
sudo rm -rf /var/lib/rabbitmq/mnesia/*

# SOLUTION: Configure disk free limit
cat > /etc/rabbitmq/rabbitmq.conf << EOF
# SOLUTION: Disk Management
disk_free_limit.absolute = 5GB
EOF

sudo systemctl restart rabbitmq-server

# SOLUTION: Configure message retention
# Producer: channel.queue_declare(queue='messages', durable=True, arguments={'x-message-ttl': 86400000})

echo "[✓] RabbitMQ disk full issue resolved"
```

### Issue 7: Authentication Failed

**Symptoms:**
- Authentication failed (wrong credentials)
- Permission denied (no access to vhost)
- Guest access denied (guest user disabled)

**Diagnosis:**
```bash
# Check RabbitMQ users
sudo rabbitmqctl list_users

# Check RabbitMQ authentication
sudo rabbitmqctl authenticate user password

# Check RabbitMQ access control
sudo rabbitmqctl list_permissions
```

**Common Causes:**
- Wrong username/password (authentication failed)
- Guest user disabled (guest access denied)
- User no access to vhost (permission denied)
- Authentication mechanism disabled (plain disabled)

**Resolution:**
```bash
# SOLUTION: Create user
sudo rabbitmqctl add_user app_user appPassword456!

# SOLUTION: Grant vhost permissions
sudo rabbitmqctl set_permissions -p /production app_user ".*" ".*" ".*"

# SOLUTION: Enable authentication
cat > /etc/rabbitmq/rabbitmq.conf << EOF
# SOLUTION: Authentication
auth_mechanisms.plain.enabled = true
guest_access.enabled = false
EOF

sudo systemctl restart rabbitmq-server

echo "[✓] Authentication failed issue resolved"
```

### Issue 8: SSL/TLS Connection Issues

**Symptoms:**
- SSL/TLS handshake failed
- Certificate validation error
- Connection refused (SSL/TLS not configured)

**Diagnosis:**
```bash
# Check SSL/TLS configuration
sudo rabbitmqctl status | grep ssl

# Check certificates
openssl s_client -connect rabbitmq-server.example.com:5671 -showcerts

# Check RabbitMQ logs
sudo journalctl -u rabbitmq-server -n 100 | grep ssl
```

**Common Causes:**
- Invalid certificate (expired, wrong CA)
- Wrong cipher suite (incompatible encryption)
- Port mismatch (TCP 5672 vs SSL 5671)
- Client verification disabled (security risk)

**Resolution:**
```bash
# SOLUTION: Generate valid certificates
sudo openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/rabbitmq/rabbitmq-server.key \
  -out /etc/rabbitmq/rabbitmq-server.crt \
  -subj "/CN=rabbitmq-server.example.com/O=RabbitMQ Organization/C=US"

# SOLUTION: Configure SSL/TLS
cat > /etc/rabbitmq/rabbitmq.conf << EOF
# SOLUTION: SSL/TLS
listeners.ssl.default = 5671
ssl_options.certfile = /etc/rabbitmq/rabbitmq-server.crt
ssl_options.keyfile = /etc/rabbitmq/rabbitmq-server.key
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = true
EOF

sudo systemctl restart rabbitmq-server

echo "[✓] SSL/TLS connection issue resolved"
```

### Issue 9: RabbitMQ Cluster Issues

**Symptoms:**
- Cluster partition (nodes isolated)
- Node not joining cluster (network issues)
- Mirror queues not syncing (data inconsistency)

**Diagnosis:**
```bash
# Check cluster status
sudo rabbitmqctl cluster_status

# Check cluster nodes
sudo rabbitmqctl cluster_status | grep rabbit@

# Check ERLANG interconnectivity
sudo rabbitmqctl status | grep erlang
```

**Common Causes:**
- Network partition (nodes isolated)
- ERLANG cookie mismatch (cluster authentication)
- Firewall blocking ERLANG port (25672)
- DNS resolution issues (hostname mismatch)

**Resolution:**
```bash
# SOLUTION: Sync ERLANG cookie
sudo rabbitmqctl stop_app
sudo cat /var/lib/rabbitmq/.erlang.cookie > /home/rabbitmq/.erlang.cookie
sudo chown rabbitmq:rabbitmq /home/rabbitmq/.erlang.cookie
sudo rabbitmqctl start_app

# SOLUTION: Configure firewall (open ERLANG port)
sudo firewall-cmd --permanent --add-port=25672/tcp
sudo firewall-cmd --reload

# SOLUTION: Verify cluster status
sudo rabbitmqctl cluster_status

echo "[✓] RabbitMQ cluster issue resolved"
```

### Issue 10: RabbitMQ Plugin Issues

**Symptoms:**
- Plugin not loading (can't access features)
- Plugin conflict (incompatible plugins)
- Plugin not enabled (feature not available)

**Diagnosis:**
```bash
# Check enabled plugins
sudo rabbitmq-plugins list

# Check plugin status
sudo rabbitmq-plugins list -e | grep plugin_name

# Check RabbitMQ logs
sudo journalctl -u rabbitmq-server -n 100 | grep plugin
```

**Common Causes:**
- Plugin not enabled (feature not available)
- Plugin conflict (incompatible plugins)
- Wrong plugin version (RabbitMQ version mismatch)
- Plugin dependencies missing (required plugin not installed)

**Resolution:**
```bash
# SOLUTION: Enable plugin
sudo rabbitmq-plugins enable rabbitmq_management

# SOLUTION: Disable conflicting plugin
sudo rabbitmq-plugins disable plugin_name

# SOLUTION: Restart RabbitMQ
sudo systemctl restart rabbitmq-server

# SOLUTION: Verify plugin
sudo rabbitmq-plugins list | grep management

echo "[✓] RabbitMQ plugin issue resolved"
```

---

## 4️⃣ Troubleshooting Methodology

### Systematic Troubleshooting Process

**1. Identify the Problem:**

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│  Step 1: Identify the Problem (Gather Clues)                            │
└────────────────────────────────────────────────────────────────────────────────────┘

Symptoms:
- What's happening? (error messages, user reports)
- When does it happen? (frequency, timing)
- Who's affected? (producer, consumer, admin)
- Where does it happen? (which component, which queue)

Evidence:
- Error logs (system logs, error logs, audit trails)
- Metrics (performance metrics, health checks)
- Configuration (rabbitmq.conf, connection string)
- Environment (OS, network, RabbitMQ version)
```

**2. Reproduce the Issue:**

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│  Step 2: Reproduce the Issue (Test Hypothesis)                            │
└────────────────────────────────────────────────────────────────────────────────────┘

Test:
- Can I reproduce the issue? (consistent symptoms)
- What triggers the issue? (specific action, condition)
- Is it intermittent? (sometimes happens, sometimes not)

Hypothesis:
- What's the likely cause? (educated guess)
- What tests can I run? (diagnostic commands, tools)
- How can I validate the hypothesis? (test results)
```

**3. Analyze the Root Cause:**

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│  Step 3: Analyze the Root Cause (Find the Underlying Cause)                  │
└────────────────────────────────────────────────────────────────────────────────────┘

Analysis:
- What's causing the issue? (not just symptoms)
- What's the underlying problem? (configuration, code, network)
- What dependencies are involved? (other components, external services)

Tools:
- Logs (system logs, error logs, audit trails)
- Metrics (performance metrics, health checks)
- Diagnostics (rabbitmqctl, Management UI, rabbitmq-diagnostics)
```

**4. Resolve the Issue:**

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│  Step 4: Resolve the Issue (Fix the Problem)                                │
└────────────────────────────────────────────────────────────────────────────────────┘

Resolution:
- What's the fix? (configuration change, code fix, restart)
- How do I implement the fix? (step-by-step)
- How do I verify the fix? (test results)

Verification:
- Is the issue resolved? (symptoms gone)
- Are there any side effects? (new issues introduced)
- Is the fix permanent? (root cause addressed)
```

**5. Prevent Future Occurrences:**

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│  Step 5: Prevent Future Occurrences (Learn from the Issue)                       │
└────────────────────────────────────────────────────────────────────────────────────┘

Prevention:
- What caused the issue? (root cause analysis)
- How can I prevent it? (configuration, monitoring, documentation)
- What monitoring do I need? (alerts, health checks)
- What documentation do I need? (runbooks, knowledge base)

Continuous Improvement:
- Document the issue and resolution (knowledge base)
- Create troubleshooting runbooks (standard procedures)
- Implement monitoring and alerting (early warning)
- Share lessons learned (team training, post-mortems)
```

---

## 5️⃣ Installation / Setup

**RabbitMQ Troubleshooting uses built-in tools.** No installation required - just use rabbitmqctl, Management UI, logs, and diagnostics.

### Prerequisites

- RabbitMQ server running (or RabbitMQ Docker image available)
- Understanding of RabbitMQ architecture (components, connections, queues)
- Understanding of RabbitMQ configuration (rabbitmq.conf, plugins)
- Understanding of Linux system administration (logs, processes, networking)
- Understanding of troubleshooting methodology (systematic approach)
- Access to RabbitMQ logs (console, file logs)
- Access to RabbitMQ Management UI (port 15672)
- Understanding of diagnostic tools (rabbitmqctl, Management UI)

### Troubleshooting Tools

**Using rabbitmqctl:**

```bash
# Check RabbitMQ status
sudo rabbitmqctl status

# Check connections
sudo rabbitmqctl list_connections

# Check queues
sudo rabbitmqctl list_queues

# Check channels
sudo rabbitmqctl list_channels

# Check users
sudo rabbitmqctl list_users

# Check vhosts
sudo rabbitmqctl list_vhosts

# Check permissions
sudo rabbitmqctl list_permissions

# Check plugins
sudo rabbitmq-plugins list
```

**Using Management UI:**

```bash
# Open Management UI
http://localhost:15672

# Check Overview tab
# Check Connections tab
# Check Queues tab
# Check Channels tab
# Check Admin tab
```

**Using Logs:**

```bash
# Check RabbitMQ logs
sudo journalctl -u rabbitmq-server -f

# Check RabbitMQ error logs
sudo journalctl -u rabbitmq-server -p err -f

# Check RabbitMQ debug logs
sudo journalctl -u rabbitmq-server -p debug -f
```

### Version Notes

- **RabbitMQ 3.12+:** All troubleshooting tools fully supported
- **rabbitmqctl:** Command-line administration (status, connections, queues)
- **Management UI:** Web-based monitoring (metrics, connections, queues)
- **Log Files:** System logs, error logs (debugging, troubleshooting)
- **rabbitmq-diagnostics:** Diagnostics tool (health checks, memory analysis)
- **Debugging Tools:** Logs, metrics, diagnostics (troubleshooting, root cause analysis)

---

## 6️⃣ Where Troubleshooting Should Be Applied (With Example)

### Troubleshooting Configuration

**Scenario:** Consumer can't connect to RabbitMQ

**Troubleshooting Configuration (troubleshooting_config.json):**

```json
{
  "rabbitmq": {
    "troubleshooting": {
      "enabled": true,
      "methodology": "systematic",
      "steps": {
        "identify_problem": {
          "symptoms": [
            "Connection refused",
            "Authentication failed",
            "Permission denied"
          ],
          "evidence": {
            "logs": [
              "system_logs",
              "error_logs",
              "audit_logs"
            ],
            "metrics": [
              "connection_count",
              "authentication_failures"
            ],
            "configuration": {
              "rabbitmq_conf": "/etc/rabbitmq/rabbitmq.conf",
              "connection_string": "amqp://localhost:5672"
            }
          }
        },
        "reproduce_issue": {
          "test": "Can I connect to RabbitMQ?",
          "hypothesis": "Wrong credentials or permissions",
          "validation": "Test connection with correct credentials"
        },
        "analyze_root_cause": {
          "analysis": "Check user authentication and vhost permissions",
          "tools": [
            "rabbitmqctl",
            "Management UI",
            "logs"
          ]
        },
        "resolve_issue": {
          "resolution": "Create user and grant vhost permissions",
          "verification": "Test connection and verify access"
        },
        "prevent_future_occurrences": {
          "prevention": "Document user creation and permission management",
          "monitoring": {
            "alerts": {
              "authentication_failures": true,
              "permission_denied": true
            },
            "health_checks": {
              "rabbitmq_status": true,
              "user_access": true
            }
          },
          "documentation": {
            "runbooks": "Create user and grant permissions",
            "knowledge_base": "User authentication and vhost permissions"
          }
        }
      }
    }
  }
}
```

### Troubleshooting Connection Issues

**Diagnosing connection failures:**

```bash
# Check RabbitMQ status
sudo rabbitmqctl status

# Check RabbitMQ logs
sudo journalctl -u rabbitmq-server -n 100 | grep connection

# Check network connectivity
telnet rabbitmq-server.example.com 5672

echo "[!] Diagnosing connection issues (status, logs, network)"
```

### Troubleshooting Message Loss

**Diagnosing message loss:**

```bash
# Check queue depth
sudo rabbitmqctl list_queues name messages

# Check bindings
sudo rabbitmqctl list_bindings

# Check consumer connections
sudo rabbitmqctl list_connections

echo "[!] Diagnosing message loss (queue depth, bindings, consumers)"
```

### Best Practices

**Troubleshooting:**
✅ Use systematic troubleshooting approach (identify, reproduce, analyze, resolve, prevent)  
✅ Gather symptoms and evidence (logs, metrics, configuration)  
✅ Reproduce the issue (test hypothesis)  
✅ Analyze root cause (find underlying problem)  
✅ Resolve the issue (fix the problem)  
✅ Verify the fix (test results)  
✅ Prevent future occurrences (learn from issue)  
✅ Document issues and resolutions (knowledge base, runbooks)  
✅ Share lessons learned (team training, post-mortems)  

**Common Mistakes:**
❌ Not gathering symptoms (blind troubleshooting)  
❌ Not reproducing the issue (guessing without testing)  
❌ Not analyzing root cause (fixing symptoms only)  
❌ Not verifying the fix (unresolved issues)  
❌ Not documenting the issue (lessons lost)  
❌ Not preventing future occurrences (recurring issues)  
❌ Not sharing lessons learned (team doesn't learn)  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Consumer Connection Failure (The "Can't Connect" Problem)**

You're troubleshooting a consumer connection issue:

- Consumer can't connect to RabbitMQ (connection refused)
- Authentication failed (wrong credentials)
- Permission denied (no access to vhost)

Current implementation:
- Consumer trying to connect (guest user)
- RabbitMQ configured (guest disabled)
- No application user created (permission denied)
- **Impact:** Consumer can't consume messages, queue backlog, production downtime

### 🧪 Lab Tasks

**Step 1: Test Connection Issue**

```python
import pika

# PROBLEM: Test connection issue (guest user disabled)
try:
    # PROBLEM: Connect as guest user (guest user disabled)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost', port=5672)
    )
    channel = connection.channel()
    
    # PROBLEM: Publish message
    channel.queue_declare(queue='messages', durable=True)
    channel.basic_publish(exchange='', routing_key='messages', body='Test Message')
    
    print("[!] Connection successful (guest user - UNEXPECTED)")
    
    connection.close()
    
except pika.exceptions.AuthenticationError:
    print("[!] Authentication failed (wrong credentials)")
    
except pika.exceptions.ProbableAccessDeniedError:
    print("[!] Permission denied (guest user disabled)")
    
except Exception as e:
    print(f"[!] Connection error: {e}")
```

**Expected observation:**
- Consumer connection refused (guest user disabled)
- Authentication failed (wrong credentials)
- Permission denied (no access to vhost)
- **Impact:** Consumer can't consume messages, queue backlog, production downtime

### ✅ Solution & Explanation

**Solution: Create Application User and Grant Permissions**

**Step 1: Create Application User**

```bash
# SOLUTION: Create application user
sudo rabbitmqctl add_user app_user appPassword456!

# SOLUTION: Grant vhost permissions
sudo rabbitmqctl set_permissions -p /production app_user ".*" ".*" ".*"

# SOLUTION: Verify permissions
sudo rabbitmqctl list_permissions -p /production

echo "[✓] Application user created (app_user/appPassword456!)"
echo "[✓] Vhost permissions granted (/production)"
```

**Step 2: Test Connection with Application User**

```python
import pika

# SOLUTION: Test connection (application user)
try:
    # SOLUTION: Connect as application user
    credentials = pika.PlainCredentials('app_user', 'appPassword456!')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost', port=5672, credentials=credentials)
    )
    channel = connection.channel()
    
    # SOLUTION: Publish message
    channel.queue_declare(queue='messages', durable=True)
    channel.basic_publish(exchange='', routing_key='messages', body='Test Message')
    
    print("[✓] Connection successful (application user - AUTHORIZED)")
    
    connection.close()
    
except pika.exceptions.AuthenticationError:
    print("[!] Authentication failed (wrong credentials)")
    
except pika.exceptions.ProbableAccessDeniedError:
    print("[!] Permission denied (wrong permissions)")
    
except Exception as e:
    print(f"[!] Connection error: {e}")
```

**How to verify:**

```bash
# SOLUTION: Verify user
sudo rabbitmqctl list_users

# SOLUTION: Verify permissions
sudo rabbitmqctl list_permissions -p /production

# SOLUTION: Test connection
python3 consumer_connection_test.py
```

**Expected output:**

```
# SOLUTION: Create Application User
[✓] Application user created (app_user/appPassword456!)
[✓] Vhost permissions granted (/production)

# SOLUTION: Test Connection
[✓] Connection successful (application user - AUTHORIZED)
```

**Comparison:**

| Design | User | Permissions | Connection |
|--------|-----|------------|-------------|
| Before (old) | Guest (disabled) | None | Failed |
| After (new) | App User | Full | Successful |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Use systematic troubleshooting approach (identify, reproduce, analyze, resolve, prevent)  
- Gather symptoms and evidence (logs, metrics, configuration)  
- Reproduce the issue (test hypothesis)  
- Analyze root cause (find underlying problem)  
- Resolve the issue (fix the problem)  
- Verify the fix (test results)  
- Prevent future occurrences (learn from issue)  
- Document issues and resolutions (knowledge base, runbooks)  
- Share lessons learned (team training, post-mortems)  

**❌ Don't:**
- Not gathering symptoms (blind troubleshooting)  
- Not reproducing the issue (guessing without testing)  
- Not analyzing root cause (fixing symptoms only)  
- Not verifying the fix (unresolved issues)  
- Not documenting the issue (lessons lost)  
- Not preventing future occurrences (recurring issues)  
- Not sharing lessons learned (team doesn't learn)  

### Troubleshooting Guidelines

```
Problem Identification:
├─ Gather symptoms (error messages, user reports)
├─ Collect evidence (logs, metrics, configuration)
├─ Identify scope (which component, which queue)
└─ Problem identification complete (clear problem statement)

Reproduce Issue:
├─ Can I reproduce the issue? (consistent symptoms)
├─ What triggers the issue? (specific action, condition)
├─ Is it intermittent? (sometimes happens, sometimes not)
└─ Reproduction complete (consistent test)

Root Cause Analysis:
├─ What's causing the issue? (not just symptoms)
├─ What's the underlying problem? (configuration, code, network)
├─ What dependencies are involved? (other components, external services)
└─ Root cause analysis complete (clear cause)

Resolution:
├─ What's the fix? (configuration change, code fix, restart)
├─ How do I implement the fix? (step-by-step)
├─ How do I verify the fix? (test results)
└─ Resolution complete (fix implemented)

Prevention:
├─ What caused the issue? (root cause analysis)
├─ How can I prevent it? (configuration, monitoring, documentation)
├─ What monitoring do I need? (alerts, health checks)
└─ Prevention complete (monitoring, documentation)
```

### Production Considerations

**Automated Troubleshooting:**

```python
# SOLUTION: Automated troubleshooting script
import requests

# Get RabbitMQ status
status = requests.get('http://rabbitmq-server.example.com:15672/api/overview').json()

# Check if RabbitMQ is running
if not status.get('running', False):
    print("[!] RabbitMQ not running - restarting")
    # SOLUTION: Restart RabbitMQ
    os.system('sudo systemctl restart rabbitmq-server')

print("[✓] Automated troubleshooting complete (RabbitMQ status checked)")
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: How do you troubleshoot RabbitMQ connection issues?**

A: Check RabbitMQ status (rabbitmqctl status). Check network connectivity (telnet, ping). Check firewall rules (open port 5672). Check logs (connection refused, authentication failed). Check user permissions (rabbitmqctl list_permissions).

**Q2: How do you troubleshoot message loss in RabbitMQ?**

A: Check queue depth (rabbitmqctl list_queues). Check bindings (rabbitmqctl list_bindings). Check consumer connections (rabbitmqctl list_connections). Check message acknowledgments (producer confirms, consumer ACK). Check message routing (exchange type, routing key).

**Q3: How do you troubleshoot RabbitMQ memory issues?**

A: Check RabbitMQ memory usage (rabbitmqctl status). Check vm_memory_high_watermark (rabbitmq.conf). Check queue depth (rabbitmqctl list_queues). Check message persistence (durable queues). Configure lazy queues (on-demand loading). Configure memory watermarks (disk flush threshold).

**Q4: How do you troubleshoot RabbitMQ cluster issues?**

A: Check cluster status (rabbitmqctl cluster_status). Check ERLANG cookie (cluster authentication). Check network connectivity (port 25672). Check firewall rules (open ERLANG port). Check DNS resolution (hostname). Check node logs (cluster partition).

**Q5: What's your troubleshooting methodology?**

A: Use systematic approach (identify, reproduce, analyze, resolve, prevent). Gather symptoms and evidence (logs, metrics). Reproduce the issue (test hypothesis). Analyze root cause (find underlying problem). Resolve the issue (fix the problem). Verify the fix (test results). Prevent future occurrences (learn from issue).

### Production Pitfalls

**Pitfall 1: Not gathering symptoms**
- Problem: Blind troubleshooting (no evidence)
- Detection: Wrong diagnosis (guessing)
- Solution: Always gather symptoms and evidence (logs, metrics)

**Pitfall 2: Not reproducing the issue**
- Problem: Guessing without testing (wrong fix)
- Detection: Unresolved issues (wasted time)
- Solution: Always reproduce the issue (test hypothesis)

**Pitfall 3: Not analyzing root cause**
- Problem: Fixing symptoms only (recurring issues)
- Detection: Issue returns (not resolved)
- Solution: Always analyze root cause (find underlying problem)

**Pitfall 4: Not verifying the fix**
- Problem: Unresolved issues (wasted time)
- Detection: Issue still exists (not fixed)
- Solution: Always verify the fix (test results)

**Pitfall 5: Not documenting the issue**
- Problem: Lessons lost (team doesn't learn)
- Detection: Issue recurs (recurring problem)
- Solution: Always document the issue (knowledge base, runbooks)

### Advanced Troubleshooting Concepts

**Automated Troubleshooting Script:**

```python
# Automated troubleshooting script
import subprocess
import requests
import json

def troubleshoot_rabbitmq():
    # SOLUTION: Check RabbitMQ status
    status = subprocess.run(['sudo', 'rabbitmqctl', 'status'], capture_output=True)
    print(f"[*] RabbitMQ status: {status.returncode}")
    
    # SOLUTION: Check connections
    connections = subprocess.run(['sudo', 'rabbitmqctl', 'list_connections'], capture_output=True)
    print(f"[*] Connections: {connections.stdout}")
    
    # SOLUTION: Check queues
    queues = subprocess.run(['sudo', 'rabbitmqctl', 'list_queues'], capture_output=True)
    print(f"[*] Queues: {queues.stdout}")
    
    # SOLUTION: Check logs
    logs = subprocess.run(['sudo', 'journalctl', '-u', 'rabbitmq-server', '-n', '100'], capture_output=True)
    print(f"[*] Logs: {logs.stdout}")
    
    # SOLUTION: Check API
    api = requests.get('http://localhost:15672/api/overview').json()
    print(f"[*] API Status: {api.get('rabbitmq_version', 'unknown')}")
    
    # SOLUTION: Automated diagnosis
    if "ECONNREFUSED" in logs.stdout:
        print("[!] RabbitMQ not running - restarting")
        subprocess.run(['sudo', 'systemctl', 'restart', 'rabbitmq-server'])
        print("[✓] RabbitMQ restarted")
    
    if "AMQP access refused" in logs.stdout:
        print("[!] Authentication/Permission issue - checking user permissions")
        subprocess.run(['sudo', 'rabbitmqctl', 'list_permissions'])
        print("[!] Check user and vhost permissions")

if __name__ == '__main__':
    troubleshoot_rabbitmq()
```

---

## 📚 Summary

Troubleshooting ensures RabbitMQ issues are resolved systematically. Problem identification gathers symptoms and evidence. Root cause analysis finds underlying problems. Resolution fixes the issue. Prevention learns from issues. Documentation captures lessons learned.

**Key takeaways:**
- Use systematic troubleshooting approach (identify, reproduce, analyze, resolve, prevent)
- Gather symptoms and evidence (logs, metrics, configuration)
- Reproduce the issue (test hypothesis)
- Analyze root cause (find underlying problem)
- Resolve the issue (fix the problem)
- Verify the fix (test results)
- Prevent future occurrences (learn from issue)
- Document issues and resolutions (knowledge base, runbooks)
- Share lessons learned (team training, post-mortems)

**Next steps:**
- Practice troubleshooting in your environments
- Learn about performance issues and debugging (next lesson)
- Learn about security issues and remediation (next lesson)
- Complete all lessons in Module 06

---

**Module 06 - Troubleshooting and Case Studies**  
**Lesson 01 - Complete**