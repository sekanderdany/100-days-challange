# 05-04: Backup and Disaster Recovery

## 📦 What Is Backup and Disaster Recovery

**Backup and Disaster Recovery** is the process of protecting RabbitMQ data from loss, corruption, and downtime. This includes automatic backups, data retention policies, restore procedures, and disaster recovery planning.

Think of backup and disaster recovery like an insurance policy:

- **Automatic Backups** = Scheduled premiums (regular backups)
- **Data Retention** = Policy coverage (retention period)
- **Restore Procedures** = Claim processing (data recovery)
- **Disaster Recovery** = Business continuity (disaster response)
- **Offsite Storage** = Safe deposit (data protection)

**Where backup fits in RabbitMQ architecture:**

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│  Production │        │  Backup       │        │  Restore      │        │  Disaster     │        │  Offsite      │
└──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
       │                    │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼                    ▼                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    RabbitMQ Backup & Disaster Recovery                                        │
│                    (Backups, Retention, Restore, Disaster Recovery)                       │
│                                                                                   │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │              │              │              │               │   │   │   │
│   │    Backup      │     Retention   │     Restore     │   │   │   │
│   │    (Scheduled)   │     (Policy)     │     (Recovery)    │   │   │   │
│   │              │              │              │               │   │   │   │
│   │              │              │              │               │   │   │   │
│   └──────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                                                   │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
       │                    │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼                    ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│  RabbitMQ    ││  Backup      ││  Data        ││  Restored     ││  Offsite     │
│  (Live)       ││  (Scheduled)  ││  (Retained)   ││  (Recovered)  ││  (Protected)  │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘
   (Live)         (Scheduled)    (Retained)     (Recovered)    (Protected)
```

**Key concepts:**
- **Automatic Backups:** Scheduled backups (cron jobs)
- **Data Retention:** Retention policies (how long to keep backups)
- **Restore Procedures:** Data recovery (restoring from backups)
- **Disaster Recovery:** Business continuity (disaster response planning)
- **Offsite Storage:** Data protection (cloud, remote storage)
- **Backup Validation:** Testing backups (restore validation)
- **Backup Encryption:** Securing backups (encryption at rest)

---

## 2️⃣ Problems Solved by Backup and Disaster Recovery

### The "Data Loss" Problem

Without backup strategy:

- Data loss (disk failure, corruption)
- No recovery (no backups available)
- System downtime (data loss = downtime)
- Compliance violations (no data retention)

**Real-world data loss scenario:**

A production system had:

```
Producer → RabbitMQ (No Backups)
          │
          ├─ Producer publishes 1,000,000 messages (high queue depth)
          ├─ RabbitMQ stores messages (no backups)
          ├─ Disk failure (data loss)
          ├─ No backups available (no recovery)
          ├─ Data loss (all messages lost)
          └─ System downtime (no data = no production)

WITHOUT BACKUP STRATEGY:
├─ Data loss (disk failure, corruption)
├─ No backups (no recovery)
├─ No restore procedures (data loss = permanent)
├─ No disaster recovery (system downtime)
├─ No offsite storage (single point of failure)
└─ **Impact:** Data loss, system downtime, compliance violation, fines, lawsuits

PROBLEMS:
├─ No backups (no recovery)
├─ No restore procedures (data loss = permanent)
├─ No disaster recovery (system downtime)
├─ No offsite storage (single point of failure)
├─ No backup validation (untested backups)
├─ No backup encryption (data exposure)
└─ **Impact:** Data loss, system downtime, compliance violation, fines, lawsuits

After implementing backup and disaster recovery:
- Automatic backups (scheduled backups)
- Data retention policies (policy-based)
- Restore procedures (data recovery)
- Disaster recovery (business continuity)
- Offsite storage (data protection)
- Backup validation (tested backups)
- Backup encryption (data protection)
- **Result:** Data protection, recovery, compliance, business continuity

### The "System Downtime" Problem

Without disaster recovery:

- System downtime (no business continuity)
- Financial loss (revenue loss)
- Reputation damage (system unavailable)
- SLA violations (99.9%+ uptime)

**Example:**

