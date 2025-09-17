import uuid
from google.adk.agents import Agent

from google import genai
from google.genai import types
import base64, os

def generate_nano_banana(image_path: str, user_feature: str):
    try:
        # 偵錯：檢查檔案是否存在
        if not os.path.exists(image_path):
            return {
                "status": "error",
                "report": f"File not found inside agent container at path: {image_path}"
            }
        # 將圖片轉成 Base64
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        return {
            "status": "error",
            "report": f"Error reading file '{image_path}': {e}"
        }

    if os.getenv("GOOGLE_GENAI_USE_VERTEXAI"):
        client = genai.Client(
            vertexai=True,
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location="global",
        )
    else:
        client = genai.Client(
            vertexai=False,
            api_key=os.getenv('GOOGLE_API_KEY'))

    msg1_image1 = types.Part.from_bytes(
        data=base64.b64decode(encoded_string),
        mime_type="image/jpeg",
    )

    model = "gemini-2.5-flash-image-preview"
    contents = [
        types.Content(
            role="user",
            parts=[msg1_image1, types.Part.from_text(text=user_feature)]
        ),
    ]

    cfg = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=32768,
        response_modalities=["TEXT", "IMAGE"],
    )

    text_out = []
    image_urls = []  # 儲存圖片 URL

    # 定義圖片儲存目錄
    result_dir = os.path.join(os.path.dirname(__file__), 'result')
    os.makedirs(result_dir, exist_ok=True)
    
    # 圖片服務的基礎 URL
    image_service_base_url = "http://localhost:8000/images"

    for chunk in client.models.generate_content_stream(
        model=model, contents=contents, config=cfg
    ):
        if getattr(chunk, "text", None):
            print(chunk.text, end="")
            text_out.append(chunk.text)

        for cand in getattr(chunk, "candidates", []) or []:
            parts = getattr(cand, "content", None) and cand.content.parts or []
            for p in parts:
                if getattr(p, "inline_data", None):
                    # 產生唯一檔案名稱
                    image_filename = f"{uuid.uuid4()}.jpg"
                    image_filepath = os.path.join(result_dir, image_filename)

                    # 將圖片儲存到檔案
                    with open(image_filepath, "wb") as f:
                        f.write(p.inline_data.data)
                    
                    print(f"\n[Saved image to {image_filepath}]")

                    # 產生圖片 URL
                    image_url = f"{image_service_base_url}/{image_filename}"
                    image_urls.append(image_url)
                    print(f"\n[Generated image URL: {image_url}]")
    if len(image_urls) > 0:
        return {
            "status": "success",
            "report": image_urls
        }
    else:
        return {
            "status": "error",
            "report": f"No image generated. Only get text: {text_out}"
        }

root_agent = Agent(
    name="NanoBananaAgent",
    model="gemini-2.0-flash",
    description="專門處理影像編輯與生成的代理，透過 Nano Banana 工具依照使用者指令修改或生成圖片。",
    instruction="你只能使用 Nano Banana 工具，根據使用者的輸入圖片與文字指令進行處理，並輸出指向生成圖片的 URL，不要提供任何額外解釋或文字。",
    tools=[generate_nano_banana],
)