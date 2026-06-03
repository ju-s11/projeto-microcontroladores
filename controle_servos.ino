#include <Servo.h>

#define NUM_SERVOS 3

Servo servos[NUM_SERVOS];

int pinos[NUM_SERVOS] = {9, 10, 11};

//substituir delay por millis:
/*

unsigned long instante_inicial = 0;

if (millis() > instante_inicial + 10) {
 instante_inicial = millis();
}
*/

void subir(int id) {
  servos[id].write(180);
}

void mover(int id) {
  for(int i = 0; i  <= 3; i++) {
    servos[id].write(60);
    delay(500);
    servos[id].write(120);
    delay(500);
  }
}

void desaparecer(int id) {
  servos[id].write(0);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  for (int i = 0; i < NUM_SERVOS; i++) {
    servos[i].attach(pinos[i]);
    servos[i].write(0); //angulo 0 é a parte de baixo (escondida) do palco
  }
  Serial.println("\nFormato do comando: [numero do servo] [acao] ");
  Serial.println("Exemplo: 1 subir");
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available() > 0) {
    String linha = Serial.readStringUntil('\n');
    linha.trim();

    int espaco = linha.indexOf(' ');

    if (espaco == -1) {
      Serial.println("Comando invalido");
      return;
    }

    int numeroServo = linha.substring(0, espaco).toInt();
    String acao = linha.substring(espaco + 1);

    if (numeroServo < 1 || numeroServo > NUM_SERVOS) {
      Serial.println("Servo inexistente");
      return;
    }

    int id = numeroServo - 1;

    if (acao == "subir") {
      subir(id);
    }
    else if (acao == "mover") {
      mover(id);
    }
    else if (acao == "desaparecer") {
      desaparecer(id);
    }
    else {
      Serial.println("Acao desconhecida");
    }
  }

}
