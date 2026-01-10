# Lab: Managing Directories

## Lab Overview

In this hands-on lab, you'll create a complete Kustomize project for a web application with:
- A base configuration
- Three environment overlays (dev, staging, production)
- Different configurations for each environment
- Practice with directory management and resource references

**Time Required:** 30-45 minutes

## Lab Objectives

By the end of this lab, you will:
- ✅ Create a base configuration with deployment and service
- ✅ Build three overlays for different environments
- ✅ Apply environment-specific customizations
- ✅ Understand resource references and directory structure
- ✅ Test and validate your configurations

## Prerequisites

- kubectl installed (version 1.14+)
- Access to a Kubernetes cluster (or use --dry-run)
- Basic understanding of Kubernetes resources

## Lab Structure

You'll build this structure:

```
webapp-lab/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
└── overlays/
    ├── dev/
    │   └── kustomization.yaml
    ├── staging/
    │   ├── kustomization.yaml
    │   └── replicas-patch.yaml
    └── prod/
        ├── kustomization.yaml
        └── resources-patch.yaml
```

## Part 1: Create Base Configuration

### Step 1: Initialize Project

Create the project directory structure:

```bash
mkdir -p webapp-lab/base
mkdir -p webapp-lab/overlays/{dev,staging,prod}
cd webapp-lab
```

**✅ Checkpoint:** Verify directory structure
```bash
tree .
# or
ls -R
```

### Step 2: Create Base Deployment

Create `base/deployment.yaml`:

<details>
<summary>Click to reveal solution</summary>

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
        env:
        - name: ENVIRONMENT
          value: "base"
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
<summary>Click to reveal solution</summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp
spec:
  selector:
    app: webapp
  ports:
  - name: http
    port: 80
    targetPort: 80
  type: ClusterIP
```
</details>

### Step 4: Create Base Kustomization

Create `base/kustomization.yaml`:

<details>
<summary>Click to reveal solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

commonLabels:
  app: webapp
  managed-by: kustomize
```
</details>

### Step 5: Test Base Configuration

```bash
kubectl kustomize base/
```

**Expected:** You should see both Deployment and Service with labels applied.

**✅ Checkpoint:** Base configuration builds without errors.

## Part 2: Create Development Overlay

### Step 6: Create Dev Kustomization

Create `overlays/dev/kustomization.yaml`:

**Requirements:**
- Reference the base
- Set namespace to `development`
- Add namePrefix `dev-`
- Add label `environment: dev`
- Set replicas to 1
- Use image tag `1.19-alpine`

<details>
<summary>Click to reveal solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: development

namePrefix: dev-

commonLabels:
  environment: dev

replicas:
- name: webapp
  count: 1

images:
- name: nginx
  newTag: "1.19-alpine"
```
</details>

### Step 7: Test Dev Overlay

```bash
kubectl kustomize overlays/dev/
```

**Verify:**
- ✅ Name is `dev-webapp`
- ✅ Namespace is `development`
- ✅ Replicas is 1
- ✅ Image is `nginx:1.19-alpine`
- ✅ Label `environment: dev` is present

## Part 3: Create Staging Overlay

### Step 8: Create Staging Kustomization

Create `overlays/staging/kustomization.yaml`:

**Requirements:**
- Reference the base
- Set namespace to `staging`
- Add namePrefix `staging-`
- Add label `environment: staging`
- Set replicas to 3
- Use image tag `1.20`
- Include a patch file for replicas

<details>
<summary>Click to reveal solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: staging

namePrefix: staging-

commonLabels:
  environment: staging

replicas:
- name: webapp
  count: 3

images:
- name: nginx
  newTag: "1.20"

patchesStrategicMerge:
- replicas-patch.yaml
```
</details>

### Step 9: Create Staging Patch

Create `overlays/staging/replicas-patch.yaml`:

**Requirements:**
- Update memory request to 192Mi
- Update memory limit to 384Mi

<details>
<summary>Click to reveal solution</summary>

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
            memory: "192Mi"
            cpu: "100m"
          limits:
            memory: "384Mi"
            cpu: "200m"
```
</details>

### Step 10: Test Staging Overlay

```bash
kubectl kustomize overlays/staging/
```

**Verify:**
- ✅ Name is `staging-webapp`
- ✅ Namespace is `staging`
- ✅ Replicas is 3
- ✅ Image is `nginx:1.20`
- ✅ Memory request is 192Mi

## Part 4: Create Production Overlay

### Step 11: Create Production Kustomization

Create `overlays/prod/kustomization.yaml`:

**Requirements:**
- Reference the base
- Set namespace to `production`
- Add namePrefix `prod-`
- Add labels: `environment: production`, `criticality: high`
- Add annotations: `monitoring: "enabled"`, `backup: "enabled"`
- Set replicas to 10
- Use image tag `1.21`
- Include a resource patch

<details>
<summary>Click to reveal solution</summary>

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: production

namePrefix: prod-

commonLabels:
  environment: production
  criticality: high

commonAnnotations:
  monitoring: "enabled"
  backup: "enabled"

replicas:
- name: webapp
  count: 10

images:
- name: nginx
  newTag: "1.21"

patchesStrategicMerge:
- resources-patch.yaml
```
</details>

### Step 12: Create Production Patch

Create `overlays/prod/resources-patch.yaml`:

**Requirements:**
- Update memory request to 512Mi
- Update memory limit to 1Gi
- Update CPU request to 500m
- Update CPU limit to 1000m

<details>
<summary>Click to reveal solution</summary>

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
</details>

### Step 13: Test Production Overlay

```bash
kubectl kustomize overlays/prod/
```

