# Contributing to AetherOS

Thank you for your interest in contributing to AetherOS! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Collaborate openly and transparently
- Prioritize user safety and system reliability

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/aetheros.git
   cd aetheros
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/aetheros.git
   ```
4. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.10+
- Bash 5.0+
- Git
- Linux environment (recommended for full functionality)

### Installation

```bash
# Install dependencies
pip install -r requirements/core.txt

# Run local installation
./install.sh

# Verify setup
bin/aether verify
```

### Running Tests

```bash
# Run verification suite
bin/aether verify

# Check Python syntax
python -m py_compile lib/*.py agents/*.py

# Lint code (if flake8 available)
flake8 lib/ agents/ --max-line-length=100
```

## How to Contribute

### Reporting Bugs

1. Check existing issues first
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, AetherOS version)
   - Logs or error messages

### Suggesting Features

1. Open an issue with `[FEATURE]` prefix
2. Describe the use case and benefits
3. Wait for community discussion
4. Once approved, implement following the workflow below

### Improving Documentation

Documentation improvements are always welcome! This includes:
- README updates
- Code comments
- Tutorial additions
- Translation improvements

## Coding Standards

### Python Code

- Follow PEP 8 style guidelines
- Use type hints where possible
- Keep functions focused and under 50 lines when feasible
- Write docstrings for public functions and classes
- Maximum line length: 100 characters

Example:
```python
def process_query(query: str, context: Optional[Dict] = None) -> QueryResult:
    """Process a natural language query and return structured results.
    
    Args:
        query: The input query string
        context: Optional context dictionary for disambiguation
        
    Returns:
        QueryResult object with parsed intent and entities
    """
    # Implementation here
    pass
```

### Bash Scripts

- Use `set -euo pipefail` for safety
- Quote all variables: `"$var"`
- Use functions for reusability
- Include comments for complex logic
- Validate inputs early

Example:
```bash
#!/usr/bin/env bash
set -euo pipefail

# Validate required arguments
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <command> [options]" >&2
    exit 1
fi
```

### Commit Messages

Follow conventional commits format:
```
feat: add memory entity extraction
fix: resolve race condition in orchestrator
docs: update installation instructions
refactor: simplify agent communication protocol
test: add integration tests for governance module
chore: update dependencies to latest versions
```

## Testing

### Before Submitting

Ensure your changes:
- [ ] Pass all existing tests
- [ ] Include new tests for new functionality
- [ ] Don't introduce linting errors
- [ ] Update documentation if needed
- [ ] Work on clean installation

### Test Categories

1. **Unit Tests**: Individual function/module testing
2. **Integration Tests**: Component interaction testing
3. **Smoke Tests**: Basic functionality verification
4. **End-to-End Tests**: Full workflow validation

## Submitting Changes

### Pull Request Process

1. **Update your branch**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Squash commits** if needed:
   ```bash
   git rebase -i HEAD~3
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request**:
   - Use descriptive title
   - Link related issues
   - Describe changes clearly
   - Include test results
   - Add screenshots if UI changes

5. **Address review feedback**:
   - Respond to all comments
   - Make requested changes promptly
   - Re-request review when ready

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes (or properly documented)
- [ ] Commit messages are clear
- [ ] Branch is up to date

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Pull Requests**: Code contributions

### Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes for significant contributions
- Invited to join the core team based on sustained involvement

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Questions?** Open an issue with the `[QUESTION]` prefix or reach out via GitHub Discussions.
