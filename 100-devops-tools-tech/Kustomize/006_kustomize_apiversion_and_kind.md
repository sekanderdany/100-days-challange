# Kustomize apiVersion and Kind

## Understanding Metadata in kustomization.yaml

Every `kustomization.yaml` file must start with two required fields that identify it as a Kustomize configuration:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
```

These fields tell Kustomize (and any tools reading the file) that this is a Kustomize configuration file.

## apiVersion

### What is apiVersion?

The `apiVersion` field specifies the version of the Kustomize API you're using. It determines which features and fields are available.

### Current Version
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
```

**This is the standard and most widely used version.**

### Version History

| Version | Status | Notes |
|---------|--------|-------|
| `kustomize.config.k8s.io/v1beta1` | ✅ **Current & Stable** | Use this version |
| `kustomize.config.k8s.io/v1alpha1` | ⚠️ Deprecated | Legacy, avoid using |

### Why v1beta1?

- **Stability**: Thoroughly tested and stable
- **Compatibility**: Works with all kubectl versions (1.14+)
- **Features**: Includes all current Kustomize features
- **Future-proof**: Will be supported for the long term

### Example
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
```

## kind

### What is Kind?

The `kind` field specifies the type of configuration file. For Kustomize, it must always be `Kustomization`.

### Value
```yaml
kind: Kustomization
```

**This value is fixed and never changes.**

### Why is it Called "Kind"?

In Kubernetes, `kind` identifies the type of resource (Deployment, Service, Pod, etc.). Similarly:
- `kind: Deployment` → A Kubernetes Deployment
- `kind: Service` → A Kubernetes Service  
- `kind: Kustomization` → A Kustomize configuration

## Complete Structure

### Minimal kustomization.yaml
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
```

### With All Metadata
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

# Optional metadata (not commonly used)
metadata:
  name: my-app-kustomization

resources:
- deployment.yaml
- service.yaml
```

**Note:** The `metadata` field is optional and rarely used in kustomization.yaml files.

## Comparison with Kubernetes Resources

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 3
  # ... deployment spec
```

### Kustomization File
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
```

### Key Differences

| Field | Kubernetes Resource | Kustomization |
|-------|-------------------|---------------|
| `apiVersion` | Resource-specific (apps/v1, v1, etc.) | Always `kustomize.config.k8s.io/v1beta1` |
| `kind` | Resource type (Deployment, Service, etc.) | Always `Kustomization` |
| `metadata` | Required (at least `name`) | Optional, rarely used |
| `spec` | Resource specification | Not used (direct fields instead) |

## Common Mistakes

### ❌ Wrong apiVersion
```yaml
# WRONG - This will fail
apiVersion: v1
kind: Kustomization
```

**Error:**
```
Error: invalid Kustomization: json: cannot unmarshal
```

### ❌ Wrong Kind
```yaml
# WRONG - This will fail
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomize  # Should be "Kustomization"
```

**Error:**
```
Error: invalid Kustomization: no kind "Kustomize" is registered
```

### ❌ Missing Fields
```yaml
# WRONG - Missing required fields
resources:
- deployment.yaml
```

**Error:**
```
Error: missing Resource metadata
```

### ✅ Correct Format
```yaml
# CORRECT
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
```

## Real-World Examples

### Example 1: Simple Base
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

commonLabels:
  app: nginx
```

### Example 2: Production Overlay
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: production

namePrefix: prod-

images:
- name: nginx
  newTag: "1.21"

replicas:
- name: nginx
  count: 10
```

### Example 3: Dev Environment
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
- name: nginx
  count: 1
```

## Validation

### Automatic Validation

Kustomize automatically validates these fields:

```bash
$ kubectl kustomize .

# If apiVersion or kind is wrong:
Error: invalid Kustomization: ...
```

### Manual Validation

Check your file structure:

```bash
# Validate kustomization.yaml
kustomize build . > /dev/null && echo "Valid!" || echo "Invalid!"
```

### YAML Linting

Use YAML linters to catch syntax errors:

```bash
# Using yamllint
yamllint kustomization.yaml

# Using VS Code YAML extension
# Install "YAML" by Red Hat
```

## Why These Fields Matter

### 1. **Tool Recognition**
Tools like kubectl, ArgoCD, and Flux recognize Kustomize files by these fields:

```bash
# kubectl knows it's a Kustomize dir because of these fields
kubectl apply -k .
```

### 2. **API Compatibility**
The `apiVersion` ensures backward compatibility:

```yaml
# Future versions might be:
# apiVersion: kustomize.config.k8s.io/v2beta1
# But v1beta1 will still work
```

### 3. **Schema Validation**
IDEs and tools use these fields for:
- Auto-completion
- Syntax checking
- Field validation

## IDE Support

### VS Code Configuration

Add to `.vscode/settings.json`:
```json
{
  "yaml.schemas": {
    "https://json.schemastore.org/kustomization.json": "kustomization.yaml"
  }
}
```

### Benefits:
- ✅ Auto-completion for fields
- ✅ Validation of apiVersion and kind
- ✅ Field descriptions on hover
- ✅ Error highlighting

## Template for New Files

### Standard Template
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
# Add your resources here
- 

# Add transformations
namespace: 
commonLabels:
  app: 
```

### Copy-Paste Template
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources: []
```

## Quick Reference

### Required Fields
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1  # MUST be this value
kind: Kustomization                          # MUST be this value
```

### Correct Values
- ✅ `apiVersion: kustomize.config.k8s.io/v1beta1`
- ✅ `kind: Kustomization`

### Incorrect Values
- ❌ `apiVersion: v1`
- ❌ `apiVersion: kustomize/v1beta1`
- ❌ `kind: Kustomize`
- ❌ `kind: kustomization`

### Common Commands
```bash
# Validate kustomization.yaml
kubectl kustomize .

# Check for errors
kustomize build .

# Apply to cluster
kubectl apply -k .
```

## Best Practices

1. **Always Include Both Fields**
   ```yaml
   # Start every kustomization.yaml with:
   apiVersion: kustomize.config.k8s.io/v1beta1
   kind: Kustomization
   ```

2. **Use Consistent Formatting**
   ```yaml
   # Keep apiVersion and kind at the top
   # Add a blank line before other fields
   apiVersion: kustomize.config.k8s.io/v1beta1
   kind: Kustomization
   
   resources:
   - deployment.yaml
   ```

3. **Don't Modify These Fields**
   - Never change `apiVersion` unless you know what you're doing
   - Never change `kind`

4. **Use Templates**
   - Create a template file
   - Copy it for new kustomizations
   - Reduces errors

## Summary

| Field | Value | Required | Modifiable |
|-------|-------|----------|------------|
| `apiVersion` | `kustomize.config.k8s.io/v1beta1` | ✅ Yes | ❌ No |
| `kind` | `Kustomization` | ✅ Yes | ❌ No |

### Remember:
- ✅ Always use `apiVersion: kustomize.config.k8s.io/v1beta1`
- ✅ Always use `kind: Kustomization`
- ✅ Place them at the top of the file
- ✅ Validate your files with `kubectl kustomize`

## Next Steps

Now you understand the required fields in kustomization.yaml:
- ✅ apiVersion purpose and value
- ✅ kind purpose and value
- ✅ Common mistakes to avoid
- ✅ Validation methods

Next, we'll learn about **managing directories** and organizing your Kustomize projects! 🚀