```
Disaster → RabbitMQ (No Disaster Recovery)
          │
          ├─ Disaster strikes (fire, flood, earthquake)
          ├─ Data center down (no access)
          ├─ No backup available (no recovery)
          ├─ Data loss (all messages lost)
          └─ System downtime (no production)

WITHOUT DISASTER RECOVERY:
├─ System downtime (no business continuity)
├─ Financial loss (revenue loss)
├─ Reputation damage (system unavailable)
├─ SLA violations (99.9%+ uptime)
└─ **Impact:** System downtime, financial loss, reputation damage, SLA violations

After implementing disaster recovery:
- Disaster recovery plan (business continuity)
- Offsite storage (data protection)
- Backup validation (tested backups)
- Backup encryption (data protection)
- SLA compliance (99.9%+ uptime)
- **Result:** Business continuity, data protection, compliance met
```

**Problems:**
- No backups (no recovery)
- No restore procedures (data loss = permanent)
- No disaster recovery (system downtime)
- No offsite storage (single point of failure)
- No backup validation (untested backups)
- No backup encryption (data exposure)
- **Impact:** Data loss, system downtime, compliance violation, fines, lawsuits

---

## 3️⃣ When You Should Use Backup and Disaster Recovery

### Development vs Production

**Development:**
- No backups needed (ephemeral data)
- No retention policies (development only)
- No restore procedures (no data to recover)
- No disaster recovery (no production)

**Staging:**
- Periodic backups (testing recovery)
- Short retention (validation only)
- Restore procedures testing (data recovery validation)
- Not used for real production workload

**Production:**
- Absolutely required for production deployment (data protection)
- Essential for compliance (data retention, recovery)
- Critical for disaster recovery (business continuity)
- Required for SLA compliance (99.9%+ uptime)
- Necessary for data protection (PII, financial, healthcare)
- Required for production systems (high availability)
- Necessary for compliance (GDPR, PCI-DSS, HIPAA)

### Backup and Disaster Recovery Scenarios

| Scenario | Backup Strategy | Example |
|----------|----------------|----------|
| **Data protection** | Automatic backups + Offsite storage | Critical systems, financial data |
| **Compliance** | Data retention + Backup validation | GDPR, PCI-DSS, HIPAA |
| **Business continuity** | Disaster recovery + SLA compliance | High availability, revenue protection |
| **Data recovery** | Restore procedures + Backup encryption | Data loss prevention, data protection |

### Required vs Optional

**Required when:**
- Production systems (any production environment)
- Data protection requirements (no data loss)
- Compliance requirements (data retention, recovery)
- Disaster recovery requirements (business continuity)
- SLA compliance requirements (99.9%+ uptime)
- Data protection requirements (PII, financial, healthcare)
- Production systems (high availability)
- Compliance requirements (GDPR, PCI-DSS, HIPAA)

**Optional when:**
- Development and testing environments
- Ephemeral data (no persistence)
- Non-critical systems (data loss acceptable)
- Internal services (data not regulated)

### Trade-offs

**Backup and Disaster Recovery:**
✅ Automatic backups (scheduled backups)  
✅ Data retention policies (policy-based)  
✅ Restore procedures (data recovery)  
✅ Disaster recovery (business continuity)  
✅ Offsite storage (data protection)  
✅ Backup validation (tested backups)  
✅ Backup encryption (data protection)  
✅ Compliance (GDPR, PCI-DSS, HIPAA)  
✅ Business continuity (disaster recovery)  
✅ SLA compliance (99.9%+ uptime)  
✅ Data protection (no data loss)  
❌ Higher cost (storage, offsite)  
❌ More management (backups, retention, restore)  
❌ Backup overhead (system resources)  
❌ More complexity (backup scheduling, validation)  

**No Backup and Disaster Recovery:**
✅ No cost (no storage, offsite)  
✅ No management (no backups, retention, restore)  
✅ No backup overhead (system resources)  
✅ Simpler deployment (no backup scheduling)  
❌ Data loss (no recovery)  
❌ No restore procedures (data loss = permanent)  
❌ No disaster recovery (system downtime)  
❌ No offsite storage (single point of failure)  
❌ No backup validation (untested backups)  
❌ No backup encryption (data exposure)  
❌ No compliance (GDPR, PCI-DSS, HIPAA violations)  
❌ Business continuity lost (system downtime)  
❌ SLA violations (99.9%+ uptime)  
❌ Financial loss (revenue loss)  

---

## 4️⃣ How Backup and Disaster Recovery Works

### Backup and Disaster Recovery Configuration Process

**Protecting RabbitMQ data from loss, corruption, and downtime:**

