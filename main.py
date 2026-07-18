import asyncio
import json
import os
import platform
import subprocess
import sys
from collections import deque
from contextlib import asynccontextmanager

import psutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

try:
    import pynvml
    pynvml.nvmlInit()
    HAS_GPU = True
except (ImportError, Exception):
    HAS_GPU = False

# Application State
# Format: { app_id: {"pid": int, "logs": deque, "clients": set(), "log_task": asyncio.Task} }
active_processes = {}

# Format: { app_id: {"cpu": float, "ram_mb": float, "vram_mb": float} }
process_metrics = {}

CONFIG_FILE = "config.json"
STATE_FILE = "state.json"
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

class LoggerWriter:
    def __init__(self, log_file, orig_stream):
        self.log_file = log_file
        self.orig_stream = orig_stream

    def write(self, message):
        self.orig_stream.write(message)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(message)
        except Exception:
            pass

    def flush(self):
        self.orig_stream.flush()

sys.stdout = LoggerWriter(os.path.join(LOGS_DIR, "orchestrator-ui-self.log"), sys.stdout)
sys.stderr = LoggerWriter(os.path.join(LOGS_DIR, "orchestrator-ui-self.log"), sys.stderr)

import logging
file_handler = logging.FileHandler(os.path.join(LOGS_DIR, "orchestrator-ui-self.log"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
for logger_name in ("uvicorn.error", "uvicorn.access"):
    logging.getLogger(logger_name).addHandler(file_handler)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state_data):
    with open(STATE_FILE, "w") as f:
        json.dump(state_data, f, indent=2)

def load_config():
    apps = []
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                apps = json.load(f)
        except Exception:
            pass
            
    if not any(a["id"] == "orchestrator-ui-self" for a in apps):
        apps.insert(0, {
            "id": "orchestrator-ui-self",
            "name": "Orchestrator UI",
            "cmd": "uvicorn main:app --host 0.0.0.0 --port 8000",
            "cwd": ".",
            "app_type": "Server",
            "group": "System",
            "icon_path": "",
            "local_url": "http://localhost:8000"
        })
        save_config(apps)
    return apps

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=2)

class AppConfig(BaseModel):
    id: str
    name: str
    cmd: str
    cwd: str
    port: Optional[int] = None
    group: Optional[str] = None
    app_type: Optional[str] = None
    local_url: Optional[str] = None
    remote_url: Optional[str] = None
    start_with_group: bool = True
    launch_external: bool = False
    description: Optional[str] = None
    icon_path: Optional[str] = None
    env: Dict[str, str] = {}

