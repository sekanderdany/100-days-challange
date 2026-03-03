# 05-03: Security Best Practices

## 🛡 What Is Security Best Practices

**Security Best Practices** is the process of hardening RabbitMQ configuration to protect against unauthorized access, data breaches, and compliance violations. This includes SSL/TLS encryption, authentication, authorization, firewall rules, audit logging, and compliance (GDPR, PCI-DSS, HIPAA).

Think of security best practices like securing a bank vault:

- **SSL/TLS Encryption** = Secure transport (armored truck)
- **Authentication** = Identity verification (security guard)
- **Authorization** = Access control (vault access)
- **Firewall Rules** = Perimeter defense (security walls)
- **Audit Logging** = Security cameras (surveillance)
- **Compliance** = Regulatory adherence (audit requirements)

**Where security fits in RabbitMQ architecture:**

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│  Developer   │        │  Security     │        │  Auditor      │        │  Compliance    │
└──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
       │                    │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼                    ▼                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    RabbitMQ Security Hardening                                              │
│                    (SSL/TLS, Authentication, Authorization, Firewall)                     │
│                                                                                   │
│   ┌────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │              │              │              │               │   │   │   │
│   │    Encryption   │     Auth        │     Authorizat   │   │   │   │
│   │    (SSL/TLS)   │     (Password)    │     (Perms)       │   │   │   │
│   │              │              │              │               │   │   │   │
│   │              │              │              │               │   │   │   │
│   └──────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                                                   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
       │                    │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼                    ▼                    ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│  RabbitMQ    ││  RabbitMQ    ││  RabbitMQ    ││  RabbitMQ    ││  RabbitMQ    ││  RabbitMQ    ││  RabbitMQ    │
│  (Unsecure)  ││  (Encrypted)  ││  (Authed)     ││  (Authorized) ││  (Firewalled)││  (Audited)   ││  (Compliant) │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘
   (Unsecure)     (Encrypted)   (Authed)     (Authorized)   (Firewalled)   (Audited)   (Compliant)
```

**Key concepts:**
- **SSL/TLS Encryption:** Encrypting data in transit (secure transport)
- **Authentication:** Verifying identity (username/password, certificates)
- **Authorization:** Granting permissions (virtual hosts, queues, exchanges)
- **Firewall Rules:** Restricting network access (open only required ports)
- **Audit Logging:** Tracking security events (access logs, connection logs)
- **Compliance:** Regulatory adherence (GDPR, PCI-DSS, HIPAA)
- **Least Privilege:** Minimum required permissions (principle of least privilege)
- **Default Vhost:** Disabling default vhost (`/`)
- **Guest User:** Disabling guest user (default user)

---

## 2️⃣ Problems Solved by Security Best Practices

### The "Security Breach" Problem

Without security hardening:

- Unauthorized access (weak authentication)
- Data interception (no encryption)
- Privilege escalation (excessive permissions)
- Compliance violations (GDPR, PCI-DSS, HIPAA)

**Real-world security scenario:**

A production system had:

```
Attacker → RabbitMQ (Unsecured)
          │
          ├─ Attacker connects (no authentication)
          ├─ Attacker publishes malicious message (unauthorized)
          ├─ Attacker consumes sensitive data (unauthorized)
          ├─ Data intercepted (no SSL/TLS encryption)
          ├─ Attacker modifies queue (excessive permissions)
          ├─ Audit logs missing (no surveillance)
          └─ Security breach (data theft, compliance violation)

WITHOUT SECURITY HARDENING:
├─ Unauthorized access (weak authentication)
├─ Data interception (no encryption)
├─ Privilege escalation (excessive permissions)
├─ No audit logging (no surveillance)
├─ No compliance (GDPR, PCI-DSS, HIPAA violations)
└─ **Impact:** Security breach, data theft, compliance violation, fines, legal action

