# Makefile for the project (Docker-focused)

# Variables
ADK_AGENT_IMAGE_NAME = nano-banana-agent
ADK_AGENT_TAG = latest
ADK_AGENT_CONTAINER_NAME = nano-banana-agent-container

IMAGE_SERVICE_IMAGE_NAME = image-web-url-service
IMAGE_SERVICE_TAG = latest
IMAGE_SERVICE_CONTAINER_NAME = image-web-url-service-container

# Targets

.PHONY: build-adk-agent build-image-service build run-adk-agent run-image-service run stop-adk-agent stop-image-service stop logs-adk-agent logs-image-service logs shell-adk-agent shell-image-service shell clean

build: build-adk-agent build-image-service

build-adk-agent:
	@echo "Building ADK agent Docker image..."
	docker build -t $(ADK_AGENT_IMAGE_NAME):$(ADK_AGENT_TAG) -f adk-agent/nano-banana-agent/Dockerfile adk-agent/

build-image-service:
	@echo "Building image service Docker image..."
	docker build -t $(IMAGE_SERVICE_IMAGE_NAME):$(IMAGE_SERVICE_TAG) -f adk-agent/image_web_url_service/Dockerfile adk-agent/

run: run-adk-agent run-image-service

run-adk-agent:
	@echo "Running ADK agent Docker container..."
	docker run -d --name $(ADK_AGENT_CONTAINER_NAME) \
		--env-file adk-agent/nano-banana-agent/.env \
		-p 8787:8787 \
		-v $(shell pwd)/adk-agent/nano-banana-agent/input:/nano-banana-agent/input \
		-v $(shell pwd)/adk-agent/nano-banana-agent/result:/app/nano-banana-agent/result \
		-v $(HOME)/.config/gcloud/application_default_credentials.json:/gcp_adc.json \
		-e GOOGLE_APPLICATION_CREDENTIALS=/gcp_adc.json \
		$(ADK_AGENT_IMAGE_NAME):$(ADK_AGENT_TAG)

run-image-service:
	@echo "Running image service Docker container..."
	docker run -d --name $(IMAGE_SERVICE_CONTAINER_NAME) \
		-p 8000:8000 \
		-v $(shell pwd)/adk-agent/nano-banana-agent/result:/nano-banana-agent/result \
		-v $(shell pwd)/adk-agent/nano-banana-agent/input:/nano-banana-agent/input \
		$(IMAGE_SERVICE_IMAGE_NAME):$(IMAGE_SERVICE_TAG)

stop: stop-adk-agent stop-image-service

stop-adk-agent:
	@echo "Stopping ADK agent Docker container..."
	-docker stop $(ADK_AGENT_CONTAINER_NAME)
	-docker rm $(ADK_AGENT_CONTAINER_NAME)

stop-image-service:
	@echo "Stopping image service Docker container..."
	-docker stop $(IMAGE_SERVICE_CONTAINER_NAME)
	-docker rm $(IMAGE_SERVICE_CONTAINER_NAME)

logs: logs-adk-agent

logs-adk-agent:
	@echo "Showing ADK agent container logs..."
	docker logs -f $(ADK_AGENT_CONTAINER_NAME)

logs-image-service:
	@echo "Showing image service container logs..."
	docker logs -f $(IMAGE_SERVICE_CONTAINER_NAME)

shell: shell-adk-agent

shell-adk-agent:
	@echo "Entering ADK agent container shell..."
	docker exec -it $(ADK_AGENT_CONTAINER_NAME) /bin/bash

shell-image-service:
	@echo "Entering image service container shell..."
	docker exec -it $(IMAGE_SERVICE_CONTAINER_NAME) /bin/bash

clean: stop
	@echo "Cleaning up..."
	-docker rmi $(ADK_AGENT_IMAGE_NAME):$(ADK_AGENT_TAG)
	-docker rmi $(IMAGE_SERVICE_IMAGE_NAME):$(IMAGE_SERVICE_TAG)
	find . -type d -name "__pycache__" -exec rm -r {} +
