# 001_05 Understanding the Vault Architecture - Deep Dive

## Learning Objectives

By the end of this lesson, you will:
- Understand Vault's layered architecture and component interactions
- Identify how data flows through Vault's core systems
- Explain the roles of storage backends, barrier, and core
- Understand the encryption key hierarchy and master key
- Recognize how Vault handles authentication and authorization
- Visualize the complete request lifecycle in Vault

## Introduction

Vault's architecture is designed with security as a foundational principle. Every component, every data flow, and every interaction has been carefully engineered to protect secrets while providing a flexible, extensible platform for secrets management. This lesson takes you beneath the surface to understand how Vault's architecture works, from the physical storage layer to the logical access controls.

## Vault Architecture Overview

### High-Level Architecture

Vault follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Vault Clients                           │
│              (Applications, Users, Systems)                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP/HTTPS (TLS)
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   API Layer                               │
│          (HTTP Endpoints, REST Interface)                  │
│  • v1/sys/* - System management                       │
│  • v1/auth/* - Authentication                          │
│  • v1/secret/* - Secrets access                       │
│  • v1/* - Other endpoints                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Core Layer                               │
│          (Request Handling, Business Logic)                  │
│  • Request routing                                       │
│  • Authentication verification                            │
│  • Authorization (policy checking)                        │
│  • Secrets engine routing                                │
│  • Audit logging                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Barrier Layer                            │
│           (Encryption/Decryption Boundary)                   │
│  • Encrypts data before storage                          │
│  • Decrypts data after retrieval                         │
│  • Manages encryption keys                              │
│  • Enforces seal state                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Storage Backend Layer                          │
│         (Physical Data Persistence)                         │
│  • Raft (Integrated Storage)                            │
│  • Consul                                              │
│  • S3, DynamoDB, etc. (non-HA)                       │
│  • File system (development only)                        │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Principles

1. **Defense in Depth**: Multiple layers of security
2. **Encrypt at Rest**: All data encrypted before storage
3. **Zero Trust**: Every request authenticated and authorized
4. **Audit Everything**: All operations logged
5. **Modular Design**: Pluggable components (auth methods, secrets engines)

## Component Deep Dive

### 1. Storage Backend

The storage backend is responsible for persisting Vault's encrypted data. It's the only component that touches physical storage.

**Responsibilities:**
- Store encrypted data from barrier layer
- Provide transactional operations (for consistency)
- Support high availability (cluster coordination)
- Maintain data durability

**Storage Backend Types:**

**Integrated Storage (Raft) - Production Default:**
- Built-in consensus algorithm
- No external dependencies
- Automatic leader election
- Data replication across nodes
- Snapshot-based backups
- Example configuration:
```hcl
storage "raft" {
  path = "/opt/vault/data"
  node_id = "vault-1"
  retry_join {
    leader_api_addr = "http://vault-1:8200"
  }
}
```

**Consul Storage - Legacy but Still Used:**
- External Consul cluster required
- Service discovery built-in
- Health checking
- KV store for data persistence
- Example configuration:
```hcl
storage "consul" {
  path = "vault/"
  address = "127.0.0.1:8500"
  scheme = "http"
}
```

**Cloud Storage - Non-HA Options:**
- AWS S3
- Azure Blob Storage
- Google Cloud Storage
- DynamoDB, Spanner, etc.
- Example (S3):
```hcl
storage "s3" {
  bucket = "my-vault-data"
  region = "us-east-1"
  access_key = "AWS_ACCESS_KEY"
  secret_key = "AWS_SECRET_KEY"
}
```

**File System - Development Only:**
- Simple file-based storage
- No high availability
- Not suitable for production
- Example configuration:
```hcl
storage "file" {
  path = "./vault-data"
}
```

**Critical Security Note:**
The storage backend NEVER sees unencrypted data. The barrier layer encrypts everything before passing it to storage. Even if an attacker gains access to the storage backend, they only see encrypted blobs.

### 2. Barrier Layer

The barrier is Vault's cryptographic boundary - the most critical security component.

**Responsibilities:**
- Encrypt all data before storage
- Decrypt all data after retrieval
- Manage encryption keys
- Enforce seal/unseal state
- Protect the master key

**Encryption Key Hierarchy:**

```
┌─────────────────────────────────────────┐
│     Master Key (Master Encryption Key)  │
│  • Stored offline (never in Vault)        │
│  • Split into key shards               │
│  • Used to encrypt keyring             │
│  • Required to unseal Vault             │
└──────────────┬──────────────────────────┘
               │ decrypts
               │
┌──────────────▼──────────────────────────┐
│      Keyring (Encryption Keys)           │
│  • Encrypted with master key           │
│  • Stored in storage backend            │
│  • Contains data encryption keys       │
│  • Rotated periodically               │
└──────────────┬──────────────────────────┘
               │ encrypts
               │
┌──────────────▼──────────────────────────┐
│     Data (Secrets, Config, etc.)       │
│  • Encrypted with keyring keys        │
│  • Stored in storage backend            │
│  • Always at rest encrypted           │
└──────────────────────────────────────────┘
```

**Seal State:**
- **Sealed**: Vault is encrypted and offline
  - Master key not in memory
  - Cannot serve any requests
  - Storage backend inaccessible
  - Physical access required to unseal

- **Unsealed**: Vault is operational
  - Master key decrypted and in memory
  - Can serve requests
  - Encryption/decryption operational
  - Sensitive data in RAM

**Seal vs. Shutdown:**
- Shutdown: Graceful process termination
  - Saves state
  - Can restart automatically
  - Still requires unseal if not using auto-unseal

- Seal: Immediate cryptographic lock
  - Clears master key from memory
  - Emergency security measure
  - Must manually unseal to recover

### 3. Core Layer

The core is Vault's business logic engine - the brains of the operation.

**Responsibilities:**
- Route incoming requests
- Verify authentication
- Check authorization (policies)
- Invoke secrets engines
- Manage token lifecycle
- Coordinate with audit devices
- Handle replication (if configured)

**Request Flow Through Core:**

```
1. Request Received
   │
   ▼
2. TLS Termination
   │
   ▼
3. Request Parsing (HTTP → Internal)
   │
   ▼
4. Authentication Check
   │   ├─→ No auth provided → 401 Unauthorized
   │   └─→ Auth provided → Verify
   │
   ▼
5. Authorization Check
   │   ├─→ Policy check
   │   ├─→ No permission → 403 Forbidden
   │   └─→ Permission granted → Continue
   │
   ▼
6. Secrets Engine Routing
   │   ├─→ Identify target engine
   │   ├─→ Route to engine
   │   └─→ Execute engine logic
   │
   ▼
7. Barrier Operations
   │   ├─→ Encrypt data (if storing)
   │   ├─→ Decrypt data (if retrieving)
   │   └─→ Pass to storage
   │
   ▼
8. Response Generation
   │
   ▼
9. Audit Logging
   │
   ▼
10. Response to Client
```

### 4. API Layer

The API layer provides the external interface to Vault.

**Endpoints Categories:**

**System Endpoints (`v1/sys/*`):**
- System configuration
- Seal/unseal operations
- Key management
- Audit device configuration
- Replication management
- Health checks

Example endpoints:
```
POST /v1/sys/seal
POST /v1/sys/unseal
GET /v1/sys/health
GET /v1/sys/leader
PUT /v1/sys/config/audits/file
```

**Authentication Endpoints (`v1/auth/*`):**
- Login operations
- Token management
- MFA challenges
- Auth method configuration

Example endpoints:
```
POST /v1/auth/userpass/login/{username}
POST /v1/auth/approle/login
POST /v1/auth/kubernetes/login
GET /v1/auth/token/renew-self
```

**Secrets Engine Endpoints (`v1/{mount}/*`):**
- Secrets access
- Engine configuration
- Dynamic credential generation

Example endpoints:
```
GET /v1/secret/data/my-secret
POST /v1/secret/data/my-secret
GET /v1/database/creds/production-db
POST /v1/transit/data/my-key/encrypt
```

### 5. Audit Devices

Audit devices provide comprehensive logging of all Vault operations.

**Types of Audit Devices:**

**File Audit Device:**
- Writes audit logs to file
- Simple, local logging
- Example configuration:
```bash
vault audit enable file file_path=/var/log/vault_audit.log
```

**Syslog Audit Device:**
- Sends logs to syslog daemon
- Centralized logging
- Example configuration:
```bash
vault audit enable syslog tag="vault"
```

**Socket Audit Device:**
- Streams logs to Unix domain socket
- Integration with log collectors (Fluentd, etc.)
- Example configuration:
```bash
vault audit enable socket address=/var/run/vault-audit.sock
```

**What Gets Logged:**
- Every request (authenticated and unauthenticated)
- Requestor identity (who)
- Operation performed (what)
- Resource accessed (where)
- Result (success/failure)
- Timestamp
- IP address
- User agent

**Security Note:**
Audit logs are immutable append-only. Vault hashes every log entry to detect tampering. You cannot modify audit logs without breaking the hash chain.

## Data Flow Examples

### Example 1: Writing a Secret

**Scenario:** Application writes API key to Vault

```
1. Client sends request:
   POST /v1/secret/data/api-key
   Headers:
     X-Vault-Token: s.abc123...
   Body:
     {
       "data": {
         "api_key": "sk_live_12345"
       }
     }

2. API Layer receives request
   - Parses HTTP
   - Extracts token
   - Validates TLS

3. Core Layer processes:
   a) Authentication
      - Validates token s.abc123...
      - Retrieves token metadata
      - Token is valid ✓

   b) Authorization
      - Checks policies for token
      - Policy: path "secret/data/api-key" { capabilities = ["create"] }
      - Permission granted ✓

   c) Secrets Engine Routing
      - Routes to KV v2 engine at /secret
      - Engine prepares data for storage

   d) Barrier Operations
      - Barrier encrypts secret data
      - Uses key from keyring
      - Encrypts: sk_live_12345 → encrypted_blob_abc123...

   e) Storage Backend
      - Stores encrypted blob
      - Writes to Raft/S3/Consul
      - Transaction commits

   f) Audit Logging
      - Logs operation
      - Records who, what, when, where
      - Hashes entry

4. Response to client:
   HTTP/1.1 200 OK
   {
     "data": {
       "created_time": "2024-02-21T12:00:00Z",
       "deletion_time": "",
       "destroyed": false,
       "version": 1
     }
   }
```

### Example 2: Reading a Secret

**Scenario:** Application retrieves API key from Vault

```
1. Client sends request:
   GET /v1/secret/data/api-key
   Headers:
     X-Vault-Token: s.abc123...

2. API Layer receives request
   - Parses HTTP
   - Extracts token

3. Core Layer processes:
   a) Authentication
      - Validates token ✓

   b) Authorization
      - Checks policies
      - Policy: path "secret/data/api-key" { capabilities = ["read"] }
      - Permission granted ✓

   c) Secrets Engine Routing
      - Routes to KV v2 engine
      - Engine requests secret

   d) Barrier Operations
      - Requests encrypted blob from storage
      - Retrieves: encrypted_blob_abc123...
      - Decrypts using keyring key
      - Decrypts: encrypted_blob_abc123... → sk_live_12345

   e) Storage Backend
      - Returns encrypted data

   f) Audit Logging
      - Logs retrieval operation

4. Response to client:
   HTTP/1.1 200 OK
   {
     "data": {
       "data": {
         "api_key": "sk_live_12345"
       },
       "metadata": {
         "created_time": "2024-02-21T12:00:00Z",
         "deletion_time": "",
         "destroyed": false,
         "version": 1
       }
     }
   }
```

### Example 3: Dynamic Credential Generation

**Scenario:** Application requests database credentials

```
1. Client sends request:
   GET /v1/database/creds/production-db
   Headers:
     X-Vault-Token: s.abc123...

2. API Layer receives request

3. Core Layer processes:
   a) Authentication ✓
   
   b) Authorization ✓
      - Policy allows database credentials

   c) Secrets Engine Routing
      - Routes to Database secrets engine
      - Engine receives request

   d) Database Engine Logic
      - Connects to database using static credentials
      - Creates new temporary user
      - Grants appropriate permissions
      - Returns credentials:
        username: v-root-prod-db-abc123
        password: xyz789

   e) Barrier Operations
      - Encrypts credentials
      - Stores in storage with lease TTL
      - Sets lease expiration

   f) Audit Logging
      - Logs credential generation

4. Response to client:
   HTTP/1.1 200 OK
   {
     "data": {
       "username": "v-root-prod-db-abc123",
       "password": "xyz789"
     },
     "lease_id": "database/creds/production-db/abc123",
     "lease_duration": "1h",
     "renewable": true
   }
```

## Security Considerations

### Defense in Depth

Vault implements multiple security layers:

1. **Network Layer**
   - TLS encryption for all traffic
   - mTLS for client authentication (optional)
   - Network segmentation recommended

2. **Authentication Layer**
   - Multiple auth methods
   - Token-based access
   - MFA support

3. **Authorization Layer**
   - Policy-based access control
   - Fine-grained permissions
   - Least privilege enforcement

4. **Encryption Layer**
   - Data encrypted at rest
   - Key hierarchy protection
   - Master key isolation

5. **Audit Layer**
   - Comprehensive logging
   - Immutable audit trails
   - Tamper detection

### Data Protection Guarantees

**At Rest:**
- All data encrypted before storage
- AES-256-GCM encryption (standard)
- Keys rotated regularly
- Master key stored offline

**In Transit:**
- TLS 1.2+ required
- Strong cipher suites
- Certificate validation
- mTLS optional but recommended

**In Memory:**
- Secrets only in RAM during processing
- Cleared after use
- Not written to disk/swap
- Protected with OS-level security

## Performance Considerations

### Bottlenecks

**Encryption/Decryption:**
- CPU-intensive operation
- Barrier layer overhead
- Mitigation: Hardware acceleration (AES-NI)

**Storage I/O:**
- Backend read/write latency
- Raft consensus overhead
- Mitigation: SSD storage, local backend

**Network:**
- TLS overhead
- Client-server latency
- Mitigation: Load balancing, geographic proximity

**Policy Evaluation:**
- Complex policy checks
- Multiple policy merges
- Mitigation: Simplify policies, cache where possible

### Scaling Strategies

**Vertical Scaling:**
- Increase CPU (for encryption)
- Increase RAM (for caching)
- Increase storage I/O (for backend)

**Horizontal Scaling:**
- Raft clustering (HA)
- Performance replication (read scaling)
- Multiple Vault clusters

**Optimization:**
- Use Integrated Storage (Raft) for HA
- Enable performance standby nodes
- Implement batch tokens for high-throughput
- Tune Raft parameters

## Troubleshooting Architecture

### Common Issues

**Vault Sealed on Startup:**
- Cause: Master key not in memory
- Solution: Unseal with key shards or auto-unseal

**Storage Backend Unreachable:**
- Cause: Network issues, backend down
- Solution: Check connectivity, restart Vault

**Authentication Failures:**
- Cause: Invalid token, policy denial
- Solution: Validate token, check policies

**Encryption Errors:**
- Cause: Keyring corruption, key mismatch
- Solution: Restore from backup, rekey if needed

### Debugging Tools

**Health Checks:**
```bash
# Check Vault health
curl http://localhost:8200/v1/sys/health

# Check leader status
curl http://localhost:8200/v1/sys/leader
```

**Debug Logging:**
```hcl
# Enable debug logging
log_level = "debug"

# Log to file
log_file = "/var/log/vault/debug.log"
```

**Performance Metrics:**
```bash
# Enable metrics
telemetry {
  disable_hostname = true
  prometheus_retention_time = "24h"
}
```

## Summary

**Key Takeaways:**

1. **Layered Architecture**: Vault's security comes from multiple protection layers, each with specific responsibilities.

2. **Barrier is Critical**: The barrier layer is Vault's cryptographic boundary - the most important security component.

3. **Encryption Everywhere**: All data encrypted at rest, in transit, and protected in memory.

4. **Modular Design**: Auth methods, secrets engines, and audit devices are pluggable and extensible.

5. **Performance Trade-offs**: Security (encryption, policy checks) impacts performance - design accordingly.

6. **Monitoring Essential**: Understand request flows to effectively monitor and troubleshoot Vault.

## Key Terms

- **Storage Backend**: Physical persistence layer for Vault's encrypted data
- **Barrier Layer**: Cryptographic boundary that encrypts/decrypts all data
- **Core Layer**: Business logic engine handling requests and routing
- **API Layer**: External interface exposing HTTP/REST endpoints
- **Audit Device**: Component that logs all Vault operations
- **Master Key**: Root encryption key, split into shards, required to unseal
- **Keyring**: Encrypted storage for data encryption keys
- **Seal State**: Vault's cryptographic offline state (sealed vs. unsealed)
- **Raft**: Consensus algorithm used by Integrated Storage for HA
- **Defense in Depth**: Security approach using multiple overlapping protections

## Further Reading

- [Vault Architecture Documentation](https://developer.hashicorp.com/vault/docs/internals/architecture)
- [Vault Security Model](https://developer.hashicorp.com/vault/docs/internals/security)
- [Vault Storage Backends](https://developer.hashicorp.com/vault/docs/configuration/storage)
- [Vault Audit Devices](https://developer.hashicorp.com/vault/docs/audit-devices)
- [Raft Consensus Algorithm](https://raft.github.io/)

## Practice Exercises

1. **Architecture Diagram**: Draw your own Vault architecture diagram showing all layers and their interactions.

2. **Request Tracing**: Trace through a complete request flow for each operation: write secret, read secret, dynamic credential generation.

3. **Component Mapping**: Map each Vault component to its primary security responsibility.

4. **Performance Analysis**: Identify potential bottlenecks in a production Vault deployment and propose mitigation strategies.

## Next Steps

Now that you understand Vault's architecture deep dive, the next lesson will explore individual components in more detail, starting with the storage backend, barrier, and core layers.

Proceed to Lesson 001_06: Vault Components - Storage Backend, Barrier, and Core.