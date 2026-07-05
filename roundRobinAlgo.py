def round_robin(processes, quantum):
    """
    processes: list of dicts, each like:
        {"pid": "P1", "arrival_time": 0, "burst_time": 5}
    quantum: int, time slice per turn

    Returns a dict with:
        "gantt": list of {"pid": ..., "start": ..., "end": ...}
                 (pid is "IDLE" for any gap where the CPU has nothing to run)
        "table": list of {"pid", "arrival_time", "burst_time",
                           "start_time", "end_time", "turnaround_time", "waiting_time"}
    """

    # work on copies so we don't mutate the original input
    procs = []
    for p in processes:
        procs.append({
            "pid": p["pid"],
            "arrival_time": p["arrival_time"],
            "burst_time": p["burst_time"],
            "remaining_time": p["burst_time"],
            "start_time": None,  # set the first time this process actually runs
        })

    # sort by arrival time (then pid, for stable tie-breaking) so we know
    # the order they become "visible"
    procs.sort(key=lambda p: (p["arrival_time"], p["pid"]))

    n = len(procs)
    i = 0             # pointer into procs, tracks who has "arrived" already
    time = 0          # always start the clock at 0 so leading idle time shows up
    queue = []
    gantt = []
    completed = []

    # add any processes that arrive at time 0
    while i < n and procs[i]["arrival_time"] <= time:
        queue.append(procs[i])
        i += 1

    # keep going as long as there's something queued OR something still to arrive
    while queue or i < n:
        if not queue:
            # CPU is idle: nothing queued yet, jump forward to the next arrival
            next_arrival = procs[i]["arrival_time"]
            gantt.append({"pid": "IDLE", "start": time, "end": next_arrival})
            time = next_arrival
            while i < n and procs[i]["arrival_time"] <= time:
                queue.append(procs[i])
                i += 1
            continue

        current = queue.pop(0)

        if current["start_time"] is None:
            current["start_time"] = time

        slice_start = time
        run_time = min(quantum, current["remaining_time"])
        slice_end = slice_start + run_time

        gantt.append({"pid": current["pid"], "start": slice_start, "end": slice_end})

        current["remaining_time"] -= run_time
        time = slice_end

        # add any new arrivals that showed up during this slice
        while i < n and procs[i]["arrival_time"] <= time:
            queue.append(procs[i])
            i += 1

        if current["remaining_time"] > 0:
            queue.append(current)
        else:
            current["end_time"] = time
            completed.append(current)

    # build the results table
    table = []
    for p in completed:
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

    # keep table in original pid order for readability
    table.sort(key=lambda row: row["pid"])

    return {"gantt": gantt, "table": table}