# Kustomize Output

## Understanding Kustomize Build Process

Kustomize takes your base Kubernetes manifests and `kustomization.yaml` file, applies all transformations, and produces a final output. This output is standard Kubernetes YAML that can be applied to your cluster.

## How to View Output

### Method 1: Using kubectl (Recommended)
```bash
kubectl kustomize <directory>
```

### Method 2: Using Standalone Kustomize
```bash
kustomize build <directory>
```

### Method 3: Direct Apply (Without Viewing)
```bash
kubectl apply -k <directory>
```

## Example: Simple Output

### Input Files

**deployment.yaml:**
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
```

**kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

namespace: production
namePrefix: prod-

commonLabels:
  environment: production
  team: platform
```

### Output Command
```bash
kubectl kustomize .
```

### Generated Output
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    environment: production
    team: platform
  name: prod-nginx
  namespace: production
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
      environment: production
      team: platform
  template:
    metadata:
      labels:
        app: nginx
        environment: production
        team: platform
    spec:
      containers:
      - image: nginx:1.19
        name: nginx
```

**What Changed:**
- ✅ Name: `nginx` → `prod-nginx` (namePrefix added)
- ✅ Namespace: Added `production`
- ✅ Labels: Added `environment: production` and `team: platform`
- ✅ Selector labels: Updated to match new labels

## Output Characteristics

### 1. **Single Stream Output**
Kustomize outputs all resources in a single YAML stream, separated by `---`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myservice
# ... service spec ...
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mydeployment
# ... deployment spec ...
```

### 2. **Sorted Output**
Resources are sorted by:
1. Namespace
2. Kind (alphabetically)
3. Name

```yaml
# Order: Namespace, ConfigMap, Service, Deployment
apiVersion: v1
kind: Namespace
---
apiVersion: v1
kind: ConfigMap
---
apiVersion: v1
kind: Service
---
apiVersion: apps/v1
kind: Deployment
```

### 3. **Annotations Added**
Kustomize may add metadata annotations:

```yaml
metadata:
  annotations:
    kustomize.config.k8s.io/behavior: create
```

## Viewing Output Options

### Option 1: View in Terminal
```bash
kubectl kustomize .
```

### Option 2: Save to File
```bash
kubectl kustomize . > output.yaml
```

### Option 3: Pipe to kubectl
```bash
kubectl kustomize . | kubectl apply -f -
```

### Option 4: Direct Apply (Preferred)
```bash
kubectl apply -k .
```

## Practical Example: Multiple Resources

### Directory Structure
```
my-app/
├── deployment.yaml
├── service.yaml
├── configmap.yaml
└── kustomization.yaml
```

### deployment.yaml
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

### service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp
spec:
  selector:
    app: webapp
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

### configmap.yaml
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: webapp-config
data:
  APP_NAME: "My Web App"
  LOG_LEVEL: "info"
```

### kustomization.yaml
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml
- configmap.yaml

namespace: production

commonLabels:
  app: webapp
  version: v1.0.0

namePrefix: prod-

images:
- name: nginx
  newTag: "1.21"
```

### Build Output
```bash
kubectl kustomize .
```

### Full Generated Output
```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: webapp
    version: v1.0.0
  name: prod-webapp
  namespace: production
spec:
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: webapp
    version: v1.0.0
  type: LoadBalancer
---
apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    app: webapp
    version: v1.0.0
  name: prod-webapp-config
  namespace: production
data:
  APP_NAME: My Web App
  LOG_LEVEL: info
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: webapp
    version: v1.0.0
  name: prod-webapp
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: webapp
      version: v1.0.0
  template:
    metadata:
      labels:
        app: webapp
        version: v1.0.0
    spec:
      containers:
      - image: nginx:1.21
        name: webapp
        ports:
        - containerPort: 80
```

## Inspecting Changes

### Before and After Comparison

**Original deployment.yaml:**
```yaml
metadata:
  name: webapp
```

**After kustomization:**
```yaml
metadata:
  labels:
    app: webapp
    version: v1.0.0
  name: prod-webapp
  namespace: production
```

### What Got Transformed:
1. **Name**: `webapp` → `prod-webapp`
2. **Namespace**: None → `production`
3. **Labels**: Added `app` and `version`
4. **Image**: `nginx:1.19` → `nginx:1.21`

