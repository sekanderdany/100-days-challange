# Patches Introduction

## What are Patches?

Patches in Kustomize allow you to make surgical modifications to Kubernetes resources without duplicating entire files. They're powerful tools for customizing configurations in specific ways that transformers cannot handle.

## Why Use Patches?

While transformers are great for simple, consistent changes, patches are needed when:
- **Complex modifications** are required
- **Specific fields** need targeted changes
- **Conditional logic** must be applied
- **Different resources** need different treatments

## Patches vs Transformers

| Feature | Transformers | Patches |
|---------|-------------|---------|
| **Scope** | All resources | Specific resources |
| **Granularity** | Broad changes | Precise changes |
| **Complexity** | Simple | Can be complex |
| **Use Case** | Add labels, change images | Modify specific fields |

### Example Comparison

**Using Transformer:**
```yaml
# Changes ALL deployments
replicas:
- name: nginx
  count: 5
```

**Using Patch:**
```yaml
# Changes specific fields in specific resource
patches:
- target:
    kind: Deployment
    name: nginx
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 5
    - op: add
      path: /spec/template/spec/containers/0/env/-
      value:
        name: NEW_VAR
        value: "new_value"
```

## Types of Patches in Kustomize

Kustomize supports three main patch formats:

### 1. Strategic Merge Patch
- Most common and easiest
- Merges YAML content
- Uses Kubernetes merge strategies
- Field: `patchesStrategicMerge`

### 2. JSON Patch (JSON 6902)
- Precise and explicit
- Uses JSON Patch RFC 6902
- Array of operations (add, remove, replace)
- Field: `patchesJson6902`

### 3. Inline Patches
- Modern unified format
- Can use either merge or JSON patches
- Field: `patches`

## When to Use Each Type

| Patch Type | Best For | Example Use Case |
|------------|----------|------------------|
| **Strategic Merge** | Simple field updates, additions | Add env vars, change resources |
| **JSON 6902** | Array operations, removals | Remove specific env var |
| **Inline** | Modern unified approach | Any patching scenario |

## Basic Patch Concepts

### Target Identification

Patches need to identify which resources to modify:

```yaml
patches:
- target:
    kind: Deployment        # Resource type
    name: nginx             # Resource name
    namespace: production   # Optional: namespace
    labelSelector: "app=web" # Optional: label selector
  patch: |-
    # patch content here
```

### Patch Content

The actual modifications to apply:

```yaml
# Strategic merge - YAML format
patch: |-
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: nginx
  spec:
    replicas: 10

# OR JSON 6902 - Operations format
patch: |-
  - op: replace
    path: /spec/replicas
    value: 10
```

## Simple Example: Strategic Merge Patch

### Scenario
You have a base deployment with 2 replicas. In production, you need 10 replicas and more resources.

**base/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.19
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
```

**overlays/prod/increase-resources.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 10
  template:
    spec:
      containers:
      - name: nginx
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

**overlays/prod/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

patchesStrategicMerge:
- increase-resources.yaml
```

### Result

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 10  # Updated
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.19  # Kept from base
        resources:
          requests:
            memory: "512Mi"  # Updated
            cpu: "500m"      # Updated
          limits:
            memory: "1Gi"    # Added
            cpu: "1000m"     # Added
```

## Simple Example: JSON 6902 Patch

### Scenario
Add an environment variable to a container.

**overlays/prod/add-env.yaml:**
```yaml
- op: add
  path: /spec/template/spec/containers/0/env
  value:
  - name: ENVIRONMENT
    value: production
  - name: LOG_LEVEL
    value: info
```

**overlays/prod/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

patchesJson6902:
- target:
    kind: Deployment
    name: nginx
  path: add-env.yaml
```

## Simple Example: Inline Patches

### Scenario
Modify replicas using inline patch.

**overlays/prod/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

patches:
- target:
    kind: Deployment
    name: nginx
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 10
```

## Common Patch Operations

### Add a Field
```yaml
- op: add
  path: /spec/template/spec/containers/0/env/-
  value:
    name: NEW_VAR
    value: "value"
```

### Replace a Value
```yaml
- op: replace
  path: /spec/replicas
  value: 10
