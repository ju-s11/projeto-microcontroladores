import tkinter
from tkinter import ttk
from datetime import datetime
import json
import os
from narracoes import GerenciadorDeVozes, TODAS_VOZES
import threading
import ia_controla_narracao2 as teste_ia 
import time

estado_teatro = False
motor = None
historia = []
ultima_data_json = 0
e_lua = False
e_foguete = False
e_prisma = False
var_personagens = {}

#funcoes

def carregar_historia():
    global historia
    try:
        if os.path.exists("historia.json"):
            with open ("historia.json", "r", encoding="utf-8") as arquivo:
                historia = json.load(arquivo)
        else:
            registrar("Nenhuma história encontrada")
            historia = []
    except (json.JSONDecodeError, PermissionError):
        # Se o arquivo estiver sendo escrito pela IA, ignora esse frame e espera o próximo
        return None

def vigiar_roteiro():
    global ultima_data_json, motor, estado_teatro
    
    if estado_teatro and os.path.exists("historia.json"):
        data_atual = os.path.getmtime("historia.json")
        
        if data_atual > ultima_data_json:
            ultima_data_json = data_atual
            carregar_historia()
            
            if historia and motor:
                registrar("Nova cena")
                motor.parar_teatro()
                time.sleep(0.5)
                motor.cortar_cena=False
                threading.Thread(target=motor.processar_mensagem, args=(historia, registrar), daemon=True).start()

    janela.after(2000, vigiar_roteiro)

    
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
        ultima_data_json = 0
        
        threading.Thread(target=teste_ia.iniciar_loop_ia, daemon=True).start()
        
        config_vozes = {}
        
        for nome, variavel in var_personagens.items():
            config_vozes[nome] = {
                "voz": TODAS_VOZES[variaveis["voz"].get()],
                "volume": variaveis["volume"].get() / 100,
                "velocidade": 100.0 / variaveis["velocidade"].get()}
        
        motor = GerenciadorDeVozes(config_vozes)
        motor.cortar_cena = False
    
        
    else:
        registrar("Teatro interrompido.")
        estado_teatro = False
        if motor:
            motor.parar_teatro()


def atu_personagens (): #para colocar as configs dos personagens na interface
    nomes_dig = nomes_personagens.get()
    lista_nomes = []
    for nome in nomes_dig.split(","):
        nome.strip()
        lista_nomes.append(nome.strip())
    
    for configuracao in aba_personagens.winfo_children():
        configuracao.destroy()

    var_personagens.clear()
    
    for nome in lista_nomes:
        tkinter.Label(aba_personagens, text=nome, font=("Arial", 10, "bold")).pack(pady=10)
        frame_p = tkinter.Frame(aba_personagens)
        frame_p.pack(fill="x", padx=10)

        voz_p = tkinter.StringVar(value = "Alba")
        tkinter.OptionMenu(frame_p, voz_p, "Alba", "Amy", "Northern Male", "Alan").pack(side=tkinter.LEFT, padx=5)

        vol_p = tkinter.Scale(frame_p, from_=0, to=100, orient=tkinter.HORIZONTAL, label = "Volume")
        vol_p.set(80)
        vol_p.pack(side=tkinter.LEFT, padx=5)

        vel_p = tkinter.Scale(frame_p, from_=50, to=200, orient=tkinter.HORIZONTAL, label = "Velocidade")
        vel_p.set(100)
        vel_p.pack(side=tkinter.LEFT, padx=5)

 
        var_personagens[nome]={
            "voz": voz_p,
            "volume": vol_p,
            "velocidade": vel_p
            }
        
    tkinter.Button(aba_personagens, text="Salvar Configurações", command=salvar_conf, bg="lightgrey", font=("Arial", 10, "bold")).pack(pady=10)
    registrar(f"Controles gerados para {lista_nomes}!")
    
def mudar_lua():
    global e_lua
    if e_lua == True:
        e_lua = False
        registrar("Lua: movimento interrompido")
    else:
        e_lua = True
        registrar("Lua: movimento iniciado")

