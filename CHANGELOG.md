# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.6]

### Added
- Enhanced Grid View layout logic to use dynamic flex-wrap instead of rigid rows. This significantly improves screen utilization by allowing multiple narrow groups to seamlessly float next to each other on a single line.
- Repositioned the "Group By" dropdown out of the global top navigation bar to create localized toolbars at the top of the Grid and List views. These dropdowns remain perfectly synchronized across views.
- Refined Grid card heights so that started apps and stopped apps share identical vertical heights natively, ensuring the layout remains cleanly aligned.
- Refactored Grid card styling to apply `mt-auto` to the CMD box. This anchors the CMD field to the absolute bottom of the card content area so it never shifts or bounces vertically when app metadata sizes differ.
- Restored the application metrics to their own dedicated line directly beneath the app status. This ensures that valuable metrics (especially GPU utilization) are never truncated on narrower windows.

### Fixed
- Resolved a DOM structure bug introduced in a recent update that mistakenly nested the Compact and Consoles views inside the List view container, rendering those tabs invisible.

## [1.0.5]
### Added
- Comprehensive `README.md` with project overview, features, setup instructions, and configuration details.
- Favicon support (`favicon.ico`) for the web application.
- Orchestrator UI Self-Monitoring: Automatically registers the backend as a monitored app, allowing users to track its CPU/RAM footprint and stream its internal `uvicorn` logs natively in the dashboard.
- `Start Hidden.vbs` utility script to launch the orchestrator completely in the background without maintaining an open command window.
- Global and per-app GPU Utilization (%) monitoring via `pynvml` (per-app VRAM is hidden due to Windows WDDM driver architecture).
- Overhauled UX designs for all views:
  - **Grid View**: Implemented robust fixed-width sizing and optimized single-line CMD previews to prevent layout shifting.
  - **List View**: Added responsive table design, prioritizing Name and Actions on mobile devices.
  - **Compact View**: 
    - Re-engineered to a flex wrap layout with fixed-width minimalist tiles.
    - Added a "Hide Inactive" toggle switch to view either only active processes or all configured apps.
    - When inactive apps are shown, they are automatically grouped into "Active Processes" and "Inactive Processes" sections with distinct styling.
  - **Header & Mobile Experience**:
    - The title text gracefully hides on narrow screens, preserving space.
    - Added a touch-friendly hamburger dropdown menu that cleanly collapses the View Tabs, Group By dropdown, and Add App button on mobile devices.
    - Removed redundant title headings for a cleaner, unified toolbar layout.
    - Added a `v1.0.5` version badge to the navbar.

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
