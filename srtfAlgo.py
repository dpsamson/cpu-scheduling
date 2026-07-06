def srtf(processes):
    
    procs = []
    for p in processes:
        procs.append({
            "pid": p["pid"],
            "arrival_time": p["arrival_time"],
            "burst_time": p["burst_time"],
            "remaining_time": p["burst_time"],
            "start_time": None,  # set the first time this process actually runs
            "end_time": None,
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

        if chosen["start_time"] is None:
            chosen["start_time"] = time

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
            chosen["end_time"] = time
            completed_count += 1
            current_pid = None  # force a new Gantt segment for whoever runs next

    # build the results table
    table = []
    for p in procs:
        turnaround_time = p["end_time"] - p["arrival_time"]
        waiting_time = turnaround_time - p["burst_time"]
        table.append({
            "pid": p["pid"],
            "arrival_time": p["arrival_time"],
            "burst_time": p["burst_time"],
            "start_time": p["start_time"],
            "end_time": p["end_time"],
            "turnaround_time": turnaround_time,
            "waiting_time": waiting_time,
        })

    table.sort(key=lambda row: row["pid"])

    return {"gantt": gantt, "table": table}