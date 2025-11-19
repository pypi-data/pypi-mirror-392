import numpy as np

def circle(t, radius=1, z=1.5, duration=10, ramp_duration=0):
    time_velocity = min(t, ramp_duration) / ramp_duration if ramp_duration > 0 else 1
    ramp_time = time_velocity * min(t, ramp_duration) / 2
    progress = (ramp_time + max(0, t - ramp_duration)) * 2 * np.pi / duration
    
    d_progress = 2 * np.pi * time_velocity / duration
    
    x = radius * np.cos(progress)
    y = radius * np.sin(progress)

    vx = -radius * np.sin(progress) * d_progress
    vy = radius * np.cos(progress) * d_progress
    
    iteration = int(progress / (2 * np.pi))
    
    return np.array([x, y, z]), np.array([vx, vy, 0]), iteration