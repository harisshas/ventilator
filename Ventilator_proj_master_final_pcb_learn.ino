#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 20, 4);
LiquidCrystal_I2C lcd2(0x26, 20, 4);
//declaring input and output pins
#define SLAVE_ADDR 9

//analog inputs
int bpminputpin=A0;
int minvollimitpin=A5;
int ieratioinputpin=A2;

//limit input pins
int piplimitinputpin=A3;
int peeplimitinputpin=A4;
int vollimitinputpin=A1;
int fio2limitinputpin=A6;

//input from sensors
int exppresinputpin=A7;
int insppresinputpin=A8;
int inspflowinputpin=A9;
int expflowinputpin=A10;
int FiO2inputpin=A11;

//digital inputs and outputs

int inspdetpin=2;     //input from slave
int expdetpin=3;      //input from slave
int startstandbypin=4;//input from slave
int estoppin=5;       //input from slave
int inspdetsigpin=6;  //output to slave

int spareinputpin=8;//spare input
int alarmonoffpin=7;   //input from toggle switch

int insprelaypin=9;   //output to relay
int exprelaypin=10;   //output to relay
int oxyrelaypin=11;   //output to relay
int buzzeroutpin=12;  //output to relay

//delaring input value variables
int bpminput;
int minvolliminput;
float ieratioinput;

int inspflowinput;
int insppresinput;
int exppresinput;
int expflowinput;
int FiO2input;

int piplimitinput;
int peeplimitinput;
int vollimitinput;
int fio2limitinput;

double currentinspflow;
double currentexpflow;
float currentinsppres;
float currentexppres;
double currentFiO2;

int currentpiplimit;
int currentpeeplimit;
int currentvollimit;
int currentfio2limit;

int piplimitmax=60;
int piplimitmin=0;

int peeplimitmax=50;
int peeplimitmin=0;

int vollimitmax=600;
int vollimitmin=200;

int fio2limitmax=100;
int fio2limitmin=21;

//recomended flow rate
float recdflwrate;

float cumtidalvolume;
float altcumtidalvol;
float peakinsppres;
float peakexppres;
int minexppress;
int peakinspflow;
double avginspflow;
double avgexpflow;

float peakfio2;
float minfio2;
float avgfio2;

unsigned long int inspstarttime;
unsigned long int inspendtime;
unsigned long int expstarttime;
unsigned long int expendtime;
int currentinsptime;
int currentexptime;
int disptidvol;

int timedelay=1; // in milli seconds

int detectvar; //to detect a complete stroke 
int strokecount; //to count the no of strokes

long int datacountsinsp;
long int datacountsexp;

float inspflowscalevalue=1.0;
float insppresscalevalue=1.0;
float exppresscalevalue=1.0;

//declaring current value of input values
int currentbpm;
float currentieratio;
int currentminvollimit;
int sendtidalvolume;
int displaytidalvolume;
int currentmode;
long int no_of_pulses;
float pulsedelayforward;
float pulsedelayreverse;
long int tinspmsec;
long int texpmsec;

//declaring min and max values of inputs
int bpmmax=31;
int bpmmin=5;
long int tidalvolumemax=36000;
long int tidalvolumemin=12000;
int sendtidalvolumemax=36;
int sendtidalvolumemin=12;
int displayvolumemax=100;
int displayvolumemin=10;
float ieratiomax=2.0;
float ieratiomin=0.4;

//declaring time variables
float totalcycletime;
float insptime;
float exptime;

//declaring previous values
int prev_bpm;
float prev_ier;
int prev_vollimit;

int piplimind;
int peeplimind;
int vollimind;
int minventind;
int leakind;

double instexpvol;
double insttidvol;
unsigned long int currenttime;
//variables for learning and updating
int vollimcheck;
int learnbit;
long int puls_mult;
long int puls_rem;
long int puls_stop;
long int last_rem;
int count_less;

