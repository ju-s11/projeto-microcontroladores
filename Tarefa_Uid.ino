#include <SPI.h>
#include <MFRC522.h>

#define SS_1 53
#define RST_1 5

#define SS_2 49
#define RST_2 6

MFRC522 leitor1(SS_1, RST_1);
MFRC522 leitor2(SS_2, RST_2);


void setup() {
  Serial.begin(9600);
  SPI.begin();
  leitor1.PCD_Init();
  leitor2.PCD_Init();
  Serial.println("Aproxime uma tag de cada leitor para ver o UID:");

}

void loop() {
  // Leitor 1

  if (leitor1.PICC_IsNewCardPresent() && leitor1.PICC_ReadCardSerial()) {
    String uid = "";

    for (byte i = 0; i < leitor1.uid.size; i++) {
      if (leitor1.uid.uidByte[i] < 0x10) {
        uid = uid + "0";
      }
      uid = uid + String(leitor1.uid.uidByte[i], HEX);
    }

    uid.toUpperCase();
    Serial.print("Leitor 1 UID: ");
    Serial.println(uid);
    leitor1.PICC_HaltA();
  }

  // Leitor 2

  if (leitor2.PICC_IsNewCardPresent() && leitor2.PICC_ReadCardSerial()) {
    String uid = "";

    for (byte i = 0; i < leitor2.uid.size; i++) {
      if (leitor2.uid.uidByte[i] < 0x10) {
        uid = uid + "0";
      }
      uid = uid + String(leitor2.uid.uidByte[i], HEX);
    }

    uid.toUpperCase();
    Serial.print("Leitor 2 UID: ");
    Serial.println(uid);
    leitor2.PICC_HaltA();
  }
}
