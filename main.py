from fastapi import FastAPI
import serial
import threading
import time

app = FastAPI()

SERIAL_PORT = '/dev/tty.usbserial-A60048RI'  # Change this to match your system
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
            if line == "hello":
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

@app.get("/move/a-to-b")
def move_a_to_b():
    return send_command("MOVE_A_TO_B")

@app.get("/move/b-to-a")
def move_b_to_a():
    return send_command("MOVE_B_TO_A")

@app.get("/rotate/{direction}/{degrees}")
def rotate_motor(direction: str, degrees: int):
    if direction not in ["forward", "backward"]:
        return {"error": "Invalid direction"}
    return send_command(f"ROTATE_{direction.upper()}_{degrees}")

@app.get("/arduino/status")
def check_status():
    return {"arduino_online": arduino_ready}
