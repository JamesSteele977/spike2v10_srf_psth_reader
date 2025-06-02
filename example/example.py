import matplotlib.pyplot as plt
from typing import List, Tuple, Dict

import sys
sys.path.append(".")

from srf_reader import read_srf_psth

def plot_srf_contents(
        file_metadata: Dict[str, float | int],
        file_contents: List[Tuple[float, List[float]]]
    ) -> None:
    relative_event_times: List[float] = [event - sweep[0] 
        for sweep in file_contents 
        for event in sweep[1]
    ]
    bins: List[float] = [
        x * file_metadata["Bin Size (sec)"] + file_metadata["Offset (sec)"] 
        for x in range(0, file_metadata["N Bins Per Sweep"] + 1) #type: ignore
    ]
    plt.hist(relative_event_times, bins=bins, color="black", alpha=0.7)
    plt.xlabel("Time")
    plt.ylabel("Event Count")
    plt.title(f"Base Tick fs: {int(1 / file_metadata['Base Tick dt (sec)'])} tick/sec, N Sweeps: {len(file_contents)}") #type: ignore
    plt.savefig("./example/example.png")
    plt.show()

if __name__ == "__main__":
    file_metadata: Dict[str, float | int]
    srf_contents: List[Tuple[float, List[float]]] 
    file_metadata, srf_contents = read_srf_psth("./example/example.srf")
    plot_srf_contents(file_metadata, srf_contents)