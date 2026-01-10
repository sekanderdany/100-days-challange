# Kustomize Installation and Setup

## What is Kustomize?

Kustomize is a standalone tool and also built into `kubectl` (Kubernetes command-line tool). It allows you to customize Kubernetes configurations without templates.

## Installation Options

### Option 1: Using kubectl (Recommended)

Kustomize is **built into kubectl** starting from version 1.14. No separate installation needed!

**Check if you have it:**
```bash
kubectl version --client
```

If your kubectl version is 1.14 or higher, you already have Kustomize!

**Usage with kubectl:**
```bash
kubectl apply -k <directory>
# or
kubectl kustomize <directory>
```

### Option 2: Standalone Kustomize Binary

For the latest features or standalone usage, install the Kustomize CLI:

#### Windows

**Using Chocolatey:**
```powershell
choco install kustomize
```

**Using Scoop:**
```powershell
scoop install kustomize
```

**Manual Installation:**
```powershell
# Download from GitHub releases
# Visit: https://github.com/kubernetes-sigs/kustomize/releases

# Example for version 5.3.0
Invoke-WebRequest -Uri "https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv5.3.0/kustomize_v5.3.0_windows_amd64.tar.gz" -OutFile "kustomize.tar.gz"

# Extract and move to PATH
tar -xzf kustomize.tar.gz
Move-Item kustomize.exe C:\Windows\System32\
```

#### Linux

**Using Binary:**
```bash
# Download the latest release
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash

# Move to PATH
sudo mv kustomize /usr/local/bin/
```

**Using Package Manager (Ubuntu/Debian):**
```bash
sudo apt-get install kustomize
```

**Using Snap:**
```bash
sudo snap install kustomize
```

#### macOS

**Using Homebrew:**
```bash
brew install kustomize
```

**Using Binary:**
```bash
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
sudo mv kustomize /usr/local/bin/
```

## Verify Installation

### Check kubectl with Kustomize
```bash
kubectl kustomize --help
```

**Expected output:**
```
Build a set of KRM resources using a 'kustomization.yaml' file...
```

### Check Standalone Kustomize
```bash
kustomize version
```

**Expected output:**
```
v5.3.0
```

## Version Differences

| Version Type | Best For | Command |
|--------------|----------|---------|
| **kubectl -k** | Production use, CI/CD | `kubectl apply -k ./` |
| **Standalone kustomize** | Latest features, development | `kustomize build ./` |

**Note:** The standalone version typically has newer features than the kubectl-embedded version.

## Basic Setup Verification

Let's verify everything works with a simple example:

### 1. Create a Test Directory
```bash
mkdir kustomize-test
cd kustomize-test
```

### 2. Create a Simple Deployment
```bash
# Create a deployment file
cat > deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
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
EOF
```

### 3. Create a Kustomization File
```bash
cat > kustomization.yaml << EOF
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

commonLabels:
  environment: test
EOF
```

### 4. Test Kustomize Build
```bash
# Using kubectl
kubectl kustomize .

# OR using standalone kustomize
kustomize build .
```

**Expected output:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    environment: test
  name: nginx-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
      environment: test
  template:
    metadata:
      labels:
        app: nginx
        environment: test
    spec:
      containers:
      - image: nginx:1.19
        name: nginx
        ports:
        - containerPort: 80
```

Notice how Kustomize added the `environment: test` label to all resources!

## Setting Up Your Workspace

### Project Structure
```
my-app/
├── base/                           # Base configuration
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
└── overlays/                       # Environment-specific configs
    ├── dev/
    │   └── kustomization.yaml
    ├── staging/
    │   └── kustomization.yaml
    └── prod/
        └── kustomization.yaml
```

### Create the Structure
```bash
# Create directories
mkdir -p my-app/base
mkdir -p my-app/overlays/{dev,staging,prod}

# Navigate to your project
cd my-app
```

## IDE Setup (Optional but Recommended)

### VS Code Extensions

1. **YAML** by Red Hat
   - Provides YAML validation
   - Kubernetes schema support

2. **Kubernetes** by Microsoft
   - Kubernetes resource snippets
   - kubectl integration

### VS Code Settings
```json
{
  "yaml.schemas": {
    "https://json.schemastore.org/kustomization.json": "kustomization.yaml"
  },
  "yaml.customTags": [
    "!ENV scalar",
    "!ENV sequence"
  ]
}
```

## Common Installation Issues

### Issue 1: kubectl version too old
```bash
# Check version
kubectl version --client

# Upgrade kubectl
# Visit: https://kubernetes.io/docs/tasks/tools/
```

### Issue 2: Permission denied (Linux/Mac)
```bash
# Make binary executable
chmod +x kustomize

# Move with sudo
sudo mv kustomize /usr/local/bin/
```

### Issue 3: Command not found (Windows)
```bash
# Ensure binary is in PATH
# Add to System Environment Variables:
# C:\path\to\kustomize
```

## Testing Your Setup

Run these commands to ensure everything works:

```bash
# 1. Check kubectl kustomize
kubectl kustomize --help

# 2. Check standalone (if installed)
kustomize version

# 3. Test with a simple build
echo "apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources: []" > kustomization.yaml

kubectl kustomize .

# Clean up
rm kustomization.yaml
```

## Quick Reference Card

```bash
# Build and view output
kubectl kustomize <directory>
kustomize build <directory>

# Apply to cluster
kubectl apply -k <directory>

# Delete resources
kubectl delete -k <directory>

# Diff before applying
kubectl diff -k <directory>

# Dry run
kubectl apply -k <directory> --dry-run=client
```

## Environment Variables (Advanced)

Kustomize supports environment variable substitution:

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

configMapGenerator:
- name: my-config
  literals:
  - APP_VERSION=${APP_VERSION:-v1.0.0}
```

```bash
# Use with environment variable
APP_VERSION=v2.0.0 kustomize build .
```

## Next Steps

Now that you have Kustomize installed and verified:

1. ✅ Kustomize is installed
2. ✅ Setup is verified
3. ✅ Project structure is understood

Next, we'll learn about the **kustomization.yaml** file - the heart of Kustomize! 🚀

## Useful Resources

- **Official Documentation:** https://kustomize.io/
- **GitHub Repository:** https://github.com/kubernetes-sigs/kustomize
- **kubectl Reference:** https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/
- **Examples:** https://github.com/kubernetes-sigs/kustomize/tree/master/examples