async def poll_process_metrics():
    while True:
        gpu_procs = {}
        if HAS_GPU:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                compute = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
                graphics = pynvml.nvmlDeviceGetGraphicsRunningProcesses(handle)
                for p in compute + graphics:
                    vram = (p.usedGpuMemory / (1024 * 1024)) if p.usedGpuMemory is not None else 0.0
                    gpu_procs[p.pid] = {"vram_mb": vram, "gpu_util": 0.0}
                    
                samples = pynvml.nvmlDeviceGetProcessUtilization(handle, 0)
                if samples:
                    for s in samples:
                        if s.pid in gpu_procs:
                            gpu_procs[s.pid]["gpu_util"] = float(s.smUtil)
                        else:
                            gpu_procs[s.pid] = {"vram_mb": 0.0, "gpu_util": float(s.smUtil)}
            except Exception:
                pass

        for app_id, state in list(active_processes.items()):
            pid = state.get("pid")
            if pid:
                try:
                    parent = psutil.Process(pid)
                    if app_id == "orchestrator-ui-self":
                        procs = [parent]
                    else:
                        procs = [parent] + parent.children(recursive=True)
                    
                    total_cpu = 0.0
                    total_ram_mb = 0.0
                    total_vram_mb = 0.0
                    total_gpu_util = 0.0
                    
                    for p in procs:
                        try:
                            # Note: interval=None on cpu_percent calculates % since last call.
                            # Calling it periodically in this loop works well.
                            total_cpu += p.cpu_percent(interval=None)
                            total_ram_mb += p.memory_info().rss / (1024 * 1024)
                            if p.pid in gpu_procs:
                                total_vram_mb += gpu_procs[p.pid]["vram_mb"]
                                total_gpu_util += gpu_procs[p.pid]["gpu_util"]
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                            
                    process_metrics[app_id] = {
                        "cpu": round(total_cpu, 1),
                        "ram_mb": round(total_ram_mb, 1),
                        "vram_mb": round(total_vram_mb, 1) if HAS_GPU else 0,
                        "gpu_util": round(total_gpu_util, 1) if HAS_GPU else 0
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        await asyncio.sleep(2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: Check state.json, populate active_processes if PIDs are alive
    saved_state = load_state()
    active_pids = {}
    
    # Inject self app
    active_processes["orchestrator-ui-self"] = {
        "pid": os.getpid(),
        "logs": deque(maxlen=500),
        "clients": set(),
        "log_task": asyncio.create_task(tail_log_file("orchestrator-ui-self"))
    }
    active_pids["orchestrator-ui-self"] = os.getpid()
    
    for app_id, pid in saved_state.items():
        if app_id == "orchestrator-ui-self":
            continue
        try:
            # Check if PID is alive
            proc = psutil.Process(pid)
            active_pids[app_id] = pid
            
            # Reconstruct active_processes
            active_processes[app_id] = {
                "pid": pid,
                "logs": deque(maxlen=500),
                "clients": set(),
                "log_task": asyncio.create_task(tail_log_file(app_id))
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    # Update state file to clear out dead PIDs
    save_state(active_pids)
    
    metrics_task = asyncio.create_task(poll_process_metrics())
    
    yield
    
    metrics_task.cancel()
    
    # Shutdown logic: Do NOT kill processes anymore, just cancel log tailing tasks
    for app_id, state in active_processes.items():
        if "log_task" in state:
            state["log_task"].cancel()

app = FastAPI(lifespan=lifespan)

# Ensure static folder exists for mounting
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


async def tail_log_file(app_id: str):
    """Tails the physical log file continuously and broadcasts chunks."""
    state = active_processes.get(app_id)
    if not state:
        return
        
    log_file = os.path.join(LOGS_DIR, f"{app_id}.log")
    while not os.path.exists(log_file):
        await asyncio.sleep(0.5)
        
    buffer = ""
    with open(log_file, "r", encoding="utf-8", errors="replace") as f:
        while True:
            chunk = f.read(4096)
            if chunk:
                # Broadcast immediately
                disconnected = set()
                for client in state["clients"]:
                    try:
                        await client.send_text(chunk)
                    except Exception:
                        disconnected.add(client)
                        
                for client in disconnected:
                    state["clients"].remove(client)
                    
                # Manage history
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    state["logs"].append(line + "\n")
            else:
                await asyncio.sleep(0.1)

@app.get("/api/apps")
async def get_apps():
    """Returns the list of configured apps, their current statuses, PID, and mapped port."""
    config = load_config()
    results = []
    for app_cfg in config:
        app_id = app_cfg["id"]
        is_running = False
        pid = None
        
        if app_id in active_processes:
            pid = active_processes[app_id]["pid"]
            try:
                proc = psutil.Process(pid)
                if proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
                    is_running = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process died, cleanup
                del active_processes[app_id]
                pid = None
        
        results.append({
            **app_cfg,
            "running": is_running,
            "pid": pid,
            "metrics": process_metrics.get(app_id) if is_running else None
        })
    return results

@app.get("/api/apps/{app_id}/icon")
async def get_app_icon(app_id: str):
    config = load_config()
    app_cfg = next((a for a in config if a["id"] == app_id), None)
    if not app_cfg or not app_cfg.get("icon_path"):
        raise HTTPException(status_code=404, detail="Icon not found")
        
    icon_path = app_cfg["icon_path"]
    if icon_path.startswith("http://") or icon_path.startswith("https://"):
        return RedirectResponse(url=icon_path)
        
    if not os.path.exists(icon_path):
        raise HTTPException(status_code=404, detail="Icon file does not exist on server")
        
    return FileResponse(icon_path)

@app.post("/api/apps/{app_id}/start")
async def start_app(app_id: str):
    """Spins up the process asynchronously, capturing stdout/stderr."""
    if app_id in active_processes:
        pid = active_processes[app_id].get("pid")
        if pid:
            try:
                if psutil.Process(pid).is_running():
                    raise HTTPException(status_code=400, detail="App is already running")
            except Exception:
                pass
        
    config = load_config()
    app_cfg = next((a for a in config if a["id"] == app_id), None)
    if not app_cfg:
        raise HTTPException(status_code=404, detail="App not found in config")
        
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["FORCE_COLOR"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    if app_cfg.get("env"):
        env.update(app_cfg["env"])
        
    # Ensure cwd exists, fallback to current dir
    cwd = app_cfg.get("cwd", ".")
    if not os.path.exists(cwd):
        os.makedirs(cwd, exist_ok=True)

    try:
        log_file = os.path.join(LOGS_DIR, f"{app_id}.log")
        # Overwrite the log file for this new run
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"--- Starting {app_cfg['name']} ---\n")
            
        f = open(log_file, "a", encoding="utf-8")
        
        creationflags = 0
        is_external = app_cfg.get("launch_external", False)
        
        if platform.system() == "Windows":
            if is_external:
                creationflags = subprocess.CREATE_NEW_CONSOLE
            else:
                # 0x08000000 is CREATE_NO_WINDOW
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | 0x08000000
                
        proc_kwargs = {
            "cwd": cwd,
            "env": env,
            "shell": True,
            "creationflags": creationflags
        }
        
        if not is_external:
            proc_kwargs["stdout"] = f
            proc_kwargs["stderr"] = subprocess.STDOUT
            
        cmd_str = app_cfg["cmd"]
        if platform.system() == "Windows" and is_external:
            app_name = app_cfg.get("name", "External App")
            cmd_str = f'start "{app_name}" cmd.exe /k "{cmd_str}"'
            
        # Spawn completely detached process
        proc = subprocess.Popen(cmd_str, **proc_kwargs)
        
        if is_external:
            f.close()
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write("[Launched in External Console Window]\n")
        
        active_processes[app_id] = {
            "pid": proc.pid,
            "logs": deque(maxlen=500),
            "clients": set(),
            "log_task": asyncio.create_task(tail_log_file(app_id))
        }
        
        # Save state
        saved_state = load_state()
        saved_state[app_id] = proc.pid
        save_state(saved_state)
        
        return {"status": "started", "pid": proc.pid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start app: {str(e)}")


async def stop_app(app_id: str):
    """Core logic to cleanly kill a process based on the OS platform."""
    if app_id not in active_processes:
        return
        
    pid = active_processes[app_id]["pid"]
    if pid is not None:
        try:
            p = psutil.Process(pid)
            if p.is_running():
                if platform.system() == "Windows":
                    if app_id == "orchestrator-ui-self":
                        # Do not tree kill self to avoid killing managed background apps
                        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
                    else:
                        # Taskkill ensures all child processes spawned by .bat are terminated
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
                else:
                    p.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    if "log_task" in active_processes[app_id]:
        active_processes[app_id]["log_task"].cancel()
                
    # Close web sockets gracefully
    clients = active_processes[app_id]["clients"].copy()
    for client in clients:
        try:
            await client.close()
        except:
            pass
            
    del active_processes[app_id]
    
    # Save state
    saved_state = load_state()
    if app_id in saved_state:
        del saved_state[app_id]
        save_state(saved_state)


@app.post("/api/apps/{app_id}/stop")
async def api_stop_app(app_id: str):
    """API endpoint to stop a process."""
    await stop_app(app_id)
    return {"status": "stopped"}


@app.post("/api/apps")
async def create_app(app_data: AppConfig):
    config = load_config()
    if any(a["id"] == app_data.id for a in config):
        raise HTTPException(status_code=400, detail="App with this ID already exists")
        
    config.append(app_data.dict())
    save_config(config)
    return {"status": "created", "app": app_data.dict()}

@app.put("/api/apps/{app_id}")
async def update_app(app_id: str, app_data: AppConfig):
    config = load_config()
    idx = next((i for i, a in enumerate(config) if a["id"] == app_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="App not found")
        
    # We no longer stop the app on config save. Changes take effect on next start.
        
    config[idx] = app_data.dict()
    save_config(config)
    return {"status": "updated", "app": app_data.dict()}

@app.delete("/api/apps/{app_id}")
async def delete_app(app_id: str):
    config = load_config()
    new_config = [a for a in config if a["id"] != app_id]
    
    if len(config) == len(new_config):
        raise HTTPException(status_code=404, detail="App not found")
        
    # Stop app if running
    await stop_app(app_id)
        
    save_config(new_config)
    return {"status": "deleted"}


@app.get("/api/system-metrics")
async def get_metrics():
    """Return JSON containing overall CPU, RAM, and optional GPU metrics."""
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    
    metrics = {
        "cpu": cpu,
        "ram": ram,
        "gpu_present": HAS_GPU
    }
    
    if HAS_GPU:
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            metrics["gpu_usage"] = util.gpu
            metrics["vram_usage_mb"] = mem.used / (1024 * 1024)
            metrics["vram_total_mb"] = mem.total / (1024 * 1024)
            metrics["vram_usage_percent"] = (mem.used / mem.total) * 100
        except Exception:
            metrics["gpu_present"] = False
            
    return metrics


@app.websocket("/ws/logs/{app_id}")
async def websocket_logs(websocket: WebSocket, app_id: str):
    """Accept client WebSocket connections to stream logs."""
    await websocket.accept()
    
    if app_id not in active_processes:
        await websocket.send_text("No active process found for this app ID.\n")
        await websocket.close()
        return
        
    state = active_processes[app_id]
    
    # Dump the existing log buffer immediately upon connection
    for line in state["logs"]:
        await websocket.send_text(line)
        
    state["clients"].add(websocket)
    try:
        # Keep connection open and wait for incoming messages (client disconnect)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in state["clients"]:
            state["clients"].remove(websocket)
