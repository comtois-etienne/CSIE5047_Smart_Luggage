#include<Arduino.h>
#include<Wire.h>

class CarControl {
public:
  CarControl(int bin1Pin, int bin2Pin, int pwm) {
    this->bin1Pin = bin1Pin;
    this->bin2Pin = bin2Pin;
    this->pwmPin = pwmPin;
  }

  void goForward(int speed) {
    analogWrite(bin1Pin, 255);
    analogWrite(bin2Pin, 0);
    analogWrite(pwmPin, 255);
    delay(10);
    analogWrite(bin1Pin, 255);
    analogWrite(bin2Pin, 0);
    analogWrite(pwmPin, 0);
    delay(10);
  }

  void goBackward(int speed) {
    analogWrite(bin1Pin, 0);
    analogWrite(bin2Pin, 255);
    analogWrite(pwmPin, 255);
    delay(10);
    analogWrite(bin1Pin, 0);
    analogWrite(bin2Pin, 255);
    analogWrite(pwmPin, 0);
    delay(10);
  }

  void stop() {
    analogWrite(bin1Pin, 0);
    analogWrite(bin2Pin, 0);
    analogWrite(pwmPin, 0);
  }

private:
  int bin1Pin;
  int bin2Pin;
  int pwmPin;
};

const int bin1 = A0;
const int bin2 = A1;
const int pwm = A2;

CarControl car(bin1, bin2, pwm);

void setup() {
  pinMode(bin1, OUTPUT);
  pinMode(bin2, OUTPUT);
  pinMode(pwm, OUTPUT);
}

void loop() {
  car.goForward(255);
  delay(2000);

  car.stop();
  delay(1000);

  car.goBackward(255);
  delay(2000);

  car.stop();
  delay(1000);
}
