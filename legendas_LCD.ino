#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 20, 4);

const int COLUNAS_LCD = 20;
const int LINHAS_LCD = 4;

String linhasTexto[50]; 
int totalLinhas = 0;
int linhaAtualScroll = 0;

unsigned long ultimoTempoScroll = 0;
const int velocidadeScroll = 1250;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  
  lcd.init();       
  lcd.backlight();  
  lcd.clear();      
  
  lcd.setCursor(0, 0);
  lcd.print("Aguardando texto...");
}

void loop() {
  // put your setup code here, to run once:
  if (Serial.available() > 0) {
    String mensagemCompleta = Serial.readStringUntil('\n');
    mensagemCompleta.trim();
    
    quebrarTextoEmLinhas(mensagemCompleta);
    
    linhaAtualScroll = 0;
    lcd.clear();
    atualizarDisplay();
    ultimoTempoScroll = millis();
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
    } else {
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