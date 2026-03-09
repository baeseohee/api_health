from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import shutil
import os
import json
import sys
from scripts.processor import HARProcessor
from scripts.health_checker import APIHealthChecker
from scripts.notifier import TeamsNotifier
from scheduler import scheduler

app = FastAPI()

# Ensure directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

@app.post("/upload")
async def upload_har(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "path": file_path}

@app.post("/run-check/{filename}")
async def run_check(filename: str):
    har_path = f"uploads/{filename}"
    if not os.path.exists(har_path):
        raise HTTPException(status_code=404, detail="HAR file not found")
    
    try:
        # Step 1: Process HAR
        processor = HARProcessor()
        processor.process(har_path)
        
        # Step 2: Run Health Check via Pytest
        import subprocess
        # Run pytest and capture output (not strict requirement since we write to file)
        # We ignore exit code because pytest returns 1 if any test fails
        subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_dynamic.py"], 
            cwd=os.getcwd(),
            capture_output=True
        )
        
        # Load results
        with open("data/health_check_results.json", "r", encoding="utf-8") as f:
            results = json.load(f)
            
        # Step 3: Send Teams Notification
        try:
            with open("config/settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
                webhook_url = settings.get("teams_webhook_url")
            
            if webhook_url:
                notifier = TeamsNotifier(webhook_url)
                notifier.send_report(results)
        except Exception as n_err:
            print(f"Warning: Failed to send notification: {n_err}")
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results")
async def get_results():
    path = "data/health_check_results.json"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/monitor")
async def read_monitor():
    return FileResponse("static/monitor.html")

# Scheduler endpoints
class SchedulerConfig(BaseModel):
    interval_minutes: int

@app.post("/api/scheduler/start")
async def start_scheduler(config: SchedulerConfig):
    result = scheduler.start(config.interval_minutes)
    return result

@app.post("/api/scheduler/stop")
async def stop_scheduler():
    result = scheduler.stop()
    return result

@app.get("/api/scheduler/status")
async def get_scheduler_status():
    return scheduler.get_status()

@app.get("/api/scheduler/history")
async def get_scheduler_history(limit: int = 50):
    return scheduler.get_history(limit)

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
