# Lab: Patches

## Lab Overview

Practice all three patch types (Strategic Merge, JSON 6902, and Inline) to customize a web application deployment.

**Time Required:** 40-50 minutes

## Objectives

- ✅ Create strategic merge patches
- ✅ Use JSON 6902 patches
- ✅ Apply inline patches
- ✅ Work with dictionaries and lists
- ✅ Add sidecars and volumes
- ✅ Modify resources and environment variables

## Prerequisites

- kubectl installed
- Completed previous labs
- Understanding of patches

## Lab Scenario

Deploy a web application that needs:
- **Dev**: Basic configuration, debug enabled
- **Staging**: Monitoring sidecar, enhanced resources
- **Prod**: Full security, monitoring, backup volumes, high resources

## Part 1: Create Base

### Step 1: Initialize

```bash
mkdir -p patches-lab/{base,overlays/{dev,staging,prod}}
cd patches-lab
```

### Step 2: Create Base Deployment

Create `base/deployment.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  labels:
    app: webapp
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
          name: http
        env:
        - name: ENV
          value: base
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```
</details>

### Step 3: Create Base Service

Create `base/service.yaml`:

<details>
<summary>Solution</summary>

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
  type: ClusterIP
```
</details>

### Step 4: Create Base Kustomization

Create `base/kustomization.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml
```
</details>

**✅ Checkpoint:** `kubectl kustomize base/` should work.

## Part 2: Development Overlay (Strategic Merge)

### Step 5: Add Debug Environment Variables

Create `overlays/dev/add-debug-env.yaml`:

**Requirements:**
- Add DEBUG=true
- Add LOG_LEVEL=debug
- Update ENV to "development"

<details>
<summary>Solution</summary>

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
        - name: ENV
          value: development
        - name: DEBUG
          value: "true"
        - name: LOG_LEVEL
          value: debug
```
</details>

### Step 6: Create Dev Kustomization

Create `overlays/dev/kustomization.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: development
namePrefix: dev-

patchesStrategicMerge:
- add-debug-env.yaml
```
</details>

**✅ Checkpoint:** Verify DEBUG env var is present.

## Part 3: Staging Overlay (JSON 6902)

### Step 7: Add Monitoring Sidecar

Create `overlays/staging/add-sidecar.yaml`:

**Requirements:** Use JSON 6902 to append a monitoring container:
- name: prometheus-exporter
- image: prom/node-exporter:latest
- port: 9100

<details>
<summary>Solution</summary>

```yaml
- op: add
  path: /spec/template/spec/containers/-
  value:
    name: prometheus-exporter
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
</details>

### Step 8: Update Resources

Create `overlays/staging/update-resources.yaml`:

**Requirements:** Use JSON 6902 to update webapp container resources:
- memory request: 256Mi
- memory limit: 512Mi

<details>
<summary>Solution</summary>

```yaml
- op: replace
  path: /spec/template/spec/containers/0/resources/requests/memory
  value: "256Mi"

- op: replace
  path: /spec/template/spec/containers/0/resources/limits/memory
  value: "512Mi"
```
</details>

### Step 9: Create Staging Kustomization

Create `overlays/staging/kustomization.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: staging
namePrefix: staging-

patchesJson6902:
- target:
    kind: Deployment
    name: webapp
  path: add-sidecar.yaml
- target:
    kind: Deployment
    name: webapp
  path: update-resources.yaml
```
</details>

**✅ Checkpoint:** Verify 2 containers and updated memory.

## Part 4: Production Overlay (Mixed Patches)

### Step 10: Add Production Labels (Strategic Merge)

Create `overlays/prod/prod-labels.yaml`:

**Requirements:**
- environment: production
- tier: frontend
- criticality: high

<details>
<summary>Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  labels:
    environment: production
    tier: frontend
    criticality: high
spec:
  template:
    metadata:
      labels:
        environment: production
```
</details>

### Step 11: Add Security Context (Inline Patch)

Create `overlays/prod/kustomization.yaml` with inline patch:

**Requirements:** Add security context:
- runAsNonRoot: true
- runAsUser: 1000
- readOnlyRootFilesystem: true

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: production
namePrefix: prod-