PROBLEMS:
├─ Weak authentication (default credentials)
├─ No SSL/TLS encryption (data interception)
├─ Excessive permissions (privilege escalation)
├─ Open ports (network exposure)
├─ No firewall rules (unrestricted access)
├─ No audit logging (no surveillance)
├─ Default vhost enabled (unauthorized access)
├─ Guest user enabled (unauthorized access)
└─ **Impact:** Security breach, data theft, compliance violation, fines, legal action

After implementing security best practices:
- SSL/TLS encryption (secure transport)
- Strong authentication (complex passwords, certificates)
- Authorization (least privilege)
- Firewall rules (restricted access)
- Audit logging (surveillance)
- Compliance (GDPR, PCI-DSS, HIPAA)
- **Result:** Secure system, authorized access, encrypted data, audit trails, compliance met

### The "Compliance Violation" Problem

Without compliance:

- GDPR violations (data protection)
- PCI-DSS violations (financial data security)
- HIPAA violations (healthcare data security)
- Legal liability (fines, lawsuits)
- Reputation damage (data breach)

**Example:**

```
Compliance Auditor → RabbitMQ (Non-Compliant)
          │
          ├─ RabbitMQ stores PII without encryption (GDPR violation)
          ├─ RabbitMQ stores financial data without audit (PCI-DSS violation)
          ├─ RabbitMQ stores healthcare data without protection (HIPAA violation)
          ├─ Audit logs missing (compliance violation)
          └─ Legal liability (fines, lawsuits)

WITHOUT COMPLIANCE:
├─ GDPR violations (data protection)
├─ PCI-DSS violations (financial data security)
├─ HIPAA violations (healthcare data security)
├─ No audit logging (compliance violation)
├─ No data encryption (compliance violation)
└─ **Impact:** Fines, lawsuits, legal action, reputation damage

After implementing compliance:
- Data encryption (at rest and in transit)
- Audit logging (surveillance)
- Data protection policies (GDPR, PCI-DSS, HIPAA)
- Data retention policies (data lifecycle)
- Data access controls (least privilege)
- **Result:** Compliance met, legal liability reduced, reputation protected

```

**Problems:**
- Weak authentication (default credentials)
- No SSL/TLS encryption (data interception)
- Excessive permissions (privilege escalation)
- Open ports (network exposure)
- No firewall rules (unrestricted access)
- No audit logging (no surveillance)
- Default vhost enabled (unauthorized access)
- Guest user enabled (unauthorized access)
- No compliance (GDPR, PCI-DSS, HIPAA violations)
- Legal liability (fines, lawsuits)
- Reputation damage (data breach)
- **Impact:** Security breach, data theft, compliance violation, fines, legal action

---

## 3️⃣ When You Should Use Security Best Practices

### Development vs Production

**Development:**
- Use default authentication (guest user)
- Don't need SSL/TLS (local development)
- Don't need audit logging (simple tests)
- Don't need compliance (development only)

**Staging:**
- Use production authentication (strong credentials)
- Use SSL/TLS encryption (production-like security)
- Use audit logging (security testing)
- Don't use for real production workload

**Production:**
- Absolutely required for production deployment (high security)
- Essential for compliance (GDPR, PCI-DSS, HIPAA)
- Critical for data protection (PII, financial, healthcare)
- Required for audit logging (surveillance)
- Required for legal liability protection (fines, lawsuits)
- Necessary for reputation protection (data breach)
- Required for production systems (99.9%+ uptime SLA)

### Security Best Practices Scenarios

| Scenario | Security Strategy | Example |
|----------|----------------|----------|
| **High security** | SSL/TLS + Strong Auth | Financial transactions, healthcare data |
| **Compliance** | Encryption + Audit Logging | GDPR, PCI-DSS, HIPAA |
| **Least privilege** | Minimal permissions | Shared infrastructure, multi-tenant |
| **Zero trust** | No default vhost + No guest | Production systems, financial data |

### Required vs Optional

