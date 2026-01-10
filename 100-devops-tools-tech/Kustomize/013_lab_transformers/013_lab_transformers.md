# Lab: Transformers

## Lab Overview

Practice using common transformers and image transformers to configure a multi-container application across three environments.

**Time Required:** 30-40 minutes

## Objectives

- ✅ Apply common labels and annotations
- ✅ Use namespace transformer
- ✅ Apply name prefixes and suffixes
- ✅ Modify replica counts
- ✅ Transform container images
- ✅ Combine multiple transformers

## Prerequisites

- kubectl installed (1.14+)
- Basic Kubernetes knowledge
- Completed "Managing Directories" lab

## Lab Scenario

Deploy a microservices application with:
- **API Service**: Custom application
- **Cache**: Redis
- **Proxy**: Nginx

**Requirements:**
- Dev: 1 replica, alpine images, development namespace
- Staging: 3 replicas, specific versions, staging namespace
- Prod: 10 replicas, production registry, production namespace

## Part 1: Create Base Configuration

### Step 1: Initialize Project

```bash
mkdir -p transformers-lab/base
mkdir -p transformers-lab/overlays/{dev,staging,prod}
cd transformers-lab
```

### Step 2: Create API Deployment

Create `base/api-deployment.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 2
  selector:
    matchLabels:
      component: api
  template:
    metadata:
      labels:
        component: api
    spec:
      containers:
      - name: api
        image: nginx:1.19
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```
</details>

### Step 3: Create Redis Deployment

Create `base/redis-deployment.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      component: cache
  template:
    metadata:
      labels:
        component: cache
    spec:
      containers:
      - name: redis
        image: redis:6.0
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
```
</details>

### Step 4: Create Services

Create `base/api-service.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    component: api
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP
```
</details>

Create `base/redis-service.yaml`:

<details>
<summary>Solution</summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis
spec:
  selector:
    component: cache
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
```
</details>

### Step 5: Create Base Kustomization

Create `base/kustomization.yaml`:

**Requirements:**
- Include all resources
- Add common label: `app: microservices`
- Add common label: `managed-by: kustomize`

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- api-deployment.yaml
- redis-deployment.yaml
- api-service.yaml
- redis-service.yaml

commonLabels:
  app: microservices
  managed-by: kustomize
```
</details>

### Step 6: Test Base

```bash
kubectl kustomize base/
```

**✅ Checkpoint:** Verify 2 Deployments and 2 Services are generated.

## Part 2: Development Overlay

### Step 7: Create Dev Overlay

Create `overlays/dev/kustomization.yaml`:

**Requirements:**
- Reference base
- Namespace: `development`
- Name prefix: `dev-`
- Labels: `environment: dev`, `team: dev-team`
- Annotations: `deployed-by: kustomize`, `env-type: development`
- Replicas: api=1, redis=1
- Images: nginx:1.19-alpine, redis:6.0-alpine

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: development

namePrefix: dev-

commonLabels:
  environment: dev
  team: dev-team

commonAnnotations:
  deployed-by: kustomize
  env-type: development

replicas:
- name: api
  count: 1
- name: redis
  count: 1

images:
- name: nginx
  newTag: "1.19-alpine"
- name: redis
  newTag: "6.0-alpine"
```
</details>

### Step 8: Validate Dev

```bash
kubectl kustomize overlays/dev/
```

**Verify:**
- [ ] Names are prefixed with `dev-`
- [ ] Namespace is `development`
- [ ] API replicas = 1
- [ ] Redis replicas = 1
- [ ] Images use alpine tags
- [ ] Environment label = `dev`

## Part 3: Staging Overlay

### Step 9: Create Staging Overlay

Create `overlays/staging/kustomization.yaml`:

**Requirements:**
- Reference base
- Namespace: `staging`
- Name prefix: `staging-`
- Labels: `environment: staging`, `team: platform-team`
- Annotations: `deployed-by: kustomize`, `env-type: staging`, `monitoring: enabled`
- Replicas: api=3, redis=2
- Images: nginx:1.20, redis:6.2

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: staging

namePrefix: staging-

commonLabels:
  environment: staging
  team: platform-team

commonAnnotations:
  deployed-by: kustomize
  env-type: staging
  monitoring: enabled

replicas:
- name: api
  count: 3
- name: redis
  count: 2

images:
- name: nginx
  newTag: "1.20"
- name: redis
  newTag: "6.2"
```
</details>

