import os
import time
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException
from prometheus_client import start_http_server, Counter, Histogram
import psycopg2
import redis

app = FastAPI()

# --- Config ---
POSTGRES_URL = os.environ.get("POSTGRES_URL")
ORACLE_PRIVKEY_PATH = os.environ.get("ORACLE_PRIVKEY_PATH")
RPS = int(os.environ.get("RPS", 10))
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")

# --- Metrics ---
REPORT_MATCH_REQUESTS = Counter("report_match_requests_total", "Total reportMatch requests")
REPORT_MATCH_SUCCESS = Counter("report_match_success_total", "Total successful reportMatches")
REPORT_MATCH_FAILURE = Counter("report_match_failure_total", "Total failed reportMatches")
DB_INSERT_SECONDS = Histogram("db_insert_seconds", "Time spent inserting to DB")

# --- Connections ---
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0)

def get_db_connection():
    return psycopg2.connect(POSTGRES_URL)

# --- Rate Limiting (Token Bucket) ---
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path == "/reportMatch":
        token_bucket = f"token_bucket:{request.client.host}"
        if not redis_client.exists(token_bucket):
            redis_client.set(token_bucket, RPS, ex=1)

        if int(redis_client.get(token_bucket)) > 0:
            redis_client.decr(token_bucket)
        else:
            raise HTTPException(status_code=429, detail="Too Many Requests")

    response = await call_next(request)
    return response

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/reportMatch")
async def report_match(request: Request):
    REPORT_MATCH_REQUESTS.inc()
    body = await request.body()

    # --- HMAC Signature ---
    try:
        with open(ORACLE_PRIVKEY_PATH, 'rb') as f:
            priv_key = f.read()
        signature = hmac.new(priv_key, body, hashlib.sha256).hexdigest()
    except Exception:
        REPORT_MATCH_FAILURE.inc()
        raise HTTPException(status_code=500, detail="Could not generate signature")

    # --- DB Insert ---
    start_time = time.time()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # This is a simplified example. In a real app, you'd parse the body.
        cur.execute(
            "INSERT INTO detection_runs (watermark_hash, is_false_positive) VALUES (%s, %s) RETURNING id",
            (hashlib.sha256(body).hexdigest(), False)
        )
        run_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        REPORT_MATCH_SUCCESS.inc()
    except Exception as e:
        REPORT_MATCH_FAILURE.inc()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        duration = time.time() - start_time
        DB_INSERT_SECONDS.observe(duration)

    response_body = {"run_id": run_id, "status": "received"}
    
    # Add signature to response headers
    headers = {"X-Signature": signature}

    return response_body

if __name__ == "__main__":
    # In a real app, you might run the metrics server in a separate thread
    # For this example, we assume it's handled by the container orchestration
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
