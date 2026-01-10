# Different Types of Patches

## Overview

Kustomize supports three patch formats, each with its own strengths. Understanding when and how to use each type will make you more effective at customizing Kubernetes configurations.

## 1. Strategic Merge Patch

### What is Strategic Merge?

Strategic Merge Patch is a Kubernetes-native patching strategy that understands resource structure and merges intelligently based on field types.

### Key Features

- **Intuitive**: Uses regular Kubernetes YAML
- **Smart Merging**: Understands how to merge lists and maps
- **Kubernetes-Aware**: Knows about Kubernetes resource semantics
- **Easy to Read**: Looks like normal Kubernetes manifests

### Syntax

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

patchesStrategicMerge:
- patch-file-1.yaml
- patch-file-2.yaml
```

### How It Works

Strategic merge looks at the patch and base, then:
1. **Replaces** scalar values (strings, numbers)
2. **Merges** maps (dictionaries)
3. **Replaces or merges** lists based on merge strategy

### Example 1: Simple Field Update

**Base:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 2
```

**Patch (increase-replicas.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 10
```

**Result:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 10  # Replaced
```

### Example 2: Adding Environment Variables

**Base:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  template:
    spec:
      containers:
      - name: webapp
        image: nginx:1.19
        env:
        - name: ENV
          value: base
```

**Patch (add-env.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  template:
    spec:
      containers:
      - name: webapp
        env:
        - name: DEBUG
          value: "true"
        - name: LOG_LEVEL
          value: info
```

**Result:**
```yaml
spec:
  template:
    spec:
      containers:
      - name: webapp
        image: nginx:1.19
        env:
        - name: ENV
          value: base
        - name: DEBUG  # Added
          value: "true"
        - name: LOG_LEVEL  # Added
          value: info
```

### Example 3: Updating Resources

**Patch (update-resources.yaml):**
```yaml
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
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

This merges with existing resources, updating values.

### Advantages

✅ Easy to write and understand  
✅ Looks like regular Kubernetes YAML  
✅ Good for adding and updating fields  
✅ Handles nested structures well

### Disadvantages

❌ Cannot easily remove fields  
❌ Array handling can be unpredictable  
❌ Requires full resource metadata

## 2. JSON Patch (JSON 6902)

### What is JSON 6902?

JSON Patch is an RFC 6902 standard format for describing changes to JSON documents using explicit operations.

### Key Features

- **Precise**: Exact control over modifications
- **Operations-Based**: Add, remove, replace, move, copy, test
- **Path-Based**: Target specific fields using JSON Pointer
- **Explicit**: No ambiguity about what changes

### Syntax

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

patchesJson6902:
- target:
    kind: Deployment
    name: webapp
  path: patches/update.yaml
```

### Operations

| Operation | Purpose | Example |
|-----------|---------|---------|
| **add** | Add a field or array element | Add env var |
| **remove** | Remove a field | Remove resource limit |
| **replace** | Replace a value | Change replica count |
| **move** | Move a value | Rename a key |
| **copy** | Copy a value | Duplicate config |
| **test** | Validate a value | Assert before change |

### JSON Pointer Paths

Paths use `/` to navigate the structure:

```
/spec/replicas                           → spec.replicas
/spec/template/spec/containers/0/image   → First container image
/metadata/labels/app                     → Label "app"
/spec/template/spec/containers/0/env/-   → Append to env array
```

### Example 1: Replace Operation

**Patch:**
```yaml
- op: replace
  path: /spec/replicas
  value: 10
```

Changes `spec.replicas` to 10.

### Example 2: Add Operation

**Add Environment Variable:**
```yaml
- op: add
  path: /spec/template/spec/containers/0/env/-
  value:
    name: DEBUG
    value: "true"
```

The `-` at the end means "append to array".

### Example 3: Remove Operation

**Remove Resource Limits:**
```yaml
- op: remove
  path: /spec/template/spec/containers/0/resources/limits
```

### Example 4: Multiple Operations

**Combined Patch:**
```yaml
- op: replace
  path: /spec/replicas
  value: 5

- op: add
  path: /spec/template/spec/containers/0/env/-
  value:
    name: LOG_LEVEL
    value: debug

- op: remove
  path: /spec/template/spec/containers/0/resources/limits/cpu
```

### Example 5: Test Operation

**Assert Before Changing:**
```yaml
- op: test
  path: /spec/replicas
  value: 2

- op: replace
  path: /spec/replicas
  value: 10
```

Only replaces if current value is 2.

### Complete Example

**target resource (base/deployment.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: webapp
        image: nginx:1.19
        env:
        - name: ENV
          value: base
```

**Patch (overlays/prod/json-patch.yaml):**
```yaml
- op: replace
  path: /spec/replicas
  value: 10

- op: add
  path: /spec/template/spec/containers/0/env/-
  value:
    name: ENVIRONMENT
    value: production

- op: replace
  path: /spec/template/spec/containers/0/image
  value: nginx:1.21
```

**kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

patchesJson6902:
- target:
    kind: Deployment
    name: webapp
  path: json-patch.yaml
```

### Advantages

✅ Precise control over changes  
✅ Can remove fields easily  
✅ Explicit array operations  
✅ Test operations for validation

### Disadvantages

❌ More verbose  
❌ Harder to read  
❌ Need to know exact paths  
❌ Fragile if structure changes

## 3. Inline Patches (Modern Unified Format)

### What are Inline Patches?

Inline patches are the modern, unified way to specify patches directly in `kustomization.yaml`. They support both strategic merge and JSON 6902 formats.

### Key Features

- **Modern**: Recommended for new projects
- **Flexible**: Supports both patch types
- **Inline**: No separate patch files needed
- **Target Selection**: Powerful targeting options

### Syntax

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

patches:
- target:
    kind: Deployment
    name: webapp
  patch: |-
    # patch content (strategic merge or JSON 6902)
```

### Example 1: Inline JSON Patch

```yaml
patches:
- target:
    kind: Deployment
    name: nginx
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 10
```

### Example 2: Inline Strategic Merge

```yaml
patches:
- target:
    kind: Deployment
    name: nginx
  patch: |-
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
              limits:
                memory: 1Gi
```

### Example 3: Label Selector

```yaml
patches:
- target:
    kind: Deployment
    labelSelector: "app=webapp,tier=backend"
  patch: |-
    - op: add
      path: /spec/template/spec/containers/0/env/-
      value:
        name: TIER
        value: backend
```

Applies to all Deployments matching the label selector.

### Example 4: Multiple Targets

```yaml
patches:
# Patch all Deployments
- target:
    kind: Deployment
  patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: placeholder
    spec:
      template:
        spec:
          securityContext:
            runAsNonRoot: true

# Patch specific Service
- target:
    kind: Service
    name: webapp
  patch: |-
    - op: replace
      path: /spec/type
      value: LoadBalancer
```

### Advantages

✅ Modern and recommended  
✅ No separate files needed  
✅ Powerful targeting  
✅ Supports both patch types

### Disadvantages

❌ Can make kustomization.yaml large  
❌ Less reusable across projects

## Comparison Table

| Feature | Strategic Merge | JSON 6902 | Inline Patches |
|---------|----------------|-----------|----------------|
| **Format** | Kubernetes YAML | JSON operations | Both |
| **Readability** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐ Fair | ⭐⭐⭐ Good |
| **Precision** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very Good |
| **Removing Fields** | ⭐ Poor | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very Good |
| **Array Operations** | ⭐⭐ Fair | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very Good |
| **File Organization** | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐ Good | ⭐⭐ Fair |
| **Reusability** | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐ Good | ⭐⭐ Fair |

## When to Use Which?

### Use Strategic Merge When:
- Adding new fields
- Updating simple values
- Working with nested structures
- You want readable patches
- Team prefers YAML

### Use JSON 6902 When:
- Need to remove fields
- Precise array operations needed
- Conditional changes (test operations)
- Complex transformations
- You need explicit control

### Use Inline Patches When:
- Small, simple patches
- Don't want separate files
- Using label selectors
- Modern greenfield projects
- Patches specific to one overlay

## Best Practices

### 1. Choose the Right Tool

```yaml
# Simple value update → Strategic Merge
patchesStrategicMerge:
- increase-replicas.yaml

# Remove field → JSON 6902
patchesJson6902:
- target:
    kind: Deployment
    name: webapp
  path: remove-limits.yaml

# Small inline change → Inline Patches
patches:
- target:
    kind: Service
  patch: |-
    - op: replace
      path: /spec/type
      value: LoadBalancer
```

### 2. Keep It Simple

Start with strategic merge, use JSON 6902 only when needed.

### 3. Organize Patch Files

```
overlays/prod/
├── kustomization.yaml
└── patches/
    ├── increase-replicas.yaml
    ├── add-monitoring.yaml
    └── update-resources.yaml
```

### 4. Document Complex Patches

```yaml
patches:
# Force all deployments to use read-only root filesystem
# for security compliance
- target:
    kind: Deployment
  patch: |-
    # ... patch content
```

## Quick Reference

### Strategic Merge
```yaml
patchesStrategicMerge:
- patch.yaml
```

### JSON 6902
```yaml
patchesJson6902:
- target:
    kind: Deployment
    name: webapp
  path: patch.yaml
```

### Inline
```yaml
patches:
- target:
    kind: Deployment
  patch: |-
    # content
```

## Next Steps

Now you understand all three patch types:
- ✅ Strategic Merge Patch
- ✅ JSON 6902 Patch
- ✅ Inline Patches
- ✅ When to use each

Next, we'll explore **patches with dictionaries and maps**! 🚀
