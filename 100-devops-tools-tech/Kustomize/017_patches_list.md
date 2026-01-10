# Patches - Working with Lists

## Overview

Lists (arrays) in Kubernetes manifests require special handling. Understanding list patching strategies is essential for modifying containers, environment variables, volumes, and other array-based configurations.

## Challenge with Lists

Unlike dictionaries, lists don't have natural keys for merging. Kustomize uses different strategies based on the field type.

## Strategic Merge with Lists

Strategic merge uses **merge keys** to identify list items.

### Common Merge Keys

| Field | Merge Key | Example |
|-------|-----------|---------|
| **containers** | `name` | Containers merged by name |
| **env** | `name` | Environment variables by name |
| **ports** | `containerPort` | Ports by port number |
| **volumeMounts** | `mountPath` | Mounts by path |
| **volumes** | `name` | Volumes by name |

### How It Works

When strategic merge sees a list with a merge key, it:
1. Matches items by the merge key
2. Merges matching items
3. Appends non-matching items

## Example 1: Adding Environment Variables

**Base:**
```yaml
spec:
  template:
    spec:
      containers:
      - name: webapp
        env:
        - name: ENV
          value: base
        - name: VERSION
          value: "1.0"
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
        env:
        - name: ENVIRONMENT
          value: production
        - name: DEBUG
          value: "false"
```

**Result:**
```yaml
env:
- name: ENV              # Original
  value: base
- name: VERSION          # Original
  value: "1.0"
- name: ENVIRONMENT      # Added
  value: production
- name: DEBUG            # Added
  value: "false"
```

## Example 2: Updating Existing Environment Variable

**Patch:**
```yaml
spec:
  template:
    spec:
      containers:
      - name: webapp
        env:
        - name: VERSION  # Same name = will merge
          value: "2.0"
```

**Result:**
```yaml
env:
- name: ENV
  value: base
- name: VERSION
  value: "2.0"  # Updated!
```

## Example 3: Adding Container to Pod

**Base:**
```yaml
spec:
  template:
    spec:
      containers:
      - name: webapp
        image: nginx:1.19
```

