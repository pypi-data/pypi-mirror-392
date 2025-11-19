# PX4 CLI Usage Examples

## Quick Start

### 1. Simulator with Lissajous Trajectory

```bash
# Connect to simulator, track lissajous with takeoff
px4 udp:localhost:14540 track lissajous --A 1.5 --B 0.75 --z 2.5 --duration 10 --ramp-duration 3 --takeoff 1.0
```

### 2. Real Quadrotor with Vicon and Circle

```bash
# Connect to real quadrotor via TCP, use Vicon mocap, track circle
px4 tcp:192.168.1.5:5760 track circle --mocap vicon:192.168.1.3 --radius 1.5 --z 2.5 --duration 6.5 --ramp-duration 1.0 --takeoff 1.0
```

### 3. Position Hold

```bash
# Hold position (0, 0, 2.0) with takeoff
px4 udp:localhost:14540 track position --mocap vicon:192.168.1.3 --z 2.0 --takeoff 1.0
```

## Detailed Examples

### Lissajous (Figure-Eight) Trajectory

**Small figure-eight close to ground:**
```bash
px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --A 0.5 --B 0.25 --z 1.5 --duration 8 --ramp-duration 2 --takeoff 0.5
```
- A=0.5m (X amplitude)
- B=0.25m (Y amplitude)
- z=1.5m (height)
- duration=8s per iteration
- ramp=2s
- takeoff to 0.5m first

**Large figure-eight at high altitude:**
```bash
px4 tcp:192.168.1.5:5760 track lissajous --mocap vicon:192.168.1.3 --A 3.0 --B 1.5 --z 3.5 --duration 12 --ramp-duration 4 --takeoff 1.0 --iterations 3
```
- A=3.0m (X amplitude)
- B=1.5m (Y amplitude)
- z=3.5m (height)
- duration=12s per iteration
- ramp=4s
- takeoff to 1.0m first
- Execute 3 iterations

**Continue from current position (no takeoff):**
```bash
# Note: Quadrotor must already be flying above 0.5m
px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --A 1.0 --B 0.5 --z 2.0 --duration 10 --ramp-duration 3
```

**Using defaults (minimal command):**
```bash
# Uses default values: A=1.0, B=0.5, z=2.0, duration=10.0, ramp-duration=3.0
px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --takeoff 1.0
```

### Circle Trajectory

**Small slow circle:**
```bash
px4 udp:localhost:14540 track circle --mocap vicon:192.168.1.3 --radius 0.75 --z 2.0 --duration 8 --ramp-duration 2 --takeoff 1.0
```
- radius=0.75m
- z=2.0m (height)
- duration=8s per iteration
- ramp=2s

**Large fast circle:**
```bash
px4 tcp:192.168.1.5:5760 track circle --mocap vicon:192.168.1.3 --radius 2.0 --z 3.0 --duration 5 --ramp-duration 1 --takeoff 1.0 --iterations 10
```
- radius=2.0m
- z=3.0m (height)
- duration=5s per iteration
- ramp=1s
- 10 iterations

**Using defaults (minimal command):**
```bash
# Uses default values: radius=1.0, z=2.0, duration=6.5, ramp-duration=1.0
px4 udp:localhost:14540 track circle --mocap vicon:192.168.1.3 --takeoff 1.0
```

### Position Hold

**Origin with low altitude:**
```bash
px4 udp:localhost:14540 track position --mocap vicon:192.168.1.3 --z 1.5 --takeoff 1.0
```
- Hold at (0, 0, 1.5) using defaults for x and y

**Offset position:**
```bash
px4 udp:localhost:14540 track position --mocap vicon:192.168.1.3 --x 2.0 --y 1.5 --z 2.5 --takeoff 1.0
```
- Hold at (2.0, 1.5, 2.5)

**From current altitude (no takeoff):**
```bash
# Quadrotor must already be flying
px4 udp:localhost:14540 track position --mocap vicon:192.168.1.3 --x 1.0 --y 1.0 --z 2.0
```

**Using defaults (minimal command):**
```bash
# Uses default values: x=0.0, y=0.0, z=2.0
px4 udp:localhost:14540 track position --mocap vicon:192.168.1.3 --takeoff 1.0
```

## Connection Types

### UDP (Simulator/SITL)

```bash
# Local simulator
px4 udp:localhost:14540 track lissajous --takeoff 1.0

# Remote simulator
px4 udp:192.168.1.100:14540 track lissajous --takeoff 1.0
```

### TCP (Real Hardware)

```bash
# Race quadrotor
px4 tcp:192.168.1.5:5760 track lissajous --mocap vicon:192.168.1.3 --takeoff 1.0

# Custom IP/port
px4 tcp:192.168.1.20:5760 track lissajous --mocap vicon:192.168.1.3 --takeoff 1.0
```

## Motion Capture Options

### Vicon

```bash
px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --A 1.0 --B 0.5 --z 2.0 --duration 10 --ramp-duration 3 --takeoff 1.0
```

### No Motion Capture (Onboard Estimation Only)

```bash
# Simply omit the --mocap argument
px4 udp:localhost:14540 track lissajous --A 1.0 --B 0.5 --z 2.0 --duration 10 --ramp-duration 3 --takeoff 1.0
```

## Tips and Best Practices

### Safety

1. **Always test in simulation first:**
   ```bash
   px4 udp:localhost:14540 track lissajous --A 1.0 --B 0.5 --z 2.0 --duration 10 --ramp-duration 3 --takeoff 1.0
   ```

