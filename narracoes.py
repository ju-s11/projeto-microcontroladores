import wave
import os
import pygame
from piper import PiperVoice, SynthesisConfig 
import threading
import queue
import time
import arduino

#pip install piper-tts
#pip install pygame

TODAS_VOZES = {
    "Alba": "modelos/en_GB-alba-medium.onnx", 
    "Amy": "modelos/en_US-amy-medium.onnx", 
    "Northern Male": "modelos/en_GB-northern_english_male-medium.onnx",
    "Alan": "modelos/en_GB-alan-medium.onnx",
}

pygame.init()
pygame.mixer.init()

class GerenciadorDeVozes:
    def __init__ (self, configuracao):
        self.vozes_carregadas = {}
        self.diretorio_saida = "arquivo_audio" 
        self.cortar_cena = False

        if not os.path.exists(self.diretorio_saida):
            os.makedirs(self.diretorio_saida) 

        self._inicializar_modelos(configuracao)
    
    def parar_teatro(self):
        self.cortar_cena = True
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            try:
                pygame.mixer.music.unload()
            except AttributeError:
                pass


    def _inicializar_modelos(self, configuracao): 
        self.configs_personagens = {}
        
        
        for personagem, config in configuracao.items():
            caminho_modelo = config["voz"]
            
            if not os.path.exists(caminho_modelo):
                raise FileNotFoundError(f"Voz de {personagem} não encontrado: {caminho_modelo}")
            
            self.vozes_carregadas[personagem] = PiperVoice.load(caminho_modelo)
            self.configs_personagens[personagem] = {
                "volume": config["volume"],
                "velocidade":config["velocidade"]}

        print("\nVozes prontas\n\n")



    def processar_mensagem(self, lista_frases, deb_print=None):

        ##teste_ana
        with open("narracao.txt", "w", encoding="utf-8") as f:
            f.write("True")
            
        
        try:
            fila_de_audios = queue.Queue() 

            def tocar_audios():
                
                while True:
                    item = fila_de_audios.get()
                    
                    if self.cortar_cena:
                        break

                    if item is None: 
                        break

                    personagem, caminho_arquivo, vol, texto = item
                    print(f"Tocando fala de {personagem}")
                    
                    if deb_print:
                        deb_print(f"{personagem}: '{texto}'")

                    arduino.enviar("lcd " + texto)
                    
                    pygame.mixer.music.load(caminho_arquivo)
                    pygame.mixer.music.set_volume(vol)
                    pygame.mixer.music.play()

                    while pygame.mixer.music.get_busy():
                        if self.cortar_cena:
                            pygame.mixer.music.stop()
                            try:
                                pygame.mixer.music.unload()
                            except AttributeError:
                                pass
                            break
                        time.sleep(0.1)

            thread = threading.Thread(target=tocar_audios)
            thread.start()


            for indice, frase in enumerate(lista_frases):
                personagem = frase["personagem"]
                texto = frase["texto"]

                if self.cortar_cena:
                    break
                    
                if personagem not in self.vozes_carregadas:
                    print(f"Personagem {personagem} não encontrado.")
                    continue

                voz = self.vozes_carregadas[personagem]
                config_pers = self.configs_personagens[personagem]

                marcador = int(time.time())
                
                nome_arquivo = f"fala{indice + 1:03d}_{personagem}_{marcador}.wav"
                caminho_arquivo = os.path.join(self.diretorio_saida, nome_arquivo)

                print(f"Gravando: {nome_arquivo}") 


                piper = SynthesisConfig(length_scale=config_pers["velocidade"])
                
                with wave.open(caminho_arquivo, 'wb') as arquivo_wav:
                    voz.synthesize_wav(texto, arquivo_wav, syn_config=piper)   

                fila_de_audios.put((personagem, caminho_arquivo, config_pers["volume"], texto))

            fila_de_audios.put(None)

            thread.join()
        #testeana
        finally:
            with open("narracao.txt", "w", encoding="utf-8") as f:
                f.write("False")
            print("\n\nProcesso concluido")

if __name__ == "__main__":
    motor = GerenciadorDeVozes(TODAS_VOZES)
 
    #exemplo de mensagem
    mensagem_exemplo = [
        {"personagem": "Amy", "texto": "Hello, my name is Margaret!"},
        {"personagem": "Northern Male", "texto": "Hi, I'm Isaac Newton. Nice to meet you! I like reading and watching movies. I was really important for the development of physics and mathematics. My work on gravity and motion has had a huge impact on science. I had a lot of fun discovering the laws of motion and gravity! My work has been really influential in the field of physics and mathematics. I hope my contributions have helped people understand the world better!"},
        {"personagem": "Alba", "texto": "Hello, I'm Ada LoveLace. It's a pleasure to meet you!"}
    ]

    motor.processar_mensagem(mensagem_exemplo)

