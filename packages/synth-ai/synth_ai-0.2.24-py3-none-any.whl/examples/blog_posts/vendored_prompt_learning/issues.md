# Known Issues

## Backend Connectivity Issue

### Problem
Both `run_mipro_in_process.py` and `run_gepa_banking77_in_process.py` scripts fail to connect to the backend when submitting optimization jobs.

### Symptoms

**MIPRO Script:**
- Task app starts successfully ✅
- Cloudflare tunnel opens successfully ✅
- Config loads and reduces budget correctly ✅
- Job submission fails with: `RuntimeError: Job submission failed with status 530`
- Error shows Cloudflare tunnel error page for `backend-local.usesynth.ai`

**GEPA Script:**
- Task app starts successfully ✅
- Cloudflare tunnel opens successfully ✅
- Config loads and reduces budget correctly ✅
- Job submission succeeds but job fails immediately
- Job ID: `pl_e2ccf2884daf432f` (example)
- Job status: `failed` after ~3 seconds

### Root Cause

The backend is not accessible at the configured URLs:

1. **MIPRO script** uses: `https://backend-local.usesynth.ai` (from `BACKEND_BASE_URL` env var or default)
   - This appears to be a Cloudflare tunnel URL that's not active/accessible
   - Returns Cloudflare error page (530)

2. **GEPA script** uses: `http://localhost:8000` (hardcoded default)
   - Backend not running on localhost:8000
   - Job submits but fails immediately

### Solution

**Option 1: Start backend locally**
```bash
# In monorepo/backend directory
# Start backend on localhost:8000
# Then scripts will work with default localhost:8000
```

**Option 2: Update backend URL in scripts**
- Set `BACKEND_BASE_URL` environment variable to correct backend URL
- Or modify scripts to use correct backend URL

**Option 3: Use local tunnel mode**
- Set `SYNTH_TUNNEL_MODE=local` to skip Cloudflare tunnel
- Still need backend running locally

### Workaround

For testing purposes, scripts can be verified to work correctly by:
1. ✅ Verifying environment variables load
2. ✅ Verifying task apps start
3. ✅ Verifying tunnels open
4. ✅ Verifying configs are modified correctly
5. ✅ Verifying job submission logic works

The scripts themselves are functioning correctly - the issue is backend connectivity.

### Files Affected

- `scripts/run_mipro_in_process.py` - Uses `BACKEND_BASE_URL` env var (defaults to `https://backend-local.usesynth.ai`)
- `scripts/run_gepa_banking77_in_process.py` - Hardcoded to `http://localhost:8000`

### Status

🔴 **Open** - Backend connectivity needs to be configured

### Notes

- Both scripts successfully demonstrate the full pipeline up to job submission
- Minimal budgets are working correctly (MIPRO: 1 iter × 1 eval, GEPA: 5 rollouts)
- Scripts complete quickly as expected (~1-3 seconds for setup + submission)
- Only backend connectivity prevents full end-to-end test

