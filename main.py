import firebase_admin
from firebase_admin import credentials, db
import serial
import time
import re
import threading
from serial.tools import list_ports
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

arduino = None

# Keys must match Firebase exactly: tv, aircon, lights, lamp, fan
device_status = {
    "tv":     "off",
    "aircon": "off",
    "lights": "off",
    "lamp":   "off",
}

current_temp = None
_ignore_next = set()  # Prevents listener echo loop


# ==============================
# FIREBASE INITIALIZATION
# ==============================
def initialize_firebase():
    cred = credentials.Certificate('key.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://elective-6fafb-default-rtdb.firebaseio.com/'
    })
    print("Firebase Connected ✅")


# ==============================
# AUTO DETECT ARDUINO
# ==============================
def auto_detect_arduino():
    ports = list_ports.comports()
    for port in ports:
        print("Checking:", port.device, "-", port.description)
        if "Arduino" in port.description or "CH340" in port.description:
            return port.device
    for port in ports:
        if port.vid is not None:
            return port.device
    return None


# ==============================
# CONNECT TO ARDUINO
# ==============================
def connect_arduino():
    global arduino
    port = auto_detect_arduino()
    if not port:
        print("No Arduino detected")
        return
    try:
        arduino = serial.Serial(port, 9600, timeout=1)
        time.sleep(3)
        arduino.reset_input_buffer()
        print("Arduino Connected on", port, "✅")
    except Exception as e:
        print("Connection error:", e)


# ==============================
# SEND COMMAND TO ARDUINO
# ==============================
def send_to_arduino(command):
    global arduino
    try:
        if arduino and arduino.is_open:
            arduino.write((command + "\n").encode())
            print("Sent to Arduino:", command)
        else:
            print("Arduino not connected.")
    except Exception as e:
        print("Send error:", e)


# ==============================
# FIREBASE WRITE (marks echo to skip)
# ==============================
def firebase_set(path, value):
    _ignore_next.add(path)
    db.reference(path).set(value)


# ==============================
# READ TEMPERATURE
# ==============================
def read_temperature():
    global arduino
    try:
        if not arduino or not arduino.is_open:
            return None

        arduino.reset_input_buffer()
        arduino.write(b'get_temp\n')

        # Try up to 5 lines to find a valid temperature reading
        for attempt in range(5):
            time.sleep(0.5)
            data = arduino.readline().decode('utf-8', errors='ignore').strip()
            if not data:
                continue

            print(f"Received (attempt {attempt+1}): {data}")

            # Extract all numbers (floats preferred over ints)
            floats = re.findall(r"[-+]?\d+\.\d+", data)
            ints   = re.findall(r"[-+]?\d+", data)

            candidates = [float(x) for x in floats] + [float(x) for x in ints]

            for val in candidates:
                # Valid room temp: between 10°C and 60°C
                if 10.0 <= val <= 60.0:
                    print(f"Valid temp: {val}")
                    return val

            print(f"  Skipped invalid value(s): {candidates}")

        print("No valid temperature found after 5 attempts")
        return None

    except Exception as e:
        print("Temp error:", e)
        return None


# ==============================
# ARDUINO COMMAND MAP
# Adjust these strings to match your Arduino sketch
# ==============================
ARDUINO_COMMANDS = {
    "tv":     {"on": "tvon",      "off": "tvoff"},
    "aircon": {"on": "airconon",  "off": "airconoff"},
    "lights": {"on": "lightson",  "off": "lightsoff"},
    "lamp":   {"on": "lampon",    "off": "lampoff"},
}


# ==============================
# APPLY DEVICE (shared logic)
# ==============================
def apply_device(name, state):
    global device_status
    if name not in device_status:
        print(f"Unknown device: {name}")
        return
    cmd = ARDUINO_COMMANDS[name][state]
    send_to_arduino(cmd)
    device_status[name] = state
    firebase_set(f"status/{name}", state)
    print(f"[apply_device] {name} -> {state} | cmd={cmd} | Firebase updated")


