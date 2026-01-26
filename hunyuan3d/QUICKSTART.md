# Hunyuan3D-2 Docker Image - Quick Start Guide

This guide will help you quickly build and run the Hunyuan3D-2 Docker image.

## Prerequisites

✅ **Docker** (20.10+)  
✅ **NVIDIA GPU** with compute capability 7.0+  
✅ **NVIDIA Driver** (525.60.13+)  
✅ **NVIDIA Container Toolkit**  
✅ **Git**

## 5-Minute Quick Start

### 1. Install NVIDIA Container Toolkit

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Verify
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi
```

### 2. Build the Image

```bash
# Run the automated build script
./build.sh
```

This will:
- Clone the Hunyuan3D-2 repository
- Copy Docker configuration files
- Build the Docker image
- Show security scan results (if Trivy is installed)

**Build time:** ~15-30 minutes depending on internet speed

### 3. Run the Container

```bash
# Create directories for models and cache
mkdir -p models cache outputs

# Run with Gradio UI (default)
docker run --gpus all -p 7860:7860 \
  -v $(pwd)/models:/models \
  -v $(pwd)/cache:/cache \
  -v $(pwd)/outputs:/app/outputs \
  hunyuan3d:latest
```

**Access:** http://localhost:7860

### 4. Or Use Docker Compose

```bash
# Edit docker-compose.yml if needed, then:
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Different Run Modes

### Gradio Web Interface (Default)
```bash
docker run --gpus all -p 7860:7860 \
  -v $(pwd)/models:/models \
  -v $(pwd)/cache:/cache \
  hunyuan3d:latest
```

### API Server
```bash
docker run --gpus all -p 8080:8080 \
  -v $(pwd)/models:/models \
  -v $(pwd)/cache:/cache \
  hunyuan3d:latest api
```

### Low VRAM Mode (6GB GPU)
```bash
docker run --gpus all -p 7860:7860 \
  -e LOW_VRAM_MODE=true \
  -v $(pwd)/models:/models \
  -v $(pwd)/cache:/cache \
  hunyuan3d:latest
```

### Mini Model (Faster)
```bash
docker run --gpus all -p 7860:7860 \
  -e MODEL_PATH=tencent/Hunyuan3D-2mini \
  -e SUBFOLDER=hunyuan3d-dit-v2-mini \
  -v $(pwd)/models:/models \
  -v $(pwd)/cache:/cache \
  hunyuan3d:latest
```

### Turbo Model (Fastest)
```bash
docker run --gpus all -p 7860:7860 \
  -e MODEL_PATH=tencent/Hunyuan3D-2 \
  -e SUBFOLDER=hunyuan3d-dit-v2-0-turbo \
  -e ENABLE_FLASHVDM=true \
  -v $(pwd)/models:/models \
  -v $(pwd)/cache:/cache \
  hunyuan3d:latest
```

## Kubernetes Deployment

### Quick Deploy
```bash
# Install GPU operator
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm install gpu-operator nvidia/gpu-operator -n gpu-operator --create-namespace

# Deploy Hunyuan3D
kubectl apply -f kubernetes/deployment.yaml

# Check status
kubectl get pods -n hunyuan3d

# Access via port-forward
kubectl port-forward -n hunyuan3d svc/hunyuan3d 7860:80
```

See [kubernetes/README.md](kubernetes/README.md) for detailed Kubernetes documentation.

## Testing the Installation

### Test Image Generation

1. Access Gradio UI at http://localhost:7860
2. Upload a test image or use text prompt
3. Click "Generate 3D Model"
4. Wait for generation (3-5 minutes)
5. Download the generated GLB file

### Test API

```bash
# Convert image to base64
img_b64_str=$(base64 -i your-image.png)

# Make API request
curl -X POST "http://localhost:8080/generate" \
     -H "Content-Type: application/json" \
     -d '{"image": "'"$img_b64_str"'"}' \
     -o output.glb
```

## Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi

# Check Docker runtime
docker info | grep -i runtime
```

### Out of Memory
- Enable LOW_VRAM_MODE=true
- Use smaller model (Hunyuan3D-2mini)
- Close other GPU applications

### Slow Model Download
- First run downloads ~5GB of models
- May take 10-30 minutes depending on internet
- Models are cached in `/cache` volume

### Port Already in Use
```bash
# Use different port
docker run --gpus all -p 8888:7860 ... hunyuan3d:latest
```

## Directory Structure

```
hunyuan3d/
├── Dockerfile              # Main Docker image definition
├── entrypoint.sh          # Container entrypoint script
├── docker-compose.yml     # Docker Compose configuration
├── build.sh               # Automated build script
├── .dockerignore          # Files to exclude from build
├── README.md              # Main documentation
├── SECURITY.md            # Security guidelines
├── QUICKSTART.md          # This file
└── kubernetes/            # Kubernetes deployment files
    ├── deployment.yaml    # Standard deployment
    ├── api-deployment.yaml  # API server variant
    ├── statefulset.yaml   # StatefulSet variant
    └── README.md          # Kubernetes documentation
```

## VRAM Requirements

| Model | Minimum VRAM | Recommended VRAM | Speed |
|-------|--------------|------------------|-------|
| Hunyuan3D-2mini | 6 GB | 12 GB | Fast |
| Hunyuan3D-2 | 16 GB | 24 GB | Standard |
| Hunyuan3D-2mv | 16 GB | 24 GB | Standard |
| Hunyuan3D-2-Turbo | 16 GB | 24 GB | 2x Faster |

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `tencent/Hunyuan3D-2` | HuggingFace model repo |
| `SUBFOLDER` | `hunyuan3d-dit-v2-0` | Model subfolder |
| `TEXGEN_MODEL_PATH` | `tencent/Hunyuan3D-2` | Texture model |
| `LOW_VRAM_MODE` | `false` | Enable memory optimizations |
| `ENABLE_FLASHVDM` | `false` | Enable FlashVDM acceleration |
| `GRADIO_PORT` | `7860` | Gradio server port |
| `API_PORT` | `8080` | API server port |
| `HOST` | `0.0.0.0` | Server bind address |
| `HF_TOKEN` | - | HuggingFace token |

## Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🔒 Review [SECURITY.md](SECURITY.md) for security best practices
- ☸️ See [kubernetes/README.md](kubernetes/README.md) for K8s deployment
- 🐛 Report issues: https://github.com/Tencent-Hunyuan/Hunyuan3D-2/issues
- 💬 Join Discord: https://discord.gg/dNBrdrGGMa

## Support

- **GitHub:** https://github.com/Tencent-Hunyuan/Hunyuan3D-2
- **HuggingFace:** https://huggingface.co/tencent/Hunyuan3D-2
- **Official Site:** https://3d.hunyuan.tencent.com
- **Paper:** https://arxiv.org/abs/2501.12202

## License

This Docker image packages Tencent's Hunyuan3D-2 model under the Tencent Hunyuan Community License.
