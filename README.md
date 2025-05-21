# app-converge-wall-controller
A python script that provides a REST API for controlling a moving wall by sending serial commands to Arduino

# Install

pip install fastapi uvicorn pyserial

# Setup

Find Arduino serial port on Mac:
ls /dev/tty.usb*

# Run

Just run ./start.sh

> Modify serial port and http port in main.py if necessary!

# Test

Test with CURL or browser:

http://localhost:8000/arduino/status

http://localhost:8000/move/a-to-b
http://localhost:8000/move/b-to-a

http://localhost:8000/rotate/forward/90
http://localhost:8000/rotate/backward/120

