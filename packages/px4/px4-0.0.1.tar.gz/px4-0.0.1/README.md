# PX4 CLI Utility

A command-line interface for commanding PX4 quadrotors over MAVLink with support for agile trajectories and motion capture feedback.

## Installation

```bash
pip install -e .
```

Or to build and install:

```bash
python3 -m build
pip install dist/px4-*.whl
```

## Usage

### Basic Command Structure

```bash
px4 {URL} {COMMAND} {TRAJECTORY} [OPTIONS]
```

### Mandatory Arguments

- **URL**: PX4 connection URL (positional, required)
  - Format: `udp:localhost:14540` or `tcp:192.168.1.5:5760`
  
- **COMMAND**: Command to execute (positional, required)
  - `track`: Track a trajectory (more commands may be added in the future)

- **TRAJECTORY**: Type of trajectory to execute (positional, required for track command)
  - `lissajous`: Figure-eight trajectory
  - `circle`: Circular trajectory
  - `position`: Hold a fixed position

### Optional Arguments

#### General Options

- `--mocap URL`: Motion capture system URL (e.g., `vicon:192.168.1.3`)
- `--takeoff HEIGHT`: Takeoff to the specified height before executing the trajectory
  - If specified, trajectories are executed relative to the takeoff position
  - If not specified, trajectories are executed relative to the current position (must be flying with height > 0.5m)
- `--iterations N`: Number of times to repeat the trajectory (default: 5)

## Trajectory Types and Parameters

### Lissajous (Figure-Eight)

Optional keyword arguments:

- `--A AMPLITUDE`: Amplitude in X direction in meters (default: 1.0)
- `--B AMPLITUDE`: Amplitude in Y direction in meters (default: 0.5)
- `--z HEIGHT`: Target height in meters (default: 2.0)
- `--duration SECONDS`: Duration of one iteration in seconds (default: 10.0)
- `--ramp-duration SECONDS`: Time to ramp up/down in seconds (default: 3.0)

**Example:**
```bash
px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --A 1.5 --B 0.75 --z 2.5 --duration 10 --ramp-duration 3 --takeoff 1.0
```

This executes a lissajous trajectory with A=1.5m, B=0.75m, height=2.5m, duration=10s, ramp=3s, taking off to 1m first.

### Circle

Optional keyword arguments:

- `--radius METERS`: Radius of the circle in meters (default: 1.0)
- `--z HEIGHT`: Target height in meters (default: 2.0)
- `--duration SECONDS`: Duration of one iteration in seconds (default: 6.5)
- `--ramp-duration SECONDS`: Time to ramp up/down in seconds (default: 1.0)

**Example:**
```bash
px4 tcp:192.168.1.5:5760 track circle --mocap vicon:192.168.1.3 --radius 1.5 --z 2.5 --duration 6.5 --ramp-duration 1.0
```

This executes a circular trajectory with radius=1.5m, height=2.5m, duration=6.5s, ramp=1s.

### Position

Optional keyword arguments:

- `--x METERS`: X coordinate in meters (default: 0.0)
- `--y METERS`: Y coordinate in meters (default: 0.0)
- `--z METERS`: Z coordinate in meters (default: 2.0)

**Example:**
```bash
px4 udp:localhost:14540 track position --x 1.0 --y 0.5 --z 2.0 --takeoff 1.0
```

This takes off to 1m and then moves to and holds position (1.0, 0.5, 2.0).

## Examples

### With Takeoff (Starting from Ground)

```bash
# Lissajous trajectory with takeoff
px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --A 1.5 --B 0.75 --z 2.5 --duration 10 --ramp-duration 3 --takeoff 1.0

# Circle with takeoff, 3 iterations
px4 udp:localhost:14540 track circle --mocap vicon:192.168.1.3 --radius 1.0 --z 2.0 --duration 6.5 --ramp-duration 1.0 --takeoff 1.0 --iterations 3

# Hold position with takeoff
px4 udp:localhost:14540 track position --mocap vicon:192.168.1.3 --z 2.0 --takeoff 1.0
```

### Without Takeoff (Already Flying)

```bash
# Lissajous from current position (must be > 0.5m high)
px4 tcp:192.168.1.5:5760 track lissajous --mocap vicon:192.168.1.3 --A 2.0 --B 1.0 --z 3.0 --duration 12 --ramp-duration 4

# Circle from current position
px4 udp:localhost:14540 track circle --mocap vicon:192.168.1.3 --radius 1.5 --z 2.5 --duration 7 --ramp-duration 1.5
```

### Without Motion Capture

```bash
# Use onboard position estimation only (omit --mocap)
px4 udp:localhost:14540 track lissajous --A 1.0 --B 0.5 --z 2.0 --duration 8 --ramp-duration 2 --takeoff 1.0
```

## Safety Features

- **Minimum Height Check**: If not using `--takeoff`, the current height must be > 0.5m to prevent accidental ground execution
- **Gradual Position Changes**: Position commands are ramped gradually
- **Controlled Landing**: After trajectory completion, the quadrotor hovers briefly then lands at the initial position

## Behavior Details

### With `--takeoff` Flag
1. Arms the quadrotor
2. Takes off to specified height
3. Moves to trajectory start position
4. Executes trajectory relative to takeoff position
5. Hovers for 2 seconds after completion
6. Lands at initial ground position

### Without `--takeoff` Flag
1. Checks current height is > 0.5m (safety check)
2. Arms the quadrotor (if not already armed)
3. Moves to trajectory start position
4. Executes trajectory relative to current position
5. Hovers for 2 seconds after completion
6. Lands at initial ground position

## Dependencies

- `numpy`: Numerical computing
- `multirobot`: Interface to PX4 and motion capture systems
  - Includes trajectory functions (`lissajous`, `circle`)
  - MAVLink communication
  - Vicon motion capture interface

## Integration with Multirobot Package

This CLI uses the `multirobot` package for:
- **Registry**: Robot configuration management (`multirobot.registry`)
- **MOCAP**: Vicon motion capture system interface (`multirobot.mocap.Vicon`)
- **Trajectories**: Pre-defined trajectory functions (`multirobot.trajectories.lissajous`, `multirobot.trajectories.circle`)
- **Client**: Async client interface with methods like `arm()`, `goto()`, `command()`

## Development

To install in development mode:

```bash
pip install -e .
```

To build for distribution:

```bash
./build.sh
```

## License

MIT License - see LICENSE file for details

## Author

Jonas Eschmann (jonas.eschmann@gmail.com)

