# Hunyuan3D-2 Docker Image

Secure Docker image for running Tencent's Hunyuan3D-2 model for high-resolution 3D asset generation from images or text.

## Features

- **Secure**: Runs as non-root user with minimal privileges
- **GPU-Accelerated**: Built on NVIDIA CUDA 12.1.1 with cuDNN 8
- **Flexible**: Multiple operation modes (Gradio UI, API server, Python scripts)
- **Optimized**: Multi-stage caching for faster builds
- **Production-Ready**: Health checks and proper logging

## System Requirements

### Hardware Requirements

- **GPU**: NVIDIA GPU with compute capability 7.0+ (Volta, Turing, Ampere, Ada, or newer)
- **VRAM**: 
  - Minimum 6 GB for shape generation only
  - Recommended 16 GB for shape + texture generation
  - 24 GB+ for optimal performance
- **RAM**: 16 GB minimum, 32 GB recommended
- **Storage**: 50 GB for image and models

### Software Requirements

- Docker Engine 20.10+
- NVIDIA Container Toolkit
- NVIDIA Driver 525.60.13+ (for CUDA 12.1)
- Kubernetes 1.24+ (for K8s deployment)

## NVIDIA Container Toolkit Setup

The NVIDIA Container Toolkit is required to access GPU resources from Docker containers.

### Installation

#### Ubuntu/Debian

```bash
# Add NVIDIA package repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install NVIDIA Container Toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

#### Verify Installation

```bash
# Test GPU access
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi
```

## Building the Image

```bash
# Clone the Hunyuan3D-2 repository
git clone https://github.com/Tencent-Hunyuan/Hunyuan3D-2.git
cd Hunyuan3D-2

# Copy Dockerfile and entrypoint.sh to the repository root
# (assuming you have them in the current directory)
cp /path/to/Dockerfile .
cp /path/to/entrypoint.sh .
chmod +x entrypoint.sh

# Build the image
docker build -t hunyuan3d:latest .

# Or with build arguments
docker build \
  --build-arg CUDA_VERSION=12.1.1 \
  -t hunyuan3d:latest .
```

## Running the Container

### Gradio Web Interface (Default)

```bash
docker run --gpus all -p 7860:7860 \
  -v $(pwd)/models:/models \
  -v $(pwd)/cache:/cache \
  hunyuan3d:latest
```

Access at: http://localhost:7860

### API Server Mode

```bash
docker run --gpus all -p 8080:8080 \
  -v $(pwd)/models:/models \
  -v $(pwd)/cache:/cache \
  hunyuan3d:latest api
```

API endpoint: http://localhost:8080

### Low VRAM Mode

For systems with limited GPU memory:

```bash
docker run --gpus all -p 7860:7860 \
  -e LOW_VRAM_MODE=true \
  -v $(pwd)/models:/models \
  -v $(pwd)/cache:/cache \
  hunyuan3d:latest
```

### Using Different Models

```bash
# Use Hunyuan3D-2mini (smaller, faster)
docker run --gpus all -p 7860:7860 \
  -e MODEL_PATH=tencent/Hunyuan3D-2mini \
  -e SUBFOLDER=hunyuan3d-dit-v2-mini \
  -v $(pwd)/models:/models \
  -v $(pwd)/cache:/cache \
  hunyuan3d:latest

# Use Hunyuan3D-2mv (multiview)
docker run --gpus all -p 7860:7860 \
  -e MODEL_PATH=tencent/Hunyuan3D-2mv \
  -e SUBFOLDER=hunyuan3d-dit-v2-mv \
  -v $(pwd)/models:/models \
  -v $(pwd)/cache:/cache \
  hunyuan3d:latest

# Use Turbo model with FlashVDM
docker run --gpus all -p 7860:7860 \
  -e MODEL_PATH=tencent/Hunyuan3D-2 \
  -e SUBFOLDER=hunyuan3d-dit-v2-0-turbo \
  -e ENABLE_FLASHVDM=true \
  -v $(pwd)/models:/models \
  -v $(pwd)/cache:/cache \
  hunyuan3d:latest