void setup()
{
  currentmode=0;
  count_less=0;
  strokecount=0;
  detectvar=0;
  datacountsinsp=0;
  datacountsexp=0;

  pinMode(startstandbypin,INPUT);
  pinMode(estoppin,INPUT);
  pinMode(inspdetpin,INPUT);
  pinMode(expdetpin,INPUT);

  pinMode(insprelaypin,OUTPUT);
  pinMode(exprelaypin,OUTPUT);
  pinMode(oxyrelaypin,OUTPUT);
  pinMode(buzzeroutpin,OUTPUT);
  pinMode(inspdetsigpin,OUTPUT);

  pinMode(alarmonoffpin,INPUT);
  
  digitalWrite(insprelaypin,HIGH);
  digitalWrite(exprelaypin,HIGH);
  digitalWrite(oxyrelaypin,LOW);
  digitalWrite(buzzeroutpin,HIGH);

  piplimind=0;
  peeplimind=0;
  vollimind=0;
  minventind=0;
  leakind=0;
    
  lcd.begin();
  lcd.backlight();
  lcd2.begin();
  lcd2.backlight();
  lcddisplaystart();
  Wire.begin();
  Serial.begin(9600);
  Serial.println("setup loop");
  learnbit=0;

  prev_bpm=0;
  prev_ier=0;
  prev_vollimit=0;
}

