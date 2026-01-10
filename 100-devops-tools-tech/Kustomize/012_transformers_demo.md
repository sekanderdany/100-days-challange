# Transformers Demo

## Overview

In this demo, we'll combine common transformers and image transformers to create a complete multi-environment deployment. You'll see how these transformers work together in practice.

## Demo Scenario

We're deploying a web application with:
- **Frontend**: Nginx serving static content
- **Backend**: Custom application container
- **Three Environments**: Dev, Staging, Production
- **Different configurations per environment**

## Step 1: Setup Project Structure

```bash
mkdir -p transformers-demo/base
mkdir -p transformers-demo/overlays/{dev,staging,prod}
cd transformers-demo
```

## Step 2: Create Base Deployment

**base/deployment.yaml:**
```bash
cat > base/deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: frontend
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
      - name: backend
        image: busybox:1.30
        command: ["sh", "-c", "while true; do echo Backend running; sleep 3600; done"]
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
EOF
```

**base/service.yaml:**
```bash
cat > base/service.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: webapp
spec:
  selector:
    app: webapp
  ports:
  - name: http
    port: 80
    targetPort: 80
  type: ClusterIP
EOF
```

**base/kustomization.yaml:**
```bash
cat > base/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

commonLabels:
  app: webapp
  managed-by: kustomize
EOF
```

## Step 3: Test Base

```bash
kubectl kustomize base/

# Notice:
# - Default configuration
# - No namespace
# - No environment-specific changes
```

## Step 4: Create Development Overlay

**overlays/dev/kustomization.yaml:**
```bash
cat > overlays/dev/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

# Namespace Transformer
namespace: development

# Name Transformer
namePrefix: dev-

# Common Labels Transformer
commonLabels:
  environment: dev
  tier: frontend
  team: dev-team

# Common Annotations Transformer
commonAnnotations:
  deployed-by: kustomize
  environment-type: development
  cost-center: dev-dept

# Replica Transformer
replicas:
- name: webapp
  count: 1

# Image Transformer
images:
- name: nginx
  newTag: "1.19-alpine"
- name: busybox
  newTag: "1.35"
EOF
```

### Test Dev Overlay

```bash
kubectl kustomize overlays/dev/
```

**Observe the transformations:**
```bash
# Filter specific fields to see changes
kubectl kustomize overlays/dev/ | grep -E "name: |namespace: |environment: |image: |replicas:"
```

## Step 5: Create Staging Overlay

**overlays/staging/kustomization.yaml:**
```bash
cat > overlays/staging/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

# Namespace Transformer
namespace: staging

# Name Transformer
namePrefix: staging-

# Common Labels Transformer
commonLabels:
  environment: staging
  tier: frontend
  team: platform-team

# Common Annotations Transformer
commonAnnotations:
  deployed-by: kustomize
  environment-type: staging
  cost-center: platform-dept
  monitoring: enabled

# Replica Transformer
replicas:
- name: webapp
  count: 3

# Image Transformer
images:
- name: nginx
  newTag: "1.20"
- name: busybox
  newTag: "1.35"
EOF
```

### Test Staging Overlay

```bash
kubectl kustomize overlays/staging/

# Compare with dev
echo "=== DEV ==="
kubectl kustomize overlays/dev/ | grep "replicas:"
echo "=== STAGING ==="
kubectl kustomize overlays/staging/ | grep "replicas:"
```

## Step 6: Create Production Overlay

**overlays/prod/kustomization.yaml:**
```bash
cat > overlays/prod/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

# Namespace Transformer
namespace: production

# Name Transformer
namePrefix: prod-
nameSuffix: -v1

# Common Labels Transformer
commonLabels:
  environment: production
  tier: frontend
  team: platform-team
  criticality: high

# Common Annotations Transformer
commonAnnotations:
  deployed-by: kustomize
  environment-type: production
  cost-center: platform-dept
  monitoring: enabled
  backup: enabled
  sla: "99.9"

# Replica Transformer
replicas:
- name: webapp
  count: 10

# Image Transformer
images:
- name: nginx
  newName: myregistry.io/nginx
  newTag: "1.21"
- name: busybox
  newName: myregistry.io/busybox
  newTag: "1.36"
EOF
```

### Test Production Overlay

```bash
kubectl kustomize overlays/prod/

# Notice the name has both prefix AND suffix:
# prod-webapp-v1
```

## Step 7: Side-by-Side Comparison

```bash
echo "=== DEVELOPMENT ==="
echo "Namespace:"
kubectl kustomize overlays/dev/ | grep "namespace:" | head -1
echo "Deployment Name:"
kubectl kustomize overlays/dev/ | grep "name: dev-" | head -1
echo "Replicas:"
kubectl kustomize overlays/dev/ | grep "replicas:" | head -1
echo "Frontend Image:"
kubectl kustomize overlays/dev/ | grep "image: nginx" | head -1
echo ""

echo "=== STAGING ==="
echo "Namespace:"
kubectl kustomize overlays/staging/ | grep "namespace:" | head -1
echo "Deployment Name:"
kubectl kustomize overlays/staging/ | grep "name: staging-" | head -1
echo "Replicas:"
kubectl kustomize overlays/staging/ | grep "replicas:" | head -1
echo "Frontend Image:"
kubectl kustomize overlays/staging/ | grep "image: nginx" | head -1
echo ""

echo "=== PRODUCTION ==="
echo "Namespace:"
kubectl kustomize overlays/prod/ | grep "namespace:" | head -1
echo "Deployment Name:"
kubectl kustomize overlays/prod/ | grep "name: prod-" | head -1
echo "Replicas:"
kubectl kustomize overlays/prod/ | grep "replicas:" | head -1
echo "Frontend Image:"
kubectl kustomize overlays/prod/ | grep "image:" | head -1
```

