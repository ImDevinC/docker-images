# Kubernetes deployment examples and usage guide

## Quick Start

### 1. Install GPU Operator

```bash
# Add NVIDIA Helm repository
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

# Install GPU Operator
helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator \
  --create-namespace \
  --wait
```

### 2. Verify GPU Support

```bash
# Check GPU operator pods
kubectl get pods -n gpu-operator

# Verify GPU nodes
kubectl get nodes -o json | jq '.items[].metadata.labels' | grep nvidia

# Test GPU access
kubectl run gpu-test --rm -it --restart=Never \
  --image=nvidia/cuda:12.1.1-base-ubuntu22.04 \
  --limits=nvidia.com/gpu=1 \
  -- nvidia-smi
```

### 3. Create HuggingFace Token Secret

```bash
# If you need to access private models
kubectl create namespace hunyuan3d

kubectl create secret generic hf-token \
  --from-literal=token=YOUR_HUGGINGFACE_TOKEN \
  --namespace hunyuan3d
```

### 4. Deploy Hunyuan3D

```bash
# Standard Gradio deployment
kubectl apply -f deployment.yaml

# Or API server deployment
kubectl apply -f api-deployment.yaml

# Or StatefulSet for persistent storage per pod
kubectl apply -f statefulset.yaml
```

### 5. Check Deployment Status

```bash
# Watch deployment progress
kubectl get pods -n hunyuan3d -w

# Check logs
kubectl logs -f -n hunyuan3d deployment/hunyuan3d

# Describe pod for troubleshooting
kubectl describe pod -n hunyuan3d <pod-name>
```

### 6. Access the Service

```bash
# Port forward for local access
kubectl port-forward -n hunyuan3d svc/hunyuan3d 7860:80

# Access at http://localhost:7860

# Or get LoadBalancer IP (if using LoadBalancer service)
kubectl get svc -n hunyuan3d
```

## Deployment Variants

### Standard Deployment (deployment.yaml)

- Single or multiple replicas
- Shared storage via PVC
- Gradio web interface
- Suitable for general use

```bash
kubectl apply -f deployment.yaml
```

### API Server Deployment (api-deployment.yaml)

- REST API endpoint
- Multiple replicas for load balancing
- Suitable for programmatic access
- No web UI

```bash
kubectl apply -f api-deployment.yaml
```

### StatefulSet Deployment (statefulset.yaml)

- Stable network identities
- Persistent storage per pod
- Ordered deployment/scaling
- Suitable for stateful workloads

```bash
kubectl apply -f statefulset.yaml
```

## Configuration Options

### Model Selection

Edit ConfigMap in `deployment.yaml`:

```yaml
data:
  # Use standard model
  MODEL_PATH: "tencent/Hunyuan3D-2"
  SUBFOLDER: "hunyuan3d-dit-v2-0"
  
  # Or use mini model (less VRAM)
  # MODEL_PATH: "tencent/Hunyuan3D-2mini"
  # SUBFOLDER: "hunyuan3d-dit-v2-mini"
  
  # Or use multiview model
  # MODEL_PATH: "tencent/Hunyuan3D-2mv"
  # SUBFOLDER: "hunyuan3d-dit-v2-mv"
  
  # Or use turbo model
  # MODEL_PATH: "tencent/Hunyuan3D-2"
  # SUBFOLDER: "hunyuan3d-dit-v2-0-turbo"
  # ENABLE_FLASHVDM: "true"
```

### Low VRAM Mode

For GPUs with less memory:

```yaml
data:
  LOW_VRAM_MODE: "true"
```

### Storage Configuration

Adjust PVC sizes based on your needs:

```yaml
spec:
  resources:
    requests:
      storage: 50Gi  # Increase if storing many models
```

### Resource Limits

Adjust based on your GPU and requirements:

```yaml
resources:
  requests:
    memory: "16Gi"
    cpu: "4"
    nvidia.com/gpu: 1
  limits:
    memory: "32Gi"
    cpu: "8"
    nvidia.com/gpu: 1
```

## Scaling

### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment hunyuan3d -n hunyuan3d --replicas=3

# Scale statefulset
kubectl scale statefulset hunyuan3d -n hunyuan3d --replicas=3
```

### Auto-scaling (HPA)

The HPA is included in `deployment.yaml`:

```bash
# View HPA status
kubectl get hpa -n hunyuan3d

# Describe HPA
kubectl describe hpa hunyuan3d-hpa -n hunyuan3d
```

## Monitoring

### Pod Status

```bash
# Get all resources
kubectl get all -n hunyuan3d

# Watch pod status
kubectl get pods -n hunyuan3d -w

# Get pod metrics (requires metrics-server)
kubectl top pods -n hunyuan3d
```

### Logs

```bash
# Stream logs
kubectl logs -f -n hunyuan3d deployment/hunyuan3d

# Get logs from specific container
kubectl logs -n hunyuan3d <pod-name> -c hunyuan3d

