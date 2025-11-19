import sys
import argparse
import asyncio
import numpy as np
from typing import Optional, Dict, Any
import time

import multirobot.registry
from multirobot.mocap import Vicon

from .trajectories import Trajectory
from .trajectories.lissajous import Lissajous
from .trajectories.circle import Circle
from .trajectories.position import Position


class PX4Commander:
    
    def __init__(self, url: str, mocap_url: Optional[str] = None):
        self.url = url
        self.mocap_url = mocap_url
        self.client = None
        self.mocap = None
        
    async def initialize(self):
        if self.mocap_url:
            mocap_type, mocap_address = self._parse_mocap_url(self.mocap_url)
            if mocap_type == "vicon":
                self.mocap = Vicon(
                    mocap_address,
                    VELOCITY_CLIP=10,
                    ACCELERATION_FILTER=20,
                    ORIENTATION_FILTER=10,
                    EXPECTED_FRAMERATE=100
                )
            else:
                raise ValueError(f"Unsupported mocap type: {mocap_type}")
        
        config = self._create_config()
        
        if self.mocap:
            clients = multirobot.registry.make_clients(self.mocap, {"px4": config})
        else:
            clients = multirobot.registry.make_clients(None, {"px4": config})
        
        self.client = clients["px4"]
        
        while self.client.position is None:
            await asyncio.sleep(0.01)
    
    def _parse_mocap_url(self, url: str) -> tuple:
        parts = url.split(":", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid mocap URL format: {url}. Expected format: 'type:address'")
        return parts[0], parts[1]
    
    def _create_config(self) -> Dict[str, Any]:
        config = {
            "type": "px4",
            "kwargs": {
                "uri": self.url,
                "log_fields_state_additional": ["in_trajectory"],
                "odometry_source": "feedback"
            },
            "mocap": "feedback"
        }
        return config
    
    async def track_trajectory(
        self,
        trajectory: Trajectory,
        takeoff_height: Optional[float] = None,
        n_iterations: int = 5,
        min_height_threshold: float = 0.5,
    ):
        initial_position = self.client.position.copy()
        print(f"Initial position: {initial_position}")
        
        if takeoff_height is not None:
            print(f"Takeoff mode: will takeoff to {takeoff_height}m")
            takeoff_position = initial_position + np.array([0, 0, takeoff_height])
            offset = takeoff_position
            
            await self.client.arm()
            print("Armed. Taking off...")
            await self.client.goto(takeoff_position, distance_threshold=0.15)
            print("Takeoff complete.")
        else:
            if initial_position[2] < min_height_threshold:
                raise ValueError(
                    f"Current height ({initial_position[2]:.2f}m) is below minimum threshold "
                    f"({min_height_threshold}m). Either use --takeoff or manually fly higher."
                )
            
            print(f"No takeoff specified. Using current position (height: {initial_position[2]:.2f}m)")
            offset = initial_position.copy()
            
            await self.client.arm()
            print("Armed.")
        
        await self._execute_trajectory(trajectory, offset, n_iterations)
        
        print("Trajectory complete. Hovering...")
        hover_time = time.time()
        final_position = self.client.position.copy()
        while time.time() - hover_time < 2:
            await self.client.goto(final_position, distance_threshold=0.15)
            await asyncio.sleep(0.01)
        
        print("Landing...")
        landing_target = initial_position.copy()
        landing_target[2] = 0
        while True:
            await self.client.goto(landing_target, distance_threshold=0.15)
            await asyncio.sleep(0.01)
    
    async def _execute_trajectory(
        self, 
        trajectory: Trajectory, 
        offset: np.ndarray, 
        n_iterations: int
    ):
        start_pos, _, _ = trajectory.get_state(0.0)
        target_position = start_pos + offset
        print(f"Moving to start position: {target_position}")
        await self.client.goto(target_position, distance_threshold=0.15)
        
        start_time = time.time()
        iteration = 0
        self.client.log_state_additional = {"in_trajectory": 1}
        
        while iteration < n_iterations:
            t = time.time() - start_time
            target_position, target_velocity, iteration = trajectory.get_state(t)
            
            if iteration != getattr(self, '_last_iteration', -1):
                print(f"Iteration: {iteration}/{n_iterations}")
                self._last_iteration = iteration
            
            self.client.command(target_position + offset, target_velocity)
            await asyncio.sleep(0.01)
        
        self.client.log_state_additional = {"in_trajectory": 0}


def create_trajectory(trajectory_type: str, params) -> Trajectory:
    if trajectory_type == "lissajous":
        return Lissajous(**params)
    elif trajectory_type == "circle":
        return Circle(**params)
    elif trajectory_type == "position":
        return Position(**params)
    else:
        raise ValueError(f"Unknown trajectory type: {trajectory_type}")


async def async_main(args):
    commander = PX4Commander(args.url, args.mocap)
    
    print("Initializing PX4 connection...")
    await commander.initialize()
    print("Connected successfully.")
    
    if args.command == "track":
        trajectory = create_trajectory(args.trajectory, vars(args))
        
        await commander.track_trajectory(trajectory=trajectory, takeoff_height=args.takeoff, n_iterations=args.iterations)


def main():
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    
    parser.add_argument("url", help="PX4 connection URL (e.g., udp:localhost:14540, tcp:192.168.1.5:5760)")
    parser.add_argument("command", choices=["track"], help="Command to execute")
    parser.add_argument("trajectory", choices=["lissajous", "circle", "position"], help="Trajectory type")
    
    parser.add_argument("--mocap", type=str, default=None, help="Motion capture system (e.g., vicon:192.168.1.3)")
    parser.add_argument("--takeoff", type=float, default=None, help="Takeoff to specified height before executing trajectory")
    parser.add_argument("--iterations", type=int, default=5, help="Number of trajectory iterations (default: 5)")

    Lissajous.declare_arguments(parser)
    Circle.declare_arguments(parser)
    Position.declare_arguments(parser)
    
    
    args = parser.parse_args()
    
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
