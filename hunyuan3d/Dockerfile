# Hunyuan3D-2 Secure Docker Image
# Base image with CUDA support for GPU acceleration
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Security: Set timezone and locale
ENV TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Create non-root user for security
RUN groupadd -r hunyuan -g 1000 && \
    useradd -r -u 1000 -g hunyuan -m -s /bin/bash hunyuan && \
    mkdir -p /app /models /cache && \
    chown -R hunyuan:hunyuan /app /models /cache

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools
    build-essential \
    cmake \
    ninja-build \
    git \
    # Python
    python3.10 \
    python3.10-dev \
    python3-pip \
    # Graphics libraries
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3.10 /usr/bin/python

# Upgrade pip and install build dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir pybind11 ninja packaging

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY --chown=hunyuan:hunyuan ./src/requirements.txt /app/

# Install PyTorch with CUDA support (specify version for reproducibility)
RUN pip install --no-cache-dir \
    torch==2.1.0 \
    torchvision==0.16.0 \
    --index-url https://download.pytorch.org/whl/cu121

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=hunyuan:hunyuan ./src /app/

# Install the package
RUN pip install --no-cache-dir -e .

# Build custom CUDA extensions
# Custom rasterizer
RUN cd /app/hy3dgen/texgen/custom_rasterizer && \
    python setup.py install && \
    cd /app

# Differentiable renderer
RUN cd /app/hy3dgen/texgen/differentiable_renderer && \
    python setup.py install && \
    cd /app

# Security: Remove unnecessary files and set proper permissions
RUN find /app -type f -name "*.pyc" -delete && \
    find /app -type d -name "__pycache__" -delete && \
    chmod -R 755 /app && \
    chmod +x /app/entrypoint.sh

# Set cache directories with proper permissions
ENV HF_HOME=/cache/huggingface \
    TORCH_HOME=/cache/torch \
    TRANSFORMERS_CACHE=/cache/huggingface/transformers

RUN mkdir -p $HF_HOME $TORCH_HOME $TRANSFORMERS_CACHE && \
    chown -R hunyuan:hunyuan /cache

# Switch to non-root user
USER hunyuan

# Expose ports for Gradio and API server
EXPOSE 7860 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import torch; import hy3dgen" || exit 1

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command (can be overridden)
CMD ["gradio"]
