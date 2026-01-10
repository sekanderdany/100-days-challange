# Lab: Components

## Lab Overview

Build reusable, optional components for monitoring, logging, security, and high availability. Mix and match components across different environments.

**Time Required:** 50-60 minutes

## Objectives

- ✅ Create reusable components
- ✅ Understand `kind: Component`
- ✅ Mix multiple components
- ✅ Apply components selectively
- ✅ Build component library

## Prerequisites

- kubectl installed
- Completed previous labs
- Understanding of components concept

## Lab Scenario

Build a payment processing application with optional features:
- **Monitoring** (Prometheus metrics)
- **Logging** (Fluentd aggregation)
- **Security** (Hardened policies)
- **High Availability** (Pod disruption budget, affinity)
- **Backup** (Scheduled backups)

Deploy with different feature combinations:
- **Dev:** Logging only
- **Staging:** Monitoring + Logging
- **Prod:** All features enabled

## Part 1: Create Base Application

### Step 1: Initialize Structure

```bash
mkdir -p payment-app/{base,components/{monitoring,logging,security,ha,backup},overlays/{dev,staging,prod}}
cd payment-app
```

### Step 2: Create Base Deployment

Create `base/deployment.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-api
  labels:
    app: payment
    component: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: payment
      component: api
  template:
    metadata:
      labels:
        app: payment
        component: api
    spec:
      containers:
      - name: api
        image: nginx:1.19
        ports:
        - containerPort: 80
          name: http
        env:
        - name: APP_NAME
          value: payment-api
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
  name: payment-api
  labels:
    app: payment
    component: api
spec:
  selector:
    app: payment
    component: api
  ports:
  - port: 80
    targetPort: 80
    name: http
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

## Part 2: Create Monitoring Component

### Step 5: Create Monitoring Sidecar

Create `components/monitoring/prometheus-sidecar.yaml`:

**Requirements:** Add Prometheus exporter container

<details>
<summary>Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-api
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

### Step 6: Create Metrics Service

Create `components/monitoring/metrics-service.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: payment-api-metrics
  labels:
    app: payment
    component: api
    monitoring: enabled
spec:
  selector:
    app: payment
    component: api
  ports:
  - port: 9100
    targetPort: 9100
    name: metrics
  type: ClusterIP
```
</details>

### Step 7: Create Monitoring Component Kustomization

Create `components/monitoring/kustomization.yaml`:

**Requirements:** 
- kind: Component
- Add monitoring: enabled label
- Include sidecar and service

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

commonLabels:
  monitoring: enabled

commonAnnotations:
  monitoring/scrape: "true"

patchesStrategicMerge:
- prometheus-sidecar.yaml

resources:
- metrics-service.yaml
```
</details>

**✅ Checkpoint:** Component has `kind: Component`.

## Part 3: Create Logging Component

### Step 8: Create Logging Sidecar

Create `components/logging/fluentd-sidecar.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-api
spec:
  template:
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd:latest
        env:
        - name: FLUENT_UID
          value: "0"
        - name: FLUENTD_CONF
          value: fluent.conf
        volumeMounts:
        - name: logs
          mountPath: /var/log
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
      volumes:
      - name: logs
        emptyDir: {}
```
</details>

### Step 9: Create Logging Component Kustomization

Create `components/logging/kustomization.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

commonLabels:
  logging: enabled

commonAnnotations:
  logging/aggregator: fluentd

patchesStrategicMerge:
- fluentd-sidecar.yaml
```
</details>

## Part 4: Create Security Component

### Step 10: Create Security Context Patch

Create `components/security/security-context.yaml`:

**Requirements:**
- runAsNonRoot: true
- runAsUser: 1000
- readOnlyRootFilesystem: true

<details>
<summary>Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-api
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

### Step 11: Create Security Component Kustomization

Create `components/security/kustomization.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

commonLabels:
  security: hardened

commonAnnotations:
  security/policy: strict

patchesStrategicMerge:
- security-context.yaml
```
</details>

## Part 5: Create High Availability Component

### Step 12: Create Pod Disruption Budget

Create `components/ha/pdb.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payment-api
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: payment
      component: api
```
</details>

### Step 13: Create Affinity Rules

Create `components/ha/affinity-patch.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-api
spec:
  template:
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - payment
              topologyKey: kubernetes.io/hostname
```
</details>

### Step 14: Create HA Component Kustomization

Create `components/ha/kustomization.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

commonLabels:
  ha: enabled

resources:
- pdb.yaml

patchesStrategicMerge:
- affinity-patch.yaml
```
</details>

## Part 6: Create Backup Component

### Step 15: Create Backup CronJob

Create `components/backup/backup-cronjob.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: payment-backup
  labels:
    app: payment
    component: backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        metadata:
          labels:
            app: payment
            component: backup
        spec:
          containers:
          - name: backup
            image: busybox:latest
            command:
            - /bin/sh
            - -c
            - echo "Running backup at $(date)"
          restartPolicy: OnFailure
```
</details>

### Step 16: Create Backup Component Kustomization

Create `components/backup/kustomization.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

commonLabels:
  backup: enabled

resources:
- backup-cronjob.yaml
```
</details>

## Part 7: Compose Environments

### Step 17: Create Dev Overlay (Logging Only)

Create `overlays/dev/kustomization.yaml`:

**Requirements:**
- Namespace: payment-dev
- Only logging component
- 1 replica

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: payment-dev

namePrefix: dev-

components:
- ../../components/logging

replicas:
- name: payment-api
  count: 1

commonLabels:
  environment: development
