import sys
import os
import threading
import webbrowser
import time
from flask import Flask, render_template, request, jsonify
from roundRobinAlgo import round_robin
from srtfAlgo import srtf
from priorityAlgo import preemptive_priority

# when PyInstaller bundles this into an exe, resources get extracted to a
# temporary folder pointed to by sys._MEIPASS; otherwise just use this file's folder
if getattr(sys, "frozen", False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, "templates"),
    static_folder=os.path.join(base_dir, "static"),
)


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


def open_browser():
    # small delay so Flask has time to actually start listening
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    app.run(port=5000, debug=False)