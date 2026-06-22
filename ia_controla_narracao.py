import json, os, time
from smolagents import CodeAgent, InferenceClientModel, tool


#os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

ultimo_estado_palco = ""
ultima_cena_executada = ""

token = "ADD_TOKEN"

'''
modelo = TransformersModel(
    model_id="Qwen/Qwen2.5-1.5B-Instruct",
    #host="http://localhost:11434"
    device_map="auto"
)

modelo = LiteLLMModel(
    model_id="ollama_chat/qwen2.5:1.5b"
)

'''
modelo = InferenceClientModel(
    token=token,
    model_id = "Qwen/Qwen2.5-7B-Instruct"
    )

@tool
#Aqui o agente recebe o personagem que for detectado no palco
def verificar_palco() -> str:
    """
    Verifica quais cientistas foram detectados no palco.
    Se os cientistas forem os mesmos da última verificação, retorna 'Sem mudanças'.
    Se houver novos cientistas, retorna o nome deles para que uma nova cena seja criada.
    O retorno pode ser um único cientista, vários separados por vírgula (ex: 'Isaac Newton, Albert Einstein'), ou 'Sem mudanças'.
    
    Returns:
        str: Uma lista ou nome dos cientistas presentes no suporte.
    """
    global ultimo_estado_palco 
    
    #usando o arquivo como um mock do palco
    with open("palco.txt","r",encoding="utf-8") as arquivo:
        personagens_atuais = arquivo.read().strip()

    print(f"Verificando palco... Estado atual: '{personagens_atuais}', Último estado: '{ultimo_estado_palco}'")

    if personagens_atuais and personagens_atuais != ultimo_estado_palco:
        print(f"Mudança detectada! Novos personagens: {personagens_atuais}")
        ultimo_estado_palco = personagens_atuais
        return personagens_atuais
    else:
        print("Sem mudanças no palco.")
        # Se não houver ninguém ou for o mesmo personagem, informa o agente.
        return "Sem mudanças"

@tool
def mover_elemento(elemento: str, angulo: int) -> str:
    """
    Move um ou mais elementos do cenário.
    Elementos disponíveis: prisma, foguete, lua, computador
    
    Args:
        elemento: O nome do objeto/cenário que deve ser movido (ex: 'prisma').
        angulo: O ângulo de rotação para o servo motor (de 0 a 180 graus).
    Returns:
        str: Confirmação do movimento do elemento.
    """
    comando = f"MOVER_SERVO:{elemento}:{angulo}"
    print(f"[PSEUDOCOMANDO] {comando}")

    ## Aqui seria a integraçao com o codigo da Julia

    return f"Servo do(a) {elemento} movido para {angulo} graus"


@tool
def acender_led(cor: str) -> str:
    """
    Envia um comando para acender o LED específico do cenário.
    Se houver 2 ou mais cientistas, acende o LED  'amarelo' (indicando crossover).
    Cores disponíveis: vermelho, amarelo, verde, azul
    
    Args:
        cor: A cor desejada para o LED (exemplos: 'branca', 'vermelha', 'azul').
    Returns:
        str: Confirmação do comando enviado ao hardware.
    """
    #print(f"[COMANDO HARDWARE] LED alterado para a cor: {cor}")
    comando = f"Acende LED da cor:{cor}"
    print(f"[PSEUDOCOMANDO] {comando}")
    return f"Acende LED da cor {cor}"


@tool
def narrar(historia: list) -> str:
    """Narra o texto gerado pela IA sobre o cientista
    Controla o arquivo narracao.txt mudando para 'True' enquanto fala e 'False' ao terminar.
    
    Args:
        historia: O texto/história que o narrador digital deve falar.
    """
    global ultima_cena_executada
    cena_atual = str(historia)
    
    if cena_atual == ultima_cena_executada:
        print("[NARRADOR] Cena já narrada, ignorando repetição.")
        return "Ignorado"
    
    with open("narracao.txt", "w", encoding="utf-8") as f:
        f.write("True")
        
    print("\n [NARRADOR] Audio ativado")
    

    for fala in historia:
        print(f"{fala['personagem']}: {fala['texto']}")


    time.sleep(5)
    
    with open("narracao.txt", "w", encoding="utf-8") as f:
        f.write("False")
    print(" [NARRADOR] Audio Concluído")
    
    ultima_cena_executada = cena_atual
    
    return "Narração executada com sucesso"


@tool
def salvar_historia(historia: list) -> str:
    """
    Salva a história gerada pela IA em um arquivo JSON.

    Args:
        historia: Lista de dicionários no formato:
        [
            {
                "personagem": "Nome",
                "texto": "Fala"
            }
        ]
    """

    with open("historia.json", "w", encoding="utf-8") as arquivo:
        json.dump(
            historia,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    print("[HISTORIA] Arquivo salvo com sucesso.")

    return "História salva com sucesso."


tools = [verificar_palco, mover_elemento, acender_led, narrar, salvar_historia]

#Verificar se eu preciso passar o nome das tools mesmo ou nao
agent = CodeAgent(
    tools = tools,
    model = modelo,
    additional_authorized_imports=["random"]
)

prompt = """
Você é o diretor de um teatro científico automatizado. 
            
Loop:
1. Cheque se há um ou mais personagens no palco, com verificar_palco(). O retorno pode ser um único cientista ou vários separados por vírgula, ex: 'Isaac Newton, Margaret Hamilton, Ada Lovelace'.
2. Se o retorno for diferente de 'Sem mudanças', faça o seguinte:
    2.1. Printe qual(is) cientista(s) está(ão) no palco.
    2.2.  Ative as ferramentas mover_elemento() e acender_led() adequadas para cada um deles.
    2.3.  Crie uma cena em inglês (narrativa curta para 1 cientista, diálogo de 4 falas para 2 ou mais).
    2.4 Converta a cena para uma variável historia no formato:
            [
                {"personagem": "Nome", "texto": "Fala"}
            ]
    2.5 Chame salvar_historia(historia).
    2.6 Chame narrar(historia).
Se o resultado for 'Sem mudanças', não faça nada.
3. Retorne ao passo 1 para checar o palco novamente.

Execute esse loop continuamente. 

"""

def iniciar_loop_ia():
    agent.run(prompt)
            


