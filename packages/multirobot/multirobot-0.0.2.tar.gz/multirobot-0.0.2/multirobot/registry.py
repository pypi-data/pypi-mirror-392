import numpy as np
import asyncio
import os
import math

VICON_IP = "192.168.1.3"
this_file_path = os.path.dirname(os.path.abspath(__file__))
configs = {
    "simulator_race": {
        "type": "simulator",
        "kwargs": {
            "parameter_path": os.path.join(this_file_path, "driver/simulator/parameters/race.json"),
            "initial_position": [0, 0, 0]
        },
    },
    "crazyflie_bl": {
        "type": "crazyflie",
        "kwargs": {"uri": "radio://0/80/2M/E7E7E7E7E9"},
        "mocap": "crazyflie_bl"
    },
    "crazyflie":{
        "type": "crazyflie",
        "kwargs": {"uri": "radio://0/80/2M/E7E7E7E7E7"},
        "mocap": "crazyflie",
    },
    "race": {
        "type": "px4",
        "kwargs": {"uri": "tcp:192.168.1.5:5760"},
        "mocap": "race_jonas",
    },
    "x500": {
        "type": "px4",
        "kwargs": {"uri": "tcp:192.168.1.5:5760"},
        "mocap": "x500_jonas",
    },
    "soft": {
        "type": "px4",
        "kwargs": {"uri": "tcp:192.168.1.10:5760"},
        "mocap": "soft",
    },
    "soft_rigid": {
        "type": "px4",
        "kwargs": {"uri": "tcp:192.168.1.16:5760"},
        "mocap": "soft_rigid",
    },
    "hummingbird": {
        "type": "betaflight",
        "kwargs": {"uri": "/dev/serial/by-name/elrs-transmitter2", "BAUD": 921600, "rate": 50, "odometry_source": "mocap"},
        "mocap": "hummingbird",
    },
    "savagebee_pusher": {
        "type": "betaflight",
        "kwargs": {"uri": "/dev/serial/by-name/elrs-transmitter1", "BAUD": 921600, "rate": 50, "odometry_source": "mocap"},
        "mocap": "savagebee_pusher",
    },
    "meteor75": {
        "type": "betaflight",
        "kwargs": {"uri": "/dev/serial/by-name/elrs-transmitter2", "BAUD": 921600, "rate": 200, "odometry_source": "mocap"},
        "mocap": "meteor75",
    },
    "pavo20": {
        "type": "betaflight",
        "kwargs": {"uri": "/dev/serial/by-name/elrs-transmitter2", "BAUD": 921600, "rate": 200, "odometry_source": "mocap"},
        "mocap": "pavo20",
    },
    "m5stampfly": {
        "type": "m5stampfly",
        "kwargs": {"uri": "/dev/serial/by-name/m5stamp-forwarder", "BAUD": 115200, "rate": 50, "odometry_source": "mocap"},
        "mocap": "m5stampfly",
    },
    "gazebo": {
        "type": "px4",
        "kwargs": {"uri": "udp:localhost:14540", "odometry_source": "feedback"},
        "mocap": "m5stampfly",
    },
}


def make_clients(mocap, configs):
    simulator_keys = [k for k in configs.keys() if configs[k]["type"] == "simulator"]
    crazyflie_keys = [k for k in configs.keys() if configs[k]["type"] == "crazyflie"]

    clients = {}
    if len(simulator_keys) > 0:
        from .driver.simulator.simulator import Simulator, SimulatedDrone
        simulator = Simulator(N_DRONES=2**(math.ceil(np.log2(len(simulator_keys)))))
        for key in simulator_keys:
            client = SimulatedDrone(simulator, name=key, **configs[key]["kwargs"])
            asyncio.create_task(client.run()),
            clients[key] = client
        asyncio.create_task(simulator.run())
    
    if len(crazyflie_keys) > 0:
        import cflib
        from multirobot.driver.crazyflie import swarm_factory
        cflib.crtp.init_drivers()
        crazyflie_configs = [configs[k] for k in crazyflie_keys]
        crazyflies = swarm_factory(crazyflie_keys, crazyflie_configs)
        for key, cfg, client in zip(crazyflie_keys, crazyflie_configs, crazyflies):
            mocap.add(cfg["mocap"], client._mocap_callback)
            client.learned_controller = True
            clients[key] = client
    
    for key in filter(lambda k: k not in simulator_keys and k not in crazyflie_keys, configs.keys()):
        cfg = configs[key]
        if cfg["type"] in ["px4", "betaflight", "m5stampfly"]:
            if cfg["type"] == "px4":
                from multirobot.driver.px4 import PX4
                type = PX4
            elif cfg["type"] == "betaflight":
                from multirobot.driver.betaflight import Betaflight
                type = Betaflight
            elif cfg["type"] == "m5stampfly":
                from multirobot.driver.m5stampfly import M5StampFly
                type = M5StampFly
            client = type(key, **cfg["kwargs"])
            mocap.add(cfg["mocap"], client._mocap_callback) if mocap is not None else None
            clients[key] = client

    
    return {k: clients[k] for k in configs.keys()}
    
    # elif backend == "px4":
    #     from px4 import PX4
    #     from mocap import Vicon
    #     VICON_IP = "192.168.1.3"
    #     mocap = Vicon(VICON_IP, VELOCITY_CLIP=5, EXPECTED_FRAMERATE=100)
    #     cfg = {
    #         "name": "race",
    #         "type": PX4,
    #         "kwargs": {"uri": "tcp:192.168.1.2:5760"},
    #         "mocap": "race_jonas",
    #     }
    #     asyncio.create_task(client.run()),
    #     print("Waiting for px4 position")
    #     while px4.position is None:
    #         await asyncio.sleep(0.1)
    #     initial_position = px4.position
    # elif backend == "crazyflie":
    #     from crazyflie import Crazyflie
    #     crazyflie_configs = [
    #         {
    #             "name": "crazyflie_bl",
    #             "type": Crazyflie,
    #             "kwargs": {"uri": "radio://0/80/2M/E7E7E7E7E9"},
    #             "mocap": "crazyflie_bl",
    #         },
    #         {
    #             "name": "crazyflie",
    #             "type": Crazyflie,
    #             "kwargs": {"uri": "radio://0/80/2M/E7E7E7E7E7"},
    #             "mocap": "crazyflie",
    #         },
    #     ]