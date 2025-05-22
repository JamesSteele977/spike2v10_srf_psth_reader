import re
from typing import List, Tuple

def decode_chunk_to_seconds(chunk: bytes, spike2v10_max_fs: float=5e5, return_ticks: bool=False) -> int | float:
    """ Decode a 4-byte chunk from the .srf file into a float (seconds or ticks). 
    32-bit unsigned integer gives channel ticks of event times.
    Args:
        chunk (bytes): 4-byte chunk from the .srf file.
        spike2v10_max_fs (float): Maximum sampling frequency of Spike2 v10. Default is 5e5.
        return_ticks (bool): If True, return raw ticks instead of seconds. Default is False. 
    Returns:
        int | float: Decoded value in ticks or seconds. 
    """
    u32: int = int.from_bytes(chunk, byteorder="little", signed=False)
    if return_ticks:
        return u32
    return u32 / spike2v10_max_fs

def read_srf_psth(srfpath: str) -> List[Tuple[float, List[float]]]:
    """ Read a .srf psth file from Spik2v10 and extract sweep/event times. 
    Args:
        srfpath (str): Path to the .srf file.
    Returns: 
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

    SWEEP_PATTERN: re.Pattern = re.compile(
        b"(.{12})"                                  # channel preamble: 12 bytes (sweep start time, sweep end time, unknown)
        b"\xff{16}\x00{36}\xff{16}"                 # channel header: ffff x 4 , .... x 9 , ffff x 4 
        b"((?:.{4})*?)"                             # body of channel containing event times
        b"(?=(?:.{12}\xff{16}\x00{36}\xff{16})|$)", # Next channel preamble/header or file end
        re.DOTALL
    )

    file_contents: List[Tuple[float, List[float]]] = []
    for offset in range(0, len(raw_bytes), 4): # jump 4 bytes for 32-bit encoding 
        
        match: re.Match | None = SWEEP_PATTERN.match(raw_bytes, offset) 
        if match:
            
            # Decode event times
            event_times: List[float] = []
            capture: bytes = match.group(2)
            for capture_offset in range(0, len(capture), 4):
                event_times.append(decode_chunk_to_seconds(capture[capture_offset:capture_offset + 4]))
            
            # Decode sweep start time
            sweep_time: float = decode_chunk_to_seconds(match.group(1)[:4])
            file_contents.append((sweep_time, event_times))
    
    return file_contents

            