**Required when:**
- Production systems (any production environment)
- High security requirements (unauthorized access prevention)
- Compliance requirements (GDPR, PCI-DSS, HIPAA)
- Data protection requirements (PII, financial, healthcare)
- Audit logging requirements (surveillance, compliance)
- Legal liability requirements (fines, lawsuits)
- Production systems (99.9%+ uptime SLA)

**Optional when:**
- Development and testing environments
- Internal services (trusted network)
- Non-compliant systems (data not regulated)
- Low-security requirements (data not sensitive)

### Trade-offs

**Security Best Practices:**
✅ SSL/TLS encryption (secure transport)  
✅ Strong authentication (complex passwords, certificates)  
✅ Authorization (least privilege)  
✅ Firewall rules (restricted access)  
✅ Audit logging (surveillance)  
✅ Compliance (GDPR, PCI-DSS, HIPAA)  
✅ Zero trust (no default vhost, no guest)  
✅ High security (unauthorized access prevention)  
✅ Production-ready (enterprise-grade)  
✅ Legal liability protection (fines, lawsuits)  
✅ Reputation protection (data breach)  
✅ Data protection (PII, financial, healthcare)  
❌ More complex configuration (SSL/TLS, auth, firewall)  
❌ Higher cost (certificates, monitoring)  
❌ More management (audit logs, compliance)  
❌ User experience friction (strong authentication)  
❌ Performance overhead (SSL/TLS, authentication)  

**No Security Best Practices:**
✅ Simpler configuration (default settings)  
✅ Lower cost (no certificates, no monitoring)  
✅ Easier to manage (no audit logs)  
✅ Faster deployment (no security validation)  
✅ Lower performance overhead (no SSL/TLS, no auth)  
❌ Unauthorized access (weak authentication)  
❌ Data interception (no encryption)  
❌ Privilege escalation (excessive permissions)  
❌ Compliance violations (GDPR, PCI-DSS, HIPAA)  
❌ Legal liability (fines, lawsuits)  
❌ Reputation damage (data breach)  
❌ Data breach (theft, interception)  

---

## 4️⃣ How Security Best Practices Work

### Security Hardening Configuration Process

**Hardening RabbitMQ for production security:**

```
1. Enable SSL/TLS Encryption
   │
   ├─ Generate SSL/TLS certificates (production encryption)
   ├─ Configure RabbitMQ for SSL/TLS (listeners.ssl)
   ├─ Configure SSL/TLS options (verify, fail)
   └─ SSL/TLS encryption complete (secure transport)
   │
2. Configure Strong Authentication
   │
   ├─ Disable guest user (remove default user)
   ├─ Disable default vhost (remove /)
   ├─ Create strong admin user (complex password)
   ├─ Create application users (least privilege)
   └─ Authentication complete (strong credentials)
   │
3. Configure Authorization
   │
   ├─ Create virtual hosts (isolation)
   ├─ Grant vhost permissions (user access)
   ├─ Grant queue permissions (access control)
   ├─ Grant exchange permissions (access control)
   └─ Authorization complete (least privilege)
   │
4. Configure Firewall Rules
   │
   ├─ Configure rabbitmq port (5672/tcp)
   ├─ Configure management port (15672/tcp)
   ├─ Configure ERLANG port (25672/tcp)
   ├─ Block all other ports (firewall default)
   └─ Firewall complete (network perimeter)
   │
5. Configure Audit Logging
   │
   ├─ Enable connection logs (access tracking)
   ├─ Enable channel logs (security events)
   ├─ Enable authentication logs (login tracking)
   ├─ Configure log retention (policy-based)
   └─ Audit logging complete (surveillance)
   │
6. Configure Compliance
   │
   ├─ Encrypt data at rest (disk encryption)
   ├─ Encrypt data in transit (SSL/TLS)
   ├─ Configure data retention (GDPR, PCI-DSS)
   ├─ Configure data access controls (least privilege)
   └─ Compliance complete (legal met)
   │
7. Security Verification
   │
   ├─ Verify SSL/TLS (certificate validation)
   ├─ Verify authentication (user access)
   ├─ Verify authorization (least privilege)
   ├─ Verify firewall rules (port scanning)
   ├─ Verify audit logging (log review)
   └─ Security verification complete (production ready)
```

