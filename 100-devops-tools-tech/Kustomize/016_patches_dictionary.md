# Patches - Working with Dictionaries

## Overview

Dictionaries (maps/objects) are key-value structures in Kubernetes manifests. Understanding how to patch them effectively is crucial for customizing configurations.

## Strategic Merge with Dictionaries

Strategic merge is excellent for working with dictionaries because it intelligently merges keys.

### How Dictionary Merging Works

**Rule**: Keys are merged, with patch values overriding base values.

**Base:**
```yaml
metadata:
  labels:
    app: webapp
    version: v1
```

**Patch:**
```yaml
metadata:
  labels:
    environment: production
    version: v2
```

**Result:**
```yaml
metadata:
  labels:
    app: webapp           # Kept from base
    version: v2           # Overridden by patch
    environment: production  # Added from patch
```

## Example 1: Adding Labels

**Base (deployment.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  labels:
    app: webapp
spec:
  template:
    metadata:
      labels:
        app: webapp
```

**Patch (add-labels.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  labels:
    environment: production
    team: platform
    cost-center: engineering
```

**Result:**
```yaml
metadata:
  labels:
    app: webapp                    # Original
    environment: production         # Added
    team: platform                  # Added
    cost-center: engineering        # Added
```

## Example 2: Updating Annotations

**Patch (update-annotations.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
    prometheus.io/path: "/metrics"
    backup-policy: "daily"
```

Adds all annotations to the deployment.

## Example 3: Modifying Resource Limits

**Base:**
```yaml
spec:
  template:
    spec:
      containers:
      - name: webapp
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
```

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
            memory: "512Mi"  # Updated
            cpu: "500m"      # Updated
          limits:            # Added
            memory: "1Gi"
            cpu: "1000m"
```

**Result:**
```yaml
resources:
  requests:
    memory: "512Mi"    # Updated
    cpu: "500m"        # Updated
  limits:              # Completely added
    memory: "1Gi"
    cpu: "1000m"
```

## Example 4: ConfigMap Data

**Base:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database.host: "localhost"
  database.port: "5432"
  app.mode: "development"
```

**Patch (prod-config.yaml):**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database.host: "prod-db.example.com"
  app.mode: "production"
  app.replicas: "10"
```

**Result:**
```yaml
data:
  database.host: "prod-db.example.com"  # Updated
  database.port: "5432"                 # Kept
  app.mode: "production"                # Updated
  app.replicas: "10"                    # Added
```

## JSON 6902 with Dictionaries

JSON 6902 provides more explicit control over dictionary operations.

### Adding Keys

```yaml
- op: add
  path: /metadata/labels/environment
  value: production
```

### Replacing Keys

```yaml
- op: replace
  path: /metadata/labels/version
  value: v2.0.0
```

### Removing Keys

```yaml
- op: remove
  path: /metadata/labels/old-label
```

## Example 5: Complex Label Management

**Scenario**: Add production labels, update version, remove temporary label.

**Patch (manage-labels.yaml):**
```yaml
- op: add
  path: /metadata/labels/environment
  value: production

- op: add
  path: /metadata/labels/tier
  value: frontend

- op: replace
  path: /metadata/labels/version
  value: v2.0.0

- op: remove
  path: /metadata/labels/temporary
```

## Example 6: Environment Variables Dictionary

**Scenario**: Add multiple environment variables as a dictionary.

**Base:**
```yaml
spec:
  template:
    spec:
      containers:
      - name: webapp
        envFrom:
        - configMapRef:
            name: base-config
```

**Patch:**
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
        envFrom:
        - configMapRef:
            name: prod-config
        - secretRef:
            name: prod-secrets
```

## Example 7: Nested Dictionaries

**Base:**
```yaml
spec:
  template:
    spec:
      securityContext:
        fsGroup: 1000
```

**Patch:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  template:
    spec:
      securityContext:
        runAsUser: 1000
        runAsNonRoot: true
        fsGroup: 2000  # Updates existing
```

**Result:**
```yaml
securityContext:
  fsGroup: 2000          # Updated
  runAsUser: 1000        # Added
  runAsNonRoot: true     # Added
```

## Practical Examples

### Production Labels Set

**overlays/prod/labels-patch.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  labels:
    environment: production
    tier: frontend
    criticality: high
    team: platform
    cost-center: engineering
    compliance: pci-dss
spec:
  template:
    metadata:
      labels:
        environment: production
        tier: frontend
```

### Monitoring Annotations

**overlays/prod/monitoring-patch.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
    grafana.dashboard.id: "webapp-prod"
    alert.email: "oncall@example.com"
```

### Resource Specifications

**overlays/prod/resources-patch.yaml:**
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
            ephemeral-storage: "1Gi"
          limits:
            memory: "1Gi"
            cpu: "1000m"
            ephemeral-storage: "2Gi"
```

## Removing Dictionary Keys

### Strategic Merge - Directive

Use special directive to remove:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  labels:
    temporary-label: null  # Remove this label
```

**Note**: This doesn't always work reliably. Better to use JSON 6902.

### JSON 6902 - Remove Operation

```yaml
- op: remove
  path: /metadata/labels/temporary-label
```

Much more reliable!

## Complete Example

**Base (base/deployment.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  labels:
    app: webapp
  annotations:
    created-by: developer
spec:
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: webapp
        image: nginx:1.19
        resources:
          requests:
            memory: "128Mi"
```

**Patch (overlays/prod/enrich-metadata.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  labels:
    environment: production
    tier: frontend
    version: v2.0.0
  annotations:
    prometheus.io/scrape: "true"
    deployment.date: "2024-01-10"
spec:
  template:
    metadata:
      labels:
        environment: production
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

**Result:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  labels:
    app: webapp                    # Original
    environment: production         # Added
    tier: frontend                  # Added
    version: v2.0.0                # Added
  annotations:
    created-by: developer          # Original
    prometheus.io/scrape: "true"   # Added
    deployment.date: "2024-01-10"  # Added
spec:
  template:
    metadata:
      labels:
        app: webapp                # Original
        environment: production     # Added
    spec:
      containers:
      - name: webapp
        image: nginx:1.19
        resources:
          requests:
            memory: "512Mi"         # Updated
            cpu: "500m"            # Added
          limits:                  # All added
            memory: "1Gi"
            cpu: "1000m"
```

## Best Practices

### 1. Group Related Changes

```
overlays/prod/patches/
├── labels.yaml           # All label changes
├── annotations.yaml      # All annotation changes
├── resources.yaml        # All resource changes
└── security.yaml         # All security changes
```

### 2. Use Consistent Naming

```yaml
# Good - descriptive labels
labels:
  app: webapp
  environment: production
  team: platform
  tier: frontend

# Avoid - vague labels
labels:
  label1: value1
  label2: value2
```

### 3. Document Label Meanings

```yaml
# overlays/prod/labels-patch.yaml
# Labels follow company tagging policy:
# - environment: deployment environment
# - team: owning team
# - cost-center: billing allocation
# - tier: application tier
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  labels:
    environment: production
    team: platform
    cost-center: engineering
    tier: frontend
```

### 4. Validate Label Keys

Use valid Kubernetes label syntax:
- Maximum 63 characters
- Must start and end with alphanumeric
- Can contain `-`, `_`, `.`

## Troubleshooting

### Issue: Labels not applied to pods

**Problem:**
```yaml
metadata:
  labels:
    environment: production  # Only on deployment
```

**Solution:**
```yaml
metadata:
  labels:
    environment: production
spec:
  template:
    metadata:
      labels:
        environment: production  # Also on pod template
```

### Issue: Annotation too long

Annotations can be much longer than labels. If you have very long annotations, they're fine!

### Issue: Special characters in keys

```yaml
# Works
annotations:
  example.com/config: "value"
  app.kubernetes.io/name: "webapp"

# Doesn't work
annotations:
  invalid key!: "value"  # Spaces and ! not allowed
```

## Quick Reference

### Strategic Merge - Add/Update
```yaml
metadata:
  labels:
    new-key: new-value
```

### JSON 6902 - Add
```yaml
- op: add
  path: /metadata/labels/new-key
  value: new-value
```

### JSON 6902 - Update
```yaml
- op: replace
  path: /metadata/labels/existing-key
  value: new-value
```

### JSON 6902 - Remove
```yaml
- op: remove
  path: /metadata/labels/old-key
```

## Next Steps

Now you understand dictionary patching:
- ✅ How strategic merge handles dictionaries
- ✅ Adding and updating keys
- ✅ Removing keys with JSON 6902
- ✅ Best practices for labels and annotations

Next, we'll learn about **patching lists and arrays**! 🚀
