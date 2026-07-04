def srtf(processes):
    """
    processes: list of dicts, each like:
        {"pid": "P1", "arrival_time": 0, "burst_time": 5}

    Returns a dict with:
        "gantt": list of {"pid": ..., "start": ..., "end": ...}
                 (pid is "IDLE" for any gap where the CPU has nothing to run)
        "table": list of {"pid", "arrival_time", "burst_time",
                           "completion_time", "turnaround_time", "waiting_time"}
    """

    procs = []
    for p in processes:
        procs.append({
            "pid": p["pid"],
            "arrival_time": p["arrival_time"],
            "burst_time": p["burst_time"],
            "remaining_time": p["burst_time"],
            "completion_time": None,
        })

    n = len(procs)
    completed_count = 0
    time = 0  # always start at 0 so leading idle time is captured

    gantt = []
    current_pid = None  # which "lane" ran during the previous tick (a pid, or "IDLE")

    while completed_count < n:
        # gather all processes that have arrived and still have work left
        available = [p for p in procs if p["arrival_time"] <= time and p["remaining_time"] > 0]

        if not available:
            # CPU idle: record/extend an IDLE segment instead of silently skipping
            if current_pid == "IDLE" and gantt:
                gantt[-1]["end"] += 1
            else:
                gantt.append({"pid": "IDLE", "start": time, "end": time + 1})
            current_pid = "IDLE"
            time += 1
            continue

        # pick the process with the smallest remaining time
        # ties broken by arrival time, then pid, to keep results consistent
        chosen = min(available, key=lambda p: (p["remaining_time"], p["arrival_time"], p["pid"]))

        # run the chosen process for exactly 1 time unit
        if chosen["pid"] == current_pid and gantt:
            # same process as last tick, just extend the last Gantt segment
            gantt[-1]["end"] += 1
        else:
            # different process, start a new Gantt segment
            gantt.append({"pid": chosen["pid"], "start": time, "end": time + 1})

        chosen["remaining_time"] -= 1
        current_pid = chosen["pid"]
        time += 1

        if chosen["remaining_time"] == 0:
            chosen["completion_time"] = time
            completed_count += 1
            current_pid = None  # force a new Gantt segment for whoever runs next

    # build the results table
    table = []
    for p in procs:
        turnaround_time = p["completion_time"] - p["arrival_time"]
        waiting_time = turnaround_time - p["burst_time"]
        table.append({
            "pid": p["pid"],
            "arrival_time": p["arrival_time"],
            "burst_time": p["burst_time"],
            "completion_time": p["completion_time"],
            "turnaround_time": turnaround_time,
            "waiting_time": waiting_time,
        })

    table.sort(key=lambda row: row["pid"])

    return {"gantt": gantt, "table": table}


if __name__ == "__main__":
    test_processes = [
        {"pid": "P1", "arrival_time": 2, "burst_time": 8},
        {"pid": "P2", "arrival_time": 3, "burst_time": 4},
        {"pid": "P3", "arrival_time": 4, "burst_time": 9},
        {"pid": "P4", "arrival_time": 5, "burst_time": 5},
    ]
    result = srtf(test_processes)
    print("Gantt Chart:")
    for seg in result["gantt"]:
        print(f"  {seg['pid']}: {seg['start']} -> {seg['end']}")
    print("\nTable:")
    for row in result["table"]:
        print(row)