### Security Hardening Mechanisms

**How SSL/TLS encryption works:**

```
SSL/TLS Encryption (Secure Transport):
├─ Generate SSL/TLS certificates (production encryption)
├─ Configure RabbitMQ for SSL/TLS (listeners.ssl)
├─ Configure SSL/TLS options (verify, fail)
└─ SSL/TLS encryption complete (secure transport)
```

**How strong authentication works:**

```
Strong Authentication (Complex Credentials):
├─ Disable guest user (remove default user)
├─ Disable default vhost (remove /)
├─ Create strong admin user (complex password)
├─ Create application users (least privilege)
└─ Authentication complete (strong credentials)
```

**How authorization works:**

```
Authorization (Least Privilege):
├─ Create virtual hosts (isolation)
├─ Grant vhost permissions (user access)
├─ Grant queue permissions (access control)
├─ Grant exchange permissions (access control)
└─ Authorization complete (least privilege)
```

---

## 5️⃣ Installation / Setup

**RabbitMQ Security Best Practices are a built-in RabbitMQ feature.** No installation required - just configure SSL/TLS, authentication, authorization, firewall rules, and audit logging.

### Prerequisites

- RabbitMQ server running (or RabbitMQ Docker image available)
- Understanding of security requirements (SSL/TLS, authentication, authorization)
- Understanding of compliance requirements (GDPR, PCI-DSS, HIPAA)
- Understanding of audit logging requirements (surveillance, compliance)
- Access to RabbitMQ Management UI (port 15672)
- Understanding of configuration management (rabbitmq.conf, environment variables)

### Generating SSL/TLS Certificates

**Using OpenSSL:**

```bash
# Generate SSL/TLS certificates
sudo openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/rabbitmq/rabbitmq-server.key \
  -out /etc/rabbitmq/rabbitmq-server.crt \
  -subj "/CN=rabbitmq-server.example.com/O=RabbitMQ Organization/C=US"
```

### Configuring SSL/TLS

**Using rabbitmq.conf:**

```bash
# Configure RabbitMQ for SSL/TLS
cat > /etc/rabbitmq/rabbitmq.conf << EOF
# Security Configuration

# SSL/TLS
listeners.ssl.default = 5671
ssl_options.certfile = /etc/rabbitmq/rabbitmq-server.crt
ssl_options.keyfile = /etc/rabbitmq/rabbitmq-server.key
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = true

# Disable default security
auth_mechanisms.plain.enabled = false
guest_access.enabled = false
default_vhost = ""
log.file.level = info
EOF

# Restart RabbitMQ
sudo systemctl restart rabbitmq-server

# Verify SSL/TLS
curl -k --cert /etc/rabbitmq/rabbitmq-server.crt \
  https://rabbitmq-server.example.com:15671/api/overview
```

### Configuring Strong Authentication

**Using rabbitmqctl:**

```bash
# Disable guest user (remove default user)
sudo rabbitmqctl delete_user guest

# Disable default vhost (remove /)
sudo rabbitmqctl delete_vhost /

# Create strong admin user
sudo rabbitmqctl add_user admin complexPassword123!
sudo rabbitmqctl set_user_tags admin administrator

# Create application user (least privilege)
sudo rabbitmqctl add_user app_user appPassword456!
sudo rabbitmqctl set_user_tags app_user
sudo rabbitmqctl set_permissions -p /production app_user ".*" ".*" ".*"

# Verify authentication
sudo rabbitmqctl list_users
sudo rabbitmqctl list_permissions -p /production
```

### Version Notes