# Get previous logs (if pod crashed)
kubectl logs -n hunyuan3d <pod-name> --previous
```

### GPU Monitoring

```bash
# Install DCGM exporter for GPU metrics
helm install dcgm-exporter nvidia/dcgm-exporter \
  --namespace gpu-operator

# View GPU metrics (if using Prometheus)
kubectl port-forward -n gpu-operator svc/dcgm-exporter 9400:9400
# Access at http://localhost:9400/metrics
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod events
kubectl describe pod -n hunyuan3d <pod-name>

# Common issues:
# - No GPU nodes available: Check node labels and GPU operator
# - Image pull errors: Verify image name and registry access
# - Insufficient resources: Check node capacity
```

### GPU Not Detected

```bash
# Verify GPU operator
kubectl get pods -n gpu-operator

# Check device plugin
kubectl logs -n gpu-operator -l app=nvidia-device-plugin-daemonset

# Test GPU allocation
kubectl run gpu-test --rm -it --restart=Never \
  --image=nvidia/cuda:12.1.1-base-ubuntu22.04 \
  --limits=nvidia.com/gpu=1 \
  -- nvidia-smi
```

### Out of Memory

```bash
# Enable low VRAM mode
kubectl set env deployment/hunyuan3d -n hunyuan3d LOW_VRAM_MODE=true

# Or use smaller model
kubectl set env deployment/hunyuan3d -n hunyuan3d \
  MODEL_PATH=tencent/Hunyuan3D-2mini \
  SUBFOLDER=hunyuan3d-dit-v2-mini
```

### Storage Issues

```bash
# Check PVC status
kubectl get pvc -n hunyuan3d

# Describe PVC
kubectl describe pvc -n hunyuan3d hunyuan3d-models

# Check available storage
kubectl exec -it -n hunyuan3d <pod-name> -- df -h
```

### Network Issues

```bash
# Test service connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -n hunyuan3d \
  -- wget -O- http://hunyuan3d:80

# Check ingress
kubectl get ingress -n hunyuan3d
kubectl describe ingress -n hunyuan3d hunyuan3d
```

## Security Best Practices

### Network Policies

Apply network policy from `deployment.yaml` to restrict traffic:

```bash
kubectl apply -f deployment.yaml
```

### Pod Security Standards

Ensure namespace has pod security standards:

```bash
kubectl label namespace hunyuan3d \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted
```

### RBAC

Create service account with minimal permissions:

```bash
kubectl create serviceaccount hunyuan3d -n hunyuan3d

# Apply appropriate RoleBinding
kubectl create rolebinding hunyuan3d \
  --serviceaccount=hunyuan3d:hunyuan3d \
  --clusterrole=view \
  -n hunyuan3d
```

## Backup and Restore

### Backup Models and Cache

```bash
# Create a backup job
kubectl create job backup-models \
  --image=busybox \
  --namespace hunyuan3d \
  -- tar czf /backup/models.tar.gz /models

# Or use velero for cluster-wide backups
velero backup create hunyuan3d-backup \
  --include-namespaces hunyuan3d
```

### Restore

```bash
# Restore from backup
velero restore create --from-backup hunyuan3d-backup
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace hunyuan3d

# Or delete specific resources
kubectl delete -f deployment.yaml

# Remove GPU operator (if no longer needed)
helm uninstall gpu-operator -n gpu-operator
kubectl delete namespace gpu-operator
```

## Advanced Configuration

### Using Init Containers for Model Pre-download

Add to deployment spec:

```yaml
initContainers:
- name: download-models
  image: hunyuan3d:latest
  command: ["/bin/bash", "-c"]
  args:
    - |
      python -c "
      from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
      pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained('${MODEL_PATH}', subfolder='${SUBFOLDER}')
      "
  env:
  - name: MODEL_PATH
    valueFrom:
      configMapKeyRef:
        name: hunyuan3d-config
        key: MODEL_PATH
  - name: SUBFOLDER
    valueFrom:
      configMapKeyRef:
        name: hunyuan3d-config
        key: SUBFOLDER
  volumeMounts:
  - name: models
    mountPath: /models
  - name: cache
    mountPath: /cache
```

### Using Affinity for GPU Node Selection

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: nvidia.com/gpu.product
          operator: In
          values:
          - NVIDIA-A100-SXM4-40GB
          - NVIDIA-A100-SXM4-80GB
```

### Multiple GPU Support

For multi-GPU inference:

```yaml
resources:
  limits:
    nvidia.com/gpu: 2  # Use 2 GPUs
```

## Performance Tuning

### Optimize Storage

- Use SSD-backed storage classes
- Consider NVMe for best performance
- Use ReadWriteMany for shared models

### Optimize Network

- Use host networking for low latency
- Configure proper MTU sizes
- Use network policies to reduce overhead

### Optimize Compute

- Pin pods to specific GPU types
- Use node affinity for consistent performance
- Monitor GPU utilization and adjust replicas
