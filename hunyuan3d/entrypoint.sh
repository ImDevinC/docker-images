#!/bin/bash
set -e

# Entrypoint script for Hunyuan3D-2 Docker container
# This script provides flexible modes of operation

# Print GPU info for debugging
echo "=== GPU Information ==="
nvidia-smi || echo "Warning: nvidia-smi not available or no GPU detected"
echo "======================="

# Default values
MODE="${1:-gradio}"
HOST="${HOST:-0.0.0.0}"
GRADIO_PORT="${GRADIO_PORT:-7860}"
API_PORT="${API_PORT:-8080}"
MODEL_PATH="${MODEL_PATH:-tencent/Hunyuan3D-2.1}"
SUBFOLDER="${SUBFOLDER:-hunyuan3d-dit-v2-1}"
TEXGEN_MODEL_PATH="${TEXGEN_MODEL_PATH:-tencent/Hunyuan3D-2.1}"

# Function to run Gradio app
run_gradio() {
    echo "Starting Gradio app on $HOST:$GRADIO_PORT"
    echo "Model: $MODEL_PATH (subfolder: $SUBFOLDER)"
    
    # Check for low VRAM mode
    VRAM_FLAG=""
    if [ "${LOW_VRAM_MODE:-false}" = "true" ]; then
        echo "Low VRAM mode enabled"
        VRAM_FLAG="--low_vram_mode"
    fi
    
    # Check for FlashVDM
    FLASHVDM_FLAG=""
    if [ "${ENABLE_FLASHVDM:-false}" = "true" ]; then
        echo "FlashVDM enabled"
        FLASHVDM_FLAG="--enable_flashvdm"
    fi
    
    exec python gradio_app.py \
        --model_path "$MODEL_PATH" \
        --subfolder "$SUBFOLDER" \
        --texgen_model_path "$TEXGEN_MODEL_PATH" \
        --server_name "$HOST" \
        --server_port "$GRADIO_PORT" \
        $VRAM_FLAG \
        $FLASHVDM_FLAG
}

# Function to run API server
run_api() {
    echo "Starting API server on $HOST:$API_PORT"
    exec python api_server.py --host "$HOST" --port "$API_PORT"
}

# Function to run minimal demo
run_demo() {
    echo "Running minimal demo"
    exec python minimal_demo.py "$@"
}

# Function to run custom Python script
run_python() {
    echo "Running Python: $*"
    exec python "$@"
}

# Function to run bash
run_bash() {
    echo "Starting bash shell"
    exec /bin/bash
}

# Main logic
case "$MODE" in
    gradio)
        run_gradio
        ;;
    api)
        run_api
        ;;
    demo)
        shift
        run_demo "$@"
        ;;
    python)
        shift
        run_python "$@"
        ;;
    bash|shell)
        run_bash
        ;;
    *)
        echo "Unknown mode: $MODE"
        echo ""
        echo "Usage: docker run [options] hunyuan3d [MODE] [ARGS]"
        echo ""
        echo "Modes:"
        echo "  gradio  - Start Gradio web interface (default)"
        echo "  api     - Start REST API server"
        echo "  demo    - Run minimal demo script"
        echo "  python  - Run custom Python script"
        echo "  bash    - Start bash shell"
        echo ""
        echo "Environment Variables:"
        echo "  HOST                - Server host (default: 0.0.0.0)"
        echo "  GRADIO_PORT        - Gradio port (default: 7860)"
        echo "  API_PORT           - API server port (default: 8080)"
        echo "  MODEL_PATH         - HuggingFace model path (default: tencent/Hunyuan3D-2)"
        echo "  SUBFOLDER          - Model subfolder (default: hunyuan3d-dit-v2-0)"
        echo "  TEXGEN_MODEL_PATH  - Texture generation model (default: tencent/Hunyuan3D-2)"
        echo "  LOW_VRAM_MODE      - Enable low VRAM mode (default: false)"
        echo "  ENABLE_FLASHVDM    - Enable FlashVDM (default: false)"
        echo "  HF_TOKEN           - HuggingFace token for private models"
        echo ""
        echo "Examples:"
        echo "  docker run -p 7860:7860 hunyuan3d"
        echo "  docker run -p 8080:8080 hunyuan3d api"
        echo "  docker run -e LOW_VRAM_MODE=true hunyuan3d gradio"
        exit 1
        ;;
esac