void loop()
{
  //reading bpminput, tidalvolumeinput and mapping them to maximum and minimum values
  
  bpminput = analogRead(bpminputpin);
  minvolliminput = analogRead(minvollimitpin);
  currentminvollimit = map(minvolliminput, 0, 900, 3, 8);
  ieratioinput = analogRead(ieratioinputpin);
  piplimitinput = analogRead(piplimitinputpin);
  peeplimitinput = analogRead(peeplimitinputpin);
  vollimitinput = analogRead(vollimitinputpin);
  fio2limitinput = analogRead(fio2limitinputpin);
  
  currentbpm = map(bpminput, 0, 1023, bpmmin, bpmmax);
  currentieratio = map(ieratioinput, 0, 1023, ieratiomax*10, ieratiomin*10);
  currentieratio=roundoff(int(currentieratio),5); //roundoff to nearest 5
  currentieratio=currentieratio/10.0;
  if(currentieratio==1.5 || currentieratio==2.5)
  currentieratio-=0.5;
  currentpiplimit = map(piplimitinput,0,1023,piplimitmin,piplimitmax);
  currentpeeplimit = map(peeplimitinput,0,1023,peeplimitmin,peeplimitmax);
  vollimitmin=round(2000/currentbpm);
  if(vollimitmin<=200)
  vollimitmin=200;
  vollimitmax=round((currentminvollimit*1000)/currentbpm);
  if(vollimitmax>=600)
  vollimitmax=600;
  currentvollimit = map(vollimitinput,0,1023,vollimitmin,vollimitmax);
  currentvollimit=roundoff(currentvollimit,25); //roundoff to nearest 25
  currentfio2limit = map(fio2limitinput,0,1023,fio2limitmin,fio2limitmax);

  totalcycletime=60.0/currentbpm;
  insptime=totalcycletime/(currentieratio+1.0);
  exptime=totalcycletime*(currentieratio/(currentieratio+1.0));
  tinspmsec=round(insptime*1000.0);
  texpmsec=round(exptime*1000.0);
  datacountsexp=0;
  datacountsinsp=0;
  if(learnbit==0)
  {
    Wire.beginTransmission(SLAVE_ADDR);
    if(strokecount==0)
    {
      no_of_pulses=tidalvolumemax;
    }
    int no_of_pulses_mult=no_of_pulses/255;
    int no_of_pulses_rem=no_of_pulses%255;
    int pulsedelayforward_mult=round(pulsedelayforward)/255;
    int pulsedelayforward_rem=round(pulsedelayforward)%255;
    int pulsedelayrev_mult=round(pulsedelayreverse)/255;
    int pulsedelayrev_rem=round(pulsedelayreverse)%255;
    Wire.write(no_of_pulses_mult);
    Wire.write(no_of_pulses_rem);
    Wire.write(pulsedelayforward_mult);
    Wire.write(pulsedelayforward_rem);
    Wire.write(pulsedelayrev_mult);
    Wire.write(pulsedelayrev_rem);
    Wire.endTransmission();
    //Serial.println("L0");
  }
  else if(learnbit==1)
  {
    last_rem=no_of_pulses;
    no_of_pulses=puls_stop;
    pulsedelayforward = round((tinspmsec*1000.0)/(no_of_pulses*2));
    pulsedelayreverse = round((texpmsec*1000.0)/(no_of_pulses*2));
    Wire.beginTransmission(SLAVE_ADDR);
    int no_of_pulses_mult=no_of_pulses/255;
    int no_of_pulses_rem=no_of_pulses%255;
    int pulsedelayforward_mult=round(pulsedelayforward)/255;
    int pulsedelayforward_rem=round(pulsedelayforward)%255;
    int pulsedelayrev_mult=round(pulsedelayreverse)/255;
    int pulsedelayrev_rem=round(pulsedelayreverse)%255;
    Wire.write(no_of_pulses_mult);
    Wire.write(no_of_pulses_rem);
    Wire.write(pulsedelayforward_mult);
    Wire.write(pulsedelayforward_rem);
    Wire.write(pulsedelayrev_mult);
    Wire.write(pulsedelayrev_rem);
    Wire.endTransmission();
    learnbit=0;
    count_less=0;
    //Serial.println("L1");
  }
  else if(learnbit==-1)
  {
    no_of_pulses=no_of_pulses+10*(currentvollimit-round(insttidvol));
    pulsedelayforward = round((tinspmsec*1000.0)/(no_of_pulses*2));
    pulsedelayreverse = round((texpmsec*1000.0)/(no_of_pulses*2));
    Wire.beginTransmission(SLAVE_ADDR);
    int no_of_pulses_mult=no_of_pulses/255;
    int no_of_pulses_rem=no_of_pulses%255;
    int pulsedelayforward_mult=round(pulsedelayforward)/255;
    int pulsedelayforward_rem=round(pulsedelayforward)%255;
    int pulsedelayrev_mult=round(pulsedelayreverse)/255;
    int pulsedelayrev_rem=round(pulsedelayreverse)%255;
    Wire.write(no_of_pulses_mult);
    Wire.write(no_of_pulses_rem);
    Wire.write(pulsedelayforward_mult);
    Wire.write(pulsedelayforward_rem);
    Wire.write(pulsedelayrev_mult);
    Wire.write(pulsedelayrev_rem);
    Wire.endTransmission();
    learnbit=0;
    count_less=0;
    //Serial.println("L-1");
  }
  vollimcheck=0;
  
  if(digitalRead(estoppin)==HIGH)
  {
    if(digitalRead(startstandbypin)==HIGH)
    {
      currentmode=1;
    }
    else
    {
      currentmode=0;
      digitalWrite(insprelaypin,HIGH);
      digitalWrite(exprelaypin,HIGH);
      digitalWrite(oxyrelaypin,LOW);
      digitalWrite(buzzeroutpin,HIGH);
      digitalWrite(inspdetsigpin,LOW);
      piplimind=0;
      peeplimind=0;
      vollimind=0;
      minventind=0;
      leakind=0;
      lcddisplayrun(currentbpm, currentieratio, displaytidalvolume, currentmode, currentminvollimit, insptime, exptime, currentpiplimit, currentpeeplimit, currentvollimit, currentfio2limit);
    }
    if((currentmode==1)||(currentmode==2))
    {
      if((prev_bpm!=currentbpm)||(prev_ier!=currentieratio)||(prev_vollimit!=currentvollimit))
      {
          learnbit=0;
          count_less=0;
         
          no_of_pulses=tidalvolumemax;
          pulsedelayforward = round((tinspmsec*1000.0)/(no_of_pulses*2));
          pulsedelayreverse = round((texpmsec*1000.0)/(no_of_pulses*2));
          
          Wire.beginTransmission(SLAVE_ADDR);
          int no_of_pulses_mult=no_of_pulses/255;
          int no_of_pulses_rem=no_of_pulses%255;
          int pulsedelayforward_mult=round(pulsedelayforward)/255;
          int pulsedelayforward_rem=round(pulsedelayforward)%255;
          int pulsedelayrev_mult=round(pulsedelayreverse)/255;
          int pulsedelayrev_rem=round(pulsedelayreverse)%255;
          Wire.write(no_of_pulses_mult);
          Wire.write(no_of_pulses_rem);
          Wire.write(pulsedelayforward_mult);
          Wire.write(pulsedelayforward_rem);
          Wire.write(pulsedelayrev_mult);
          Wire.write(pulsedelayrev_rem);
          Wire.endTransmission();
      }
      if(digitalRead(estoppin)==HIGH && digitalRead(inspdetpin)==LOW && digitalRead(expdetpin)==LOW)
      {
        currentmode=4;
        lcddisplayrun(currentbpm, currentieratio, displaytidalvolume, currentmode, currentminvollimit, insptime, exptime, currentpiplimit, currentpeeplimit, currentvollimit, currentfio2limit);
        digitalWrite(insprelaypin,HIGH);
        digitalWrite(exprelaypin,HIGH);
        digitalWrite(buzzeroutpin,HIGH);
        digitalWrite(inspdetsigpin,LOW);
        piplimind=0;
        peeplimind=0;
        vollimind=0;
        insttidvol=0;
        minventind=0;
        leakind=0;
      }
      //insp stroke
      while(digitalRead(estoppin)==HIGH && digitalRead(inspdetpin)==HIGH)
      {
          if(datacountsinsp==0)
          {
            inspstarttime=millis();
            currentmode=1;
            digitalWrite(insprelaypin,LOW);
            digitalWrite(exprelaypin,HIGH);
            if(currentvollimit>480 && currentfio2limit>90)
            {
              digitalWrite(oxyrelaypin,LOW);
            }
            else
            {
              digitalWrite(oxyrelaypin,HIGH);
            }
            digitalWrite(buzzeroutpin,HIGH);
            digitalWrite(inspdetsigpin,LOW);
            lcddisplayrun(currentbpm, currentieratio, displaytidalvolume, currentmode, currentminvollimit, insptime, exptime, currentpiplimit, currentpeeplimit, currentvollimit, currentfio2limit);
            peakinspflow=0;
            avginspflow=0;
            altcumtidalvol=0;
            peakfio2=0;
            minfio2=1023;
            avgfio2=0;
        
            cumtidalvolume=0.0;
            peakinsppres=0;
            detectvar=0;
            piplimind=0;
            peeplimind=0;
            vollimind=0;
            insttidvol=0;
            minventind=0;
            leakind=0;
          }
          datacountsinsp++;
          inspflowinput=analogRead(inspflowinputpin);
          insppresinput=analogRead(insppresinputpin);
          FiO2input=analogRead(FiO2inputpin);
          if(inspflowinput<=204) //after observing in serial monitor. the stray values were observed to be around 250 counts
          {
            currentinspflow=0;
          }
          else if(inspflowinput>204 && inspflowinput<=611)
          {
            currentinspflow=0.0614*inspflowinput-12.563;
          }
          else if(inspflowinput>611 && inspflowinput<=1023)
          {
            currentinspflow=1.1623*pow(2.73,0.0049*inspflowinput);
          }
          //Serial.println(currentinspflow);
          avginspflow+=currentinspflow;
          currentinsppres=((float(insppresinput)/204.6-2.5)*140.614)/4;
          //Serial.println(FiO2input);
          if(FiO2input>peakfio2)
          {
            peakfio2=FiO2input;
          }
          if(FiO2input<minfio2)
          {
            minfio2=FiO2input;
          }
          avgfio2+=FiO2input;
          //Serial.println(currentinsppres);
          cumtidalvolume+=(currentinspflow*timedelay*inspflowscalevalue)/60;
          if(currentinsppres>peakinsppres)
          {
            peakinsppres=currentinsppres*insppresscalevalue;
          }
          if(currentinsppres>currentpiplimit)
          {
             digitalWrite(inspdetsigpin,HIGH);
             if(digitalRead(alarmonoffpin)==HIGH)
             {
                digitalWrite(buzzeroutpin,LOW);
             }
             piplimind=1;
          }
          //delay(timedelay);
          //delayMicroseconds(100);
          currenttime=millis();
          currentinsptime=(currenttime-inspstarttime);
          //altcumtidalvol=(avginspflow*tinspmsec)/(60*datacountsinsp);
          insttidvol=(currentinsptime*avginspflow)/(datacountsinsp*60);
          //Serial.println(avginspflow/datacountsinsp);
          //Serial.println(insttidvol);
          if(round(insttidvol)>currentvollimit)
          {
            digitalWrite(inspdetsigpin,HIGH);
            if(vollimcheck==0)
            {
              Wire.requestFrom(SLAVE_ADDR,2);
              puls_mult=Wire.read();
              puls_rem=Wire.read();
              puls_stop=puls_mult*255+puls_rem;
              //Serial.println(puls_stop);
              vollimcheck=1;
              learnbit=1;
            }
            /*if(digitalRead(alarmonoffpin)==HIGH)
            {
                digitalWrite(buzzeroutpin,LOW);
            }*/
          }
          if(roundoff(round(insttidvol),10)*currentbpm>10000)
          {
            minventind=1;
            //digitalWrite(inspdetsigpin,HIGH);
            if(digitalRead(alarmonoffpin)==HIGH)
            {
                digitalWrite(buzzeroutpin,LOW);
            }
          }
      }
      //exp stroke
      //Serial.println("Stray detect");
      while(digitalRead(estoppin)==HIGH && digitalRead(expdetpin)==HIGH)
      {
          if(datacountsexp==0)
          {
              inspendtime=millis();
              expstarttime=millis();
              avgexpflow=0;
              instexpvol=0;
              datacountsexp=0;
              peakexppres=0;
              minexppress=50;
              currentmode=2;
              
              //digitalWrite(exprelaypin,LOW);
              //digitalWrite(insprelaypin,HIGH);
              digitalWrite(inspdetsigpin,LOW);
              digitalWrite(buzzeroutpin,HIGH);
              digitalWrite(oxyrelaypin,LOW);
              unsigned long int testtime1;
              unsigned long int testtime2;
              testtime1=millis();
              lcddisplayrun(currentbpm, currentieratio, displaytidalvolume, currentmode, currentminvollimit, insptime, exptime, currentpiplimit, currentpeeplimit, currentvollimit, currentfio2limit);
              testtime2=millis();
              Serial.print("testtime:");
              Serial.println(testtime2-testtime1);
              digitalWrite(insprelaypin,HIGH);
              digitalWrite(exprelaypin,LOW);
          }
          expflowinput=analogRead(expflowinputpin);
          exppresinput=analogRead(exppresinputpin);
          //currentexppres=map(exppresinput, expprescountmin, expprescountmax, exppresmin, exppresmax);
          currentexppres=((float(exppresinput)/204.6-2.5)*140.614)/4;
          //Serial.println(expflowinput);
          if(expflowinput<=204) //after observing in serial monitor. the stray values were observed to be around 250 counts
          {
            currentexpflow=0;
          }
          else if(expflowinput>204 && expflowinput<=611)
          {
            currentexpflow=0.0614*expflowinput-12.563;
          }
          else if(expflowinput>611 && expflowinput<=1023)
          {
            currentexpflow=1.1623*pow(2.73,0.0049*expflowinput);
          }
          avgexpflow+=currentexpflow;
          if(currentexppres>peakexppres)
          {
              peakexppres=currentexppres*exppresscalevalue;
          }
          if(currentexppres<minexppress)
          {
              minexppress=currentexppres*exppresscalevalue;
          }
          detectvar=1;
          //peep alarm
          if(currentexppres<=currentpeeplimit && digitalRead(alarmonoffpin)==HIGH)
          {
            digitalWrite(buzzeroutpin,LOW);
          }
          //peep limit action
          if(currentexppres<=currentpeeplimit)
          {
            //digitalWrite(exprelaypin,LOW);
            peeplimind=1;
          }
          datacountsexp++;
          currenttime=millis();
          currentexptime=(currenttime-expstarttime);
          instexpvol=(currentexptime*avgexpflow)/(datacountsexp*60);
          //Serial.println(-1*avgexpflow/datacountsexp);
          //Serial.println(insttidvol-instexpvol);
          //Serial.println(instexpvol);
          //delay(timedelay);
          //delayMicroseconds(100);
      }
      if(detectvar==1)
      {
          expendtime=millis();
          Serial.print("Insp TV: ");
          Serial.print(insttidvol);
          Serial.print(" Exp TV: ");
          Serial.print(instexpvol);
          Serial.print(" Pulse: ");
          Serial.print(puls_stop);
          Serial.print(" Datacountsinsp: ");
          Serial.print(datacountsinsp);
          Serial.print(" Datacountsexp: ");
          Serial.println(datacountsexp);
          if((round(insttidvol)<round(currentvollimit/2) && piplimind!=1)||((insttidvol-instexpvol)>=150))
          {
            leakind=1;
            if(digitalRead(alarmonoffpin)==HIGH)
            {
                digitalWrite(buzzeroutpin,LOW);
            }
          }
          if(roundoff(round(insttidvol),10)*currentbpm<3000)
          {
            minventind=-1;
            if(digitalRead(alarmonoffpin)==HIGH)
            {
                digitalWrite(buzzeroutpin,LOW);
            }
          }
          //Serial.print("Insp:");
          int obtinsptime=roundoff((inspendtime-inspstarttime),1);
          int obtexptime=roundoff((expendtime-expstarttime),1);
          int obtbpm=round(60000/(obtinsptime+obtexptime));
          lcd2.clear();
          lcd2.setCursor (0,0);
          lcd2.print("BPM=");
          lcd2.print(currentbpm);
          lcd2.setCursor (10,0);
          lcd2.print("TiV:");
          if(cumtidalvolume<0)
          {
              lcd2.print("_SO_");
          }
          else
          {
              float finavgfio2=avgfio2/datacountsinsp;
              Serial.print("Avg FiO2: ");
              Serial.println(finavgfio2);
              if(finavgfio2<=18)
              {
                  currentFiO2=0;
              }
              else if(finavgfio2>18 && finavgfio2<=110)
              {
                  currentFiO2=0.2283*finavgfio2-4.1087;
              }
              else if(finavgfio2>110 && finavgfio2<=588)
              {
                  currentFiO2=0.1653*finavgfio2+2.8201;
              }
              else if(finavgfio2>588)
              {
                  currentFiO2=100.0;
              }
              altcumtidalvol=(avginspflow*currentinsptime)/(60*datacountsinsp);
              disptidvol=round(insttidvol); //roundoff to nearest 1
             
              if(roundoff(disptidvol,10)<currentvollimit && piplimind!=1 && leakind!=1)
              {
                count_less++;
                //Serial.println(count_less);
              }
              else
              {
                count_less=0;
              }
              if(count_less>=1)
              {
                learnbit=-1;
              }
              disptidvol=roundoff(round(insttidvol),25);
              lcd2.print(disptidvol);
              lcd2.print("ml");
               
              if(disptidvol>(1.2*currentvollimit))
                vollimind=1;
              
              lcd2.setCursor(0,3);
              lcd2.print("FR:");
              //calculation of recommended flow rate
              recdflwrate=(((currentvollimit/totalcycletime)*(currentfio2limit-21.0))/79.0)*0.06;
              int minrecdflwrate,maxrecdflwrate;
              if(round(recdflwrate)<1)
              {
                minrecdflwrate=0;
              }
              else
              {
                minrecdflwrate=round(recdflwrate)-1;
              }
              if(round(recdflwrate)>10)
              {
                maxrecdflwrate=round(recdflwrate)+1;
              }
              else
              {
                maxrecdflwrate=round(recdflwrate)+1;
              }
              lcd2.print(minrecdflwrate);
              lcd2.print("-");
              lcd2.print(maxrecdflwrate);
              lcd2.print("Lpm");
          }
          
          lcd2.setCursor (0,1);
          if(currentieratio==0.5)
          {
              lcd2.print("I:E=2:1");
          }
          else
          {
              lcd2.print("I:E=1:");
              lcd2.print(currentieratio);
          }
          strokecount++;
          lcd2.setCursor(7,1);
          lcd2.print("   FiO2:");
          lcd2.print(round(currentFiO2));
          lcd2.print("%");
          lcd2.setCursor (0,2);
          lcd2.print("PIP:");
          lcd2.print(round(peakinsppres));
          lcd2.print("cm");
          lcd2.setCursor(10,2);  
          lcd2.print("PEEP:");
          lcd2.print(minexppress);
          lcd2.print("cm");
          if(minventind==1)
          {
            lcd2.setCursor (10,3);
            lcd2.print("MIVH");
          }
          if(minventind==-1)
          {
            lcd2.setCursor (10,3);
            lcd2.print("MIVL");
          }         
          if(peeplimind==1)
          {
            lcd2.setCursor (15,3);
            lcd2.print("PEEPL");
          }
          if(piplimind==1)
          {
            lcd2.setCursor (10,3);
            lcd2.print("PIPH");
          }
          if(leakind==1)
          {
            lcd2.setCursor (10,3);
            lcd2.print("LEAK");
          }
          if(vollimind==1)
          {
            lcd2.setCursor (15,3);
            lcd2.print("VOLH ");
          }
        }
        prev_bpm=currentbpm;
        prev_ier=currentieratio;
        prev_vollimit=currentvollimit;
     }
  }
  else
  {
    currentmode=3;
    lcddisplayrun(currentbpm, currentieratio, displaytidalvolume, currentmode, currentminvollimit, insptime, exptime, currentpiplimit, currentpeeplimit, currentvollimit, currentfio2limit);
    digitalWrite(insprelaypin,HIGH);
    digitalWrite(exprelaypin,HIGH);
    digitalWrite(oxyrelaypin,LOW);  
    digitalWrite(buzzeroutpin,HIGH);    
    digitalWrite(inspdetsigpin,LOW);
    insttidvol=0;
  }
}

