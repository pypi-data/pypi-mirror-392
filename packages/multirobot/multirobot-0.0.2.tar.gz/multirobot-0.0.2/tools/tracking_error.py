#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import os


XY_ONLY = False

def main():
    for csv_path in sys.argv[1:]:
        csv_file = Path(csv_path)
    
        if not csv_file.exists():
            print(f"Error: File {csv_file} does not exist")
            sys.exit(1)
        
        df = pd.read_csv(csv_file)
        # mask = np.array(df["in_trajectory"] == 1) & np.array(df["trigga"] == 1)
        mask = np.array(df["in_trajectory"] == 1)
        position = np.array(df[['x', 'y', 'z']])[mask]
        target_position = np.array(df[['target_x', 'target_y', 'target_z']])[mask]
        if XY_ONLY:
            position[:, 2] = 0.0
            target_position[:, 2] = 0.0
        error = position - target_position
        error = np.linalg.norm(error, axis=1)
        print(f"{csv_path} Mean norm: {error.mean()}")
        plt.plot(target_position[:, 0], target_position[:, 1], "r")
        plt.plot(position[:, 0], position[:, 1], "b")
        plt.xlabel("x [m]")
        plt.ylabel("y [m]")
        plt.savefig(f"{csv_path}_{error.mean():.4f}.pdf")
        # plt.title(f"{os.path.basename(csv_path)}: avg error: {error.mean()} m")
        plt.show()

        

if __name__ == "__main__":
    main()