- **RabbitMQ 3.12+:** All security best practices fully supported
- **SSL/TLS Encryption:** Secure transport (listeners.ssl)
- **Strong Authentication:** Complex credentials, guest user disabled
- **Authorization:** Least privilege principle, vhost permissions
- **Firewall Rules:** Restricted access (open only required ports)
- **Audit Logging:** Connection logs, channel logs, authentication logs
- **Compliance:** Data encryption, audit logging, data retention

---

## 6️⃣ Where Security Best Practices Should Be Applied (With Example)

### Security Hardening Configuration

**Scenario:** Production RabbitMQ deployment with high security

**Security Configuration (security_config.json):**

```json
{
  "rabbitmq": {
    "ssl": {
      "enabled": true,
      "certificate": "/etc/rabbitmq/rabbitmq-server.crt",
      "key": "/etc/rabbitmq/rabbitmq-server.key",
      "verify": "verify_peer",
      "fail_if_no_peer_cert": true
    },
    "authentication": {
      "guest_user_disabled": true,
      "default_vhost_disabled": true,
      "admin_user": {
        "name": "admin",
        "password": "complexPassword123!",
        "tags": ["administrator"]
      },
      "application_users": [
        {
          "name": "app_user",
          "password": "appPassword456!",
          "tags": [],
          "vhost": "/production",
          "permissions": {
            "configure": ".*",
            "write": ".*",
            "read": ".*"
          }
        }
      ]
    },
    "authorization": {
      "vhosts": {
        "/production": {
          "users": ["admin", "app_user"],
          "permissions": ".*"
        }
      }
    },
    "firewall": {
      "allowed_ports": [5671, 5672, 15671, 15672, 25672],
      "blocked_ips": ["0.0.0.0/0"]
    },
    "audit_logging": {
      "connection_logs": {
        "enabled": true,
        "retention_days": 90
      },
      "channel_logs": {
        "enabled": true,
        "retention_days": 90
      },
      "authentication_logs": {
        "enabled": true,
        "retention_days": 365
      }
    },
    "compliance": {
      "gdpr": {
        "enabled": true,
        "data_encryption": true,
        "data_retention_days": 365
      },
      "pci_dss": {
        "enabled": true,
        "audit_frequency": "daily",
        "log_retention_days": 365
      },
      "hipaa": {
        "enabled": true,
        "data_access_controls": true,
        "audit_frequency": "daily"
      }
    }
  }
}
```

### SSL/TLS Configuration

**Configuring RabbitMQ for SSL/TLS:**

```bash
# Configure RabbitMQ for SSL/TLS
cat > /etc/rabbitmq/rabbitmq.conf << EOF
# Security Configuration

# SSL/TLS
listeners.ssl.default = 5671
ssl_options.certfile = /etc/rabbitmq/rabbitmq-server.crt
ssl_options.keyfile = /etc/rabbitmq/rabbitmq-server.key
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = true

# Disable default security
auth_mechanisms.plain.enabled = false
guest_access.enabled = false
default_vhost = ""
log.file.level = info
EOF

sudo systemctl restart rabbitmq-server

# Verify SSL/TLS
curl -k --cert /etc/rabbitmq/rabbitmq-server.crt \
  https://rabbitmq-server.example.com:15671/api/overview
```

### Best Practices

**SSL/TLS Encryption:**
✅ Use SSL/TLS certificates (production encryption)  
✅ Verify certificates (validity checks)  
✅ Configure SSL/TLS options (verify, fail)  
✅ Monitor SSL/TLS expiration (certificate rotation)  
✅ Use strong encryption (RSA 2048+)  

**Strong Authentication:**
✅ Disable guest user (remove default user)  
✅ Disable default vhost (remove /)  
✅ Use strong passwords (complex, long)  
✅ Use certificate-based authentication (mutual TLS)  
✅ Rotate credentials regularly (password changes)  

**Authorization:**
✅ Use least privilege principle (minimum permissions)  
✅ Create virtual hosts (isolation)  
✅ Grant minimum permissions (access control)  
✅ Separate admin and application users (role separation)  
✅ Review permissions regularly (audit)  

