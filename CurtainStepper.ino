#include <AccelStepper.h>

// === Constants ===
const int DIR_PIN = 5;
const int STEP_PIN = 2;
const int ENABLE_PIN = 8;
const float DEFAULT_MAX_SPEED = 1500.0;
const float DEFAULT_ACCELERATION = 1600.0;

AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

// === Globals ===
bool serialReady = false;
String inputBuffer = "";
bool motorEnabled = false;

void enableMotor() {
  digitalWrite(ENABLE_PIN, LOW); // Enable DRV8825
  motorEnabled = true;
}

void disableMotor() {
  digitalWrite(ENABLE_PIN, HIGH); // Disable DRV8825 (motor released)
  motorEnabled = false;
}

void setup() {
  stepper.setMaxSpeed(DEFAULT_MAX_SPEED);
  stepper.setAcceleration(DEFAULT_ACCELERATION);

  pinMode(ENABLE_PIN, OUTPUT);
  disableMotor();  // Start with motors disabled

  Serial.begin(115200);

  // Wait until Serial is connected (USB serial)
  while (!Serial) {
    delay(10);
  }

  serialReady = true;
  Serial.println("Hello from Curtain Controller v1.0");
}

void loop() {
  // Handle incoming serial commands
  if (serialReady && Serial.available()) {
    char inChar = Serial.read();
    if (inChar == '\n' || inChar == '\r') {
      if (inputBuffer.length() > 0) {
        handleCommand(inputBuffer);
        inputBuffer = "";
      }
    } else {
      inputBuffer += inChar;
    }
  }

  // Run stepper and auto-disable when done
  if (motorEnabled) {
    stepper.run();
    if (stepper.distanceToGo() == 0) {
      disableMotor();
      Serial.println("Motor automatically disabled");
    }
  }
}

// === Command Handler ===
void handleCommand(String cmd) {
  cmd.trim();
  cmd.toLowerCase();

  if (cmd == "ping") {
    Serial.println("pong");
  }
  else if (cmd == "stop") {
    stepper.stop();  // Graceful stop
    stepper.moveTo(stepper.currentPosition());  // Immediately stop
    disableMotor();
    Serial.println("Motor stopped");
  }
  else if (cmd == "reset") {
    stepper.setCurrentPosition(0);
    Serial.println("Position reset to 0");
  }
  else if (cmd.startsWith("up ")) {
    int steps = cmd.substring(3).toInt();
    enableMotor();
    stepper.move(stepper.distanceToGo() + steps);
    Serial.print("Moving up ");
    Serial.print(steps);
    Serial.println(" steps");
  }
  else if (cmd.startsWith("down ")) {
    int steps = cmd.substring(5).toInt();
    enableMotor();
    stepper.move(stepper.distanceToGo() - steps);
    Serial.print("Moving down ");
    Serial.print(steps);
    Serial.println(" steps");
  }
  else if (cmd.startsWith("speed ")) {
    float speed = cmd.substring(6).toFloat();
    if (speed > 0) {
      stepper.setMaxSpeed(speed);
      Serial.print("Speed set to ");
      Serial.println(speed);
    } else {
      Serial.println("Error: Invalid speed value");
    }
  }
  else if (cmd.startsWith("accel ")) {
    float accel = cmd.substring(6).toFloat();
    if (accel > 0) {
      stepper.setAcceleration(accel);
      Serial.print("Acceleration set to ");
      Serial.println(accel);
    } else {
      Serial.println("Error: Invalid acceleration value");
    }
  }
  else {
    Serial.print("Error: Unknown command: ");
    Serial.println(cmd);
  }
}
