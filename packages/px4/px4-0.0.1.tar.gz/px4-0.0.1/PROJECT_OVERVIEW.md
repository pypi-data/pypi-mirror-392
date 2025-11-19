# PX4 CLI Project Overview

## Project Structure

```
episode/
├── px4/
│   └── __init__.py          # Main CLI implementation (400+ lines)
├── build.sh                 # Build and publish script
├── pyproject.toml           # Package configuration
├── README.md                # Main documentation
├── EXAMPLES.md              # Usage examples
├── INSTALL.md              # Installation guide
└── PROJECT_OVERVIEW.md     # This file
```

## What Was Built

A complete command-line interface (CLI) utility called `px4` for commanding PX4 quadrotors over MAVLink with support for:

1. **Agile Trajectories**
   - Lissajous (figure-eight) trajectories
   - Circular trajectories
   - Position hold

2. **Motion Capture Integration**
   - Vicon motion capture system support
   - Onboard estimation fallback

3. **Safety Features**
   - Minimum height checks
   - Optional automatic takeoff
   - Controlled landing
   - Gradual position transitions

4. **Flexible Configuration**
   - Multiple connection types (UDP, TCP)
   - Configurable trajectory parameters with sensible defaults
   - Iteration control

## Architecture

### Core Components

1. **PX4Commander Class**
   - Manages PX4 client connection
   - Handles mocap initialization
   - Orchestrates trajectory execution
   - Implements safety checks

2. **Trajectory Tracking**
   - `_track_lissajous()`: Figure-eight trajectories
   - `_track_circle()`: Circular trajectories
   - `_track_position()`: Position hold

3. **CLI Interface**
   - Argument parsing with `argparse`
   - Keyword arguments for all optional parameters
   - Trajectory parameter extraction
   - Async execution with `asyncio`

### Integration with multirobot Package

The CLI leverages the `multirobot` package for:
- **Registry**: Robot configuration (`multirobot.registry`)
- **MOCAP**: Motion capture interface (`multirobot.mocap.Vicon`)
- **Trajectories**: Lissajous and circle functions (`multirobot.trajectories`)
- **Client**: Async quadrotor control interface

## Usage Pattern

```
px4 {URL} {COMMAND} {TRAJECTORY} [OPTIONS]
```

### Mandatory Arguments (Positional):
1. **URL**: Connection URL (e.g., `udp:localhost:14540`)
2. **COMMAND**: Command to execute (e.g., `track`)
3. **TRAJECTORY**: Trajectory type (e.g., `lissajous`, `circle`, `position`)

### Optional Arguments (Keyword):

**General:**
- `--mocap-url URL`: Motion capture system
- `--takeoff HEIGHT`: Automatic takeoff
- `--iterations N`: Number of iterations (default: 5)

**Lissajous:**
- `--A` (default: 1.0), `--B` (default: 0.5), `--z` (default: 2.0)
- `--duration` (default: 10.0), `--ramp-duration` (default: 3.0)

**Circle:**
- `--radius` (default: 1.0), `--z` (default: 2.0)
- `--duration` (default: 6.5), `--ramp-duration` (default: 1.0)

**Position:**
- `--x` (default: 0.0), `--y` (default: 0.0), `--z` (default: 2.0)

### Examples:

**Lissajous with takeoff:**
```bash
px4 udp:localhost:14540 track lissajous --mocap-url vicon:192.168.1.3 --A 1.5 --B 0.75 --z 2.5 --duration 10 --ramp-duration 3 --takeoff 1.0
```

**Circle using defaults:**
```bash
px4 tcp:192.168.1.5:5760 track circle --mocap-url vicon:192.168.1.3 --takeoff 1.0
```

**Position hold:**
```bash
px4 udp:localhost:14540 track position --x 1.0 --y 0.5 --z 2.0 --takeoff 1.0
```

## Key Features Implementation

### 1. Takeoff Mode Logic

When `--takeoff HEIGHT` is specified:
- Arms the quadrotor
- Takes off to specified height
- Executes trajectory **relative to takeoff position**
- Lands at original ground position

When `--takeoff` is NOT specified:
- Checks current height > 0.5m (safety)
- Arms if needed
- Executes trajectory **relative to current position**
- Lands at original ground position

### 2. Safety Checks

```python
if initial_position[2] < min_height_threshold:
    raise ValueError("Current height below minimum threshold")
```

Prevents accidental ground execution without takeoff.

### 3. Trajectory Execution Loop

```python
start_time = time.time()
iteration = 0
while iteration < n_iterations:
    t = time.time() - start_time
    target_position, target_velocity, iteration = trajectory_function(t, **params)
    client.command(target_position + offset, target_velocity)
    await asyncio.sleep(0.01)
```

100Hz control loop for smooth trajectory tracking.

### 4. Connection Handling

Supports multiple URL formats:
- `udp:localhost:14540` - UDP connection (simulator)
- `tcp:192.168.1.5:5760` - TCP connection (real hardware)
- Motion capture: `--mocap-url vicon:192.168.1.3` (optional)

### 5. Keyword Arguments Design

All optional parameters use keyword arguments (`--name value`) for clarity:
- Self-documenting: `--A 1.5 --B 0.75` is clearer than `1.5 0.75`
- Flexible: Can specify only parameters you want to override
- Default values: Each parameter has sensible defaults
- Extensible: Easy to add new parameters without breaking existing commands

