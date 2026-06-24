#include <FastLED.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <ServoTimer2.h>

#define PINO_DADOS 7
#define QTD_LEDS 11
#define NUM_SERVOS 3

// LEDS

CRGB leds[QTD_LEDS];
int padrao[QTD_LEDS] = {1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1};

byte deslocamento = 0;

int p = 0;
int deslize = 0;
int preenchidos = 0;
int posicao = 0;
int brilhoFade = 0;
int direcao = 5;

String estado = "apagar";

unsigned long tempoAnterior = 0;
unsigned long intervalo = 100;

// SERVOS

ServoTimer2 servos[NUM_SERVOS];
bool movendo[NUM_SERVOS] = {false, false, false};

unsigned long ultimo_tempo[NUM_SERVOS];

int etapa[NUM_SERVOS] = {0, 0, 0};
int repeticoes[NUM_SERVOS] = {0, 0, 0};

int pinos[NUM_SERVOS] = {9, 10, 11};

// LCD

LiquidCrystal_I2C lcd(0x27, 20, 4);

const int COLUNAS_LCD = 20;
const int LINHAS_LCD = 4;

String linhasTexto[50]; 
int totalLinhas = 0;
int linhaAtualScroll = 0;

unsigned long ultimoTempoScroll = 0;
const int velocidadeScroll = 1500;

int anguloParaMicros(int angulo) {
  return map(angulo, 0, 180, 750, 2250);
}

void subir(int id) {
  servos[id].write(anguloParaMicros(180));
}

void iniciar_mover(int id) {
  movendo[id] = true;
  etapa[id] = 0;
  repeticoes[id] = 0;
  ultimo_tempo[id] = millis();

  servos[id].write(anguloParaMicros(60));
}

void atualizar_mover(int id) {
  if (!movendo[id]) {
    return;
  }

  if(millis() - ultimo_tempo[id] >= 500) {
    ultimo_tempo[id] = millis();

    if (etapa[id] == 0) {
      servos[id].write(anguloParaMicros(120));
      etapa[id] = 1;
    }
    else {
      servos[id].write(anguloParaMicros(60));
      etapa[id] = 0;

      repeticoes[id]++;

      if(repeticoes[id] >= 3) {
        movendo[id] = false;
      }
    }
  }
}

void descer(int id) {
  servos[id].write(anguloParaMicros(0));
}

void quebrarTextoEmLinhas(String texto) {
  totalLinhas = 0;
  String linhaAtual = "";
  
  int indiceEspaco = 0;
  while (texto.length() > 0 && totalLinhas < 50) {
    indiceEspaco = texto.indexOf(' ');
    String palavra;
    
    if (indiceEspaco == -1) {
      palavra = texto;
      texto = "";
    } else {
      palavra = texto.substring(0, indiceEspaco);
      texto = texto.substring(indiceEspaco + 1);
    }
    
    if (palavra.length() == 0) continue;

    if (linhaAtual.length() + palavra.length() + (linhaAtual.length() > 0 ? 1 : 0) <= COLUNAS_LCD) {
      if (linhaAtual.length() > 0) {
        linhaAtual += " ";
      }
      linhaAtual += palavra;
    } 
    else {
      linhasTexto[totalLinhas] = linhaAtual;
      totalLinhas++;
      linhaAtual = palavra;
    }
  }
  
  if (linhaAtual.length() > 0 && totalLinhas < 50) {
    linhasTexto[totalLinhas] = linhaAtual;
    totalLinhas++;
  }
}

void atualizarDisplay() {
  for (int i = 0; i < LINHAS_LCD; i++) {
    lcd.setCursor(0, i);
    int indiceLinhaTexto = linhaAtualScroll + i;
    
    if (indiceLinhaTexto < totalLinhas) {
      lcd.print(linhasTexto[indiceLinhaTexto]);
      
      for (int j = linhasTexto[indiceLinhaTexto].length(); j < COLUNAS_LCD; j++) {
        lcd.print(" ");
      }
    } else {
      for (int j = 0; j < COLUNAS_LCD; j++) {
        lcd.print(" ");
      }
    }
  }
}

