import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, Query, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.video_processor import VideoProcessor

app = FastAPI(title="DeepSearch Biological Forensics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
PDF_PATH = os.path.join(BASE_DIR, "DeepSearch_Deepfake_Detection_System_Specification.pdf")

# Mount static frontend directories
app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/DeepSearch_Deepfake_Detection_System_Specification.pdf")
async def serve_pdf():
    if os.path.exists(PDF_PATH):
        return FileResponse(
            PDF_PATH,
            media_type="application/pdf",
            filename="DeepSearch_Deepfake_Detection_System_Specification.pdf"
        )
    return JSONResponse(status_code=404, content={"error": "PDF documentation not found"})

@app.get("/api/samples")
async def list_samples():
    """Lists available forensic test clips in samples/."""
    if not os.path.exists(SAMPLES_DIR):
        return []
    files = [f for f in os.listdir(SAMPLES_DIR) if f.endswith(('.mp4', '.avi', '.mov', '.webm'))]
    return [{"name": f, "url": f"/samples/{f}"} for f in files]

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    """Receives forensic video sample and saves to samples/."""
    os.makedirs(SAMPLES_DIR, exist_ok=True)
    file_path = os.path.join(SAMPLES_DIR, file.filename)
    content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    return {
        "status": "success",
        "filename": file.filename,
        "size_bytes": len(content),
        "url": f"/samples/{file.filename}"
    }

@app.post("/api/analyze")
async def analyze_video(
    file: UploadFile = None,
    filename: str = Query(None),
    method: str = Query("CHROM")
):
    """Executes full biological rPPG and spatio-temporal coherence analysis."""
    os.makedirs(SAMPLES_DIR, exist_ok=True)
    target_path = None

    if file:
        target_path = os.path.join(SAMPLES_DIR, file.filename)
        content = await file.read()
        with open(target_path, "wb") as buffer:
            buffer.write(content)
    elif filename:
        clean_name = os.path.basename(filename)
        target_path = os.path.join(SAMPLES_DIR, clean_name)

    if not target_path or not os.path.exists(target_path):
        return JSONResponse(
            status_code=400,
            content={"error": "Valid video file upload or existing sample filename must be provided."}
        )

    try:
        processor = VideoProcessor(method=method)
        # Process up to 180 frames (approx. 6 seconds of video at 30 FPS)
        results = processor.analyze_video(target_path, max_frames=180)
        return results
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Forensic analysis failed: {str(e)}"})

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
            await websocket.send_json({"status": "active"})
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    uvicorn.run("backend.server:app", host="127.0.0.1", port=8000, reload=True)