## Output Validation

### 1. Validate YAML Syntax
```bash
kubectl kustomize . | kubectl apply --dry-run=client -f -
```

### 2. Validate Against Schema
```bash
kubectl kustomize . | kubectl apply --dry-run=server -f -
```

### 3. Show Diff (If Already Applied)
```bash
kubectl diff -k .
```

## Common Output Scenarios

### Scenario 1: Preview Before Applying
```bash
# See what will be created
kubectl kustomize ./overlays/prod

# Review the output, then apply
kubectl apply -k ./overlays/prod
```

### Scenario 2: Debug Issues
```bash
# Build and inspect
kubectl kustomize . > debug.yaml

# Open in editor to check
code debug.yaml
```

### Scenario 3: GitOps Workflow
```bash
# Generate and commit
kubectl kustomize ./overlays/prod > manifests/prod.yaml
git add manifests/prod.yaml
git commit -m "Update prod manifests"
```

### Scenario 4: CI/CD Pipeline
```bash
# Generate in CI pipeline
kustomize build overlays/prod > output.yaml

# Deploy in CD pipeline
kubectl apply -f output.yaml
```

## Output Format Options

### Standard YAML Output
```bash
kubectl kustomize .
```

### JSON Output
```bash
kubectl kustomize . -o json
```

### Compact Output (using yq)
```bash
kubectl kustomize . | yq eval -P
```

## Troubleshooting Output Issues

### Issue 1: Empty Output
```bash
$ kubectl kustomize .
# No output

# Check for errors
$ kubectl kustomize . 2>&1
Error: unable to find one or more resources
```

**Solution:** Verify all resources exist in `kustomization.yaml`

### Issue 2: Unexpected Transformations
```bash
# Check what's being transformed
kubectl kustomize . | grep -A 10 "name:"
```

**Solution:** Review your `kustomization.yaml` transformers

### Issue 3: Missing Resources
```bash
# List all resources
kubectl kustomize . | yq eval '.kind' -
```

**Solution:** Ensure all files are listed in `resources:`

## Output Best Practices

### 1. **Always Preview**
```bash
# Never apply blind
kubectl kustomize ./overlays/prod  # Review first
kubectl apply -k ./overlays/prod   # Then apply
```

### 2. **Use Dry Run**
```bash
kubectl apply -k . --dry-run=client -o yaml
```

### 3. **Check Differences**
```bash
kubectl diff -k ./overlays/prod
```

### 4. **Save for Audit**
```bash
# Keep a record
kubectl kustomize ./overlays/prod > deployed-$(date +%Y%m%d).yaml
```

### 5. **Validate Before Apply**
```bash
# Syntax check
kubectl kustomize . | kubectl apply --dry-run=server -f -
```

## Output in Different Contexts

### Development
```bash
# Quick preview
kubectl kustomize ./overlays/dev
```

### Testing
```bash
# Dry run test
kubectl apply -k ./overlays/test --dry-run=server
```

### Production
```bash
# Full validation
kubectl kustomize ./overlays/prod > prod-review.yaml
# Review prod-review.yaml
kubectl apply -k ./overlays/prod
```

## Quick Reference Commands

```bash
# View output
kubectl kustomize .
kustomize build .

# Save output
kubectl kustomize . > output.yaml

# Apply output
kubectl apply -k .

# Dry run
kubectl apply -k . --dry-run=client

# Server-side dry run (validates against cluster)
kubectl apply -k . --dry-run=server

# Show diff
kubectl diff -k .

# Delete resources
kubectl delete -k .

# View specific overlay
kubectl kustomize ./overlays/prod
```

## Summary

| Command | Purpose |
|---------|---------|
| `kubectl kustomize .` | View generated output |
| `kubectl apply -k .` | Apply to cluster |
| `kubectl diff -k .` | Show differences |
| `kubectl delete -k .` | Delete resources |
| `--dry-run=client` | Client-side validation |
| `--dry-run=server` | Server-side validation |

## Next Steps

Now you understand Kustomize output:
- ✅ How to view generated manifests
- ✅ How transformations are applied
- ✅ How to validate before applying
- ✅ How to troubleshoot issues

Next, we'll dive into **apiVersion and Kind** in kustomization.yaml! 🚀
