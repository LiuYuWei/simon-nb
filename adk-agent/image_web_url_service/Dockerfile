# 使用官方 Python 映像檔作為基礎
FROM python:3.11-slim

# 設定容器內的工作目錄
WORKDIR /app

# 複製並安裝依賴
COPY ./image_web_url_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式的原始碼
COPY ./image_web_url_service/main.py ./main.py

# 開放圖片服務的 port
EXPOSE 8000

# 容器啟動時執行的指令
CMD ["python", "main.py"]
