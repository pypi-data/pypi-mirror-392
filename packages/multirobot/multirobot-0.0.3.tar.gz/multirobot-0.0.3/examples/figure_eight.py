import numpy as np
import matplotlib.pyplot as plt
from multirobot.trajectories.lissajous import lissajous
from multirobot.trajectories.circle import circle
import asyncio
import time
import multirobot.registry
from multirobot.mocap import Vicon
import copy
import trigga

async def main():
    # machine = "simulator_race"
    # machine = "crazyflie_bl"
    # machine = "race"
    # machine = "soft"
    machine = "gazebo"
    # machine = "soft_rigid"
    # machine = "meteor75"
    # machine = "savagebee_pusher"
    # machine = "hummingbird"
    # machine = "pavo20"
    # machine = "m5stampfly"

    behavior = "trajectory"
    # behavior = "speed"
    # behavior = "position"
    # behavior = "angle"
    # behavior = "crash"
    # behavior = "step_response"

    no_trigga_machines = ["race", "soft", "gazebo"]
    DISABLE_TRIGGA = True

    assert not DISABLE_TRIGGA or machine in no_trigga_machines
    if not DISABLE_TRIGGA:
        trigga.run(type="foot-pedal", path="/dev/input/by-id/usb-PCsensor_FootSwitch-event-kbd")
    # trigga.run(type="gamepad")
    scale = 3
    target_height = 3.3
    offset = np.array([0, 0, 0.0])
    lissajous_parameters = dict(A=1.0*scale, B=0.5*scale, z=target_height, duration=10, ramp_duration=3)
    circle_parameters = dict(radius=1.0, z=target_height, duration=6.5, ramp_duration=1)
    N_ITERATIONS = 5

    t_vals = np.linspace(0, lissajous_parameters["duration"] + lissajous_parameters["ramp_duration"]/2, 1000)
    coords = np.array([lissajous(t, **lissajous_parameters)[0] for t in t_vals])
    vels = np.array([lissajous(t, **lissajous_parameters)[1] for t in t_vals])

    # plt.figure(figsize=(6, 6))
    # plt.plot(t_vals, coords[:, 0], label="x")
    # plt.plot(t_vals, vels[:, 0], label="vx")
    # plt.plot(t_vals, coords[:, 1], label="y")
    # plt.plot(t_vals, vels[:, 1], label="vy")
    # plt.legend()
    # plt.show()

    # plt.figure(figsize=(6, 6))
    # plt.plot(coords[:, 0], coords[:, 1])
    # plt.xlabel("x")
    # plt.ylabel("y")
    # plt.axis("equal")
    # plt.title("Figure Eight")
    # plt.show()

    config = copy.deepcopy(multirobot.registry.configs[machine])
    if machine == "race":
        config["kwargs"]["uri"] = "tcp:192.168.1.5:5760"
    # if machine == "meteor75" or machine == "pavo20":
    #     config["kwargs"]["SOFT_LANDING"] = False
    if machine in ["simulator_race", "gazebo"]:
        if machine == "simulator_race":
            config["kwargs"]["initial_position"] = [0, 0, 0]
        mocap = None
    else:
        mocap = Vicon(multirobot.registry.VICON_IP, VELOCITY_CLIP=10, ACCELERATION_FILTER=20, ORIENTATION_FILTER=10, EXPECTED_FRAMERATE=100)
    
    config["kwargs"]["log_fields_state_additional"] = ["in_trajectory"]

    clients = multirobot.registry.make_clients(mocap, {machine: config})
    client = clients[machine]
    client.log_state_additional["in_trajectory"] = 0


    while client.position is None:
        await asyncio.sleep(0.01)
    
    initial_position = client.position
    takeoff_position = initial_position + np.array([0, 0, 1.0])
    target_position = np.zeros(3) + np.array([0, 0, target_height]) + offset

    if not DISABLE_TRIGGA:
        while not trigga.trigga:
            await asyncio.sleep(0.01)

    await client.arm()

    if behavior == "trajectory":
        # trajectory_type = "circle"
        trajectory_type = "lissajous"
        if trajectory_type == "circle":
            target_position = np.array([circle_parameters["radius"], 0, target_height]) + offset
        assert trajectory_type in ["lissajous", "circle"]
    if behavior == "trajectory":
        await client.goto(takeoff_position, distance_threshold=0.15)
        await client.goto(target_position, distance_threshold=0.15)
        # await asyncio.sleep(1)
        start_time = time.time()
        iteration = 0
        while iteration < N_ITERATIONS:
            client.log_state_additional["in_trajectory"] = 1
            if trajectory_type == "lissajous":
                target_position, target_velocity, iteration = lissajous(time.time() - start_time, **lissajous_parameters)
            elif trajectory_type == "circle":
                target_position, target_velocity, iteration = circle(time.time() - start_time, **circle_parameters)
            print(f"iteration: {iteration}")
            client.command(target_position + offset, target_velocity)
            await asyncio.sleep(0.01)
        client.log_state_additional["in_trajectory"] = 0
        hover_time = time.time()
        while time.time() - hover_time < 2:
            await client.goto(np.array(target_position), distance_threshold=0.15)
            await asyncio.sleep(0.01)
        while True:
            # land
            await client.goto(np.array([0, 0, 0]), distance_threshold=0.15)

    elif behavior == "step_response":
        await client.goto(takeoff_position, distance_threshold=0.15)
        await client.goto(target_position, distance_threshold=0.25)
        EPSILON = 0.25
        while True:
            client.log_state_additional["in_trajectory"] = 1
            target = np.array([1, 0, target_height])
            start_time = time.time()
            while time.time() - start_time < 2:
                await client.goto(target, distance_threshold=EPSILON)
                await asyncio.sleep(0.01)
            target = np.array([-1, 0, target_height])
            start_time = time.time()
            while time.time() - start_time < 2:
                await client.goto(target, distance_threshold=EPSILON)
                await asyncio.sleep(0.01)

    elif behavior == "position":
        height = 1.00
        client.log_state_additional["in_trajectory"] = 1
        target = np.array([0, 0, height])
        N = 10
        for i in range(10):
            print(f"Going to {target}")
            await client.goto(initial_position + (target - initial_position) * i / N, distance_threshold=0.15)
            await asyncio.sleep(0.01)
        while True:
            await client.goto(target)
            await asyncio.sleep(0.01)
    elif behavior == "angle":
        height = 0.50
        client.log_state_additional["in_trajectory"] = 1
        target = initial_position.copy()
        target[2] = height
        print(f"Going to {target}")

        await client.goto(target, distance_threshold=0.15, target_yaw=0)
        start_time = time.time()
        while time.time() - start_time < 1:
            await client.goto(target, target_yaw=0)
            await asyncio.sleep(0.01)
        print(f"Going back")
        target_yaw = np.pi/2
        while True:
            await client.goto(target, target_yaw=target_yaw)
            start_time = time.time()
            while time.time() - start_time < 1.5:
                await client.goto(target, target_yaw=target_yaw)
                await asyncio.sleep(0.01)
            await client.goto(target, target_yaw=0)
            start_time = time.time()
            while time.time() - start_time < 1.5:
                await client.goto(target, target_yaw=0)
                await asyncio.sleep(0.01)
    elif behavior == "speed":
        height = 1.00
        x_offset = 1.5
        client.log_state_additional["in_trajectory"] = 1
        target = np.array([x_offset, 0, height])
        takeoff_target = initial_position + np.array([0, 0, height])
        distance_threshold = 0.15
        target_velocity = np.array([7, 0, 0])
        start_time = time.time()
        await client.goto(initial_position + np.array([0, 0, 0.3]), distance_threshold=0.15)
        await client.goto(initial_position + np.array([0, 0, 0.6]), distance_threshold=0.15)
        while time.time() - start_time < 3:
            await client.goto(takeoff_target, distance_threshold=0.15)
            await asyncio.sleep(0.01)
        print(f"Going to {target}")
        start_time = time.time()
        ramp = 1
        while abs(client.position[0] - target[0]) > distance_threshold:
            if time.time() - start_time < ramp:
                real_target_velocity = target_velocity * (time.time() - start_time) / ramp
            else:
                real_target_velocity = target_velocity
            if abs(client.position[0] - target[0]) < 1.5:
                real_target_velocity = np.array([0, 0, 0])
            print(f"Speeding to: {target} with velocity {real_target_velocity}")
            client.command(target, real_target_velocity)
            await asyncio.sleep(0.01)
        start_time = time.time()
        while time.time() - start_time < 3:
            await client.goto(target)
            await asyncio.sleep(0.01)
        while True:
            landing_target = target.copy()
            landing_target[2] = 0
            await client.goto(landing_target, distance_threshold=0.15)
            await asyncio.sleep(0.01)
    elif behavior == "crash":
        height = 0.83
        y_offset = 1.5 - 0.05
        client.log_state_additional["in_trajectory"] = 1
        target = np.array([0, y_offset, height])
        distance_threshold = 0.15
        target_velocity = [0, 3, 0]
        print(f"Going to {target}")
        while client.position[1] < target[1] - distance_threshold:
            client.command(target, target_velocity)
            await asyncio.sleep(0.01)
        while True:
            await client.goto([0, 0.5, height])


    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())