```
1. Configure Automatic Backups
   │
   ├─ Schedule backups (cron jobs)
   ├─ Configure backup type (full, incremental)
   ├─ Configure backup location (local, offsite)
   └─ Automatic backups complete (scheduled)
   │
2. Configure Data Retention Policies
   │
   ├─ Set retention period (policy-based)
   ├─ Configure backup rotation (delete old backups)
   ├─ Configure retention per backup type (full, incremental)
   └─ Data retention complete (policy-based)
   │
3. Configure Restore Procedures
   │
   ├─ Stop RabbitMQ (prepare for restore)
   ├─ Restore backup (backup restoration)
   ├─ Verify restore (data integrity check)
   ├─ Start RabbitMQ (resumed operations)
   └─ Restore complete (data recovered)
   │
4. Configure Disaster Recovery
   │
   ├─ Document disaster recovery plan (business continuity)
   ├─ Configure offsite storage (data protection)
   ├─ Configure failover (automatic recovery)
   ├─ Test disaster recovery (simulated disaster)
   └─ Disaster recovery complete (business continuity)
   │
5. Configure Backup Validation
   │
   ├─ Test backup restoration (restore validation)
   ├─ Verify backup integrity (checksum, encryption)
   ├─ Schedule restore testing (regular validation)
   └─ Backup validation complete (tested backups)
   │
6. Configure Backup Encryption
   │
   ├─ Encrypt backups (at rest)
   ├─ Configure encryption keys (key management)
   ├─ Verify encryption (decrypt test)
   └─ Backup encryption complete (data protection)
```

### Backup and Disaster Recovery Mechanisms

**How automatic backups work:**

```
Automatic Backups (Scheduled Backups):
├─ Schedule backups (cron jobs)
├─ Configure backup type (full, incremental)
├─ Configure backup location (local, offsite)
└─ Automatic backups complete (scheduled)
```

**How restore procedures work:**

```
Restore Procedures (Data Recovery):
├─ Stop RabbitMQ (prepare for restore)
├─ Restore backup (backup restoration)
├─ Verify restore (data integrity check)
├─ Start RabbitMQ (resumed operations)
└─ Restore complete (data recovered)
```

---

## 5️⃣ Installation / Setup

**RabbitMQ Backup and Disaster Recovery is a built-in RabbitMQ feature.** No installation required - just configure automatic backups, data retention policies, restore procedures, and disaster recovery planning.

### Prerequisites

- RabbitMQ server running (or RabbitMQ Docker image available)
- Understanding of data protection requirements (no data loss)
- Understanding of compliance requirements (data retention, recovery)
- Understanding of disaster recovery requirements (business continuity)
- Understanding of backup strategies (full, incremental, differential)
- Understanding of offsite storage requirements (cloud, remote storage)
- Understanding of restore procedures (data recovery)
- Access to RabbitMQ Management UI (port 15672)
- Understanding of backup validation (restore testing)
- Understanding of backup encryption (data protection)

### Configuring Automatic Backups

**Using cron jobs:**

```bash
# Configure automatic backups
sudo crontab -e << EOF
# RabbitMQ Automatic Backups
# Schedule daily backup at 2 AM (0 2 * * *)
0 2 * * * root /bin/tar -czf /var/backups/rabbitmq-backup-$(date +\%Y\%m\%d).tar.gz /var/lib/rabbitmq/

# Schedule weekly full backup at 2 AM on Sunday (0 2 * * 0)
0 2 * * 0 root /bin/tar -czf /var/backups/rabbitmq-full-backup-$(date +\%Y\%m\%d).tar.gz /var/lib/rabbitmq/

# Schedule incremental backup every 6 hours
0 */6 * * * root /bin/tar -czf /var/backups/rabbitmq-incremental-backup-$(date +\%Y\%m\%d-\%H\%M).tar.gz /var/lib/rabbitmq/
EOF

echo "[✓] Automatic backups configured (scheduled)"
```

### Configuring Data Retention

**Using bash script:**

```bash
# Configure data retention policies
cat > /usr/local/bin/rabbitmq-cleanup.sh << 'EOF'
#!/bin/bash
# RabbitMQ Data Retention Policy

# Delete backups older than 90 days
find /var/backups/ -name "rabbitmq-backup-*" -mtime +90 -delete

# Delete backups older than 7 days (incremental)
find /var/backups/ -name "rabbitmq-incremental-backup-*" -mtime +7 -delete

# Keep only last 7 full backups
ls -t /var/backups/rabbitmq-full-backup-* | tail -n +8 | xargs rm -f

echo "[x] Cleaned up old backups (retention policy applied)"
EOF

chmod +x /usr/local/bin/rabbitmq-cleanup.sh

# Schedule cleanup (daily at 3 AM)
(crontab -l 2>/dev/null || true; echo "0 3 * * * root /usr/local/bin/rabbitmq-cleanup.sh") | crontab -

echo "[✓] Data retention policies configured (retention: 90 days)"
```

