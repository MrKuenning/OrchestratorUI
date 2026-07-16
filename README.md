# OrchestratorUI

OrchestratorUI is a web-based process manager and orchestrator designed to run, monitor, and control various applications and scripts from a single unified dashboard.

## Features

- **Centralized Dashboard**: View and manage all your configured applications in one place.
- **Process Management**: Start and stop applications asynchronously.
- **Real-time Log Tailing**: View live console outputs via WebSockets directly in the browser.
- **Resource Monitoring**: Live monitoring of CPU, RAM, and GPU (VRAM) usage per application using `psutil` and `pynvml`.
- **Flexible Execution**: Launch apps in the background or in an external console window.
- **Custom Configuration**: Easily define apps with custom commands, working directories, environment variables, grouping, and more in `config.json`.
- **State Persistence**: Remembers running applications and reconnects to active processes if the orchestrator restarts.

## Prerequisites

- Python 3.8+
- Windows (recommended, though mostly cross-platform with minor adjustments)

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd "OrchestratorUI - App1"
   ```

2. **Run the startup script:**
   Simply double-click on `start.bat` or run it from the command line:
   ```bash
   start.bat
   ```
   This script will automatically install required dependencies (`fastapi`, `uvicorn`, `websockets`, `psutil`, `pynvml`) and launch the FastAPI server.

3. **Access the Dashboard:**
   Open your web browser and navigate to:
   [http://localhost:8000/static/index.html](http://localhost:8000/static/index.html)

## Configuration (`config.json`)

Applications are defined in `config.json`. Here is an example of the structure:

```json
[
  {
    "id": "app_1",
    "name": "My Python Script",
    "cmd": "python my_script.py",
    "cwd": "C:/path/to/script",
    "port": 8080,
    "group": "Backend",
    "app_type": "Script",
    "start_with_group": true,
    "launch_external": false,
    "description": "Runs the background data processor.",
    "icon_path": "static/icons/python.png",
    "env": {
      "MY_VAR": "value"
    }
  }
]
```

### Configuration Fields:
- `id`: Unique identifier for the app.
- `name`: Display name in the UI.
- `cmd`: The command to execute.
- `cwd`: The working directory to execute the command in.
- `port`: (Optional) Port the application runs on.
- `group`: (Optional) Group category for organizing apps.
- `app_type`: (Optional) The type of application (e.g., Script, Web server).
- `start_with_group`: (Boolean) Whether to start this app when the group starts.
- `launch_external`: (Boolean) If true, launches the app in a new, external console window. If false, captures output internally for the UI.
- `description`: (Optional) Short description of what the app does.
- `icon_path`: (Optional) Path or URL to an icon for the app.
- `env`: (Optional) Key-value pairs for environment variables.

## Future Plans (Concept)
- Advanced views (List, Grid with side-by-side consoles).
- Console color support.
- Combining and linking configurations.
- Advanced grouping and sorting features.