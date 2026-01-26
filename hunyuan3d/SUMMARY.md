# Hunyuan3D-2 Docker Image - Project Summary

## Overview

This is a secure, production-ready Docker image for Tencent's Hunyuan3D-2 model, designed to run in Kubernetes environments with NVIDIA Container Toolkit support.

**Model:** Hunyuan3D-2 - High-resolution 3D asset generation from images/text  
**Source:** https://huggingface.co/tencent/Hunyuan3D-2  
**Paper:** https://arxiv.org/abs/2501.12202

## What's Included

### Docker Configuration
- ✅ **Dockerfile** - Secure multi-stage build with CUDA 12.1.1 support
- ✅ **entrypoint.sh** - Flexible entrypoint supporting multiple run modes
- ✅ **docker-compose.yml** - Easy local deployment
- ✅ **.dockerignore** - Optimized build context

### Kubernetes Manifests
- ✅ **deployment.yaml** - Standard Gradio UI deployment
- ✅ **api-deployment.yaml** - REST API server deployment
- ✅ **statefulset.yaml** - StatefulSet for persistent storage per pod

### Documentation
- ✅ **README.md** - Complete setup and usage guide
- ✅ **QUICKSTART.md** - 5-minute quick start guide
- ✅ **SECURITY.md** - Security best practices and compliance
- ✅ **kubernetes/README.md** - Detailed K8s deployment guide

### Automation
- ✅ **build.sh** - Automated build script
- ✅ **Makefile** - Common operations (build, run, deploy, etc.)

## Key Features

### Security
- Runs as non-root user (UID 1000)
- All Linux capabilities dropped
- Minimal base image (NVIDIA CUDA official)
- Security scanning integration (Trivy, Grype)
- Pod Security Standards compliant
- Network policies for traffic restriction
- Secrets management best practices

### Flexibility
- Multiple run modes: Gradio UI, API server, CLI
- Support for all model variants (standard, mini, turbo, multiview)
- Configurable via environment variables
- Low VRAM mode for smaller GPUs
- Multiple deployment options (Docker, K8s, StatefulSet)

### Production-Ready
- Health checks and readiness probes
- Resource limits and quotas
- Horizontal Pod Autoscaling
- Persistent storage configuration
- Ingress with TLS support
- Monitoring and logging setup

### NVIDIA GPU Support
- CUDA 12.1.1 with cuDNN 8
- NVIDIA Container Toolkit integration
- GPU Operator compatible
- Multi-GPU support
- Compute capability 7.0+ (Volta and newer)

## System Requirements

### Hardware
- **GPU:** NVIDIA GPU (Volta/Turing/Ampere/Ada or newer)
- **VRAM:** 6GB minimum (16GB recommended)
- **RAM:** 16GB minimum (32GB recommended)
- **Storage:** 50GB for images and models

### Software
- **Docker:** 20.10+
- **NVIDIA Driver:** 525.60.13+
- **NVIDIA Container Toolkit:** Latest
- **Kubernetes:** 1.24+ (for K8s deployment)
- **NVIDIA GPU Operator:** Latest (for K8s)

## Quick Start

```bash
# 1. Build
./build.sh

# 2. Run
make run
# Or: docker run --gpus all -p 7860:7860 hunyuan3d:latest

# 3. Access
# Open http://localhost:7860
```

## Model Variants

| Model | VRAM | Speed | Use Case |
|-------|------|-------|----------|
| **Hunyuan3D-2** | 16GB | Standard | Best quality |
| **Hunyuan3D-2-Turbo** | 16GB | 2x faster | Fast generation |
| **Hunyuan3D-2mini** | 6GB | Fast | Low VRAM systems |
| **Hunyuan3D-2mv** | 16GB | Standard | Multiview input |

## Deployment Options

### 1. Docker (Local)
```bash
docker run --gpus all -p 7860:7860 hunyuan3d:latest
```

### 2. Docker Compose
```bash
docker-compose up -d
```

### 3. Kubernetes (Production)
```bash
kubectl apply -f kubernetes/deployment.yaml
```

### 4. Makefile
```bash
make run          # Standard model
make run-mini     # Mini model
make run-turbo    # Turbo model
make run-api      # API server
```

## File Structure

```
hunyuan3d/
├── Dockerfile              # Docker image definition
├── entrypoint.sh          # Container entrypoint
├── docker-compose.yml     # Docker Compose config
├── .dockerignore          # Build exclusions
├── build.sh               # Build automation
├── Makefile               # Common operations
├── README.md              # Main documentation
├── QUICKSTART.md          # Quick start guide
├── SECURITY.md            # Security guidelines
├── SUMMARY.md             # This file
└── kubernetes/
    ├── deployment.yaml         # Standard deployment
    ├── api-deployment.yaml     # API variant
    ├── statefulset.yaml        # StatefulSet variant
    └── README.md               # K8s documentation
```

## Security Highlights