def apply_all(state):
    send_to_arduino("allon" if state == "on" else "alloff")
    for k in list(device_status.keys()):
        device_status[k] = state
        firebase_set(f"status/{k}", state)
    print(f"[apply_all] all -> {state} | Firebase updated")


# ==============================
# FIREBASE LISTENER
# ==============================
def firebase_listener(event):
    path  = event.path
    value = event.data
    print(f"Firebase event path={path} value={value}")

    if value is None:
        return

    # Skip echoes from our own writes
    full_path = f"status{path}"
    if full_path in _ignore_next:
        _ignore_next.discard(full_path)
        print(f"  Skipped self-write echo: {full_path}")
        return

    # Startup full snapshot - skip
    if path == "/" and isinstance(value, dict):
        print("  Startup snapshot ignored")
        return

    # Voice command
    if path == "/command":
        voice_commands = {
            "turn on all devices":  ("all",    "on"),
            "turn off all devices": ("all",    "off"),
            "turn on the tv":       ("tv",     "on"),
            "turn off the tv":      ("tv",     "off"),
            "turn on the aircon":   ("aircon", "on"),
            "turn off the aircon":  ("aircon", "off"),
            "turn on the lights":   ("lights", "on"),
            "turn off the lights":  ("lights", "off"),
            "turn on the lamp":     ("lamp",   "on"),
            "turn off the lamp":    ("lamp",   "off"),
        }
        if value in voice_commands:
            target, state = voice_commands[value]
            if target == "all":
                apply_all(state)
            else:
                apply_device(target, state)
        return

    # Individual device path: /tv /lights /lamp /fan
    device = path.lstrip("/")
    if device in device_status and value in ("on", "off"):
        cmd = ARDUINO_COMMANDS[device][value]
        send_to_arduino(cmd)
        device_status[device] = value
        print(f"  External set {device} -> {value} | cmd={cmd}")


# ==============================
# TEMPERATURE LOOP
# ==============================
def temperature_loop():
    global current_temp
    while True:
        temp = read_temperature()
        if temp is not None:
            current_temp = temp
            db.reference("status/temp").set(temp)
            print("Temperature Updated:", temp)
        time.sleep(5)


# ==============================
# SERVE FRONTEND
# ==============================
@app.route('/')
def index():
    return app.send_static_file('index.html')


# ==============================
# FLASK API ROUTES
# ==============================

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "devices":           device_status,
        "temperature":       current_temp,
        "arduino_connected": arduino is not None and arduino.is_open
    })


@app.route('/api/device/<device_name>', methods=['POST'])
def control_device(device_name):
    data  = request.get_json()
    state = data.get("state", "").lower()

    if state not in ("on", "off"):
        return jsonify({"error": "Invalid state. Use 'on' or 'off'"}), 400

    if device_name not in device_status:
        return jsonify({"error": f"Unknown device: {device_name}"}), 404

    apply_device(device_name, state)
    return jsonify({"device": device_name, "state": state, "firebase": "updated"})


@app.route('/api/all', methods=['POST'])
def control_all():
    data  = request.get_json()
    state = data.get("state", "").lower()

    if state not in ("on", "off"):
        return jsonify({"error": "Invalid state"}), 400

    apply_all(state)
    return jsonify({"all_devices": state, "firebase": "updated"})


@app.route('/api/temperature', methods=['GET'])
def get_temperature():
    return jsonify({"temperature": current_temp})


# ==============================
# MAIN PROGRAM
# ==============================
if __name__ == "__main__":
    initialize_firebase()
    connect_arduino()

    # Sync Firebase -> local on startup
    snapshot = db.reference("status").get()
    if snapshot and isinstance(snapshot, dict):
        for k in device_status:
            if k in snapshot and snapshot[k] in ("on", "off"):
                device_status[k] = snapshot[k]
        print("Startup sync from Firebase:", device_status)

    # Firebase listener thread
    threading.Thread(
        target=lambda: db.reference("status").listen(firebase_listener),
        daemon=True
    ).start()
    print("Listening to Firebase... 📡")

    # Temperature loop thread
    threading.Thread(target=temperature_loop, daemon=True).start()

    print("Starting Flask on http://0.0.0.0:5000 🚀")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)