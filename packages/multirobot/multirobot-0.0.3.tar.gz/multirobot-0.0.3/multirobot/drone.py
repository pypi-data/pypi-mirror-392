import asyncio
from enum import Enum
import numpy as np
import time
import csv
from scipy.spatial.transform import Rotation as R
import trigga

class Drone:
    def __init__(self, name, stdout=None, log_fields_state_additional=[]):
        self.stdout = stdout
        self.position = None
        self.velocity = None
        self.orientation = None
        self.simulated = False
        print(f"Client {name} initialized", file=self.stdout)
        self.name = name
        self.csvfile = open(f"log_{time.strftime('%Y-%m-%d_%H-%M-%S')}_{name}.csv", 'w', newline='')
        self.writer = csv.writer(self.csvfile)
        self.log_fields = ['timestamp', 'trigga', 'x', 'y', 'z', 'euler_x', 'euler_y', 'euler_z', 'qw', 'qx', 'qy', 'qz', 'vx', 'vy', 'vz', 'target_x', 'target_y', 'target_z', 'target_vx', 'target_vy', 'target_vz']
        self.log_fields_metadata = None
        self.log_fields_state_additional = log_fields_state_additional
        self.header_written = False
        self.target_position = None
        self.target_velocity = None
        self.log_state_additional = {}
    def _odometry_callback(self, timestamp, position, orientation, velocity, metadata):
        if self.log_fields_metadata is None:
            self.log_fields_metadata = list(metadata.keys())
        if self.log_state_additional is not None:
            self.log_fields_state_additional = list(self.log_state_additional.keys())
        
        if self.log_fields_metadata is not None and self.log_fields_state_additional is not None and not self.header_written:
            self.writer.writerow(self.log_fields + self.log_fields_metadata + self.log_fields_state_additional)
            self.header_written = True
        euler = R.from_quat(orientation).as_euler('XYZ')
        target_position = self.target_position if self.target_position is not None else np.zeros(3)
        target_velocity = self.target_velocity if self.target_velocity is not None else np.zeros(3)
        self.writer.writerow([timestamp, 1 if trigga.trigga else 0, *position, *euler, *orientation, *velocity, *target_position, *target_velocity] + [metadata[field] for field in self.log_fields_metadata] + [self.log_state_additional[field] for field in self.log_fields_state_additional])
        self.position = position
        self.velocity = velocity
        self.orientation = orientation
    async def arm(self):
        await self._arm()
    async def disarm(self):
        await self._disarm()
    def command(self, position, velocity, yaw=0):
        self.target_position = position
        self.target_velocity = velocity
        self._forward_command(position, velocity, yaw=yaw)

    async def goto(self, target_input, distance_threshold=0.15, timeout=None, relative=True, target_yaw=None, yaw_threshold=10/180*np.pi, verbose=True):
        print(f"Going to {target_input}") if verbose else None
        distance = None
        yaw = None
        start = time.time()
        while distance is None or distance > distance_threshold or (target_yaw is not None and yaw is None) or (target_yaw is not None and yaw is not None and abs(yaw - target_yaw) > yaw_threshold) or (timeout is not None and time.time() - start < timeout) and not self.disarmed:
            if self.position is not None:
                target = target_input if relative else target_input
                distance = np.linalg.norm(target - self.position)
                if self.orientation is not None:
                    w_m, z_m = self.orientation[0], self.orientation[3]
                    if w_m < 0:
                        w_m = -w_m
                        z_m = -z_m
                    d_m = np.sqrt(w_m*w_m + z_m*z_m)
                    if d_m > 1e-6:
                        yaw = 2 * np.arctan2(z_m / d_m, w_m / d_m)
                # print(f"Distance to target: {distance:.2f} m", file=mux[4])
                self.command(target, [0, 0, 0], yaw=target_yaw if target_yaw is not None else 0)
            else:
                print("Position not available yet")
            await asyncio.sleep(0.1)

    async def land(self):
        while self.position is None:
            print("Land: Position not available yet")
            await asyncio.sleep(0.1)
        target_position = self.position.copy()
        target_position[2] = 0.0
        await self.goto(target_position, distance_threshold=0.1)

    async def run(self):
        while True:
            await asyncio.sleep(0.1)