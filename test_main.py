from main import request_history, max_allowed_requests, time_window_seconds
from datetime import datetime, timedelta
import time


def check_rate_limit_direct(key, max_req, window):
    now = datetime.utcnow()
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

    if len(request_history[key]) < max_req:
        request_history[key].append(now)
        return True, max_req - len(request_history[key]), reset_time
    else:
        return False, 0, reset_time


def test_allow_first_request():
    key = "t1:c1:login"
    allowed, remaining, _ = check_rate_limit_direct(key, 2, 3)
    assert allowed is True
    assert remaining == 1

def test_allow_second_request():
    key = "t1:c1:login"
    allowed, remaining, _ = check_rate_limit_direct(key, 2, 3)
    assert allowed is True
    assert remaining == 0

def test_third_blocked():
    key = "t1:c1:login"
    allowed, remaining, _ = check_rate_limit_direct(key, 2, 3)
    assert allowed is False
    assert remaining == 0

def test_after_wait():
    key = "t1:c1:login"
    time.sleep(3)
    allowed, remaining, _ = check_rate_limit_direct(key, 2, 3)
    assert allowed is True
