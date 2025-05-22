from fastapi import FastAPI
import serial
import threading
import time

app = FastAPI()

SERIAL_PORT = '/dev/tty.usbmodem2101'  # Change this to match your system
BAUD_RATE = 115200

ser = None
arduino_ready = False
serial_lock = threading.Lock()

def open_serial():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        return True
    except Exception as e:
        print(f"Failed to open serial port: {e}")
        return False

def listen_to_arduino():
    global arduino_ready
    if not open_serial():
        return

    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if not arduino_ready and line.startswith("Hello"):
                arduino_ready = True
                print("Arduino is online")
            elif line:
                print(f"Arduino says: {line}")
        except Exception as e:
            print(f"Error reading from serial: {e}")
            arduino_ready = False
            break

threading.Thread(target=listen_to_arduino, daemon=True).start()

def send_command(command: str):
    global arduino_ready
    if not ser or not ser.is_open:
        return {"error": "Serial not connected"}
    try:
        with serial_lock:
            ser.write((command + '\n').encode())
            response = ser.readline().decode('utf-8').strip()
            return {"sent": command, "response": response}
    except Exception as e:
        arduino_ready = False
        return {"error": str(e)}

@app.get("/move/up")
def move_a_to_b():
    return send_command("up 10000")

@app.get("/move/down")
def move_b_to_a():
    return send_command("down 10000")

@app.get("/move/{direction}/{steps}")
def rotate_motor(direction: str, steps: int):
    if direction == "up":
        return send_command(f"up {steps}")
    elif direction == "down":
        return send_command(f"down {steps}")
    else:
        return {"error": "Invalid direction"}

@app.get("/stop")
def stop_motor():
    return send_command("stop")

@app.get("/speed/{speed}")
def set_speed(speed: int):
    if speed < 0 or speed > 5000:
        return {"error": "Speed must be between 0 and 5000"}
    return send_command(f"speed {speed}")

# Set acceleration and deceleration
@app.get("/accel/{accel}")
def set_acceleration(accel: int):
    if accel < 0 or accel > 5000:
        return {"error": "Acceleration must be between 0 and 5000"}
    return send_command(f"accel {accel}")

@app.get("/arduino/status")
def check_status():
    global arduino_ready
    if not ser or not ser.is_open:
        return {"error": "Serial not connected"}
    try:
        with serial_lock:
            ser.write(b'ping\n')
            response = ser.readline().decode('utf-8').strip()
            if response == "pong":
                return {"arduino_online": True}
            else:
                return {"arduino_online": False}
    except Exception as e:
        arduino_ready = False
        return {"error": str(e)}        