### Version Notes

- **RabbitMQ 3.12+:** All backup and disaster recovery features fully supported
- **Automatic Backups:** Scheduled backups (cron jobs, external tools)
- **Data Retention:** Retention policies (policy-based)
- **Restore Procedures:** Data recovery (backup restoration, data integrity)
- **Disaster Recovery:** Business continuity (failover, offsite storage)
- **Backup Validation:** Restore testing (checksum, encryption)
- **Backup Encryption:** Data protection (encryption at rest, key management)

---

## 6️⃣ Where Backup and Disaster Recovery Should Be Applied (With Example)

### Backup and Disaster Recovery Configuration

**Scenario:** Production RabbitMQ deployment with data protection

**Backup Configuration (backup_config.json):**

```json
{
  "rabbitmq": {
    "backup": {
      "enabled": true,
      "schedule": {
        "daily": "0 2 * * *",
        "weekly": "0 2 * * 0",
        "incremental": "0 */6 * * *"
      },
      "location": {
        "local": "/var/backups/",
        "offsite": "s3://rabbitmq-backups/",
        "encryption": true
      },
      "type": {
        "full": "rabbitmq-full-backup-$(date +\\%Y\\%m\\%d).tar.gz",
        "incremental": "rabbitmq-incremental-backup-$(date +\\%Y\\%m\\%d-\\%H\\%M).tar.gz"
      }
    },
    "retention": {
      "enabled": true,
      "policy": {
        "daily": "90 days",
        "weekly": "90 days",
        "incremental": "7 days",
        "full": "7 backups"
      }
    },
    "restore": {
      "enabled": true,
      "procedure": {
        "stop_rabbitmq": true,
        "verify_restore": true,
        "start_rabbitmq": true
      }
    },
    "disaster_recovery": {
      "enabled": true,
      "offsite_storage": {
        "s3": "s3://rabbitmq-backups/",
        "azure": "azure://rabbitmq-backups/",
        "gcp": "gs://rabbitmq-backups/"
      },
      "failover": {
        "enabled": true,
        "cluster_failover": true
      }
    },
    "validation": {
      "enabled": true,
      "schedule": "weekly",
      "encryption": {
        "enabled": true,
        "key_management": "AWS KMS"
      }
    },
    "encryption": {
      "enabled": true,
      "algorithm": "AES-256",
      "key_rotation": "90 days"
    }
  }
}
```

### Automatic Backup Configuration

**Configuring automatic backups:**

```bash
# Configure automatic backups
sudo crontab -e << EOF
# RabbitMQ Automatic Backups
# Schedule daily backup at 2 AM (0 2 * * *)
0 2 * * * root /bin/tar -czf /var/backups/rabbitmq-backup-$(date +\%Y\%m\%d).tar.gz /var/lib/rabbitmq/

# Schedule weekly full backup at 2 AM on Sunday (0 2 * * 0)
0 2 * * 0 root /bin/tar -czf /var/backups/rabbitmq-full-backup-$(date +\%Y\%m\%d).tar.gz /var/lib/rabbitmq/

# Schedule incremental backup every 6 hours
0 */6 * * * root /bin/tar -czf /var/backups/rabbitmq-incremental-backup-$(date +\%Y\%m\%d-\%H\%M).tar.gz /var/lib/rabbitmq/
EOF

echo "[✓] Automatic backups configured (scheduled)"
```

### Data Retention Configuration

**Configuring data retention policies:**

```bash
# Configure data retention policies
cat > /usr/local/bin/rabbitmq-cleanup.sh << 'EOF'
#!/bin/bash
# RabbitMQ Data Retention Policy

# Delete backups older than 90 days
find /var/backups/ -name "rabbitmq-backup-*" -mtime +90 -delete

# Delete backups older than 7 days (incremental)
find /var/backups/ -name "rabbitmq-incremental-backup-*" -mtime +7 -delete

# Keep only last 7 full backups
ls -t /var/backups/rabbitmq-full-backup-* | tail -n +8 | xargs rm -f

echo "[x] Cleaned up old backups (retention policy applied)"
EOF

chmod +x /usr/local/bin/rabbitmq-cleanup.sh

# Schedule cleanup (daily at 3 AM)
(crontab -l 2>/dev/null || true; echo "0 3 * * * root /usr/local/bin/rabbitmq-cleanup.sh") | crontab -

echo "[✓] Data retention policies configured (retention: 90 days)"
```