2. **Start with small trajectories and low speeds:**
   ```bash
   px4 tcp:192.168.1.5:5760 track circle --mocap vicon:192.168.1.3 --radius 0.5 --z 1.5 --duration 10 --ramp-duration 3 --takeoff 0.5
   ```

3. **Use appropriate takeoff height:**
   - For small indoor spaces: `--takeoff 0.5` to `--takeoff 1.0`
   - For larger spaces: `--takeoff 1.0` to `--takeoff 2.0`

4. **Keep emergency stop ready:**
   - Always be ready to interrupt with `Ctrl+C`
   - Have RC controller ready as backup

### Testing Workflow

1. **Test position hold first:**
   ```bash
   px4 udp:localhost:14540 track position --mocap vicon:192.168.1.3 --z 1.5 --takeoff 1.0
   ```

2. **Test single iteration:**
   ```bash
   px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --A 1.0 --B 0.5 --z 2.0 --duration 10 --ramp-duration 3 --takeoff 1.0 --iterations 1
   ```

3. **Scale up gradually:**
   ```bash
   # Small
   px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --A 0.5 --B 0.25 --z 2.0 --duration 10 --ramp-duration 3 --takeoff 1.0
   
   # Medium
   px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --A 1.0 --B 0.5 --z 2.5 --duration 10 --ramp-duration 3 --takeoff 1.0
   
   # Large
   px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --A 2.0 --B 1.0 --z 3.0 --duration 10 --ramp-duration 3 --takeoff 1.0
   ```

### Performance Tuning

**Fast aggressive trajectory:**
```bash
px4 tcp:192.168.1.5:5760 track lissajous --mocap vicon:192.168.1.3 --A 2.0 --B 1.0 --z 2.5 --duration 6 --ramp-duration 1 --takeoff 1.0
```
- Short duration (6s) = faster movement
- Short ramp (1s) = more aggressive

**Slow smooth trajectory:**
```bash
px4 tcp:192.168.1.5:5760 track lissajous --mocap vicon:192.168.1.3 --A 2.0 --B 1.0 --z 2.5 --duration 15 --ramp-duration 5 --takeoff 1.0
```
- Long duration (15s) = slower movement
- Long ramp (5s) = smoother transitions

## Advanced Usage

### Override Specific Parameters Only

You can specify only the parameters you want to change from defaults:

```bash
# Only change height, use defaults for rest
px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --z 3.0 --takeoff 1.0

# Only change amplitude, use defaults for rest
px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --A 2.5 --takeoff 1.0

# Only change duration and ramp
px4 udp:localhost:14540 track circle --mocap vicon:192.168.1.3 --duration 10 --ramp-duration 2 --takeoff 1.0
```

### Combining Multiple Options

```bash
# Full specification with all options
px4 tcp:192.168.1.5:5760 track lissajous \
    --mocap vicon:192.168.1.3 \
    --A 2.0 \
    --B 1.0 \
    --z 3.0 \
    --duration 12 \
    --ramp-duration 4 \
    --takeoff 1.5 \
    --iterations 10
```

## Troubleshooting

### "Current height below minimum threshold"

You tried to run without `--takeoff` while on the ground:
```bash
# Wrong (on ground without --takeoff)
px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --A 1.0 --B 0.5 --z 2.0 --duration 10 --ramp-duration 3

# Right (add --takeoff)
px4 udp:localhost:14540 track lissajous --mocap vicon:192.168.1.3 --A 1.0 --B 0.5 --z 2.0 --duration 10 --ramp-duration 3 --takeoff 1.0
```

### Connection Issues

```bash
# Check your URL format
# Good:
px4 udp:localhost:14540 track lissajous --takeoff 1.0
px4 tcp:192.168.1.5:5760 track lissajous --mocap vicon:192.168.1.3 --takeoff 1.0

# Bad:
px4 localhost:14540 track lissajous --takeoff 1.0  # Missing protocol
px4 udp://localhost:14540 track lissajous --takeoff 1.0  # Don't use ://
```

### Motion Capture Not Working

```bash
# Try without mocap first
px4 udp:localhost:14540 track position --z 1.5 --takeoff 1.0

# Check Vicon IP is correct
px4 udp:localhost:14540 track position --mocap vicon:192.168.1.3 --z 1.5 --takeoff 1.0
```

### Missing Required Arguments

```bash
# Error: must specify all required positional arguments
px4 udp:localhost:14540 lissajous  # Missing 'track' command

# Correct:
px4 udp:localhost:14540 track lissajous --takeoff 1.0
```

## Command Reference Summary

### Mandatory Arguments (positional)
1. URL (e.g., `udp:localhost:14540`)
2. Command (e.g., `track`)
3. Trajectory type (e.g., `lissajous`, `circle`, `position`)

### Optional Arguments (keyword)
- `--mocap URL` - Motion capture system (e.g., `vicon:192.168.1.3`)
- `--takeoff HEIGHT` - Automatic takeoff
- `--iterations N` - Number of iterations (default: 5)

### Trajectory-Specific Parameters
**Lissajous:**
- `--A` (default: 1.0), `--B` (default: 0.5), `--z` (default: 2.0)
- `--duration` (default: 10.0), `--ramp-duration` (default: 3.0)

**Circle:**
- `--radius` (default: 1.0), `--z` (default: 2.0)
- `--duration` (default: 6.5), `--ramp-duration` (default: 1.0)

**Position:**
- `--x` (default: 0.0), `--y` (default: 0.0), `--z` (default: 2.0)
