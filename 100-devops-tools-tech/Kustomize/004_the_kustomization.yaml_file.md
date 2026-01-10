# The kustomization.yaml File

## What is kustomization.yaml?

The `kustomization.yaml` file is the **heart of Kustomize**. It's a configuration file that tells Kustomize:
- Which Kubernetes resources to include
- What transformations to apply
- How to customize your configurations

Think of it as a "recipe" that describes how to build your final Kubernetes manifests.

## Basic Structure

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

# Your customizations go here
```

**Required fields:**
- `apiVersion`: Always `kustomize.config.k8s.io/v1beta1`
- `kind`: Always `Kustomization`

## Core Sections

### 1. Resources

The `resources` field lists all Kubernetes manifest files to include:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml
- configmap.yaml
```

**Resources can be:**
- Local files: `deployment.yaml`
- Directories: `./configs/`
- URLs: `https://raw.githubusercontent.com/...`
- Other kustomizations: `../../base`

### 2. Common Transformers

Add fields to all resources:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

# Add labels to all resources
commonLabels:
  app: myapp
  team: platform

# Add annotations to all resources
commonAnnotations:
  managed-by: kustomize
  version: "1.0"

# Add prefix to all resource names
namePrefix: dev-

# Add suffix to all resource names
nameSuffix: -v1
```

### 3. Namespace

Set namespace for all resources:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

namespace: production
```

## Complete Example

Let's create a real example with a simple Nginx deployment:

### deployment.yaml
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
```

### service.yaml
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

### kustomization.yaml
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

namespace: default

commonLabels:
  app: nginx
  environment: dev

namePrefix: dev-

images:
- name: nginx
  newTag: "1.21"

replicas:
- name: nginx
  count: 3
```

### Output (after running `kustomize build`)

```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: nginx
    environment: dev
  name: dev-nginx
  namespace: default
spec:
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: nginx
    environment: dev
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx
    environment: dev
  name: dev-nginx
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
      environment: dev
  template:
    metadata:
      labels:
        app: nginx
        environment: dev
    spec:
      containers:
      - image: nginx:1.21
        name: nginx
        ports:
        - containerPort: 80
```

Notice the changes:
- ✅ Name changed from `nginx` to `dev-nginx` (namePrefix)
- ✅ Namespace set to `default`
- ✅ Labels added: `environment: dev`
- ✅ Image tag updated to `1.21`
- ✅ Replicas changed to `3`

## All Available Fields

Here's a comprehensive overview of `kustomization.yaml` fields:

### Resource Management
```yaml
# Include resources
resources:
- deployment.yaml
- https://raw.githubusercontent.com/...

# Include other kustomizations
bases:  # Deprecated, use resources
- ../../base

# Generate ConfigMaps
configMapGenerator:
- name: app-config
  files:
  - application.properties
  literals:
  - KEY=VALUE

# Generate Secrets
secretGenerator:
- name: app-secret
  files:
  - secret.txt
  literals:
  - PASSWORD=secret123
```

### Transformers
```yaml
# Common fields for all resources
commonLabels:
  app: myapp

commonAnnotations:
  version: "1.0"

namespace: production

namePrefix: prod-
nameSuffix: -v2

# Modify images
images:
- name: nginx
  newName: myregistry/nginx
  newTag: latest

# Modify replicas
replicas:
- name: my-deployment
  count: 5
```

### Patches
```yaml
# Strategic merge patches
patchesStrategicMerge:
- patch-deployment.yaml

# JSON 6902 patches
patchesJson6902:
- target:
    group: apps
    version: v1
    kind: Deployment
    name: nginx
  path: patch.yaml

# Inline patches
patches:
- target:
    kind: Deployment
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 3
```

### Advanced Features
```yaml
# Components (reusable pieces)
components:
- ../../components/monitoring

# Custom configurations
configurations:
- kustomizeconfig.yaml

# Generators
generators:
- secret-generator.yaml

# Transformers
transformers:
- transformer.yaml

# Validators
validators:
- validator.yaml

# Variable replacements
vars:
- name: SERVICE_NAME
  objref:
    kind: Service
    name: myservice
    apiVersion: v1
  fieldref:
    fieldpath: metadata.name
```

## Field Categories

| Category | Fields | Purpose |
|----------|--------|---------|
| **Resource Loading** | resources, bases | Include files |
| **Generators** | configMapGenerator, secretGenerator | Create resources |
| **Name Transformers** | namePrefix, nameSuffix | Modify names |
| **Label Transformers** | commonLabels, commonAnnotations | Add labels |
| **Namespace Transformer** | namespace | Set namespace |
| **Image Transformer** | images | Update images |
| **Replica Transformer** | replicas | Set replica count |
| **Patches** | patches, patchesStrategicMerge, patchesJson6902 | Modify resources |
| **Components** | components | Include reusable configs |

## File Location

The `kustomization.yaml` file must be in the **root of the directory** you're kustomizing:

```bash
# Correct
my-app/
└── kustomization.yaml

# Correct - with resources
my-app/
├── kustomization.yaml
├── deployment.yaml
└── service.yaml

# Incorrect - nested
my-app/
└── config/
    └── kustomization.yaml  # kubectl apply -k my-app won't find this
```

## Common Patterns

### Pattern 1: Simple App
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml
```

### Pattern 2: Base + Overlays
```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: production
namePrefix: prod-

replicas:
- name: myapp
  count: 10
```

### Pattern 3: Generated ConfigMaps
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

configMapGenerator:
- name: app-config
  literals:
  - DATABASE_URL=postgres://db:5432
  - LOG_LEVEL=info
```

## Validation

Kustomize validates your `kustomization.yaml`:

```bash
# Build to check for errors
kustomize build .

# Common errors
# ❌ Error: unable to find one or more resources
# ❌ Error: invalid Kustomization: missing required field
# ❌ Error: json: cannot unmarshal...
```

## Best Practices

1. **Keep it Simple**: Start with basic fields
2. **Use Comments**: Document your choices
3. **Version Control**: Always commit kustomization.yaml
4. **Validate Often**: Run `kustomize build` frequently
5. **Organize Resources**: Group related files together

## Quick Reference

```yaml
# Minimal kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml

# Common kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
namespace: default
commonLabels:
  app: myapp
images:
- name: nginx
  newTag: "1.21"

# Advanced kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../base
namespace: production
namePrefix: prod-
commonLabels:
  environment: production
images:
- name: myapp
  newTag: v2.0.0
replicas:
- name: myapp
  count: 10
configMapGenerator:
- name: config
  files:
  - app.properties
patchesStrategicMerge:
- patch.yaml
```

## Next Steps

Now that you understand the `kustomization.yaml` file:
- ✅ You know its structure
- ✅ You understand core fields
- ✅ You've seen real examples

Next, we'll learn about **Kustomize output** and how to preview and apply your configurations! 🚀
