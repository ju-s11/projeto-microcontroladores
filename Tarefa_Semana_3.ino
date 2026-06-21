#include <SPI.h>
#include <MFRC522.h>

#define SS_1  53
#define RST_1 5

#define SS_2  49
#define RST_2 6  

#define SS_3 48
#define RST_3 8

MFRC522 leitor1(SS_1, RST_1);
MFRC522 leitor2(SS_2, RST_2);
MFRC522 leitor3(SS_3, RST_3);

String UID_NEWTON = "03A4699A";  // UID da tag do Isaac Newton
String UID_LOVELACE = "0ED93202";  // UID da tag da Ada Lovelace
String UID_HAMILTON = "A3A6DBE4";  // UID da tag da Margaret Hamilton

unsigned long tempoAnterior = 0;
unsigned long intervalo = 1000;

String lerLeitor(MFRC522 &leitor) {

  if (!leitor.PICC_IsNewCardPresent() || !leitor.PICC_ReadCardSerial()) {
    return "";
  }

  String resultado = "";

  for (byte i = 0; i < leitor.uid.size; i++) {
    if (leitor.uid.uidByte[i] < 0x10) {
      resultado = resultado + "0";
    }
    resultado = resultado + String(leitor.uid.uidByte[i], HEX);
  }

  resultado.toUpperCase();
  leitor.PICC_HaltA();

  return resultado;
}

String qualPersonagem(String uid) {
  if (uid == "") {
    return "vazia";
  }
  else if (uid == UID_NEWTON) {
    return "Isaac Newton";
  }
  else if (uid == UID_LOVELACE) {
    return "Ada Lovelace";
  }
  else if (uid == UID_HAMILTON) {
    return "Margaret Hamilton";
  }
  else {
    return "desconhecida";
  }
}

void setup() {
  Serial.begin(9600);
  SPI.begin();
  leitor1.PCD_Init();
  leitor2.PCD_Init();
  leitor3.PCD_Init();

}

void loop() {
  
  if (millis() - tempoAnterior >= intervalo) {
    tempoAnterior = millis();
    leitor1.PCD_Init();
    leitor2.PCD_Init();
    leitor3.PCD_Init();

    String tag1 = lerLeitor(leitor1);
    String tag2 = lerLeitor(leitor2);
    String tag3 = lerLeitor(leitor3);

    Serial.print("Posicao 1: ");
    Serial.println(qualPersonagem(tag1));

    Serial.print("Posicao 2: ");
    Serial.println(qualPersonagem(tag2));

    Serial.print("Posicao 3: ");
    Serial.println(qualPersonagem(tag3));

    Serial.println("-------------------");
  
  }
}