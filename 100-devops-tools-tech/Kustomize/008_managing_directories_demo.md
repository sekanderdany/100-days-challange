# Managing Directories Demo

## Overview

In this demo, we'll create a complete Kustomize project with a base configuration and three overlays (dev, staging, production). You'll see how directory management works in practice.

## Demo Setup

We'll build a simple Nginx web application that's deployed across three environments with different configurations.

## Step 1: Project Initialization

```bash
# Create project structure
mkdir -p nginx-app/base
mkdir -p nginx-app/overlays/{dev,staging,prod}
cd nginx-app
```

**Resulting structure:**
```
nginx-app/
├── base/
└── overlays/
    ├── dev/
    ├── staging/
    └── prod/
```

## Step 2: Create Base Configuration

### Create Base Deployment

**base/deployment.yaml:**
```bash
cat > base/deployment.yaml << 'EOF'
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
EOF
```

### Create Base Service

**base/service.yaml:**
```bash
cat > base/service.yaml << 'EOF'
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
EOF
```

### Create Base Kustomization

**base/kustomization.yaml:**
```bash
cat > base/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

commonLabels:
  app: nginx
  managed-by: kustomize
EOF
```

## Step 3: Verify Base Configuration

```bash
# View the base output
kubectl kustomize base/

# Expected: deployment and service with common labels
```

**Output:**
```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: nginx
    managed-by: kustomize
  name: nginx
spec:
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: nginx
    managed-by: kustomize
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx
    managed-by: kustomize
  name: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
      managed-by: kustomize
  template:
    metadata:
      labels:
        app: nginx
        managed-by: kustomize
    spec:
      containers:
      - image: nginx:1.19
        name: nginx
        ports:
        - containerPort: 80
        resources:
          limits:
            cpu: 200m
            memory: 128Mi
          requests:
            cpu: 100m
            memory: 64Mi
```

## Step 4: Create Development Overlay

**overlays/dev/kustomization.yaml:**
```bash
cat > overlays/dev/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: development

namePrefix: dev-

commonLabels:
  environment: dev
  team: development

replicas:
- name: nginx
  count: 1

images:
- name: nginx
  newTag: "1.19-alpine"
EOF
```

### Test Dev Overlay

```bash
# Build dev configuration
kubectl kustomize overlays/dev/

# Notice the changes:
# - Namespace: development
# - Name: dev-nginx
# - Labels: environment: dev
# - Image: nginx:1.19-alpine
```

## Step 5: Create Staging Overlay

**overlays/staging/kustomization.yaml:**
```bash
cat > overlays/staging/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: staging

namePrefix: staging-

commonLabels:
  environment: staging
  team: platform

replicas:
- name: nginx
  count: 3

images:
- name: nginx
  newTag: "1.20"
EOF
```

### Test Staging Overlay

```bash
kubectl kustomize overlays/staging/

# Notice:
# - Namespace: staging
# - Name: staging-nginx
# - Replicas: 3
# - Image: nginx:1.20
```

## Step 6: Create Production Overlay

**overlays/prod/kustomization.yaml:**
```bash
cat > overlays/prod/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: production

namePrefix: prod-

commonLabels:
  environment: production
  team: platform
  criticality: high

commonAnnotations:
  monitoring: "true"
  backup: "true"

replicas:
- name: nginx
  count: 10

images:
- name: nginx
  newTag: "1.21"

patchesStrategicMerge:
- resources-patch.yaml
EOF
```

### Create Production Resource Patch

**overlays/prod/resources-patch.yaml:**
```bash
cat > overlays/prod/resources-patch.yaml << 'EOF'
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
EOF
```

### Test Production Overlay

```bash
kubectl kustomize overlays/prod/

# Notice:
# - Namespace: production
# - Name: prod-nginx
# - Replicas: 10
# - Image: nginx:1.21
# - Enhanced resources
# - Additional annotations
```

## Step 7: Compare All Environments

### View All Environments

```bash
echo "=== DEV ENVIRONMENT ==="
kubectl kustomize overlays/dev/ | grep -E "name:|namespace:|replicas:|image:"

echo ""
echo "=== STAGING ENVIRONMENT ==="
kubectl kustomize overlays/staging/ | grep -E "name:|namespace:|replicas:|image:"

echo ""
echo "=== PRODUCTION ENVIRONMENT ==="
kubectl kustomize overlays/prod/ | grep -E "name:|namespace:|replicas:|image:"
```