```

### Remove a Field
```yaml
- op: remove
  path: /spec/template/spec/containers/0/env/0
```

### Copy a Value
```yaml
- op: copy
  from: /spec/template/spec/containers/0/image
  path: /spec/template/spec/initContainers/0/image
```

### Move a Value
```yaml
- op: move
  from: /spec/template/metadata/labels/old-key
  path: /spec/template/metadata/labels/new-key
```

### Test a Value
```yaml
- op: test
  path: /spec/replicas
  value: 2
```

## Use Cases for Patches

### 1. Environment-Specific Resources

```yaml
# Production needs more memory
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
              limits:
                memory: "2Gi"
```

### 2. Adding Sidecars

```yaml
# Add logging sidecar in production
patches:
- target:
    kind: Deployment
  patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: not-important
    spec:
      template:
        spec:
          containers:
          - name: logging-agent
            image: fluentd:latest
```

### 3. Enabling Features

```yaml
# Enable debug mode in dev
patches:
- target:
    kind: Deployment
    labelSelector: "app=webapp"
  patch: |-
    - op: add
      path: /spec/template/spec/containers/0/env/-
      value:
        name: DEBUG
        value: "true"
```

### 4. Removing Resources

```yaml
# Remove resource limits in dev
patches:
- target:
    kind: Deployment
  patch: |-
    - op: remove
      path: /spec/template/spec/containers/0/resources/limits
```

## Best Practices

### 1. **Start with Strategic Merge**
Easier to read and maintain:
```yaml
patchesStrategicMerge:
- increase-replicas.yaml
```

### 2. **Use JSON 6902 for Precision**
When you need exact control:
```yaml
patchesJson6902:
- target:
    kind: Deployment
    name: nginx
  path: precise-changes.yaml
```

### 3. **Keep Patches Small**
One purpose per patch file:
```
overlays/prod/
├── increase-replicas.yaml
├── add-resources.yaml
└── enable-monitoring.yaml
```

### 4. **Name Patches Clearly**
```
# Good
increase-replicas.yaml
add-monitoring-sidecar.yaml
enable-debug-mode.yaml

# Avoid
patch1.yaml
changes.yaml
updates.yaml
```

### 5. **Document Complex Patches**
```yaml
# overlays/prod/kustomization.yaml
patchesStrategicMerge:
# Increases replicas to 10 for production load
- increase-replicas.yaml
# Adds fluentd sidecar for centralized logging
- add-logging-sidecar.yaml
```

## Debugging Patches

### View Final Output
```bash
kubectl kustomize overlays/prod/
```

### Test Before Apply
```bash
kubectl apply -k overlays/prod/ --dry-run=client -o yaml
```

### Check for Errors
```bash
kubectl kustomize overlays/prod/ 2>&1 | grep -i error
```

## Common Pitfalls

### ❌ Pitfall 1: Wrong Resource Name
```yaml
# Patch targets "webapp" but base has "web-app"
patches:
- target:
    kind: Deployment
    name: webapp  # Won't match!
```

### ❌ Pitfall 2: Incorrect Path
```yaml
# Path doesn't exist
- op: replace
  path: /spec/templates/spec  # Should be /spec/template/spec
  value: {}
```

### ❌ Pitfall 3: Mixed Patch Types
```yaml
# Don't mix strategic merge and JSON patch in same file
# Pick one format per patch file
```

## Quick Reference

| What You Want | Patch Type | Difficulty |
|---------------|------------|------------|
| Change simple values | Strategic Merge | ⭐ Easy |
| Add env variables | Strategic Merge | ⭐ Easy |
| Modify arrays precisely | JSON 6902 | ⭐⭐ Medium |
| Remove specific items | JSON 6902 | ⭐⭐ Medium |
| Complex multi-field changes | Strategic Merge | ⭐⭐ Medium |
| Conditional modifications | Inline with selectors | ⭐⭐⭐ Hard |

## Next Steps

Now you understand patch basics:
- ✅ What patches are and why use them
- ✅ Three types of patches
- ✅ When to use each type
- ✅ Common operations

Next, we'll dive deep into the **different types of patches** with detailed examples! 🚀
