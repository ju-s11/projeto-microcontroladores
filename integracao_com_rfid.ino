#include <FastLED.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <ServoTimer2.h>
#include <SPI.h>
#include <MFRC522.h>

#define PINO_DADOS 7
#define QTD_LEDS 11
#define NUM_SERVOS 3
#define NUM_REPETICOES_SERVO 5

#define SS_1  53
#define RST_1 5
#define SS_2  49
#define RST_2 6  
#define SS_3 48
#define RST_3 8

// RFID

MFRC522 leitor1(SS_1, RST_1);
MFRC522 leitor2(SS_2, RST_2);
MFRC522 leitor3(SS_3, RST_3);

String UID_NEWTON = "03A4699A";  // UID da tag do Isaac Newton
String UID_LOVELACE = "0ED93202";  // UID da tag da Ada Lovelace
String UID_HAMILTON = "A3A6DBE4";  // UID da tag da Margaret Hamilton
String UID_EINSTEIN = "E3E5689A";
String UID_CURIE = "FC0C3302";
String UID_LATTES = "D0A04A10";

unsigned long tempoAnteriorRfid = 0;
unsigned long intervaloRfid = 5000;

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

unsigned long ultimo_tempo[NUM_SERVOS] = {0, 0, 0};

int etapa[NUM_SERVOS] = {0, 0, 0};
int repeticoes[NUM_SERVOS] = {0, 0, 0};

int pinos[NUM_SERVOS] = {9, 10, 11};

// LCD

LiquidCrystal_I2C lcd(0x27, 20, 4);

const int COLUNAS_LCD = 20;
const int LINHAS_LCD = 4;

String linhasTexto[100]; 
int totalLinhas = 0;
int linhaAtualScroll = 0;

unsigned long ultimoTempoScroll = 0;
const int INTERVALO_SCROLL = 1500;

int anguloParaMicros(int angulo) {
  return map(angulo, 0, 180, 750, 2250);
}

void subir(int id) {
  servos[id].write(anguloParaMicros(180));
}

void descer(int id) {
  servos[id].write(anguloParaMicros(0));
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

      if(repeticoes[id] >= NUM_REPETICOES_SERVO) {
        movendo[id] = false;
      }
    }
  }
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
  Serial.print(">>> LCD recebeu ");
  Serial.print(resto.length());
  Serial.println(" caracteres");

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
  else if (uid == UID_EINSTEIN) {
    return "Albert Einstein";
  }
  else if (uid == UID_CURIE) {
    return "Marie Curie";
  }
  else if (uid == UID_LATTES) {
    return "César Lattes";
  }
  else {
    return "desconhecida";
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

  SPI.begin();
  leitor1.PCD_Init();
  leitor2.PCD_Init();
  leitor3.PCD_Init();
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
    if (millis() - ultimoTempoScroll >= INTERVALO_SCROLL) {
      ultimoTempoScroll = millis();
      
      if (linhaAtualScroll < totalLinhas - LINHAS_LCD) {
        linhaAtualScroll++;
        atualizarDisplay();
      }
    }
  }

  for (int i = 0; i < NUM_SERVOS; i++) {
    atualizar_mover(i);
  }

  if (millis() - tempoAnteriorRfid >= intervaloRfid) {
    tempoAnteriorRfid = millis();

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

    Serial.println("--------------------");
  }
}