**Firewall Rules:**
✅ Open only required ports (5672, 15672, 25672)  
✅ Block all other ports (firewall default)  
✅ Use security groups (port-based access)  
✅ Monitor firewall logs (intrusion detection)  
✅ Scan for open ports (vulnerability assessment)  

**Audit Logging:**
✅ Enable connection logs (access tracking)  
✅ Enable channel logs (security events)  
✅ Enable authentication logs (login tracking)  
✅ Configure log retention (policy-based)  
✅ Monitor audit logs (security surveillance)  
✅ Review audit logs regularly (compliance)  

**Compliance:**
✅ Encrypt data at rest (disk encryption)  
✅ Encrypt data in transit (SSL/TLS)  
✅ Configure data retention (GDPR, PCI-DSS, HIPAA)  
✅ Configure data access controls (least privilege)  
✅ Monitor compliance (audit, legal review)  
✅ Document security policies (compliance evidence)  

### Common Mistakes

❌ Using guest user → Unauthorized access (default credentials)  
❌ Using default vhost → Unauthorized access (unprotected)  
❌ Using weak passwords → Security breach (credential cracking)  
❌ Not using SSL/TLS → Data interception (no encryption)  
❌ Excessive permissions → Privilege escalation (data breach)  
❌ Open firewall ports → Network exposure (unrestricted access)  
❌ Not enabling audit logs → No surveillance (compliance violation)  
❌ Not implementing compliance → Legal liability (fines, lawsuits)  
❌ Not rotating credentials → Security breach (stolen passwords)  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Security Breach (The "Data Theft" Problem)**

You're securing RabbitMQ for production:

- System must be highly secure (unauthorized access prevention)
- System must be compliant (GDPR, PCI-DSS, HIPAA)
- Audit logging required (surveillance)
- Legal liability risk (fines, lawsuits)

Current implementation:
- Guest user enabled (default credentials)
- Default vhost enabled (unprotected access)
- Weak passwords (credential cracking)
- No SSL/TLS encryption (data interception)
- Excessive permissions (privilege escalation)
- No firewall rules (network exposure)
- No audit logging (no surveillance)
- **Impact:** Security breach, data theft, compliance violation, fines, legal action

### 🧪 Lab Tasks

**Step 1: Configure Insecure RabbitMQ**

```bash
# Configure RabbitMQ (INSECURE)
cat > /etc/rabbitmq/rabbitmq.conf << EOF
# PROBLEM: No SSL/TLS, guest user enabled, default vhost enabled
listeners.tcp.default = 5672
management.tcp.port = 15672
vm_memory_high_watermark = 4GB
log.file.level = info
EOF

sudo systemctl restart rabbitmq-server

# PROBLEM: Guest user enabled, default vhost enabled, weak authentication
echo "[!] RabbitMQ configured (INSECURE - guest user, default vhost, weak auth)"
```

**Step 2: Test Insecure Access**

```python
import pika

# Test insecure access (guest user)
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', port=5672)
)
channel = connection.channel()

# PROBLEM: Guest user access (unauthorized)
channel.queue_declare(queue='messages', durable=True)
channel.basic_publish(exchange='', routing_key='messages', body='Malicious Message')
print("[!] Published message (guest user - UNAUTHORIZED)")

connection.close()

# PROBLEM: Access to default vhost (unprotected)
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', port=5672)
)
channel = connection.channel()

# PROBLEM: Excessive permissions (privilege escalation)
channel.queue_declare(queue='admin_config', durable=True)  # PROBLEM: Access to admin queue
channel.basic_publish(exchange='', routing_key='admin_config', body='Malicious Config')
print("[!] Published message (excessive permissions - PRIVILEGE ESCALATION)")

connection.close()
```

**Expected observation:**
- RabbitMQ configured (insecure)
- Guest user access (unauthorized)
- Default vhost access (unprotected)
- Excessive permissions (privilege escalation)
- No SSL/TLS (data interception)
- No firewall (network exposure)
- No audit logs (no surveillance)
- **Impact:** Security breach, data theft, compliance violation, fines, legal action

