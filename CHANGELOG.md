# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive `README.md` with project overview, features, setup instructions, and configuration details.
- Favicon support (`favicon.ico`) for the web application.
- Orchestrator UI Self-Monitoring: Automatically registers the backend as a monitored app, allowing users to track its CPU/RAM footprint and stream its internal `uvicorn` logs natively in the dashboard.
- `Start Hidden.vbs` utility script to launch the orchestrator completely in the background without maintaining an open command window.
- Global and per-app GPU Utilization (%) monitoring via `pynvml` (per-app VRAM is hidden due to Windows WDDM driver architecture).
- Overhauled UX designs for all views:
  - **Grid View**: Implemented robust fixed-width sizing and optimized single-line CMD previews to prevent layout shifting.
  - **List View**: Added responsive table design, prioritizing Name and Actions on mobile devices.
  - **Compact View**: Re-engineered to a flex wrap layout with fixed-width minimalist tiles.

### Fixed
- Fixed an annoying UI bug where inline expanded consoles would violently snap to the top of the log when the dashboard's asynchronous refresh cycle triggered. Log scroll positions are now perfectly persisted.

## [0.1.0] - Initial Release

### Added
- Initial web-based process manager and orchestrator.
- FastAPI backend (`main.py`) for application management and real-time log tailing via WebSockets.
- Ability to start and stop configured applications asynchronously.
- Live resource monitoring (CPU, RAM, GPU/VRAM) using `psutil` and `pynvml`.
- Configuration system via `config.json` supporting custom commands, environments, and grouped applications.
- Web UI (static files) to view active consoles and application statuses.
- State persistence (`state.json`) to reconnect to active processes after orchestrator restarts.
- Concept document (`Concept.txt`) outlining future planned features and UI enhancements.
