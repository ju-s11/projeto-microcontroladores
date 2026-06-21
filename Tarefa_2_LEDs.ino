#include <FastLED.h>

#define PINO_DADOS 6
#define QTD_LEDS 11

CRGB leds[QTD_LEDS];
int padrao[QTD_LEDS] = {1,0,1,1,0,1,0,0,1,0,1};

char estado = 'o';

unsigned long tempoAnterior = 0;
unsigned long intervalo = 100;

byte deslocamento = 0;

int p = 0;
int deslize = 0;
int preenchidos = 0;
int posicao = 0;

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

void setup() {
  Serial.begin(9600);
  FastLED.addLeds<WS2812B, PINO_DADOS, GRB>(leds, QTD_LEDS);
  FastLED.setBrightness(180);

}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    
    if (c != '\n' && c != '\r') {
      estado = c;

      if (c == 'r') {
        posicao = 0;
      }
      else if (c == 'd') {
        p = 0;
      }

      Serial.print("Mude o estado para: ");
      Serial.println(estado);
    }
  }

  if (millis() - tempoAnterior >= intervalo) {
    tempoAnterior = millis();

    switch(estado) {
      case 'o':
        FastLED.clear();
        break;

      case 'w':
        for (int i = 0; i < QTD_LEDS; i++) {
          leds[i] = CRGB::White;
        }
        break;
      
      case 'f':
        fogo();
        break;

      case 'e':
        espectro();
        break;

      case 'd':
        dispersao();
        break;

      case 'b':
        dados();
        break;

      case 'c':
        calculo();
        break;

      case 'r':
        decolagem();
        break;

      default:
        FastLED.clear();
        break;
    }

  FastLED.show();
  }
}
