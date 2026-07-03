def round_robin(processes, quantum):
    """
    processes: list of dicts, each like:
        {"pid": "P1", "arrival_time": 0, "burst_time": 5}
    quantum: int, time slice per turn

    Returns a dict with:
        "gantt": list of {"pid": ..., "start": ..., "end": ...}
        "table": list of {"pid", "arrival_time", "burst_time",
                           "completion_time", "turnaround_time", "waiting_time"}
    """

    # work on copies so we don't mutate the original input
    procs = []
    for p in processes:
        procs.append({
            "pid": p["pid"],
            "arrival_time": p["arrival_time"],
            "burst_time": p["burst_time"],
            "remaining_time": p["burst_time"],
        })

    # sort by arrival time so we know the order they become "visible"
    procs.sort(key=lambda p: p["arrival_time"])

    time = 0
    queue = []
    gantt = []
    completed = []
    i = 0  # pointer into procs, tracks who has "arrived" already
    n = len(procs)

    # start the clock at the first process' arrival time
    if procs:
        time = procs[0]["arrival_time"]

    # add any processes that arrive at time 0 (or the starting time)
    while i < n and procs[i]["arrival_time"] <= time:
        queue.append(procs[i])
        i += 1

    while queue:
        current = queue.pop(0)

        # if this process hasn't started yet and there's a gap, jump time forward
        start_time = max(time, current["arrival_time"])
        run_time = min(quantum, current["remaining_time"])
        end_time = start_time + run_time

        gantt.append({"pid": current["pid"], "start": start_time, "end": end_time})

        current["remaining_time"] -= run_time
        time = end_time

        # add any new arrivals that showed up during this slice
        while i < n and procs[i]["arrival_time"] <= time:
            queue.append(procs[i])
            i += 1

        if current["remaining_time"] > 0:
            queue.append(current)
        else:
            current["completion_time"] = time
            completed.append(current)


    # build the results table
    table = []
    for p in completed:
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

    # keep table in original pid order for readability
    table.sort(key=lambda row: row["pid"])

    return {"gantt": gantt, "table": table}


if __name__ == "__main__":
    # quick manual test
    test_processes = [
        {"pid": "P1", "arrival_time": 0, "burst_time": 5},
        {"pid": "P2", "arrival_time": 1, "burst_time": 3},
        {"pid": "P3", "arrival_time": 2, "burst_time": 1},
    ]
    result = round_robin(test_processes, quantum=2)
    print("Gantt Chart:")
    for seg in result["gantt"]:
        print(f"  {seg['pid']}: {seg['start']} -> {seg['end']}")
    print("\nTable:")
    for row in result["table"]:
        print(row)