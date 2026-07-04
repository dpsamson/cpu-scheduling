from flask import Flask, render_template, request, jsonify
from roundRobinAlgo import round_robin
from srtfAlgo import srtf
from priorityAlgo import preemptive_priority

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/schedule/round-robin", methods=["POST"])
def schedule_round_robin():
    data = request.get_json()

    processes = data.get("processes", [])
    quantum = data.get("quantum")

    if not processes or not quantum:
        return jsonify({"error": "Missing processes or quantum"}), 400

    result = round_robin(processes, quantum)
    return jsonify(result)


@app.route("/schedule/srtf", methods=["POST"])
def schedule_srtf():
    data = request.get_json()

    processes = data.get("processes", [])

    if not processes:
        return jsonify({"error": "Missing processes"}), 400

    result = srtf(processes)
    return jsonify(result)


@app.route("/schedule/priority", methods=["POST"])
def schedule_priority():
    data = request.get_json()

    processes = data.get("processes", [])

    if not processes:
        return jsonify({"error": "Missing processes"}), 400

    if any("priority" not in p for p in processes):
        return jsonify({"error": "Each process must include a priority value"}), 400

    result = preemptive_priority(processes)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)