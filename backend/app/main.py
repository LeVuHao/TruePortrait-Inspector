"""
FastAPI REST API Service for PhotoCheck
Phụ trách bởi: HẢO
Cung cấp Endpoint:
- GET  /api/v1/health       : Kiểm tra trạng thái máy chủ
- POST /api/v1/analyze      : Upload file ảnh và chạy toàn bộ Image Processing Pipeline
- GET  /api/v1/presets      : Danh sách các presets và thông số cấu hình
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .pipeline import run_pipeline
from .core.config import PRESET_CONFIGS, DEFAULT_PRESET

app = FastAPI(
    title="PhotoCheck API Service",
    description="Backend API phục vụ kiểm tra và đánh giá chất lượng ảnh thẻ tự động bằng Xử lý ảnh số (DIP)",
    version="1.0.0"
)

# Cấu hình CORS để Frontend React kết nối thông suốt
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "PhotoCheck API",
        "status": "online",
        "docs_url": "/docs"
    }


@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "service": "PhotoCheck Backend"}


@app.get("/api/v1/presets")
def get_presets():
    return {
        "default_preset": DEFAULT_PRESET,
        "presets": PRESET_CONFIGS
    }


@app.post("/api/v1/analyze")
async def analyze_photo(
    file: UploadFile = File(...),
    preset: str = Form(DEFAULT_PRESET)
):
    """
    Endpoint tiếp nhận file ảnh tải lên từ React Web Dashboard.
    """
    # 1. Kiểm tra định dạng đuôi file hợp lệ
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    filename_lower = (file.filename or "").lower()
    if not any(filename_lower.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng file không được hỗ trợ ({file.filename}). Vui lòng tải lên file ảnh JPG hoặc PNG."
        )
        
    try:
        # 2. Đọc byte data
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="File tải lên không có dữ liệu (rỗng).")
            
        # 3. Chạy Image Processing Pipeline
        result = run_pipeline(file_bytes, preset_name=preset)
        return result
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi trong quá trình xử lý ảnh: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