void lcddisplayrun(int displaybpmvalue, float displayieratio, int displaytidalvolume, int displaymode, int displaytvset, double displayinsptime, double displayexptime, int displaypiplimit, int displaypeeplimit, int displayvollimit, int displayfio2limit)
{
  lcd.clear();
  lcd.print("BPM=");
  lcd.print(displaybpmvalue);
  lcd.setCursor(10,0); 
  lcd.print("TiV=");
  lcd.print(displayvollimit);
  lcd.print("mL");
  lcd.setCursor (0,1); // go to start of 2nd line
  if(displayieratio==0.5)
  {
    lcd.print("I:E=2:1");
  }
  else
  {
  lcd.print("I:E=1:");
  lcd.print(displayieratio);
  }
  lcd.setCursor(7,1); 
  lcd.print("   FiO2L=");
  lcd.print(displayfio2limit);
  lcd.print("%");
  //lcd.print(" ");  
  //lcd.print(displayinsptime);  
  lcd.setCursor (0,2); 
  lcd.print("PIPL:");
  lcd.print(displaypiplimit);
  lcd.print("cm");
  lcd.setCursor(10,2); 
  lcd.print("PEEPL:");
  lcd.print(displaypeeplimit);
  lcd.print("cm");
  lcd.setCursor (0,3); 
  lcd.print("MVL=");
  lcd.print(displaytvset);
  lcd.print("lpm");
  lcd.setCursor(10,3); 
  lcd.print("MODE=");
  if(displaymode==0)
    lcd.print("STB");
  else if(displaymode==1)
    lcd.print("INS");
  else if(displaymode==2)
    lcd.print("EXP");
  else if(displaymode==3)
    lcd.print("EST");
  else if(displaymode==4)
    lcd.print("RST");
  if((displaymode==0)||(displaymode==3)||(displaymode==4))
  delay(300);
}
void lcddisplaystart()
{
  lcd.clear();
  lcd2.clear();
  lcd.setCursor (0,1); // go to start of 2nd line
  lcd2.setCursor (0,1); // go to start of 2nd line
  lcd.print("   PROJECT  SWAAS");
  lcd2.print("   PROJECT  SWAAS");
  lcd.setCursor (0,2); // go to start of 2nd line
  lcd2.setCursor (0,2); // go to start of 2nd line
  lcd.print("   GOC  WORKSHOPS");
  lcd2.print("   GOC  WORKSHOPS");
  delay(500);
}
int roundoff(int num,int scale)
{
  int output;
  if(num%scale<=int(scale/2))
    output=int(num/scale)*scale;
  else if(num%scale>int(scale/2))
    output=(int(num/scale)+1)*scale;
  return output;
}
