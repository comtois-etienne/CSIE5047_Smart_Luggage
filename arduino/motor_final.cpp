//the code has been test
#include<Arduino.h>
#include<Wire.h>
#include <Servo.h>

Servo myservo;

#define bin1 9
#define bin2 10
#define pwmb 8

int servoPin = 7;

void setup() {
  pinMode(bin1, OUTPUT);
  pinMode(bin2, OUTPUT);
  pinMode(pwmb, OUTPUT);
  myservo.attach(servoPin);  
}

void goForward(int speed) {
  digitalWrite(bin1, HIGH);
  digitalWrite(bin2, LOW);
  analogWrite(pwmb, speed);
  delay(1000);
  analogWrite(pwmb, 0);
  delay(10);
}

void goBackward(int speed) {
  digitalWrite(bin1, LOW);
  digitalWrite(bin2, HIGH);
  analogWrite(pwmb, speed);
  delay(10);
  analogWrite(pwmb, 0);
  delay(10);
}

void stop() {
  digitalWrite(bin1, LOW);
  digitalWrite(bin2, LOW);
  analogWrite(pwmb, 0);
}

void steer() {
  myservo.write(angle)
  //30.1 27.1
}
void loop() {
  goForward(255);
  
//  stop();
//  delay(1000);
//
//  goBackward(255);
//  delay(2000);
//  
//  stop();
//  delay(1000);
}


void loop() {
  // Move the servo from 0 to 180 degrees in steps of 1 degree
  for (int angle = 0; angle <= 180; angle++) {
    myservo.write(angle);      // Set the servo position
    delay(15);                 // Wait for the servo to reach the position
  }

  delay(1000);  // Pause for a second

  // Move the servo from 180 to 0 degrees in steps of 1 degree
  for (int angle = 180; angle >= 0; angle--) {
    myservo.write(angle);      // Set the servo position
    delay(15);                 // Wait for the servo to reach the position
  }

  delay(1000);  // Pause for a second
}