## Step 8: Transformer Impact Analysis

### Labels Analysis

```bash
# Show all labels added by commonLabels
echo "=== DEV LABELS ==="
kubectl kustomize overlays/dev/ | yq eval 'select(.kind == "Deployment") | .metadata.labels'

echo "=== STAGING LABELS ==="
kubectl kustomize overlays/staging/ | yq eval 'select(.kind == "Deployment") | .metadata.labels'

echo "=== PROD LABELS ==="
kubectl kustomize overlays/prod/ | yq eval 'select(.kind == "Deployment") | .metadata.labels'
```

### Annotations Analysis

```bash
# Show all annotations
kubectl kustomize overlays/prod/ | grep -A 5 "annotations:"
```

### Image Analysis

```bash
# Compare images across environments
for env in dev staging prod; do
  echo "=== $env ==="
  kubectl kustomize overlays/$env/ | grep "image:" | sort | uniq
  echo ""
done
```

## Step 9: Apply to Cluster (Optional)

**⚠️ Only if you have a cluster available**

```bash
# Create namespaces
kubectl create namespace development
kubectl create namespace staging
kubectl create namespace production

# Apply all environments
kubectl apply -k overlays/dev/
kubectl apply -k overlays/staging/
kubectl apply -k overlays/prod/

# Verify
kubectl get all -n development
kubectl get all -n staging
kubectl get all -n production
```

## Step 10: Verify Transformers

### Check Names

```bash
kubectl get deployments --all-namespaces | grep webapp

# Expected output:
# development   dev-webapp               1/1     1            1
# staging       staging-webapp           3/3     3            3
# production    prod-webapp-v1          10/10   10           10
```

### Check Labels

```bash
kubectl get deployment -n production -o yaml | grep -A 10 "labels:"

# Should see:
# - environment: production
# - criticality: high
# - team: platform-team
```

### Check Images

```bash
kubectl describe deployment -n development | grep "Image:"
kubectl describe deployment -n staging | grep "Image:"
kubectl describe deployment -n production | grep "Image:"
```

## Step 11: Update Base and See Propagation

Add a new label to base:

```bash
cat > base/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

commonLabels:
  app: webapp
  managed-by: kustomize
  version: v2.0.0  # NEW LABEL
EOF
```

### Rebuild all environments

```bash
# New label appears in ALL environments
kubectl kustomize overlays/dev/ | grep "version:"
kubectl kustomize overlays/staging/ | grep "version:"
kubectl kustomize overlays/prod/ | grep "version:"
```

## Step 12: Dynamic Image Updates

Simulate a CI/CD pipeline updating images:

```bash
# Update production image tag
cd overlays/prod
kustomize edit set image nginx=myregistry.io/nginx:1.22

# Check the change
cat kustomization.yaml | grep -A 3 "images:"

# Build and verify
kubectl kustomize .
```

## Step 13: Transformer Precedence Demo

Create a conflict to see precedence:

**Add to overlays/prod/kustomization.yaml:**
```yaml
# Both prefix and suffix
namePrefix: prod-
nameSuffix: -release

# Result will be: prod-webapp-release
```

```bash
kubectl kustomize overlays/prod/ | grep "name: prod-"
# Output: name: prod-webapp-release
```

## Step 14: Clean Up

```bash
# Delete from cluster (if applied)
kubectl delete -k overlays/dev/
kubectl delete -k overlays/staging/
kubectl delete -k overlays/prod/

# Delete namespaces
kubectl delete namespace development staging production
```

## Comparison Table

Fill this table with actual values from your demo:

| Transformer | Development | Staging | Production |
|-------------|-------------|---------|------------|
| **Namespace** | development | staging | production |
| **Name Prefix** | dev- | staging- | prod- |
| **Name Suffix** | (none) | (none) | -v1 |
| **Final Name** | dev-webapp | staging-webapp | prod-webapp-v1 |
| **Replicas** | 1 | 3 | 10 |
| **Nginx Image** | nginx:1.19-alpine | nginx:1.20 | myregistry.io/nginx:1.21 |
| **Backend Image** | busybox:1.35 | busybox:1.35 | myregistry.io/busybox:1.36 |
| **Environment Label** | dev | staging | production |
| **Criticality Label** | (none) | (none) | high |
| **Monitoring Annotation** | (none) | enabled | enabled |
| **Backup Annotation** | (none) | (none) | enabled |

## Key Observations

1. **Single Source of Truth**: Base contains the core configuration
2. **Layered Customization**: Each overlay adds its specific transformations
3. **No File Duplication**: All environments share the same base files
4. **Easy Updates**: Change base once, affects all environments
5. **Clear Intent**: Each transformer has a specific, understandable purpose

## Common Operations

```bash
# View any environment
kubectl kustomize overlays/<env>/

# Apply any environment
kubectl apply -k overlays/<env>/

# Dry run
kubectl apply -k overlays/<env>/ --dry-run=client

# Show diff
kubectl diff -k overlays/<env>/

# Update image
cd overlays/<env>
kustomize edit set image nginx=nginx:newtag
```

## Next Steps

You've seen transformers in action! Key takeaways:
- ✅ Common transformers modify all resources consistently
- ✅ Image transformers simplify container management
- ✅ Transformers can be combined for powerful effects
- ✅ Changes propagate from base to all overlays

Now let's practice with a hands-on lab! 🚀
