# Image Transformers

## What are Image Transformers?

Image transformers allow you to modify container images in your Kubernetes manifests without editing the original files. This is extremely useful for:
- Changing image tags across environments
- Using different image registries
- Testing new versions
- CI/CD pipelines

## The `images` Field

### Syntax

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

images:
- name: <original-image-name>
  newName: <new-image-name>      # Optional: Change registry/repo
  newTag: <new-tag>               # Optional: Change tag
  digest: <new-digest>            # Optional: Use digest instead of tag
```

## Basic Operations

### 1. Change Image Tag

Most common use case - update the version:

**kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

images:
- name: nginx
  newTag: "1.21"
```

**Input deployment.yaml:**
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
```

**Output:**
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
        image: nginx:1.21
```

### 2. Change Image Name (Registry)

Switch to a different registry:

```yaml
images:
- name: nginx
  newName: myregistry.azurecr.io/nginx
  newTag: "1.21"
```

**Result:**
```yaml
# Before: nginx:1.19
# After:  myregistry.azurecr.io/nginx:1.21
```

### 3. Use Image Digest

For immutable deployments:

```yaml
images:
- name: nginx
  digest: sha256:abcdef1234567890...
```

**Result:**
```yaml
# Before: nginx:1.19
# After:  nginx@sha256:abcdef1234567890...
```

## Multiple Images

You can transform multiple images in one kustomization:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

images:
- name: nginx
  newTag: "1.21"
- name: redis
  newTag: "6.2"
- name: postgres
  newTag: "13"
```

## Image Matching

### Matching Rules

Kustomize matches images by name. The matching can be:

#### 1. Exact Match
```yaml
# In deployment: nginx:1.19
# In kustomization:
images:
- name: nginx  # Matches exactly
  newTag: "1.21"
```

#### 2. With Registry
```yaml
# In deployment: docker.io/library/nginx:1.19
# In kustomization:
images:
- name: docker.io/library/nginx
  newTag: "1.21"
```

#### 3. Short Name
```yaml
# In deployment: myapp:v1
# In kustomization:
images:
- name: myapp
  newTag: v2
```

## Environment-Specific Examples

### Development

```yaml
# overlays/dev/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

images:
- name: myapp
  newTag: dev-latest  # Use latest dev build
```

### Staging

```yaml
# overlays/staging/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

images:
- name: myapp
  newTag: "1.2.3"  # Specific version for testing
```

### Production

```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

images:
- name: myapp
  newName: prodregistry.io/myapp
  newTag: "1.2.3"
  # Or use digest for immutability:
  # digest: sha256:abc123...
```

## Advanced Use Cases

### 1. Private Registry

```yaml
images:
- name: nginx
  newName: mycompany.azurecr.io/nginx
  newTag: "1.21"
```

### 2. Multi-Container Pod

```yaml
# deployment.yaml has multiple containers
spec:
  containers:
  - name: app
    image: myapp:v1
  - name: sidecar
    image: logger:v1
  - name: proxy
    image: nginx:1.19

# kustomization.yaml updates all
images:
- name: myapp
  newTag: v2
- name: logger
  newTag: v2
- name: nginx
  newTag: "1.21"
```

### 3. Init Containers

Image transformer works with init containers too:

```yaml
# deployment.yaml
spec:
  initContainers:
  - name: init-db
    image: busybox:1.30
  containers:
  - name: app
    image: myapp:v1

# kustomization.yaml
images:
- name: busybox
  newTag: "1.35"
- name: myapp
  newTag: v2
```

## CI/CD Integration

### Example: Automated Tag Update

```bash
# In your CI/CD pipeline
export IMAGE_TAG=$(git rev-parse --short HEAD)

# Update kustomization.yaml
cd overlays/prod
kustomize edit set image myapp=myregistry.io/myapp:${IMAGE_TAG}

# Apply
kubectl apply -k .
```

### Example: Using kustomize CLI

```bash
# Set image using kustomize CLI
kustomize edit set image nginx=nginx:1.21

# This modifies kustomization.yaml:
# images:
# - name: nginx
#   newTag: "1.21"
```

## Complete Example

### Base Configuration

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
      - name: frontend
        image: nginx:1.19
        ports:
        - containerPort: 80
      - name: backend
        image: myapp:v1.0.0
        ports:
        - containerPort: 8080
```