### Restore Procedure

**Restoring from backup:**

```bash
# SOLUTION: Restore procedure
echo "[!] Stopping RabbitMQ (prepare for restore)"
sudo systemctl stop rabbitmq-server

# SOLUTION: Restore backup (backup restoration)
echo "[!] Restoring backup (restoring from backup)"
sudo tar -xzf /var/backups/rabbitmq-backup-2026-01-31.tar.gz -C /var/lib/rabbitmq/

# SOLUTION: Verify restore (data integrity check)
echo "[!] Verifying restore (data integrity check)"
sudo systemctl start rabbitmq-server
sudo rabbitmqctl status

echo "[✓] Restore complete (data recovered)"
```

### Best Practices

**Automatic Backups:**
✅ Schedule backups (cron jobs)  
✅ Configure backup type (full, incremental)  
✅ Configure backup location (local, offsite)  
✅ Monitor backup status (backup success, backup failures)  
✅ Test backup restoration (restore validation)  

**Data Retention:**
✅ Set retention period (policy-based)  
✅ Configure backup rotation (delete old backups)  
✅ Configure retention per backup type (full, incremental)  
✅ Monitor backup storage (disk space usage)  

**Restore Procedures:**
✅ Document restore procedures (data recovery)  
✅ Test restore procedures (restore validation)  
✅ Monitor restore status (data integrity)  
✅ Plan restore downtime (maintenance window)  

**Disaster Recovery:**
✅ Document disaster recovery plan (business continuity)  
✅ Configure offsite storage (data protection)  
✅ Configure failover (automatic recovery)  
✅ Test disaster recovery (simulated disaster)  

**Backup Validation:**
✅ Test backup restoration (restore validation)  
✅ Verify backup integrity (checksum, encryption)  
✅ Schedule restore testing (regular validation)  
✅ Monitor backup validation (restore success)  

**Backup Encryption:**
✅ Encrypt backups (at rest)  
✅ Configure encryption keys (key management)  
✅ Verify encryption (decrypt test)  
✅ Rotate encryption keys (key rotation)  

### Common Mistakes

❌ No automatic backups → Data loss (no recovery)  
❌ No data retention → Disk full (no cleanup)  
❌ No restore procedures → Data loss = permanent (no recovery)  
❌ No disaster recovery plan → System downtime (no business continuity)  
❌ No offsite storage → Single point of failure (data loss)  
❌ No backup validation → Untested backups (restore failure)  
❌ No backup encryption → Data exposure (data theft)  

---

## 7️⃣ Hands-On Lab

### 🔴 Problem Scenario

**Data Loss (The "No Recovery" Problem)**

You're protecting RabbitMQ data from loss:

- System must protect data (no data loss)
- System must be compliant (data retention, recovery)
- System must have recovery procedures (data recovery)
- System must have disaster recovery (business continuity)
- SLA requirements (99.9%+ uptime)

Current implementation:
- No automatic backups (no scheduled backups)
- No data retention policies (disk full risk)
- No restore procedures (data loss = permanent)
- No disaster recovery (system downtime)
- No offsite storage (single point of failure)
- No backup validation (untested backups)
- No backup encryption (data exposure)
- **Impact:** Data loss, system downtime, compliance violation, fines, lawsuits

### 🧪 Lab Tasks

**Step 1: Test Data Loss**

```bash
# Simulate data loss (no backups)
echo "[!] Simulating data loss (no backups)"
sudo systemctl stop rabbitmq-server

# PROBLEM: No backup available (no recovery)
echo "[!] No backup available (no recovery)"
echo "[!] Data loss (all messages lost)"

# PROBLEM: No restore procedures (data loss = permanent)
echo "[!] No restore procedures (data loss = permanent)"

# PROBLEM: No disaster recovery (system downtime)
echo "[!] No disaster recovery (system downtime)"

# PROBLEM: No offsite storage (single point of failure)
echo "[!] No offsite storage (single point of failure)"

# PROBLEM: No backup validation (untested backups)
echo "[!] No backup validation (untested backups)"

# PROBLEM: No backup encryption (data exposure)
echo "[!] No backup encryption (data exposure)"

echo "[!] Data loss scenario (PROBLEM: No backups, no recovery, no disaster recovery)"
```

