#include <FastLED.h>

#define PINO_DADOS 7
#define QTD_LEDS 11

CRGB leds[QTD_LEDS];
int padrao[QTD_LEDS] = {1,0,1,1,0,1,0,0,1,0,1};

String estado = "apagar";

unsigned long tempoAnterior = 0;
unsigned long intervalo = 100;

byte deslocamento = 0;

int p = 0;
int deslize = 0;
int preenchidos = 0;
int posicao = 0;
int brilhoFade = 0;
int direcao = 5;


void fogo() {

  FastLED.clear();

  for (int i = 0; i < 5; i++) {
    int verde = random(40,151);
    leds[i] = CRGB(255, verde, 0);
  }
}

void espectro() {

  int espacamento = 255 / QTD_LEDS;

  for(int i = 0; i < QTD_LEDS; i++) {
    int matiz = deslocamento + i*espacamento;
    leds[i] = CHSV(matiz, 255, 255);
  }

  deslocamento += 10;
}

void dispersao() {

  int espacamento = 255 / QTD_LEDS;

  for(int i = 0; i < QTD_LEDS; i++) {
    int matiz = i * espacamento;
    CRGB corEspectro = CHSV(matiz, 255, 255);
    leds[i] = blend(CRGB::White, corEspectro, p);
  }

  if (p < 255) {
    p += 5;
    if (p > 255) {
      p = 255;
    }
  }
}

void dados() {

  for(int i = 0; i < QTD_LEDS; i++) {

    int pos = (i + deslize) % QTD_LEDS;

    if(padrao[pos] == 1) {
      leds[i] = CRGB(0, 255, 180);
    }
    else {
      leds[i] = CRGB(0, 20, 15);
    }
  }
  deslize++;
}

void calculo() {

  FastLED.clear();

  for(int i = 0; i < QTD_LEDS; i++) {

    if(i < preenchidos) {
      leds[i] = CRGB(50, 210, 150);
    }
  }

  preenchidos++;
  if (preenchidos > QTD_LEDS) {
    preenchidos = 0;
  }
}

void decolagem() {
  
  FastLED.clear();

  for(int i = 0; i < QTD_LEDS; i++) {

    if (i == posicao) {
      leds[i] = CRGB(180, 200, 255);
    }
    else if (i < posicao) {
      int distancia = posicao - i;
      int brilho = 255 - distancia * 60;
      brilho = max(brilho, 0);
      leds[i] = CRGB(brilho, 100 * brilho / 255, 0);
    }
  }

  if (posicao < QTD_LEDS + 5) {
    posicao++;
  }
}

void respirar() {
  
  for(int i = 0; i < QTD_LEDS; i++) {
    leds[i] = CRGB(brilhoFade, brilhoFade, brilhoFade);
  }

  brilhoFade += direcao;

  if(brilhoFade >= 255) {
    brilhoFade = 255;
    direcao = -1 * direcao;
  }
  else if(brilhoFade <= 0) {
    brilhoFade = 0;
    direcao = -1 * direcao;
  }
}

void setup() {
  Serial.begin(9600);
  FastLED.addLeds<WS2812B, PINO_DADOS, GRB>(leds, QTD_LEDS);
  FastLED.setBrightness(180);

}

void loop() {
  if (Serial.available() > 0) {
    String entrada = Serial.readStringUntil('\n');
    entrada.trim();

    int espaco = entrada.indexOf(' ');

    String nome = entrada;

    int tempo = -1;

    if(espaco != -1) {
      nome = entrada.substring(0, espaco);
      tempo = entrada.substring(espaco + 1).toInt();
    }
    estado = nome;

    if(tempo > 0) {
      intervalo = tempo;
    }

    if(nome == "decolagem") {
      posicao = 0;
    }
    else if(nome == "dispersao") {
      p = 0;
    }

    Serial.print("Efeito: ");
    Serial.print(nome);
    Serial.print(" | Intervalo: ");
    Serial.println(intervalo);
    }

  if (millis() - tempoAnterior >= intervalo) {
    tempoAnterior = millis();

    if (estado == "apagar") {
      FastLED.clear();
    }
    else if (estado == "branco") {
      for (int i = 0; i < QTD_LEDS; i++) {
        leds[i] = CRGB::White;
      }
    }
    else if (estado == "fogo") {
      fogo();
    }
    else if (estado == "espectro") {
      espectro();
    }
    else if (estado == "dispersao") {
      dispersao();
    }
    else if (estado == "dados") {
      dados();
    }
    else if (estado == "calculo") {
      calculo();
    }
    else if (estado == "decolagem") {
      decolagem();
    }
    else if (estado == "respirar") {
      respirar();
    }
    else {
      FastLED.clear();
    }

  FastLED.show();
    }
  }