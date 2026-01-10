# Lab: Overlays

## Lab Overview

Build a complete multi-environment application deployment using base and overlay pattern with increasing complexity across environments.

**Time Required:** 45-60 minutes

## Objectives

- ✅ Create a shared base configuration
- ✅ Build dev overlay with minimal resources
- ✅ Build staging overlay with monitoring
- ✅ Build production overlay with full features
- ✅ Understand overlay composition
- ✅ Use nested overlays

## Prerequisites

- kubectl installed
- Completed previous labs
- Understanding of overlays concept

## Lab Scenario

Deploy an e-commerce application with:
- **Backend API** (nginx serving API)
- **Database** (redis)
- **Requirements:**
  - Dev: Minimal setup, debug enabled
  - Staging: Monitoring enabled, medium resources
  - Prod: High availability, security, monitoring, autoscaling

## Part 1: Create Base Configuration

### Step 1: Initialize Directory Structure

```bash
mkdir -p ecommerce/{base,overlays/{dev,staging,prod}}
cd ecommerce
```

### Step 2: Create Base API Deployment

Create `base/api-deployment.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: ecommerce
    component: api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ecommerce
      component: api
  template:
    metadata:
      labels:
        app: ecommerce
        component: api
    spec:
      containers:
      - name: api
        image: nginx:1.19
        ports:
        - containerPort: 80
          name: http
        env:
        - name: REDIS_HOST
          value: redis
        - name: REDIS_PORT
          value: "6379"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```
</details>

### Step 3: Create Base API Service

Create `base/api-service.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api
  labels:
    app: ecommerce
    component: api
spec:
  selector:
    app: ecommerce
    component: api
  ports:
  - port: 80
    targetPort: 80
    name: http
  type: ClusterIP
```
</details>

### Step 4: Create Base Redis Deployment

Create `base/redis-deployment.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  labels:
    app: ecommerce
    component: database
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ecommerce
      component: database
  template:
    metadata:
      labels:
        app: ecommerce
        component: database
    spec:
      containers:
      - name: redis
        image: redis:6-alpine
        ports:
        - containerPort: 6379
          name: redis
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
```
</details>

### Step 5: Create Base Redis Service

Create `base/redis-service.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis
  labels:
    app: ecommerce
    component: database
spec:
  selector:
    app: ecommerce
    component: database
  ports:
  - port: 6379
    targetPort: 6379
    name: redis
  type: ClusterIP
```
</details>

### Step 6: Create Base Kustomization

Create `base/kustomization.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- api-deployment.yaml
- api-service.yaml
- redis-deployment.yaml
- redis-service.yaml

commonLabels:
  app: ecommerce
```
</details>

**✅ Checkpoint:** `kubectl kustomize base/` should produce all resources.

## Part 2: Development Overlay

### Step 7: Create Dev Overlay

Create `overlays/dev/kustomization.yaml`:

**Requirements:**
- Namespace: `ecommerce-dev`
- Name prefix: `dev-`
- API replicas: 1
- Redis replicas: 1
- Use alpine images
- Add debug labels

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: ecommerce-dev

namePrefix: dev-

commonLabels:
  environment: development
  debug: "true"

replicas:
- name: api
  count: 1
- name: redis
  count: 1

images:
- name: nginx
  newTag: 1.19-alpine
- name: redis
  newTag: 6-alpine

patches:
- target:
    kind: Deployment
    name: api
  patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: api
    spec:
      template:
        spec:
          containers:
          - name: api
            env:
            - name: ENV
              value: development
            - name: DEBUG
              value: "true"
            - name: LOG_LEVEL
              value: debug
```
</details>

**✅ Checkpoint:** Verify dev overlay has debug env vars and 1 replica.

## Part 3: Staging Overlay

### Step 8: Add Monitoring Sidecar

Create `overlays/staging/add-monitoring.yaml`:

**Requirements:** Add prometheus-exporter sidecar to API

<details>
<summary>Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
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
</details>

### Step 9: Create Staging Kustomization

Create `overlays/staging/kustomization.yaml`:

**Requirements:**
- Namespace: `ecommerce-staging`
- Prefix: `staging-`
- API replicas: 3
- Redis replicas: 2
- Medium resources
- Monitoring labels

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: ecommerce-staging

namePrefix: staging-

commonLabels:
  environment: staging
  monitoring: enabled

replicas:
- name: api
  count: 3
- name: redis
  count: 2

patchesStrategicMerge:
- add-monitoring.yaml

patches:
- target:
    kind: Deployment
    name: api
  patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: api
    spec:
      template:
        spec:
          containers:
          - name: api
            resources:
              requests:
                memory: "256Mi"
                cpu: "250m"
              limits:
                memory: "512Mi"
                cpu: "500m"
- target:
    kind: Deployment
    name: redis
  patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: redis
    spec:
      template:
        spec:
          containers:
          - name: redis
            resources:
              requests:
                memory: "128Mi"
                cpu: "100m"
              limits:
                memory: "256Mi"
                cpu: "200m"
```
</details>

**✅ Checkpoint:** Verify 2 containers in API pod and updated resources.

## Part 4: Production Overlay

### Step 10: Create Production HPA

Create `overlays/prod/hpa.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 5
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```
</details>

### Step 11: Add Production Security

Create `overlays/prod/security-patch.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: api
        securityContext:
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
```
</details>

### Step 12: Create Production Kustomization

Create `overlays/prod/kustomization.yaml`:

**Requirements:**
- Namespace: `ecommerce-prod`
- Prefix: `prod-`
- HPA enabled
- Security hardened
- High resources
- Private registry
- Production labels

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base
- hpa.yaml

