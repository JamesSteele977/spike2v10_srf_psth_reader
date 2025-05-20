import matplotlib.pyplot as plt
from typing import List, Tuple

import sys
sys.path.append(".")

from srf_reader import read_srf_psth

def plot_srf_contents(
        file_contents: List[Tuple[float, List[float]]], 
        bin_size: float=0.01, 
        t_min: float=0.0, 
        t_max: float=3.0) -> None:
    relative_event_times: List[float] = [event - sweep[0] 
        for sweep in file_contents 
        for event in sweep[1]
    ]
    plt.hist(relative_event_times, bins=int((t_max - t_min) / bin_size), range=(t_min, t_max), color="black", alpha=0.7)
    plt.xlabel("Time")
    plt.ylabel("Event Count")
    plt.savefig("./example/example.png")
    plt.show()

if __name__ == "__main__":
    srf_contents: List[Tuple[float, List[float]]] = read_srf_psth("./example/example.srf")
    plot_srf_contents(srf_contents)