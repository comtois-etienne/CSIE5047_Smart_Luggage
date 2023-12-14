//arduino code for being slaved
#include <Wire.h>
#include<Arduino.h>

#define serialSpeed 9600

void setup() {
  Serial.begin(serialSpeed);
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming command
    String command = Serial.readStringUntil('\n');
    
    // Parse the command and extract speed and steering values
    if (command.startsWith("SPEED:") && command.indexOf(",STEERING:") != -1) {
      // Extract speed value
      float speed = command.substring(6, command.indexOf(",STEERING:")).toFloat();
      
      // Extract steering value
      float steering = command.substring(command.indexOf(",STEERING:") + 10).toFloat();
      
      // Do something with the speed and steering values
      // Replace the following lines with your actual motor control and steering logic
      Serial.print("Received commands - Speed: ");
      Serial.print(speed);
      Serial.print(", Steering: ");
      Serial.println(steering);
    }
  }
  
  // Your main loop code goes here
}
