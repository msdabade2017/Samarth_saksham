# Design: Load Balancing Rate Limiter

## Purpose
A simple in-memory rate limiter and load balancer for API requests using FastAPI. It limits requests per client/action, prevents overload, and queues extra requests per tenant.

## How It Works
- Uses FastAPI for the API.
- Tracks request history and queues in memory (dicts, lists, deque).

### Main Data Structures
- `request_history`: Maps (tenant, client, action) to timestamps
- `current_load`: Number of active requests
- `tenant_queues`: Per-tenant queue for waiting requests
- `max_allowed_requests`, `time_window_seconds`: Per-key rate limit configs

## Request Handling
- **/check_and_consume**: Checks and consumes a slot, queues if overloaded
- **/status/...**: Shows usage and queue for a key

## Notes
- All state is in memory (lost on restart)
- Each tenant has its own queue
- No auto-processing for queued requests

## Limitations
- Not distributed (single server only)
- No persistence (could add Redis/DB)
- No authentication or input validation

##Testing
- Unit testing (test_main.py)
 
