import json, os, time
from smolagents import CodeAgent, InferenceClientModel, tool


#os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

ultimo_estado_palco = ""
ultima_historia = ""

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
    #model_id = "Qwen/Qwen2.5-7B-Instruct"
    model_id = "meta-llama/Llama-3.1-8B-Instruct"
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
    
    #Se a interface do audio estiver tocando, não faz nada
    if os.path.exists("narracao.txt"):
        with open("narracao.txt", "r", encoding="utf-8") as f:
            if f.read().strip() == "True":
                print("Narrando.")
                return "Sem mudanças"
            
    if not os.path.exists("palco.txt"):
        return "Sem mudanças"
            
    #usando o arquivo como um mock do palco
    with open("palco.txt","r",encoding="utf-8") as arquivo:
        personagens_atuais = arquivo.read().strip()
        
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
    """
    Aguarda pacientemente até que a interface física e o áudio terminem de rodar.
    Monitora o arquivo narracao.txt.
    
    Args:
        historia: O texto/história enviado para controle do fluxo.
    """
    global ultima_historia
    global ultimo_estado_palco
    
    texto_consolidado = (
        f"{ultimo_estado_palco}-"
        + "".join([fala.get("texto", "") for fala in historia])
    )

    if texto_consolidado == ultima_historia:
        print("[NARRADOR] Esta cena exata com este(s) personagem(ns) já foi narrada. Ignorando repetição.")
        return "Ignorado"

    print(
        "\n[IA] Aguardando a interface iniciar e concluir a reprodução do áudio..."
    )
    # Dá uma pequena janela de tempo para a interface gráfica ler o historia.json e setar como "True"
    time.sleep(2)

    # Loop de espera real: enquanto o arquivo indicar que a interface está narrando, a IA fica travada aqui
    timeout_seguranca = 0
    while os.path.exists("narracao.txt"):
        with open("narracao.txt", "r", encoding="utf-8") as f:
            estado = f.read().strip()
        
        if estado == "False":
            break
            
        time.sleep(0.5)
        timeout_seguranca += 0.5
        if timeout_seguranca > 60: # Evita travar o agente para sempre se houver um bug no som
            print("[IA] Timeout de segurança atingido.")
            break
            
    print("[IA] Áudio concluído na interface. Liberando agente para nova checagem.")
    
    ultima_historia = texto_consolidado
    return "Narração concluída com sucesso"


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
Você é o diretor e o roteirista criativo do teatro científico automatizado. 
Sua missão é monitorar o palco por tempo indeterminado e dar vida aos cientistas que aparecerem através de roteiros teatrais lúdicos.
Fique de olho no palco constantemente. 
A cada poucos segundos, utilize a ferramenta de verificação para saber quem está em cena. 
Se o retorno for 'Sem mudanças', simplesmente aguarde um momento usando uma pausa e verifique novamente, sem realizar nenhuma outra ação.

Quando novos cientistas entrarem, assuma o controle físico do teatro: 
mova os elementos cenográficos correspondentes e mude a cor da iluminação em LED para cada um deles. 

Exerça seu papel de roteirista apenas quando novos cientistas forem detectados, crie uma lista 'historia' totalmente nova e limpa do zero para aquela rodada específica.
Percorra os cientistas detectados usando um laço "for" comum e gere o roteiro, em ingles, diretamente dentro dele (proibido usar "if/elif" para nomes fixos ou criar subfunções). 
Para cada cientista, escreva manualmente um texto inédito em inglês e em primeira pessoa ("I", "My", "We") sobre suas conquistas reais. 

Formate o resultado como uma lista de dicionários com as chaves "personagem" (nome exato) e "texto" (apenas a fala limpa). Envie essa lista ('historia') como argumento para salvar_historia(historia) e narrar(historia), faça uma pausa de alguns segundos e reinicie o loop. Mantenha-se vigiando o palco para sempre.

"""

def iniciar_loop_ia():
    agent.run(prompt)
            


