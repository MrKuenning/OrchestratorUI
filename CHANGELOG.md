# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive `README.md` with project overview, features, setup instructions, and configuration details.

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
