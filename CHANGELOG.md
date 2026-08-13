# Changelog



## [1.0.9] - 2026-08-13

### Added
- **Console Standard Input Support**: Added interactive text input fields to both the single console drawer and tiled multi-console views, allowing direct `stdin` interaction via WebSockets.
- **Dynamic Prompt Detection**: Automated regex detection on incoming log streams to recognize prompts (`[y/n]`, `[yes/no]`, `press any key...`) and render instant one-click action buttons.
- **Collapsible Console Sidebar**: Added a sidebar toggle button and a zero-height docked left-edge expand tab for the Consoles view (persisted in `localStorage`).
- **Dynamic Slim Console Scaling**: Reduced minimum console tile width from `600px` down to `300px`, enabling multiple pinned consoles to dynamically scale side-by-side without forcing wide horizontal scrollbars.
- **Clone Application Feature**: Added a "Clone App" action button to Grid View (and List View) that creates a duplicate configuration with automatically incremented trailing ID digits, unique app names, and safely incremented ports.
- **Centered Confirmation Modals**: Added styled, centered confirmation modals for stopping and deleting applications, prominently displaying the app's name before proceeding.
- **Automatic Config Backup**: Added automatic copying of `config.json` to `config.bkp` during backend startup (`lifespan` initialization).
- **UI Restart Guard**: Visually disables input fields with `"Disconnected (UI restarted)"` if a running process was launched prior to a backend server restart.

## [1.0.8] - 2026-08-10

### Added
- Enhanced multi-console dashboard layouts with improved WebSocket reconnect handling and tile management.

## [1.0.7] - 2026-07-17

### Fixed
- Fixed a bug where Orchestrator UI would double-count RAM usage by including the memory footprint of all its child applications in its own metric.
- Fixed an issue where stopping Orchestrator UI would forcefully kill all background applications it had launched (by removing the Tree Kill flag from its stop routine).

## [1.0.6] - 2026-07-16

### Added
- Enhanced Grid View layout logic to use dynamic flex-wrap instead of rigid rows. This significantly improves screen utilization by allowing multiple narrow groups to seamlessly float next to each other on a single line.
- Repositioned the "Group By" dropdown out of the global top navigation bar to create localized toolbars at the top of the Grid and List views. These dropdowns remain perfectly synchronized across views.
- Refined Grid card heights so that started apps and stopped apps share identical vertical heights natively, ensuring the layout remains cleanly aligned.
- Refactored Grid card styling to apply `mt-auto` to the CMD box. This anchors the CMD field to the absolute bottom of the card content area so it never shifts or bounces vertically when app metadata sizes differ.
- Restored the application metrics to their own dedicated line directly beneath the app status. This ensures that valuable metrics (especially GPU utilization) are never truncated on narrower windows.

### Fixed
- Resolved a DOM structure bug introduced in a recent update that mistakenly nested the Compact and Consoles views inside the List view container, rendering those tabs invisible.

## [1.0.5] - 2026-07-16
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

## [0.1.0] - 2026-07-16 - Initial Release

### Added
- Initial web-based process manager and orchestrator.
- FastAPI backend (`main.py`) for application management and real-time log tailing via WebSockets.
- Ability to start and stop configured applications asynchronously.
- Live resource monitoring (CPU, RAM, GPU/VRAM) using `psutil` and `pynvml`.
- Configuration system via `config.json` supporting custom commands, environments, and grouped applications.
- Web UI (static files) to view active consoles and application statuses.
- State persistence (`state.json`) to reconnect to active processes after orchestrator restarts.
- Concept document (`Concept.txt`) outlining future planned features and UI enhancements.
