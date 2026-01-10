# Components

## What are Components?

**Components** are reusable, optional configuration pieces that can be selectively included in your base or overlays.

Think of components as **plug-and-play features**:
- Enable monitoring? Add monitoring component
- Need logging? Add logging component
- Want security? Add security component

```
base/
components/
  monitoring/      ← Optional monitoring
  logging/         ← Optional logging
  security/        ← Optional security
overlays/
  dev/             ← Uses logging only
  prod/            ← Uses all components
```

## Components vs Overlays

| Feature | Overlays | Components |
|---------|----------|------------|
| Purpose | Environment variants | Optional features |
| Relationship | Mutually exclusive | Can combine multiple |
| Usage | Choose one (dev OR prod) | Mix and match (monitoring + security) |
| Structure | Complete customization | Partial addition |

**Example:**

```yaml
# Overlay: Pick one
overlays/dev/      ← Use dev
overlays/prod/     ← OR use prod

# Component: Mix many
components/
  monitoring/      ← ✓ Include
  logging/         ← ✓ Include  
  security/        ← ✓ Include
  backup/          ← ✗ Skip
```

## When to Use Components

Use components for:
- ✅ **Optional features** (monitoring, logging, backup)
- ✅ **Cross-cutting concerns** (security policies, resource limits)
- ✅ **Conditional additions** (enable in prod, disable in dev)
- ✅ **Reusable patterns** (same monitoring for all apps)

Don't use components for:
- ❌ Environment-specific configs (use overlays)
- ❌ Required resources (include in base)
- ❌ Complete replacements (use patches)

## Component Structure

A component is a directory with a `kustomization.yaml` that has `kind: Component`:

```
components/
└── monitoring/
    ├── kustomization.yaml  (kind: Component)
    ├── prometheus-sidecar.yaml
    └── service-monitor.yaml
```

## Creating a Component

### Example: Monitoring Component

**components/monitoring/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

commonLabels:
  monitoring: enabled

patchesStrategicMerge:
- prometheus-sidecar.yaml

resources:
- service-monitor.yaml
```

**Key difference:** `kind: Component` (not `Kustomization`)

**components/monitoring/prometheus-sidecar.yaml:**

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
```

**components/monitoring/service-monitor.yaml:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp-metrics
spec:
  selector:
    app: webapp
  ports:
  - port: 9100
    name: metrics
```

## Using Components

### In Overlays

**overlays/prod/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

components:
- ../../components/monitoring
- ../../components/logging
- ../../components/security
```

**overlays/dev/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

# Dev: Only logging, no monitoring/security
components:
- ../../components/logging
```

## Complete Example

### Directory Structure

```
myapp/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
├── components/
│   ├── monitoring/
│   │   ├── kustomization.yaml
│   │   ├── prometheus-sidecar.yaml
│   │   └── service-monitor.yaml
│   ├── logging/
│   │   ├── kustomization.yaml
│   │   └── fluentd-sidecar.yaml
│   └── security/
│       ├── kustomization.yaml
│       └── security-context.yaml
└── overlays/
    ├── dev/
    │   └── kustomization.yaml (logging only)
    └── prod/
        └── kustomization.yaml (all components)
```

### Base

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
      - name: webapp
        image: nginx:1.19
        ports:
        - containerPort: 80
```

**base/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml
```

### Component: Monitoring

**components/monitoring/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

commonLabels:
  monitoring: enabled

patchesStrategicMerge:
- prometheus-sidecar.yaml

resources:
- service-monitor.yaml
```

**components/monitoring/prometheus-sidecar.yaml:**

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
```

### Component: Logging

**components/logging/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

commonLabels:
  logging: enabled

patchesStrategicMerge:
- fluentd-sidecar.yaml
```

**components/logging/fluentd-sidecar.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  template:
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd:latest
        volumeMounts:
        - name: logs
          mountPath: /var/log
      volumes:
      - name: logs
        emptyDir: {}
```

### Component: Security

**components/security/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

commonLabels:
  security: hardened

patches:
- target:
    kind: Deployment
  path: security-context.yaml
```

**components/security/security-context.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
      - name: webapp
        securityContext:
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
```

### Using in Dev

**overlays/dev/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: dev

components:
- ../../components/logging

replicas:
- name: webapp
  count: 1
```

**Result:** Dev has base + logging only

### Using in Prod

**overlays/prod/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: prod

components:
- ../../components/monitoring
- ../../components/logging
- ../../components/security

replicas:
- name: webapp
  count: 10
```

**Result:** Prod has base + monitoring + logging + security

## Building with Components

```bash
# Dev: Base + logging
kubectl kustomize overlays/dev/