### Step 10: Validate Staging

```bash
kubectl kustomize overlays/staging/
```

**Verify:**
- [ ] Names are prefixed with `staging-`
- [ ] Namespace is `staging`
- [ ] API replicas = 3
- [ ] Redis replicas = 2
- [ ] Nginx image = 1.20
- [ ] Monitoring annotation present

## Part 4: Production Overlay

### Step 11: Create Production Overlay

Create `overlays/prod/kustomization.yaml`:

**Requirements:**
- Reference base
- Namespace: `production`
- Name prefix: `prod-`
- Name suffix: `-v1`
- Labels: `environment: production`, `team: platform-team`, `criticality: high`
- Annotations: `deployed-by: kustomize`, `env-type: production`, `monitoring: enabled`, `backup: enabled`
- Replicas: api=10, redis=3
- Images: 
  - nginx → prodregistry.io/api:1.21
  - redis → prodregistry.io/redis:7.0

<details>
<summary>Solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: production

namePrefix: prod-
nameSuffix: -v1

commonLabels:
  environment: production
  team: platform-team
  criticality: high

commonAnnotations:
  deployed-by: kustomize
  env-type: production
  monitoring: enabled
  backup: enabled

replicas:
- name: api
  count: 10
- name: redis
  count: 3

images:
- name: nginx
  newName: prodregistry.io/api
  newTag: "1.21"
- name: redis
  newName: prodregistry.io/redis
  newTag: "7.0"
```
</details>

### Step 12: Validate Production

```bash
kubectl kustomize overlays/prod/
```

**Verify:**
- [ ] Names have prefix `prod-` and suffix `-v1`
- [ ] Namespace is `production`
- [ ] API replicas = 10
- [ ] Redis replicas = 3
- [ ] Images use prodregistry.io
- [ ] Criticality label = high
- [ ] Backup annotation present

## Part 5: Comparison and Analysis

### Step 13: Create Comparison

Run this comparison script:

```bash
#!/bin/bash

for env in dev staging prod; do
  echo "=== $env ===$(echo $env | tr '[:lower:]' '[:upper:]') ==="
  echo -n "Namespace: "
  kubectl kustomize overlays/$env/ | grep "namespace:" | head -1 | awk '{print $2}'
  
  echo -n "API Name: "
  kubectl kustomize overlays/$env/ | grep "name: .*api" | head -1 | awk '{print $2}'
  
  echo -n "API Replicas: "
  kubectl kustomize overlays/$env/ | yq eval 'select(.kind == "Deployment" and .metadata.name | contains("api")) | .spec.replicas' - | head -1
  
  echo -n "Redis Replicas: "
  kubectl kustomize overlays/$env/ | yq eval 'select(.kind == "Deployment" and .metadata.name | contains("redis")) | .spec.replicas' - | head -1
  
  echo ""
done
```

### Step 14: Fill Comparison Table

| Property | Dev | Staging | Production |
|----------|-----|---------|------------|
| Namespace | development | staging | production |
| API Name | dev-api | staging-api | prod-api-v1 |
| Redis Name | dev-redis | staging-redis | prod-redis-v1 |
| API Replicas | 1 | 3 | 10 |
| Redis Replicas | 1 | 2 | 3 |
| Nginx Image | nginx:1.19-alpine | nginx:1.20 | prodregistry.io/api:1.21 |
| Redis Image | redis:6.0-alpine | redis:6.2 | prodregistry.io/redis:7.0 |

## Part 6: Apply and Test (Optional)

### Step 15: Apply to Cluster

```bash
# Create namespaces
kubectl create namespace development
kubectl create namespace staging
kubectl create namespace production

