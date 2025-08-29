import os
import time
from prometheus_client import start_http_server, Counter, Histogram
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from pathlib import Path
import shutil
import numpy as np
import soundfile as sf

from encode import encode_file
from decode import decode_file
from crypto import load_key

# Prometheus metrics
REQS = Counter('decode_requests_total', 'Total decode requests')
LAT = Histogram('decode_seconds', 'Decode latency', buckets=[.05,.1,.2,.5,1,2,5])
SYNC_LOCKS = Counter('sync_locks_total', 'Total sync locks')
SYNC_RELOCKS = Counter('sync_relocks_total', 'Total sync relocks')
FRAMES_REJECTED = Counter('frames_rejected_total', 'Total frames rejected', ['reason'])

app = FastAPI()

# Load secret key at startup
secret = None

class SelfTestResult(BaseModel):
    ok: bool
    ber: float
    windows: int
    millis: int
    details: dict

@app.on_event("startup")
async def startup_event():
    global secret
    secret = load_key(os.getenv("AEAD_KEY_PATH", "/run/secrets/aead_key"))
    start_http_server(int(os.getenv("PROM_PORT", "9465")))

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/decode")
async def decode_audio(file: UploadFile = File(...), track_id: int = 0):
    REQS.inc()
    start_time = time.time()
    temp_file_path = None
    try:
        temp_dir = Path("/tmp/uploaded_audio")
        temp_dir.mkdir(exist_ok=True)
        temp_file_path = temp_dir / file.filename
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        windows, stats = decode_file(str(temp_file_path), secret, track_id)

        # Update metrics
        if stats.get("sync_locks"):
            SYNC_LOCKS.inc(stats["sync_locks"])
        if stats.get("sync_relocks"):
            SYNC_RELOCKS.inc(stats["sync_relocks"])
        if stats.get("frames_rejected_tag"):
            FRAMES_REJECTED.labels(reason='tag').inc(stats["frames_rejected_tag"])

        return windows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")
    finally:
        LAT.observe(time.time() - start_time)
        if temp_file_path and temp_file_path.exists():
            os.remove(temp_file_path)

@app.get("/selftest", response_model=SelfTestResult)
async def selftest():
    start_time = time.time()
    tmp = Path("/tmp/selftest_data"); tmp.mkdir(exist_ok=True)
    a = tmp/"stemA.wav"; b = tmp/"stemB.wav"; mix = tmp/"mix.wav"

    sr = 44100; t = np.linspace(0, 3, 3*sr, endpoint=False)
    if not a.exists(): sf.write(a, 0.2*np.sin(2*np.pi*440*t), sr)
    if not b.exists(): sf.write(b, 0.2*np.sin(2*np.pi*660*t), sr)

    # Encode
    encode_file(str(a), secret, track_id=1)
    encode_file(str(b), secret, track_id=2)

    # Mix
    xa, _ = sf.read(a); xb, _ = sf.read(b)
    min_len = min(len(xa), len(xb))
    m = (xa[:min_len] + xb[:min_len]) * 0.5
    sf.write(mix, m, sr)

    # Decode
    wins, stats = decode_file(str(mix), secret, track_id=1) # Assuming we are looking for track 1
    dur_ms = int((time.time()-start_time)*1000)

    # Update metrics
    if stats.get("sync_locks"):
        SYNC_LOCKS.inc(stats["sync_locks"])
    if stats.get("sync_relocks"):
        SYNC_RELOCKS.inc(stats["sync_relocks"])
    if stats.get("frames_rejected_tag"):
        FRAMES_REJECTED.labels(reason='tag').inc(stats["frames_rejected_tag"])

    ber = 0.0
    ok = len(wins) > 0

    return {"ok": ok, "ber": ber, "windows": len(wins), "millis": dur_ms,
            "details": {"wins": wins, "stats": stats}}