namespace: ecommerce-prod

namePrefix: prod-

commonLabels:
  environment: production
  tier: critical
  monitoring: enabled

commonAnnotations:
  managed-by: kustomize
  contact: ops@example.com

images:
- name: nginx
  newName: my-registry.io/nginx
  newTag: 1.19
- name: redis
  newName: my-registry.io/redis
  newTag: 6-alpine

patchesStrategicMerge:
- security-patch.yaml

patches:
- target:
    kind: Deployment
    name: api
  patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: api
    spec:
      replicas: 5
      template:
        spec:
          containers:
          - name: api
            env:
            - name: ENV
              value: production
            - name: LOG_LEVEL
              value: info
            resources:
              requests:
                memory: "512Mi"
                cpu: "500m"
              limits:
                memory: "1Gi"
                cpu: "1000m"
- target:
    kind: Deployment
    name: redis
  patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: redis
    spec:
      replicas: 3
      template:
        spec:
          containers:
          - name: redis
            resources:
              requests:
                memory: "256Mi"
                cpu: "200m"
              limits:
                memory: "512Mi"
                cpu: "400m"
```
</details>

**✅ Checkpoint:** Verify HPA, security context, and production resources.

## Part 5: Validation

### Step 13: Compare All Environments

```bash
echo "=== DEV ==="
kubectl kustomize overlays/dev/ | grep -E "namespace: |name: dev-|replicas: |DEBUG"

echo "=== STAGING ==="
kubectl kustomize overlays/staging/ | grep -E "namespace: |name: staging-|replicas: |monitoring"

echo "=== PROD ==="
kubectl kustomize overlays/prod/ | grep -E "namespace: |name: prod-|HorizontalPodAutoscaler|securityContext:"
```

### Step 14: Verify Differences

Dev should have:
- [ ] 1 API replica
- [ ] DEBUG=true
- [ ] development namespace
- [ ] Alpine images

Staging should have:
- [ ] 3 API replicas
- [ ] 2 Redis replicas
- [ ] Monitoring sidecar
- [ ] Medium resources

Production should have:
- [ ] 5 API replicas (base for HPA)
- [ ] HPA configured
- [ ] Security context
- [ ] Private registry images
- [ ] High resources

## Part 6: Apply (Optional)

```bash
kubectl create namespace ecommerce-dev ecommerce-staging ecommerce-prod

kubectl apply -k overlays/dev/
kubectl apply -k overlays/staging/
kubectl apply -k overlays/prod/
```

### Verify Deployments

```bash
# Dev
kubectl get all -n ecommerce-dev

# Staging
kubectl get all -n ecommerce-staging

# Production
kubectl get all -n ecommerce-prod
kubectl get hpa -n ecommerce-prod
```

## Part 7: Advanced - Nested Overlays

### Step 15: Create Regional Production Overlays

```bash
mkdir -p overlays/prod-regions/{us-east,eu-west}
```

**overlays/prod-regions/us-east/kustomization.yaml:**

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../prod

nameSuffix: -use1

commonLabels:
  region: us-east-1

patches:
- target:
    kind: Service
    name: api
  patch: |-
    metadata:
      annotations:
        service.beta.kubernetes.io/aws-load-balancer-type: nlb
        service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
```
</details>

**overlays/prod-regions/eu-west/kustomization.yaml:**

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../prod

nameSuffix: -euw1

commonLabels:
  region: eu-west-1

patches:
- target:
    kind: Deployment
  patch: |-
    spec:
      template:
        spec:
          affinity:
            nodeAffinity:
              requiredDuringSchedulingIgnoredDuringExecution:
                nodeSelectorTerms:
                - matchExpressions:
                  - key: topology.kubernetes.io/region
                    operator: In
                    values:
                    - eu-west-1
```
</details>

### Step 16: Test Regional Overlays

```bash
kubectl kustomize overlays/prod-regions/us-east/
kubectl kustomize overlays/prod-regions/eu-west/
```

## Part 8: Comparison Table

| Feature | Dev | Staging | Prod |
|---------|-----|---------|------|
| API Replicas | 1 | 3 | 5 (HPA: 5-20) |
| Redis Replicas | 1 | 2 | 3 |
| API Memory | 128Mi/256Mi | 256Mi/512Mi | 512Mi/1Gi |
| Debug | Enabled | Disabled | Disabled |
| Monitoring | No | Sidecar | Sidecar |
| HPA | No | No | Yes |
| Security | Basic | Basic | Hardened |
| Images | Alpine | Standard | Private Registry |

## Cleanup

```bash
kubectl delete -k overlays/dev/
kubectl delete -k overlays/staging/
kubectl delete -k overlays/prod/
kubectl delete namespace ecommerce-dev ecommerce-staging ecommerce-prod
```

## Validation Checklist

- [ ] Base configuration created with API and Redis
- [ ] Dev overlay: 1 replica, debug enabled, alpine images
- [ ] Staging overlay: 3 replicas, monitoring sidecar, medium resources
- [ ] Prod overlay: 5 replicas, HPA, security, high resources
- [ ] Regional overlays: US and EU variants
- [ ] All overlays build successfully
- [ ] Differences clearly visible

## Summary

In this lab, you practiced:
- ✅ Creating a shared base configuration
- ✅ Building environment-specific overlays
- ✅ Using transformers (namespace, replicas, images)
- ✅ Applying patches for customization
- ✅ Adding environment-specific resources (HPA)
- ✅ Creating nested overlays for regions
- ✅ Comparing configuration differences

Excellent work! 🎉 Next: Components! 🚀
