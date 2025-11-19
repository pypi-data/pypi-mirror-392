# Installation Guide

## Prerequisites

1. **Python 3.8+**
2. **multirobot package** - Must be installed separately

## Installation Steps

### 1. Install the multirobot package

The `px4` CLI depends on the `multirobot` package. Install it first:

```bash
# If it's a pip package
pip install multirobot

# Or if you have it locally
pip install /path/to/multirobot
```

### 2. Install px4 CLI

#### Development Installation (Recommended for development)

```bash
cd /home/jonas/git/episode
pip install -e .
```

This creates a symlink, so changes to the code are immediately available.

#### Production Installation

```bash
cd /home/jonas/git/episode
pip install .
```

#### Build and Install as Wheel

```bash
cd /home/jonas/git/episode
python3 -m build
pip install dist/px4-*.whl
```

### 3. Verify Installation

```bash
px4 --help
```

You should see the help message with usage instructions.

## Quick Test

Test with a simulator:

```bash
# Start PX4 SITL (in another terminal)
# Then run:
px4 udp:localhost:14540 none track position 0 0 1.5 --takeoff 1.0
```

## Uninstallation

```bash
pip uninstall px4
```

## Publishing to PyPI

To publish this package to PyPI (requires authentication in `~/.pypirc`):

```bash
./build.sh
```

This will:
1. Clean previous builds
2. Build source distribution
3. Upload to PyPI using twine

## Development Setup

For active development:

```bash
# Clone/navigate to repository
cd /home/jonas/git/episode

# Install in editable mode with dev dependencies
pip install -e .

# Make changes to px4/__init__.py
# Changes are immediately available

# Test your changes
px4 udp:localhost:14540 none track position 0 0 1.5 --takeoff 1.0
```

## Troubleshooting

### "No module named 'multirobot'"

Install the multirobot package:
```bash
pip install multirobot
```

### "px4: command not found"

The installation didn't add the script to your PATH. Try:
```bash
# Reinstall
pip install --force-reinstall .

# Or use python -m
python3 -m px4 --help
```

### Permission denied during installation

Use `--user` flag:
```bash
pip install --user .
```

Or use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install .
```


