# simon-nb: Nano Banana API as Google ADK AI Agent 專案

本專案展示一個完整的人工智慧代理系統，其中包含一個命令列介面（CLI），用於與生成式 AI 模型互動以處理和編輯圖像。

![img](./img/image_1.png)

## 系統架構

本專案由三個主要元件組成，各自在獨立的 Docker 容器中運行：

1.  **ADK 代理 (`adk-agent`)**: 這是使用 ADK 框架建立的核心代理。它接收包含圖像路徑和文字提示的請求，使用生成式 AI 模型（Gemini）執行所要求的圖像操作，並儲存結果。

2.  **圖像網路服務 (`image_web_url_service`)**: 一個基於 FastAPI 的網路服務，具有兩個主要功能：
    *   透過 `/images/...` 端點提供 `result` 目錄中生成的圖像。
    *   提供一個 `/upload/` 端點，允許客戶端將新圖像上傳到 `input` 目錄。

3.  **CLI 工具 (`simon-nb`)**: 一個基於 Python 的命令列工具，作為使用者介面。它允許使用者：
    *   透過協調對其他服務的呼叫來處理新圖像（來自 URL 或本地路徑）。
    *   直接將圖像上傳到圖像服務。

## 環境準備

在開始之前，請確保您已安裝以下軟體：

*   **Docker**: 用於建立和運行容器化服務。 [安裝 Docker](https://docs.docker.com/get-docker/)
*   **Python 3.11+**: 用於運行 CLI 工具。
*   **Google Cloud SDK**: 用於向 Google Cloud 服務（Vertex AI）進行身份驗證。請確保您已運行 `gcloud auth application-default login`。

## 安裝

1.  **複製儲存庫**

    ```bash
    git clone https://github.com/LiuYuWei/simon-nb.git
    cd simon-nb
    ```

2.  **設定環境變數**

    為了讓 `simon-nb` CLI 工具可以從任何目錄運行，您需要設定一個指向專案根目錄的環境變數。將以下行添加到您的 shell 設定檔中（例如 `~/.zshrc`, `~/.bashrc`）：

    ```bash
    export SIMON_NB_PROJECT_ROOT="/path/to/your/simon-nb/project/root"
    ```

    請記得將 `/path/to/your/simon-nb/project/root` 替換為您機器上專案的實際絕對路徑。重新啟動您的終端機或 source 設定檔（例如 `source ~/.zshrc`）以使變更生效。

3.  **安裝 CLI 工具**

    以可編輯模式安裝 CLI 工具及其依賴項。這使您可以在不需重新安裝的情況下修改腳本。

    ```bash
    pip install -e .
    ```

## 環境變數設定 (`.env`)

在執行代理（agent）之前，您需要設定環境變數以進行 Google Generative AI 服務的身份驗證。代理程式可以透過兩種方式進行設定：使用 Vertex AI 或使用 Google AI Studio API 金鑰。

在 `adk-agent/nano-banana-agent/` 目錄中建立一個名為 `.env` 的檔案。此檔案不受 Git 追蹤，您必須手動建立。

**注意：** ADK 框架會在代理啟動時自動從此 `.env` 檔案載入變數。

### 方法一：使用 Vertex AI（建議）

如果您已經在使用 Google Cloud，這是建議的生產環境方法。

1.  請確保您已按照 **環境準備** 中的說明使用 gcloud CLI 進行身份驗證。
2.  建立 `.env` 檔案，內容如下：

    ```
    GOOGLE_GENAI_USE_VERTEXAI=true
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    ```

    請將 `"your-gcp-project-id"` 替換為您實際的 Google Cloud 專案 ID。

### 方法二：使用 Google AI Studio API 金鑰

這種方法對於快速測試和開發更為簡單。

1.  從 [Google AI Studio](https://aistudio.google.com/app/apikey) 取得 API 金鑰。
2.  建立 `.env` 檔案，內容如下：

    ```
    GOOGLE_API_KEY="your-google-api-key"
    ```

    請將 `"your-google-api-key"` 替換為您實際的 API 金鑰。

## 使用方法

1.  **建立 Docker 映像檔**

    首先，為代理和圖像服務建立 Docker 映像檔。此命令只需運行一次，或在您更改服務的原始碼（`agent.py`, `image_web_url_service/main.py`）或其 Dockerfile 時運行。

    ```bash
    make build
    ```

2.  **運行服務**

    在背景中啟動這兩個服務。

    ```bash
    make run
    ```

    您可以使用 `make logs-adk-agent` 或 `make logs-image-service` 來查看每個服務的日誌。

3.  **使用 CLI 工具**

    服務運行後，您可以從系統的任何地方使用 `simon-nb` 命令。

    **語法：**
    ```bash
    simon-nb <image_source> "<prompt>"
    ```

    *   `<image_source>`: 可以是圖像的 URL 或本地檔案路徑。
    *   `"<prompt>"`: 給代理的文字指令。

    **範例（使用本地圖像）：**
    ```bash
    simon-nb "/path/to/my/photo.jpg" "將背景更換為專業的辦公室場景"
    ```

    **範例（使用 URL）：**
    ```bash
    simon-nb "https://example.com/image.png" "讓這張圖看起來像水彩畫"
    ```

    最終處理完成的圖像將儲存在您目前的工作目錄中。

4.  **停止服務**

    若要停止正在運行的 Docker 容器，請使用：
    ```bash
    make stop
    ```

## API 端點

### 圖像上傳

`image_web_url_service` 提供一個用於直接上傳圖像的端點。

*   **URL**: `/upload/`
*   **方法**: `POST`
*   **內文**: `multipart/form-data`，其中包含一個名為 `file` 的圖像欄位。

**使用 `curl` 的範例：**
```bash
curl -X POST -F "file=@/path/to/your/image.jpg" http://127.0.0.1:8000/upload/
```

**成功回應：**
```json
{
  "file_path": "/nano-banana-agent/input/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.jpg"
}
```