**Verify:**
- ✅ Name is `prod-webapp`
- ✅ Namespace is `production`
- ✅ Replicas is 10
- ✅ Image is `nginx:1.21`
- ✅ Memory request is 512Mi
- ✅ Annotations are present

## Part 5: Compare All Environments

### Step 14: Generate Comparison

Create a comparison script:

```bash
echo "=== DEVELOPMENT ==="
kubectl kustomize overlays/dev/ | grep -E "name: |namespace: |replicas: |image: " | head -20

echo ""
echo "=== STAGING ==="
kubectl kustomize overlays/staging/ | grep -E "name: |namespace: |replicas: |image: " | head -20

echo ""
echo "=== PRODUCTION ==="
kubectl kustomize overlays/prod/ | grep -E "name: |namespace: |replicas: |image: " | head -20
```

### Step 15: Create Comparison Table

Fill in this table with your results:

| Property | Development | Staging | Production |
|----------|-------------|---------|------------|
| Name | dev-webapp | staging-webapp | prod-webapp |
| Namespace | development | staging | production |
| Replicas | 1 | 3 | 10 |
| Image Tag | 1.19-alpine | 1.20 | 1.21 |
| Memory Request | 128Mi | 192Mi | 512Mi |
| Memory Limit | 256Mi | 384Mi | 1Gi |
| CPU Request | 100m | 100m | 500m |
| CPU Limit | 200m | 200m | 1000m |

## Part 6: Apply to Cluster (Optional)

**⚠️ Skip this if you don't have a Kubernetes cluster available.**

### Step 16: Create Namespaces

```bash
kubectl create namespace development
kubectl create namespace staging
kubectl create namespace production
```

### Step 17: Deploy All Environments

```bash
# Deploy to dev
kubectl apply -k overlays/dev/

# Deploy to staging
kubectl apply -k overlays/staging/

# Deploy to production
kubectl apply -k overlays/prod/
```

### Step 18: Verify Deployments

```bash
# Check dev
kubectl get all -n development

# Check staging
kubectl get all -n staging

# Check production
kubectl get all -n production
```

### Step 19: Verify Different Configurations

```bash
# Check dev replicas (should be 1)
kubectl get deployment -n development

# Check staging replicas (should be 3)
kubectl get deployment -n staging

# Check prod replicas (should be 10)
kubectl get deployment -n production
```

## Part 7: Make a Change

### Step 20: Update Base

Add a new label to `base/kustomization.yaml`:

```yaml
commonLabels:
  app: webapp
  managed-by: kustomize
  version: v2.0.0  # Add this line
```

### Step 21: Rebuild All Environments

```bash
kubectl kustomize overlays/dev/ | grep "version:"
kubectl kustomize overlays/staging/ | grep "version:"
kubectl kustomize overlays/prod/ | grep "version:"
```

**Observe:** The new label appears in ALL environments! 🎉

### Step 22: Apply Updates (Optional)

```bash
kubectl apply -k overlays/dev/
kubectl apply -k overlays/staging/
kubectl apply -k overlays/prod/
```

## Part 8: Clean Up

### Step 23: Delete Resources (If Applied)

```bash
kubectl delete -k overlays/dev/
kubectl delete -k overlays/staging/
kubectl delete -k overlays/prod/
```

### Step 24: Delete Namespaces (If Created)

```bash
kubectl delete namespace development staging production
```

## Validation Checklist

Mark each item as you complete it:

- [ ] Base configuration created and validated
- [ ] Dev overlay created with correct settings
- [ ] Staging overlay created with patch
- [ ] Production overlay created with enhanced resources
- [ ] All overlays reference base correctly
- [ ] Comparison table completed
- [ ] Optional: Resources applied to cluster
- [ ] Optional: Verified different configurations
- [ ] Base update propagated to all overlays
- [ ] Optional: Clean up completed

## Challenge Exercises

### Challenge 1: Add ConfigMap
Add a ConfigMap to the base with environment-specific values in each overlay.

### Challenge 2: Add QA Environment
Create a fourth overlay for `qa` environment between staging and production.

### Challenge 3: Multi-Region
Create region-specific overlays (us-east, us-west, eu-central) that build on production.

### Challenge 4: Add Ingress
Add an Ingress resource to production only.

## Troubleshooting Tips

### Issue: "unable to find base"
```bash
# Check your relative path
ls ../../base/kustomization.yaml
```

### Issue: "no such file"
```bash
# Check file names match exactly
ls -la overlays/prod/
```

### Issue: "unknown field"
```bash
# Check YAML indentation
yamllint kustomization.yaml
```

## Summary

In this lab, you:
- ✅ Created a base configuration
- ✅ Built three environment overlays
- ✅ Applied different customizations per environment
- ✅ Used patches to modify resources
- ✅ Understood directory structure and references
- ✅ Saw how base updates propagate to all overlays

## Next Steps

Now that you've mastered directory management:
- Move on to transformers (common, image, replica)
- Learn about different patch types
- Explore components and advanced patterns

Great job! 🎉 You're becoming a Kustomize expert! 🚀

## Reference Files

All solution files are available in this directory:
- [base/deployment.yaml](base/deployment.yaml)
- [base/service.yaml](base/service.yaml)
- [base/kustomization.yaml](base/kustomization.yaml)
- [overlays/dev/kustomization.yaml](overlays/dev/kustomization.yaml)
- [overlays/staging/kustomization.yaml](overlays/staging/kustomization.yaml)
- [overlays/staging/replicas-patch.yaml](overlays/staging/replicas-patch.yaml)
- [overlays/prod/kustomization.yaml](overlays/prod/kustomization.yaml)
- [overlays/prod/resources-patch.yaml](overlays/prod/resources-patch.yaml)
