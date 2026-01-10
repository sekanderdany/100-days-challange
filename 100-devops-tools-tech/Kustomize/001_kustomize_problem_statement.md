# Kustomize Problem Statement

## Why Do We Need Kustomize?

When working with Kubernetes, we often need to deploy the same application across multiple environments (development, staging, production). Each environment typically requires different configurations:

- **Different image tags** (dev, staging, production versions)
- **Different resource limits** (smaller in dev, larger in prod)
- **Different replica counts** (1 in dev, 10 in prod)
- **Different environment variables** (database URLs, API keys)
- **Different ingress hosts** (dev.example.com, prod.example.com)

## The Traditional Problem

Without Kustomize, teams typically face these challenges:

### 1. **Copy-Paste Hell**
```bash
# Multiple similar files for different environments
deployment-dev.yaml
deployment-staging.yaml
deployment-prod.yaml
service-dev.yaml
service-staging.yaml
service-prod.yaml
```

This leads to:
- Code duplication
- Difficult maintenance
- High risk of inconsistencies
- Hard to track changes across environments

### 2. **Manual Find-Replace**
Manually editing YAML files for each environment:
```yaml
# Manually changing values for each deployment
replicas: 3  # Remember to change this for each environment!
image: myapp:v1.0.0  # Don't forget to update this!
```

This causes:
- Human errors
- Time-consuming deployments
- Inconsistent configurations

### 3. **Complex Templating**
Using tools like `sed`, `envsubst`, or custom scripts:
```bash
sed -i 's/IMAGE_TAG/v1.0.0/g' deployment.yaml
sed -i 's/REPLICAS/3/g' deployment.yaml
```

Problems:
- Not Kubernetes-native
- Hard to debug
- Fragile and error-prone
- Poor version control

## What Kustomize Solves

Kustomize provides a **template-free** way to customize Kubernetes configurations:

### ✅ **DRY Principle (Don't Repeat Yourself)**
- Maintain one base configuration
- Apply environment-specific changes as overlays
- No code duplication

### ✅ **Declarative Configuration**
- Pure YAML, no templates
- Easy to read and understand
- Works seamlessly with kubectl

### ✅ **Environment Management**
```
base/                    # Common configuration
├── deployment.yaml
├── service.yaml
└── kustomization.yaml

overlays/
├── dev/                # Dev-specific changes
│   └── kustomization.yaml
├── staging/            # Staging-specific changes
│   └── kustomization.yaml
└── prod/               # Production-specific changes
    └── kustomization.yaml
```

### ✅ **Built into kubectl**
```bash
# No additional installation needed
kubectl apply -k overlays/dev/
kubectl apply -k overlays/prod/
```

## Real-World Example

**Without Kustomize:**
```yaml
# deployment-dev.yaml (1 of 3 copies)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.19-dev
        resources:
          limits:
            memory: "128Mi"
            cpu: "100m"

# deployment-prod.yaml (manual copy with changes)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 10
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.19
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**With Kustomize:**
```yaml
# base/deployment.yaml (one source of truth)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.19

# overlays/prod/kustomization.yaml (only the differences)
bases:
- ../../base
replicas:
- name: nginx-deployment
  count: 10
images:
- name: nginx
  newTag: 1.19
patchesStrategicMerge:
- resources.yaml
```

## Key Benefits

| Challenge | Kustomize Solution |
|-----------|-------------------|
| Multiple environment configs | Base + Overlays pattern |
| Image tag management | Image transformer |
| Resource customization | Patches and transformers |
| Name prefixes/suffixes | Built-in transformers |
| Label management | Common labels transformer |
| Configuration reuse | Components and bases |

## When to Use Kustomize

✅ **Perfect for:**
- Managing multiple Kubernetes environments
- Customizing third-party applications
- GitOps workflows
- CI/CD pipelines
- Simple to medium complexity deployments

⚠️ **Consider alternatives when:**
- You need complex logic and conditionals (use Helm)
- You require package management features
- You need to share applications as packages

## Next Steps

In the following tutorials, we'll learn:
1. How Kustomize compares to Helm
2. How to install and use Kustomize
3. Core concepts and features
4. Hands-on labs with real examples

Let's dive in! 🚀
