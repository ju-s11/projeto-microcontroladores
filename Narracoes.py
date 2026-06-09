import wave
import os
import pygame
from piper import PiperVoice ## para pegar as vozes
import threading
import queue
import time

#pip install piper-tts
#pip install pygame

#criacao dos personagens e de suas respectivas vozes
TODAS_VOZES = {
    "Faber": "modelos/pt_BR-faber-medium.onnx",
    "Cadu": "modelos/pt_BR-cadu-medium.onnx",
}

class GerenciadorDeVozes:
    def __init__ (self, configuracao):
        #carregar todas as vozes conhecidas
        self.vozes_carregadas = {}
        self.diretorio_saida = "arquivo_audio" # pasta de saida dos audios

        if not os.path.exists(self.diretorio_saida):
            os.makedirs(self.diretorio_saida) # cria pasta se ela nao existir

        self._inicializar_modelos(configuracao) # chama a proxima funcao



    def _inicializar_modelos(self, configuracao): 
        #recebe dicionario que criei com as vozes e guarda a voz de cada personagem
        for personagem, caminho_modelo in TODAS_VOZES.items():

            if not os.path.exists(caminho_modelo):#se tiver erro com os arquivos
                raise FileNotFoundError(f"Voz de {personagem} não encontrado: {caminho_modelo}")
            
            self.vozes_carregadas[personagem] = PiperVoice.load(caminho_modelo)

        print("\nVozes prontas\n\n")



    def processar_mensagem(self, lista_frases):

        pygame.mixer.init()
        fila_de_audios = queue.Queue() #fila para os audios que vao ser reproduzidus

        def tocar_audios():
            
            while True:
                item = fila_de_audios.get()

                if item is None: 
                    break

                personagem, caminho_arquivo = item
                print(f"Tocando fala de {personagem}")
                
                pygame.mixer.music.load(caminho_arquivo)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

        thread = threading.Thread(target=tocar_audios)
        thread.start()


        for indice, frase in enumerate(lista_frases):
            personagem = frase["personagem"]
            texto = frase["texto"]

            if personagem not in self.vozes_carregadas:
                print(f"Personagem {personagem} não encontrado.")
                continue

            voz = self.vozes_carregadas[personagem]

            nome_arquivo = f"fala{indice + 1:03d}_{personagem}.wav"
            caminho_arquivo = os.path.join(self.diretorio_saida, nome_arquivo)

            print(f"Gravando: {nome_arquivo}") 

            with wave.open(caminho_arquivo, 'wb') as arquivo_wav:
                voz.synthesize_wav(texto, arquivo_wav)   

            fila_de_audios.put((personagem, caminho_arquivo))

        fila_de_audios.put(None)

        thread.join()
        pygame.mixer.quit()
        
        print("\n\nProcesso concluido")

if __name__ == "__main__":
    motor = GerenciadorDeVozes(TODAS_VOZES)
 
    #exemplo de mensagem
    mensagem_exemplo = [
        {"personagem": "Faber", "texto": "Olá, como vai? Me chamo Faber e eu sou um cientista"},
        {"personagem": "Cadu", "texto": "Tudo bem, obrigado. E você? Eu sou o Cadu. Prazer em te conhecer."},
        {"personagem": "Faber", "texto": "Estou ótimo, obrigado por perguntar. O prazer é meu, Cadu. Vamos trabalhar juntos para criar algo incrível."}
    ]

    motor.processar_mensagem(mensagem_exemplo)