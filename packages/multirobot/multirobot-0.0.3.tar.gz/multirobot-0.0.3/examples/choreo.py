from copy import copy
from muxify import Muxify
import asyncio
import sys
import numpy as np
from multirobot.driver.simulator.simulator import Simulator, SimulatedDrone
import matplotlib.pyplot as plt
import json
import l2f
import os
import trigga
from multirobot.trajectories.lissajous_uniform import lissajous_uniform, plot_lissajous
import multirobot.registry
from multirobot.mocap import Vicon
import cflib
import signal
from copy import deepcopy, copy
np.random.seed(42)

class Behavior:
    def __init__(self, clients, lissajous_parameters={}, position_offset=np.array([0, 0, 0]), spacing=None, height=0.3):
        self.clients = clients
        self.initial_positions = []
        self.position_offsets = []
        self.lissajous_parameters = lissajous_parameters
        assert len(self.clients) > 0, "At least one client is required"
        self.spacing = spacing if spacing is not None else np.array([0, *np.ones(len(clients)-1)])
        self.height = height
        self.position_offset = position_offset

    async def run(self):
        print("Waiting for deadman trigger")
        while not trigga.trigga:
            await asyncio.sleep(0.1)
        for i, client in enumerate(self.clients):
            while client.position is None or client.velocity is None:
                await asyncio.sleep(0.1)
            self.initial_positions.append(copy(client.position))
        self.initial_positions = np.array(self.initial_positions)
        self.target_positions = self.initial_positions.copy()
        self.target_positions[:, 2] = self.height
        self.initial_target_positions = self.target_positions.copy()
        self.target_velocities = np.zeros_like(self.target_positions)
        for client in self.clients:
            await client.arm()
            self.send_commands()
            await asyncio.sleep(0.10)
        print("Clients armed")
        tick = 0
        EPSILON = 0.25
        print("Waiting for clients to reach initial positions")
        while not all([np.linalg.norm(client.position - self.target_positions[i]) < EPSILON for i, client in enumerate(self.clients)]):
            mask = [np.linalg.norm(client.position - self.target_positions[i]) > EPSILON for i, client in enumerate(self.clients)] 
            print(f"Mask: {np.array([c.name for c in self.clients])[mask]}")
            self.send_commands()
            await asyncio.sleep(0.1)
            tick += 1
        print("Starting behavior")
        t = 0
        dt = 0.1
        cumsum_spacing = np.cumsum(self.spacing)
        while True:
            in_trajectory = np.sum(t > cumsum_spacing)
            # print(f"In trajectory: {in_trajectory}, t: {t:.2f}, tick: {tick}")
            self.target_positions[in_trajectory:] = self.initial_target_positions[:-in_trajectory] if in_trajectory > 0 else self.initial_target_positions
            for i, client in enumerate(self.clients):
                if t > cumsum_spacing[i]:
                    offset = 0.5
                    self.target_positions[i], self.target_velocities[i] = lissajous_uniform(t - cumsum_spacing[i] + offset, **self.lissajous_parameters, z=self.height)
                    self.target_positions[i] += self.position_offset
            self.send_commands()
            await asyncio.sleep(dt)
            tick += 1
            t += dt
    
    def send_commands(self):
        # drones_in_avoidance, (target_positions, target_velocities) = self.avoid_collisions(self.target_positions, self.target_velocities)
        target_positions, target_velocities = self.target_positions, self.target_velocities
        for client, target_position, target_velocity in zip(self.clients, target_positions, target_velocities):
            client.command(target_position, target_velocity)


VICON_IP = "192.168.1.3"
async def main():
    mocap = Vicon(VICON_IP, VELOCITY_CLIP=5, EXPECTED_FRAMERATE=100)
    global simulator
    RANDOM_CLOSE_CALLS = False
    scale = 1.2
    lissajous_parameters = dict(A=1.5*scale, B=0.8*scale, duration=20)
    initial_positions = np.array([
        [0, 0., 0],
        [-0.3, 0, 0],
        [-0.6, 0, 0],
        [-0.9, 0, 0],
        [-1.2, 0, 0],
        [-1.5, 0, 0],
    ])
    spacing = np.array([2, 1.25, 1.0, 1.0, 0.75, 1.0]) * 20/15
    real_machines = ["race", "savagebee_pusher", "crazyflie_bl", "crazyflie", "hummingbird", "m5stampfly"]
    # real_machines = ["crazyflie_bl"]
    # real_machines = ["race", "m5stampfly"]
    # real_machines = ["race"]
    # real_machines = []
    # real_machines = ["race"] #, "savagebee_pusher", "crazyflie_bl", "crazyflie", "hummingbird"]
    simulator_shadows = [f"simulator_race.{machine}_shadow" for machine in real_machines]
    simulator_shadow_lookup = {"_".join(k.split(".")[1].split("_")[:-1]): k for k in simulator_shadows}
    simulator_machines = [f"simulator_race.{i}" for i in range(len(spacing)-len(real_machines))]
    machines = real_machines + simulator_shadows + simulator_machines
    configs = {machine:deepcopy(multirobot.registry.configs[machine.split(".")[0]]) for machine in machines}
    for i, key in enumerate(real_machines+simulator_machines):
        config = configs[key]
        if config["type"] == "simulator":
            config["kwargs"]["initial_position"] = initial_positions[i]
    clients_kv = multirobot.registry.make_clients(mocap, configs)
    clients = [clients_kv[machine] for machine in real_machines + simulator_machines]

    assert len(clients) == len(spacing), f"Number of clients ({len(clients)}) and spacing ({len(spacing)}) must match"
    
    behavior = Behavior(clients, lissajous_parameters=lissajous_parameters, spacing=spacing, height=0.7, position_offset=np.array([0, 0, 0]))
    async def loop():
        tick = 0
        dt = 0.01
        while True:
            for i, client_key in enumerate(real_machines):
                client = clients_kv[client_key]
                simulator_shadow_key = simulator_shadow_lookup[client_key]
                simulator_shadow = clients_kv[simulator_shadow_key]
                if client.position is not None and client.velocity is not None and client.orientation is not None:
                    simulator_shadow.simulator.state.states[simulator_shadow.id].position = client.position
                    simulator_shadow.simulator.state.states[simulator_shadow.id].linear_velocity = client.velocity
                    simulator_shadow.simulator.state.states[simulator_shadow.id].orientation = client.orientation
                    simulator_shadow.simulator.state.states[simulator_shadow.id].angular_velocity = np.array([0, 0, 0])
                
            await asyncio.sleep(dt)
            tick += 1
    tasks = [
        asyncio.create_task(trigga.monitor(type="foot-pedal", path="/dev/input/by-id/usb-PCsensor_FootSwitch-event-kbd")),
        # asyncio.create_task(trigga.monitor(type="gamepad")),
        asyncio.create_task(behavior.run()),
        asyncio.create_task(loop())
    ]
    await asyncio.sleep(1)
    await asyncio.gather(*tasks)

class MocapDummy:
    def __init__(self):
        pass
    def _mocap_callback(self, timestamp, position, orientation, velocity, reset_counter):
        pass


async def main_mocap_test():
    mocap = Vicon(VICON_IP, VELOCITY_CLIP=5, EXPECTED_FRAMERATE=100)
    for name in ["hummingbird", "m5stampfly", "crazyflie", "crazyflie_bl", "race_jonas"]:
        mocap.add(name, MocapDummy()._mocap_callback)
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(main_mocap_test())


