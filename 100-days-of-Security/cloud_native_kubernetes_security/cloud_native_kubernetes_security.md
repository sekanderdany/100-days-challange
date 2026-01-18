# Cloud Native & Kubernetes Security – Master Course Folder Structure

This is a **final, production‑grade syllabus** combining **KCSA + CKS** with **real‑world enterprise security additions**. Organized from **beginner → advanced**, suitable for **tutorials, labs, and certification prep**.

---

## 00‑Foundations‑of‑Cloud‑Native‑Security
- 00.01 What Is Cloud Native Security
- 00.02 Understanding the Attacker Mindset
- 00.03 The Attack Lifecycle
- 00.04 The 4Cs of Cloud Native Security
- 00.05 Shared Responsibility Model
- 00.06 Cloud Provider Security (AWS / GCP / Azure)
- 00.07 Infrastructure & Node Security Basics

---

## 01‑Kubernetes‑Architecture‑and‑Threat‑Model
- 01.01 Kubernetes Architecture (Security View)
- 01.02 Trust Boundaries & Data Flow
- 01.03 Kubernetes Isolation Techniques
- 01.04 Kubernetes Threat Model Overview
- 01.05 Persistence Attacks
- 01.06 Denial of Service Attacks
- 01.07 Malicious Code Execution
- 01.08 Compromised Containers
- 01.09 Network‑Based Attacks
- 01.10 Privilege Escalation
- 01.11 Access to Sensitive Data

---

## 02‑Cluster‑Setup‑and‑Hardening
- 02.01 CIS Benchmarks Overview
- 02.02 CIS for Linux
- 02.03 CIS for Kubernetes
- 02.04 kube‑bench Tool
- 02.05 Verifying Platform Binaries
- 02.06 Kubernetes Release Security
- 02.07 Secure Cluster Upgrade Process

---

## 03‑Control‑Plane‑and‑Node‑Security
- 03.01 API Server Security
- 03.02 API Groups & Access Control
- 03.03 Controller Manager Security
- 03.04 Scheduler Security
- 03.05 etcd Security (TLS, Backup, Restore)
- 03.06 Kubelet Security
- 03.07 Securing Container Runtime
- 03.08 kube‑proxy Security
- 03.09 Securing Node Metadata

---

## 04‑Identity‑Authentication‑and‑Authorization
- 04.01 Authentication Mechanisms
- 04.02 Certificates & PKI Basics
- 04.03 Kubernetes Certificates API
- 04.04 kubeconfig Security
- 04.05 OIDC Authentication
- 04.06 External IAM Integration (AWS IAM / Azure AD / GCP IAM)
- 04.07 Authorization Overview
- 04.08 RBAC Deep Dive
- 04.09 Roles & ClusterRoles
- 04.10 RoleBindings & ClusterRoleBindings
- 04.11 ABAC (Conceptual)
- 04.12 Service Accounts Security

---

## 05‑Pod‑and‑Workload‑Security
- 05.01 Pod Security Standards
- 05.02 Pod Security Admission
- 05.03 Understanding Pod Security Policies (Deprecated)
- 05.04 Security Contexts
- 05.05 Linux Capabilities
- 05.06 Secrets Management (Native)
- 05.07 Encrypting Secrets at Rest
- 05.08 External Secrets Management (Vault, ESO, KMS)
- 05.09 Secret Rotation Strategies

---

## 06‑Admission‑Control‑and‑Policy‑Enforcement
- 06.01 Admission Controllers Overview
- 06.02 Validating Admission Controllers
- 06.03 Mutating Admission Controllers
- 06.04 ImagePolicyWebhook
- 06.05 Open Policy Agent (OPA)
- 06.06 OPA in Kubernetes
- 06.07 Gatekeeper Architecture
- 06.08 Writing & Enforcing Policies

---

## 07‑Network‑Security‑and‑Multi‑Tenancy
- 07.01 Kubernetes Networking Security Basics
- 07.02 Network Policies
- 07.03 Default‑Deny Models
- 07.04 Ingress Security
- 07.05 TLS Termination & Annotations
- 07.06 Multi‑Tenancy Models
- 07.07 Namespace Isolation
- 07.08 Node‑Based Isolation
- 07.09 Resource Quotas & Limits
- 07.10 API Priority & Fairness

---

## 08‑Linux‑and‑System‑Hardening
- 08.01 Least Privilege Principle
- 08.02 Reducing Attack Surface
- 08.03 Limiting Node Access
- 08.04 SSH Hardening
- 08.05 sudo Security
- 08.06 Firewall Basics (UFW)
- 08.07 Identifying Open Ports
- 08.08 Removing Obsolete Packages
- 08.09 Kernel Module Restrictions

---

## 09‑Runtime‑Security‑and‑Observability
- 09.01 Kubernetes Audit Logging
- 09.02 Audit Policy Design
- 09.03 Runtime Threat Detection
- 09.04 Falco Architecture
- 09.05 Writing Falco Rules
- 09.06 Mutable vs Immutable Infrastructure
- 09.07 Enforcing Runtime Immutability

---

## 10‑Advanced‑Runtime‑Isolation
- 10.01 Linux Syscalls
- 10.02 Seccomp Profiles
- 10.03 AppArmor Profiles
- 10.04 Aqua Tracee
- 10.05 Container Sandboxing
- 10.06 gVisor
- 10.07 Kata Containers
- 10.08 RuntimeClass in Kubernetes

---

## 11‑Service‑Mesh‑and‑Zero‑Trust‑Networking
- 11.01 TLS Fundamentals
- 11.02 Mutual TLS
- 11.03 Kubernetes PKI Deep Dive
- 11.04 Service Mesh Overview
- 11.05 Istio Architecture
- 11.06 Istio Security Model
- 11.07 mTLS with Istio
- 11.08 Pod‑to‑Pod Encryption
- 11.09 Introduction to Cilium
- 11.10 Cilium Architecture
- 11.11 eBPF‑Based Security Policies

---

## 12‑Supply‑Chain‑Security
- 12.01 Supply Chain Threat Landscape
- 12.02 Image Hardening
- 12.03 Image Registry Security
- 12.04 Vulnerability Scanning (Trivy)
- 12.05 Static Analysis (kubesec)
- 12.06 KubeLinter
- 12.07 SBOM Fundamentals
- 12.08 SBOM Formats & Workflows
- 12.09 Automating SBOM in CI/CD

---

## 13‑Incident‑Response‑and‑Forensics
- 13.01 Kubernetes Incident Response Lifecycle
- 13.02 Detecting Compromised Pods
- 13.03 Containment & Quarantine
- 13.04 Log & Audit Forensics
- 13.05 Post‑Incident Remediation

---

## 14‑Backup‑Disaster‑Recovery‑and‑Resilience
- 14.01 etcd Backup Security
- 14.02 Velero Architecture
- 14.03 Backup Encryption
- 14.04 Restore Security Risks
- 14.05 Ransomware Scenarios

---

## 15‑Compliance‑Governance‑and‑Production‑Readiness
- 15.01 Compliance Frameworks
- 15.02 Threat Modeling Frameworks
- 15.03 Supply Chain Compliance
- 15.04 Automation & Security Tooling
- 15.05 Security Maturity Models
- 15.06 Kubernetes Security Anti‑Patterns
- 15.07 Platform‑Specific Security (EKS / AKS / GKE)
- 15.08 FinSecOps & Resource Abuse Detection

---

## 🎓 Outcome
- KCSA Ready
- CKS Ready
- Production Kubernetes Security Architect Ready

