import re
import struct
from typing import List, Tuple, Dict

def read_srf_psth(srfpath: str) -> Tuple[Dict[str, float | int], List[Tuple[float, List[float]]]]:
    """ Read a .srf psth file from Spik2v10 and extract sweep/event times. 
    Args:
        srfpath (str): Path to the .srf file.
    Returns: 
        Dict[str, float | int]: File metadata in the format:
        {
            "N Bins Per Sweep" : int,
            "Bin Size (sec)" : float,
            "Offset (sec)" : float, 
            "Base Tick dt (sec)" : float
        }
        List[Tuple[float, List[float]]]: File contents in the format:
            [
                (sweep1_start_time, [sweep1_event_time_1, sweep1_event_time_2, ...]),
                (sweep2_start_time, [sweep2_event_time_1, sweep2_event_time_2, ...]),
                ...
                (sweepN_start_time, [sweepN_event_time_1, sweepN_event_time_2, ...])
            ]
        where trial_start_time is the time of sweep triggers (e.g. stimulus onset)
        and sweepN_event_time_M is the time of the Mth event in the Nth sweep (e.g. neuron APs)
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
        b"(.{12})"                                  # channel preamble: 12 bytes (sweep start time, sweep end time, unknown)
        b"\xff{16}\x00{36}\xff{16}"                 # channel header: ffff x 4 , .... x 9 , ffff x 4 
        b"((?:.{4})*?)"                             # body of channel containing event times
        b"(?=(?:.{12}\xff{16}\x00{36}\xff{16})|$)", # Next channel preamble/header or file end
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

            
