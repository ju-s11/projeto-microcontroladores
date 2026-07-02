import arduino
import time

def atualizar_palco():
    personagens = []

    while True:
        linha = arduino.ler()
        if linha is None:
            continue

        if linha.startswith("--------"):
            break

        if linha.startswith("Posicao"):
            partes = linha.split(": ")
            if len(partes) == 2:
                nome = partes[1].strip()
                if nome != "vazia" and nome != "desconhecida":
                    personagens.append(nome)
    
    texto = ", ".join(personagens)
    with open("palco.txt", "w", encoding="utf-8") as f:
        f.write(texto)

def iniciar_ponte():
    while True:
        atualizar_palco()
        time.sleep(0.1)