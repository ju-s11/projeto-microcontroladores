#include <Servo.h>

#define NUM_SERVOS 3

Servo servos[NUM_SERVOS];

int pinos[NUM_SERVOS] = {9, 10, 11};

bool movendo[NUM_SERVOS] = {false, false, false};

unsigned long ultimo_tempo[NUM_SERVOS];

int etapa[NUM_SERVOS] = {0, 0, 0};
int repeticoes[NUM_SERVOS] = {0, 0, 0};

void subir(int id) {
  servos[id].write(180);
}

void iniciar_mover(int id) {
  movendo[id] = true;
  etapa[id] = 0;
  repeticoes[id] = 0;
  ultimo_tempo[id] = millis();

  servos[id].write(60);
}

void atualizar_mover(int id) {
  if (!movendo[id]) {
    return;
  }

  if(millis() - ultimo_tempo[id] >= 500) {
    ultimo_tempo[id] = millis();

    if (etapa[id] == 0) {
      servos[id].write(120);
      etapa[id] = 1;
    }
    else {
      servos[id].write(60);
      etapa[id] = 0;

      repeticoes[id]++;

      if(repeticoes[id] >= 3) {
        movendo[id] = false;
      }
    }
  }
}

void descer(int id) {
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
  for (int i = 0; i < NUM_SERVOS; i++) {
    atualizar_mover(i);
  }

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
      iniciar_mover(id);
    }
    else if (acao == "descer") {
      descer(id);
    }
    else {
      Serial.println("Acao desconhecida");
    }
  }

}
