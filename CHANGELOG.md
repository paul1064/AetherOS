# Changelog

All notable changes to AetherOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial public release preparation
- GitHub community files (CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md)
- Enhanced documentation structure

### Changed
- Improved .gitignore with comprehensive patterns
- Updated README.md with professional formatting

## [0.13.0] - 2026-04-06

### Added
- **Core System**
  - Multi-agent orchestration framework
  - Self-healing supervisor daemon
  - Resource monitoring and management
  - Vector-based memory system with ChromaDB
  - Entity and episode memory curation
  
- **Meta-Agents**
  - Observer agent for system monitoring
  - Reflector agent for pattern analysis
  - Architect agent for system optimization
  - Guardian agent for safety enforcement
  
- **Desktop Integration**
  - Hyprland Wayland compositor support
  - Screenshot capture capabilities
  - Speech-to-text input (whisper.cpp)
  - Desktop session management
  
- **API & Interface**
  - FastAPI REST API server
  - Unified CLI (`bin/aether`)
  - TUI operator console
  - Status reporting tools
  
- **Governance**
  - Policy enforcement engine
  - Access control profiles
  - Audit logging
  - Compliance checking

- **Installation**
  - Automated bootstrap scripts
  - Btrfs snapshot management
  - Disk layout configuration
  - Live installer seeding

- **Documentation**
  - Comprehensive README.md
  - Architecture documentation
  - Deployment checklist
  - Operations runbook
  - Project index

### Changed
- Improved error handling across all agents
- Enhanced memory query performance
- Streamlined service startup sequence
- Better logging output formatting

### Fixed
- Python indentation errors in core module
- Undefined variable references in API app
- Import order violations (PEP8 E402)
- Missing blank lines between functions (PEP8 E302)
- Unused import cleanup

### Technical Details
- **Python**: 3.10+
- **Key Dependencies**:
  - FastAPI 0.116.1
  - Uvicorn 0.35.0
  - Pydantic 2.11.7
  - ChromaDB 1.0.20
  - PyYAML 6.0.2
  - Requests 2.32.4

## [0.12.0] - Previous Release

*Note: Earlier versions were part of internal development.*

---

## Version Numbering

AetherOS uses semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes or architectural shifts
- **MINOR**: New features, backward-compatible
- **PATCH**: Bug fixes and minor improvements

## Release Schedule

- **Patch releases**: As needed for critical fixes
- **Minor releases**: Monthly feature updates
- **Major releases**: Quarterly architectural updates

## Getting Previous Versions

Previous versions can be accessed via Git tags:
```bash
git tag -l  # List all version tags
git checkout v0.13.0  # Checkout specific version
```

---

**Note**: This changelog is maintained manually. For detailed commit history, see the Git repository.