### ✅ Solution & Explanation

**Solution: Implement Security Best Practices (SSL/TLS + Strong Auth + Authorization + Firewall + Audit)**

**Step 1: Generate SSL/TLS Certificates**

```bash
# SOLUTION: Generate SSL/TLS certificates
sudo openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/rabbitmq/rabbitmq-server.key \
  -out /etc/rabbitmq/rabbitmq-server.crt \
  -subj "/CN=rabbitmq-server.example.com/O=RabbitMQ Organization/C=US"

echo "[✓] SSL/TLS certificates generated (production encryption)"
```

**Step 2: Configure SSL/TLS**

```bash
# SOLUTION: Configure RabbitMQ for SSL/TLS
cat > /etc/rabbitmq/rabbitmq.conf << EOF
# SOLUTION: Security Configuration

# SSL/TLS
listeners.ssl.default = 5671
ssl_options.certfile = /etc/rabbitmq/rabbitmq-server.crt
ssl_options.keyfile = /etc/rabbitmq/rabbitmq-server.key
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = true

# Disable default security
auth_mechanisms.plain.enabled = false
guest_access.enabled = false
default_vhost = ""
log.file.level = info
EOF

sudo systemctl restart rabbitmq-server

echo "[✓] RabbitMQ configured for SSL/TLS (secure transport)"
```

**Step 3: Configure Strong Authentication**

```bash
# SOLUTION: Disable guest user (remove default user)
sudo rabbitmqctl delete_user guest
echo "[✓] Guest user disabled (security improvement)"

# SOLUTION: Disable default vhost (remove /)
sudo rabbitmqctl delete_vhost /
echo "[✓] Default vhost disabled (security improvement)"

# SOLUTION: Create strong admin user
sudo rabbitmqctl add_user admin complexPassword123!
sudo rabbitmqctl set_user_tags admin administrator
echo "[✓] Strong admin user created (complex password)"

# SOLUTION: Create application user (least privilege)
sudo rabbitmqctl add_user app_user appPassword456!
sudo rabbitmqctl set_user_tags app_user
sudo rabbitmqctl set_permissions -p /production app_user ".*" ".*" ".*"
echo "[✓] Application user created (least privilege)"

# SOLUTION: Verify authentication
sudo rabbitmqctl list_users
sudo rabbitmqctl list_permissions -p /production
echo "[✓] Authentication configured (strong credentials, guest disabled)"
```

**How to verify:**

```python
import pika

# SOLUTION: Test secure access (strong authentication)
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', port=5672)
)
channel = connection.channel()

# SOLUTION: Test strong authentication (admin user)
credentials = pika.PlainCredentials('admin', 'complexPassword123!')
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', port=5672, credentials=credentials)

channel.queue_declare(queue='messages', durable=True)
channel.basic_publish(exchange='', routing_key='messages', body='Secure Message')
print("[✓] Published message (admin - AUTHORIZED)")

connection.close()

# SOLUTION: Test application user access (least privilege)
credentials = pika.PlainCredentials('app_user', 'appPassword456!')
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', port=5672, credentials=credentials)

channel.queue_declare(queue='messages', durable=True)
channel.basic_publish(exchange='', routing_key='messages', body='Application Message')
print("[✓] Published message (application user - LEAST PRIVILEGE)")

connection.close()
```

**Expected output:**

```
# SOLUTION: SSL/TLS Certificates
[✓] SSL/TLS certificates generated (production encryption)

# SOLUTION: SSL/TLS Configuration
[✓] RabbitMQ configured for SSL/TLS (secure transport)

# SOLUTION: Strong Authentication
[✓] Guest user disabled (security improvement)
[✓] Default vhost disabled (security improvement)
[✓] Strong admin user created (complex password)
[✓] Application user created (least privilege)
[✓] Authentication configured (strong credentials, guest disabled)

# SOLUTION: Verification
[✓] Published message (admin - AUTHORIZED)
[✓] Published message (application user - LEAST PRIVILEGE)
```

