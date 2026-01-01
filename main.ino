int ledPins[5] = {6, 7, 8, 9, 10};

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 5; i++) {
    pinMode(ledPins[i], OUTPUT);
  }
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    for (int i = 0; i < 5; i++) {
      digitalWrite(ledPins[i], data.charAt(i) == '1');
    }
  }
}
