# ENG4033 - Microcontroladores - Projeto Final

## Tema

Projeto da disciplina ENG4033 - Projeto de Programação em Microcontroladores com o tema Teatro Interativo Automatizado. O objetivo foi desenvolver um sistema de teatro automatizado onde personagens (representados por tags RFID) interagem com o ambiente, acionando mecanismos físicos e uma narração gerada dinamicamente por Inteligência Artificial.

## Descrição Técnica
O sistema é composto por uma integração entre hardware (Arduino) e software (Python). A interface gráfica, desenvolvida com tkinter atua como painel de controle central do teatro, permitindo que o usuário configure o clima, o tema e as vozes de cada personagem.

Utilizamos a biblioteca smolagents para conectar aos servidores da Hugging Face e instanciar um agente de IA que é responsável por atuar como uma espécie de "Diretor e Roteirista" do teatro, ele monitora a entrada de personagens no palco, gera o roteiro e coordena os elementos móveis do palco.

A comunicação entre o computador e o Arduino é feita com a biblioteca pyserial. O Python processa os comandos de palco e envia instruções seriais para o microcontrolador, que controla o movimento dos servomotores, a iluminação e a exibicação de um texto em um LCD.

A narração fica por conta da biblioteca Piper-TTS. O sistema converte o roteiro gerado pela IA em arquivos de áudio em tempo real, que são reproduzidos sincronizadamente pela biblioteca pygame.

O sistema detecta a presença dos personagens através de leitores RFID. A ponte de comunicação lê os UIDs das tags presentes e atualiza o estado do palco, que é lido pelo agente de IA para decidir qual cena será encenada.

## Pré-Requisitos
- Python versão 3.13
- Pygame versão 2.6
- Piper-TTS versão 1.4.2
- Smolagents versão 1.26
- Pyserial versão 3.5
- ServoTimer2 - biblioteca para os servos encontrada neste [link](https://github.com/nabontra/ServoTimer2)
- Modelos de voz - é necessário ter a pasta modelos/ no diretório raiz com os arquivos .onnx que podem ser encontrado nesse [link](https://drive.google.com/drive/folders/1dYDVqlYoaun7ELEjK224L1el2gv5nK6A?usp=sharing) 

## Instalação
Para executar o projeto é necessário um interpretador Python e a Arduino IDE para gerenciar o microcontrolador.
Configuramos o ambiente com o gerenciador de pacotes pip.
Execute esse comando no terminal para instalar as bibliotecas:

```console
$ pip install pygame piper-tts smolagents pyserial
```
Para compilar o código .ino no seu microcontrolador, é necessário instalar a biblioteca ServoTimer2. Abra a Arduino IDE, vá em Sketch > Include Library > Add. ZIP Library e selecionar o arquivo .zip


## Como Usar
Clone este repositório
```console
$git clone https://github.com/ju-s11/projeto-microcontroladores.git
```

E rode o arquivo inteface.py
```console
$python interface.py
```


## Tecnologias
[![Python](https://img.shields.io/badge/Python-3+-green?logo=python)](https://python.org)
### Participantes
- Ana Carolina Esteves
- Julia Guimarães Simão
- Manuela de Carvalho Borba
- Rodrigo Touma Costa


