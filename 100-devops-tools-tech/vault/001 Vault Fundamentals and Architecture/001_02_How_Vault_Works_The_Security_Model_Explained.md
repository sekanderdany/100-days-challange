# How Vault Works - The Security Model Explained

## Learning Objectives

By the end of this lesson, you will understand:
- Vault's core security architecture and design principles
- How to barrier, storage backend, and core components interact
- The authentication and authorization flow in Vault
- How encryption protects data at rest and in transit
- The difference between sealed and unsealed states

## Introduction

Vault's security model is built on a foundation of cryptographic barriers, zero-trust principles, and defense-in-depth. Understanding how Vault works internally is critical for operating it securely and effectively in production environments.

## Vault's Security Architecture

### The Three Pillars of Vault Security

1. **Cryptographic Barrier**: Encryption at rest and in transit
2. **Least Privilege**: Fine-grained access control
3. **Auditability**: Complete logging of all operations

### Core Components Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Vault Client                          │
│              (Application, User, System)                │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/HTTPS (TLS/mTLS)
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Vault API Layer (HTTP)                      │
│         CLI, API, UI all use same endpoint               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Authentication Methods Layer                    │
│   (Token, AppRole, Kubernetes, LDAP, OIDC, etc.)       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               Barrier Layer                              │
│    Encryption/Decryption of all data to/from storage     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                Core Layer                                │
│      Path-based routing, policy enforcement, leases      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│             Storage Backend                             │
│   (Raft, Consul, Integrated Storage, Filesystem, etc.)   │
└─────────────────────────────────────────────────────────┘
```

## The Barrier: Vault's Encryption Engine

### What is the Barrier?

The barrier is the cryptographic boundary that encrypts all data before it reaches the storage backend and decrypts it after retrieval. It ensures that even with physical access to the storage backend, data remains unreadable without Vault being unsealed.

### Barrier Encryption Flow

**Writing Data:**
1. Client sends encrypted request via TLS
2. Barrier decrypts request
3. Core processes request (policy check, validation)
4. Barrier encrypts data with master key
5. Encrypted data written to storage backend

**Reading Data:**
1. Client sends request via TLS
2. Barrier decrypts request
3. Core processes request (policy check, validation)
4. Encrypted data read from storage backend
5. Barrier decrypts data with master key
6. Data returned to client via TLS

### Encryption Keys

Vault uses a multi-layered encryption approach:

1. **Master Key**: Generated during initialization, never stored in Vault
2. **Unseal Keys**: Fragments of master key, held by operators
3. **Data Encryption Keys (DEKs)**: Per-object encryption keys
4. **Key Encryption Keys (KEKs)**: Wrap DEKs using master key

### Seal vs Unsealed States

**Sealed State:**
- Master key is not available in memory
- Barrier cannot encrypt or decrypt data
- Vault can only perform initialization and unseal operations
- No secrets can be accessed
- High security, low availability

**Unsealed State:**
- Master key is loaded in memory
- Barrier can encrypt and decrypt data
- Normal operations are possible
- Secrets can be accessed
- Requires protecting master key in memory

**Why Sealing Matters:**
- Physical security: Server compromise doesn't expose encrypted data
- Memory protection: Sealed Vault has no secrets in memory
- Compliance: Meets requirements for data at rest encryption
- Disaster recovery: Storage backup can be safely stored

## The Storage Backend

### Storage Backend Options

Vault supports multiple storage backends, each with trade-offs:

1. **Integrated Storage (Raft)**: Modern default, embedded consensus
2. **Consul**: External Consul cluster
3. **Filesystem**: Simple, not production-ready
4. **Cloud Storage**: AWS S3, Azure Blob, GCS (via plugins)
5. **Database**: MySQL, PostgreSQL, MongoDB (via plugins)

### What the Storage Backend Sees

The storage backend only sees encrypted data:
```
# Example storage backend view (Raft)
/path/to/secret/1: "a8f7e9d2c3b1a5e6f4d7c8b9a0e1f2d3..."
/path/to/secret/2: "b9e8a7f6d5c4b3a2e1d0f9c8b7a6e5f4..."
/sys/core/keys: "c0f9e8d7c6b5a4e3d2f1c0b9a8e7f6d5..."
```

The storage backend cannot:
- Read any secret data
- Understand data structure
- Access authentication information
- Modify policies or configuration

### Storage Backend Security

**Never Trust Storage Backend:**
- Assume storage can be copied or accessed
- Assume storage admin is malicious
- Assume storage can be compromised
- Assume storage can be stolen

**Always Encrypt at Storage Level:**
- Use encryption-at-rest on storage
- Use secure transit between Vault and storage
- Use network isolation for storage backend
- Rotate storage credentials regularly

## Core: The Brains of Vault

### Core Responsibilities

The Core component handles all business logic:

1. **Path Routing**: Map requests to secrets engines or auth methods
2. **Policy Enforcement**: Check access before operations
3. **Lease Management**: Track TTL and renewal
4. **Token Management**: Create, renew, revoke tokens
5. **Secret Generation**: Generate dynamic secrets
6. **Audit Logging**: Record all operations

### Request Flow Through Core

```
1. Authentication Request
   ├─ Validate credentials with auth method
   ├─ Create or retrieve token
   ├─ Associate policies with token
   └─ Return token to client

