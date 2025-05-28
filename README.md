# app-converge-wall-controller

A python script that provides a REST API for controlling a rising curtain by sending serial commands to Arduino.

Contains also Arduino code file (.ino) that can be flashed to Arduino using Arduino IDE.

# Install

pip install fastapi uvicorn pyserial

> You may want to create a python virtual environment and activate that first:
>
> python -m venv venv
>
> source venv/bin/activate

# Setup

1. Make all hardware connections, power up the system, and flash the CurtainStepper.ino to your Arduino.

2. Test that Arduino can control the curtain / stepper motor using Arduino IDE's serial console. Check the commands from CurtainStepper.ino, for example "up 3000".

3. Close serial console from Arduino IDE so that it does not reserve it anymore.

4. Find the name of the Arduino serial port.
- On Windows, typically COM5 or similar. 
- On Linux, typically /dev/tty/USB0 or /dev/ttyACM0 or similar. 
- On Mac, typically /dev/tty.usbmodem2101 or similar.

> You can also find that from Arduino IDE.

> On Mac and Linux, you can easily list them in console:
>
> ls /dev/tty.usb*

5. Edit the name of the serial port in main.py, for example on Mac:
SERIAL_PORT = '/dev/tty.usbmodem2101'

6. Depending on what HTTP ports are available, you may also need to edit start.sh, which sets HTTP port to 8600 by default.

7. Make sure that start.sh is runnable (chmod +x start.sh).

# Run

Just run ./start.sh

This will start a simple server that offers the REST API and relays commands to Arduino over serial port connection (over USB).

## Optional: Run as a service

There is a .service script that you can use for running the curtain controller as a service. The main benefit is that it will automatically start after PC reboot and also restarted in case it crashes, making the setup easier to use and more reliable.

> You can still plug in/out Arduino anytime you want, the service finds it from the specified serial port and starts to use it. You can use /ping endpoint to check remotely if Arduino is online.

sudo cp curtain.service /etc/systemd/system/curtain.service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable curtain.service
sudo systemctl start curtain.service

Check status:
sudo systemctl status curtain.service

View logs:
journalctl -u curtain.service -f

# Test

Test the REST API with CURL or browser. For example with curl:

curl -k http://localhost:8600/ping

Check if Arduino is online, should return "pong":
http://localhost:8600/ping

Check the status of the curtain, returns "up" or "down":
http://localhost:8600/status

Move curtain to "up" position. Also changes status to "up".
http://localhost:8600/move/up

Move curtain N steps upwards. Does not change curtain position status.
http://localhost:8600/move/up/5000

Move curtain to "down" position. Also changes status to "down".
http://localhost:8600/move/down

Move curtain N steps downwards. Does not change curtain position status.
http://localhost:8600/move/down/3200

Stop the motors. Notice: motors are always automatically released after movement ends.
http://localhost:8600/stop

Change the motor speed.
http://localhost:8600/speed/2000

Change the motor acceleration.
http://localhost:8600/accel/3000

# Tuning

Depending on your physical setup and curtain length, you need to find suitable values for default "up" and "down" commands and edit these to main.py, where the default is currently 10000.

```
@app.get("/move/up")
def move_up():
    return send_command("up 10000")

@app.get("/move/down")
def move_down():
    return send_command("down 10000")
```

> The idea is that curtain starts from "up" position, and "down" command rolls the curtain down up to the desired length. Then, "up" command should have the same value to roll it back up.