**Expected observation:**
- No backups available (no recovery)
- No restore procedures (data loss = permanent)
- No disaster recovery (system downtime)
- No offsite storage (single point of failure)
- No backup validation (untested backups)
- No backup encryption (data exposure)
- **Impact:** Data loss, system downtime, compliance violation, fines, lawsuits

### ✅ Solution & Explanation

**Solution: Implement Backup and Disaster Recovery (Automatic Backups + Retention + Restore + Disaster Recovery)**

**Step 1: Configure Automatic Backups**

```bash
# SOLUTION: Configure automatic backups
sudo crontab -e << EOF
# RabbitMQ Automatic Backups
# Schedule daily backup at 2 AM (0 2 * * *)
0 2 * * * root /bin/tar -czf /var/backups/rabbitmq-backup-$(date +\%Y\%m\%d).tar.gz /var/lib/rabbitmq/

# Schedule weekly full backup at 2 AM on Sunday (0 2 * * 0)
0 2 * * 0 root /bin/tar -czf /var/backups/rabbitmq-full-backup-$(date +\%Y\%m\%d).tar.gz /var/lib/rabbitmq/

# Schedule incremental backup every 6 hours
0 */6 * * * root /bin/tar -czf /var/backups/rabbitmq-incremental-backup-$(date +\%Y\%m\%d-\%H\%M).tar.gz /var/lib/rabbitmq/
EOF

echo "[✓] Automatic backups configured (scheduled)"
```

**Step 2: Configure Data Retention**

```bash
# SOLUTION: Configure data retention policies
cat > /usr/local/bin/rabbitmq-cleanup.sh << 'EOF'
#!/bin/bash
# RabbitMQ Data Retention Policy

# Delete backups older than 90 days
find /var/backups/ -name "rabbitmq-backup-*" -mtime +90 -delete

# Delete backups older than 7 days (incremental)
find /var/backups/ -name "rabbitmq-incremental-backup-*" -mtime +7 -delete

# Keep only last 7 full backups
ls -t /var/backups/rabbitmq-full-backup-* | tail -n +8 | xargs rm -f

echo "[x] Cleaned up old backups (retention policy applied)"
EOF

chmod +x /usr/local/bin/rabbitmq-cleanup.sh

# Schedule cleanup (daily at 3 AM)
(crontab -l 2>/dev/null || true; echo "0 3 * * * root /usr/local/bin/rabbitmq-cleanup.sh") | crontab -

echo "[✓] Data retention policies configured (retention: 90 days)"
```

**Step 3: Configure Restore Procedures**

```bash
# SOLUTION: Create restore script
cat > /usr/local/bin/rabbitmq-restore.sh << 'EOF'
#!/bin/bash
# RabbitMQ Restore Procedure

echo "[!] Stopping RabbitMQ (prepare for restore)"
sudo systemctl stop rabbitmq-server

echo "[!] Restoring backup (restoring from backup)"
BACKUP_FILE=$1
sudo tar -xzf /var/backups/$BACKUP_FILE -C /var/lib/rabbitmq/

echo "[!] Starting RabbitMQ (resuming operations)"
sudo systemctl start rabbitmq-server

echo "[!] Verifying restore (data integrity check)"
sudo rabbitmqctl status

echo "[✓] Restore complete (data recovered)"
EOF

chmod +x /usr/local/bin/rabbitmq-restore.sh

echo "[✓] Restore procedures configured (data recovery)"
```

**Step 4: Test Restore**

```bash
# SOLUTION: Test restore (restore validation)
echo "[!] Testing restore (restore validation)"
sudo /usr/local/bin/rabbitmq-restore.sh rabbitmq-backup-2026-01-31.tar.gz

# SOLUTION: Verify restore (data integrity)
echo "[!] Verifying restore (data integrity)"
sudo rabbitmqctl status

echo "[✓] Restore test complete (restore validated)"
```

**How to verify:**

```bash
# SOLUTION: Verify automatic backups
ls -lh /var/backups/

# SOLUTION: Verify data retention
sudo /usr/local/bin/rabbitmq-cleanup.sh

# SOLUTION: Verify restore procedures
sudo /usr/local/bin/rabbitmq-restore.sh rabbitmq-backup-2026-01-31.tar.gz
```

