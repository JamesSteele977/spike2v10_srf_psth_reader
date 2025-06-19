import re
import struct
from typing import List, Tuple, Dict

def read_srf_psth(srfpath: str) -> Tuple[Dict[str, float | int], List[Tuple[float, List[float]]]]:
    """
    Reads a .srf PSTH file from Spike2v10 and extracts sweep/event times.

    Args:
        srfpath: Path to the .srf file.

    Returns:
        A tuple containing:
            - metadata (dict): File metadata with the following keys:
                - "N Bins Per Sweep" (int)
                - "Bin Size (sec)" (float)
                - "Offset (sec)" (float)
                - "Base Tick dt (sec)" (float)
            - data (list): List of tuples, each containing:
                - sweep_start_time (float): Time of the sweep trigger (e.g., stimulus onset)
                - event_times (list of float): Times of events in the sweep (e.g., neuron APs)
    """
    with open(srfpath, "rb") as f:
        raw_bytes: bytes = f.read()

    file_metadata: Dict[str, float | int] = {
        "N Bins Per Sweep": int.from_bytes(raw_bytes[8:12], byteorder="little", signed=False),
        "Bin Size (sec)": struct.unpack("<d", raw_bytes[16:24])[0],
        "Offset (sec)": struct.unpack("<d", raw_bytes[24:32])[0],
        "Base Tick dt (sec)": struct.unpack("<d", raw_bytes[40:48])[0]
    }

    SWEEP_PATTERN: re.Pattern = re.compile(
        b"(.{12})"                                      # channel preamble: 12 bytes (sweep start time, sweep end time, unknown)
        b"\xff{16}.{2}\x00{34}\xff{16}"                 # channel header: ffff x 4 , .... x 9 , ffff x 4 
        b"((?:.{4})*?)"                                 # body of channel containing event times
        b"(?=(?:.{12}\xff{16}.{2}\x00{34}\xff{16})|$)", # Next channel preamble/header or file end
        re.DOTALL
    )

    file_contents: List[Tuple[float, List[float]]] = []
    for offset in range(64, len(raw_bytes), 4): # start at bottom of header, jump 4 bytes for 32-bit encoding 
        
        match: re.Match | None = SWEEP_PATTERN.match(raw_bytes, offset) 
        if match:
            
            # Decode event times
            event_times: List[float] = []
            capture: bytes = match.group(2)
            for capture_offset in range(0, len(capture), 4):
                event_times.append(int.from_bytes(capture[capture_offset:capture_offset + 4], byteorder="little", signed=False) * file_metadata["Base Tick dt (sec)"])
            
            # Decode sweep start time
            sweep_time: float = int.from_bytes(match.group(1)[:4], byteorder="little", signed=False) * file_metadata["Base Tick dt (sec)"]
            file_contents.append((sweep_time, event_times))
    
    return file_metadata, file_contents

            