# Apply
kubectl apply -k overlays/dev/
kubectl apply -k overlays/staging/
kubectl apply -k overlays/prod/
```

### Step 16: Verify Deployments

```bash
# Check all deployments
kubectl get deployments --all-namespaces | grep -E "api|redis"

# Expected output similar to:
# development   dev-api       1/1     1            1
# development   dev-redis     1/1     1            1
# staging       staging-api   3/3     3            3
# staging       staging-redis 2/2     2            2
# production    prod-api-v1   10/10   10           10
# production    prod-redis-v1 3/3     3            3
```

### Step 17: Verify Transformers

```bash
# Check labels
kubectl get deployment -n production prod-api-v1 -o jsonpath='{.metadata.labels}' | jq

# Check annotations
kubectl get deployment -n production prod-api-v1 -o jsonpath='{.metadata.annotations}' | jq

# Check images
kubectl describe deployment -n production prod-api-v1 | grep Image:
```

## Part 7: Update and Propagate

### Step 18: Add New Label to Base

Update `base/kustomization.yaml`:

```yaml
commonLabels:
  app: microservices
  managed-by: kustomize
  version: v2.0.0  # Add this
```

### Step 19: Verify Propagation

```bash
# Check all environments
for env in dev staging prod; do
  echo "=== $env ==="
  kubectl kustomize overlays/$env/ | grep "version: v2.0.0"
done
```

**Result:** New label appears in ALL environments! ✅

## Part 8: Clean Up

```bash
# Delete resources
kubectl delete -k overlays/dev/
kubectl delete -k overlays/staging/
kubectl delete -k overlays/prod/

# Delete namespaces
kubectl delete namespace development staging production
```

## Challenge Exercises

### Challenge 1: Add ConfigMap Generator
Add a ConfigMap to each environment with different values.

### Challenge 2: Add Resource Quotas
Create different resource quotas per environment.

### Challenge 3: Add HPA
Add HorizontalPodAutoscaler to production only.

### Challenge 4: Multi-Registry
Use different registries for dev (docker.io), staging (staging-registry.io), prod (prod-registry.io).

## Validation Checklist

- [ ] Base configuration created with 4 resources
- [ ] Dev overlay with correct transformers
- [ ] Staging overlay with correct transformers
- [ ] Production overlay with prefix AND suffix
- [ ] All replicas set correctly
- [ ] All images transformed correctly
- [ ] Labels applied to all resources
- [ ] Annotations applied appropriately
- [ ] Comparison table filled
- [ ] Optional: Resources deployed to cluster
- [ ] Optional: Base update propagated

## Troubleshooting

### Issue: Image not transformed
```bash
# Check image name matches exactly
kubectl kustomize overlays/dev/ | grep "image:"
```

### Issue: Replicas not changed
```bash
# Verify deployment name matches
kubectl kustomize overlays/dev/ | yq eval 'select(.kind == "Deployment") | .metadata.name'
```

### Issue: Labels not applied
```bash
# Check commonLabels syntax
cat overlays/dev/kustomization.yaml
```

## Summary

In this lab, you practiced:
- ✅ Common labels and annotations transformers
- ✅ Namespace transformer
- ✅ Name prefix and suffix transformers
- ✅ Replica transformer
- ✅ Image transformer with registry changes
- ✅ Combining multiple transformers
- ✅ Base update propagation

## Reference Files

Solution files are in this directory:
- [base/api-deployment.yaml](base/api-deployment.yaml)
- [base/redis-deployment.yaml](base/redis-deployment.yaml)
- [base/api-service.yaml](base/api-service.yaml)
- [base/redis-service.yaml](base/redis-service.yaml)
- [base/kustomization.yaml](base/kustomization.yaml)
- [overlays/dev/kustomization.yaml](overlays/dev/kustomization.yaml)
- [overlays/staging/kustomization.yaml](overlays/staging/kustomization.yaml)
- [overlays/prod/kustomization.yaml](overlays/prod/kustomization.yaml)

Excellent work! 🎉 Next, we'll learn about patches! 🚀