**base/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
```

### Dev Overlay

**overlays/dev/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: development

images:
- name: nginx
  newTag: "1.19-alpine"  # Smaller image for dev
- name: myapp
  newTag: dev-latest     # Latest dev build
```

### Prod Overlay

**overlays/prod/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: production

images:
- name: nginx
  newName: myregistry.azurecr.io/nginx
  newTag: "1.21"
- name: myapp
  newName: myregistry.azurecr.io/myapp
  digest: sha256:abc123def456...  # Immutable with digest
```

## Image Transformer vs Patches

### When to use Image Transformer

✅ **Use `images` field when:**
- Simply changing tags
- Switching registries
- Same for all instances of an image

### When to use Patches

✅ **Use patches when:**
- Need to change other container properties
- Different changes per container
- Complex modifications needed

### Example Comparison

**Using Image Transformer:**
```yaml
images:
- name: nginx
  newTag: "1.21"
```

**Using Patch:**
```yaml
patchesStrategicMerge:
- |-
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: webapp
  spec:
    template:
      spec:
        containers:
        - name: nginx
          image: nginx:1.21
```

Image transformer is cleaner and simpler! ✨

## Best Practices

### 1. Use Specific Tags in Production

```yaml
# Good for production
images:
- name: myapp
  newTag: "1.2.3"

# Avoid in production
images:
- name: myapp
  newTag: latest  # Don't use 'latest' in prod
```

### 2. Use Digests for Critical Apps

```yaml
# Maximum immutability
images:
- name: myapp
  digest: sha256:abc123...
```

### 3. Keep Base Generic

```yaml
# base/deployment.yaml - Use generic tags
image: myapp:latest

# overlays/prod/kustomization.yaml - Specify exact versions
images:
- name: myapp
  newTag: "1.2.3"
```

### 4. Document Image Sources

```yaml
# Add comments in kustomization.yaml
images:
  # Frontend nginx - updated 2024-01-10
- name: nginx
  newTag: "1.21"
  # Backend app - release v1.2.3
- name: myapp
  newTag: "1.2.3"
```

## Common Pitfalls

### ❌ Pitfall 1: Image Name Mismatch

```yaml
# In deployment.yaml
image: docker.io/library/nginx:1.19

# In kustomization.yaml - WON'T MATCH
images:
- name: nginx
  newTag: "1.21"

# Fix: Use full name
images:
- name: docker.io/library/nginx
  newTag: "1.21"
```

### ❌ Pitfall 2: Missing Image in Resources

```yaml
# kustomization.yaml references non-existent image
images:
- name: redis
  newTag: "6.2"

# But deployment.yaml doesn't have redis
# Result: No error, but nothing happens
```

### ❌ Pitfall 3: Tag and Digest Together

```yaml
# Don't use both
images:
- name: nginx
  newTag: "1.21"
  digest: sha256:abc123...  # Digest takes precedence
```

## Testing Image Transformations

```bash
# Test image transformation
kubectl kustomize overlays/prod/ | grep "image:"

# Expected output:
# - image: myregistry.io/myapp:1.2.3
# - image: myregistry.io/nginx:1.21
```

## Quick Reference

### Change Tag Only
```yaml
images:
- name: nginx
  newTag: "1.21"
```

### Change Registry and Tag
```yaml
images:
- name: nginx
  newName: myregistry.io/nginx
  newTag: "1.21"
```

### Use Digest
```yaml
images:
- name: nginx
  digest: sha256:abc123...
```

### Multiple Images
```yaml
images:
- name: nginx
  newTag: "1.21"
- name: redis
  newTag: "6.2"
```

## CLI Commands

```bash
# Set image using kustomize CLI
kustomize edit set image nginx=nginx:1.21

# Set image with new name
kustomize edit set image nginx=myregistry.io/nginx:1.21

# View current images
cat kustomization.yaml | grep -A 2 "images:"
```

## Next Steps

Now you understand image transformers:
- ✅ How to change image tags
- ✅ How to switch registries
- ✅ How to use digests
- ✅ CI/CD integration patterns

Next, we'll see a **live demo** of using transformers together! 🚀
