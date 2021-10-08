#include <Wire.h>
#define SLAVE_ADDR 9

//data obtained from master
long int no_of_pulses;
int pulsedelayforward;
int pulsedelayreverse;

long int pulsecount;

//external inputs
int estoppin=7;
int standbypin=8;
int limitswitchpin=9; //to be changed

//to drive
int pulseswitch=11;
int dirswitch=12;

//output to master 
int insprelaypin=2;
int exprelaypin=3;
int standbysigpin=4;
int estoppsigpin=5;

//input from master
int mastdetsigpin=6; // to be changed

void setup()
{
  pinMode(pulseswitch,OUTPUT);
  pinMode(dirswitch,OUTPUT);
  pinMode(limitswitchpin,INPUT);
  pinMode(insprelaypin,OUTPUT);
  pinMode(exprelaypin,OUTPUT);
  pinMode(estoppin,INPUT);
  pinMode(standbypin,INPUT);
  pinMode(estoppsigpin,OUTPUT);
  pinMode(standbysigpin,OUTPUT);
  pinMode(mastdetsigpin,INPUT);

  /*no_of_pulses = 10000;
  pulsedelayforward = 25;
  pulsedelayreverse = 25;*/
  
  digitalWrite(insprelaypin,LOW);
  digitalWrite(exprelaypin,LOW);
  
  Wire.begin(SLAVE_ADDR);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
  Serial.begin(9600);
}
void requestEvent()
{
  Wire.write(round(pulsecount/255));
  Wire.write(round(pulsecount%255));
}
void receiveEvent() 
{
  long int no_of_pulses_mult=Wire.read();
  int no_of_pulses_rem=Wire.read();
  int pulsedelayforward_mult=Wire.read();
  int pulsedelayforward_rem=Wire.read();
  int pulsedelayrev_mult=Wire.read();
  int pulsedelayrev_rem=Wire.read();
  no_of_pulses = no_of_pulses_mult*255+no_of_pulses_rem;
  pulsedelayforward = pulsedelayforward_mult*255+pulsedelayforward_rem;
  pulsedelayreverse = pulsedelayrev_mult*255+pulsedelayrev_rem;
  /*Serial.print("No of pulses:");
  Serial.println(no_of_pulses);
  Serial.print("Pulsedelay forward:");
  Serial.println(pulsedelayforward);
  Serial.print("Pulsedelay reverse:");
  Serial.println(pulsedelayreverse);*/
  pulsedelayforward-=9; //offset
  pulsedelayreverse-=9; //offset
}
void loop()
{
    if(digitalRead(estoppin)==HIGH)
    {
      digitalWrite(estoppsigpin,HIGH);
      if(digitalRead(standbypin)==HIGH)
      {
        digitalWrite(standbysigpin,HIGH);
        //reset strokes
        if(digitalRead(limitswitchpin)==LOW)
        {
          //retract backward
          digitalWrite(dirswitch,HIGH);
          for(pulsecount=0;(digitalRead(limitswitchpin)==LOW) && (digitalRead(estoppin)==HIGH);pulsecount++)
          {
            digitalWrite(pulseswitch,HIGH);
            delayMicroseconds(100);
            digitalWrite(pulseswitch,LOW);
            delayMicroseconds(100);
          }
        }
      //insp stroke
      digitalWrite(dirswitch,LOW);
      digitalWrite(insprelaypin,HIGH);
      digitalWrite(exprelaypin,LOW);
      int checkval=0;
      long int checkcount=0;
      for(pulsecount=0;(pulsecount<no_of_pulses) && (digitalRead(estoppin)==HIGH);pulsecount++)
      {
        if(digitalRead(mastdetsigpin)==HIGH && checkval==0)
        {
          checkval=1;
          checkcount=pulsecount;         
        }
        if(checkval==0)
        {
          digitalWrite(pulseswitch,HIGH);
          delayMicroseconds(pulsedelayforward);
          digitalWrite(pulseswitch,LOW);
          delayMicroseconds(pulsedelayforward);
        }
        if(checkval==1)
        {
          digitalWrite(pulseswitch,HIGH);
          delayMicroseconds(pulsedelayforward);
          digitalWrite(pulseswitch,HIGH);
          delayMicroseconds(pulsedelayforward);
        }
      }
      digitalWrite(dirswitch,HIGH);
      digitalWrite(insprelaypin,LOW);
      digitalWrite(exprelaypin,HIGH);
      for(long int pulsecount=0;(pulsecount<no_of_pulses) && (digitalRead(estoppin)==HIGH) && (digitalRead(limitswitchpin)==LOW);pulsecount++)
      {
        if(checkval==0)
        {
          digitalWrite(pulseswitch,HIGH);
          delayMicroseconds(pulsedelayreverse);
          digitalWrite(pulseswitch,LOW);
          delayMicroseconds(pulsedelayreverse);
        }
        if(checkval==1)
        {
          if(pulsecount>no_of_pulses-checkcount)
          {
            digitalWrite(pulseswitch,HIGH);
            delayMicroseconds(pulsedelayreverse);
            digitalWrite(pulseswitch,LOW);
            delayMicroseconds(pulsedelayreverse);
          }
          else
          {
            digitalWrite(pulseswitch,HIGH);
            delayMicroseconds(pulsedelayreverse);
            digitalWrite(pulseswitch,HIGH);
            delayMicroseconds(pulsedelayreverse);
          }
        }
      }
    }
    else
    {
       digitalWrite(standbysigpin,LOW);
       digitalWrite(insprelaypin,LOW);
       digitalWrite(exprelaypin,LOW);
    }
  }
  else
  {
    digitalWrite(estoppsigpin,LOW);
    digitalWrite(insprelaypin,LOW);
    digitalWrite(exprelaypin,LOW);
  }
}
