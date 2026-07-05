const processRows = document.getElementById("process-rows");
const addRowBtn = document.getElementById("add-row-btn");
const runBtn = document.getElementById("run-btn");
const ganttChart = document.getElementById("gantt-chart");
const ganttRuler = document.getElementById("gantt-ruler");
const resultsRows = document.getElementById("results-rows");
const averagesEl = document.getElementById("averages");

const algorithmSelect = document.getElementById("algorithm");
const quantumField = document.getElementById("quantum-field");
const priorityHeaderCells = document.querySelectorAll(".priority-col");

function updateFormForAlgorithm() {
  const algorithm = algorithmSelect.value;

  quantumField.style.display = algorithm === "round-robin" ? "flex" : "none";

  const showPriority = algorithm === "priority";
  priorityHeaderCells.forEach(cell => {
    cell.style.display = showPriority ? "" : "none";
  });
  document.querySelectorAll(".priority-input-cell").forEach(cell => {
    cell.style.display = showPriority ? "" : "none";
  });
}

algorithmSelect.addEventListener("change", updateFormForAlgorithm);
updateFormForAlgorithm();

let processCount = 0;

function addProcessRow() {
  processCount++;
  const row = document.createElement("tr");
  const showPriority = algorithmSelect.value === "priority";
  row.innerHTML = `
    <td>P${processCount}</td>
    <td><input type="number" class="arrival-input" min="0" value="0"></td>
    <td><input type="number" class="burst-input" min="1" value="1"></td>
    <td class="priority-input-cell" style="display: ${showPriority ? "" : "none"}">
      <input type="number" class="priority-input" min="1" value="1">
    </td>
    <td><button class="remove-row-btn">x</button></td>
  `;
  row.querySelector(".remove-row-btn").addEventListener("click", () => {
    row.remove();
  });
  processRows.appendChild(row);
}

addRowBtn.addEventListener("click", addProcessRow);

// start with 2 rows by default
addProcessRow();
addProcessRow();
updateFormForAlgorithm();

function collectProcesses() {
  const rows = processRows.querySelectorAll("tr");
  const processes = [];
  rows.forEach((row, index) => {
    const arrival = parseInt(row.querySelector(".arrival-input").value);
    const burst = parseInt(row.querySelector(".burst-input").value);
    const priority = parseInt(row.querySelector(".priority-input").value);
    processes.push({
      pid: `P${index + 1}`,
      arrival_time: arrival,
      burst_time: burst,
      priority: priority,
    });
  });
  return processes;
}

// consistent color per PID, assigned in order of first appearance
const PALETTE = ["#e0a458", "#6fcf97", "#7fb2e0", "#d9695f", "#b98fd6", "#e0d158"];
const pidColors = {};
let colorIndex = 0;

function colorForPid(pid) {
  if (pid === "IDLE") {
    return "#3a4642"; // muted graphite, visually distinct from process colors
  }
  if (!pidColors[pid]) {
    pidColors[pid] = PALETTE[colorIndex % PALETTE.length];
    colorIndex++;
  }
  return pidColors[pid];
}

const UNIT_WIDTH = 40; // px per time unit

function renderGanttChart(gantt) {
  ganttChart.innerHTML = "";
  ganttRuler.innerHTML = "";

  gantt.forEach(seg => {
    const duration = seg.end - seg.start;

    const block = document.createElement("div");
    block.classList.add("gantt-block");
    if (seg.pid === "IDLE") {
      block.classList.add("gantt-block-idle");
    }
    block.style.width = `${duration * UNIT_WIDTH}px`;
    block.style.background = colorForPid(seg.pid);
    block.textContent = seg.pid;
    ganttChart.appendChild(block);

    const tick = document.createElement("div");
    tick.classList.add("gantt-tick");
    tick.style.width = `${duration * UNIT_WIDTH}px`;
    tick.textContent = seg.start;
    ganttRuler.appendChild(tick);
  });

  // final tick marking the end of the whole timeline
  if (gantt.length > 0) {
    const lastEnd = gantt[gantt.length - 1].end;
    const endTick = document.createElement("div");
    endTick.classList.add("gantt-tick");
    endTick.style.width = "0px";
    endTick.textContent = lastEnd;
    ganttRuler.appendChild(endTick);
  }
}

function renderTable(table) {
  resultsRows.innerHTML = "";
  let totalWaiting = 0;
  let totalTurnaround = 0;
  const showPriority = algorithmSelect.value === "priority";

  table.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.pid}</td>
      <td>${row.arrival_time}</td>
      <td>${row.burst_time}</td>
      <td class="priority-col" style="display: ${showPriority ? "" : "none"}">${row.priority ?? ""}</td>
      <td>${row.start_time}</td>
      <td>${row.end_time}</td>
      <td>${row.turnaround_time}</td>
      <td>${row.waiting_time}</td>
    `;
    resultsRows.appendChild(tr);
    totalWaiting += row.waiting_time;
    totalTurnaround += row.turnaround_time;
  });

  const avgWaiting = (totalWaiting / table.length).toFixed(2);
  const avgTurnaround = (totalTurnaround / table.length).toFixed(2);
  averagesEl.textContent = `Average Waiting Time: ${avgWaiting}ms | Average Turnaround Time: ${avgTurnaround}ms`;
}

runBtn.addEventListener("click", async () => {
  const processes = collectProcesses();
  const algorithm = algorithmSelect.value;

  let endpoint = "";
  let payload = { processes };

  if (algorithm === "round-robin") {
    endpoint = "/schedule/round-robin";
    payload.quantum = parseInt(document.getElementById("quantum").value);
  } else if (algorithm === "srtf") {
    endpoint = "/schedule/srtf";
  } else if (algorithm === "priority") {
    endpoint = "/schedule/priority";
  }

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const err = await response.json();
      alert(err.error || "Something went wrong");
      return;
    }

    const result = await response.json();
    renderGanttChart(result.gantt);
    renderTable(result.table);
  } catch (error) {
    console.error("Error running scheduler:", error);
    alert("Could not reach the server.");
  }
});