patchesStrategicMerge:
- prod-labels.yaml

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
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            fsGroup: 1000
          containers:
          - name: webapp
            securityContext:
              readOnlyRootFilesystem: true
              allowPrivilegeEscalation: false
```
</details>

### Step 12: Add Volumes (Strategic Merge)

Create `overlays/prod/add-volumes.yaml`:

**Requirements:**
- Add volume "data" (emptyDir)
- Mount to /var/data in webapp container

<details>
<summary>Solution</summary>

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
        - name: data
          mountPath: /var/data
      volumes:
      - name: data
        emptyDir: {}
```
</details>

### Step 13: Update Production Kustomization

Update `overlays/prod/kustomization.yaml` to include volumes patch:

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: production
namePrefix: prod-

replicas:
- name: webapp
  count: 10

patchesStrategicMerge:
- prod-labels.yaml
- add-volumes.yaml

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
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            fsGroup: 1000
          containers:
          - name: webapp
            securityContext:
              readOnlyRootFilesystem: true
              allowPrivilegeEscalation: false
            resources:
              requests:
                memory: "512Mi"
                cpu: "500m"
              limits:
                memory: "1Gi"
                cpu: "1000m"
```
</details>

## Part 5: Validation

### Step 14: Compare All Environments

```bash
echo "=== DEV ==="
kubectl kustomize overlays/dev/ | grep -E "name: |namespace: |DEBUG|LOG_LEVEL"

echo "=== STAGING ==="
kubectl kustomize overlays/staging/ | grep -E "containers:" -A 2

echo "=== PROD ==="
kubectl kustomize overlays/prod/ | grep -E "replicas: |security|volume"
```

### Step 15: Verify Patches

Dev environment should have:
- [ ] DEBUG=true env var
- [ ] LOG_LEVEL=debug env var

Staging environment should have:
- [ ] 2 containers (webapp + prometheus-exporter)
- [ ] Updated memory: 256Mi request, 512Mi limit

Production environment should have:
- [ ] 10 replicas
- [ ] Security context configured
- [ ] Volume mounted
- [ ] Production labels

## Part 6: Apply (Optional)

```bash
kubectl create namespace development staging production
kubectl apply -k overlays/dev/
kubectl apply -k overlays/staging/
kubectl apply -k overlays/prod/
```

### Verify

```bash
# Check dev env vars
kubectl get deployment -n development dev-webapp -o jsonpath='{.spec.template.spec.containers[0].env}' | jq

# Check staging containers
kubectl get deployment -n staging staging-webapp -o jsonpath='{.spec.template.spec.containers[*].name}'

# Check prod replicas and security
kubectl get deployment -n production prod-webapp -o yaml | grep -E "replicas:|securityContext:" -A 3
```

## Part 7: Advanced Challenges

### Challenge 1: Remove Limit

Use JSON 6902 to remove CPU limit from dev environment.

<details>
<summary>Hint</summary>

```yaml
- op: remove
  path: /spec/template/spec/containers/0/resources/limits/cpu
```
</details>

### Challenge 2: Add Init Container

Add an init container to production that runs database migrations.

### Challenge 3: Conditional Environment Variables

Add different database URLs for each environment using patches.

### Challenge 4: Add Health Checks

Add liveness and readiness probes to production only.

## Cleanup

```bash
kubectl delete -k overlays/dev/
kubectl delete -k overlays/staging/
kubectl delete -k overlays/prod/
kubectl delete namespace development staging production
```

## Validation Checklist

- [ ] Base configuration created
- [ ] Dev: Strategic merge patch for env vars
- [ ] Staging: JSON 6902 patch for sidecar
- [ ] Staging: JSON 6902 patch for resources
- [ ] Prod: Strategic merge for labels
- [ ] Prod: Inline patch for security
- [ ] Prod: Strategic merge for volumes
- [ ] All patches apply without errors
- [ ] Configurations validated

## Summary

In this lab, you practiced:
- ✅ Strategic Merge patches (easy to read)
- ✅ JSON 6902 patches (precise control)
- ✅ Inline patches (modern approach)
- ✅ Dictionary patches (labels, annotations)
- ✅ List patches (env vars, containers, volumes)
- ✅ Combining multiple patch types

Excellent work! 🎉 Next: Overlays! 🚀