### Environment Comparison

| Property | Dev | Staging | Production |
|----------|-----|---------|------------|
| **Namespace** | development | staging | production |
| **Name Prefix** | dev- | staging- | prod- |
| **Replicas** | 1 | 3 | 10 |
| **Image Tag** | 1.19-alpine | 1.20 | 1.21 |
| **Memory Request** | 64Mi | 64Mi | 256Mi |
| **Memory Limit** | 128Mi | 128Mi | 512Mi |
| **CPU Request** | 100m | 100m | 500m |
| **CPU Limit** | 200m | 200m | 1000m |

## Step 8: Apply to Cluster (Optional)

### Create Namespaces

```bash
kubectl create namespace development
kubectl create namespace staging
kubectl create namespace production
```

### Deploy to Dev

```bash
kubectl apply -k overlays/dev/

# Verify
kubectl get all -n development
```

### Deploy to Staging

```bash
kubectl apply -k overlays/staging/

# Verify
kubectl get all -n staging
```

### Deploy to Production

```bash
kubectl apply -k overlays/prod/

# Verify
kubectl get all -n production
```

## Step 9: Update Base and See Propagation

Let's update the base deployment and see it affect all environments:

**Modify base/deployment.yaml** - Add environment variable:
```bash
cat > base/deployment.yaml << 'EOF'
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
        env:
        - name: NGINX_VERSION
          value: "BASE"
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
EOF
```

### Rebuild All Environments

```bash
# Dev now has the env variable
kubectl kustomize overlays/dev/ | grep -A 2 "env:"

# Staging has it too
kubectl kustomize overlays/staging/ | grep -A 2 "env:"

# Production has it as well
kubectl kustomize overlays/prod/ | grep -A 2 "env:"
```

**Result:** One change in base automatically propagates to all overlays! 🎉

## Step 10: Clean Up

```bash
# Delete from all environments
kubectl delete -k overlays/dev/
kubectl delete -k overlays/staging/
kubectl delete -k overlays/prod/

# Delete namespaces
kubectl delete namespace development staging production
```

## Final Directory Structure

```
nginx-app/
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
        ├── kustomization.yaml
        └── resources-patch.yaml
```

## Key Takeaways

1. **Single Source of Truth**: Base contains common configuration
2. **DRY Principle**: No duplicate YAML files
3. **Easy Updates**: Change base once, affects all overlays
4. **Environment Isolation**: Each overlay is independent
5. **Clear Structure**: Easy to understand and maintain

## Common Operations

### View Specific Environment
```bash
kubectl kustomize overlays/dev/
kubectl kustomize overlays/staging/
kubectl kustomize overlays/prod/
```

### Apply Specific Environment
```bash
kubectl apply -k overlays/dev/
kubectl apply -k overlays/staging/
kubectl apply -k overlays/prod/
```

### Dry Run Before Apply
```bash
kubectl apply -k overlays/prod/ --dry-run=client -o yaml
```

### Show Diff
```bash
kubectl diff -k overlays/prod/
```

## Workflow Summary

```
1. Create base configuration (common resources)
   ↓
2. Create overlays for each environment
   ↓
3. Test with: kubectl kustomize overlays/<env>/
   ↓
4. Apply with: kubectl apply -k overlays/<env>/
   ↓
5. Update base when needed (changes propagate to all overlays)
```

## Demo Commands Reference

```bash
# Project setup
mkdir -p nginx-app/base nginx-app/overlays/{dev,staging,prod}

# Create base files
# (deployment.yaml, service.yaml, kustomization.yaml)

# Test base
kubectl kustomize base/

# Create overlay files
# (overlays/dev/kustomization.yaml, etc.)

# Test overlays
kubectl kustomize overlays/dev/
kubectl kustomize overlays/staging/
kubectl kustomize overlays/prod/

# Apply to cluster
kubectl apply -k overlays/dev/
kubectl apply -k overlays/staging/
kubectl apply -k overlays/prod/

# Clean up
kubectl delete -k overlays/dev/
kubectl delete -k overlays/staging/
kubectl delete -k overlays/prod/
```

## Next Steps

You've seen directory management in action! Now let's practice with a hands-on lab where you'll:
- Create your own base configuration
- Build multiple overlays
- Apply patches
- Test different scenarios

Ready for the lab? Let's go! 🚀