```

### With HuggingFace Token (Private Models)

```bash
docker run --gpus all -p 7860:7860 \
  -e HF_TOKEN=your_token_here \
  -v $(pwd)/models:/models \
  -v $(pwd)/cache:/cache \
  hunyuan3d:latest
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server bind address | `0.0.0.0` |
| `GRADIO_PORT` | Gradio web interface port | `7860` |
| `API_PORT` | API server port | `8080` |
| `MODEL_PATH` | HuggingFace model repository | `tencent/Hunyuan3D-2` |
| `SUBFOLDER` | Model subfolder | `hunyuan3d-dit-v2-0` |
| `TEXGEN_MODEL_PATH` | Texture generation model | `tencent/Hunyuan3D-2` |
| `LOW_VRAM_MODE` | Enable low VRAM optimizations | `false` |
| `ENABLE_FLASHVDM` | Enable FlashVDM acceleration | `false` |
| `HF_TOKEN` | HuggingFace authentication token | (none) |
| `HF_HOME` | HuggingFace cache directory | `/cache/huggingface` |
| `TORCH_HOME` | PyTorch cache directory | `/cache/torch` |

## Kubernetes Deployment

### Prerequisites

1. **NVIDIA GPU Operator** or **NVIDIA Device Plugin** installed in your cluster
2. Nodes with NVIDIA GPUs and drivers installed
3. Container runtime configured for GPU support

### Install NVIDIA GPU Operator (Recommended)

```bash
# Add NVIDIA Helm repository
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

# Install GPU Operator
helm install --wait --generate-name \
  -n gpu-operator --create-namespace \
  nvidia/gpu-operator
```

### Verify GPU Node Labels

```bash
kubectl get nodes -o json | jq '.items[].metadata.labels' | grep nvidia
```

You should see labels like:
- `nvidia.com/gpu.present=true`
- `nvidia.com/gpu.count=1` (or more)

### Deployment Manifest

Create `hunyuan3d-deployment.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: hunyuan3d
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: hunyuan3d-models
  namespace: hunyuan3d
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: standard  # Change to your storage class
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: hunyuan3d-cache
  namespace: hunyuan3d
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: standard
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hunyuan3d
  namespace: hunyuan3d
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hunyuan3d
  template:
    metadata:
      labels:
        app: hunyuan3d
    spec:
      # Node selector for GPU nodes
      nodeSelector:
        nvidia.com/gpu.present: "true"
      
      # Tolerations if using taints
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
      
      containers:
      - name: hunyuan3d
        image: hunyuan3d:latest
        imagePullPolicy: IfNotPresent
        
        # Resource requests and limits
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: 1
          limits:
            memory: "32Gi"
            cpu: "8"
            nvidia.com/gpu: 1
        
        # Environment variables
        env:
        - name: MODEL_PATH
          value: "tencent/Hunyuan3D-2"
        - name: SUBFOLDER
          value: "hunyuan3d-dit-v2-0"
        - name: LOW_VRAM_MODE
          value: "false"
        - name: GRADIO_PORT
          value: "7860"
        
        # Ports
        ports:
        - containerPort: 7860
          name: gradio
          protocol: TCP
        
        # Volume mounts
        volumeMounts:
        - name: models
          mountPath: /models
        - name: cache
          mountPath: /cache
        
        # Liveness probe
        livenessProbe:
          httpGet:
            path: /
            port: 7860
          initialDelaySeconds: 120
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        
        # Readiness probe
        readinessProbe:
          httpGet:
            path: /
            port: 7860
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # Security context
        securityContext:
          runAsUser: 1000
          runAsGroup: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: false
          capabilities:
            drop:
            - ALL
      
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: hunyuan3d-models
      - name: cache
        persistentVolumeClaim:
          claimName: hunyuan3d-cache
---
apiVersion: v1
kind: Service
metadata:
  name: hunyuan3d
  namespace: hunyuan3d
spec:
  type: LoadBalancer  # or ClusterIP/NodePort
  selector:
    app: hunyuan3d
  ports:
  - port: 80
    targetPort: 7860
    protocol: TCP
    name: gradio
```