```
</details>

### Step 18: Create Staging Overlay (Monitoring + Logging)

Create `overlays/staging/kustomization.yaml`:

**Requirements:**
- Namespace: payment-staging
- Monitoring + Logging
- 3 replicas

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: payment-staging

namePrefix: staging-

components:
- ../../components/monitoring
- ../../components/logging

replicas:
- name: payment-api
  count: 3

commonLabels:
  environment: staging
```
</details>

### Step 19: Create Production Overlay (All Components)

Create `overlays/prod/kustomization.yaml`:

**Requirements:**
- Namespace: payment-prod
- All components (monitoring, logging, security, ha, backup)
- 10 replicas

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: payment-prod

namePrefix: prod-

components:
- ../../components/monitoring
- ../../components/logging
- ../../components/security
- ../../components/ha
- ../../components/backup

replicas:
- name: payment-api
  count: 10

commonLabels:
  environment: production
  tier: critical

patches:
- target:
    kind: Deployment
    name: payment-api
  patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: payment-api
    spec:
      template:
        spec:
          containers:
          - name: api
            resources:
              requests:
                memory: "512Mi"
                cpu: "500m"
              limits:
                memory: "1Gi"
                cpu: "1000m"
```
</details>

## Part 8: Validation

### Step 20: Build and Compare

```bash
echo "=== DEV (Base + Logging) ==="
kubectl kustomize overlays/dev/ | grep -E "kind: |name: |logging|containers:" -A 1

echo "=== STAGING (Base + Monitoring + Logging) ==="
kubectl kustomize overlays/staging/ | grep -E "kind: |name: |monitoring|logging|containers:" -A 1

echo "=== PROD (Base + All Components) ==="
kubectl kustomize overlays/prod/ | grep -E "kind: |name: |monitoring|security|PodDisruptionBudget|CronJob" -A 1
```

### Step 21: Count Containers

```bash
# Dev: 2 containers (api + fluentd)
kubectl kustomize overlays/dev/ | yq eval 'select(.kind == "Deployment") | .spec.template.spec.containers | length'

# Staging: 3 containers (api + prometheus + fluentd)
kubectl kustomize overlays/staging/ | yq eval 'select(.kind == "Deployment") | .spec.template.spec.containers | length'

# Prod: 3 containers + security + ha + backup
kubectl kustomize overlays/prod/ | grep -E "kind: " | sort | uniq -c
```

### Step 22: Verify Components

Dev should have:
- [ ] logging: enabled label
- [ ] 2 containers (api + fluentd)
- [ ] 1 replica

Staging should have:
- [ ] monitoring: enabled label
- [ ] logging: enabled label
- [ ] 3 containers (api + prometheus + fluentd)
- [ ] metrics-service

Production should have:
- [ ] All component labels
- [ ] 3 containers
- [ ] PodDisruptionBudget
- [ ] Pod anti-affinity
- [ ] Security context
- [ ] Backup CronJob

## Part 9: Apply (Optional)

```bash
kubectl create namespace payment-dev payment-staging payment-prod

kubectl apply -k overlays/dev/
kubectl apply -k overlays/staging/
kubectl apply -k overlays/prod/
```

### Verify

```bash
# Dev: Check containers
kubectl get deployment -n payment-dev dev-payment-api -o jsonpath='{.spec.template.spec.containers[*].name}'

# Staging: Check services
kubectl get svc -n payment-staging

# Prod: Check all resources
kubectl get all,pdb,cronjob -n payment-prod
```

## Part 10: Advanced - Custom Component Combinations

### Challenge 1: QA Environment

Create `overlays/qa/` with:
- Monitoring (for testing)
- Security (like prod)
- No logging (reduce noise)
- 2 replicas

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: payment-qa

components:
- ../../components/monitoring
- ../../components/security

replicas:
- name: payment-api
  count: 2

commonLabels:
  environment: qa
```
</details>

### Challenge 2: Canary Environment

Create component for canary deployments with special labels.

### Challenge 3: Regional Production

Create `overlays/prod-us-east/` and `overlays/prod-eu-west/` that both use prod components but add regional affinity.

## Cleanup

```bash
kubectl delete -k overlays/dev/
kubectl delete -k overlays/staging/
kubectl delete -k overlays/prod/
kubectl delete namespace payment-dev payment-staging payment-prod
```

## Component Comparison Table

| Environment | Monitoring | Logging | Security | HA | Backup | Replicas |
|-------------|------------|---------|----------|----|----- ---|----------|
| Dev | ❌ | ✅ | ❌ | ❌ | ❌ | 1 |
| Staging | ✅ | ✅ | ❌ | ❌ | ❌ | 3 |
| Prod | ✅ | ✅ | ✅ | ✅ | ✅ | 10 |

## Validation Checklist

- [ ] Base deployment and service created
- [ ] Monitoring component with sidecar and metrics service
- [ ] Logging component with fluentd sidecar
- [ ] Security component with hardened policies
- [ ] HA component with PDB and affinity
- [ ] Backup component with CronJob
- [ ] Dev overlay: logging only
- [ ] Staging overlay: monitoring + logging
- [ ] Prod overlay: all components
- [ ] All builds successful

## Summary

In this lab, you practiced:
- ✅ Creating reusable components with `kind: Component`
- ✅ Building component library (monitoring, logging, security, ha, backup)
- ✅ Mixing and matching components per environment
- ✅ Applying components selectively
- ✅ Understanding component composition
- ✅ Building flexible, modular configurations

**Congratulations!** 🎉 You've completed the Kustomize tutorial series! 🚀

## Next Steps

- Apply these patterns to your projects
- Build your own component library
- Share components across teams
- Explore advanced Kustomize features
- Integrate with CI/CD pipelines

**Happy Kustomizing!** 🎊
