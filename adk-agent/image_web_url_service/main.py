import os
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
import uvicorn

# 初始化 FastAPI 應用
app = FastAPI()

# --- 靜態圖片服務相關設定 ---

# 確定 result 圖片目錄的絕對路徑 (用於提供圖片)
result_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'nano-banana-agent', 'result')
)
os.makedirs(result_directory, exist_ok=True)

# 掛載靜態檔案目錄，讓 /images 路徑可以存取 result 資料夾的圖片
app.mount("/images", StaticFiles(directory=result_directory), name="images")

# --- 圖片上傳服務相關設定 ---

# 確定 input 圖片目錄的絕對路徑 (用於儲存上傳的圖片)
input_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'nano-banana-agent', 'input')
)
os.makedirs(input_directory, exist_ok=True)

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    """
    接收上傳的圖片，儲存到 input 資料夾，並回傳儲存路徑。
    """
    try:
        # 產生唯一的檔案名稱，保留原始副檔名
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(input_directory, unique_filename)

        # 儲存檔案
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 回傳包含新檔案路徑的 JSON
        return {"file_path": file_path}
    finally:
        file.file.close()

@app.get("/")
def read_root():
    return {"message": "圖片服務正在運行。請透過 /images/<filename> 訪問圖片，或透過 POST /upload/ 上傳圖片。"}

# 執行服務
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)