def mudar_foguete():
    global e_foguete
    if e_foguete == True:
        e_foguete = False
        registrar("Foguete: movimento interrompido")
    else:
        e_foguete = True
        registrar("Foguete: movimento iniciado")
    
def mudar_prisma():
    global e_prisma
    if e_prisma == True:
        e_prisma = False
        registrar("Prisma: movimento interrompido")
    else:
        e_prisma = True
        registrar("Prisma: movimento iniciado")
    
def mudar_historia():
    clima_escolhido = clima.get()
    registrar(f"Teor da História alterada para: {clima_escolhido}")
    
def mudar_luz():
    luz_escolhido = luz.get()
    registrar(f"Luz do led alterada para: {luz_escolhido}")
    

def salvar_conf():
    dados_para_salvar = {
        "cenario": {
            "clima": clima.get(),
            "luz": luz.get()
        },
        "personagens": {}
    }
    
    for nome, variaveis in var_personagens.items():
        dados_para_salvar["personagens"][nome] = {
            "voz": variaveis["voz"].get(),
            "volume": variaveis["volume"].get(),
            "velocidade": variaveis["velocidade"].get()} 
        
    with open("memoria_teatro.json", "w", encoding="utf-8") as arquivo:
        json.dump(dados_para_salvar, arquivo, indent=4, ensure_ascii=False)
        
    registrar("Configurações salvas com sucesso!")


def carregar_conf():
    if os.path.exists("memoria_teatro.json"):
        with open("memoria_teatro.json", "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            
            clima.set(dados["cenario"]["clima"])
            luz.set(dados["cenario"]["luz"])
            
            if "personagens" in dados:
                nomes_salvos = list(dados["personagens"].keys())
                if nomes_salvos:
                    nomes_personagens.set(",".join(nomes_salvos))
                    atu_personagens()
            
                for nome, config in dados["personagens"].items():
                    if nome in var_personagens:
                        var_personagens[nome]["voz"].set(dados["personagens"][nome]["voz"])
                        var_personagens[nome]["volume"].set(dados["personagens"][nome]["volume"])
                        var_personagens[nome]["velocidade"].set(dados["personagens"][nome]["velocidade"])
            
            registrar("Configurações anteriores carregadas!")


#janela principal
janela = tkinter.Tk()
janela.title("Configurações + Debug")
janela.geometry("600x550")

abas = ttk.Notebook(janela)
abas.pack(pady=10, fill="both", expand=True)

aba_debug = tkinter.Frame(abas)
aba_cenario = tkinter.Frame(abas)
aba_personagens = tkinter.Frame(abas)

abas.add(aba_cenario, text="Configurações do Cenário e da História")
abas.add(aba_personagens, text="Configurações dos Personagens")
abas.add(aba_debug, text="Debug")


#debug

frame = tkinter.Frame(aba_debug, height = 30)
frame.pack(pady=15, fill="x", padx=25)

title_deb = tkinter.Label(frame, text="Debug:", font=("Arial", 9, "bold"))
title_deb.place(relx=0.5, rely=0.5, anchor="center")

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
clima= tkinter.StringVar()
tkinter.Entry(frame5, textvariable = clima, width=40).pack(side=tkinter.LEFT, padx = 5)
tkinter.Button(frame5, text="Aplicar", command=mudar_historia).pack(side=tkinter.LEFT, padx=5)

framep = tkinter.Frame(aba_cenario)
framep.pack(fill="x", padx=25, pady = 12.5, anchor=tkinter.CENTER)
tkinter.Label(framep, text="Nome dos personagens:").pack(side=tkinter.LEFT)
nomes_personagens= tkinter.StringVar()
tkinter.Entry(framep, textvariable = nomes_personagens, width=40).pack(side=tkinter.LEFT, padx = 5)
tkinter.Button(framep, text="Aplicar", command=atu_personagens).pack(side=tkinter.LEFT, padx=5)


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

tkinter.Button(aba_personagens, text="Salvar Configurações", command=salvar_conf, bg="lightgrey", font=("Arial", 10, "bold")).pack(pady=10)


carregar_conf()
vigiar_roteiro()
janela.mainloop()