2. Secret Request (e.g., GET /secret/data/myapp)
   ├─ Authenticate token
   ├─ Check policies for path access
   ├─ Retrieve secret from storage (via Barrier)
   ├─ Check lease information
   ├─ Add lease metadata
   ├─ Log to audit devices
   └─ Return secret to client

3. Write Request (e.g., POST /secret/data/myapp)
   ├─ Authenticate token
   ├─ Check policies for write capability
   ├─ Validate input data
   ├─ Encrypt and store secret (via Barrier)
   ├─ Log to audit devices
   └─ Return success to client
```

## Authentication Flow

### Step-by-Step Authentication

1. **Client submits credentials** to auth method
   ```
   POST /v1/auth/userpass/login/user1
   {"password": "securepassword123"}
   ```

2. **Vault authenticates** with configured auth method
   - UserPass: Check username/password against stored credentials
   - LDAP: Query LDAP server
   - Kubernetes: Validate service account token
   - AppRole: Verify role ID and secret ID

3. **Vault creates a token** with:
   - Token TTL (time-to-live)
   - Token policies (access control)
   - Token metadata
   - Parent token reference (if applicable)
   - Use limits (optional)

4. **Vault returns token** to client
   ```json
   {
     "auth": {
       "client_token": "s.1234567890abcdef",
       "lease_duration": 86400,
       "renewable": true,
       "policies": ["default", "myapp"]
     }
   }
   ```

5. **Client uses token** for subsequent requests
   ```
   GET /v1/secret/data/myapp
   X-Vault-Token: s.1234567890abcdef
   ```

### Token Lifecycle

```
┌─────────┐  Create   ┌─────────┐  Use     ┌─────────┐
│  Client │──────────▶│   Vault │─────────▶│  Token  │
└─────────┘           └─────────┘           └─────────┘
                         │                        │
                         │ Renewable              │ TTL
                         │─────────┐              │
                         │         ▼              │
                         │    ┌─────────┐         │
                         │    │ Renew   │◀────────┤
                         │    └─────────┘         │
                         │                        │
                         │ Expired               │ Revoked
                         │        ┌───────────────┤
                         │        ▼               │
                         │   ┌─────────┐          │
                         └───│ Expire  │◀─────────┘
                             │ Revoke │
                             └─────────┘
```

## Authorization Flow

### Policy-Based Access Control

After authentication, every request goes through policy checks:

1. **Extract token** from request
2. **Lookup token** in Vault (validate, check expiration)
3. **Load policies** associated with token
4. **Match path** to policy rules
5. **Check capabilities** (read, write, delete, list, sudo)
6. **Allow or deny** request

### Policy Evaluation Example

**Token Policies:** `["default", "database-admin"]`

**Request:** `GET /v1/database/creds/production`

**Policy Check:**
```hcl
# default policy
path "secret/data/*" {
  capabilities = ["read"]
}

# database-admin policy
path "database/creds/production" {
  capabilities = ["create", "read", "update", "delete"]
}
```

**Result:** ✅ Allowed (read capability on database/creds/production)

## Data Protection Model

### Encryption at Rest

1. **Master Key**: Generated during initialization
   - 256-bit AES key (AES-256-GCM)
   - Never stored in Vault data
   - Split into unseal key shards

2. **Data Encryption**: Per-object encryption
   - Each secret encrypted with unique DEK
   - DEK encrypted with KEK (derived from master key)
   - Uses authenticated encryption (AES-GCM)

3. **Key Rotation**: Periodic rotation supported
   - Rotate master key
   - Re-encrypt all data
   - Can be done without downtime

### Encryption in Transit

1. **TLS Configuration**: Required for production
   - TLS 1.2 or higher
   - Strong cipher suites
   - Certificate validation

2. **mTLS Support**: Mutual TLS for client authentication
   - Client certificates required
   - Certificate validation
   - Certificate revocation checking

3. **API Security**: Additional protections
   - Rate limiting
   - Request size limits
   - Request timeout configuration

## Security Guarantees

### What Vault Guarantees

✅ **Confidentiality**: Data encrypted at rest and in transit
✅ **Integrity**: Authenticated encryption prevents tampering
✅ **Auditability**: Complete logging of all operations
✅ **Least Privilege**: Fine-grained access control
✅ **Revocability**: Immediate revocation of access
✅ **Zero Trust**: Never trust, always verify

### What Vault Does NOT Guarantee

❌ **Network Security**: You must secure network connections
❌ **Client Security**: Clients must protect tokens
❌ **Storage Security**: Storage backend must be secured
❌ **Physical Security**: Servers must be physically secured
❌ **Operational Security**: Proper procedures must be followed

## Common Security Patterns

### Pattern 1: Least Privilege Access

```hcl
# Bad: Too broad
path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Good: Specific paths and capabilities
path "secret/data/myapp/*" {
  capabilities = ["read"]
}
```

### Pattern 2: Time-Limited Access

```bash
# Create token with short TTL
vault token create -ttl=1h -policy=myapp-policy

