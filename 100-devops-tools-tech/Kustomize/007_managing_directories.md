# Managing Directories in Kustomize

## Introduction

One of Kustomize's most powerful features is its ability to organize Kubernetes configurations using a directory structure. This enables:
- **Code Reusability**: Share common configurations across environments
- **Clean Organization**: Separate base configs from environment-specific changes
- **Easy Maintenance**: Update once in base, apply everywhere
- **GitOps Friendly**: Clear version control and code reviews

## The Base and Overlays Pattern

### Concept

The most common directory pattern in Kustomize:

```
my-app/
├── base/                    # Common configuration
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
└── overlays/                # Environment-specific customizations
    ├── dev/
    │   └── kustomization.yaml
    ├── staging/
    │   └── kustomization.yaml
    └── prod/
        └── kustomization.yaml
```

### Base Directory

**Purpose**: Contains the common Kubernetes manifests that are shared across all environments.

**What goes here:**
- Standard deployment configurations
- Service definitions
- ConfigMaps and Secrets templates
- Common resource definitions

**Example: base/kustomization.yaml**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

commonLabels:
  app: myapp
```

### Overlays Directory

**Purpose**: Contains environment-specific customizations that build on top of the base.

**What goes here:**
- Environment-specific resource adjustments
- Different replica counts
- Different image tags
- Environment-specific ConfigMaps
- Namespace configurations

**Example: overlays/prod/kustomization.yaml**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: production
namePrefix: prod-

replicas:
- name: myapp
  count: 10

images:
- name: myapp
  newTag: v2.0.0
```

## Complete Directory Example

### Project Structure
```
webapp/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
└── overlays/
    ├── dev/
    │   ├── kustomization.yaml
    │   └── resources-patch.yaml
    ├── staging/
    │   └── kustomization.yaml
    └── prod/
        ├── kustomization.yaml
        └── replicas-patch.yaml
```

### Base Configuration

**base/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.19
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
```

**base/service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

**base/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

commonLabels:
  app: nginx
  managed-by: kustomize
```

### Dev Overlay

**overlays/dev/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: development

namePrefix: dev-

commonLabels:
  environment: dev

replicas:
- name: nginx
  count: 1

images:
- name: nginx
  newTag: "1.19-alpine"
```

### Staging Overlay

**overlays/staging/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: staging

namePrefix: staging-

commonLabels:
  environment: staging

replicas:
- name: nginx
  count: 3

images:
- name: nginx
  newTag: "1.20"
```

### Production Overlay

**overlays/prod/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: production

namePrefix: prod-

commonLabels:
  environment: production

replicas:
- name: nginx
  count: 10

images:
- name: nginx
  newTag: "1.21"

patchesStrategicMerge:
- replicas-patch.yaml
```

**overlays/prod/replicas-patch.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  template:
    spec:
      containers:
      - name: nginx
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
```

## Using the Directory Structure

### Build for Different Environments

**Development:**
```bash
kubectl kustomize overlays/dev/
```

**Staging:**
```bash
kubectl kustomize overlays/staging/
```

**Production:**
```bash
kubectl kustomize overlays/prod/
```

### Apply to Cluster

**Development:**
```bash
kubectl apply -k overlays/dev/
```

**Production:**
```bash
kubectl apply -k overlays/prod/
```

## Referencing Resources

### Relative Paths

When referencing the base from overlays, use relative paths:

```yaml
# From overlays/dev/kustomization.yaml
resources:
- ../../base  # Go up two directories to base
```

```yaml
# From overlays/prod/subfolder/kustomization.yaml
resources:
- ../../../base  # Go up three directories to base
```

### Multiple Bases

You can reference multiple bases:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base
- ../../common-configs
- ../shared
```

### Remote Resources

Reference resources from Git or URLs:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- https://raw.githubusercontent.com/user/repo/main/base/
- github.com/user/repo/base?ref=v1.0.0
```

## Advanced Directory Patterns

### Pattern 1: Shared Components

```
my-app/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
├── components/
│   ├── monitoring/
│   │   ├── servicemonitor.yaml
│   │   └── kustomization.yaml
│   └── ingress/
│       ├── ingress.yaml
│       └── kustomization.yaml
└── overlays/
    ├── dev/
    │   └── kustomization.yaml
    └── prod/
        └── kustomization.yaml
```

**overlays/prod/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base
- ../../components/monitoring
- ../../components/ingress
```

### Pattern 2: Multi-Application

```
infrastructure/
├── app1/
│   ├── base/
│   └── overlays/
├── app2/
│   ├── base/
│   └── overlays/
└── shared/
    ├── namespace.yaml
    └── kustomization.yaml
```

### Pattern 3: Regional Deployments

```
global-app/
├── base/
├── regions/
│   ├── us-east/
│   │   └── kustomization.yaml
│   ├── us-west/
│   │   └── kustomization.yaml
│   └── eu-central/
│       └── kustomization.yaml
```

## Directory Best Practices

### 1. Keep Base Simple
```yaml
# base/kustomization.yaml - Keep it minimal
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

# Don't add environment-specific configs here!
```

### 2. One Overlay Per Environment
```
overlays/
├── dev/          # One for development
├── staging/      # One for staging  
└── prod/         # One for production
```

### 3. Use Descriptive Names
```
# Good
overlays/production/
overlays/development/
overlays/qa-testing/

# Avoid
overlays/env1/
overlays/env2/
```

### 4. Group Related Resources
```
base/
├── networking/
│   ├── service.yaml
│   └── ingress.yaml
├── workloads/
│   └── deployment.yaml
└── kustomization.yaml
```

### 5. Document Directory Structure
```
# Create a README.md in your project
project/
├── README.md          # Explain directory structure
├── base/
└── overlays/
```

## Common Patterns Summary

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Base + Overlays** | Multi-environment deployments | dev, staging, prod |
| **Components** | Optional features | monitoring, logging |
| **Shared** | Common resources | namespaces, RBAC |
| **Regional** | Geographic deployments | us-east, eu-west |
| **Multi-App** | Microservices | app1, app2, app3 |

## Navigation Commands

```bash
# View base output
kubectl kustomize base/

# View dev overlay output
kubectl kustomize overlays/dev/

# View prod overlay output
kubectl kustomize overlays/prod/

# Apply dev environment
kubectl apply -k overlays/dev/

# Apply prod environment
kubectl apply -k overlays/prod/

# Delete dev environment
kubectl delete -k overlays/dev/
```

## Troubleshooting

### Issue: "unable to find base"
```bash
# Error
Error: unable to find one or more bases: ../../base

# Solution: Check relative path
# From overlays/dev/, base should be at ../../base
ls ../../base/kustomization.yaml
```

### Issue: "no resources found"
```bash
# Error
Error: no resources found

# Solution: Check base kustomization.yaml has resources listed
cat base/kustomization.yaml
```

## Summary

| Concept | Purpose |
|---------|---------|
| **Base** | Common configurations for all environments |
| **Overlays** | Environment-specific customizations |
| **Relative Paths** | Reference base from overlays |
| **Components** | Reusable optional features |
| **Resources** | Include files or directories |

## Next Steps

Now you understand directory management in Kustomize:
- ✅ Base and Overlays pattern
- ✅ Directory structure organization
- ✅ Resource referencing
- ✅ Best practices

Next, we'll see a **live demo** of managing directories with real examples! 🚀