### Deploy to Kubernetes

```bash
# Apply the deployment
kubectl apply -f hunyuan3d-deployment.yaml

# Check deployment status
kubectl get pods -n hunyuan3d

# View logs
kubectl logs -f -n hunyuan3d deployment/hunyuan3d

# Get service endpoint
kubectl get svc -n hunyuan3d
```

### API Server Deployment

For API server mode, modify the deployment:

```yaml
env:
- name: MODE
  value: "api"
- name: API_PORT
  value: "8080"

ports:
- containerPort: 8080
  name: api
  protocol: TCP
```

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hunyuan3d-hpa
  namespace: hunyuan3d
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hunyuan3d
  minReplicas: 1
  maxReplicas: 3
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

## Security Considerations

1. **Non-root User**: Container runs as user `hunyuan` (UID 1000)
2. **Read-only Filesystem**: Where possible, mount volumes as read-only
3. **Dropped Capabilities**: All Linux capabilities dropped except necessary ones
4. **Network Policies**: Implement Kubernetes NetworkPolicies to restrict traffic
5. **Resource Limits**: Always set memory and CPU limits in production
6. **Secrets Management**: Use Kubernetes Secrets for HF_TOKEN
7. **Image Scanning**: Scan images for vulnerabilities before deployment
8. **TLS/HTTPS**: Use ingress with TLS termination for production

### Using Secrets for HuggingFace Token

```bash
# Create secret
kubectl create secret generic hf-token \
  --from-literal=token=your_token_here \
  -n hunyuan3d

# Reference in deployment
env:
- name: HF_TOKEN
  valueFrom:
    secretKeyRef:
      name: hf-token
      key: token
```

## Monitoring and Logging

### GPU Metrics

Monitor GPU usage with NVIDIA DCGM Exporter:

```bash
helm install --generate-name \
  -n gpu-operator \
  nvidia/dcgm-exporter
```

### Application Logs

```bash
# Stream logs
kubectl logs -f -n hunyuan3d deployment/hunyuan3d

# View recent logs
kubectl logs --tail=100 -n hunyuan3d deployment/hunyuan3d
```

## Troubleshooting

### GPU Not Detected

```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi

# Verify container runtime
kubectl describe node <node-name> | grep -i runtime

# Check GPU operator pods
kubectl get pods -n gpu-operator
```

### Out of Memory Errors

- Enable `LOW_VRAM_MODE=true`
- Use smaller models (Hunyuan3D-2mini)
- Increase GPU memory limits
- Reduce batch sizes

### Model Download Issues

- Set `HF_TOKEN` for private models
- Check network connectivity
- Verify storage capacity
- Pre-download models to persistent volume

### Performance Issues

- Use turbo models with FlashVDM
- Enable GPU monitoring
- Check for CPU/memory bottlenecks
- Optimize storage I/O

## Model Variants

| Model | Size | VRAM Required | Speed | Quality |
|-------|------|---------------|-------|---------|
| Hunyuan3D-2 | 1.1B | 16GB | Standard | Highest |
| Hunyuan3D-2-Turbo | 1.1B | 16GB | Fast | High |
| Hunyuan3D-2mini | 0.6B | 6GB | Fast | Good |
| Hunyuan3D-2mv | 1.1B | 16GB | Standard | High (multiview) |

## License

This Docker image packages Tencent's Hunyuan3D-2 model. Please review the [Tencent Hunyuan Community License](https://huggingface.co/tencent/Hunyuan3D-2) before use.

## Support

- GitHub: https://github.com/Tencent-Hunyuan/Hunyuan3D-2
- HuggingFace: https://huggingface.co/tencent/Hunyuan3D-2
- Discord: https://discord.gg/dNBrdrGGMa

## References

- [Hunyuan3D 2.0 Paper](https://arxiv.org/abs/2501.12202)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-container-toolkit)
- [Kubernetes GPU Support](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)