void fogo() {

  FastLED.clear();

  for (int i = 0; i < 5; i++) {
    int verde = random(40, 151);
    leds[i] = CRGB(255, verde, 0);
  }
}

void espectro() {

  int espacamento = 255 / QTD_LEDS;

  for (int i = 0; i < QTD_LEDS; i++) {
    int matiz = deslocamento + i * espacamento;
    leds[i] = CHSV(matiz, 255, 255);
  }

  deslocamento += 10;
}

void dispersao() {

  int espacamento = 255 / QTD_LEDS;

  for (int i = 0; i < QTD_LEDS; i++) {
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

  for (int i = 0; i < QTD_LEDS; i++) {

    int pos = (i + deslize) % QTD_LEDS;

    if (padrao[pos] == 1) {
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

  for (int i = 0; i < QTD_LEDS; i++) {

    if (i < preenchidos) {
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

  for (int i = 0; i < QTD_LEDS; i++) {

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

  for (int i = 0; i < QTD_LEDS; i++) {
    leds[i] = CRGB(brilhoFade, brilhoFade, brilhoFade);
  }

  brilhoFade += direcao;

  if (brilhoFade >= 255) {
    brilhoFade = 255;
    direcao = -1 * direcao;
  }
  else if (brilhoFade <= 0) {
    brilhoFade = 0;
    direcao = -1 * direcao;
  }
}

void processarLed(String resto) {

  int espaco = resto.indexOf(' ');
  String nome = resto;
  int tempo = -1;

  if (espaco != -1) {
    nome = resto.substring(0, espaco);
    tempo = resto.substring(espaco + 1).toInt();
  }
  estado = nome;

  if (tempo > 0) {
    intervalo = tempo;
  }

  if (nome == "decolagem") {
    posicao = 0;
  }
  else if (nome == "dispersao") {
    p = 0;
  }

  Serial.print("Efeito: ");
  Serial.print(nome);
  Serial.print(" | Intervalo: ");
  Serial.println(intervalo);
}

void processarLcd(String resto) {

  quebrarTextoEmLinhas(resto);

  linhaAtualScroll = 0;
  lcd.clear();
  atualizarDisplay();
  ultimoTempoScroll = millis();
}

void processarServo(String resto) {

  int espaco = resto.indexOf(' ');

  if (espaco == -1) {
      Serial.println("Comando invalido");
      return;
    }

  int numeroServo = resto.substring(0, espaco).toInt();
  String acao = resto.substring(espaco + 1);

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

void setup() {
  Serial.begin(9600);

  FastLED.addLeds<WS2812B, PINO_DADOS, GRB>(leds, QTD_LEDS);
  FastLED.setBrightness(180);

  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Aguardando texto...");

  for (int i = 0; i < NUM_SERVOS; i++) {
    servos[i].attach(pinos[i]);
    servos[i].write(anguloParaMicros(0)); //angulo 0 é a parte de baixo (escondida) do palco
  }
}

void loop() {
  if (Serial.available() > 0) {
    String entrada = Serial.readStringUntil('\n');
    entrada.trim();

    int espaco = entrada.indexOf(' ');
    String prefixo = entrada;
    String resto = "";

    if (espaco != -1) {
      prefixo = entrada.substring(0, espaco);
      resto = entrada.substring(espaco + 1);
    }

    if (prefixo == "led") {
      processarLed(resto);
    }
    else if (prefixo == "servo") {
      processarServo(resto);
    }
    else if (prefixo == "lcd") {
      processarLcd(resto);
    }
    else {
      Serial.println("Prefixo desconhecido");
    }
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

  if (totalLinhas > LINHAS_LCD) {
    if (millis() - ultimoTempoScroll >= velocidadeScroll) {
      ultimoTempoScroll = millis();
      
      linhaAtualScroll++;
      
      if (linhaAtualScroll > totalLinhas - LINHAS_LCD) {
        linhaAtualScroll = 0; 
      }
      
      atualizarDisplay();
    }
  }

  for (int i = 0; i < NUM_SERVOS; i++) {
    atualizar_mover(i);
  }
}