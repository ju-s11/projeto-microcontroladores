import tkinter
from tkinter import ttk
from datetime import datetime
import json
import os
from Narracoes import GerenciadorDeVozes, TODAS_VOZES
import threading

estado_teatro = False
motor = None

historia = [
            {"personagem": "Margaret Hamilton", "texto": "The interface is now controlling the theater!"},
            {"personagem": "Isaac Newton", "texto": "Amazing! It actually works live."},
            {"personagem": "Ada LoveLace", "texto": "Splendid! Everything is connected now."}
        ]

indice_historia = 0

#funcoes dos botoes
def registrar(mensagem):
    hora_atual = datetime.now().strftime("%H:%M:%S")
    caixa_deb.insert(tkinter.END, f"[{hora_atual}] {mensagem}\n")
    caixa_deb.see(tkinter.END)

def iniciar_teatro():
    global estado_teatro, motor, indice_historia
    
    if estado_teatro == False:
        registrar("Teatro Iniciado...")
        estado_teatro = True
        indice_historia = 0
        
        config_vozes = {
            "Ada LoveLace":{
                "voz": TODAS_VOZES[voz_ada.get()],
                "volume":vol_ada.get()/100,
                "velocidade":100.0/vel_ada.get()
                },
            "Margaret Hamilton": {
                "voz": TODAS_VOZES[voz_marg.get()],
                "volume":vol_marg.get()/100,
                "velocidade":100.0/vel_marg.get()
                },
            "Isaac Newton": {
                "voz": TODAS_VOZES[voz_isaac.get()],
                "volume":vol_isaac.get()/100,
                "velocidade":100.0/vel_isaac.get()
                }
        }
        
        motor = GerenciadorDeVozes(config_vozes)
        motor.cortar_cena = False
    
        def tarefa_thread():
            global estado_teatro
            motor.processar_mensagem(historia, registrar)
            estado_teatro = False
    
        threading.Thread (target = tarefa_thread).start()
        
    else:
        registrar("Teatro interrompido.")
        estado_teatro = False
        if motor:
            motor.parar_teatro()

def prox_fala():
    global motor, indice_historia
    
    if indice_historia >= len(historia):
        registrar("Não há mais falas.")
        return
    
    config_vozes = {
        "Ada LoveLace":{
            "voz": TODAS_VOZES[voz_ada.get()],
            "volume":vol_ada.get()/100,
            "velocidade":100.0/vel_ada.get()
            },
        "Margaret Hamilton": {
            "voz": TODAS_VOZES[voz_marg.get()],
            "volume":vol_marg.get()/100,
            "velocidade":100.0/vel_marg.get()
            },
        "Isaac Newton": {
            "voz": TODAS_VOZES[voz_isaac.get()],
            "volume":vol_isaac.get()/100,
            "velocidade":100.0/vel_isaac.get()
            }
        }
    
    
    if motor is None:
        motor = GerenciadorDeVozes(config_vozes)
    
    motor.cortar_cena = False
    fala_atual = [historia[indice_historia]]
    
    def tarefa_thread():
        global indice_historia
        motor.processar_mensagem(fala_atual, registrar)
        indice_historia += 1
    
    threading.Thread(target=tarefa_thread).start()

def mudar_lua():
    registrar("Posição da Lua alterada")

def mudar_foguete():
    registrar("Posição do Foguete alterada")
    
def mudar_prisma():
    registrar("Posição do Prisma alterada")
    
def mudar_historia():
    clima_escolhido = clima.get()
    registrar(f"Teor da História alterada para: {clima_escolhido}")
    
def mudar_luz():
    luz_escolhido = luz.get()
    registrar(f"Luz do led alterada para: {luz_escolhido}")
    
def mudar_ada():
    v = vol_ada.get()
    velocidade = vel_ada.get()
    voz = voz_ada.get()
    vel = velocidade/100
    registrar(f"Ada: Volume = {v}\n		Velocidade = {vel}x\n		Voz = {voz}")

def mudar_marg():
    v = vol_marg.get()
    velocidade = vel_marg.get()
    voz = voz_marg.get()
    vel = velocidade/100
    registrar(f"Margaret: Volume = {v}\n		     Velocidade = {vel}x\n		     Voz = {voz}")

def mudar_isaac():
    v = vol_isaac.get()
    velocidade = vel_isaac.get()
    voz = voz_isaac.get()
    vel = velocidade/100
    registrar(f"Isaac: Volume = {v}\n		  Velocidade = {vel}x\n		  Voz = {voz}")