- ✅ Non-root container execution
- ✅ Dropped capabilities (cap_drop: ALL)
- ✅ Security Context constraints
- ✅ Network policies
- ✅ Pod Security Standards
- ✅ Secrets externalization
- ✅ Resource quotas and limits
- ✅ Image vulnerability scanning
- ✅ TLS/HTTPS support
- ✅ RBAC configuration

## NVIDIA Container Toolkit Requirements

### Why It's Needed
The NVIDIA Container Toolkit allows Docker containers to access NVIDIA GPUs. Without it, the container cannot use GPU acceleration.

### Installation
```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Verification
```bash
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi
```

## Kubernetes GPU Requirements

### GPU Operator
The NVIDIA GPU Operator manages GPU resources in Kubernetes:

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator \
  --create-namespace
```

### What It Provides
- **Device Plugin:** Exposes GPUs to Kubernetes
- **DCGM Exporter:** GPU metrics for monitoring
- **Node Feature Discovery:** Auto-labels GPU nodes
- **GPU Driver Management:** Automated driver installation

### Resource Requests
Pods request GPU resources:
```yaml
resources:
  limits:
    nvidia.com/gpu: 1  # Request 1 GPU
```

## Performance Characteristics

### Generation Times (Approximate)
- **Shape Generation:** 30-60 seconds
- **Texture Generation:** 60-120 seconds
- **Total (Image to 3D):** 2-5 minutes
- **Turbo Model:** ~50% faster

### VRAM Usage
- **Shape Only:** ~4-6 GB
- **Shape + Texture:** ~12-16 GB
- **Low VRAM Mode:** ~6-10 GB

### Storage Requirements
- **Docker Image:** ~8-10 GB
- **Models (cached):** ~5-8 GB per variant
- **Temporary Files:** ~1-2 GB per generation

## Common Use Cases

### 1. Web Interface (Gradio)
For interactive 3D generation with visual feedback
```bash
make run
```

### 2. REST API Server
For programmatic access and integration
```bash
make run-api
```

### 3. Batch Processing
For processing multiple images
```bash
docker run --gpus all -v $(pwd)/input:/input -v $(pwd)/output:/output \
  hunyuan3d:latest python /path/to/batch_script.py
```

### 4. Development
For model development and testing
```bash
make dev-run  # With code mounted
```

## Monitoring and Observability

### Container Logs
```bash
# Docker
docker logs -f hunyuan3d

# Kubernetes
kubectl logs -f -n hunyuan3d deployment/hunyuan3d
```

### GPU Metrics
```bash
# Host
nvidia-smi

# Container
docker exec hunyuan3d nvidia-smi

# Kubernetes (with DCGM)
kubectl port-forward -n gpu-operator svc/dcgm-exporter 9400:9400
```

### Health Checks
Built-in health checks verify:
- Python environment is functional
- Dependencies are importable
- GPU is accessible

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| GPU not detected | Verify NVIDIA Container Toolkit installation |
| Out of memory | Enable LOW_VRAM_MODE or use mini model |
| Slow downloads | First run downloads ~5GB, use persistent cache |
| Port conflicts | Change port mapping: `-p 8888:7860` |
| K8s pod pending | Check GPU node labels and operator status |
| Build fails | Ensure Docker has enough disk space (50GB+) |

## Best Practices

### For Development
- Use `make dev-run` to mount code for live changes
- Enable verbose logging with environment variables
- Use mini model for faster iteration

### For Production
- Use StatefulSet for persistent storage per pod
- Configure HPA for auto-scaling
- Enable monitoring with Prometheus/Grafana
- Use Ingress with TLS for secure access
- Implement backup strategy for models
- Set up log aggregation (ELK, Loki)

### For Security
- Scan images regularly with Trivy
- Use private registry for images
- Rotate secrets periodically
- Apply Network Policies
- Enable audit logging
- Follow principle of least privilege

## Maintenance

### Regular Tasks
- **Weekly:** Check for security updates
- **Monthly:** Update base image and dependencies
- **Quarterly:** Review and update documentation

### Upgrades
```bash
# Pull latest code
git pull

# Rebuild image
make build

# Test thoroughly
make test

# Deploy
make k8s-deploy
```

## Support and Resources

- **GitHub:** https://github.com/Tencent-Hunyuan/Hunyuan3D-2
- **HuggingFace:** https://huggingface.co/tencent/Hunyuan3D-2
- **Discord:** https://discord.gg/dNBrdrGGMa
- **Official Site:** https://3d.hunyuan.tencent.com
- **Paper:** https://arxiv.org/abs/2501.12202

## License

This Docker image configuration is provided as-is. The Hunyuan3D-2 model is subject to the Tencent Hunyuan Community License. Please review the license terms before use in production.

## Contributing

Contributions welcome! Please:
1. Test changes thoroughly
2. Update documentation
3. Follow security best practices
4. Submit pull requests with clear descriptions

## Acknowledgments

Built on top of:
- Tencent Hunyuan3D-2 model
- NVIDIA CUDA Docker images
- Kubernetes GPU Operator
- Open source community tools

---

**Last Updated:** January 25, 2026  
**Version:** 1.0.0  
**Maintainer:** Docker Images Team
