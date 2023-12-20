#include <Wire.h>
#include <Arduino.h>
#include <Servo.h>

Servo myservo;

#define bin1 9
#define bin2 10
#define pwmb 8
#define serialSpeed 9600

int servoPin = 7;

void setup() {
  pinMode(bin1, OUTPUT);
  pinMode(bin2, OUTPUT);
  pinMode(pwmb, OUTPUT);
  myservo.attach(servoPin);  
  Serial.begin(serialSpeed);
}

void goForward(int speed) {
  digitalWrite(bin1, HIGH);
  digitalWrite(bin2, LOW);
  analogWrite(pwmb, speed);
}

void goBackward(int speed) {
  digitalWrite(bin1, LOW);
  digitalWrite(bin2, HIGH);
  analogWrite(pwmb, speed);
}

void steering(int angle) {
  myservo.write(angle);
}

void stop() {
  digitalWrite(bin1, LOW);
  digitalWrite(bin2, LOW);
  analogWrite(pwmb, 0);
}

void processCommands(String command) {
  if (command.startsWith("SPEED:") && command.indexOf(",STEERING:") != -1) {
    
    float speed = command.substring(6, command.indexOf(",STEERING:")).toFloat();
    
    float steering = command.substring(command.indexOf(",STEERING:") + 10).toFloat();
    
    if (speed > 0) {
      goForward(speed);
    } else if (speed < 0) {
      goBackward(-speed); // Make speed positive for backward motion
    } else {
      stop();
    }
    //motor control and steering logic
    //Serial.print("Received commands - Speed: ");
    //Serial.print(speed);
    //Serial.print(", Steering: ");
    //Serial.println(steering);
  }
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming command
    String command = Serial.readStringUntil('\n');
    
    // Process the received commands
    processCommands(command);
  }
  
  // Your main loop code goes here
}