def salvar_conf():
    dados_para_salvar = {
        "cenario": {
            "clima": clima.get(),
            "luz": luz.get()
        },
        "ada": {
            "voz": voz_ada.get(),
            "volume": vol_ada.get(),
            "velocidade": vel_ada.get()
        },
        "margaret": {
            "voz": voz_marg.get(),
            "volume": vol_marg.get(),
            "velocidade": vel_marg.get()
        },
        "isaac": {
            "voz": voz_isaac.get(),
            "volume": vol_isaac.get(),
            "velocidade": vel_isaac.get()
        }
    }
    
    with open("memoria_teatro.json", "w", encoding="utf-8") as arquivo:
        json.dump(dados_para_salvar, arquivo, indent=4)
        
    registrar("Configurações salvas com sucesso!")


def carregar_conf():
    if os.path.exists("memoria_teatro.json"):
        with open("memoria_teatro.json", "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            
            clima.set(dados["cenario"]["clima"])
            luz.set(dados["cenario"]["luz"])
            
            voz_ada.set(dados["ada"]["voz"])
            vol_ada.set(dados["ada"]["volume"])
            vel_ada.set(dados["ada"]["velocidade"])
            
            voz_marg.set(dados["margaret"]["voz"])
            vol_marg.set(dados["margaret"]["volume"])
            vel_marg.set(dados["margaret"]["velocidade"])
            
            voz_isaac.set(dados["isaac"]["voz"])
            vol_isaac.set(dados["isaac"]["volume"])
            vel_isaac.set(dados["isaac"]["velocidade"])
            
            registrar("Configurações anteriores carregadas!")


#janela principal
janela = tkinter.Tk()
janela.title("Configurações + Debug")
janela.geometry("600x500")

abas = ttk.Notebook(janela)
abas.pack(pady=10, fill="both", expand=True)

aba_debug = tkinter.Frame(abas)
aba_cenario = tkinter.Frame(abas)
aba_personagens = tkinter.Frame(abas)

abas.add(aba_cenario, text="Configurações do Cenário e da História")
abas.add(aba_personagens, text="Configurações dos Personagens")
abas.add(aba_debug, text="Debug")


#debug

frame = tkinter.Frame(aba_debug)
frame.pack()
title_deb = tkinter.Label(frame, text="Debug:", font=("Arial", 9, "bold"))
title_deb.pack(side = tkinter.CENTER, pady=10)
tkinter.Button(frame, text="Falar Próxima Fala", command=prox_fala, bg="lightgrey", font=("Arial", 10, "bold")).pack(side = tkinter.RIGHT, pady=5)

caixa_deb = tkinter.Text(aba_debug, height = 20, width = 70, bg = "black", fg="lime")
caixa_deb.pack()
caixa_deb.insert(tkinter.END, "O sistema está ligado e pronto para uso!\n")

tkinter.Button(aba_debug, text="Salvar Configurações", command=salvar_conf, bg="lightgrey", font=("Arial", 10, "bold")).pack(pady=10)


#botoes
tkinter.Label(aba_cenario, text="Controle do Teatro:", font=("Arial", 9, "bold")).pack(pady=25, anchor="w", padx=25)

frame1 = tkinter.Frame(aba_cenario)
frame1.pack(fill="x", padx=25, pady = 12.5, anchor=tkinter.CENTER)
tkinter.Label(frame1, text="Controle Geral:").pack(side=tkinter.LEFT)
tkinter.Button(frame1, text="Iniciar/Parar Teatro",command = iniciar_teatro).pack(side=tkinter.LEFT, padx=5)

frame2 = tkinter.Frame(aba_cenario)
frame2.pack(fill="x", padx=25, pady = 12.5, anchor=tkinter.CENTER)
tkinter.Label(frame2, text="Controle da Lua:").pack(side=tkinter.LEFT)
tkinter.Button(frame2, text="Esconder/Mostrar Lua",command = mudar_lua).pack(side=tkinter.LEFT, padx=5)

frame3 = tkinter.Frame(aba_cenario)
frame3.pack(fill="x", padx=25, pady = 12.5, anchor=tkinter.CENTER)
tkinter.Label(frame3, text="Controle do Foguete:").pack(side=tkinter.LEFT)
tkinter.Button(frame3, text="Esconder/Mostrar Foguete",command = mudar_foguete).pack(side=tkinter.LEFT, padx=5)

frame4 = tkinter.Frame(aba_cenario)
frame4.pack(fill="x", padx=25, pady = 12.5, anchor=tkinter.CENTER)
tkinter.Label(frame4, text="Controle do Prisma:").pack(side=tkinter.LEFT)
tkinter.Button(frame4, text="Esconder/Mostrar Prisma",command = mudar_prisma).pack(side=tkinter.LEFT, padx=5)

frame5 = tkinter.Frame(aba_cenario)
frame5.pack(fill="x", padx=25, pady = 12.5, anchor=tkinter.CENTER)
tkinter.Label(frame5, text="Controle do Clima da História:").pack(side=tkinter.LEFT)
clima = tkinter.StringVar()
clima.set("Alegre")
menu_clima=tkinter.OptionMenu(frame5, clima, "Alegre", "Triste", "Engraçada", "Assustadora")
menu_clima.pack(side=tkinter.LEFT, padx=5)
tkinter.Button(frame5, text="Aplicar", command=mudar_historia).pack(side=tkinter.LEFT, padx=5)

frame6 = tkinter.Frame(aba_cenario)
frame6.pack(fill="x", padx=25, pady = 12.5, anchor=tkinter.CENTER)
tkinter.Label(frame6, text="Controle da Luz:").pack(side=tkinter.LEFT)
luz = tkinter.StringVar()
luz.set("Off")
menu_luz=tkinter.OptionMenu(frame6, luz, "OFF", "White", "Fogo", "Espectro", "Dispersão de luz branca", "Cálculo em loop", "Fluxo de dados", "Decolagem do foguete")
menu_luz.pack(side=tkinter.LEFT, padx=5)
tkinter.Button(frame6, text="Aplicar", command=mudar_luz).pack(side=tkinter.LEFT, padx=5)

tkinter.Button(aba_cenario, text="Salvar Configurações", command=salvar_conf, bg="lightgrey", font=("Arial", 10, "bold")).pack(pady=10)


#configuração dos personagens
tkinter.Label(aba_personagens, text="Ada Lovelace", font=("Arial", 10, "bold")).pack(pady=10)
frame_ada = tkinter.Frame(aba_personagens)
frame_ada.pack(fill="x", padx=10)

voz_ada = tkinter.StringVar(value = "Alba")
tkinter.OptionMenu(frame_ada, voz_ada, "Alba", "Amy", "Northern Male", "Alan").pack(side=tkinter.LEFT, padx=5)

vol_ada = tkinter.Scale(frame_ada, from_=0, to=100, orient=tkinter.HORIZONTAL, label = "Volume")
vol_ada.set(80)
vol_ada.pack(side=tkinter.LEFT, padx=5)

vel_ada = tkinter.Scale(frame_ada, from_=50, to=200, orient=tkinter.HORIZONTAL, label = "Velocidade")
vel_ada.set(100)
vel_ada.pack(side=tkinter.LEFT, padx=5)

tkinter.Button(frame_ada, text="Aplicar", command=mudar_ada).pack(side=tkinter.LEFT, padx=10)



tkinter.Label(aba_personagens, text="Margaret Hamilton", font=("Arial", 10, "bold")).pack(pady=10)
frame_marg = tkinter.Frame(aba_personagens)
frame_marg.pack(fill="x", padx=10)

voz_marg = tkinter.StringVar(value = "Amy")
tkinter.OptionMenu(frame_marg, voz_marg, "Alba", "Amy", "Northern Male", "Alan").pack(side=tkinter.LEFT, padx=5)

vol_marg = tkinter.Scale(frame_marg, from_=0, to=100, orient=tkinter.HORIZONTAL, label = "Volume")
vol_marg.set(80)
vol_marg.pack(side=tkinter.LEFT, padx=5)

vel_marg = tkinter.Scale(frame_marg, from_=50, to=200, orient=tkinter.HORIZONTAL, label = "Velocidade")
vel_marg.set(100)
vel_marg.pack(side=tkinter.LEFT, padx=5)

tkinter.Button(frame_marg, text="Aplicar", command=mudar_marg).pack(side=tkinter.LEFT, padx=10)



tkinter.Label(aba_personagens, text="Isaac Newton", font=("Arial", 10, "bold")).pack(pady=10)
frame_isaac = tkinter.Frame(aba_personagens)
frame_isaac.pack(fill="x", padx=10)

voz_isaac = tkinter.StringVar(value = "Northern Male")
tkinter.OptionMenu(frame_isaac, voz_isaac, "Alba", "Amy", "Northern Male", "Alan").pack(side=tkinter.LEFT, padx=5)

vol_isaac = tkinter.Scale(frame_isaac, from_=0, to=100, orient=tkinter.HORIZONTAL, label = "Volume")
vol_isaac.set(80)
vol_isaac.pack(side=tkinter.LEFT, padx=5)

vel_isaac = tkinter.Scale(frame_isaac, from_=50, to=200, orient=tkinter.HORIZONTAL, label = "Velocidade")
vel_isaac.set(100)
vel_isaac.pack(side=tkinter.LEFT, padx=5)

tkinter.Button(frame_isaac, text="Aplicar", command=mudar_isaac).pack(side=tkinter.LEFT, padx=10)


tkinter.Button(aba_personagens, text="Salvar Configurações", command=salvar_conf, bg="lightgrey", font=("Arial", 10, "bold")).pack(pady=10)


carregar_conf()

janela.mainloop()

