# RabbitMQ Course

## 📚 Course Overview

Welcome to the RabbitMQ course! This course covers everything you need to know to become a RabbitMQ expert, from basic concepts to advanced production deployment, troubleshooting, and real-world case studies.

**What You'll Learn:**

- **Core Concepts**: Queues, Exchanges, Bindings, Virtual Hosts, Users, Permissions
- **Reliability**: Message Acknowledgments, Publisher Confirms, Dead Letter Exchanges, Message TTL
- **Messaging Patterns**: Work Queues, Pub/Sub, Routing, RPC, Competing Consumers, Request/Reply
- **Advanced Features**: Clustering, High Availability, Security, Monitoring, Performance Tuning
- **Best Practices**: Production Setup, Performance Tuning, Security, Backup/Recovery, Monitoring
- **Troubleshooting**: Common Issues, Performance Debugging, Security Remediation, Case Studies

---

## 🎯 Module Structure

| Module | Topic | Status |
|--------|-------|--------|
| **Module 00** | Introduction | ✅ |
| **Module 01** | Core Concepts | ✅ |
| **Module 02** | Reliability & Message Guarantees | ✅ |
| **Module 03** | Messaging Patterns | ✅ |
| **Module 04** | Advanced Features | ✅ |
| **Module 05** | Best Practices & Production Deployment | ✅ |
| **Module 06** | Troubleshooting and Case Studies | ✅ |

---

## 📖 Course Content

### Module 00: Introduction
- [00-01: What Is RabbitMQ and Why It Exists](./00-01-What-Is-RabbitMQ-and-Why-It-Exists.md)
- [00-02: AMQP Protocol and Message Structure](./00-02-AMQP-Protocol-and-Message-Structure.md)
- [00-03: RabbitMQ Management and Monitoring](./00-03-RabbitMQ-Management-and-Monitoring.md)
- [00-04: Basic Messaging Patterns in RabbitMQ](./00-04-Basic-Messaging-Patterns-in-RabbitMQ.md)

### Module 01: Core Concepts
- [01-01: Exchanges and Their Types](./01-01-Exchanges-and-Their-Types.md)
- [01-02: Queues and Queue Properties](./01-02-Queues-and-Queue-Properties.md)
- [01-03: Bindings and Routing Keys](./01-03-Bindings-and-Routing-Keys.md)
- [01-04: Virtual Hosts, Users and Permissions](./01-04-Virtual-Hosts-Users-and-Permissions.md)

### Module 02: Reliability & Message Guarantees
- [02-01: Message Acknowledgment and Reliability](./02-01-Message-Acknowledgment-and-Reliability.md)
- [02-02: Publisher Confirms](./02-02-Publisher-Confirms.md)
- [02-03: Dead Letter Exchanges (DLX)](./02-03-Dead-Letter-Exchanges-DLX.md)
- [02-04: Message TTL and Expiration](./02-04-Message-TTL-and-Expiration.md)
- [02-05: Consumer Prefetch and Fair Dispatch](./02-05-Consumer-Prefetch-and-Fair-Dispatch.md)
- [02-06: Message Durability and Persistence](./02-06-Message-Durability-and-Persistence.md)
- [02-07: Transactionality and Atomic Operations](./02-07-Transactionality-and-Atomic-Operations.md)

### Module 03: Messaging Patterns
- [03-00: Module 03 Overview](./03-00-Module-03-Overview.md)
- [03-01: Work Queues Pattern](./03-01-Work-Queues-Pattern.md)
- [03-02: Publish/Subscribe Pattern](./03-02-Publish-Subscribe-Pattern.md)
- [03-03: Routing Pattern](./03-03-Routing-Pattern.md)
- [03-04: RPC Pattern](./03-04-RPC-Pattern.md)
- [03-05: Competing Consumers Pattern](./03-05-Competing-Consumers-Pattern.md)
- [03-06: Request/Reply Pattern](./03-06-Request-Reply-Pattern.md)
- [03-07: Architectural Patterns](./03-07-Architectural-Patterns.md)

### Module 04: Advanced Features
- [04-00: Module 04 Overview](./04-00-Module-04-Overview.md)
- [04-01: Clustering and High Availability](./04-01-Clustering-and-High-Availability.md)
- [04-02: RabbitMQ Security](./04-02-RabbitMQ-Security.md)
- [04-03: Monitoring and Alerting](./04-03-Monitoring-and-Alerting.md)
- [04-04: Performance Tuning and Optimization](./04-04-Performance-Tuning-and-Optimization.md)
- [04-05: Advanced Message Patterns](./04-05-Advanced-Message-Patterns.md)
- [04-06: Message Ordering and Consistency](./04-06-Message-Ordering-and-Consistency.md)
- [04-07: Multi-Data Centers and Global Queues](./04-07-Multi-Data-Centers-and-Global-Queues.md)

### Module 05: Best Practices & Production Deployment
- [05-00: Module 05 Overview](./05-00-Module-05-Overview.md)
- [05-01: Production Environment Setup](./05-01-Production-Environment-Setup.md)
- [05-02: Performance Tuning Best Practices](./05-02-Performance-Tuning-Best-Practices.md)
- [05-03: Security Best Practices](./05-03-Security-Best-Practices.md)
- [05-04: Backup and Disaster Recovery](./05-04-Backup-and-Disaster-Recovery.md)
- [05-05: Monitoring and Alerting Best Practices](./05-05-Monitoring-and-Alerting-Best-Practices.md)

