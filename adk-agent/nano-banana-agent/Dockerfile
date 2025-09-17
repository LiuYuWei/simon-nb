# 使用官方 Python 映像檔作為基礎
FROM python:3.11-slim

# 設定容器內的工作目錄
WORKDIR /app

# 安裝編譯 Rust/Python native 套件需要的工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    rustc \
    cargo \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 複製並安裝依賴
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式的原始碼
COPY ./nano-banana-agent/ ./nano-banana-agent/

# 開放 ADK 服務的 port
EXPOSE 8787

# 容器啟動時執行的指令
CMD ["adk", "web", "--port", "8787", "--host", "0.0.0.0"]
