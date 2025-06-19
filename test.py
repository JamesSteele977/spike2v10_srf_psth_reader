if __name__ == "__main__":
    from srf_reader import read_srf_psth
    
    for i in range(1, 3):
        print(f"\nTEST {i}")
        file_metadata, rasters = read_srf_psth(f"./tests/test{i}.srf")

        for key, value in file_metadata.items():
            print(f"\t{key}: {value}")
        print("\nRasters:")
        for sweep_start_time, event_times in rasters:
            print(f"\tSweep Start Time: {sweep_start_time:.6f} sec, Event Times: {event_times}")