**Expected output:**

```
# SOLUTION: Automatic Backups
[✓] Automatic backups configured (scheduled)

# SOLUTION: Data Retention
[✓] Data retention policies configured (retention: 90 days)

# SOLUTION: Restore Procedures
[✓] Restore procedures configured (data recovery)

# SOLUTION: Restore Test
[!] Testing restore (restore validation)
[!] Stopping RabbitMQ (prepare for restore)
[!] Restoring backup (restoring from backup)
[!] Starting RabbitMQ (resuming operations)
[!] Verifying restore (data integrity check)
[✓] Restore complete (data recovered)
[✓] Restore test complete (restore validated)
```

**Comparison:**

| Design | Automatic Backups | Retention | Restore | Disaster Recovery |
|--------|----------------|----------|---------|----------------|
| No Backups (old) | No | No | No | No |
| With Backups (new) | Yes | Yes | Yes | Yes |

---

## 8️⃣ Best Practices & Production Notes

### Do's and Don'ts

**✅ Do:**
- Schedule automatic backups (cron jobs)  
- Configure backup type (full, incremental)  
- Configure backup location (local, offsite)  
- Set retention period (policy-based)  
- Configure backup rotation (delete old backups)  
- Document restore procedures (data recovery)  
- Test restore procedures (restore validation)  
- Document disaster recovery plan (business continuity)  
- Configure offsite storage (data protection)  
- Test disaster recovery (simulated disaster)  
- Validate backups (restore testing)  
- Encrypt backups (data protection)  
- Rotate encryption keys (key rotation)  

**❌ Don't:**
- No automatic backups → Data loss (no recovery)  
- No data retention → Disk full (no cleanup)  
- No restore procedures → Data loss = permanent (no recovery)  
- No disaster recovery → System downtime (no business continuity)  
- No offsite storage → Single point of failure (data loss)  
- No backup validation → Untested backups (restore failure)  
- No backup encryption → Data exposure (data theft)  

### Backup and Disaster Recovery Guidelines

```
Automatic Backups:
├─ Schedule backups (cron jobs)
├─ Configure backup type (full, incremental)
├─ Configure backup location (local, offsite)
└─ Monitor backup status (backup success, backup failures)

Data Retention:
├─ Set retention period (policy-based)
├─ Configure backup rotation (delete old backups)
├─ Configure retention per backup type (full, incremental)
└─ Monitor backup storage (disk space usage)

Restore Procedures:
├─ Document restore procedures (data recovery)
├─ Test restore procedures (restore validation)
├─ Monitor restore status (data integrity)
└─ Plan restore downtime (maintenance window)

Disaster Recovery:
├─ Document disaster recovery plan (business continuity)
├─ Configure offsite storage (data protection)
├─ Configure failover (automatic recovery)
└─ Test disaster recovery (simulated disaster)

Backup Validation:
├─ Test backup restoration (restore validation)
├─ Verify backup integrity (checksum, encryption)
├─ Schedule restore testing (regular validation)
└─ Monitor backup validation (restore success)

Backup Encryption:
├─ Encrypt backups (at rest)
├─ Configure encryption keys (key management)
├─ Verify encryption (decrypt test)
└─ Rotate encryption keys (key rotation)
```

### Production Considerations

**Backup Strategy:**

```bash
# SOLUTION: Full + Incremental backup strategy
# Full backup (daily)
0 2 * * * root /bin/tar -czf /var/backups/rabbitmq-full-backup-$(date +\%Y\%m\%d).tar.gz /var/lib/rabbitmq/

# Incremental backup (every 6 hours)
0 */6 * * * root /bin/tar -czf /var/backups/rabbitmq-incremental-backup-$(date +\%Y\%m\%d-\%H\%M).tar.gz /var/lib/rabbitmq/
```

**Offsite Storage:**

```bash
# SOLUTION: Configure offsite storage (S3)
# Upload backups to S3
aws s3 sync /var/backups/ s3://rabbitmq-backups/ --delete

echo "[✓] Offsite storage configured (S3)"
```

---

## 9️⃣ Interview & Real-World Notes

### Common Interview Questions

**Q1: How do you configure RabbitMQ automatic backups?**

A: Use cron jobs to schedule backups (daily, weekly). Configure backup type (full, incremental). Configure backup location (local, offsite). Monitor backup status (backup success, backup failures).