## Code Quality

- **Type hints**: Used throughout for clarity
- **Docstrings**: All major functions documented
- **Error handling**: Graceful failures with helpful messages
- **Safety first**: Multiple checks to prevent accidents
- **Clean structure**: Modular design with clear separation of concerns
- **User-friendly**: Clear parameter names and helpful help text

## Testing

The CLI structure was validated with comprehensive tests covering:
- Argument parsing for all trajectory types
- Parameter extraction from keyword arguments
- Default value handling
- Various command combinations

All tests passed successfully.

## Installation

```bash
# Install multirobot first
pip install multirobot

# Install px4 CLI
cd /home/jonas/git/episode
pip install -e .

# Verify
px4 --help
```

## Dependencies

- **Python 3.8+**
- **numpy**: Numerical operations
- **multirobot**: PX4 and mocap interface (must be installed separately)

## Future Enhancements

The CLI is designed to support additional commands beyond `track`:
- `land`: Emergency landing
- `calibrate`: Sensor calibration
- `status`: Report quadrotor status
- `test`: Run system tests

Add new commands by:
1. Adding to `argparse` choices
2. Implementing handler in `async_main()`
3. Creating new methods in `PX4Commander`

## Files Detail

### px4/__init__.py (400+ lines)
Complete implementation including:
- `PX4Commander` class (250+ lines)
- CLI argument parsing with keyword args (80+ lines)
- Trajectory parameter extraction (40+ lines)
- Main entry point (30+ lines)
- Comprehensive error handling
- Safety features

### pyproject.toml
- Standard Python package configuration
- Dependencies specified
- Entry point configured: `px4 = "px4:main"`

### README.md
- Comprehensive user documentation
- Command structure with keyword args
- All trajectory types explained with defaults
- Safety features documented
- Examples for all use cases

### EXAMPLES.md
- Detailed usage examples with keyword args
- Quick start guide
- Troubleshooting section
- Best practices
- Testing workflow
- Command reference summary

### INSTALL.md
- Step-by-step installation
- Prerequisites
- Multiple installation methods
- Troubleshooting

### build.sh
- Build automation
- PyPI publishing

## Design Decisions

1. **Single file implementation**: Kept everything in `__init__.py` for simplicity since the codebase is focused
2. **argparse over click/typer**: Standard library, no extra dependencies
3. **Keyword arguments**: All optional parameters use `--name value` for clarity and flexibility
4. **Sensible defaults**: Each parameter has a default value for common use cases
5. **Async/await**: Matches multirobot package async interface
6. **Relative trajectories**: Safer - trajectories offset from takeoff/current position
7. **Height safety check**: Prevents ground execution accidents
8. **100Hz control loop**: Smooth trajectory following

## CLI Design Philosophy

### Before (positional arguments):
```bash
px4 udp:localhost:14540 vicon:192.168.1.3 track lissajous 1.5 0.75 2.5 10 3 --takeoff 1.0
```
Problems:
- Hard to remember parameter order
- All parameters must be specified
- Unclear what each number means

### After (keyword arguments):
```bash
px4 udp:localhost:14540 track lissajous --mocap-url vicon:192.168.1.3 --A 1.5 --B 0.75 --z 2.5 --duration 10 --ramp-duration 3 --takeoff 1.0
```
Benefits:
- Self-documenting: each parameter clearly labeled
- Flexible: only specify what you want to change
- Defaults: common use cases require minimal flags
- Extensible: easy to add new parameters

### Minimal Commands (using defaults):
```bash
# Lissajous with all defaults
px4 udp:localhost:14540 track lissajous --takeoff 1.0

# Circle with custom height only
px4 udp:localhost:14540 track circle --z 3.0 --takeoff 1.0

# Position at origin
px4 udp:localhost:14540 track position --takeoff 1.0
```

## Usage in Practice

### Old Way (manual script):
- Edit Python script
- Change machine, behavior, parameters
- Run script
- Repeat for different configs

### New Way (CLI):
```bash
# Quick experiments with different parameters
px4 udp:localhost:14540 track lissajous --A 1.5 --takeoff 1.0
px4 udp:localhost:14540 track lissajous --A 2.0 --takeoff 1.0
px4 udp:localhost:14540 track lissajous --A 2.5 --duration 8 --takeoff 1.0

# Easy to script different tests
for A in 1.0 1.5 2.0 2.5; do
  px4 udp:localhost:14540 track lissajous --A $A --takeoff 1.0
done
```

Much faster iteration and testing!

## Summary

A production-ready CLI utility that:
- ✅ Supports PX4 quadrotors over MAVLink
- ✅ Integrates with Vicon motion capture (optional)
- ✅ Implements lissajous, circle, and position trajectories
- ✅ Has safety features (height checks, gradual movements)
- ✅ Supports takeoff and landing
- ✅ Uses keyword arguments for clarity and flexibility
- ✅ Provides sensible defaults for all parameters
- ✅ Is well-documented with extensive examples
- ✅ Has clean, maintainable code
- ✅ Is ready for pip installation
- ✅ Matches the desired CLI interface with improved usability

The tool is ready to use and can be installed with `pip install -e .` after installing the `multirobot` package.
