#include <Servo.h>
int capteur = 2;
Servo myservo;
#define MIN 500
#define MAX 2500
#define PAUSE 500


void setup() { 
  myservo.attach(8, MIN, MAX);  //servo pin
  pinMode(capteur,INPUT);
}

void loop() {
if (digitalRead(capteur) == LOW){
myservo.write(180);
delay(PAUSE);
myservo.write(0);
delay(PAUSE);
  }
}
