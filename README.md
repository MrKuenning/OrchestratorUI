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

List View
<img width="1518" height="806" alt="2026-07-19 10_30_11-Command Palette" src="https://github.com/user-attachments/assets/44705f45-895c-40a5-8cf3-f92da617bd54" />
Quickly start and top your scripts and UIs.
See them grouped by app or by status.
See the resouces consumed per app.

Console View
<img width="1518" height="806" alt="2026-07-19 10_31_49-OpenVPN Connect" src="https://github.com/user-attachments/assets/be0ddc1d-dc58-4a69-b394-e16037e87de7" />
There are several ways to view the console outputs, one of them is the console screen where you can pin apps and view their output.

Compact View
<img width="546" height="660" alt="2026-07-19 10_43_06-OpenVPN Connect" src="https://github.com/user-attachments/assets/1ab0ad33-a242-463a-a78e-d4b929573e95" />
Clean compact view has mobile responsive design.

Image of the Grid Card
<img width="413" height="316" alt="2026-07-19 10_33_57-PowerToys Quick Access (Preview)" src="https://github.com/user-attachments/assets/7280fc79-434d-476c-8fad-4d983e7bf1d4" />
Grid view gives puts everything at your fingertips.

Image of the Config Screen
<img width="791" height="881" alt="2026-07-19 10_35_08-OpenVPN Connect" src="https://github.com/user-attachments/assets/8c31f5cc-efb0-4c84-9346-2eb95a436222" />
Easy to configure apps via GUI or JSON




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
   You can run the orchestrator manually or completely in the background:
   - **Standard Mode**: Double-click `start.bat` (this leaves a CMD window open).
   - **Hidden Mode (Recommended)**: Double-click `Start Hidden.vbs`. This executes the orchestrator entirely in the background with no persistent window.

   This script will automatically install required dependencies (`fastapi`, `uvicorn`, `websockets`, `psutil`, `pynvml`) and launch the FastAPI server.

3. **Access the Dashboard:**
   Open your web browser and navigate to:
   [http://localhost:8000/static/index.html](http://localhost:8000/static/index.html)
   
   *Note: OrchestratorUI tracks its own resource usage natively! You will see an "Orchestrator UI" app at the top of your dashboard where you can monitor its live CPU/RAM footprint and stream its backend logs.*

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