# Use periodic tokens for long-running apps
vault token create -policy=myapp-policy -period=24h
```

### Pattern 3: Renewable Leases

```bash
# Database secrets engine with renewable lease
vault write database/config/mydb \
    lease_ttl=1h \
    lease_max_ttl=24h

# Renew lease before expiration
vault lease renew database/creds/mydb/abcdef
```

### Pattern 4: Audit Everything

```bash
# Enable audit logging
vault audit enable file file_path=/var/log/vault/audit.log

# Monitor audit logs for suspicious activity
tail -f /var/log/vault/audit.log | grep "request_path"
```

## Real-World Security Considerations

### Production Deployment

1. **Network Isolation**
   - Place Vault in private network
   - Use load balancer with TLS termination
   - Restrict access to storage backend

2. **Certificate Management**
   - Use certificates from corporate PKI
   - Implement certificate rotation
   - Use mTLS for server-to-server communication

3. **Monitoring and Alerting**
   - Monitor seal/unseal events
   - Alert on failed authentication attempts
   - Track policy violations

4. **Backup and Recovery**
   - Regular snapshots of storage backend
   - Secure storage of unseal keys
   - Test recovery procedures

### Security Best Practices

1. **Never share root tokens**
   - Use root token only for initialization
   - Revoke root token after setup
   - Use individual auth methods for operators

2. **Rotate secrets regularly**
   - Enable automatic rotation where possible
   - Set appropriate TTLs
   - Monitor expiration

3. **Implement defense in depth**
   - Network security (firewalls, VPC)
   - Application security (TLS, mTLS)
   - Operational security (procedures, training)

4. **Plan for compromise**
   - Know how to seal Vault quickly
   - Have incident response procedures
   - Practice incident response

## Summary

Vault's security model is built on three pillars:

1. **Cryptographic Barrier**: Encrypts all data at rest and in transit
2. **Least Privilege**: Fine-grained, policy-based access control
3. **Auditability**: Complete logging of all operations

The barrier ensures that even with physical access to the storage backend, data remains unreadable without Vault being unsealed. The core handles all business logic, including path routing, policy enforcement, lease management, and audit logging.

Understanding Vault's security architecture is essential for:
- Designing secure deployments
- Implementing proper access controls
- Troubleshooting security issues
- Meeting compliance requirements

In the next lesson, we'll explore real-world use cases and benefits of Vault in modern DevSecOps environments.

## Key Terms

- **Barrier**: Cryptographic boundary encrypting all data
- **Sealed State**: Vault cannot encrypt/decrypt data
- **Unsealed State**: Vault master key is in memory
- **Storage Backend**: Where encrypted data is stored
- **Core**: Vault's business logic component
- **Master Key**: Primary encryption key, never stored
- **Unseal Keys**: Fragments of master key, held by operators
- **TLS**: Transport Layer Security for encryption in transit
- **mTLS**: Mutual TLS for client certificate authentication
- **Lease**: Time-limited secret access
- **Policy**: Rules defining access control
- **Token**: Authentication credential with associated policies

## Further Reading

- [Vault Architecture Documentation](https://developer.hashicorp.com/vault/docs/internals/architecture)
- [Vault Security Model](https://developer.hashicorp.com/vault/docs/internals/security)
- [Vault Encryption Details](https://developer.hashicorp.com/vault/docs/internals/encryption)

## Practice Exercises

1. Draw a diagram showing Vault request flow from client to storage backend
2. Explain the difference between sealed and unsealed states
3. Describe how the barrier protects data in the storage backend
4. Create a simple policy that allows read access to a specific path
5. Explain the token lifecycle from creation to expiration

## Next Steps

Proceed to "Real-World Use Cases and Benefits" to learn about practical Vault deployments.