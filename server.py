from fastapi import FastAPI, Request, HTTPException, Response
from pydantic import BaseModel
import time
import socket
import os
import sys
import asyncio
import random
import psutil
from datetime import datetime

app = FastAPI(title="Infrastructure Testing API", version="1.0.0")
start_time = time.time()
request_counter = 0

class Item(BaseModel):
    name: str
    value: str

@app.middleware("http")
async def count_requests(request: Request, call_next):
    global request_counter
    request_counter += 1
    response = await call_next(request)
    return response

@app.get("/")
async def home():
    return {
        "message": "Infrastructure Testing Server",
        "hostname": socket.gethostname(),
        "uptime_seconds": round(time.time() - start_time, 2),
        "total_requests": request_counter,
        "endpoints": [
            "/health", "/metrics", "/echo", "/slow", "/error",
            "/cpu", "/memory", "/env", "/status/{code}", "/load"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "cpu_usage": psutil.cpu_percent() < 90,
            "memory_available": psutil.virtual_memory().available > 100 * 1024 * 1024,
            "disk_available": psutil.disk_usage('/').free > 1 * 1024 * 1024 * 1024
        }
    }

@app.get("/health/live")
async def liveness():
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    return {"status": "ready"}

@app.get("/metrics")
async def metrics():
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        "uptime_seconds": round(time.time() - start_time, 2),
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "python_version": sys.version.split()[0],
        "total_requests": request_counter,
        "cpu": {
            "percent": cpu_percent,
            "count": psutil.cpu_count()
        },
        "memory": {
            "total_mb": round(memory.total / 1024 / 1024, 2),
            "available_mb": round(memory.available / 1024 / 1024, 2),
            "used_percent": memory.percent
        },
        "disk": {
            "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
            "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
            "used_percent": disk.percent
        }
    }

@app.get("/cpu")
async def cpu_load(duration: int = 1):
    if duration > 10:
        raise HTTPException(status_code=400, detail="Duration cannot exceed 10 seconds")

    cpu_usage = []
    for _ in range(duration):
        cpu_usage.append(psutil.cpu_percent(interval=1))

    return {
        "average_cpu_percent": round(sum(cpu_usage) / len(cpu_usage), 2),
        "samples": cpu_usage,
        "cpu_count": psutil.cpu_count()
    }

@app.get("/memory")
async def memory_info():
    memory = psutil.virtual_memory()
    return {
        "total_mb": round(memory.total / 1024 / 1024, 2),
        "available_mb": round(memory.available / 1024 / 1024, 2),
        "used_mb": round(memory.used / 1024 / 1024, 2),
        "percent": memory.percent
    }

@app.get("/env")
async def environment():
    safe_vars = {k: v for k, v in os.environ.items()
                 if not any(secret in k.lower() for secret in ['password', 'secret', 'key', 'token'])}
    return {
        "environment_variables": safe_vars,
        "count": len(safe_vars)
    }

@app.get("/echo")
async def echo_get(request: Request):
    return {
        "method": "GET",
        "args": dict(request.query_params),
        "headers": dict(request.headers),
        "client_host": request.client.host if request.client else None
    }

@app.post("/echo")
async def echo_post(request: Request):
    try:
        body = await request.json()
    except:
        body = {}

    return {
        "method": "POST",
        "data": body,
        "headers": dict(request.headers),
        "client_host": request.client.host if request.client else None
    }

@app.get("/slow")
async def slow(delay: int = 2):
    if delay > 30:
        raise HTTPException(status_code=400, detail="Delay cannot exceed 30 seconds")
    await asyncio.sleep(delay)
    return {"message": f"Delayed for {delay} seconds", "timestamp": datetime.utcnow().isoformat()}

@app.get("/error")
async def trigger_error(code: int = 500):
    if code < 400 or code > 599:
        raise HTTPException(status_code=400, detail="Error code must be between 400 and 599")
    raise HTTPException(status_code=code, detail=f"Simulated error with code {code}")

@app.get("/status/{status_code}")
async def return_status(status_code: int):
    if status_code < 100 or status_code > 599:
        raise HTTPException(status_code=400, detail="Status code must be between 100 and 599")
    return Response(
        content=f'{{"status_code": {status_code}, "message": "Custom status code"}}',
        status_code=status_code,
        media_type="application/json"
    )

@app.get("/load")
async def simulate_load(iterations: int = 1000000):
    if iterations > 100000000:
        raise HTTPException(status_code=400, detail="Iterations cannot exceed 100 million")

    start = time.time()
    result = 0
    for i in range(iterations):
        result += i * random.random()

    duration = time.time() - start
    return {
        "iterations": iterations,
        "duration_seconds": round(duration, 4),
        "result": round(result, 2)
    }

@app.post("/data")
async def create_data(item: Item):
    return {
        "message": "Data received",
        "item": item.dict(),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/random")
async def random_response():
    responses = [
        {"status": "success", "value": random.randint(1, 100)},
        {"status": "success", "value": random.choice(["alpha", "beta", "gamma"])},
        {"status": "success", "value": round(random.random(), 4)}
    ]
    return random.choice(responses)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
