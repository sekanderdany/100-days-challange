# Overlays

## What are Overlays?

**Overlays** are variations of a base configuration. They allow you to customize Kubernetes resources for different environments without duplicating YAML files.

Think of overlays as **layers on top of a base**:
- Base = Common configuration
- Overlay = Environment-specific customizations

```
base/          ← Common config (1x)
overlays/
  dev/         ← Dev customizations
  staging/     ← Staging customizations
  prod/        ← Production customizations
```

## Why Use Overlays?

### Problem Without Overlays

```yaml
# deployment-dev.yaml
replicas: 1
image: nginx:1.19-alpine

# deployment-staging.yaml
replicas: 3
image: nginx:1.19

# deployment-prod.yaml
replicas: 10
image: nginx:1.19
```

**Issues:**
- ❌ Duplicated configuration
- ❌ Hard to maintain consistency
- ❌ Error-prone updates

### Solution With Overlays

```
base/deployment.yaml       ← Single source of truth
overlays/dev/              ← Only differences
overlays/staging/          ← Only differences
overlays/prod/             ← Only differences
```

**Benefits:**
- ✅ DRY (Don't Repeat Yourself)
- ✅ Easy to update common config
- ✅ Clear differences between environments

## Directory Structure

```
myapp/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
└── overlays/
    ├── dev/
    │   └── kustomization.yaml
    ├── staging/
    │   └── kustomization.yaml
    └── prod/
        └── kustomization.yaml
```

## Base Configuration

**base/deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: webapp
        image: nginx:1.19
        ports:
        - containerPort: 80
```

**base/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml
```

## Development Overlay

**overlays/dev/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: development

namePrefix: dev-

replicas:
- name: webapp
  count: 1

images:
- name: nginx
  newTag: 1.19-alpine
```

**Apply:**

```bash
kubectl kustomize overlays/dev/
```

**Result:**
- Namespace: `development`
- Name: `dev-webapp`
- Replicas: `1`
- Image: `nginx:1.19-alpine`

## Staging Overlay

**overlays/staging/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: staging

namePrefix: staging-

replicas:
- name: webapp
  count: 3

commonLabels:
  environment: staging
```

**Result:**
- Namespace: `staging`
- Name: `staging-webapp`
- Replicas: `3`
- Labels: `environment: staging`

## Production Overlay

**overlays/prod/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: production

namePrefix: prod-

replicas:
- name: webapp
  count: 10

commonLabels:
  environment: production
  tier: frontend

images:
- name: nginx
  newName: my-registry.io/nginx
  newTag: 1.19
```

**Result:**
- Namespace: `production`
- Name: `prod-webapp`
- Replicas: `10`
- Labels: `environment: production`, `tier: frontend`
- Image: `my-registry.io/nginx:1.19`

## Overlay Capabilities

### 1. Transformers

```yaml
# overlays/dev/kustomization.yaml
namespace: dev
namePrefix: dev-
nameSuffix: -v1

replicas:
- name: webapp
  count: 1

images:
- name: nginx
  newTag: alpine

commonLabels:
  env: dev

commonAnnotations:
  managed-by: kustomize
```

### 2. Patches

```yaml
# overlays/prod/kustomization.yaml
resources:
- ../../base

patches:
- target:
    kind: Deployment
    name: webapp
  patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: webapp
    spec:
      template:
        spec:
          containers:
          - name: webapp
            resources:
              requests:
                memory: "512Mi"
                cpu: "500m"
```

### 3. Additional Resources

```yaml
# overlays/prod/kustomization.yaml
resources:
- ../../base
- hpa.yaml           # Prod only
- ingress.yaml       # Prod only
- certificate.yaml   # Prod only
```

### 4. ConfigMap/Secret Generators

```yaml
# overlays/dev/kustomization.yaml
resources:
- ../../base

configMapGenerator:
- name: app-config
  literals:
  - LOG_LEVEL=debug
  - DEBUG=true
```

## Overlays vs Patches

### When to Use Overlays

Use overlays when you need:
- ✅ Environment-specific configurations (dev, staging, prod)
- ✅ Regional deployments (us-east, eu-west)
- ✅ Customer-specific variants (client-a, client-b)
- ✅ Testing variations

### When to Use Patches

Use patches when you need:
- ✅ Small modifications to base
- ✅ Surgical changes to specific fields
- ✅ Precise control over transformations

**Best Practice:** Combine both!

```yaml
# overlays/prod/kustomization.yaml
resources:
- ../../base

# Use transformers for simple changes
namespace: production
replicas:
- name: webapp
  count: 10

# Use patches for complex changes
patches:
- target:
    kind: Deployment
  path: security-patch.yaml
```

## Multiple Overlays

You can create overlays for different purposes:

```
overlays/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── regions/
│   ├── us-east-1/
│   ├── us-west-2/
│   └── eu-west-1/
└── customers/
    ├── customer-a/
    └── customer-b/
```

## Nested Overlays

Overlays can reference other overlays:

```
base/
overlays/
  common-prod/      ← Base production config
  prod-us-east/     ← References common-prod
  prod-eu-west/     ← References common-prod
```

**overlays/prod-us-east/kustomization.yaml:**

```yaml
resources:
- ../common-prod

namespace: prod-us-east

patches:
- target:
    kind: Deployment
  patch: |-
    spec:
      template:
        spec:
          affinity:
            nodeAffinity:
              requiredDuringSchedulingIgnoredDuringExecution:
                nodeSelectorTerms:
                - matchExpressions:
                  - key: region
                    operator: In
                    values:
                    - us-east-1
```

## Example: Complete Multi-Environment Setup

**Base:**

```yaml
# base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml
```

**Dev:**

```yaml
# overlays/dev/kustomization.yaml
resources:
- ../../base

namespace: dev
namePrefix: dev-
replicas:
- name: webapp
  count: 1
images:
- name: nginx
  newTag: alpine
```

**Staging:**

```yaml
# overlays/staging/kustomization.yaml
resources:
- ../../base

namespace: staging
namePrefix: staging-
replicas:
- name: webapp
  count: 3
```

**Production:**

```yaml
# overlays/prod/kustomization.yaml
resources:
- ../../base
- hpa.yaml

namespace: production
namePrefix: prod-
replicas:
- name: webapp
  count: 10

patches:
- target:
    kind: Deployment
  path: prod-patches.yaml
```

## Testing Overlays

```bash
# Preview each overlay
kubectl kustomize overlays/dev/
kubectl kustomize overlays/staging/
kubectl kustomize overlays/prod/

# Compare differences
diff <(kubectl kustomize overlays/dev/) \
     <(kubectl kustomize overlays/prod/)

# Apply
kubectl apply -k overlays/dev/
kubectl apply -k overlays/staging/
kubectl apply -k overlays/prod/
```

## Best Practices

### 1. Keep Base Minimal

Base should contain only common configuration:

```yaml
# ✅ Good base
base/
├── deployment.yaml  (minimal spec)
├── service.yaml
└── kustomization.yaml

# ❌ Bad base
base/
├── deployment-with-prod-resources.yaml
├── hpa.yaml  (not needed in dev)
└── certificate.yaml  (not needed in dev)
```

### 2. Use Descriptive Overlay Names

```
✅ overlays/dev/
✅ overlays/staging/
✅ overlays/production/

❌ overlays/env1/
❌ overlays/env2/
```

### 3. Document Differences

Add README in each overlay:

```markdown
# Production Overlay

## Differences from Base
- 10 replicas (base has 2)
- Production namespace
- Private registry images
- Resource limits increased
- HPA enabled
```

### 4. Use Version Control

```bash
git commit -m "Update prod replicas to 10"
git tag -a prod-v1.2.3 -m "Production release"
```

## Common Patterns

### Pattern 1: Environment-Specific Config

```yaml
# overlays/dev/kustomization.yaml
configMapGenerator:
- name: app-config
  literals:
  - DB_HOST=dev-db.example.com
  - LOG_LEVEL=debug
```

### Pattern 2: Feature Flags

```yaml
# overlays/canary/kustomization.yaml
resources:
- ../../base

replicas:
- name: webapp
  count: 1

commonLabels:
  version: canary
```

### Pattern 3: Regional Deployments

```yaml
# overlays/us-east/kustomization.yaml
resources:
- ../../base

nameSuffix: -use1

patches:
- target:
    kind: Service
  patch: |-
    metadata:
      annotations:
        service.beta.kubernetes.io/aws-load-balancer-type: nlb
```

## Summary

**Overlays** allow you to:
- ✅ Customize base configs for different environments
- ✅ Avoid duplication
- ✅ Maintain consistency
- ✅ Track differences easily

**Key Concepts:**
- Base = Common configuration
- Overlay = Environment-specific customization
- Overlays can use transformers, patches, and additional resources
- Overlays can be nested

**Next:** Practice with the Overlay Lab! 🚀