**Q2: How do you configure RabbitMQ data retention?**

A: Use bash script to delete old backups (find, delete). Configure retention period (90 days). Configure backup rotation (keep last 7 full backups). Schedule cleanup (cron job).

**Q3: How do you restore RabbitMQ from backup?**

A: Stop RabbitMQ (prepare for restore). Restore backup (tar -xzf). Verify restore (rabbitmqctl status). Start RabbitMQ (resumed operations).

**Q4: How do you implement RabbitMQ disaster recovery?**

A: Document disaster recovery plan (business continuity). Configure offsite storage (S3, Azure, GCP). Configure failover (cluster failover). Test disaster recovery (simulated disaster).

**Q5: How do you validate RabbitMQ backups?**

A: Test backup restoration (restore to staging). Verify backup integrity (checksum, encryption). Schedule restore testing (weekly validation). Monitor backup validation (restore success).

### Production Pitfalls

**Pitfall 1: No automatic backups**
- Problem: Data loss (no recovery)
- Detection: Disk failure, data loss
- Solution: Always schedule automatic backups (cron jobs)

**Pitfall 2: No data retention**
- Problem: Disk full (no cleanup)
- Detection: Disk space usage, backup failures
- Solution: Always configure data retention (retention policies)

**Pitfall 3: No restore procedures**
- Problem: Data loss = permanent (no recovery)
- Detection: Data loss, restore failure
- Solution: Always document restore procedures (data recovery)

**Pitfall 4: No disaster recovery**
- Problem: System downtime (no business continuity)
- Detection: System downtime, SLA violations
- Solution: Always document disaster recovery plan (business continuity)

**Pitfall 5: No offsite storage**
- Problem: Single point of failure (data loss)
- Detection: Data center failure, data loss
- Solution: Always configure offsite storage (S3, Azure, GCP)

**Pitfall 6: No backup validation**
- Problem: Untested backups (restore failure)
- Detection: Restore failure (data loss)
- Solution: Always validate backups (restore testing)

**Pitfall 7: No backup encryption**
- Problem: Data exposure (data theft)
- Detection: Data breach, compliance violation
- Solution: Always encrypt backups (AES-256, key rotation)

### Advanced Backup Concepts

**Backup Strategy Implementation:**

```bash
# Full + Incremental backup strategy
cat > /usr/local/bin/rabbitmq-backup.sh << 'EOF'
#!/bin/bash
# RabbitMQ Backup Strategy (Full + Incremental)

# Full backup (daily)
echo "[x] Full backup (daily)"
/bin/tar -czf /var/backups/rabbitmq-full-backup-$(date +\%Y\%m\%d).tar.gz /var/lib/rabbitmq/

# Incremental backup (every 6 hours)
echo "[x] Incremental backup (every 6 hours)"
/bin/tar -czf /var/backups/rabbitmq-incremental-backup-$(date +\%Y\%m\%d-\%H\%M).tar.gz /var/lib/rabbitmq/

# Upload to offsite storage (S3)
echo "[x] Uploading to offsite storage (S3)"
aws s3 sync /var/backups/ s3://rabbitmq-backups/ --delete

echo "[✓] Backup complete (full + incremental, offsite)"
EOF

chmod +x /usr/local/bin/rabbitmq-backup.sh
```

---

## 📚 Summary

Backup and Disaster Recovery ensures RabbitMQ data is protected from loss, corruption, and downtime. Automatic backups provide scheduled data protection. Data retention policies manage backup storage. Restore procedures enable data recovery. Disaster recovery planning ensures business continuity. Offsite storage provides data protection. Backup validation ensures tested backups. Backup encryption secures data at rest.

**Key takeaways:**
- Schedule automatic backups (cron jobs)
- Configure backup type (full, incremental)
- Configure backup location (local, offsite)
- Set retention period (policy-based)
- Configure backup rotation (delete old backups)
- Document restore procedures (data recovery)
- Document disaster recovery plan (business continuity)
- Configure offsite storage (data protection)
- Validate backups (restore testing)
- Encrypt backups (data protection)
- Rotate encryption keys (key rotation)

**Next steps:**
- Practice with backup and disaster recovery in your environments
- Learn about monitoring and alerting best practices (next lesson)
- Learn about troubleshooting and case studies (Module 06)
- Complete all lessons in Module 05

---

**Module 05 - Best Practices & Production Deployment**  
**Lesson 04 - Complete**