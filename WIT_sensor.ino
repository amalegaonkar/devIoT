
/*
Author: 
* Copyright Cisco Systems, 2016
*/
#include <Wire.h>

#define STOP_CMD          0
#define TEMP_CMD          1
#define TOUCH_CMD         2
#define BUTTON_CMD        3
#define SOUND_CMD         4
#define LIGHT_CMD         5
#define ANGLE_CMD         6

#define LED_CMD           50
#define BUZZER_CMD        51
#define RELAYON_CMD       52
#define RELAYOFF_CMD      53

const int pin_temp = A0;
const int pin_angle = A2;
const int pin_sound = A3;
const int pin_light = A1;
const int pin_led = 3;
const int pin_buzzer = 5;
const int pin_button = 4;
const int pin_touch = 8;
const int pin_relay = 7;

int cmd_id;

const int colorR = 255;
const int colorG = 0;
const int colorB = 0;

void setup()
{
    Serial.begin(9600);
    pinMode(pin_led, OUTPUT);
    pinMode(pin_buzzer, OUTPUT);
    pinMode(pin_relay, OUTPUT);
    pinMode(pin_button, INPUT);
    pinMode(pin_touch, INPUT);
 
}

void read_temp()
{
    float temperature;
    int B=4250;                  // B value of the thermistor
    float resistance;
    int val = analogRead(pin_temp);                               // get analog value
    resistance=(float)(1023-val)*10000/val;                      // get resistance
    temperature=1/(log(resistance/10000)/B+1/298.15)-273.15;     // calc temperature
    Serial.println(temperature, 0);
}

void read_touch()
{
    int val = digitalRead(pin_touch);
    Serial.println(val);
}

void read_button()
{
    int val = digitalRead(pin_button);
    Serial.println(val);
    /*
    if (digitalRead(pin_button)) {
        Serial.println("1");
    } else {
        Serial.println("0");
    }*/
}

void read_sound()
{
    int val = analogRead(pin_sound);
    Serial.println(val);
}

void read_light()
{
    int val = analogRead(pin_light);
    Serial.println(val);
}

void read_angle()
{
    int val = analogRead(pin_angle);
    Serial.println(val);
}


bool stop_action()
{
    char c;
    while (Serial.available() > 0) {
        c = Serial.peek();
        if (c == '0') {
            return true;
        } else {
            if ((c == '\r') || (c == '\n')) {
                // to check next character
                c = Serial.read();
            } else {
                return false;
            }
        }
    }
    return false;
}

void set_led()
{
    for (long i = 0; i < 15; i++) {
        digitalWrite(pin_led, HIGH);
        delay(100);
        digitalWrite(pin_led, LOW);
        delay(100);
        
        if (stop_action()) {
            break;
        }
    }
}

void set_buzzer(int n)
{
    int tones[] = { 1915, 1700, 1519, 1432, 1275, 1136, 1014, 956 };
    int tone = tones[n];
    int duration = 3000;

    for (long i = 0; i < duration * 1000L; i += tone * 2) {
        digitalWrite(pin_buzzer, HIGH);
        delayMicroseconds(tone);
        digitalWrite(pin_buzzer, LOW);
        delayMicroseconds(tone);
        if (stop_action()) {
            break;
        }
    }
}

void set_relay_on()
{
    digitalWrite(pin_relay, HIGH);
}

void set_relay_off()
{
    digitalWrite(pin_relay, LOW);
}



void loop()
{
    if (Serial.available() > 0) {
        cmd_id = Serial.parseInt();
        switch (cmd_id) {
        case STOP_CMD:
            break;
        case TEMP_CMD:
            read_temp();
            break;
        case TOUCH_CMD:
            read_touch();
            break;
        case BUTTON_CMD:
            read_button();
            break;
        case SOUND_CMD:
            read_sound();
            break;
        case LIGHT_CMD:
            read_light();
            break;
        case ANGLE_CMD:
            read_angle();
            break;
            
        case LED_CMD:
            set_led();
            Serial.println("end");
            break;
        case BUZZER_CMD:
            set_buzzer(0);
            Serial.println("end");
            break;
        case RELAYON_CMD:
            set_relay_on();
            Serial.println("end");
            break;
        case RELAYOFF_CMD:
            set_relay_off();
            Serial.println("end");
            break;
        default:
            break;
        }
    }
    delay(50);
}

