# Makefile for Hunyuan3D-2 Docker Image
.PHONY: help build run run-api run-mini run-turbo test clean logs shell scan push

# Default values
IMAGE_NAME ?= hunyuan3d
IMAGE_TAG ?= latest
REGISTRY ?=
GRADIO_PORT ?= 7860
API_PORT ?= 8080

help: ## Show this help message
	@echo "Hunyuan3D-2 Docker Image - Make Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Environment Variables:"
	@echo "  IMAGE_NAME    Docker image name (default: hunyuan3d)"
	@echo "  IMAGE_TAG     Docker image tag (default: latest)"
	@echo "  REGISTRY      Docker registry (default: empty)"
	@echo "  GRADIO_PORT   Gradio port (default: 7860)"
	@echo "  API_PORT      API server port (default: 8080)"

build: ## Build Docker image
	./build.sh

run: ## Run with Gradio UI (standard model)
	@mkdir -p models cache outputs
	docker run --gpus all -p $(GRADIO_PORT):7860 \
		-v $(PWD)/models:/models \
		-v $(PWD)/cache:/cache \
		-v $(PWD)/outputs:/app/outputs \
		--name hunyuan3d \
		--rm \
		$(IMAGE_NAME):$(IMAGE_TAG)

run-api: ## Run API server
	@mkdir -p models cache outputs
	docker run --gpus all -p $(API_PORT):8080 \
		-v $(PWD)/models:/models \
		-v $(PWD)/cache:/cache \
		-v $(PWD)/outputs:/app/outputs \
		--name hunyuan3d-api \
		--rm \
		$(IMAGE_NAME):$(IMAGE_TAG) api

run-mini: ## Run with mini model (less VRAM)
	@mkdir -p models cache outputs
	docker run --gpus all -p $(GRADIO_PORT):7860 \
		-e MODEL_PATH=tencent/Hunyuan3D-2mini \
		-e SUBFOLDER=hunyuan3d-dit-v2-mini \
		-e LOW_VRAM_MODE=true \
		-v $(PWD)/models:/models \
		-v $(PWD)/cache:/cache \
		-v $(PWD)/outputs:/app/outputs \
		--name hunyuan3d-mini \
		--rm \
		$(IMAGE_NAME):$(IMAGE_TAG)

run-turbo: ## Run with turbo model (faster)
	@mkdir -p models cache outputs
	docker run --gpus all -p $(GRADIO_PORT):7860 \
		-e MODEL_PATH=tencent/Hunyuan3D-2 \
		-e SUBFOLDER=hunyuan3d-dit-v2-0-turbo \
		-e ENABLE_FLASHVDM=true \
		-v $(PWD)/models:/models \
		-v $(PWD)/cache:/cache \
		-v $(PWD)/outputs:/app/outputs \
		--name hunyuan3d-turbo \
		--rm \
		$(IMAGE_NAME):$(IMAGE_TAG)

run-detached: ## Run in background with Gradio UI
	@mkdir -p models cache outputs
	docker run -d --gpus all -p $(GRADIO_PORT):7860 \
		-v $(PWD)/models:/models \
		-v $(PWD)/cache:/cache \
		-v $(PWD)/outputs:/app/outputs \
		--name hunyuan3d \
		--restart unless-stopped \
		$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "Container started. Access at http://localhost:$(GRADIO_PORT)"

compose-up: ## Start with docker-compose
	docker-compose up -d

compose-down: ## Stop docker-compose
	docker-compose down

compose-logs: ## View docker-compose logs
	docker-compose logs -f

test: ## Test GPU access
	docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi

shell: ## Open shell in running container
	docker exec -it hunyuan3d /bin/bash

logs: ## View container logs
	docker logs -f hunyuan3d

stop: ## Stop running container
	docker stop hunyuan3d || true
	docker stop hunyuan3d-api || true
	docker stop hunyuan3d-mini || true
	docker stop hunyuan3d-turbo || true

clean: ## Remove container and local cache
	docker stop hunyuan3d || true
	docker rm hunyuan3d || true
	docker stop hunyuan3d-api || true
	docker rm hunyuan3d-api || true
	@read -p "Delete cache and models? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf cache/* models/* outputs/*; \
		echo "Cleaned cache, models, and outputs"; \
	fi

clean-image: ## Remove Docker image
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG) || true

scan: ## Scan image for vulnerabilities
	@if command -v trivy >/dev/null 2>&1; then \
		trivy image --severity HIGH,CRITICAL $(IMAGE_NAME):$(IMAGE_TAG); \
	else \
		echo "Trivy not installed. Install from: https://github.com/aquasecurity/trivy"; \
	fi

tag: ## Tag image for registry
	@if [ -z "$(REGISTRY)" ]; then \
		echo "Error: REGISTRY not set. Use: make tag REGISTRY=your-registry.com"; \
		exit 1; \
	fi
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "Tagged: $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)"

push: tag ## Push image to registry
	@if [ -z "$(REGISTRY)" ]; then \
		echo "Error: REGISTRY not set. Use: make push REGISTRY=your-registry.com"; \
		exit 1; \
	fi
	docker push $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "Pushed: $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)"

k8s-deploy: ## Deploy to Kubernetes
	kubectl apply -f kubernetes/deployment.yaml

k8s-delete: ## Delete from Kubernetes
	kubectl delete -f kubernetes/deployment.yaml

k8s-logs: ## View Kubernetes logs
	kubectl logs -f -n hunyuan3d deployment/hunyuan3d

k8s-shell: ## Open shell in Kubernetes pod
	kubectl exec -it -n hunyuan3d deployment/hunyuan3d -- /bin/bash

k8s-status: ## Check Kubernetes deployment status
	kubectl get all -n hunyuan3d

info: ## Show image information
	@echo "Image: $(IMAGE_NAME):$(IMAGE_TAG)"
	@docker images $(IMAGE_NAME):$(IMAGE_TAG) --format "Size: {{.Size}}"
	@docker images $(IMAGE_NAME):$(IMAGE_TAG) --format "Created: {{.CreatedAt}}"
	@if [ -n "$(REGISTRY)" ]; then \
		echo "Registry: $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)"; \
	fi

gpu-info: ## Show GPU information
	nvidia-smi

docker-info: ## Show Docker GPU runtime info
	docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi

# Development targets
dev-build: ## Build without cache
	docker build --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) .

dev-run: ## Run with code mounted (for development)
	@mkdir -p models cache outputs
	docker run --gpus all -p $(GRADIO_PORT):7860 \
		-v $(PWD)/models:/models \
		-v $(PWD)/cache:/cache \
		-v $(PWD)/outputs:/app/outputs \
		-v $(PWD)/Hunyuan3D-2:/app \
		--name hunyuan3d-dev \
		--rm \
		$(IMAGE_NAME):$(IMAGE_TAG)
