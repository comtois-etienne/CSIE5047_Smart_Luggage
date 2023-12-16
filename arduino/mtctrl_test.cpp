#include<Arduino.h>
#include<Wire.h>
#include <SpqrkFun_TB6612.h>

#define AIN1 8
#define AIN2 7
#define PWMA 6

#define BIN1 10
#define BIN1 9
#define PWMB 5

#define STBY 11

//const int offsetA = 1;
const int offsetB = 1;

Motor motor2 = Motor(BIN1, BIN2, PWMB, offsetB, STBY);

void setup() {
  pinMode(BIN1, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(PWMB, OUTPUT);
}

//drive(speed,time)
//stanby() til any command
//forward

//void goForward() {
//}
void loop() {
   motor2.drive(255,1000);   //1sec
   motor2.drive(-255,1000);  //1sec
   motor2.brake();           
   delay(1000);
   
   forward(motor2, 150);  
   delay(1000);				       
   
   back(motor2, -150); 
   delay(1000);
   
   brake(motor2);    
   delay(1000);

   brake(motor2);  
   delay(1000);   
}