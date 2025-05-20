// LED Pin Tanımlamaları
const int CORN_LED_PIN = 8;
const int CANNABIS_LED_PIN = 9;
const int BUZZER = 10;
// L298N Motor Sürücü Pin Tanımlamaları (DİJİTAL PİNLER)
// Motor A (Örneğin sol motor)
const int MOTOR_A_IN1 = 3;  // L298N IN1 -> Arduino D2
const int MOTOR_A_IN2 = 4;  // L298N IN2 -> Arduino D3
// const int MOTOR_A_ENA = 10; // Opsiyonel: Motor A hız kontrolü için PWM pini (L298N ENA -> Arduino D10)

// Motor B (Örneğin sağ motor)
const int MOTOR_B_IN3 = 5;  // L298N IN3 -> Arduino D4
const int MOTOR_B_IN4 = 6;  // L298N IN4 -> Arduino D5
// const int MOTOR_B_ENB = 11; // Opsiyonel: Motor B hız kontrolü için PWM pini (L298N ENB -> Arduino D11)

String gelenKomut;

// --- Motor Kontrol Fonksiyonları ---
void motorlariDurdur() {
  // Motor A durdur
  digitalWrite(MOTOR_A_IN1, LOW);
  digitalWrite(MOTOR_A_IN2, LOW);
  // if (MOTOR_A_ENA != -1) analogWrite(MOTOR_A_ENA, 0); // Eğer ENA pini tanımlıysa ve PWM kullanılıyorsa

  // Motor B durdur
  digitalWrite(MOTOR_B_IN3, LOW);
  digitalWrite(MOTOR_B_IN4, LOW);
  // if (MOTOR_B_ENB != -1) analogWrite(MOTOR_B_ENB, 0); // Eğer ENB pini tanımlıysa ve PWM kullanılıyorsa

  Serial.println("Motorlar durduruldu.");
}

void motorlariIleriSur(int hiz = 200) { // hiz parametresi opsiyonel, 0-255 arası (PWM için)
  // Motor A ileri
  digitalWrite(MOTOR_A_IN1, HIGH);
  digitalWrite(MOTOR_A_IN2, LOW);
  // if (MOTOR_A_ENA != -1) analogWrite(MOTOR_A_ENA, hiz); // Eğer ENA pini tanımlıysa ve PWM kullanılıyorsa

  // Motor B ileri
  digitalWrite(MOTOR_B_IN3, HIGH);
  digitalWrite(MOTOR_B_IN4, LOW);
  // if (MOTOR_B_ENB != -1) analogWrite(MOTOR_B_ENB, hiz); // Eğer ENB pini tanımlıysa ve PWM kullanılıyorsa

  Serial.println("Motorlar ileri hareket ediyor.");
}

void motorlariGeriSur(int hiz = 200) {
  // Motor A geri
  digitalWrite(MOTOR_A_IN1, LOW);
  digitalWrite(MOTOR_A_IN2, HIGH);
  // if (MOTOR_A_ENA != -1) analogWrite(MOTOR_A_ENA, hiz);

  // Motor B geri
  digitalWrite(MOTOR_B_IN3, LOW);
  digitalWrite(MOTOR_B_IN4, HIGH);
  // if (MOTOR_B_ENB != -1) analogWrite(MOTOR_B_ENB, hiz);

  Serial.println("Motorlar geri hareket ediyor.");
}

void setup() {
  Serial.begin(9600);

  pinMode(CORN_LED_PIN, OUTPUT);
  pinMode(CANNABIS_LED_PIN, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  pinMode(MOTOR_A_IN1, OUTPUT);
  pinMode(MOTOR_A_IN2, OUTPUT);
  // if (MOTOR_A_ENA != -1) pinMode(MOTOR_A_ENA, OUTPUT); // Eğer ENA pini tanımlıysa
  pinMode(MOTOR_B_IN3, OUTPUT);
  pinMode(MOTOR_B_IN4, OUTPUT);
  // if (MOTOR_B_ENB != -1) pinMode(MOTOR_B_ENB, OUTPUT); // Eğer ENB pini tanımlıysa

  digitalWrite(CORN_LED_PIN, LOW);
  digitalWrite(CANNABIS_LED_PIN, LOW);

  // Başlangıçta motorları durdur
  // Eğer ENA/ENB pinlerini Arduino'dan PWM ile kontrol ediyorsanız, başlangıçta hızlarını 0 yapın
  // veya eğer sadece ON/OFF ise digitalWrite(MOTOR_A_ENA, HIGH); gibi etkinleştirin.
  // Bu örnekte ENA/ENB'nin L298N üzerinde jumper ile 5V'a bağlı olduğu varsayılıyor
  // veya kullanılmıyorlarsa (motorlar her zaman etkin).
  motorlariDurdur();

  Serial.println("Arduino Hazır. Motorlar ve LED'ler için komut bekleniyor (Dijital Pinler)...");
}

void loop() {
  if (Serial.available() > 0) {
    gelenKomut = Serial.readStringUntil('\n');
    gelenKomut.trim();

    Serial.print("Alınan Komut: ");
    Serial.println(gelenKomut);

    if (gelenKomut == "CORN_DETECTED") {
      digitalWrite(CORN_LED_PIN, HIGH);
      digitalWrite(CANNABIS_LED_PIN, LOW);
      digitalWrite(BUZZER, LOW);
      motorlariIleriSur(); // Motorları ileri sür
      Serial.println("Mısır LED'i YAKILDI. Motorlar İLERİ.");
    }
    else if (gelenKomut == "CANNABIS_DETECTED") {
      digitalWrite(CANNABIS_LED_PIN, HIGH);
      digitalWrite(CORN_LED_PIN, LOW);
      digitalWrite(BUZZER, HIGH);
      motorlariDurdur(); // Kenevir algılanınca motorları durdur
      Serial.println("Kenevir LED'i YAKILDI. Motorlar DURDU.");
    }
    else if (gelenKomut == "CLEAR") {
      digitalWrite(CORN_LED_PIN, LOW);
      digitalWrite(CANNABIS_LED_PIN, LOW);
      motorlariDurdur(); // Hiçbir şey algılanmazsa motorları durdur
      Serial.println("LED'ler SÖNDÜRÜLDÜ. Motorlar DURDU.");
    }
    else if (gelenKomut == "STOP_ALL") {
      digitalWrite(CORN_LED_PIN, LOW);
      digitalWrite(CANNABIS_LED_PIN, LOW);
      motorlariDurdur(); // Program sonlandığında motorları durdur
      Serial.println("Tüm işlemler durduruldu. LED'ler SÖNDÜRÜLDÜ. Motorlar DURDU.");
    }
    gelenKomut = "";
  }
}