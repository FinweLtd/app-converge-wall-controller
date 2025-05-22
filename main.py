from fastapi import FastAPI
import serial
import threading
import time

from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import HTTPException

app = FastAPI()

SERIAL_PORT = '/dev/tty.usbmodem2101'  # Update to match your device
BAUD_RATE = 115200
RECONNECT_INTERVAL = 5  # Seconds

ser = None
arduino_ready = False
serial_lock = threading.Lock()

def try_open_serial():
    global ser
    try:
        s = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to boot/reset
        print(f"[INFO] Serial port {SERIAL_PORT} opened")
        return s
    except Exception as e:
        print(f"[WARN] Failed to open serial port: {e}")
        return None

def listen_to_arduino():
    global ser, arduino_ready
    buffer = ""

    while True:
        if not ser or not ser.is_open:
            ser = try_open_serial()
            arduino_ready = False
            buffer = ""

        if ser:
            try:
                # Read whatever is available
                chunk = ser.read(ser.in_waiting or 1).decode('utf-8', errors='ignore')
                if chunk:
                    buffer += chunk
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            print(f"[Serial] {line}")
                            if not arduino_ready and line.startswith("Hello"):
                                arduino_ready = True
                                print("[INFO] Arduino is online")
            except Exception as e:
                print(f"[ERROR] Serial read failed: {e}")
                try:
                    ser.close()
                except:
                    pass
                ser = None
                arduino_ready = False

        time.sleep(0.01 if ser else RECONNECT_INTERVAL)

def read_serial_line(timeout=2.0):
    start = time.time()
    buffer = ""
    while time.time() - start < timeout:
        try:
            chunk = ser.read(ser.in_waiting or 1).decode('utf-8', errors='ignore')
            if chunk:
                buffer += chunk
                if '\n' in buffer:
                    line, _ = buffer.split('\n', 1)
                    return line.strip()
        except Exception as e:
            break
    return None

def send_command(command: str):
    global ser, arduino_ready
    if not ser or not ser.is_open:
        return {"error": "Serial not connected"}
    try:
        with serial_lock:
            ser.write((command + '\n').encode())
            response = read_serial_line()
            if response:
                return {"sent": command, "response": response}
            else:
                return {"sent": command, "error": "No response from Arduino"}
            
    except Exception as e:
        print(f"[ERROR] Failed to write/read: {e}")
        arduino_ready = False
        try:
            ser.close()
        except:
            pass
        ser = None
        return {"error": str(e)}

# Start listener thread
threading.Thread(target=listen_to_arduino, daemon=True).start()

# === REST API Endpoints ===

@app.get("/move/up")
def move_up():
    return send_command("up 10000")

@app.get("/move/down")
def move_down():
    return send_command("down 10000")

@app.get("/move/{direction}/{steps}")
def move(direction: str, steps: int):
    if direction not in ("up", "down"):
        return {"error": "Invalid direction"}
    return send_command(f"{direction} {steps}")

@app.get("/stop")
def stop():
    return send_command("stop")

@app.get("/speed/{speed}")
def set_speed(speed: int):
    if not 0 <= speed <= 5000:
        return {"error": "Speed must be between 0 and 5000"}
    return send_command(f"speed {speed}")

@app.get("/accel/{accel}")
def set_accel(accel: int):
    if not 0 <= accel <= 5000:
        return {"error": "Acceleration must be between 0 and 5000"}
    return send_command(f"accel {accel}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": f"{type(exc).__name__}: {str(exc)}"},
    )
