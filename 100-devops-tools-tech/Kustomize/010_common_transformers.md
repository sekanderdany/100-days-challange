# Common Transformers

## What are Transformers?

Transformers are Kustomize features that modify Kubernetes resources in a consistent and predictable way. They apply changes across all resources without requiring you to edit individual files.

Think of transformers as "global find-and-replace" operations that work across your entire configuration.

## Types of Common Transformers

Kustomize provides several built-in transformers:

| Transformer | Purpose | Example |
|-------------|---------|---------|
| **commonLabels** | Add labels to all resources | `app: myapp` |
| **commonAnnotations** | Add annotations to all resources | `version: "1.0"` |
| **namespace** | Set namespace for all resources | `production` |
| **namePrefix** | Add prefix to all resource names | `prod-` |
| **nameSuffix** | Add suffix to all resource names | `-v1` |
| **replicas** | Set replica count for deployments | `count: 5` |

## 1. commonLabels

Adds labels to **all** resources and their selectors.

### Syntax
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

commonLabels:
  app: myapp
  team: platform
  environment: production
```

### Example

**Input deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
```

**After applying commonLabels:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: myapp
    team: platform
    environment: production
spec:
  selector:
    matchLabels:
      app: nginx
      team: platform
      environment: production
  template:
    metadata:
      labels:
        app: nginx
        team: platform
        environment: production
```

### Important Notes

- ✅ Adds labels to metadata
- ✅ Adds labels to spec.selector.matchLabels
- ✅ Adds labels to spec.template.metadata.labels
- ⚠️ Can override existing labels with the same key

### Use Cases
- Environment identification (`environment: prod`)
- Team ownership (`team: platform`)
- Cost tracking (`cost-center: engineering`)
- Application grouping (`app: myapp`)

## 2. commonAnnotations

Adds annotations to all resources (metadata only, not selectors).

### Syntax
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

commonAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "9090"
  version: "1.0.0"
  managed-by: "kustomize"
```

### Example

**Input:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
```

**Output:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
    version: "1.0.0"
    managed-by: "kustomize"
```

### Difference from Labels

| Feature | Labels | Annotations |
|---------|--------|-------------|
| Selectable | ✅ Yes | ❌ No |
| Size Limit | 63 characters | Unlimited |
| Used for | Selection, grouping | Metadata, config |
| Added to selectors | ✅ Yes | ❌ No |

### Use Cases
- Monitoring configuration
- Deployment tracking
- Version information
- Tool configuration

## 3. namespace

Sets the namespace for all resources.

### Syntax
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

namespace: production
```

### Example

**Input:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
# No namespace specified
```

**Output:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: production
```

### Important Notes

- ✅ Adds namespace to all namespaced resources
- ✅ Skips cluster-scoped resources (ClusterRole, etc.)
- ✅ Overrides existing namespace if present

### Use Cases
- Multi-environment deployments
- Tenant isolation
- Environment separation

## 4. namePrefix

Adds a prefix to all resource names.

### Syntax
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

namePrefix: prod-
```

### Example

**Input:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
---
apiVersion: v1
kind: Service
metadata:
  name: nginx
```

**Output:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prod-nginx
---
apiVersion: v1
kind: Service
metadata:
  name: prod-nginx
```

### Important Notes

- ✅ Updates all resource names
- ✅ Updates references (Service selectors, etc.)
- ✅ Maintains consistency across references

### Use Cases
- Environment prefixing (`dev-`, `prod-`)
- Version identification (`v1-`, `v2-`)
- Team prefixing (`team-a-`)

## 5. nameSuffix

Adds a suffix to all resource names.

### Syntax
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

nameSuffix: -v2
```

### Example

**Input:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
```

**Output:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-v2
```

### Use Cases
- Version suffixes (`-v1`, `-v2`)
- Deployment variants (`-canary`, `-stable`)
- Feature branches (`-feature-x`)

## 6. replicas

Sets the replica count for Deployments and StatefulSets.

### Syntax
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

replicas:
- name: nginx
  count: 5
```

### Example

**Input:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 1
```

**Output:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 5
```

### Multiple Deployments
```yaml
replicas:
- name: nginx
  count: 5
- name: redis
  count: 3
- name: postgres
  count: 1
```

### Use Cases
- Environment-specific scaling
- Production vs development
- Load testing scenarios

## Combining Transformers

You can use multiple transformers together:

### Example: Complete Configuration

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

namespace: production

namePrefix: prod-

commonLabels:
  app: myapp
  environment: production
  team: platform

commonAnnotations:
  managed-by: kustomize
  version: "2.0.0"
  prometheus.io/scrape: "true"

replicas:
- name: myapp
  count: 10
```

### Result

**Input deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 1
```

**Output:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prod-myapp
  namespace: production
  labels:
    app: myapp
    environment: production
    team: platform
  annotations:
    managed-by: kustomize
    version: "2.0.0"
    prometheus.io/scrape: "true"
spec:
  replicas: 10
  selector:
    matchLabels:
      app: myapp
      environment: production
      team: platform
```

## Transformer Order

Transformers are applied in this order:
1. namespace
2. namePrefix / nameSuffix
3. commonLabels
4. commonAnnotations
5. replicas

## Best Practices

### 1. Use Meaningful Labels
```yaml
# Good
commonLabels:
  app: nginx
  environment: production
  team: platform

# Avoid
commonLabels:
  label1: value1
  label2: value2
```

### 2. Keep Prefixes/Suffixes Short
```yaml
# Good
namePrefix: prod-

# Avoid (too long)
namePrefix: production-environment-
```

### 3. Use Annotations for Non-Selectable Data
```yaml
# Use annotations for metadata
commonAnnotations:
  build-date: "2024-01-10"
  git-commit: "abc123"
  
# Use labels for selection
commonLabels:
  app: myapp
  version: v1
```

### 4. Set Namespace in Overlays, Not Base
```yaml
# base/kustomization.yaml - NO namespace
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml

# overlays/prod/kustomization.yaml - YES namespace
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../base
namespace: production
```

## Real-World Example

### Base Configuration
```yaml
# base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

commonLabels:
  app: webapp
  managed-by: kustomize
```

### Development Overlay
```yaml
# overlays/dev/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: development
namePrefix: dev-

commonLabels:
  environment: dev

replicas:
- name: webapp
  count: 1
```

### Production Overlay
```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: production
namePrefix: prod-

commonLabels:
  environment: production
  criticality: high

commonAnnotations:
  monitoring: enabled
  backup: enabled

replicas:
- name: webapp
  count: 10
```

## Quick Reference

| Transformer | Syntax | Applies To |
|-------------|--------|------------|
| commonLabels | `key: value` | All resources + selectors |
| commonAnnotations | `key: value` | All resources (metadata only) |
| namespace | `production` | All namespaced resources |
| namePrefix | `prod-` | All resource names |
| nameSuffix | `-v1` | All resource names |
| replicas | `name: webapp, count: 5` | Deployments, StatefulSets |

## Next Steps

Now you understand common transformers:
- ✅ Labels and annotations
- ✅ Namespace transformation
- ✅ Name prefixes and suffixes
- ✅ Replica management

Next, we'll learn about **image transformers** - a powerful way to manage container images! 🚀
