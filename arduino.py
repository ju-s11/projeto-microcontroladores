import serial
import time

arduino = serial.Serial('COM6', 9600) # Se atentar sobre essa porta COM6
time.sleep(2)

def enviar(comando):
    print(f"[ENVIARIA PRO ARDUINO]: {comando}")
    # arduino.write((comando + '\n').encode())   # descomenta quando tiver o Arduino

def ler():
    if arduino.in_waiting > 0:
        return arduino.readline().decode().strip()
    return None

def fechar():
    arduino.close()

SERVOS = {"prisma": 1, "foguete": 2, "lua": 3}

LUZES = {
    "OFF": "apagar",
    "Branco": "branco",
    "Fogo": "fogo",
    "Espectro": "espectro",
    "Dispersão de luz branca": "dispersao",
    "Cálculo em loop": "calculo",
    "Fluxo de dados": "dados",
    "Decolagem do foguete": "decolagem",
    "Respirar": "respirar"
}

def comando_luz(nome_luz):
    efeito = LUZES[nome_luz]
    return f"led {efeito} 40"