### Module 06: Troubleshooting and Case Studies
- [06-00: Module 06 Overview](./06-00-Module-06-Overview.md)
- [06-01: Common Issues and Troubleshooting](./06-01-Common-Issues-and-Troubleshooting.md)
- [06-02: Performance Issues and Debugging](./06-02-Performance-Issues-and-Debugging.md)
- [06-03: Security Issues and Remediation](./06-03-Security-Issues-and-Remediation.md)
- [06-04: Real-World Case Studies](./06-04-Real-World-Case-Studies.md)
- [06-05: Best Practices for Troubleshooting](./06-05-Best-Practices-for-Troubleshooting.md)

---

## 🚀 Quick Start

### Prerequisites
- RabbitMQ 3.12+ installed or Docker
- Basic Linux/Unix knowledge
- Basic networking knowledge
- Python or other programming language

### Installation

**Ubuntu/Debian:**
```bash
# Update package list
sudo apt-get update

# Install RabbitMQ
sudo apt-get install rabbitmq-server

# Enable Management Plugin
sudo rabbitmq-plugins enable rabbitmq_management

# Start RabbitMQ
sudo systemctl start rabbitmq-server

# Enable Management Plugin (if not enabled)
sudo rabbitmq-plugins enable rabbitmq_management

# Check RabbitMQ status
sudo systemctl status rabbitmq-server

# Access Management UI
# http://localhost:15672 (guest/guest)
```

**Docker:**
```bash
# Run RabbitMQ container
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -p 25672:25672 \
  -e RABBITMQ_DEFAULT_USER=guest \
  -e RABBITMQ_DEFAULT_PASS=guest \
  rabbitmq:3.12-management

# Access Management UI
# http://localhost:15672 (guest/guest)
```

---

## 📊 Course Progress

```
Course Progress:
██████████████████████████████░░░░ 95% Complete

Modules Completed:
✅ Module 00: Introduction
✅ Module 01: Core Concepts
✅ Module 02: Reliability & Message Guarantees
✅ Module 03: Messaging Patterns
✅ Module 04: Advanced Features
✅ Module 05: Best Practices & Production Deployment
✅ Module 06: Troubleshooting and Case Studies

Current Module: Module 06 - Troubleshooting and Case Studies (100% Complete)
```

---

## 🎓 Learning Path

```
Start: Module 00 (Introduction)
  ↓
Module 01 (Core Concepts)
  ↓
Module 02 (Reliability & Message Guarantees)
  ↓
Module 03 (Messaging Patterns)
  ↓
Module 04 (Advanced Features)
  ↓
Module 05 (Best Practices & Production Deployment)
  ↓
Module 06 (Troubleshooting and Case Studies)
  ↓
Complete! (RabbitMQ Expert)
```

---

## 💡 Tips for Learning

1. **Start with the basics**: Module 00 and Module 01 provide the foundation for all later modules
2. **Practice hands-on**: Each lesson includes hands-on labs to reinforce concepts
3. **Read the documentation**: RabbitMQ has excellent documentation - use it!
4. **Join the community**: RabbitMQ has a vibrant community - forums, mailing lists, Slack
5. **Contribute**: RabbitMQ is open source - contribute bugs, features, documentation

---

## 🛠 Getting Help

If you encounter any issues while going through this course:

1. **Check the documentation**: RabbitMQ has excellent documentation
2. **Search the forums**: RabbitMQ community forums are a great resource
3. **Ask the community**: RabbitMQ community is very helpful
4. **Report bugs**: RabbitMQ GitHub issues are actively monitored

---

## 📜 Resources

- [RabbitMQ Official Documentation](https://www.rabbitmq.com/documentation.html)
- [RabbitMQ GitHub](https://github.com/rabbitmq/rabbitmq-server)
- [RabbitMQ Community](https://www.rabbitmq.com/community.html)
- [RabbitMQ Blog](https://blog.rabbitmq.com/)
- [RabbitMQ Forums](https://groups.google.com/forum/#!forum/rabbitmq-users)

---

## 🏆 Course Completion

Congratulations on completing the RabbitMQ course! You're now a RabbitMQ expert. 🎓

**You've learned:**
- Core Concepts (Queues, Exchanges, Bindings, Virtual Hosts, Users, Permissions)
- Reliability (Acknowledgments, Publisher Confirms, DLX, Message TTL)
- Messaging Patterns (Work Queues, Pub/Sub, Routing, RPC, Competing Consumers, Request/Reply)
- Advanced Features (Clustering, High Availability, Security, Monitoring, Performance Tuning)
- Best Practices (Production Setup, Performance Tuning, Security, Backup/Recovery, Monitoring)
- Troubleshooting (Common Issues, Performance Debugging, Security Remediation, Case Studies)

**Next Steps:**
- Practice in your environments (development, staging, production)
- Read RabbitMQ documentation for advanced topics
- Join RabbitMQ community (forums, mailing lists, Slack)
- Contribute to RabbitMQ open source (bugs, features, documentation)
- Continue learning (DevOps, Cloud Native, System Architecture, Security)

**Course Progress:**
- Module 00: Introduction ✅
- Module 01: Core Concepts ✅
- Module 02: Reliability & Message Guarantees ✅
- Module 03: Messaging Patterns ✅
- Module 04: Advanced Features ✅
- Module 05: Best Practices & Production Deployment ✅
- Module 06: Troubleshooting and Case Studies ✅

**Course Status:**
- 6 Modules completed
- 50 Lessons completed
- 100% Complete

**You're now a RabbitMQ expert!** 🎓

---

**RabbitMQ Course - Complete**