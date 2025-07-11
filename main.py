from fastapi import FastAPI, Request
from datetime import datetime, timedelta
from collections import deque

app = FastAPI()


request_history = {}         
current_load = 5
max_allowed_load = 5         

tenant_queues = {}          
max_queue_size = 3          
max_allowed_requests = {}    
time_window_seconds = {}     

@app.post("/check_and_consume")
async def check_and_consume(request: Request):
    global current_load

    data = await request.json()
    tenant = data["tenant_id"]
    client = data["client_id"]
    action = data["action_type"]
    max_req = data["max_requests"]
    window = data["window_duration_seconds"]

    now = datetime.utcnow()
    key = f"{tenant}:{client}:{action}"

    
    if key not in request_history:
        request_history[key] = []
        max_allowed_requests[key] = max_req
        time_window_seconds[key] = window

   
    valid_time = now - timedelta(seconds=window)
    request_history[key] = [t for t in request_history[key] if t > valid_time]
    
    if request_history[key]:
        first_time = request_history[key][0]
        reset_time = int((first_time + timedelta(seconds=window)).timestamp())
    else:
        reset_time = int((now + timedelta(seconds=window)).timestamp())

    if current_load >= max_allowed_load:
        if tenant not in tenant_queues:
            tenant_queues[tenant] = deque()

        if len(tenant_queues[tenant]) >= max_queue_size:
            return {
                "allowed": False,
                "status": "rejected",
                "message": "Queue is full"
            }

        tenant_queues[tenant].append(data)
        return {
            "allowed": False,
            "status": "queued",
            "message": "Request queued"
        }

    
    current_load += 1

    if len(request_history[key]) < max_req:
        request_history[key].append(now)
        current_load -= 1
        return {
            "allowed": True,
            "status": "processed",
            "remaining_requests": max_req - len(request_history[key]),
            "reset_time_seconds": reset_time
        }
    else:
        current_load -= 1
        return {
            "allowed": False,
            "status": "processed",
            "remaining_requests": 0,
            "reset_time_seconds": reset_time
        }

@app.get("/status/{tenant_id}/{client_id}/{action_type}")
async def get_status(tenant_id: str, client_id: str, action_type: str):
    key = f"{tenant_id}:{client_id}:{action_type}"
    now = datetime.utcnow()

    
    logs = request_history.get(key, [])
    max_req = max_allowed_requests.get(key, 0)
    window = time_window_seconds.get(key, 0)

    valid_time = now - timedelta(seconds=window)
    active_logs = [t for t in logs if t > valid_time]

    
    queue_items = []
    if tenant_id in tenant_queues:
        for item in tenant_queues[tenant_id]:
            queue_items.append({
                "client_id": item["client_id"],
                "action_type": item["action_type"]
            })

    return {
        "tenant_id": tenant_id,
        "client_id": client_id,
        "action_type": action_type,
        "max_requests": max_req,
        "window_duration_seconds": window,
        "current_requests": len(active_logs),
        "timestamps": [t.isoformat() for t in active_logs],
        "queue_size": len(queue_items),
        "queue_status": queue_items
    }