**Patch (add-sidecar.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  template:
    spec:
      containers:
      - name: logging-agent
        image: fluentd:latest
        volumeMounts:
        - name: logs
          mountPath: /var/log
```

**Result:**
```yaml
containers:
- name: webapp           # Original
  image: nginx:1.19
- name: logging-agent    # Added (different name)
  image: fluentd:latest
  volumeMounts:
  - name: logs
    mountPath: /var/log
```

## Example 4: Adding Ports

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
        ports:
        - containerPort: 8080
          name: metrics
          protocol: TCP
        - containerPort: 9090
          name: admin
          protocol: TCP
```

Adds new ports to the container.

## JSON 6902 with Lists

JSON 6902 provides precise control over list operations using array indices and special `-` notation.

### Array Index Notation

```
/spec/template/spec/containers/0     → First container
/spec/template/spec/containers/1     → Second container
/spec/template/spec/containers/-     → Append to end
```

### Example 5: Append to List

**Add environment variable to end of list:**
```yaml
- op: add
  path: /spec/template/spec/containers/0/env/-
  value:
    name: NEW_VAR
    value: "new_value"
```

The `-` means "append to array".

### Example 6: Insert at Specific Position

**Insert at beginning:**
```yaml
- op: add
  path: /spec/template/spec/containers/0/env/0
  value:
    name: FIRST_VAR
    value: "first"
```

### Example 7: Remove from List

**Remove second environment variable:**
```yaml
- op: remove
  path: /spec/template/spec/containers/0/env/1
```

**Remove last element:**
```yaml
- op: remove
  path: /spec/template/spec/containers/0/env/-
```

### Example 8: Replace List Item

**Replace first environment variable:**
```yaml
- op: replace
  path: /spec/template/spec/containers/0/env/0
  value:
    name: UPDATED_VAR
    value: "updated"
```

## Complete Examples

### Example 9: Add Multiple Environment Variables

**JSON 6902 Patch:**
```yaml
- op: add
  path: /spec/template/spec/containers/0/env/-
  value:
    name: DATABASE_URL
    value: "postgresql://prod-db:5432"

- op: add
  path: /spec/template/spec/containers/0/env/-
  value:
    name: CACHE_URL
    value: "redis://prod-cache:6379"

- op: add
  path: /spec/template/spec/containers/0/env/-
  value:
    name: LOG_LEVEL
    value: "info"
```

### Example 10: Add Init Container

**Strategic Merge Patch:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  template:
    spec:
      initContainers:
      - name: init-db
        image: busybox:1.35
        command: ['sh', '-c', 'until nc -z db 5432; do sleep 1; done']
```

### Example 11: Add Volume and Mount

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
        volumeMounts:
        - name: config
          mountPath: /etc/config
          readOnly: true
        - name: data
          mountPath: /var/data
      volumes:
      - name: config
        configMap:
          name: app-config
      - name: data
        emptyDir: {}
```

### Example 12: Add Multiple Containers

**Patch (add-sidecars.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  template:
    spec:
      containers:
      - name: logging
        image: fluentd:latest
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
      - name: monitoring
        image: prometheus-exporter:latest
        ports:
        - containerPort: 9090
        resources:
          requests:
            memory: "32Mi"
            cpu: "25m"
```

## Complex List Scenarios

### Scenario 1: Conditional Environment Variables

**Base has:**
```yaml
env:
- name: ENV
  value: base
```

**Dev adds:**
```yaml
env:
- name: DEBUG
  value: "true"
```

**Prod adds:**
```yaml
env:
- name: DEBUG
  value: "false"
- name: METRICS_ENABLED
  value: "true"
```

Each overlay can add different variables!

### Scenario 2: Resource Limits Per Container

**Patch for specific container:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  template:
    spec:
      containers:
      - name: webapp  # Matches by name
        resources:
          limits:
            memory: "1Gi"
            cpu: "1000m"
      - name: sidecar  # Matches by name
        resources:
          limits:
            memory: "256Mi"
            cpu: "200m"
```

## Removing List Items

### Strategic Merge - Limitations

Strategic merge is NOT good at removing list items. Use JSON 6902 instead.

### JSON 6902 - Remove by Index

```yaml
# Remove first environment variable
- op: remove
  path: /spec/template/spec/containers/0/env/0

# Remove second port
- op: remove
  path: /spec/template/spec/containers/0/ports/1
```

### JSON 6902 - Remove Multiple Items

```yaml
# Remove from end to beginning to avoid index shifts
- op: remove
  path: /spec/template/spec/containers/0/env/2

- op: remove
  path: /spec/template/spec/containers/0/env/1
```

**Important**: Remove from high indices to low to avoid shifting!

## Replace Directive (Strategic Merge)

For complete list replacement:

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
        - name: ONLY_VAR
          value: "only_value"
```

This replaces the ENTIRE env list for that container.

## Practical Examples

### Add Monitoring Sidecar

**overlays/prod/add-monitoring.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  template:
    spec:
      containers:
      - name: prometheus-exporter
        image: prom/node-exporter:latest
        ports:
        - containerPort: 9100
          name: metrics
        resources:
          requests:
            memory: "32Mi"
            cpu: "25m"
          limits:
            memory: "64Mi"
            cpu: "50m"
```

### Add Security Context

**overlays/prod/security-patch.yaml:**
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
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
          readOnlyRootFilesystem: true
```

### Add Health Checks

**overlays/prod/health-checks.yaml:**
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
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Best Practices

### 1. Use Strategic Merge for Adding

```yaml
# Easy to read and maintain
spec:
  template:
    spec:
      containers:
      - name: webapp
        env:
        - name: NEW_VAR
          value: "value"
```

### 2. Use JSON 6902 for Removing

```yaml
# Explicit and reliable
- op: remove
  path: /spec/template/spec/containers/0/env/2
```

### 3. Name Your List Items

```yaml
# Good - has names
containers:
- name: webapp
- name: sidecar

env:
- name: DATABASE_URL
- name: CACHE_URL

# Avoid - anonymous items are harder to patch
ports:
- 8080
- 9090
```

### 4. Group Related Additions

```yaml
# Add all env vars together
env:
- name: DB_HOST
  value: "db.example.com"
- name: DB_PORT
  value: "5432"
- name: DB_NAME
  value: "production"
```

### 5. Use Separate Patches for Different Concerns

```
overlays/prod/
├── add-sidecars.yaml        # Sidecar containers
├── add-volumes.yaml         # Volume config
├── add-env-vars.yaml        # Environment variables
└── add-health-checks.yaml   # Probes
```

## Troubleshooting

### Issue: Duplicate items in list

**Problem:** Both base and patch have item with same merge key.

**Solution:** They will merge! If you want to replace, ensure keys match exactly.

### Issue: Wrong array index

**Problem:**
```yaml
- op: remove
  path: /spec/template/spec/containers/0/env/5  # Only 3 items exist
```

**Solution:** Check the current list length first.

### Issue: Environment variable not added

**Problem:** Using wrong container index.

**Solution:**
```bash
# Check container order
kubectl kustomize . | yq eval '.spec.template.spec.containers[].name'
```

## Quick Reference

### Strategic Merge - Add to List
```yaml
containers:
- name: new-container
  image: new-image
```

### JSON 6902 - Append
```yaml
- op: add
  path: /spec/template/spec/containers/-
  value:
    name: new-container
    image: new-image
```

### JSON 6902 - Insert at Index
```yaml
- op: add
  path: /spec/template/spec/containers/0
  value:
    name: first-container
    image: image
```

### JSON 6902 - Remove
```yaml
- op: remove
  path: /spec/template/spec/containers/1
```

### JSON 6902 - Replace
```yaml
- op: replace
  path: /spec/template/spec/containers/0
  value:
    name: updated-container
    image: new-image
```

## Next Steps

Now you understand list patching:
- ✅ Strategic merge with merge keys
- ✅ JSON 6902 for precise array operations
- ✅ Adding, removing, and replacing list items
- ✅ Best practices for different list types

Next, let's practice with a **hands-on patches lab**! 🚀
