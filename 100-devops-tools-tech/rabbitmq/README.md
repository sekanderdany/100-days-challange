# RabbitMQ - 100 DevOps Tools Course

## Course Overview

This course provides a comprehensive guide to RabbitMQ, an open-source message broker that implements the Advanced Message Queuing Protocol (AMQP). You'll learn how to build reliable, scalable messaging systems for microservices architectures.

## Course Structure

### Module 00: Foundations of RabbitMQ ✅ COMPLETE
- **00-01:** What Is RabbitMQ and Why It Exists
- **00-02:** AMQP Protocol and Message Structure
- **00-03:** RabbitMQ Management and Monitoring
- **00-04:** Basic Messaging Patterns in RabbitMQ

### Module 01: Core Concepts ✅ COMPLETE
- **01-01:** Exchanges and Their Types
- **01-02:** Queues and Queue Properties
- **01-03:** Bindings and Routing Keys
- **01-04:** Virtual Hosts, Users and Permissions

### Module 02: Advanced RabbitMQ Features
- **02-01:** Message Acknowledgment and Reliability
- **02-02:** Publisher Confirms
- **02-03:** Dead Letter Exchanges (DLX)
- **02-04:** Message TTL and Expiration
- **02-05:** Consumer Prefetch and Fair Dispatch
- **02-06:** Message Durability and Persistence
- **02-07:** Transactionality and Atomic Operations

### Module 03: Clustering and High Availability
- **03-01:** RabbitMQ Clustering Fundamentals
- **03-02:** Mirror Queues vs Classic Queues
- **03-03:** Quorum Queues (Modern Approach)
- **03-04:** Federation and Shovel
- **03-05:** High Availability Patterns
- **03-06:** Load Balancing and Consumer Scaling
- **03-07:** Disaster Recovery and Backup

### Module 04: Performance and Tuning
- **04-01:** Performance Optimization Strategies
- **04-02:** Connection and Channel Management
- **04-03:** Memory and Disk Tuning
- **04-04:** Flow Control and Rate Limiting
- **04-05:** Lazy Queues and Disk I/O
- **04-06:** Monitoring and Alerting Setup
- **04-07:** Benchmarking and Capacity Planning

### Module 05: Security Best Practices
- **05-01:** Authentication and Authorization
- **05-02:** Network Security (SSL/TLS)
- **05-03:** Secrets Management (Vault Integration)
- **05-04:** Least Privilege Access Control
- **05-05:** Security Auditing and Compliance
- **05-06:** DDoS Protection and Rate Limiting
- **05-07:** Secure Deployment Patterns

### Module 06: Integration Patterns
- **06-01:** Request-Reply (RPC) Pattern
- **06-02:** Event-Driven Architecture
- **06-03:** Microservices Communication
- **06-04:** Retry and Circuit Breaker Patterns
- **06-05:** Saga Pattern for Distributed Transactions
- **06-06:** CQRS (Command Query Responsibility) with RabbitMQ
- **06-07:** Event Sourcing and Event Store

### Module 07: DevOps Automation
- **07-01:** Docker and Kubernetes Deployment
- **07-02:** Infrastructure as Code with Terraform
- **07-03:** CI/CD Integration with RabbitMQ
- **07-04:** Monitoring Stack (Prometheus, Grafana, Alertmanager)
- **07-05:** Log Aggregation and Analysis
- **07-06:** Automated Scaling (HPA, KEDA)
- **07-07:** Chaos Engineering with RabbitMQ

### Module 08: Troubleshooting and Debugging
- **08-01:** Common Issues and Solutions
- **08-02:** Connection and Channel Problems
- **08-03:** Memory and Disk Issues
- **08-04:** Performance Bottlenecks
- **08-05:** Message Routing Debugging
- **08-06:** Consumer Lag Detection
- **08-07:** Cluster Troubleshooting
- **08-08:** Tools and Techniques for Debugging

### Module 09: Capstone Projects
- **09-01:** E-Commerce Order Processing System
- **09-02:** Real-Time Notification Service
- **09-03:** Event-Driven Microservices Platform
- **09-04:** Distributed Task Processing System
- **09-05:** Message Analytics Pipeline
- **09-06:** Multi-Region Messaging System

---

## Prerequisites

Before starting this course, you should have:

- Basic understanding of messaging concepts
- Familiarity with at least one programming language (Python recommended)
- Docker installed (for running RabbitMQ in containers)
- Basic knowledge of command line operations

---

## Recommended Setup

### Local Development

```bash
# Install Docker
# Start RabbitMQ with Management Plugin
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

### Install Python Client

```bash
# Install Pika (Python AMQP client)
pip install pika
```

---

## Course Progress

- [x] Module 00 - Foundations of RabbitMQ
- [x] Module 01 - Core Concepts
- [ ] Module 02 - Advanced RabbitMQ Features (IN PROGRESS)
- [ ] Module 03 - Clustering and High Availability
- [ ] Module 04 - Performance and Tuning
- [ ] Module 05 - Security Best Practices
- [ ] Module 06 - Integration Patterns
- [ ] Module 07 - DevOps Automation
- [ ] Module 08 - Troubleshooting and Debugging
- [ ] Module 09 - Capstone Projects

---

## Additional Resources

- [RabbitMQ Official Documentation](https://www.rabbitmq.com/documentation)
- [RabbitMQ GitHub Repository](https://github.com/rabbitmq/rabbitmq-server)
- [Pika Python Client Documentation](https://pika.readthedocs.io/)
- [RabbitMQ Management Plugin Guide](https://www.rabbitmq.com/management.html)

---

**Course Start Date:** January 26, 2026  
**Last Updated:** January 26, 2026