**Comparison:**

| Design | SSL/TLS | Strong Auth | Authorization | Firewall | Audit Logs |
|--------|---------|-----------|------------|----------|-----------|
| Insecure (old) | No | No | No | No | No |
| Secure (new) | Yes | Yes | Yes | Yes | Yes |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Use SSL/TLS encryption (secure transport)  
- Use strong authentication (complex passwords, certificates)  
- Use least privilege principle (minimum permissions)  
- Configure firewall rules (restricted access)  
- Enable audit logging (surveillance)  
- Implement compliance (GDPR, PCI-DSS, HIPAA)  
- Rotate credentials regularly (password changes)  
- Monitor security events (intrusion detection)  
- Document security policies (compliance evidence)  

**❌ Don't:**
- Using guest user → Unauthorized access (default credentials)  
- Using default vhost → Unauthorized access (unprotected)  
- Using weak passwords → Security breach (credential cracking)  
- Not using SSL/TLS → Data interception (no encryption)  
- Excessive permissions → Privilege escalation (data breach)  
- Open firewall ports → Network exposure (unrestricted access)  
- Not enabling audit logs → No surveillance (compliance violation)  
- Not implementing compliance → Legal liability (fines, lawsuits)  

### Security Hardening Guidelines

```
SSL/TLS Encryption:
├─ Use SSL/TLS certificates (production encryption)
├─ Verify certificates (validity checks)
├─ Configure SSL/TLS options (verify, fail)
└─ Monitor SSL/TLS expiration (certificate rotation)

Strong Authentication:
├─ Disable guest user (remove default user)
├─ Disable default vhost (remove /)
├─ Use strong passwords (complex, long)
├─ Use certificate-based authentication (mutual TLS)
└─ Rotate credentials regularly (password changes)

Authorization:
├─ Use least privilege principle (minimum permissions)
├─ Create virtual hosts (isolation)
├─ Grant minimum permissions (access control)
├─ Separate admin and application users (role separation)
└─ Review permissions regularly (audit)

Firewall Rules:
├─ Open only required ports (5672, 15672, 25672)
├─ Block all other ports (firewall default)
├─ Use security groups (port-based access)
└─ Monitor firewall logs (intrusion detection)

Audit Logging:
├─ Enable connection logs (access tracking)
├─ Enable channel logs (security events)
├─ Enable authentication logs (login tracking)
└─ Monitor audit logs (security surveillance)

Compliance:
├─ Encrypt data at rest (disk encryption)
├─ Encrypt data in transit (SSL/TLS)
├─ Configure data retention (GDPR, PCI-DSS, HIPAA)
├─ Configure data access controls (least privilege)
└─ Monitor compliance (audit, legal review)
```

---

## 📚 Summary

Security Best Practices ensures RabbitMQ is hardened against unauthorized access. SSL/TLS encryption secures data in transit. Strong authentication verifies identity. Authorization controls access. Firewall rules restrict network access. Audit logging provides surveillance. Compliance meets regulatory requirements.

**Key takeaways:**
- Use SSL/TLS encryption (secure transport)
- Use strong authentication (complex passwords, certificates)
- Use least privilege principle (minimum permissions)
- Configure firewall rules (restricted access)
- Enable audit logging (surveillance)
- Implement compliance (GDPR, PCI-DSS, HIPAA)
- Rotate credentials regularly (password changes)
- Monitor security events (intrusion detection)
- Document security policies (compliance evidence)

**Next steps:**
- Practice with security best practices in your environments
- Learn about backup and disaster recovery (next lesson)
- Learn about monitoring and alerting best practices (next lesson)
- Complete all lessons in Module 05

---

**Module 05 - Best Practices & Production Deployment**  
**Lesson 03 - Complete**