# simon-nb: Nano Banana API as Google ADK AI Agent Project

This project demonstrates a complete AI agent system with a command-line interface (CLI) for interacting with a generative AI model to process and edit images.

![img](./img/image_1.png)

## Architecture

The project consists of three main components that run in separate Docker containers:

1.  **ADK Agent (`adk-agent`)**: This is the core agent built using the ADK framework. It receives requests containing an image path and a text prompt, uses a generative AI model (Gemini) to perform the requested image manipulation, and saves the result.

2.  **Image Web Service (`image_web_url_service`)**: A FastAPI-based web service with two primary functions:
    *   It serves the generated images from the `result` directory via a `/images/...` endpoint.
    *   It provides an `/upload/` endpoint to allow clients to upload new images to the `input` directory.

3.  **CLI Tool (`simon-nb`)**: A Python-based command-line tool that acts as the user interface. It allows the user to:
    *   Process a new image (from a URL or local path) by orchestrating the calls to the other services.
    *   Upload images directly to the image service.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Docker**: To build and run the containerized services. [Install Docker](https://docs.docker.com/get-docker/)
*   **Python 3.11+**: For running the CLI tool.
*   **Google Cloud SDK**: Required for authenticating with Google Cloud services (Vertex AI). Make sure you have run `gcloud auth application-default login`.

## Installation

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/LiuYuWei/simon-nb.git
    cd simon-nb
    ```

2.  **Set Environment Variable**

    To allow the `simon-nb` CLI tool to be run from any directory, you need to set an environment variable that points to the project's root directory. Add the following line to your shell's configuration file (e.g., `~/.zshrc`, `~/.bashrc`):

    ```bash
    export SIMON_NB_PROJECT_ROOT="/path/to/your/simon-nb/project/root"
    ```

    Remember to replace `/path/to/your/simon-nb/project/root` with the actual absolute path to the project on your machine. Restart your terminal or source the configuration file (e.g., `source ~/.zshrc`) for the change to take effect.

3.  **Install CLI Tool**

    Install the CLI tool and its dependencies in editable mode. This allows you to make changes to the script without needing to reinstall.

    ```bash
    pip install -e .
    ```

## Environment Variable Setup (`.env`)

Before running the agent, you need to set up environment variables for authentication with Google Generative AI services. The agent can be configured in two ways: using Vertex AI or using a Google AI Studio API key.

Create a file named `.env` in the `adk-agent/nano-banana-agent/` directory. This file is not tracked by Git, so you must create it manually.

**Note:** The ADK framework automatically loads variables from this `.env` file when the agent starts.

### Method 1: Using Vertex AI (Recommended)

This is the recommended method for production environments if you are already using Google Cloud.

1.  Ensure you have authenticated with the gcloud CLI as described in the **Prerequisites** section.
2.  Create the `.env` file with the following content:

    ```
    GOOGLE_GENAI_USE_VERTEXAI=true
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    ```

    Replace `"your-gcp-project-id"` with your actual Google Cloud project ID.

### Method 2: Using a Google AI Studio API Key

This method is simpler for quick testing and development.

1.  Obtain an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Create the `.env` file with the following content:

    ```
    GOOGLE_API_KEY="your-google-api-key"
    ```

    Replace `"your-google-api-key"` with your actual API key.

## Usage

1.  **Build the Docker Images**

    First, build the Docker images for the agent and the image service. This command only needs to be run once, or whenever you make changes to the services' source code (`agent.py`, `image_web_url_service/main.py`) or their Dockerfiles.

    ```bash
    make build
    ```

2.  **Run the Services**

    Start the two services in the background.

    ```bash
    make run
    ```

    You can check the logs for each service using `make logs-adk-agent` or `make logs-image-service`.

3.  **Use the CLI Tool**

    Once the services are running, you can use the `simon-nb` command from anywhere on your system.

    **Syntax:**
    ```bash
    simon-nb <image_source> "<prompt>"
    ```

    *   `<image_source>`: Can be a URL to an image or a local file path.
    *   `"<prompt>"`: The text instruction for the agent.

    **Example (with a local image):**
    ```bash
    simon-nb "/path/to/my/photo.jpg" "Change the background to a professional office setting"
    ```

    **Example (with a URL):**
    ```bash
    simon-nb "https://example.com/image.png" "Make this look like a watercolor painting"
    ```

    The final processed image will be saved in your current working directory.

4.  **Stopping the Services**

    To stop the running Docker containers, use:
    ```bash
    make stop
    ```

## API Endpoint

### Image Upload

The `image_web_url_service` exposes an endpoint for direct image uploads.

*   **URL**: `/upload/`
*   **Method**: `POST`
*   **Body**: `multipart/form-data` with a `file` field containing the image.

**Example using `curl`:**
```bash
curl -X POST -F "file=@/path/to/your/image.jpg" http://127.0.0.1:8000/upload/
```

**Success Response:**
```json
{
  "file_path": "/nano-banana-agent/input/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.jpg"
}
```