# Prod: Base + all components
kubectl kustomize overlays/prod/
```

## Component Features

### 1. Labels and Annotations

```yaml
# components/feature-x/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

commonLabels:
  feature-x: enabled

commonAnnotations:
  feature-x/version: "1.0"
```

### 2. Patches

```yaml
# components/resource-limits/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

patches:
- target:
    kind: Deployment
  patch: |-
    spec:
      template:
        spec:
          containers:
          - name: webapp
            resources:
              limits:
                memory: "1Gi"
                cpu: "1000m"
```

### 3. Additional Resources

```yaml
# components/ingress/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

resources:
- ingress.yaml
- certificate.yaml
```

### 4. ConfigMaps/Secrets

```yaml
# components/observability/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

configMapGenerator:
- name: observability-config
  literals:
  - ENABLE_TRACING=true
  - ENABLE_METRICS=true
```

## Real-World Components

### Component: Monitoring

```
components/monitoring/
├── kustomization.yaml
├── prometheus-sidecar.yaml
├── service-monitor.yaml
└── grafana-dashboard.yaml
```

### Component: Backup

```
components/backup/
├── kustomization.yaml
├── backup-cronjob.yaml
└── backup-pvc.yaml
```

### Component: TLS

```
components/tls/
├── kustomization.yaml
├── certificate.yaml
└── tls-secret.yaml
```

### Component: High Availability

```
components/ha/
├── kustomization.yaml
├── pod-disruption-budget.yaml
├── affinity-rules.yaml
└── topology-spread.yaml
```

## Mixing Multiple Components

**overlays/prod-full/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

components:
- ../../components/monitoring
- ../../components/logging
- ../../components/security
- ../../components/backup
- ../../components/tls
- ../../components/ha

namespace: production
replicas:
- name: webapp
  count: 15
```

**Result:** All features enabled!

## Component Order Matters

Components are applied in order:

```yaml
components:
- ../../components/base-security     # Applied first
- ../../components/enhanced-security # Overrides base
```

Later components can override earlier ones.

## Testing Components Individually

```bash
# Test component alone
kubectl kustomize components/monitoring/

# Test base with one component
cd overlays/dev
kubectl kustomize .

# Test with multiple components
cd overlays/prod
kubectl kustomize .
```

## Best Practices

### 1. Make Components Independent

Each component should work standalone:

```yaml
# ✅ Good: Self-contained
components/monitoring/
├── kustomization.yaml
├── prometheus-sidecar.yaml
└── service-monitor.yaml

# ❌ Bad: Depends on other components
components/monitoring/
└── kustomization.yaml (depends on logging component)
```

### 2. Use Clear Naming

```
✅ components/monitoring/
✅ components/security-hardening/
✅ components/tls-enabled/

❌ components/comp1/
❌ components/feature/
```

### 3. Document Component Purpose

Add README in each component:

```markdown
# Monitoring Component

Adds Prometheus metrics collection to deployments.

## Adds:
- Prometheus exporter sidecar
- ServiceMonitor resource
- Metrics service

## Labels:
- monitoring: enabled
```

### 4. Keep Components Focused

One concern per component:

```yaml
# ✅ Good: Single purpose
components/monitoring/    (only monitoring)
components/logging/       (only logging)

# ❌ Bad: Mixed concerns
components/observability/ (monitoring + logging + tracing)
```

## Common Component Patterns

### Pattern 1: Environment Flags

```
components/
├── dev-mode/     (DEBUG=true, verbose logging)
├── staging-mode/ (some debug, monitoring)
└── prod-mode/    (optimized, minimal logging)
```

### Pattern 2: Feature Toggles

```
components/
├── feature-new-ui/
├── feature-beta-api/
└── feature-experimental/
```

### Pattern 3: Compliance

```
components/
├── pci-compliance/
├── hipaa-compliance/
└── gdpr-compliance/
```

## Components vs Other Kustomize Features

| Need | Solution |
|------|----------|
| Environment variants | Overlays |
| Optional features | Components |
| Small modifications | Patches |
| Common config | Base |
| Generated config | Generators |

## Summary

**Components** are:
- ✅ Reusable, optional configurations
- ✅ Can be mixed and matched
- ✅ Applied selectively per environment
- ✅ Independent and focused

**Key Concepts:**
- `kind: Component` in kustomization.yaml
- Referenced in `components:` field
- Can include patches, resources, labels
- Order matters (later overrides earlier)

**Use Cases:**
- Optional monitoring/logging
- Security hardening
- Feature flags
- Compliance requirements
- Cross-cutting concerns

**Next:** Practice with the Components Lab! 🚀
