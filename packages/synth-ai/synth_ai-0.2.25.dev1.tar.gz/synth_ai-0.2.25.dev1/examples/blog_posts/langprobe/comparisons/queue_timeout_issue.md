# Queue Timeout Issue Analysis

## Problem Summary

The experiment queue is crashing and getting clogged due to timeout errors when polling the backend API for job progress.

## Root Cause

1. **Backend `/events` endpoint is too slow**: The endpoint `/api/prompt-learning/online/jobs/{job_id}/events` is taking longer than 60 seconds to respond. This is likely because:
   - The endpoint calls `get_job_by_job_id()` which queries PostgREST (we just increased PostgREST timeout to 60s)
   - PostgREST queries to Supabase are slow under load
   - The entire request chain (backend → PostgREST → Supabase → response) exceeds 60 seconds

2. **Celery workers timeout**: The `_poll_backend_progress()` function uses `requests.get()` with `timeout=60`, which times out when the backend takes longer than 60 seconds.

3. **Error handling is too aggressive**: When timeouts occur:
   - The error is logged as `ERROR` level, which may cause Celery to mark tasks as failed
   - Multiple workers all timeout simultaneously (all polling different jobs)
   - The poller continues retrying every 5 seconds, creating a cascade of timeout errors
   - This clogs the queue with error logs and potentially causes workers to crash

4. **No exponential backoff**: On timeout, the poller immediately retries after 5 seconds, creating a thundering herd problem when the backend is overloaded.

## Evidence

From logs:
- Multiple `ReadTimeout` errors: `HTTPConnectionPool(host='localhost', port=8000): Read timed out. (read timeout=60)`
- All occurring around the same time (13:16:03-13:16:07)
- Multiple workers affected simultaneously (ForkPoolWorker-2, -3, -4, -5, -6)
- Errors logged as `ERROR` level, which may cause Celery task failures
- After timeout, workers retry immediately (line 841-848 show new polling attempts)

## Impact

- Queue gets clogged with error logs
- Workers may crash or be marked as failed
- Progress polling stops working, making it impossible to track job status
- User sees jobs stuck in "queued" status (as shown in terminal output)

## Solution Needed

1. **Increase timeout**: Increase the `requests.get()` timeout to 120 seconds or more to handle slow backend responses
2. **Better error handling**: 
   - Catch `ReadTimeout` specifically and log as WARNING instead of ERROR
   - Don't let timeouts crash the poller thread
   - Add exponential backoff on repeated timeouts
3. **Backend optimization**: The `/events` endpoint should be optimized to respond faster, or use a different mechanism (e.g., websockets, server-sent events)


